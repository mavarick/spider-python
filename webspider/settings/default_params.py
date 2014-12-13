"""
global params
"""

# url database
default_url_db = {"host":       "127.0.0.1",
          "port":       3306,
          "username":   "root",
          "password":   "",
          "database":   "liuxf",
          "charset":    "utf8",
          "tablename":    "url"}

# proxy database
default_proxy_db = {"host":       "127.0.0.1",
          "port":       3306,
          "username":   "root",
          "password":   "",
          "database":   "liuxf",
          "charset":    "utf8",
          "tablename":    "proxy"}

# Enhanced Queue params
DEFAULT_QUEUE_SIZE = 1000          # default queue size
DEFAULT_QUEUE_TIMEOUT = 0.0001     # default queue timeout

# Links pattern
RE_PATTERN_URL = [
        (r'href\s*=\s*(\'|\")(.+?)(\1)', 2), # represent the 2nd brackets,
                                             # in use ,should be result[1]
    						]

# log config file relative path
TRACE_LOG_CONF = r"./webspider/trace/log.conf"
APP_LOG_PATH   = r"./logs/run.log"
LOGGER_KEY = "root"
# Url Queue maxsize
URL_QUEUE_MAX_SIZE = 100
# Opener timeout for openning one url
URL_OPEN_TIMEOUT = 5

# monitor relative params
# Monitor Info Queue length, which decides exit time when program exits
MONITOR_QUEUE_LEN = 5

# result Queue Max size
RESULT_QUEUE_MAX_SIZE = 100

# get or put timeout for queue
QUEUE_TIMEOUT = 0.001

