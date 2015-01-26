#!/usr/bin/env python
#encoding:utf8

from selenium import selenium
'''
use selenium to analysis the webpage, for functions:
    1, get screen shot of the web pages

WARN:
1, the program will be blocked when get request for one url
2, the path to save screenshot should be absolute path
3, the screenshot image is TOO BIG for some content website!
'''

class SeleniumServer(object):
    def __init__(self, host, port, browser='firefox', timeout=30000):
        '''
        @params:
        host/port: SHOULD be localhost running selenium-rc server's configuration
        @example:
            host: "localhost"
            port: 4444
            browser:"firefox"
        '''
        self.host = host
        self.port = port
        self.browser = browser
        self.timeout = timeout

    def open(self, url, para = ''):
        '''
        @params: should be the added parammeters to url
        '''
        self.sel = selenium(self.host, self.port, self.browser, url)

        self.sel.start()
        self.sel.set_timeout(self.timeout)
        self.sel.open(para) #could raise timeout exception!

    def capture_entire_screenshot(self, url, url_params, to_path, params):
        ''' 
        @params:
            url/url_params: the screenshot url
            to_path : the save path of the screenshot
            params  : the added parameters for screenshot, for example: "background=#666666"
        '''
        self.open(url, url_params)
        self.sel.capture_entire_page_screenshot(to_path, params)
        self.reset()

    def stop(self):
        ''' you must stop the server after you shutdown it, for the
        opened record browser will be there all time!
        '''
        self.sel.stop()

    def close(self):
        ''' simulate the 'close' button is clicked on the browser page
        '''
        self.sel.close()

    def reset(self):
        self.sel.close()  # close the page
        self.sel.stop()   # close the server

def test():
    selobj = SeleniumServer("localhost", 4444, timeout=60000)
    selobj.capture_entire_screenshot(
        url = "http://ent.qq.com/movie/",
        url_params = '',
        to_path = "/Users/apple/Documents/projects/webspider/webspider/tools/sceernshot/qq.png", 
        params = '')

#test()
        
