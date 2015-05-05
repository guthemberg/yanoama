#!/home/upmc_aren/python_env/bin/python

try:
    import json
except ImportError:
    import simplejson as json


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

import sys

try:
    from yanoama.core.essential import Essential, \
                    get_hostname, log
    from yanoama.backend.mongo import Mongo
except ImportError:
    sys.path.append(get_install_path()) 
    #import yanoama modules alternatively
    from yanoama.core.essential import Essential, \
                    get_hostname, log
    from yanoama.backend.mongo import Mongo





if __name__ == '__main__':
    kernel=Essential()
    db = Mongo()
    local_peers=db.get_peers()
    for coordinator in kernel.get_coordinators(get_hostname()):
        peers=db.get_peers(coordinator)
        to_be_removed=[]
        for hostname in peers.keys():
            if hostname in local_peers:
                if local_peers[hostname]>peers[hostname]:
                    to_be_removed.append(hostname)
        for hostname in to_be_removed:
            del local_peers[hostname]
    db.save_peers(local_peers)
    #log/print out to the standard output
    log('current number of members:'+str(len(local_peers.keys()))+', done.')
