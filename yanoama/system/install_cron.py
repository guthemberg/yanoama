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


_backend = config.get('coordinators', {})

print _backend.keys()

hostname = subprocess.Popen(['hostname'], stdout=subprocess.PIPE, close_fds=True)\
        .communicate()[0]

print hostname