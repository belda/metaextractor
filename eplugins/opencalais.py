''' opencalais.com to extract metadata from fulltext.
    In order for this plugin to work, you have to define your opencalais.com api key in settings
    and you have to have pycalais installed (https://github.com/ubergrape/pycalais) '''
from metaextractor import BasePlugin 
from calais.base.client import Calais
from settings import OPENCALAIS_API_KEY
import requests

class Extractor(BasePlugin):
    def extract(self, **kwargs):
        api = Calais(OPENCALAIS_API_KEY, submitter="Metaextractor")
        if kwargs.has_key("text"):
            result = api.analyze(content=kwargs['text'], content_type="TEXT/HTML")
        elif kwargs.has_key("url"):
            result = api.analyze_url(kwargs['url'])
        else:
            return {}
        return self.process_result(result)

    def process_result(self, result):
        ret = {}
        for k in ('entities', 'languages', 'socialTags', 'info', 'meta', 'relations', 'topics'):
            try:
                ret['opencalais_'+k] = getattr(result, k)
            except:
                pass
        return ret