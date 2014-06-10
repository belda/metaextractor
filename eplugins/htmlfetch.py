''' Extracts data by basic html title etc '''
import re
from metaextractor import BasePlugin 
from lxml import etree


class Extractor(BasePlugin):
    def extract_content(self, content,  **kwargs):
        ret = {}
        root = etree.HTML(content)
        ret['title'] = xpathit(root,"//title")
        if kwargs.has_key("content_holder"):
            ret['link'] = kwargs['content_holder'].url
        ret['image_url'] = xpathit(root, "//link[@rel='image_src']/@href")
        ret['description'] = xpathit(root, "//meta[@name='description']/@content")
        ret['author'] = xpathit(root, "//meta[@name='author']/@content")
        if not ret['author']:
            try:
                ret['author'] = re.search("^(https?:)?(\/\/)?(www\.)?(?P<author>[a-z0-9\.]+)(|\/|\/.+)$", ret['link']).groupdict().get('author')
            except: #if it does not find, no biggie
                pass
        try:
            ret['apple-touch-icon'] = xpathit(root, "//link[@rel='apple-touch-icon']/@href")
        except:
            pass
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
    
