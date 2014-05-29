import pkgutil
import eplugins

class Metaextractor(object):
    ''' Metaextractor uses available modules to process the input and returned extracted metadata .
        Without any parameters it loads all available plugins.
        params:
            - config - { 'plugins' : ['htmlfetch', 'schemato'],   #list of enabled plugins
                        'skiperrors' : False,         #should errors in plugin be skipped  or propagated
                         } '''
    config      = {}
    extractors  = []
    def __init__(self, *args, **kwargs):
        if kwargs.has_key('config'): #takes the plugins from configuration
            plugins = config['plugins']
            self.config = config
        else: #load up all available plugins
            plugins = [ modname for importer, modname, ispkg in pkgutil.iter_modules(eplugins.__path__) if not ispkg ]
        for p in plugins:
            mod_name = 'eplugins.'+p
            module = __import__(mod_name, fromlist=[mod_name,])
            extractor = getattr(module, 'Extractor')(self.config) #instantiate the extractor from the eplugin
            self.extractors.append(extractor)
        
    def extract(self,**kwargs):
        ''' Extract the data from supplied argument 
            params:
                - url - the url address from which to extract
                - content - the byte content of the file to be processed'''
        ret = {}
        for e in self.extractors:
            if not (self.config.get("skiperrors") == True):
                ret.update(e.extract(**kwargs))
            else:
                try:
                    ret.update(e.extract(**kwargs))
                except Exception, e:
                    pass
        return ret
    
    
class BasePlugin(object):
    ''' Basic plugin parent that defines the minimum functionality '''
    config = {}
    def __init__(self,config):
        self.config = config
        
    def extract(self,**kwargs):
        return {}
    