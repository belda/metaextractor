''' Extracts data by basic html title etc '''
from metaextractor import BasePlugin 
import requests
from lxml import etree


class Extractor(BasePlugin):
    def extract(self, **kwargs):
        rsp = requests.get(kwargs.get('url'))
        ret = {}
        root = etree.HTML(rsp.content)
        ret['title'] = xpathit(root,"//title")
        ret['link'] = rsp.url
        ret['image_url'] = xpathit(root, "//link[@rel='image_src']/@href")
        return ret
        
def xpathit(elm, xpath):
    """ Extracts textual representation of the xpath value from underneath element elm """
    if xpath[0:1] in ["'", '"'] and xpath[-1:] in ["'", '"']:
        return xpath   
    if xpath=="":
        return ""
    try:
        val_elm = elm.xpath(xpath)
    except etree.XPathEvalError:
        return "XPathEvalError: "+xpath
    if isinstance(val_elm, str):
        return val_elm
    elif len(val_elm)==0:
        return ""
    else:
        return val_elm[0].text if isinstance(val_elm[0], etree._Element) else val_elm[0]
    
