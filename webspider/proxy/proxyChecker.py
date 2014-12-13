#encoding:utf8
"""
1, supply one api to get an proxy
2, check the availibility of proxy
"""
import time
import urllib2
import socket
import traceback

from webspider.core.opener import BuildinOpener
from webspider.utils.algos import avg
from webspider.utils.connect import connect
import webspider.trace.trace.trace as trace

# [EXTERNAL PARAMETERS]
PROXY_TEST_URL = "http://www.baidu.com"
CONNECTION_CNT = 3
PROXY_TEST_TIMEOUT = 10

# keyword
keyword = [
					"UnknownOpenUrlException", # for some unkown exception
					]

class ProxyTester(object):
	def __init__(self, db_info):
		self.db_config = db_info
		self.total_proxy = self.get_total_proxy()
		
	def get_total_proxy(self):
		"""get total proxy and save them in variance"""
		assert 0, "this method must be overwritten"
	
	def test(self):
		"""this method is for reminding users of subclasses"""
		assert 0, "this method must be overwritten"
		
	def _test(self):
		opener = BuildinOpener(timeout=PROXY_TEST_TIMEOUT)
		trace.trace.info("PROXYTEST","PROXY_TEST_URL : %s" % PROXY_TEST_URL)
		trace.trace.info("PROXYTEST","CONNECTION_CNT : %s" % CONNECTION_CNT)
		trace.trace.info("PROXYTEST","PROXY_TEST_TIMEOUT : %s" % PROXY_TEST_TIMEOUT)
		trace.trace.info("PROXYTEST","Start ...")
		for item in self.total_proxy:
			id, proxy, connect_time = item
			conn_times = []
			trace.trace.info("PROXYTEST", "id: %s, proxy: %s" % (id, proxy))
			for i in range(CONNECTION_CNT):
				# TODO, WARN: 101
				st = time.time()
				try:
					res = opener.open(PROXY_TEST_URL, proxy=_proxy)
					et = time.time()
					t = et - st
				except (urllib2.URLError, urllib2.HTTPError, socket.timeout), ex:
					trace.trace.warn("PROXYTEST", "TIMEOUT exception")
					t = 10000
				except Exception, ex:
					trace.trace.warn("PROXYTEST", 
										"UnknownOpenUrlException:"+traceback.format_exc())
					t = 10000
				conn_times.append(t)
			conn_time = avg(conn_times)
			self.update_proxy(id, proxy, conn_time)
			
	def update_proxy(self, id, proxy, conn_time):
		"""update proxy and save the new data"""
		assert 0, "this method must be overwritten"

	def __del__(self):
		trace.trace.info("EXIT", "Server Name: {0}".format(self.__class__))	
		
class ProxyMysqlTester(ProxyTester):
	def __init__(self, db_info):
		super(ProxyMysqlTester, self).__init__(db_info)
		self.db_type = self.db_config['type']
		self.db = connect(self.db_type, self.db_config)
		self.tablename = self.db_config['tablename']
		self.update_sql = 'update {0} set connect_time={1} where id={2}'
		
	def get_total_proxy(self):
		sql = "select id, proxy, connect_time from {0}".format(self.tablename)
    self.db.execute(sql)
    items = self.db.fetchall()
    if len(items) == 0:
       raise NoProxyDataException, "No data in table: {0}".format(self.tablename)
    return items
  
  def test(self):
  	self._test()
  	
  def update_proxy(self, id, proxy, conn_time):
  	"""update proxy info in mysql"""
  	sql = self.update_sql.format(self.tablename, conn_time, id)
  	self.db.execute(sql)
  	self.commit()
		