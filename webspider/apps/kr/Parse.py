# coding=utf8
""" parse functions

Here must use `from modulename import function` to explicitly import
correspond parsing function

NOTICE:
  1, if no data get, PLEASE raise NoDataException
"""
import re
import json
import sys
import traceback

import pdb

from bs4 import BeautifulSoup as BS

from webspider.exception.SpiderException import NoDataException

def getContentDefault(page, url):
    """ Default function to parse the content

    @PARAMS:
        content_lst: list of tuple: (title_str, tag_dic, content_str),...
          title: string, the title of content
          tag: json format, relevant tag of name
          content: json format, detail about the page
        flag: dict, extend manipulations about the result
    @NOTICE:
        parse function should split the content with max possibility.
        the splited contents share minimum relevant.
    """
    #bs = BS(page)
    title_str = "" # the main title of content
    tag_dict = {}  # tags of content, e.x. add time, author, source.
    content_str = "" # content, could be save as html
    flag_dict = {}
    return [[(title_str, tag_dict, content_str)], flag_dict]

# add parse functios Here. TODO
# def parse_function(page):
#    ....

def parse_content(page, url):
    bs = BS(page)
    try:
        article = bs.find("article", attrs={"class": "single-post"})
        if not article: return None
        header = article.find("header")
        title = header.text if header else ""

        author = article.find("div", attrs={"class":"author"})
        author = author.text if author else ""
        
        content = article.find("section", attrs={"class":"article"})
        content = content.text

        tag_dict = {"author": author}
        return [[(title, tag_dict, content)], {}]
    except:
        traceback.print_exc()        
        return None

