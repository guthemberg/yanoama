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
import os

_hosts = config.get('hosts', {})

temp_file='/tmp/hosts_1'
hosts_file='/etc/hosts'
hosts_origin_file='/etc/hosts.origin'
temp_hosts_file='/tmp/hosts'
f = open(temp_file, 'w')

for ip in _hosts.keys():
    f.write(ip+'\t\t'+_hosts[ip]+'\n')
f.close()
#check if /etc/hosts.origin exists 
if not os.path.exists(hosts_origin_file):
    subprocess.Popen(['sudo','cp', '-f',hosts_file,hosts_origin_file], \
                     stdout=subprocess.PIPE, close_fds=True)
output_file=open(temp_hosts_file,'w')
subprocess.Popen(['sudo','cat',temp_file,hosts_origin_file], \
                 stdout=output_file, close_fds=True)
output_file.close()
subprocess.Popen(['sudo','cp', '-f',temp_hosts_file,hosts_file], \
                 stdout=subprocess.PIPE, close_fds=True)
#clean up
subprocess.Popen(['sudo','rm', temp_file,temp_hosts_file], \
                     stdout=subprocess.PIPE, close_fds=True)

