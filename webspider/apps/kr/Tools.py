#!/usr/bin/env python
import re

from webspider.utils.var2str import var2str

def extend_links(url, links, flag_dic):
    """ extend the url depending on `flag`, which is fetched by the content

    @NOTICE:
        This should be some advanced methods, the structure seems to be reconsidered!
    @params:
        url: base url
        links: url links from url
        flag_dic: flag dict, in which there should be flags, which is from parse functions
    """
    # TODO
    return links

"""
@EXAMPLE:
# when scrawl `brand.tmall.com`, the page list url is not valid url, which should be
# http://url.../?page=4, it is completed by javascript, so when click the link, the url
# is always the same, so we use `flag_dic` to indicate extended manipulations

RE_PAGE_CNT = 'page=\d'
def extend_links(url, links, flag_dic):
    if re.search(RE_PAGE_CNT, url):
        return links
    page_cnt = flag_dic.get("page_cnt", 0)
    if page_cnt > 0:
        for i in range(1, page_cnt + 1):
            page_param = "page=%d" % i
            new_url = url + "&%s" % page_param
            # one bug, here should be replaced, not simplely added
            links.append(new_url)
    return links
"""
def extend_content(url, content, flag_dict):
  """ extend the content, or simply handle content

  @PARAMS:
    url:    string, url of content
    content: list of tuples with format: (title_str, tag_dict, content_str)
    flag_dict: dict of some information.
  @RETURN:
    content
  """
  # add the handlers here. TODO
  # content = function1(url, content)

  # special characters handling. ESPECIALLY escaped character in html
  # translating the result to some type easy to save and check
  _content = []
  for (title_str, tag_dict, content_str) in content:
    _content.append((title_str,
                     var2str.var2str(tag_dict), content_str))
  return _content

