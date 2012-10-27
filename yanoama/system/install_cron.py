import sys
try:
    import json
except ImportError:
    import simplejson as json

try:
    config_file = file('/etc/yanoama.conf').read()
    config = json.loads(config_file)
except Exception, e:
    print "There was an error in your configuration file (/etc/yanoama.conf)"
    raise e


_backend = config.get('coordinators', {})

print _backend.keys()