''' Uses http://omnidator.appspot.com/ to extract schema.org metadata '''
from metaextractor import BasePlugin 
import requests

class Extractor(BasePlugin):
    def extract(self, **kwargs):
        url = kwargs.get('url')
        rsp = requests.get("http://omnidator.appspot.com/microdata/json/?url="+url)
        if rsp.ok:
            js = rsp.json()
            ret = { 'jsonld' : rsp.json() }
            if js.has_key("@") and len(js["@"]) and js["@"][0].has_key("a") and "schema.org/Article" in js["@"][0]["a"]:
                ret['title'] = js["@"][0]["http://schema.org/Article#headline name"].strip()
                ret['image_url'] = js["@"][0]["http://schema.org/Article#image"].replace("<","").replace(">","")
            return ret
        else:
            return {}
