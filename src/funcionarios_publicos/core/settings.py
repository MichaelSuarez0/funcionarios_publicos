BOT_NAME = "funcionarios_publicos"
LOG_ENABLED = True
LOG_LEVEL = "INFO"

ROBOTSTXT_OBEY = False

# Concurrencia
CONCURRENT_REQUESTS_PER_DOMAIN = 16
CONCURRENT_REQUESTS = 16
DOWNLOAD_DELAY = 0.05

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
)


# Autothrottle
AUTOTHROTTLE_ENABLED = False
# AUTOTHROTTLE_START_DELAY = 0.25
# AUTOTHROTTLE_MAX_DELAY = 2.0
# AUTOTHROTTLE_TARGET_CONCURRENCY = 3.0

# Retries / timeouts
RETRY_ENABLED = True
RETRY_TIMES = 2
DOWNLOAD_TIMEOUT = 15

# Cache HTTP (desarrollo)
HTTPCACHE_ENABLED = False
HTTPCACHE_EXPIRATION_SECS = 86400

ITEM_PIPELINES = {"funcionarios_publicos.core.pipelines.FechaPipeline": 300}

FEED_EXPORTERS = {
    "csv": "funcionarios_publicos.core.exporters.SemiColonCsvItemExporter",
}

TWISTED_REACTOR = "twisted.internet.selectreactor.SelectReactor"
