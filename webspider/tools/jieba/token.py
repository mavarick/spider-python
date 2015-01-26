#!/usr/bin/env python
#encoding:utf8

'''
split the passages for key words, functions:
1, 分词
2, 词性标注
3, 关键词提取
4, 新词标记
5, 并行处理
could read the README.txt of jieba module for more detail
'''

import jieba
import jieba.analyse
import jieba.posseg

class JiebaSegment(object):
    def __init__(self):
        pass
    def cut(self, sentence, cut_all=False, HMM=False):
        '''
        @params:
        cut_all: full mode or not
            full mode: 我/ 来到/ 北京/ 清华/ 清华大学/ 华大/ 大学
            precise mode: 我/ 来到/ 北京/ 清华大学
        HMM: weather use HMM model or not
        '''
        seg_list = jieba.cut(sentence, cut_all, HMM)
        return seg_list
    def load_userdict(self, filename):
        ''' load the user defined new words, format:
        词语  词频 词性(可省略)   -- 每行
        '''
        jieba.load_userdict(filename)
    def extract_tags(self, sentence, topK=10, withWeight=False, method="TextRank"):
        ''' extract key words, two methods:
        1, TFIDF: TF/IDF
        2, TextRank: TextRank
        and the filter allowd pos could be used, default is allowPOS=['ns', 'n', 'vn', 'v']
        '''
        method = "TextRank"
        extract_func = jieba.analyse.textrank
        if method.lower() == "tfidf":
            extract_func = jieba.analyse.extract_tags
        return extract_func(sentence, topK=topK, withWeight=withWeight)
    def posseg(self, sentence):
        ''' tag the word pos by calling the method: jieba.posseg.cut
        which use HMM method.
        '''
        words = jieba.posseg.cut(sentence)
        for w in words:
            yield w.word, w.flag

    def enable_parallel(core_num=4):
        jieba.enable_parallel(core_num)
    def disable_parallel():
        jieba.disable_parallel()

def test():
    jb = JiebaSegment()
    sentence = "近日,谷歌召开了Project Ara模块化手机开发者大会,公布了最新版本的Ara原型机,它最大的特点就是每一个零部件都可以自由拆卸"
    print("Test:")
    print(sentence)
    print("精确分词:")
    for item in jb.cut(sentence, cut_all=True, HMM=True):
        print(item)
    print("关键词:")
    keys = jb.extract_tags(sentence, withWeight=True)
    for k in keys:
        print k[0], k[1]
    print("词性标注:")
    result = jb.posseg(sentence)
    for item in result:
        print(u"{0}, {1}".format(item[0], item[1]))
test()





