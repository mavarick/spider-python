#encoding:utf8
"""
PROXY API FOR CONSUMER
"""
import webspider.trace.trace as trace

from webspider.utils.connect import connect
from webspider.utils.algos import wheel_select, random_select
from webspider.exception.SpiderException import NoProxyDataException


# [EXTERNAL PARAMETERS]
# for max connection time of proxy
PROXY_CONNECTION_MAX_TIME = 10

def getProxyServer(appname, type, db_info):
  return {
        "mysql": ProxyMysqlServer,
        "lcoal": ProxyLocalServer
        }.get(type, ProxyServer)(db_info)

class ProxyServer(object):
  def __init__(self, db_info):
    self.db_config = db_info
    self.total_proxy = self.get_total_proxy()
    self.avail_proxy = self.get_avail_proxy()
  def get_total_proxy(self):
    """get total proxy and save them in variance"""
    assert 0, "this method must be overwritten"
  def get(self, method="wheel"):
    """get one proxy"""
    return ()
  def get_avail_proxy(self):
    """update avaialable proxy, which should be saved in variance"""
    assert 0, "this method must be overwritten"
  def update_proxy(self):
    """update proxy and save the new data"""
    assert 0, "this method must be overwritten"
  def __del__(self):
    trace.trace.info("EXIT", "Server Name: {0}".format(self.__class__))
    
class ProxyMysqlServer(ProxyServer):
  def __init__(self, db_info):
    super(ProxyMysqlServer, self).__init__(db_info)
    self.db_type = self.db_config['type']
    self.db = connect(self.db_type, self.db_config)
    self.tablename = self.db_config['tablename']
    self.selection_method = self.db_config['method']
    
  def get_total_proxy(self):
    sql = "select id, proxy, connect_time from {0}".format(self.tablename)
    self.db.execute(sql)
    items = self.db.fetchall()
    if len(items) == 0:
       raise NoProxyDataException, "No data in table: %s" % self.tablename
    return items
   
  def get_avail_proxy(self):
    return [item for item in self.total_proxy 
                if item[2]<PROXY_CONNECTION_MAX_TIME]
  
  def get(self):
    if self.selection_method == 'random':
      return random_select(self.avail_proxy)
    elif self.selection_method == 'wheel':
      conn_time_weights = [1/t for t in self.proxy_conn_times]
      return wheel_select(self.avail_proxy, conn_time_weights)
    raise Exception("Wrong select method for proxy, method name: '%s'" % method)
  
  def update_proxy(self):
    """reload the relavant data"""
    self.total_proxy = self.get_total_proxy()
    self.avail_proxy = self.get_avail_proxy()
  
class ProxyLocalServer(ProxyServer):  # TODO
  def __init__(self, db_info):
    super(ProxyLocalServer, self).__init__(db_info)
