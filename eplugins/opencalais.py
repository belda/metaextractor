''' opencalais.com to extract metadata from fulltext.
    In order for this plugin to work, you have to define your opencalais.com api key in settings
    and you have to have pycalais installed (https://github.com/ubergrape/pycalais) '''
from metaextractor import BasePlugin 
from calais.base.client import Calais
from settings import OPENCALAIS_API_KEY
import requests

class Extractor(BasePlugin):
    def extract_content(self, content, **kwargs):
        api = Calais(OPENCALAIS_API_KEY, submitter="Metaextractor")
        result = api.analyze(content=content, content_type="TEXT/HTML")
        return self.process_result(result)

    def extract_url(self, url, **kwargs):
        api = Calais(OPENCALAIS_API_KEY, submitter="Metaextractor")
        result = api.analyze_url(url)
        return self.process_result(result)
        
    def process_result(self, result):
        ret = {}
        for k in ('entities', 'languages', 'socialTags', 'info', 'meta', 'relations', 'topics'):
            try:
                ret['opencalais_'+k] = getattr(result, k)
            except:
                pass
        return ret