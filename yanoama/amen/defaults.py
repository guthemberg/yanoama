import sys
import os
import subprocess
import socket
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

#  Amen Defaults
BACKEND = config.get('backend', 'mongodb')

_backend = config.get('backend', {})
_mongo = _backend.get('mongo', {})

hostname = subprocess.Popen(['hostname'], stdout=subprocess.PIPE, close_fds=True)\
        .communicate()[0].rstrip()
ip_address=socket.gethostbyname(hostname)

MONGO = {
    'port': _mongo.get('port', 39167),
#    'host': _mongo.get('host', '127.0.0.1'),
    'host': ip_address,
    'user': _mongo.get('user', ''),
    'password': _mongo.get('password', ''),
    'database' : 'amen',
}

# 1 minute default
SYSTEM_CHECK_PERIOD = config.get('system_check_period', 60)

# default storage path for objects
STORAGE_PATH = config.get('storage_path', '/tmp/objects')
if not os.path.isdir(STORAGE_PATH):
    os.makedirs(STORAGE_PATH)

#SYSTEM_CHECKS = ['cpu', 'memory', 'disk', 'network', 'loadavg']
SYSTEM_CHECKS = ['node']

if sys.platform == 'darwin':
    del SYSTEM_CHECKS[3] # Delete network check on macos


key = config.get('secret_key', None)
PROXY = config.get('proxy', None) # Relative baseurl if true

TIMEZONE = config.get('timezone','UTC')

if key != None and len(key) > 0:
    SECRET_KEY = key
else:
    SECRET_KEY = 'TGJKhSSeZaPZr24W6GlByAaLVe0VKvg8qs+8O7y=' #Don't break the dashboard

