""" function about the page
"""
import re
import sys

try:
    from BeautifulSoup import BeautifulSoup as BS
except:
		from bs4 import BeautifulSoup as BS
		
from webspider.settings.default_params import RE_PATTERN_URL

#def openUrl(opener, url, proxy, agent):
#    """ open url
#    
#    @params:opener: different opener
#    """
#    return opener.open()

def getLinks(content):
    """ get all links of content
    """
    links = set()
    for pattern in RE_PATTERN_URL:
        p, idx = pattern
        result = re.findall(p, content)
        for item in result:
            links.add(item[idx-1])
    return links
