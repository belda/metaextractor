''' Extracts data in opengraph atributes '''
from metaextractor import BasePlugin 
from lxml import etree
from htmlfetch import Extractor as HE

class Extractor(HE):
    def extract(self, content,  **kwargs):
        ret = {}
        self.content = content
        
        maps = ( ('title',      'title'),
                 ('link',       'url'),
                 ('image_url',  'image'),
                 ('description','description'),
                 ('site_name',  'site_name'),
                 ('author',     'site_name'),
                 ('og_type',    'type') )
        for a,b in maps:
            ret[a] = self.xpath( "//meta[@property='og:%s' or @name='og:%s']/@content" % (b,b))
        return ret

