""" url opener
"""
import urllib2
import urllib
import socket
import cookielib
import gzip
import os
import StringIO

import requests


def getUrlOpener(type, **args):
    """ return correspont `opener` according to `type`
    default is `buildin`

    @args: `cookie_filename`: cookie file name
            `timeout`: timeout, only valid to 'buildin' and 'requests'
    """
    return {
            "buildin": BuildinOpener,
            "requests": RequestsOpener,
            "mechanize": MechanizeOpener
        }.get(type, BuildinOpener)(**args)

class Opener(object):
    def open(self, url):
        assert 0, "this method must be overwritten"
    def ungzip(self, zip_string):
        gz = gzip.GzipFile(fileobj=StringIO.StringIO(zip_string))
        try:
            return gz.read()
        finally:
            gz.close()

class BuildinOpener(Opener):
    def __init__(self, cookie_filename=None, timeout=5):
        self.timeout = timeout
        socket.setdefaulttimeout(timeout)

    def open(self, url, agent_dic=None, proxy=None, cookie = None, data = {}):
        # proxy
        proxy_support = (urllib2.ProxyHandler() if (not proxy) else
                         urllib2.ProxyHandler({'http':
                              ("http://" + proxy)
                              if not proxy.startswith("http://") else proxy })
                         )
        req = urllib2.Request(url)
        if agent_dic:
            for key, val in agent_dic.iteritems():
                req.add_header(key, val)

        opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler, \
                    urllib2.HTTPCookieProcessor(cookie))
        response = opener.open(req, timeout = self.timeout)
        if response.code != 200:
          raise urllib2.HTTPError(url=url, msg="RESPONSE CODE is not 200")
        content = response.read()
        if not content:
          raise Exception, "NO RESPONSE data. URL:[{0}]".format(url)
        if content.find("DOCTYPE") <0:
          content = self.ungzip(content)
        return content

class RequestsOpener(Opener):
    def __init__(self, cookie_filename=None, timeout=1):
        try:
            import requests
        except ImportError:
            raise
        self.timeout = timeout
        self.cookie_file = cookie_filename
        self.cookie_exist_flag = 0

    def open(self, url, agent_dic=None, proxy=None, cookie = None, **kargs):
        # agent_dic
        headers = {}
        if agent_dic:
            headers = agent_dic
        if proxy:
            proxy = {"http": "http://%s"%proxy if not proxy.startswith("http://") else proxy}
        if cookie:
            cookie = cookielib.FileCookieJar(cookie)
        params = kargs.get("params", None)
        data   = kargs.get("data", None)
        s = requests.Session()
        req = requests.Request('GET', url, headers = headers, cookies = cookie, params = params, data = data)

        prepped = s.prepare_request(req)
        r = s.send(prepped, proxies = proxy, timeout = self.timeout)

        if r.status_code != requests.codes.ok:
             raise Exception, "NO RESPONSE data. URL:[{0}]".format(url)
        return r.text

class MechanizeOpener(Opener):
    def __init__(self, cookie_filename=None):
        try:
            import mechanize
        except ImportError:
            raise
        self.browser = mechanize.Browser()
        self.cj = cookielib.LWPCookieJar()
        if cookie_filename is not None:
            self.cj.load(cookie_filename)
        self.browser.set_cookiejar(self.cj)
        self.browser.set_handle_equiv(True)
        self.browser.set_handle_gzip(True)
        self.browser.set_handle_redirect(True)
        self.browser.set_handle_referer(True)
        self.browser.set_handle_robots(False)

    def open(self, url, agent_dic=None, proxy = None, data=None):
        if agent_dic:
            self.browser.addheaders = agent_dic.items()
        if proxy:
            pass # TODO
        return self.browser.open(url, data=data).read()
    def close(self):
        resp = self.browser.response()
        if resp is not None:
            resp.close()
        self.browser.clear_history()

if __name__ == "__main__":
    #mb = MechanizeOpener()
    #print mb.open("http://www.baidu.com")
    b = BuildinOpener("co.co")
    proxy = "103.3.221.154:8080"
    print b.open("http://10.255.253.14:8871/",proxy=proxy)

