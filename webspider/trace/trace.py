"""
project trace module

the most difference of this module with directly using
`logging.config.fileConfig(configfile)` is the logging file could be
specifed by `log_data_file`

This feature could be completed by modifing logger.root.handlers[1].stream = \
        open("new_log.file", "a")
"""
import sys
import ConfigParser
import logging
import logging.config
import warnings

if __name__ == "__main__":
  import os
  import sys
  sys.path.append(r"E:\data\spider\webspider")
  #from webspider.utils.tools import reload_module
  #reload_module(logging)
#  log_config_file = r"webspider/trace/log.conf"
#  log_data_file   = r"webspider/trace/logs/run.log"
  log_config_file = "log.conf"
  log_data_file = "logs/run.log"

LEVEL_dic = {
               "DEBUG": logging.DEBUG,
               "INFO": logging.INFO,
               "WARNING": logging.WARNING,
               "ERROR": logging.ERROR,
               "CRITICAL": logging.CRITICAL
            }
class LogConfig(object):
  def __init__(self, log_config_file, log_data_file=None):
    self.log_config_file = log_config_file
    self.log_data_file = log_data_file  # for self app
    self.log_config = ConfigParser.RawConfigParser()
    self.log_config.read(self.log_config_file)
    self.logger_prefix = "logger_"
    self.handler_prefix = "handler_"
    self.formatter_prefix = "formatter_"

    self._check_section()
    self._parse_option()

  def _check_section(self):
    # check logger
    self.__check_logger()
    # check  handler
    self.__check_handler()
    # check formatter
    self.__check_formatter()

  def _parse_option(self):
    # parse formatter option
    for formatter, formatter_info in self.formatters.items():
      section_name = formatter_info["section_name"]
      f = self.log_config.get(section_name, "format")
      datefmt = self.log_config.get(section_name, "datefmt")
      self.formatters[formatter]["value"] = logging.Formatter(f, datefmt)
    # parse handlers
    for handler, handler_info in self.handlers.items():
      section_name = handler_info["section_name"]
      handler_class = self.log_config.get(section_name, "class")
      handler_str = self.log_config.get(section_name, "args")
      handler_args = eval(self.log_config.get(section_name, "args"))
      level = self.log_config.get(section_name, "level")
      formatter = self.log_config.get(section_name, "formatter")
      _handler = eval("logging."+handler_class)
      # only FileHandler has file path paramter.
      if isinstance(_handler, logging.FileHandler):
        if self.log_data_file:
          handler_args[0] = self.log_data_file
        else:
          warnings.warn("fileHandler found, but log data file is not specified")
      self.handlers[handler]["value"] = _handler(*handler_args)
      self.handlers[handler]["value"].setLevel(
          LEVEL_dic.get(level.upper(), LEVEL_dic["INFO"]))
      self.handlers[handler]["value"].setFormatter(
          self.formatters[formatter]["value"])
    # parse logger
    for logger, logger_info in self.loggers.items():
      section_name = logger_info["section_name"]
      self.__parse_logger(logger, section_name)

  def __parse_logger(self, logger_name, section_name):
    """
    """
    tuple_items = self.log_config.items(section_name)
    logger = logging.getLogger(logger_name)
    for k, v in tuple_items:
      if k == "handlers":
        handlers = filter(None, [h.strip() for h in v.split(",")])
        for h in handlers:
          logger.addHandler(self.handlers[h]["value"])
      if k == "level":
        logger.setLevel(LEVEL_dic.get(v, LEVEL_dic["INFO"]))
      if k == "propagate" and v:
        logger.propagate = int(v)
      # here other attributes could be added. TODO
    self.loggers[logger_name]['value'] = logger

  def __check_logger(self):
    _loggers = self.log_config.get("loggers", "keys").split(",")
    self.loggers = {}
    for logger in _loggers:
      logger = logger.strip()
      if logger:
        logger_section_name = self.logger_prefix + logger
        if not self.log_config.has_section(logger_section_name):
          raise Exception(
              "ERROR: no logger section name: {0}".format(logger_section_name))
        self.loggers.setdefault(logger, {})
        self.loggers[logger]["section_name"] = logger_section_name
    if not self.loggers:
      raise Exception(
          "ERROR: No logger keys in {0}".format(self.log_config_file))

  def __check_handler(self):
    _handlers = self.log_config.get("handlers", "keys").split(",")
    self.handlers = {}
    for handler in _handlers:
      handler = handler.strip()
      if handler:
        handler_section_name = self.handler_prefix + handler
        if not self.log_config.has_section(handler_section_name):
          raise Exception("ERROR: no handler section name: {0}".format(handler_section_name))
        self.handlers.setdefault(handler , {})
        self.handlers[handler]["section_name"] = handler_section_name
    if not self.handlers:
      raise Exception("ERROR: No handler keys in {0}".format(self.log_config_file))

  def __check_formatter(self):
    _formatters = self.log_config.get("formatters", "keys").split(",")
    self.formatters = {}
    for formatter in _formatters:
      formatter = formatter.strip()
      if formatter:
        formatter_section_name = self.formatter_prefix + formatter
        if not self.log_config.has_section(formatter_section_name):
          raise Exception("ERROR: no formatter section name: {0}".format(formatter_section_name))
        self.formatters.setdefault(formatter, {})
        self.formatters[formatter]["section_name"] = formatter_section_name
    if not self.formatters:
      raise Exception("ERROR: No formatter keys in {0}".format(self.log_config_file))

  def getLogger(self, logger_name="root"):
    return self.loggers[logger_name]['value']


class Trace(object):
  def __init__(self, log_config_file, log_key="root", log_data_file=None):
    self.log_config_file = log_config_file
    self.log_data_file   = log_data_file
    self.log_key = log_key
    Log = LogConfig(self.log_config_file, self.log_data_file)
    self.logger = Log.getLogger(self.log_key)

  def info(self, key, info):
    self.logger.info("[{0}]: {1}".format(key, info))
  def error(self, key, err_info):
    self.logger.error("[{0}]: {1}".format(key, err_info))
  def warn(self, key, warn_info):
    self.logger.warn("[{0}]: {1}".format(key, warn_info))

__default_log_file = r"webspider/trace/log.conf"
trace = Trace(__default_log_file)

def test():
  log_key = "root"
  print "{0}:{1}".format(log_config_file, os.path.exists(log_config_file))
  t = Trace(log_config_file, log_key, log_data_file)
  t.info("TEST TRACE", "OK")

if __name__ == "__main__":
  test()


