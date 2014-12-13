""" content.py

contains methods to save the content
"""
import os
import datetime
from webspider.utils.connect import connect
from webspider.utils.BatchInserter import BatchInsert

BATCH_SIZE = 100

def get_content_server(type, **params):
    """ get different type of saver
    
    mysql : config, batch_size
    local : save_path
    stdout : {}
    """
    return {'': SaveStdout,
            'mysql': SaveMysql,
            'local': SaveLocal}[type](**params)
    
class SaveServer(object):
    """ print directly to console
    """
    def send(self, item):
        pass
    def close(self):
        pass
    def clear(self):
        """ clear the server data. delete if exists
        """
        print "No Content `clear` for stdout"

class SaveStdout(SaveServer):
    """ print directly to console
    """
    def send(self, item):
        print item

class SaveMysql(SaveServer):
    def __init__(self, config = None, batch_size = None):
        self.config = config
        type = config.get("type", '')
        self.db = connect(type, config)
        self.tablename = self.config['tablename']
        if not batch_size:
            batch_size = 1
        self.fields = ('url_id', "content", 'add_time')
        self.batch_inserter = BatchInsert(self.db, self.tablename,
                                self.fields, batch_size)
        
    def send(self, item):
        add_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.fields[-1] == 'add_time':
            # add `add_time` to mysql
            item = list(item)
            item.append(add_time)
        self.batch_inserter.insert(item)
    def commit(self):
        self.batch_inserter.commit()
    def close(self):
        del self.batch_inserter
        self.db.close()
    def clear(self):
        sql = "truncate %s" % self.tablename
        self.db.execute(sql)
        print "Content Table `%s` has been truncated" % self.tablename

class SaveLocal(object):
    def __init__(self, save_path=None):
        self.path = save_path
        self.__check_path_exist(self.path)
        self.fp = open(self.path, 'a+')
    def __check_path_exist(self, path):
        dirname = os.path.dirname(path)
        if not os.path.exists():
            os.makedirs(dirname)
    def send(self, item):
        print >>self.fp, '\t'.join(map(str, item))
    def commit(self):
        self.fp.flush()
    def close(self):
        self.fp.close()
    def clear(self):
        """ delete the file if exists
        """
        if os.path.exists(self.path):
            os.system("rm %s" % self.path)
            print "Delete Content Path : %s" % self.path
        else:
            print "Centent Path `%s` does not exist" % self.path
