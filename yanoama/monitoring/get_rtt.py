#!/usr/bin/env python
import sys
#for reding conf files easly, got from http://www.voidspace.org.uk/python/configobj.html, please add it as dependency
#from planetlab import PlanetLabAPI
#from configobj import ConfigObj
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

try:
    from yanoama.planetlab.planetlab import MyOps
    from yanoama.backend.mongo import Mongo
    from yanoama.core.essential import log,\
            online,saveNodes,getIntialNodes,\
            checkNodes
except ImportError:
    sys.path.append(get_install_path()) 
    #import yanoama modules alternatively
    from yanoama.planetlab.planetlab import MyOps
    from yanoama.backend.mongo import Mongo
    from yanoama.core.essential import log,\
            online,saveNodes,getIntialNodes,\
            checkNodes






      

if __name__ == '__main__':
    if not online():
        log('offline')
        sys.exit(-1)
    log('run get_rtt... ')
    nodes,filename=getIntialNodes(sys.argv)   
    myops_nodes={}
    try:
        myops_nodes=MyOps().getAvailableNodes()
    except:
        print 'failed to get myops information: myops_nodes=MyOps().getAvailableNodes()'
    bad_nodes=[]
    #checking existing nodes, and excluding bad nodes
    checkNodes(nodes, myops_nodes, bad_nodes)
    #checking remaining potential new nodes
    checkNodes(nodes, {}, [], myops_nodes)
    #clean up bad nodes
    for hostname in bad_nodes:
        del nodes[hostname]
    saveNodes(nodes, filename)
    db=Mongo()
    db.save_raw_nodes(nodes)
    log('done. ')
    sys.exit(0)