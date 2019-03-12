

METAEXTRACTOR_CONFIG = { 'plugins'      : ['htmlfetch','opengraph','omnidator'],
                         'skip_errors'  : True }
#METAEXTRACTOR_CONFIG['field_priority'] = { 'link' : [ 'schematoplugin', 'htmlfetch' ] }

OPENCALAIS_API_KEY="t6bcvf5pg7yz2pnme6skzz8b"

REDIS_KEY_PREFIX = "ME-"
REDIS_LOGIN = { 'host' :'localhost', 'port':6379, 'db':0}

CELERY_TASKS_NAME = "MetaExtractorTasks"
CELERY_BROKER = "redis://localhost"
CELERY_BACKEND = "redis://localhost"


# *** schemato configuration ***********
VALIDATOR_MODULES = [
    "schemas.rnews.RNewsValidator",
    "schemas.opengraph.OpenGraphValidator",
    "schemas.schemaorg.SchemaOrgValidator",
    "schemas.schemaorg_rdf.SchemaOrgRDFaValidator",
    "schemas.parselypage.ParselyPageValidator",
]

# root of schema cache
CACHE_ROOT = "/tmp"
# how many seconds to wait until re-cache
CACHE_EXPIRY = 60 * 60 * 100

# *** end schemato configuration *******
