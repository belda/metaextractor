

METAEXTRACTOR_CONFIG = { 'plugins'      : ['htmlfetch','omnidator'],
                         'skip_errors'  : True }
#METAEXTRACTOR_CONFIG['field_priority'] = { 'link' : [ 'schematoplugin', 'htmlfetch' ] }

OPENCALAIS_API_KEY=""


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
CACHE_EXPIRY = 60 * 60 * 500

# *** end schemato configuration *******