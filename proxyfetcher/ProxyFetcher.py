#!/usr/bin/env python
#encoding:utf8
__author__ = ''

import sys
import re
import urlparse
import hashlib
import pdb
from bs4 import BeautifulSoup as BS
from datetime import datetime

if __name__ == "__main__":
    sys.path.append("..")

from webspider.core.opener import getUrlOpener
from webspider.utils.connect import connect
from webspider.utils.tools import get_url_root
from config import URL_DB_CONFIG, sql_create, sql_insert_update


''' proxy should contains:
id: hash value of the total result
ip, port, is_http, is_https, sup_get, sup_post,
class  # 匿名度： 透明，高匿
addr   # 位置
response_time: unit:second, default: 30
url    # source url
is_available, is_deleted
insert_time, last_changed_time

主要抓取 http://www.kuaidaili.com/ 主页上面的一些稳定ip，并且作为一种服务实时监控

TODO:
  1, add cookie, agent information;
  2, transform to server;
  3, stability of server(try .. except ..)
'''


class ProxyBaseFetcher(object):
    def __init__(self, name, conn_config):
        self.name = name
        self.conn_config = conn_config

    def insert_item(self):
        '''
        insert one item formatted as specified format
        :return:  {"code": 0, "msg": 'error info'}; 0, ok, other, faild with msg
        '''
        raise NotImplementedError("this meshod should be rewritten")
    def delete_item(self):
        ''' usually just set flag like `is_delete` to 1
        :return: {"code": 0, "msg": 'error info'}; 0, ok, other, faild with msg
        '''
        raise NotImplementedError("this meshod should be rewritten")

    def get_item(self):
        '''
        :return: one item, or None
        '''
        raise NotImplementedError("this meshod should be rewritten")

    def describe(self):
        '''
        :return: informations about this server
        '''
        raise NotImplementedError("this meshod should be rewritten")

    def parse(self):
        '''
        parse the url
        :return:
        '''
        raise NotImplementedError("this meshod should be rewritten")


re_digits = r'[\d.]+'
DEFAULT_RESPONSE_TIME = 10
class kuaidaili_server(ProxyBaseFetcher):

    def __init__(self, conn_config=URL_DB_CONFIG):
        super(kuaidaili_server, self).__init__("kuaidaili", conn_config)
        self.door_url = "http://www.kuaidaili.com/proxylist/"
        self.opener_type = "requests"
        self.conn = connect('mysql', conn_config)
        if not self.conn:
            raise Exception("Can not connect mysql")

    def parse(self):
        # check mysql
        self.check_mysql()
        # open the page
        opener = getUrlOpener(self.opener_type)
        content = opener.open(self.door_url)

        root_url = get_url_root(self.door_url)
        bs = BS(content)
        container = bs.find("div", attrs={"id":"container"})
        check_bs_node(container)
        listnav = container.find("div", attrs={"id":"listnav"})
        check_bs_node(listnav)
        url_nodes = listnav.findAll("a")
        urls = [t['href'] for t in url_nodes]
        urls = [urlparse.urljoin(root_url, url) if url.startswith('/') else url for url in urls]

        # get content for each sub url
        num = 0
        for url in urls:
            content = opener.open(url)
            bs = BS(content)
            proxy_list = bs.find("div", attrs={"id": "list"})
            nodes = proxy_list.find("table").findAll("tr")
            for node in nodes[1:]: # ignore the first
                tds = node.findAll("td")
                items = [t.text for t in tds]
                ip, port , _class, http_https, get_post, addrs_channel, resp_time, _web_check = items
                http_set = filter(lambda x: x, [t.strip().lower() for t in http_https.split(',', 2)])
                is_http = 1 if 'http' in http_set else 0
                is_https = 1 if 'https' in http_set else 0

                methods = filter(lambda x: x, [t.strip().lower() for t in get_post.split(',', 2)])
                sup_get = 1 if 'get' in methods else 0
                sup_post = 1 if 'post' in methods else 0

                addrs_channel = filter(lambda x: x, [t.strip().lower() for t in addrs_channel.split(' ', 2)])
                if len(addrs_channel) > 1:
                    addrs, channel = addrs_channel[0], addrs_channel[1]
                elif len(addrs_channel) == 1:
                    addrs, channel = addrs_channel[0], ""
                else:
                    addrs = channel = ""
                #
                resp_digit_time = re.search(re_digits, resp_time.strip())
                resp_time = float(resp_digit_time.group()) if resp_digit_time else DEFAULT_RESPONSE_TIME

                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                is_available, is_deleted = 1, 0
                insert_time = last_changed_time = now
                ip_port = "%s:%s"%(ip, port) if port else ip
                data_id = hashlib.md5(ip_port).hexdigest()
                source = url

                #pdb.set_trace()
                row = (data_id, ip_port, is_http, is_https, sup_get, sup_post, _class, addrs, # insert
                            channel, resp_time, source,is_available, is_deleted, insert_time, last_changed_time, # insert
                            is_http, is_https, sup_get, sup_post, _class, addrs, channel, resp_time, source,     # update
                            is_available, is_deleted, last_changed_time)  # update
                #
                print ">>", row
                cursor = self.conn.get_cursor()
                cursor.execute(sql_insert_update, row)
                self.conn.commit()

                num += 1

    def check_mysql(self):
        # check if table exists
        print "sql::", sql_create
        self.conn.execute(sql_create)
        self.conn.commit()

def check_bs_node(node, tag=""):
    if not node:
        raise Exception("bs node[tag: %s] has no value[%s]"%(tag, node))


def main():
    s = kuaidaili_server()
    s.parse()

main()

