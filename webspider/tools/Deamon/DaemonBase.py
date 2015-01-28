#!/usr/bin/env python

import sys, os, time, atexit
from signal import SIGTERM

class Daemon(object):
    def __init__(self, pidfile):
        self.pidfile = pidfile
        
    def daemonize(self):
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s) \n"%(e.errno, e.strerror))
            sys.exit(1)
        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)
        # do the second fork
        try:
            pid = os.fork()
            if pid > 0 :
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s) \n"%(e.errno, e.strerror))
            sys.exit(1)

        # redirect standrad file descriptors
        sys.stdout.flush()
        sys.stderr.flush()

        # write pid file
        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile, 'w+').write("%s\n"%pid)

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist, Daemon already running? \n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)
        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        '''stop the daemon
        '''
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        if not pid:
            message = "pid file %s does not exist, Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return 

        # try to kill the daemon process
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)  # TODO, why here is a loop to kill?
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)

    def restart(self):
        self.stop()
        self.start()

    def run(self):
        '''
        this method should be overrided, It will be called after the process
        has been daemonized by start() or restart()
        '''
''' USAGE:
# FOR EXAMPLE:
class MyDaemon(Daemon):
    def run(self):
        while 1:
            time.sleep(1)

if __name__ == "__main__":
    daemon = MyDaemon("/tmp/daemon-example.pid")
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        if 'stop' == sys.argv[1]:
            daemon.stop()
        if 'restart' == sys.argv[1]:
            daemon.restart()
    else:
        print "usage: %s start|stop|restart"%sys.argv[0]
        sys.exit(2)
'''













