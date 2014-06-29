#!/usr/bin/env python

try:
    import json
except ImportError:
    import simplejson as json

import subprocess
#looking for yanoama module
def get_install_path():
    try:
        config_file = file('/etc/yanoama.conf').read()
        config = json.loads(config_file)
    except Exception, e:
        print "There was an error in your configuration file (/etc/yanoama.conf)"
        raise e
    _ple_deployment = config.get('ple_deployment', {"path":"/home/upmc_aren/yanoama"})
    return (_ple_deployment['path']) 

import os
import sys

try:
    from yanoama.core.essential import Essential, \
                    install_cron_job, get_hostname
except ImportError:
    sys.path.append(get_install_path()) 
    #import yanoama modules alternatively
    from yanoama.core.essential import Essential, \
                    install_cron_job, get_hostname



#deployment is based on the node role
#that's either coordinator or peer
if __name__ == '__main__':
    """Deploy yanoama based on the node role,
    either peer or coordinator.

    """
    kernel=Essential()
    info=""
    if (len(sys.argv)==2):
        if sys.argv[1] == "db_port":
            sys.stdout.write("%d" % kernel.get_db_port())
    else:
        sys.stdout.write('')

sys.exit(0)