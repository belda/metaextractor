''' Extracts data using schemato distiller
    https://github.com/parsely/schemato '''
from metaextractor import BasePlugin 
from schemato import Schemato
from schemato.distillery import ParselyDistiller, NewsDistiller


class Extractor(BasePlugin):
    def extract(self, **kwargs):
        sch = Schemato(kwargs.get('url'))
        d1 = ParselyDistiller(sch)
        try:
            return d1.distill()
        except AttributeError:
            pass
        d2 = NewsDistiller(sch)
        return d2.distill()        