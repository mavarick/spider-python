"""
some functions
"""
import os
import types

def field2sql(item):
    """translate item to Mysql Value as in sql
    Note: python use '' when print list if it contains string
    """
    result = ""
    if type(item) == type(0) or \
       type(item) == type(0L) or \
       type(item) == type(0.0):
        result = '%s' % item
    elif type(item) == type('') or type(item) == type(u''):
        result =  "'"+sql_escape(item)+"'"
    elif type(item) == type([]) or \
         type(item) == type({}) or \
         type(item) == type(set()):
        result = "'" + sql_escape("%s" % item) + "'"
    else:
        result = "'" + sql_escape('%s' % item) + "'"
    return result

def sql_escape(_string):
    """ escape string to sql compatible
    """
    return _string.replace('\\', '\\\\')\
                .replace("'", "\\'")\
                .replace('"', '\\"')

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

def read_dir(path, start='', end = ''):
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

def __test__():
    #a="what\\\'\"s"
    #print sql_escape(a)
    where_dic={"id":5L}
    where_str = ','.join(["%s=%s" % (t[0], field2sql(t[1])) for t in where_dic.items()])
    print where_str


if __name__ == "__main__":
    __test__()
