"""
Url manipulation with mysql
"""
import sys
import time
import datetime
import threading
import Queue

from webspider.settings.default_params import default_url_db
from webspider.utils.connect import connect
from webspider.utils.tools import field2sql
from webspider.trace.trace import trace
from webspider.core.controler import Controler
from webspider.exception.SpiderException import ProgramExit

from webspider.settings.default_params import URL_QUEUE_MAX_SIZE
from webspider.settings.default_params import QUEUE_TIMEOUT

class UrlServer(object):
  def __init__(self, db_config):
    self.db_type = db_config.get("type", 'mysql')
    self.db_config = db_config
    self.tablename = db_config.get("tablename", "")
    self.db = connect(self.db_type, self.db_config)

  def is_alive(self):
    """check weather server(mysql) is connected"""
    return self.db.isAlive()

  def count(self):
    """get item count of table"""
    sql = 'select count(1) from {0}'.format(self.tablaname)
    self.db.execute(sql)
    return self.db.fetchone()

  def truncate(self):
    """ truncate the table. tip: used for test
    """
    sql = 'truncate {0}'.format(self.tablename)
    self.db.execute(sql)
    trace.info("MYSQL",
           "Url Table `{0}` has been truncated".format(self.tablename))

  def query(self, sql):
    self.db.execute(sql)
    while 1:
      rows = self.db.fetchmany(5000)
      if not rows:
        break
      for row in rows:
        yield row

  def close(self):
    if self.is_alive(): self.db.close()

  def __del__(self):
    self.close()
    trace.info("EXIT", "Server Name: {0}".format(self.__class__))

class UrlFetchServer(UrlServer):
  def __init__(self, db_config):
    super(UrlFetchServer, self).__init__(db_config)
    self.fetch_url_sql = \
        "select id, url from {0} where is_fetched = 0 limit {1}"
    self.update_url_fetched = "update {0} set is_fetched=1 where id in ({1})"
    self.url_queue = Queue.Queue(URL_QUEUE_MAX_SIZE)
    # when queue size is below `self.url_queue_insert_size`, fetch urls
    self.url_queue_insert_size = int((URL_QUEUE_MAX_SIZE-1.0)/2)
    # fetch size from mysql
    self.url_fetch_size = int(URL_QUEUE_MAX_SIZE/2)
    # fetch cnt
    self.fetched_url_cnt = 0
    # sleep time. when Queue is full or fetching no data, program waiting time
    self.sleep_time = 1

  def __query_urls(self):
    """ query urls from mysql
    """
    #if Controler.getExitCode() == 1:
    #  return []
    sql = self.fetch_url_sql.format(self.tablename, self.url_fetch_size)
    self.db.execute(sql)
    # update `is_fetched` of fetched urls
    items = self.db.fetchall()
    if items: # maybe result is ()
      ids = ','.join([field2sql(t[0]) for t in items])
      sql = self.update_url_fetched.format(self.tablename, ids)
      self.db.execute(sql)
      self.db.commit()
    return items

  def get_url(self):
    """ get one url from url queue
    """
    flag = 1
    try:
      # id, url
      item = self.url_queue.get(timeout=QUEUE_TIMEOUT)
      flag = 0
    except Queue.Empty, ex:
      return ()
    id, url = item
    self.fetched_url_cnt += 1
    return id, url

  def start_url_queue(self):
    s = threading.Thread(target=self.__start_url_queue, args=())
    s.setDaemon(True)
    s.start()

  def __start_url_queue(self):
    while 1:
      if Controler.getExitCode() == 1:
        trace.info("EXIT",
          "urlServer's Queue Exit, Controler.getExitCode() is True")
        return
      if self.url_queue.qsize() < self.url_queue_insert_size:
        items = self.__query_urls()
        for item in items:
          ok_flag = 1
          while ok_flag:
            if Controler.getExitCode() == 1:
                trace.info("EXIT",
                      "urlServer's Queue Exit, Controler.getExitCode() is True")
                return
            try:
              self.url_queue.put(item, timeout = QUEUE_TIMEOUT)
              ok_flag = 0
            except Queue.Full, ex:
              traceback.print_exc()
              time.sleep(self.sleep_time)
        if not items:
          time.sleep(self.sleep_time)
      else:
        time.sleep(self.sleep_time)

  def get_url_fetched_cnt(self):
    """ return url count whici is fetched
    """
    return self.fetched_url_cnt

  def get_url_queue_cnt(self):
    """ return the url queue size
    """
    return self.url_queue.qsize()

class UrlUpdateServer(UrlServer):
  def __init__(self, db_config):
    super(UrlUpdateServer, self).__init__(db_config)
    self.update_url_sql = 'update {0} set {1} where {2}'
    self.insert_url_sql = 'insert ignore into {0}(url, add_time) values {1}'
    self.insert_door_url_sql = 'insert ignore into {0}(id, url, add_time) values {1}'

  def _update(self, where_dic, update_dic):
    """ update one item
    """
    where_str = ','.join(["{0}={1}".format(t[0], field2sql(t[1]))
                    for t in where_dic.items()])
    update_str = ','.join(["{0}={1}".format(t[0], field2sql(t[1]))
                    for t in update_dic.items()])
    sql = self.update_url_sql.format(self.tablename, update_str, where_str)

    self.db.execute(sql)
    self.db.commit()

  def updateFetchedUrl(self, id):
    """ update field `is_fetched` in mysql
    """
    self._update(where_dic={"id":id}, update_dic={"is_fetched":1})

  def updateFinishedUrl(self, id):
    """ update field `is_finished` of url in mysql
    """
    self._update(where_dic={"id":id}, update_dic={"is_finished":1})

  def insertNewUrls(self, urls):
    """ url is list whose element's type is (`url`, `add_time`)
    url id would be allocated automatically in mysql
    """
    if not urls: return
    values = ','.join(['(' + ','.join([field2sql(t) for t in url]) + ')'
                       for url in urls])
    sql = self.insert_url_sql.format(self.tablename, values)
    self.db.execute(sql)
    self.db.commit()

  def insertDoorUrls(self, items):
    """ url is list whose element is (`id`, `url`, `add_time`)
    """
    if not items: return
    values = ','.join(['(' + ','.join([field2sql(t) for t in url]) + ')'
                       for url in items])
    sql = self.insert_door_url_sql.format(self.tablename, values)
    self.db.execute(sql)
    self.db.commit()

  def reset_url_is_fetched(self):
    sql = 'update {0} set is_fetched = 0 where is_finished = 0'.format(
          self.tablename)
    self.db.execute(sql)
    self.db.commit()

def __test__():
  db = UrlUpdateServer(URL_DB_CONFIG)
  db.updateFetchedUrl(1)

if __name__ == '__main__':
  __test__()


