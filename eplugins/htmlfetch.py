''' Extracts data by basic html title etc '''
import re
from metaextractor import BasePlugin 
from lxml import etree
from io import StringIO, BytesIO

class Extractor(BasePlugin):
    def extract(self, content,  **kwargs):
        ret = {}
        self.content = content
        self.encoding = kwargs.get('encoding', None)

        ret['title'] = self.xpath("//title").strip()
        if kwargs.has_key("url"):
            ret['link'] = kwargs['url']
        ret['image'] = self.xpath("//link[@rel='image_src']/@href")
        ret['description'] = self.xpath("//meta[@name='description']/@content").strip()
        ret['author'] = self.xpath("//meta[@name='author']/@content")
        if not ret['author']:
            try:
                ret['author'] = re.search("^(https?:)?(\/\/)?(www\.)?(?P<author>[a-z0-9\.]+)(|\/|\/.+)$", ret['link']).groupdict().get('author')
            except: #if it does not find, no biggie
                pass
        try:
            ret['apple-touch-icon'] = self.xpath("//link[@rel='apple-touch-icon']/@href")
        except:
            pass
        return ret

    @property
    def root_elm(self):
        if not hasattr(self, '_root'):
            parser = etree.HTMLParser(encoding="utf-8")
            self._root = etree.parse(BytesIO(self.content.encode("utf-8")), parser)
        return self._root
        
    def xpath(self, xpath, elm = None):
        """ Extracts textual representation of the xpath value from underneath element elm """
        if elm == None:
            elm = self.root_elm
        if xpath[0:1] in ["'", '"'] and xpath[-1:] in ["'", '"']:
            return xpath   
        if xpath=="":
            return ""
        try:
            val_elm = elm.xpath(xpath)
        except etree.XPathEvalError:
            return "XPathEvalError: "+xpath
        if isinstance(val_elm, str):
            ttt = val_elm
        elif len(val_elm)==0:
            ttt =  ""
        else:
            ttt = val_elm[0].text if isinstance(val_elm[0], etree._Element) else val_elm[0]
        return ttt
        