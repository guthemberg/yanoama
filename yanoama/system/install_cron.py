import sys
try:
    import json
except ImportError:
    import simplejson as json

import subprocess

try:
    config_file = file('/etc/yanoama.conf').read()
    config = json.loads(config_file)
except Exception, e:
    print "There was an error in your configuration file (/etc/yanoama.conf)"
    raise e


_coordinators = config.get('coordinators', {})

hostname = subprocess.Popen(['hostname'], stdout=subprocess.PIPE, close_fds=True)\
        .communicate()[0].rstrip()

if hostname in _coordinators.keys():
    #copy get_rtt
    subprocess.Popen(['cp', 'yanoama/monitoring/get_rtt.py','./'], stdout=subprocess.PIPE, close_fds=True)
#    print "inside"
    mystring = str(_coordinators[hostname])+"       */6     *       *       *       cd ~/yanoama && python get_rtt.py > output.log 2>&1"
#    print mystring
    echo = subprocess.Popen(['echo', mystring], stdout=subprocess.PIPE, close_fds=True)
    install_cron_output = subprocess.Popen(['crontab'], stdin=echo.stdout, stdout=subprocess.PIPE, close_fds=True)

else:
    print "outside"