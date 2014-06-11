import pkgutil
import eplugins
import requests

class Metaextractor(object):
    ''' Metaextractor uses available modules to process the input and returned extracted metadata .
        Without any parameters it loads all available plugins.
        params:
            - config - { 'plugins' : ['htmlfetch', 'schematoplugin'],   #list of enabled plugins
                        'skip_errors' : False,         #should errors in plugin be skipped  or propagated
                        'none_means_empty' : True,     #when merging 2 dicts, consider that None value is same as empty and should be overwritten by a value
                        'field_priority'  : { 'link' : [ 'schematoplugin', 'htmlfetch' ] }, #you can override the priority for individual fields (rightmost 
                                                                                            #override leftones
                         } '''
    
    config      = { 'plugins'           : [ modname for importer, modname, ispkg in pkgutil.iter_modules(eplugins.__path__) if not ispkg ],
                    'skip_errors'       : True, 
                    'none_means_empty'  : True}
    extractors  = []
    def __init__(self, *args, **kwargs):
        if kwargs.has_key('config') and isinstance(kwargs.get('config'), dict):
            self.config.update( kwargs.get('config') )
        for p in self.config['plugins']:
            mod_name = 'eplugins.'+p
            module = __import__(mod_name, fromlist=[mod_name,])
            extractor = getattr(module, 'Extractor')(self.config) #instantiate the extractor from the eplugin
            self.extractors.append(extractor)
        
    def extract(self,**kwargs):
        ''' Extract the data from supplied argument 
            params:
                - url - the url address from which to extract
                - content - the byte content of the file to be processed'''
        
        #do the work
        edicts = {}
        for ext in self.extractors:
            try:
                edict = ext.extract(**kwargs)
            except Exception, e:
                if not (self.config.get("skip_errors") == True):
                    raise
                edict = {}
            if self.config['none_means_empty']: #clear out None values
                edict = dict((k, v) for k, v in edict.iteritems() if v)
            edicts[ext.__module__[ext.__module__.rindex(".")+1:]] = edict

        ret = {}
        for p in self.config['plugins']:
            ret.update(edicts[p])
            
        if self.config.has_key('field_priority'): #now overwrite the per field priority overrides
            for field in self.config['field_priority']:
                fps = self.config['field_priority']['field']
                for p in fps:
                    if edicts[p].has_key(field):
                        ret[field] = edicts[p][field]
          
        return ret
    
    
class BasePlugin(object):
    ''' Basic plugin parent that defines the minimum functionality, it handles the "download only once" functionality using ContentHolder '''
    config = {}
    def __init__(self,config):
        self.config = config
        
    def extract(self,**kwargs):
        content = kwargs['content_holder'].content if kwargs.has_key('content_holder') else kwargs.get('content')
        if content!= None and hasattr(self,'extract_content') and hasattr(self.extract_content, '__call__'):
            return self.extract_content(content=content, **kwargs)
        elif hasattr(self,'extract_url') and hasattr(self.extract_url, '__call__'):
            return self.extract_url(url=url, **kwargs)
        return {}
    
class ContentHolder(object):
    ''' Object representing content using url or downloaded content. It is used to avoid duplication of downloads '''
    url = None
    _content = None
    def __init__(self, *args, **kwargs):
        if kwargs.has_key('content'):
            self._content = kwargs.get('content')
        if kwargs.has_key('url'):
            self.url = kwargs.get('url')
    
    @property
    def content(self): 
        if self._content:
            return self._content
        if self.url:
            rsp = requests.get(self.url)
            if rsp.ok:
                self._content = rsp.content
                return self._content
        return None
    @content.setter
    def content(self, val):
        self._content = val
            
            