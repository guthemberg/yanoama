#!/usr/bin/env python

try:
    import json
except ImportError:
    import simplejson as json
import sys
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


try:
    from yanoama.core.essential import Essential, \
                    check_hostname, log, build_hosts_file
    from yanoama.backend.mongo import Mongo
except ImportError:
    sys.path.append(get_install_path()) 
    #import yanoama modules alternatively
    from yanoama.core.essential import Essential, \
                    check_hostname, log, build_hosts_file
    from yanoama.backend.mongo import Mongo




                                      
    
if __name__ == '__main__':
    db=Mongo()
    kernel=Essential()
    for coordinator in kernel.get_coordinators():
        if db.am_i_a_member_of_this(coordinator):
            build_hosts_file(coordinator)
            sys.exit(0)
    build_hosts_file()
    hostname='coordinator'
    log(hostname+' ('+check_hostname(hostname)+'), done.')
    sys.exit(0)
