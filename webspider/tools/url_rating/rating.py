#!/usr/bin/env python
#encoding:utf8

'''
get the url rating by posting url to http://www.alexa.cn/
'''

import sys
sys.path.append("../../")

from core.opener import getUrlOpener
try:
    from BeautifulSoup import BeautifulSoup as BS
except:
    from bs4 import BeautifulSoup as BS

request_url = "http://www.alexa.cn/index.php?url={0}"

url_info = {
    "name": "", # name
    "site": "", # site url
    "company": "", # site company
    "pr": "", # page rank
    "pv_monthly": "", # monthly pv
    "ip_monthly": "", # monthly ip

    "rating_monthly": "", #  average monthly rating
}
def get_rating(url):
    url = request_url.format(url)
    print("URL: ", url)
    content = getUrlOpener('selenium').open(url)
    bs = BS(content)

    # 网站名称
    url_info['name'] = get_nagivablestring_content(bs, u"网站名称")
    url_info['site'] = get_nagivablestring_content(bs, u"网站首页网址")
    url_info['company'] = get_nagivablestring_content(bs, u"主办单位名称")
    url_info['pr'] = get_nagivablestring_content(bs, "Google PR")

    url_info['pv_monthly'] = get_nagivablestring_content(bs, u"日均 PV [月平均]")
    url_info['ip_monthly'] = get_nagivablestring_content(bs, u"日均 IP [月平均]")

    url_info['rating_monthly'] = get_nagivablestring_content(bs, u"一月平均排名")
    return url_info

def get_nagivablestring_content(bs, key):
    navigable_string_node = bs.find(text=key)
    content_node = navigable_string_node.parent
    return content_node.font.text

def test():
    url = "www.36kr.com"
    url_info = get_rating(url)
    for k, v in url_info.iteritems():
        print(u"{0} : {1}".format(k, v))
#test()
