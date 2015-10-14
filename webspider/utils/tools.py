#!/usr/bin/env python
#encoding:utf8

"""
some functions
"""
import os
import types
import urlparse


def field2sql(item):
    """translate item to Mysql Value as in sql
    Note: python use '' when print list if it contains string
    """
    result = ""
    if (isinstance(item, int) or isinstance(item, float)):
        result = '%s' % item
    elif isinstance(item, str) or isinstance(item, unicode):
        result =  "'"+sql_escape(item)+"'"
    elif (isinstance(item, list) or
         isinstance(item, dict) or
         isinstance(item, set)):
        result = "'" + sql_escape("%s" % item) + "'"
    else:
        result = "'" + sql_escape('%s' % item) + "'"
    return result


def sql_escape(_string):
    """ escape string to sql compatible
    """
    return _string.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"')


def check_app(msg):
    """ decorate the check process of prepare app
    """
    def _dec_pre_app(func):
        def __dec_pre_app(*args, **kwargs):
            print "[CHECK] %s" % msg
            func(*args, **kwargs)
            print "Done"
        return __dec_pre_app
    return _dec_pre_app


def read_dir(path, start='', end=''):
    """ read the directory and return the filenames' list in this directory
    """
    return [os.path.join(path, f) for f in os.listdir(path)
            if (f.startswith(start) and f.endswith(end))]


def trim_url(link):
    """ trim the url
    """
    # TODO
    return link


def reload_module(module, recursion=True, visited_dict = {}, print_info = False):
  """reload module recursively or not"""
  reload(module)
  visited_dict[module] = 1
  if print_info: print("{0} has been loaded".format(module.__name__))
  if not recursion: return
  for m in module.__dict__.values():
    if type(m) == types.ModuleType and m not in visited_dict:
      reload_module(m, recursion = recursion,
                    visited_dict = visited_dict,
                    print_info=print_info)


def get_url_root(url):
    # 获得地址的跟地址，注意url必须是http开头
    elem = urlparse.urlparse(url)
    scheme, netloc = elem.scheme, elem.netloc
    return "{}://{}".format(scheme, netloc)



def __test__():
    #a="what\\\'\"s"
    #print sql_escape(a)
    where_dic={"id":5L}
    where_str = ','.join(["%s=%s" % (t[0], field2sql(t[1])) for t in where_dic.items()])
    print where_str


if __name__ == "__main__":
    __test__()
