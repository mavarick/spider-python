"""
create an app

create relavant directory and files in apps/appname
"""
import os
import sys
import shutil

try:
    appname = sys.argv[1]
except Exception, ex:
    print "No Appname"

def create_app(appname):
    app_dir = ''
    create_flag = 1
    try:
        # create the directory
        app_dir = "./webspider/apps/" + appname
        print "Create directory: %s" % app_dir
        os.mkdir(app_dir)
        # copy Params.py and Parse.py
        template_file = ["./webspider/core/template/Params.py", 
                         "./webspider/core/template/Parse.py",
                         "./webspider/core/template/Control.py",
                         "./webspider/core/template/Tools.py",
                         "./webspider/core/template/app_flag"]
        print "Copy the template files: %s" % template_file
        for f in template_file:
            shutil.copy(f, app_dir)
        # record the process flag
        init_file = os.path.join(app_dir, "__init__.py")
        print >> open(init_file, 'w'), ''
        flag_file = os.path.join(app_dir, "app_flag")
        print >>open(flag_file, 'w'), create_flag
        print "App[%s] Created!, Path: %s" % (appname, app_dir)
    except Exception, ex:
        print "Error when make dir: %s, info:" % app_dir
        print ex

if __name__ == "__main__":
    create_app(appname)
