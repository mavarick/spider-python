"""
python preapp.py appname
create relavant mysql database/tables.
check parse functions
"""
from webspider.utils.connect import connect
from webspider.utils.tools import check_app
from webspider.core.opener import getUrlOpener

import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import shutil
import traceback

try:
    appname = sys.argv[1]
except Exception, ex:
    print "No Appname"
    sys.exit(0)

def pre_app():
    # check app directory
    app_dir = "./webspider/apps/"+appname
    files = [os.path.join(app_dir, "Params.py"),
                os.path.join(app_dir, "Parse.py"),
                os.path.join(app_dir, "Control.py"),
                os.path.join(app_dir, "app_flag")]
    check_dir(app_dir, files)
    # import relevant params
    sys.path.append(app_dir)
    Params = __import__("Params")
    Parse = __import__("Control")
    # Check Url db
    url_db_config = Params.URL_DB_CONFIG
    check_url_db(url_db_config)
    # Check Proxy db
    proxy_config = Params.USE_PROXY_INFO
    check_proxy(proxy_config)
    # Check Content db
    content_config = Params.CONTENT_CONFIG
    check_content_config(content_config)
    # check the opener
    opener = Params.OPENER
    check_opener(opener)
    # ChecK User Agent Server
    use_agent_info = Params.USE_AGENT_INFO
    check_agent(use_agent_info)
    # Check Cookie files
    use_cookie_info = Params.USE_COOKIE_INFO
    check_cookie(use_cookie_info)
    # Check Door urls
    door_urls = Params.DOOR_URLS
    check_door_urls(door_urls)
    # Check the valid url
    re_valid_urls = Params.RE_VALID_URL
    check_valid_urls(re_valid_urls)
    # Check the parse functions
    #check_url_parser(Parse)
    
@check_app("Check App Derecotry")
def check_dir(app_dir, files):
    exit_flag = 0
    for f in files:
        print " %s" % f
        if not os.path.exists(f):
            print "%s does not exist!" % f
            exit_flag = 1
    if exit_flag:
        raise Exception, ("`%s` does not created or created unsuccessfully" %
                             appname)

@check_app("Check Url Config")
def check_url_db(db_config):
    """ check url db, 1, exists? do nothing; create it
    """
    tablename = db_config['tablename']
    type = db_config['type']
    db = connect(type, db_config)
    if db.is_table_exist(tablename):
        print "table `%s` already exists" % tablename
    else:
        # InnoDB, MyISAM
        sql = """
            CREATE TABLE if not exists `%s` (
              `id` int(11) NOT NULL AUTO_INCREMENT,
              `url` varchar(255) NOT NULL unique,
              `add_time` datetime NOT NULL,
              `is_fetched` tinyint(4) NOT NULL DEFAULT '0',
              `is_finished` tinyint(4) NOT NULL DEFAULT '0',
              PRIMARY KEY (`id`)
            ) ENGINE=MyISAM AUTO_INCREMENT=25 DEFAULT CHARSET=utf8
            """  % tablename
        print "Create Table `%s`" % tablename
        db.execute(sql)

@check_app("Check Proxy Config")
def check_proxy(proxy_config):
    if not proxy_config["is_used"]:
        print "Proxy is Not Used"
    else:
        type = proxy_config.get("type", "")
        if not type:
            raise Exception, "`proxy_config` has no key `type`"
        if type == 'mysql':
            db = connect(type, proxy_config)
            tablename = proxy_config['tablename']
            if not db.is_table_exist(tablename):
                raise Exception, "Proxy Table `%s` does't Exist" % tablename

@check_app("Check Content Config")
def check_content_config(content_config):
    type = content_config.get("type")
    if type=="stdout":
        print "parsing content will be print to `stdout`"
    if type =='mysql':
            db = connect(type, content_config)
            tablename = content_config['tablename']
            if db.is_table_exist(tablename):
                print "Table `%s` has already existed" % tablename
            else:
                sql = """
                    CREATE TABLE if not exists `%s` (
                      `id` int(11) NOT NULL AUTO_INCREMENT,
                      `url_id` int(11) NOT NULL,
                      `title` varchar(1000) NOT NULL,
                      `type` varchar(1000) NOT NULL,
                      `content` text,
                      `add_time` datetime NOT NULL,
                      PRIMARY KEY (`id`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
                    """ % tablename
                print "Create Table `%s`" % tablename
                db.execute(sql)

@check_app("Check Opener ...")
def check_opener(opener):
    op = getUrlOpener(opener)
    print "Opener Type: `%s` -> `%s`" % (opener, op)

@check_app("Check Agent")
def check_agent(use_agent):
    if not use_agent["is_used"]:
        print "Agent is not used"
    else:
        try:
            from webspider.agent.agentServer import getAgentServer
            t = getAgentServer(appname, use_agent["type"], use_agent)
        except BaseException, ex:
            raise Exception, "Import Agent Failed!"

@check_app("Check cookie")
def check_cookie(use_cookie_info):
    if not use_cookie_info["is_used"]:
        print "Cookie is not used"
    else:
      for cookie_dir in use_cookie_info["path"]:
        try:
            if not (os.path.exists(cookie_dir)):
                print("[ERROR] cookie path [{0}] doesn't exist".format(cookie_dir))
            else:
                print "Cookie directory[%s] already exists" % cookie_dir
                files = os.path.listdir(cookie_dir)
                print "Cookie Files: %s" % files
        except:
            raise

@check_app("Check door urls")
def check_door_urls(door_url_lst):
    """ open the url if sucessfully
    """
    from webspider.core.opener import BuildinOpener
    opener = BuildinOpener()
    for item in door_url_lst:
        id, url = item
        try:
            print url, 
            opener.open(url)
            print "Done"
        except:
            print "Error"
            traceback.print_exc()
    
@check_app("Check valid Regex of urls")
def check_valid_urls(valid_url_lst):
    """ just print the url
    """
    for url in valid_url_lst:
        print url

#deprecated
@check_app("Check url parser")
def check_url_parser(Parse):
    """ check if url parser if exists.
    
    we'd better to use some url to test the urlParser
    """
    valid_url_lst = Parse.REGISTER_URL_PARSE
    for item in valid_url_lst:
        p, parser = item
        try:
            print p,
            # to get the name of __module__
            func = eval("%s.%s" % (Parse.__name__, parser))
            print func
        except AttributeError, ex:
            print "Error"
            raise Exception, "Parser Error"

if __name__ == "__main__":
    pre_app()

