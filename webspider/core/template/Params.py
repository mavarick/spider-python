#-*- coding:utf-8 -*-
""" params for certain app

"""
# Url Mysql config
URL_DB_CONFIG = {
          "type":       "",     #"mysql",
          "host":       "",     #"127.0.0.1",
          "port":       3306,
          "user":       "",     #"root",
          "passwd":     "",     #3306
          "db":         "",     #"liuxf",
          "charset":    "",     #"utf8",
          "tablename":  ""      #"url"
}

"""
 save the content. Code should be extendable, for example:
  CONTENT_CONFIG = {}  # output to stdout
  CONTENT_CONFIG = {
           'type' : "local",
           'path' : "{absolut path}"
       }
 CONTENT_CONFIG = {
            'type': "mysql",
            ...
        }
"""
CONTENT_CONFIG={
          "type":       "",     #'mysql',
          "host":       "",     #"127.0.0.1",
          "port":       3306,
          "user":       "",     #"root",
          "passwd":     "",
          "db":         "",     #"liuxf",
          "charset":    "",     #"utf8",
          "tablename":  ""      #"spider_content"
}

# proxy Mysql db config. proxy will not be used if {}
USE_PROXY_INFO = {
          "is_used": True, 
          "method": "random",   # selection method: random, wheel
          "type":       "",     #"mysql",
          "host":       "",     #"127.0.0.1",
          "port":       3306,
          "user":       "",     #"root",
          "passwd":     "",     #"password",
          "db":         "",     #"liuxf",
          "charset":    "",     #"utf8",
          "tablename":  ""      #"proxy"
}

# Modify here to Use `use_agent` or not. Absolute path of one app
USE_AGENT_INFO = {
          "is_used": True,
          "method": "random",   # selection method: random
          "type": "local",
          "file": r"E:\data\spider\webspider\webspider\agent\agent.py"
          }

# Add cookie file path to use COOKIE, or not if ''. Absolute path
# cookie file should be local.
USE_COOKIE_INFO = {
          "is_used": True,
          "method": "random",  # selection method: random
          "path":[r'E:\data\spider\webspider\webspider\cookie'],
          "start": "",
          "end": ".cj"
          }

# opener type, opener types are below, see `opener.py`
#   1, "buildin" -> BuildinOpener. use `urllib2` to open one url
#   2, "requests" -> RequestsOpener. use `requests` to open one url
#   3, "mechanize" -> MechanizeOpener. user `mechanize` to open one url
OPENER = "buildin"

# Start url, `id` of start url is 0, then follows
DOOR_URLS = [
        # (id, url)
        (0, "http://www.baidu.com"),
        (1, "http://www.douban.com")
    ]
# error pages. if page content matches any one below, the page is error pages \
#   of site or expired pages. 
# Take Notices: if web page call other web's page, and failed, maybe some block \
#   of page is failed, the content needed is still there! # TODO
ERROR_PAGES = ["页面访问错误", 
               "您访问的页面不存在"
                ]

# regex of urls to be save in URL pool. Maybe here just limit the domian, appropriate
# regulations will demilish the number of url to be inserted into mysql, so here
# should be racked the brain carefully!
RE_VALID_URL = [
        (r"http://www.douban.com"),
    ]
RE_INVALID_URL = [
        #(r"")
    ]
# weather is url saved with params
URL_WITH_PARAMS = True

# Multi threads to run the spider
THREAD_NUM = 2

# Interval of Printing Running info
PRINT_INTERVAL = 5

# sleeping time when no url is fetched from urlServer
SLEEP_TIME_FETCH_EMPTY_URL = 1
