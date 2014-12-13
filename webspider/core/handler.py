"""
main code to get the url content, parse content to get needed text
"""
import re
import sys
reload(sys)
sys.setdefaultencoding("utf8")

import urlparse
from webspider.core.opener import getUrlOpener
from webspider.utils.GetLinks import getLinks
from webspider.utils.tools import trim_url

from webspider.exception.SpiderException import PageErrorException
import webspider.settings.default_params as default_params
from webspider.cookie.cookieServer import cookieServer

from webspider.proxy.proxyServer import getProxyServer
from webspider.agent.agentServer import getAgentServer
from webspider.cookie.cookieServer import cookieServer

class UrlHandler(object):
  def __init__(self, appname, Params, Parse, Tools):
    self.appname = appname
    self.apppath = "webspider/apps/"+appname
    self.proxyServer = None
    if Params.USE_PROXY_INFO["is_used"]:
      proxy_type = Params.USE_PROXY_INFO["type"]
      self.proxyServer = getProxyServer(self.appname, 
                                        proxy_type, 
                                        Params.USE_PROXY_INFO)
    self.agentServer = None
    if Params.USE_AGENT_INFO["is_used"]:
      agent_type = Params.USE_AGENT_INFO["type"]
      self.agentServer = getAgentServer(self.appname,
                                        agent_type, 
                                        Params.USE_AGENT_INFO)
    self.cookieServer = None
    if Params.USE_COOKIE_INFO["is_used"]:
      self.cookieServer = cookieServer(appname, Params.USE_COOKIE_INFO)
    self.url_open_timeout = default_params.URL_OPEN_TIMEOUT
    self.error_pages = Params.ERROR_PAGES
    self.re_valid_url = Params.RE_VALID_URL
    self.re_invalid_url = Params.RE_INVALID_URL
    self.is_url_with_params = Params.URL_WITH_PARAMS
    #
    self.opener = getUrlOpener(Params.OPENER, timeout = self.url_open_timeout) 
    self.content_config = Params.CONTENT_CONFIG
    self.Params = Params
    self.Parse = Parse
    self.Tools = Tools
  
  def gogo(self, url):
    self.url_base = self.getBasePath(url)
    # open url
    page = self.openUrl(url)
    # Website return error_page
    self.checkErrorPage(page)
    # get links to be inserted into Mysql
    links = self.getValidUrls(page)
    # get needed content
    content, content_flag_dic = self.getContent(url, page)
    # extend the links
    links = self.extend_links(url, links, content_flag_dic)
    # extend the content
    content = self.extend_content(url, content, content_flag_dic)
    
    return links, content

  def extend_links(self, url, links, content_flag_dic):
    """ extend the url links
    """
    return self.Tools.extend_links(url, links, content_flag_dic)
  
  def extend_content(self, url, content, content_flag_dic):
    return self.Tools.extend_content(url, content, content_flag_dic)

  def getBasePath(self, url):
    """ get url domain
    """
    url_parse = urlparse.urlparse(url)
    return "%s://%s" % (url_parse.scheme, url_parse.netloc)

  def openUrl(self, url):
    # proxy_id, proxy, connect_time
    proxy_item = self.proxyServer.get() if self.proxyServer else None
    proxy = proxy_item[1] if proxy_item else ""
    # agent
    agent_dic = self.agentServer.get() if self.agentServer else None
    # cookie
    cookie = self.cookieServer.get_cookie() if self.cookieServer else None
    
    return self.opener.open(url, agent_dic = agent_dic, \
                            proxy = proxy,
                            cookie = cookie)

  def checkErrorPage(self, page):
    for re_item in self.error_pages:
      if re.search(re_item, page):
        raise PageErrorException, \
            "ERROR: error page, Page contains '{0}'".format(re_item)

  def getValidUrls(self, page):
    """ get valid links
    """
    links = getLinks(page) 
    result = []
    for link in links:
      ok_flag = 1
      # handle relative url
      if link.startswith(".") \
        or link.startswith("/") \
        or link.strip() in ['', '#']: # /, ./, ../
          link = urlparse.urljoin(self.url_base, link)
      # handle url with parameters
      if not self.is_url_with_params:
        link = self.trim_url_params(link)
        
      # negetive regex
      for pattern in self.re_invalid_url:
        if re.search(pattern, link):
          ok_flag = 0
          break
      if not ok_flag:
        continue
      # positive regex
      for pattern in self.re_valid_url:
        if re.search(pattern, link):
          result.append(link)
          break
    return result

  def trim_url_params(self, link):
    """ elimite the params of url
    """
    items = urlparse.urlparse(link)
    scheme = items.scheme
    netloc = items.netloc
    base_url = scheme + "://" + netloc
    path = items.path
    return urlparse.urljoin(base_url, path)

  def getContent(self, url, page):
    """ parse page, get wanted text depend on url
    """
    return self.Parse.parse(url, page)
