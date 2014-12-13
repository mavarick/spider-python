# -*- coding: utf-8 -*-
"""
Mysql api
"""

import MySQLdb

class MysqlApi(object):
    def __init__(self):
        self.conn = None
        self.cursor = None
    def Connect(self, host, port, user, passwd, db, charset = None):
        '''链接MYSQL'''
        charset = (charset is None) and 'utf8' or charset
        self.conn = MySQLdb.connect(host = host, db = db,
                        user = user, port = port, passwd = passwd,
                        charset = charset, use_unicode='True')
        self.cursor = self.conn.cursor()
        #self.get_cursor()

    def get_cursor(self):
        if not self.cursor:
            self.cursor = self.conn.cursor()

    def execute(self, sql):
        '执行Mysql Sql语句'
        self.get_cursor()
        #print sql
        self.cursor.execute(sql)
        self.conn.commit()
    
    def commit(self):
        self.conn.commit()

    def fetchmany(self, count):
        result = self.cursor.fetchmany(count)
        return result

    def fetchall(self):
        result = self.cursor.fetchall()
        return result

    def fetchone(self):
        result = self.cursor.fetchone()
        return result

    def truncate(self, tablename):
        cmd = 'truncate %s' % tablename
        self.execute(cmd)

    def load_from_txt(self, filepath, tablename, replace=True, field_term='\\t'):
        '''把数据从文件中load进入数据库'''
        if replace == True:
            sql = "LOAD DATA LOCAL INFILE '%s' REPLACE INTO TABLE %s CHARACTER SET UTF8 FIELDS TERMINATED BY " \
                    "'%s' ENCLOSED BY '%s'" % (filepath, tablename, field_term, '')
        else:
            sql = "LOAD DATA LOCAL INFILE '%s' IGNORE INTO TABLE %s CHARACTER SET UTF8 FIELDS TERMINATED BY " \
                    "'%s' ENCLOSED BY '%s'; " % (filepath, tablename, field_term, '')
        predo = 'SET max_error_count = 0; '
        self.execute(predo)
        self.execute(sql)

    def load_to_txt(self, tablename, filepath,fields = ['*'], field_term = '\\t'):
        '''把表中指定字段的数据load进入本地文件
        指定的fields为字符串列表或者是*
        这个地方可能会涉及到写权限问题
        '''
        sql = "select %s INTO OUTFILE '%s' FIELDS TERMINATED BY '%s' " \
                "OPTIONALLY ENCLOSED BY '' LINES TERMINATED BY '\\n' " \
                "FROM %s" % (','.join(fields), filepath, field_term, tablename)
        self.execute(sql)
    
    def is_table_exist(self, tablename):
        """ check weather table is exist 
        """
        sql = "show tables"
        self.execute(sql)
        tables = []
        for item in  self.fetchall():
            tables.append(str(item[0]))
        return tablename in tables

    def isAlive(self):
        '''检查链接是否存活'''
        flag = 0
        try:
            self.conn.ping()
            flag = 1
        except Exception, ex:
            pass
        return flag
    def close(self):
        '''close the connection'''
        if self.cursor:
            self.cursor.close()
        self.conn.close()


def __test__():
    host = '127.0.0.1'
    port = 3306
    user = 'root'
    password = ''
    charset = 'utf8'
    db = 'liuxf'
    t = MysqlApi()
    t.Connect(host, port , user, password, db, charset)
    print t
    items =[(1, 'http://www.cz88.net/proxy/index.aspx'), (2, 'http://www.cz88.net/proxy/http_2.aspx'), (3,
'http://www.cz88.net/proxy/http_3.aspx'), (4, 'http://www.cz88.net/proxy/http_4.aspx'), (5,
'http://www.cz88.net/proxy/http_5.aspx'), (6, 'http://www.cz88.net/proxy/http_6.aspx'), (7,
'http://www.cz88.net/proxy/http_7.aspx'), (8, 'http://www.cz88.net/proxy/http_8.aspx'), (9,
'http://www.cz88.net/proxy/http_9.aspx'), (10, 'http://www.cz88.net/proxy/http_10.aspx'), (11,
'http://www.cnproxy.com/proxy1.html'), (12, 'http://www.cnproxy.com/proxy2.html'), (13,
'http://www.cnproxy.com/proxy3.html'), (14, 'http://www.cnproxy.com/proxy4.html'), (15,
'http://www.cnproxy.com/proxy5.html'), (16, 'http://www.cnproxy.com/proxy6.html'), (17,
'http://www.cnproxy.com/proxy7.html'), (18, 'http://www.cnproxy.com/proxy8.html'), (19,
'http://www.cnproxy.com/proxy9.html'), (20, 'http://www.cnproxy.com/proxy10.html'), (21,
'http://www.cnproxy.com/proxyedu1.html'), (22, 'http://www.cnproxy.com/proxyedu2.html'), (23,
'http://www.site-digger.com/html/articles/20110516/proxieslist.html'), (25,
'http://www.free998.net/daili/httpdaili/8949.html'), (26, 'http://www.free998.net/daili/httpdaili/8949_2.html'), (27,
'http://www.free998.net/daili/httpdaili/8949_3.html'), (29, 'http://www.free998.net/daili/httpdaili/8947.html')]
    sql = "insert ignore into url(id, url) values(%s, '%s')" 
    for item in items:
        sql_item = sql % tuple(item)
        print sql_item
        t.execute(sql_item)

if __name__=='__main__':
    __test__()
