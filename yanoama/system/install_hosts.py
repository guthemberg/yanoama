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


_hosts = config.get('hosts', {})

temp_file='/tmp/hosts'
f = open(temp_file, 'w')

for ip in _hosts.keys():
    f.write(ip+'\t\t'+_hosts[ip]+'\n')
f.close()
subprocess.Popen(['sudo','cp', '-f',temp_file,'/etc/hosts'], \
                 stdout=subprocess.PIPE, close_fds=True)
