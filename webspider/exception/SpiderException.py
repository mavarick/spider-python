""" self-defined exeptions of spider
"""

class SpiderException(BaseException):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

class PageErrorException(SpiderException):
    """ if the page contains some `error` text, this could be raised
    """
    def __init__(self, msg):
        super(PageErrorException, self).__init__(msg)

class QueueErrorException(SpiderException):
    def __init__(self, msg=""):
        super(QueueErrorException, self).__init__(msg)

class ProgramExit(BaseException):
    """ Control Exit if Control.getExitCode() ==1
    """
    def __init__(self, msg=""):
        super(ProgramExit, self).__init__(msg)

class NoDataException(SpiderException):
  def __init__(self, msg=""):
    super(NoDataException, self).__init__(msg)
class NoProxyDataException(NoDataException):
  def __init__(self, msg=""):
    super(NoProxyDataException, self).__init__(msg)
