#-*- coding: utf-8 -*-
""" spider
"""
import os
import sys
import time
import datetime
import threading
import traceback
import urllib2
import socket

from urllib2 import URLError

from webspider.settings.default_params import MONITOR_QUEUE_LEN
from webspider.settings.default_params import TRACE_LOG_CONF, APP_LOG_PATH, LOGGER_KEY
# trace
import webspider.trace.trace as trace

from webspider.url.urlServer import UrlFetchServer, UrlUpdateServer
from webspider.core.handler import UrlHandler
from webspider.core.controler import Controler
#from webspider.core.content import get_content_server
from webspider.content.contentServer import getContentServer

from webspider.exception.SpiderException import PageErrorException,ProgramExit
from webspider.utils.tools import reload_module

lock = threading.Lock()

# PARAMETERS
MONITOR_EXIT_QUEUE_LEN = 3

class spider(object):
  def __init__(self, appname):
    self.appname = appname
    self.base_dir = os.getcwd()
    app_dir = os.path.join(self.base_dir, "webspider", "apps", appname)
    sys.path.append(app_dir)
    self.Params = __import__("Params")
    self.Parse = __import__("Control")
    self.Tools = __import__("Tools")
    # trace configure
    log_conf_file = os.path.join(self.base_dir, TRACE_LOG_CONF)
    log_data_file = os.path.join(app_dir, APP_LOG_PATH)
    logger_key = LOGGER_KEY
    global trace
    trace.trace = trace.Trace(log_conf_file, logger_key, log_data_file)
    # start the urlServer
    self.urlDb_config = self.Params.URL_DB_CONFIG
    self.urlFetchServer = UrlFetchServer(self.urlDb_config)
    self.content_config = self.Params.CONTENT_CONFIG
    # start the urlHandler
    self.urlHandler = UrlHandler(appname, self.Params, self.Parse, self.Tools)
    # Door url
    self.door_urls = self.Params.DOOR_URLS
    trace.trace.info("PARAMS", "Door Urls: {0}".format(self.door_urls))
    # thread number
    self.thread_num = self.Params.THREAD_NUM
    trace.trace.info("PARAMS", "Threads Number: {0}".format(self.thread_num))
    # Monitor Info printing interval
    self.print_info_interval = self.Params.PRINT_INTERVAL
    # sleepting time duration when eath thread get empty url from UrlServer
    self.time_sleep_fetch_empty_url = self.Params.SLEEP_TIME_FETCH_EMPTY_URL
    trace.trace.info("PARAMS",
           "Print Info Interval: {0}s".format(self.print_info_interval))
    self.prepare_monitor()

  def prepare_monitor(self):
    """ prepare the monitor statistics
    """
    self.url_monitor={
        "num_fetched_url": 0,   # number of fetched url
        "num_queue_url": 0,     # number or url in urlFetchedServer's queue
        "num_err_server": 0,    # e.x. timeout error, HTTPError, URLError
        "num_err_page": 0,      # number of err pages, which contains words in `ERROR_PAGES`
        "num_good_page": 0,     # number of normal pages.
        }

    self.threads_monitor = {
        "num_url_handled": [0] * self.thread_num, # handling url number
        "is_work": [0] * self.thread_num,   # signal weather thread in processing
        }
    self.monitor_exit_queue = [0] * MONITOR_EXIT_QUEUE_LEN

  def monitor(self):
    """ monitor the status of app

    1, relevant number of url fetching.
    2, threads info.
    """
    st = time.time()
    self.run_time = 0

#    self.monitor_info = [None] * self.MonitorQueueLen
    while 1:
      try:
        if Controler.getExitCode() == 1:
          self.print_info()
          return
        # url fetched cnt
        self.url_monitor["num_fetched_url"] = \
                  self.urlFetchServer.get_url_fetched_cnt()
        # url queue cnt
        self.url_monitor["num_queue_url"] = \
                  self.urlFetchServer.get_url_queue_cnt()
        et = time.time()
        self.run_time = et - st
#        self.M_num_threads = '|'.join(map(str, self.M_threads_status))
        self.print_info()

        if (not any(self.threads_monitor["is_work"]) and
            self.url_monitor["num_queue_url"] == 0):
          # bug when first contidion is True and second condition is False, TODO
          self.monitor_exit_queue.append(1)
          self.monitor_exit_queue.pop(0)
        if all(self.monitor_exit_queue):
          trace.trace.info("NORMALEXIT",
                     "Program Exit for url in queue is empty")
          Controler.setExitCode(1)
      except KeyboardInterrupt, ex:
        self.prompt()
        Controler.setExitCode(1)
      except:
        traceback.print_exc()
        Controler.setExitCode(1)
      time.sleep(self.print_info_interval)

  def print_info(self):
    trace.trace.info("MONITOR",
               ("{0:.1f}s: URLINFO: nF[{1[num_fetched_url]}], "+
                              "nQ[{1[num_queue_url]}], "+
                              "nSE[{1[num_err_server]}], "+
                              "nPE[{1[num_err_page]}], "+
                              "nGood[{1[num_good_page]}] " +
              " THREADinFO: nURL[{2}], STATUS[{3}]").format(
              self.run_time,
              self.url_monitor,
              "|".join(list(map(str, self.threads_monitor["num_url_handled"]))),
              "|".join(list(map(str, self.threads_monitor["is_work"]))))
              )

  def prompt(self):
    print """
    r) reload `params` and `parse`
    e) exit
    other) continue

    NOTICE: SUB THREADS CONTINUE TO RUN DURING YOUR CHOOSING!
    """
    choice = raw_input("choose: ")
    print(">> Your choice: {0}".format(choice))
    handler_dic = {
          'r': self.update_context,
          'e': exit,            # system exit
          'c': lambda x=0:x,    # just for continue
          }
    handler_dic.get(choice.lower(), handler_dic['c'])()

  def start(self):
    print "Insert into Door Urls..."
    self.insertDoorUrls()
    # start the url Queue
    print "Start UrlFetchServer Queue..."
    self.urlFetchServer.start_url_queue()
    threads = []
    print "Start Threads..."
    i = 0
    while i < self.thread_num:
      threads.append(
          threading.Thread(target=self.spider, args=(i,))
        )
      i += 1
    for t in threads:
      t.setDaemon(True)
    for t in threads:
      t.start()
    # start the monitor
    print "Start Monitor..."
    self.monitor()
    self.urlFetchServer.close()
    #self.check_url_status()

  def spider(self, thread_num=0):
    urlUpdateServer = UrlUpdateServer(self.urlDb_config)
    contentSaveServer = getContentServer(
                                         self.appname,
                                         self.content_config["type"],
                                         self.content_config)
    while 1:
      self.threads_monitor["is_work"][thread_num] = 0
      if Controler.getExitCode() == 1:
        trace.trace.info("EXIT",
              "Thread [{0}] exit, for Controler.ExitCode is True".format(thread_num))
        return
      try:
        # get one url as formation, (id, url)
        url_item = self.urlFetchServer.get_url()  # self.urlFetchServer
        if not url_item:
          time.sleep(self.time_sleep_fetch_empty_url)
          continue
        url_id, url = url_item
        self.threads_monitor["is_work"][thread_num] = 1
        # update is_fetched field in db
        urlUpdateServer.updateFetchedUrl(url_id)

        # handle the url
        _links, content = self.urlHandler.gogo(url) # self.urlHandler
        add_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # insert new links to db
        links = [(link, add_time) for link in _links]
        if links:
          urlUpdateServer.insertNewUrls(links)

        # output the content
        contentSaveServer.save(url_id, content)

        # update the url table
        urlUpdateServer.updateFinishedUrl(url_id)

        with lock:
          self.threads_monitor["num_url_handled"][thread_num] += 1
          self.url_monitor["num_good_page"] += 1
      # Self-Defined Exceptions
      # TODO, `requests` or `mechanize` maybe not return `urllib2` excptions
      except urllib2.URLError, ex:
        trace.trace.error("URLError",
              "URLError when handling `URL`[{0}] `url_id`[{1}] `thread_num`[{2}]"
              .format(url, url_id, thread_num))
        with lock:
          self.url_monitor["num_err_server"] +=1
      except urllib2.HTTPError, ex:
        trace.trace.error("HTTPError",
              "HTTPError when handling `URL`[{0}] `url_id`[{1}] `thread_num`[{2}]"
              .format(url, url_id, thread_num))
        with lock:
          self.url_monitor["num_err_server"] +=1
      except socket.timeout, ex:
        trace.trace.error("SOCKET_TIMEOUT",
              "TIMEOUT when handling `URL`[{0}] `url_id`[{1}] `thread_num`[{2}]"
              .format(url, url_id, thread_num))
        with lock:
          self.url_monitor["num_err_server"] +=1
      except PageErrorException, ex:
        trace.trace.error("PAGEError",
              "PageError when handling `URL`[{0}] `url_id`[{1}] `thread_num`[{2}]"
              .format(url, url_id, thread_num))
        with lock:
          self.url_monitor["num_err_page"] +=1
      except ProgramExit, ex:
        return
      except:
        trace.trace.error("UNKNOWNError",
                    "PageError when handling `URL`[{0}] `url_id`[{1}] `thread_num`[{2}], error_info: {3}"
                    .format(url, url_id, thread_num, traceback.format_exc()))

      finally:
        pass
    urlUpdateServer.close()
    contentSaveServer.close()

  def insertDoorUrls(self):
    """ insert door urls to Mysql
    """
    urlDoorServer = UrlUpdateServer(self.urlDb_config)
    add_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _items = []
    for item in self.door_urls:
      id, url = item
      _items.append((id, url, add_time))
    urlDoorServer.insertDoorUrls(_items)
    trace.trace.info("DOOR_INSERSION_EXIT", "Insert Door Done and server exit ..")

  def check_url_status(self):
    """ check the url data consistence

    1, is_fetched must be 0 is is_finished = 0
    """
    urlServer = UrlUpdateServer(self.urlDb_config)
    urlServer.check_url_status()

  def update_context(self):
    trace.trace.info("MODULERELOAD", "reloading `Params` and `Parse`")
    reload_module(self.Params, recursion=True)
    reload_module(self.Parse, recursion=True)
    reload_module(self.Tools, recursion=True)

