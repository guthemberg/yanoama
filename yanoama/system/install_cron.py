try:
    import json
except ImportError:
    import simplejson as json

import subprocess
from random import randrange

##this script checks the role of the node
#and install cron tasks accordingly 
try:
    config_file = file('/etc/yanoama.conf').read()
    config = json.loads(config_file)
except Exception, e:
    print "There was an error in your configuration file (/etc/yanoama.conf)"
    raise e


_coordinators = config.get('coordinators', {})
_ple_deployment = config.get('ple_deployment', {})

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
    subprocess.Popen(['sudo','cp', _ple_deployment['path']+'/yanoama/monitoring/get_rtt.py','/usr/local/bin/'], stdout=subprocess.PIPE, close_fds=True)
    #making it runnable
    subprocess.Popen(['sudo','chmod', 'guo+x','/usr/local/bin/get_rtt.py'], stdout=subprocess.PIPE, close_fds=True)
#    print "inside"
    mystring = str(minute)+"       "+str(hour)+"     *       *       *       get_rtt.py > output.log 2>&1"
#    print mystring
    echo = subprocess.Popen(['echo', mystring], stdout=subprocess.PIPE, close_fds=True)
    install_cron_output = subprocess.Popen(['crontab'], stdin=echo.stdout, stdout=subprocess.PIPE, close_fds=True)

else:
    print "outside"