""" define one class to control the spider
"""

class Controler(object):
    exitflag = 0
    msg = ''
    @staticmethod
    def getExitCode():
        return Controler.exitflag
    @staticmethod
    def setExitCode(flag, msg=''):
        Controler.exitflag = flag
        Controler.msg = msg
    @staticmethod
    def getExitMsg():
        return Controler.msg



