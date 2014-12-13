"""
check proxy 
"""
import sys
from webspider.proxy.proxyServer import ProxyServer

try:
    appname = sys.argv[1]
except Exception, ex:
    appname = ''

CONNECTION_CNT = 3
PROXY_TEST_URL = 'http://www.baidu.com'
PROXY_TEST_TIMEOUT = 5


def check_proxy():
    print "APPNAME: %s"% appname
    if appname:
        check_app_proxy()
    else:
        check_default_proxy()

def check_app_proxy():
    app_dir = "./webspider/apps/"+appname
    sys.path.append(app_dir)
    Params = __import__("Params")
    proxy_config = Params.PROXY_CONFIG
    proxy_db = ProxyServer(proxy_config)
    print "Start Check Proxy Info in app : %s" % appname
    print "Proxy Db info: %s" % proxy_config
    proxy_db.check_proxy(CONNECTION_CNT, PROXY_TEST_URL, PROXY_TEST_TIMEOUT)
    print "Done"

def check_default_proxy():
    from webspider.settings.default_params import default_proxy_db
    proxy_db = ProxyServer(default_proxy_db)
    print "Start Check Proxy Info in default settings"
    print "Proxy Db info: %s" % default_proxy_db
    proxy_db.check_proxy(CONNECTION_CNT, PROXY_TEST_URL, PROXY_TEST_TIMEOUT)
    print "Done"
    
if __name__ == "__main__":
    check_proxy()
