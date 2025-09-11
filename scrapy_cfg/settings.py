BOT_NAME = "funcionarios_ppublicos"
#LOG_LEVEL = "INFO"

ROBOTSTXT_OBEY = False
# USER_AGENT = "vigilancia_prospectiva (+https://example.org/contact)"

# Concurrencia
CONCURRENT_REQUESTS = 40
CONCURRENT_REQUESTS_PER_DOMAIN = 10
DOWNLOAD_DELAY = 0.0

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
)


# Autothrottle (útil si algunos sitios son lentos)
AUTOTHROTTLE_ENABLED = False
# AUTOTHROTTLE_START_DELAY = 0.25
# AUTOTHROTTLE_MAX_DELAY = 2.0
# AUTOTHROTTLE_TARGET_CONCURRENCY = 3.0

# Retries / timeouts
RETRY_ENABLED = True
RETRY_TIMES = 1
DOWNLOAD_TIMEOUT = 10

# Cache HTTP (desarrollo)
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 86400

# Pipelines (opcional si grabas a DB)
# ITEM_PIPELINES = {
#     "vigilancia_prospectiva.scrapy.pipelines.NormalizePipeline": 100,
# }

FEEDS = {
    "salida.json": {
        "format": "json",
        "encoding": "utf8",
        "indent": 4,
        "overwrite": True,
    }
}

TWISTED_REACTOR = "twisted.internet.iocpreactor.reactor.IOCPReactor"
