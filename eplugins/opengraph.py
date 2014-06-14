''' Extracts data in opengraph atributes '''
from metaextractor import BasePlugin 
from htmlfetch import xpathit
from lxml import etree


class Extractor(BasePlugin):
    def extract_content(self, content,  **kwargs):
        ret = {}
        r = etree.HTML(content)
        maps = ( ('title',      'title'),
                 ('link',       'url'),
                 ('image_url',  'image'),
                 ('description','description'),
                 ('site_name',  'site_name'),
                 ('author',     'site_name'),
                 ('og_type',    'type') )
        for a,b in maps:
            ret[a] = xpathit(r, "//meta[@property='og:%s']/@content" % b)
        return ret

