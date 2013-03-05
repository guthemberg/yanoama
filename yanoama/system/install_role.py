try:
    import json
except ImportError:
    import simplejson as json

import subprocess
from random import randrange
import struct
import os

##this script checks the role of the node
#and installs cron and amen (for coordinator) 
try:
    config_file = file('/etc/yanoama.conf').read()
    config = json.loads(config_file)
except Exception, e:
    print "There was an error in your configuration file (/etc/yanoama.conf)"
    raise e


_coordinators = config.get('coordinators', {})
_ple_deployment = config.get('ple_deployment', {})
DEPLOYMENT_PATH=_ple_deployment['path']
_amen = config.get('amen', {})
STORAGE_PATH = _ple_deployment['storage_path']
AMEN_HOME=_amen['home']

hostname = subprocess.Popen(['hostname'], stdout=subprocess.PIPE, close_fds=True)\
        .communicate()[0].rstrip()

minute=randrange(0,59)
hour=randrange(0,8)

if hostname in _coordinators.keys():
    #this is a coordinator
    ##it install in the cron a 
    #a job to run at random hour
    #and random minute
    #
    #installing script
    subprocess.Popen(['sudo','cp', _ple_deployment['path']+'/yanoama/monitoring/get_rtt.py','/bin/'], stdout=subprocess.PIPE, close_fds=True)
    #making it runnable
    subprocess.Popen(['sudo','chmod', 'guo+x','/bin/get_rtt.py'], stdout=subprocess.PIPE, close_fds=True)
#    print "inside"
    mystring = str(minute)+"       "+str(hour)+"     *       *       *       get_rtt.py > /tmp/get_rtt_output.log 2>&1"
#    print mystring
    echo = subprocess.Popen(['echo', mystring], stdout=subprocess.PIPE, close_fds=True)
    install_cron_output = subprocess.Popen(['crontab'], stdin=echo.stdout, stdout=subprocess.PIPE, close_fds=True)
    #install amen in coordinator: mongodb 
    #based on
    #http://docs.mongodb.org/manual/tutorial/install-mongodb-on-red-hat-centos-or-fedora-linux/
    #last visit 5 March 2013
    if (struct.calcsize('P') * 8)==32:
        #architecture 32 bits
        subprocess.Popen(['sudo','cp', DEPLOYMENT_PATH+'/contrib/mongodb/fedora/10gen.repo.i686','/etc/yum.repos.d/10gen.repo'], stdout=subprocess.PIPE, close_fds=True)
    else:
        #architecture 64 bits
        subprocess.Popen(['sudo','cp', DEPLOYMENT_PATH+'/contrib/mongodb/fedora/10gen.repo.x86_64','/etc/yum.repos.d/10gen.repo'], stdout=subprocess.PIPE, close_fds=True)
    #listen on 39167 port
    subprocess.Popen(['sudo','cp',DEPLOYMENT_PATH+'/contrib/mongodb/mongod.conf','/etc/mongod.conf'], stdout=subprocess.PIPE, close_fds=True)
    subprocess.Popen(['sudo','/sbin/chkconfig','mongod','on'], stdout=subprocess.PIPE, close_fds=True)
    subprocess.Popen(['sudo','/sbin/service','mongod','start'], stdout=subprocess.PIPE, close_fds=True)    

else:
    #peer/storage node role
    #default dir for storing objects/videos
    if os.path.exists(STORAGE_PATH):
        subprocess.Popen(['rm','-rf',STORAGE_PATH], stdout=subprocess.PIPE, close_fds=True)
    subprocess.Popen(['mkdir',STORAGE_PATH], stdout=subprocess.PIPE, close_fds=True)
    #install amen agent/deamon in this peer
    if not os.path.exists(AMEN_HOME):
        subprocess.Popen(['sudo','mkdir',AMEN_HOME],stdout=subprocess.PIPE, close_fds=True)
        subprocess.Popen(['sudo','mkdir',AMEN_HOME+'/bin'],stdout=subprocess.PIPE, close_fds=True)
        subprocess.Popen(['sudo','touch',AMEN_HOME+'/amend.log'],stdout=subprocess.PIPE, close_fds=True)
    subprocess.Popen(['sudo','cp',DEPLOYMENT_PATH+'/contrib/amen/amend',AMEN_HOME+'/bin/'],stdout=subprocess.PIPE, close_fds=True)
    #run daemon
    subprocess.Popen(['sudo','chmod','+x',AMEN_HOME+'/bin/amend'],stdout=subprocess.PIPE, close_fds=True)
    subprocess.Popen(['sudo',AMEN_HOME+'/bin/amend','start'],stdout=subprocess.PIPE, close_fds=True)
        
    print "outside"