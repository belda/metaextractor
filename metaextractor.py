import pkgutil
import eplugins
import requests
import re
import charade
import settings
import json
import redis
import time
from lxml import etree
from celery import Celery
from celery.contrib.methods import task_method

red = redis.StrictRedis(**settings.REDIS_LOGIN)
jobq = Celery(settings.CELERY_TASKS_NAME, backend = settings.CELERY_BACKEND, broker = settings.CELERY_BROKER)

        
def extract(**kwargs):
    ''' Metaextractor uses available modules to process the input and returned extracted metadata .
        Without any parameters it loads all available plugins.
        params:
            - config - { 'plugins' : ['htmlfetch', 'schematoplugin'],   #list of enabled plugins
                        'skip_plugins' : ['opencalais'],                #list of plugins, that are dissabled
                        'skip_errors' : False,                          #should errors in plugin be skipped  or propagated
                        'none_means_empty' : True,                      #when merging 2 dicts, consider that None value is same as empty and should be overwritten by a value
                        'field_priority'  : { 'link' : [ 'schematoplugin', 'htmlfetch' ] }, #you can override the priority for individual fields (rightmost 
                                                                                            #override leftones
                        'nocache'    : true,                            #should all caches be skipped    
                        'nocache_global' : false,                       #should the global cache be skipped
                        'nocache_plugins': ['htmlfetch'],               #should the cache be skipped for specified plugins
                        'wait_for_jobs'     : 8 #how many seconds to wait for individual plugins to finish the job
                         } 
            - url    - url to extract from
            - content_holder - ContentHolder instance, that helps with not downloading content multiple times'''
    
    #init config
    config      = { 'plugins'           : [ modname for importer, modname, ispkg in pkgutil.iter_modules(eplugins.__path__) if not ispkg ],
                    'skip_plugins'      : [],
                    'skip_errors'       : True, 
                    'none_means_empty'  : True,
                    'nocache'           : False,
                    'nocache_global'    : False,
                    'nocache_plugins'   : [],
                    'wait_for_jobs'     : 10}
    extractors  = []
    if kwargs.has_key('config') and isinstance(kwargs.get('config'), dict):
        config.update( kwargs.get('config') )
#        kwargs['config'] = config #to be able to put it to the other function
        
    #try the cache
    if red and kwargs.has_key('url'):
        rediskey = settings.REDIS_KEY_PREFIX+"WHOLE-"+kwargs['url']+";"+json.dumps(config)
        if not (config['nocache'] or config['nocache_global']):
            dd = red.get(rediskey)
            if dd:
                return json.loads(dd)
    
    #load up the plugins
    for p in config['plugins']:
        if p not in config['skip_plugins']:
            mod_name = 'eplugins.'+p
            module = __import__(mod_name, fromlist=[mod_name,])
            extractor = getattr(module, 'Extractor')(config) #instantiate the extractor from the eplugin
            extractors.append(extractor)
    
    #do the work***
    #initialize the content holder
    #get the data
    if kwargs.has_key('url'):
        content_holder = ContentHolder(url=kwargs['url'], config=config)
    elif kwargs.has_key('content'):
        content_holder = ContentHolder(content=kwargs['content'], config=config)
    else:
        raise AttributeError("You must supply either url or content parameter")
    #create the celery jobs
    responses = {}
    for ext in extractors:
        responses[ext.name] = inner_extract.apply_async(args=[ext], kwargs=content_holder.__dict__)
    
    #periodically chek, whether the responses are ready and collect them
    edicts = {}
    for i in range(0,config['wait_for_jobs']*4,):
        time.sleep(.25)
        allready = True
        for ext in extractors:
            if responses[ext.name].ready():
                try:
                    edict = responses[ext.name].get()
                except Exception, e:
                    if not (config.get("skip_errors") == True):
                        raise
                    edict = {}
                if config['none_means_empty']: #clear out None values
                    edict = dict((k, v) for k, v in edict.iteritems() if v)
            else:
                edict = {}
                allready = False
            edicts[ext.name] = edict
        if allready:
            break
    
    #prepare the response
    ret = {}
    for p in config['plugins']:
        ret.update(edicts.get(p,{}))
        
    #now overwrite the per field priority overrides
    if config.has_key('field_priority'): 
        for field in config['field_priority']:
            fps = config['field_priority']['field']
            for p in fps:
                if edicts[p].has_key(field):
                    ret[field] = edicts[p][field]
      
    #write back to cache              
    if red and kwargs.has_key('url'):
        if len(ret.keys())>0: #do not cache empty
            red.set(rediskey, json.dumps(ret), settings.CACHE_EXPIRY)
    return ret


@jobq.task( hard_time_limit=60)
def inner_extract(plugin, **kwargs):
    ''' Creates a background Celery job to run the extractors in paralel '''
    #try the cache
    usecache = red and kwargs.has_key('url') and kwargs.has_key('config')
    if usecache:
        rediskey = settings.REDIS_KEY_PREFIX+"plugin-"+plugin.name+":"+kwargs['url']
        if not (kwargs['config']['nocache'] or plugin.name in kwargs['config']['nocache_plugins']):
            dd = red.get(rediskey)
            if dd:
                return json.loads(dd)
    ret = plugin.extract(**kwargs)
    #write back to cache              
    if usecache:
        red.set(rediskey, json.dumps(ret), settings.CACHE_EXPIRY)
    return ret
    
    
class BasePlugin(object):
    ''' Basic plugin parent that defines the minimum functionality, it handles the "download only once" functionality using ContentHolder '''
    config = {}
    def __init__(self,config):
        self.config = config
        
    def extract(self,**kwargs):
        self.content = content
        self.encoding = kwargs.get('encoding', None)
        return {}
    
    @property
    def name(self):
        return self.__module__[self.__module__.rindex(".")+1:]
    
class ContentHolder(object):
    ''' Object representing content using url or downloaded content. It is used to avoid duplication of downloads, and easy access '''
    content_holder = None
    url = None
    content = None
    encoding = None
    def __init__(self, *args, **kwargs):
        if kwargs.has_key('config'):
            self.config = kwargs['config']
            self.encoding = self.config.get("remote_encoding", None)
        if kwargs.has_key('content'):
            self.content = kwargs.get('content')
        if kwargs.has_key('url'):
            self.url = kwargs.get('url')
        if self.url and not self.content:
            rsp = requests.get(self.url)
            if rsp.ok:
                if self.encoding:
                    rsp.encoding = self.encoding
                else:
                    encodings = self.get_encodings_from_content(rsp.content)
                    if encodings:
                        self.encoding = encodings[0]
                        rsp.encoding = encodings[0]
                    else:
                        rsp.encoding = rsp.apparent_encoding
                        self.encoding = rsp.apparent_encoding
                self.content = rsp.text
                self.url = rsp.url
            else:
                raise requests.exceptions.RequestException("Remote content was not retrieved")
                
    def get_encodings_from_content(self, content):
        charset_re = re.compile(r'<meta.*?charset=["\']*(.+?)["\'>]', flags=re.I)
        pragma_re = re.compile(r'<meta.*?content=["\']*;?charset=(.+?)["\'>]', flags=re.I)
        xml_re = re.compile(r'^<\?xml.*?encoding=["\']*(.+?)["\'>]')
        # FIXME: Does not work in python 3
        return (charset_re.findall(content) +
                pragma_re.findall(content) +
                xml_re.findall(content))