#!/usr/bin/env python
#encoding:utf8

"""
cookie server for webspider
"""
import os
import cookielib
from webspider.utils.tools import read_dir
import webspider.trace.trace as trace

class cookieServer(object):
  def __init__(self, app_name, cookie_info):
    """ cookie server.

    actually, cookie directory is given and all cookie filenames 
    are read, and return just one cookie

    if app_name is given: the apps/{appp_name}/cookie will be added to cookie paths.
    if paths is given: each path in paths will be added to cookie_paths
    @params: app_name: appname, string
    @params: path: cookie path, list
    @params: start: cookie file name should start with
    @params: end: cookie file name should end with
    @params: method  = random|wheel, string
      if random: select one cookie path from list randomly. DEFAULT used
      if wheel : select one cookie path from weighted list, cosidering 
          weight of path(larger the weight is, larger the possibility to be used is)
    RETURN:
      use different random strategy to get one random cookie file(relevant path)

    USAGE:
      cs = cookieServer()
      cs.load(app_name, cookie_paths, start, end, method)
      cs.get_cookie()
    """
    self.appname = appname
    self.cookie_path = cookie_info["path"]
    self.cookie_start = cookie_info["start"]
    self.cookie_end   = cookie_info["end"]
    self.cookie_method = cookie_info["method"]
    
    if self.cookie_method == 'random':
      from webspider.utils.algos import random_select
      self.select_fun = random_select
    else:
      raise Exception("NoRandomSelectorError, name: {0}".format(method))
    # read the cookie files
    self.cookie_files = self._read_cookie_files()
  
  def _read_cookie_files(self):
    """ cookie file endswith '.cj'
    """
    files = []
    for path in self.cookie_path:
      cookie_files = [f for f in read_dir(path, 
                                          start=self.cookie_start, 
                                          end=self.cookie_end)]
      files.extend(cookie_files)
    return files

  def get_cookie(self):
    """ return one cookie file path
    """
    cookie_file = self.select_fun(self.cookie_files)
    cj = cookielib.LWPCookieJar()
    if cookie_file and os.path.exists(cookie_file): cj.load(cookie_file)
    return cj
      
  def __del__(self):
    trace.trace.info("EXIT", "Server Name: {0}".format(self.__class__))
