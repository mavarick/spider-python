""" parse functions

Here must use `from modulename import function` to explicitly import
correspond parsing function
"""
import re
from Parse import getContentDefault, parse_content
# add parse function, TODO
# for example, `from Parse import getCZ89proxy`

REGISTER_URL_PARSE = [
    #(r'', function)
    (r'http://www.36kr.com/p/(\d+)\.html', parse_content),
    ]

def parse(url, page, print_info=False):
    """ parse `content` depend on url
    """
    fun = getContentDefault
    for pattern in REGISTER_URL_PARSE:
        url_pattern, fun_name = pattern
        if re.search(url_pattern, url):
            fun=fun_name
            break
    if print_info:
        print "%s <== %s" % (url, fun)
    return fun(page, url)



