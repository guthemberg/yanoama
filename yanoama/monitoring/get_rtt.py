#!/usr/bin/env python
import sys
from subprocess import PIPE, Popen 
#for reding conf files easly, got from http://www.voidspace.org.uk/python/configobj.html, please add it as dependency
#from planetlab import PlanetLabAPI
#from configobj import ConfigObj
import pickle
from datetime import datetime
from pymongo import Connection
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
except ImportError:
    sys.path.append(get_install_path()) 
    #import yanoama modules alternatively
    from yanoama.planetlab.planetlab import MyOps

import os

def get_db_name_and_port():
    try:
        config_file = file('/etc/yanoama.conf').read()
        config = json.loads(config_file)
    except Exception, e:
        print "There was an error in your configuration file (/etc/yanoama.conf)"
        raise e
    _amen = config.get('amen', {})
    _backend = _amen.get('backend', {})
    _mongo = _backend.get('mongo', {})    
    return _mongo.get('db_name','yanoama'),_mongo.get('port',39167)

def get_latency():
    try:
        config_file = file('/etc/yanoama.conf').read()
        config = json.loads(config_file)
    except Exception, e:
        print "There was an error in your configuration file (/etc/yanoama.conf)"
        raise e
    _coordinators = config.get('coordinators', {})
    HOSTNAME = Popen(['hostname'], stdout=PIPE, close_fds=True)\
        .communicate()[0].rstrip()
    return float(_coordinators.get(HOSTNAME).get('latency'))

#see bootstratNodesFile() for having information about the file format
def readNodes(filename):
    nodes_file = open(filename, "r") # read mode
    dictionary = pickle.load(nodes_file)
    nodes_file.close()
    return dictionary

#see bootstratNodesFile() for having information about the file format
def saveNodes(dictionary,filename):
    nodes_file = open(filename, "w") # write mode
    pickle.dump(dictionary, nodes_file)
    nodes_file.close()


def getRTT(hostname):
    try:
        return (float(Popen("sh "+get_install_path()+"/yanoama/monitoring/get_rtt.sh "+hostname, stdout=PIPE,shell=True).communicate()[0]))
    except:
        return -1

def online():
    rtt=getRTT('www.google.com')
    if rtt==-1 :
        return False
    return True

def log_to_file(msg,logfile):
    nodes_file = open(logfile, "a") # read mode
    now = datetime.now()
    nodes_file.write(now.strftime("%Y-%m-%d %H:%M")+': '+msg)
    nodes_file.close()

def log(msg):
    now = datetime.now()
    print now.strftime("%Y-%m-%d %H:%M")+': '+msg


def getIntialNodes(cmd_args):
    nodes={}
    filename=''
    if len(cmd_args) > 1:
        filename=cmd_args[1]+'_nodes.pck'
        nodes=readNodes(filename)
    else:
        filename=get_install_path()+'/nodes.pck'
        if os.path.isfile(filename):
            nodes=readNodes(filename)
        else:
            try:
                nodes=MyOps().getAvailableNodes()
            except:
                print 'FATAL EEROR: failed to get myops information: nodes=MyOps().getAvailableNodes(). bye.'
                sys.exit(-1)
    return nodes,filename

def checkNodes(nodes,myops_nodes,bad_nodes,new_nodes=None):
    if new_nodes is not None:
        for hostname in new_nodes:
            rtt=getRTT(hostname)
            if rtt>0.0 :
                nodes[hostname]=rtt
        return
            
    for hostname in nodes:
        if "measurement-lab.org" in hostname:
            bad_nodes.append(hostname)
            continue
        c_rtt = float(nodes[hostname])
        rtt=getRTT(hostname)
        if rtt>0.0 :
            if c_rtt==0.0 :
                nodes[hostname]=rtt
            elif rtt<c_rtt:
                nodes[hostname]=rtt
        else:
            bad_nodes.append(hostname)
        #if it is in myops nodes, remove it
        try:
            del myops_nodes[hostname]
        except:
            pass

def save_to_db(nodes):  
    db_name,port=get_db_name_and_port()
    latency=get_latency()
    too_far_nodes=[]
    for hostname in nodes.keys():
        if nodes[hostname]<latency:
            too_far_nodes.append(hostname)
    #clean up bad nodes
    for hostname in too_far_nodes:
        del nodes[hostname]
    connection = Connection('localhost', port)
    db = connection[db_name]
    nodes_latency_measurements=db.nodes_latency_measurements
    nodes_latency_measurements.drop()
    nodes_latency_measurements.insert(nodes)
      

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
    save_to_db(nodes)
    log('done. ')
    sys.exit(0)