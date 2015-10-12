"""
run the app and open the monitor

default: run app
`clear`: clear the url server and content server
"""

import os
import sys
import traceback
from webspider.core.spider import spider

USAGE = """
USAGE:
    # run the app
        python runapp.py appname run
    # clear the database
        python runapp.py appname clear
    # some tools
        python runapp.py appname tool
        # tool includes:
            1, reset is_fetched =0 if is_finished = 0
            2, generate cookies
    # test parsing function
        python runapp.py appname testparse url

"""

try:
    appname = sys.argv[1]
    run_flag = sys.argv[2]
except IndexError, ex:
    print(USAGE)
    sys.exit(0)

app_dir = "./webspider/apps/"+appname
sys.path.append(app_dir)

def main():
    if run_flag == 'run':
        # run the app
        sp = spider(appname)
        sp.start()
    elif run_flag == 'clear':
        clear(appname)
    elif run_flag == 'tool':
        extend_tools()
    elif run_flag == 'testparse':
        # this is not in `tool` for considering of high use frequency.
        test_parse()
    else:
      print(USAGE)

def clear(appname):
    # clear url server and content_server
    Params = __import__("Params")
    from webspider.content.contentServer import getContentServer
    from webspider.url.urlServer import UrlServer
    urlDb_config = Params.URL_DB_CONFIG
    content_config = Params.CONTENT_CONFIG
    urlServer = UrlServer(urlDb_config)
    urlServer.truncate()
    contentServer = getContentServer(
                                     appname,
                                     content_config["type"],
                                     content_config)
    contentServer.truncate()

def extend_tools():
    USAGE = """
      1) update data in `url` db. set is_fetched=0 if is_finished = 0;
      2) generate cookies;
      #3) proxy testing;
      e) exit.
    """
    print(USAGE)
    choice = raw_input("choice: ")
    print(">> Your choice: {0}".format(choice))
    handler_dic = {
          "1": reset_url_is_fetched,
          "2": create_cookie,
          "e": sys.exit,
          }
    handler_dic.get(choice, handler_dic['e'])()
    print(" == DONE == ")

def reset_url_is_fetched():
    Params = __import__("Params")
    urlDb_config = Params.URL_DB_CONFIG
    from webspider.url.urlServer import UrlUpdateServer
    urlUpdateServer = UrlUpdateServer(urlDb_config)
    urlUpdateServer.reset_url_is_fetched()

def create_cookie():
    # create cookie directory in app path
    import cookielib
    from webspider.core.opener import BuildinOpener
    cookie_dir = os.path.join(app_dir, "cookie")
    try:
        os.mkdir(cookie_dir)
    except:
        pass
    print("Automatically Generate Cookie in Directory: {0}".format(cookie_dir))
    url = raw_input("From url: ")
    cookie_cnt = int(raw_input("Count: "))
    ok_n = 0
    not_ok_n = 0
    for i in xrange(cookie_cnt):
        cookie_filename = "{0}.cj".format(i+1)
        cookie_filename = os.path.join(cookie_dir, cookie_filename)
        print("COOKIE creating : {0}".format(cookie_filename))
        try:
            cj = cookielib.LWPCookieJar(cookie_filename)
            opener = BuildinOpener()
            opener.open(url, cookie=cj)
            cj.save(ignore_discard=True, ignore_expires=True)
            ok_n +=1
        except Exception, ex:
            traceback.print_exc()
            not_ok_n += 1
            print("Failed..")
    print("Plan: {0}, Success: {1}, Fail: {2}".format(cookie_cnt, ok_n, not_ok_n))

def test_parse():
    from webspider.core.opener import getUrlOpener
    from webspider.proxy.proxyServer import getProxyServer
    from webspider.agent.agentServer import getAgentServer
    from webspider.cookie.cookieServer import cookieServer

    try:
      url = sys.argv[3]
    except:
      print("[ERROR] wrong url")
      print USAGE
      return
    Parse = __import__("Control")
    #opener = getUrlOpener("buildin")
    #opener = getUrlOpener("requests")
    opener = getUrlOpener("mechanize")
    print("Test Url: {0}".format(url))
    print("Open Url")

    base_dir = os.getcwd()
    app_dir = os.path.join(base_dir, "webspider", "apps", appname)
    sys.path.append(app_dir)
    Params = __import__("Params")

    if Params.USE_PROXY_INFO["is_used"]:
      proxy_type = Params.USE_PROXY_INFO["type"]
      proxyServer = getProxyServer(appname,
                                        proxy_type,
                                        Params.USE_PROXY_INFO)
    agentServer = None
    if Params.USE_AGENT_INFO["is_used"]:
      agent_type = Params.USE_AGENT_INFO["type"]
      agentServer = getAgentServer(appname,
                                        agent_type,
                                        Params.USE_AGENT_INFO)
    cookieServer = None
    if Params.USE_COOKIE_INFO["is_used"]:
      cookieServer = cookieServer(appname, Params.USE_COOKIE_INFO)

    proxy_item = proxyServer.get() if proxyServer else None
    proxy = proxy_item[1] if proxy_item else ""
    # agent
    agent_dic = agentServer.get() if agentServer else None
    # cookie
    cookie = cookieServer.get_cookie() if cookieServer else None

    content = opener.open(url, agent_dic = agent_dic,
                            proxy = proxy,
                            cookie = cookie)

    if not content:
        raise Exception, "No opening Responce, Please Check"
    # get relevant function to parse the url content
    print("Parse Url")
    content = Parse.parse(url, content, print_info =True)
    print("Content:")
    print(content)

if __name__ == '__main__':
    main()
