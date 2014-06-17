''' Extracts data using schemato distiller
    https://github.com/parsely/schemato '''
from metaextractor import BasePlugin 
from schemato import Schemato
from schemato.distillery import ParselyDistiller, NewsDistiller


class Extractor(BasePlugin):
    def extract(self, url, **kwargs):
        sch = Schemato(url)
        d1 = ParselyDistiller(sch)
        try:
            return d1.distill()
        except AttributeError:
            pass
        d2 = NewsDistiller(sch)
        return d2.distill()        