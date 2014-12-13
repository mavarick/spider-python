# -*- coding:utf-8 -*-
'''
content server, mainly for saving data
'''
import time
import traceback
import datetime
import threading
import Queue

import webspider.trace.trace as trace

from webspider.core.controler import Controler
from webspider.utils.connect import connect
from webspider.exception.SpiderException import ProgramExit
from webspider.utils.tools import field2sql

from webspider.settings.default_params import RESULT_QUEUE_MAX_SIZE
from webspider.settings.default_params import QUEUE_TIMEOUT

def getContentServer(appname, type, db_info):
    return {
        "mysql": ContentMysqlServer,   
        }.get(type)(db_info)

class ContentServer(object):
    def __init__(self, db_config):
        self.db_config = db_config
    
    def save(self, id, items):
        """ item are list of element with type : (title, tags, content)
        """
        assert 0, "save function should be overwritten"
    
    def close(self):
        assert 0, "this method should be overwritten"
        
    def __del__(self):
        self.close()
        trace.trace.info("EXIT", "Server Name: {0}".format(self.__class__))

class ContentMysqlServer(ContentServer):
    def __init__(self, db_config):
        super(ContentMysqlServer, self).__init__(db_config)
        self.db_type = db_config.get("type", 'mysql')
        self.db_config = db_config
        self.tablename = db_config.get("tablename", "")
        self.db = connect(self.db_type, self.db_config)
        
        self.insert_content_sql = (
           "insert ignore into {0}(url_id, title, type, content, add_time) values {1}")
    
    def save(self, id, items):
        """ items should be list of content
        """
        add_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        value_lst = []
        for item in items:
            title, type, info = item
            if not title: continue
            value = '(' + ','.join(map(field2sql, [id, title, type, info, add_time])) + ')'
            value_lst.append(value)
        if not value_lst: return
        sql = self.insert_content_sql.format(self.tablename, ','.join(value_lst))
        self.db.execute(sql)
        self.db.commit()
        
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
        print("Url Table `{0}` has been truncated".format(self.tablename))
    
    def close(self):
        if self.is_alive(): self.db.close()
