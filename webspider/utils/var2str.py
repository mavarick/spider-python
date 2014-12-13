# -*- coding: utf-8 -*-

"""
translate variance and its formated character which have regularities

for example:
  raw input: 
     v={'aa': 12345, 'bbbb': [1, 2, 3, 4, {'flag': 'vvvv||||xxxxx'}, set(['y', 'x', 'z'])]}
  after `var2str.var2str(v)`
    v_str=<aa::12345##bbbb::<1||2||3||4||<flag::vvvv|xxxxx>||<y|||x|||z>>>
  then reverse back: `var2str.str2var(v_str)`
    v_var={'aa': '12345', 'bbbb': ['1', '2', '3', '4', {'flag': 'vvvv|xxxxx'}, set(['y', 'x', 'z'])]}

NOTATION:
  1, KEY of DICT should be string.
  2, SET amd TUPLE automatically are transformed to LIST
  3, INT/FLOAT/LONG etc. are automatically transformed to STRING 
  4, SEPERATORS would be replace to '' in character.
"""
import types

# TAKE notation of sequence, which has one order
sep_dict = {
      "dict_sep": "##",  # seperator of elements of dict
      "dict_k_v_sep": "::",  # k::v
      "list_sep": "||",   # list seperator
      "set_sep": "|||",    # set seperator
      "tuple_sep": "||"    # tuple seperator
      }
sep_nest = ("<", ">")  # better not repeated char, e.x. ("<-", "->")

# internal operations
sep_values = sep_dict.values()
def erase_sep(s):
  for v in sep_values:
    s = s.replace(v, "")
  for v in sep_nest:
    s=s.replace(v, "")
  return s
_s=sep_nest[0]
_e=sep_nest[1]
class var2str(object):
  @staticmethod
  def var2str(var):
    if not var: return ""
    if type(var) == types.DictType:
      result = []
      for key,value in var.items():
        v_str = var2str.var2str(value)
        k_str = erase_sep("{0}".format(key))
        result.append("{key}{sep}{value}".format(
                                                 key=k_str, 
                                                 sep=sep_dict["dict_k_v_sep"],
                                                 value=v_str))
      return _s+sep_dict["dict_sep"].join(result)+_e
      #return sep_dict["dict_sep"].join(result)
    elif type(var) == types.ListType:
      result = [var2str.var2str(v) for v in var]
      return _s+sep_dict["list_sep"].join(result)+_e
      #return sep_dict["list_sep"].join(result)
    elif type(var) == type(set([])):
      result = [var2str.var2str(v) for v in var]
      return _s+sep_dict["set_sep"].join(result)+_e
      #return sep_dict["set_sep"].join(result)
    elif type(var) == types.TupleType:
      result = [var2str.var2str(v) for v in var]
      return _s+sep_dict["tuple_sep"].join(result)+_e
      #return sep_dict["tuple_sep"].join(result)
    elif type(var) in [types.StringType, 
                       types.IntType,
                       types.LongType,
                       types.FloatType]:
      return erase_sep("{0}".format(var))
    else:
      raise TypeError("Type is not supported. var: {0}, type: {1}".format(
                                  var, type(var)))
  @staticmethod
  def str2var(value):
    # certain the outer nested elements' type
    if NestType.is_nest_type(value, _s, _e):
      _var = NestType(value)
      _var.replace_nest_vars()
      var = _var.parse_var()
      if type(var) == types.DictType:
        for k, v in var.items():
          if type(v)==NestType:
            var[k] = var2str.str2var(str(v))
      if type(var) == types.ListType:
        for n, v in enumerate(var):
          if type(v) == NestType:
            var[n] = var2str.str2var(str(v))
      if type(var) == type(set()):
        # because element in set must be hashable, so there is no meaning for 
        #   for parsing set
        pass 
      return var
    else:
      return value
  
class NestType(object):
    def __init__(self, s, s_tag=_s, e_tag=_e):
      self.value = str(s)
      self.s_tag = s_tag
      self.e_tag = e_tag
      self.replace_s = None
      
    @staticmethod
    def is_nest_type(value, s_tag, e_tag): 
       if (not value.startswith(s_tag) or 
           not value.endswith(e_tag)):
         return 0
       return 1

    def _get_obj_str(self, var):
      return "[NestType]"+str(hash(var))
    def has_nest_element(self):
      if self.replace_s is None:
        self.replace_nest_vars()
      return self.repalce_s == self.value
    
    def _replace_nest_var(self, s, nest_dic={}):
      s_len = len(s)
      tag_index = 0
      s_tag_len, e_tag_len = len(self.s_tag), len(self.e_tag)
      nest_index =[]
      for i in range(s_len):
        if s[i:i+s_tag_len] == self.s_tag:
          tag_index +=1
          if tag_index == 1: nest_index.append(i)
        if s[i:i+e_tag_len] == self.e_tag:
          tag_index -=1
          if tag_index == 0: nest_index.append(i)
        if len(nest_index) == 2: break
      if len(nest_index) <2: return s
      nest_index_s = nest_index[0]
      nest_index_e = nest_index[1] + e_tag_len
      nest_str = s[nest_index_s:nest_index_e]
      nest_var = NestType(nest_str, s_tag=self.s_tag, e_tag = self.e_tag)
      nest_var_str = self._get_obj_str(nest_var)
      nest_dic[nest_var_str] = nest_var
      return s[0:nest_index_s] + nest_var_str + s[nest_index_e:]
    
    def replace_nest_vars(self):
      # trim sign in start and end
      nest_dic = {}
      if not NestType.is_nest_type(self.value, self.s_tag, self.e_tag):
        raise Exception(
            "[ERROR] `{0}` does not match NestType format".format(self.value))
      s = _trim_tag(self.value, self.s_tag, self.e_tag)
      while 1:
        replace_s = self._replace_nest_var(s,nest_dic)
        if replace_s == s: break
        s = replace_s
      self.replace_s = replace_s
      self.nest_dic = nest_dic
    
    def parse_var(self):
      """string `replace_s` has no nestType at all"""
      s = self.replace_s
      var = None
      dict_sep = sep_dict["dict_sep"]
      dict_k_v_sep = sep_dict["dict_k_v_sep"]
      list_sep = sep_dict["list_sep"]
      set_sep = sep_dict["set_sep"]
      if dict_k_v_sep in s: # dict
        var = {}
        items = s.split(dict_sep)
        for item in items:
          if not item: continue
          k,v=item.split(dict_k_v_sep)
          var[k] = self.nest_dic.get(v, v)
      elif set_sep in s:
        var = set([self.nest_dic.get(t, t) for t in s.split(set_sep)])
      elif list_sep in s:
        var = [self.nest_dic.get(t, t) for t in s.split(list_sep)]
      else:
        # just one string
        var = s
      return var
    
    def __str__(self):
      return self.value
    def __unicode__(self):
      return self.value
          
def _trim_tag(str, s, e):
  """trim the `str` off start `s` and end `e`"""
  return str[len(s):(len(str)-len(e))]
  
def test():
  a = {"aa": 12345, "bbbb":[1,2,3,4,{'flag':"vvvv||||世界是我的"},set(['x', 'y','z'])]}
  #a = {}
  print a
  a_str = var2str.var2str(a)
  print ">>", a_str
  a_var = var2str.str2var(a_str)
  print ">>", a_var
  
if __name__ == "__main__":
  test()
