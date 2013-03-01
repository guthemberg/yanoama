#!/usr/bin/env python
import sys
from subprocess import PIPE
from subprocess import Popen
#for reding conf files easly, got from http://www.voidspace.org.uk/python/configobj.html, please add it as dependency
#from planetlab import PlanetLabAPI
#from configobj import ConfigObj
import pickle
from datetime import datetime
try:
    import json
except ImportError:
    import simplejson as json

#looking for yanoama module
try:
    from yanoama.planetlab.planetlab import MyOps
except ImportError:
    try:
        config_file = file('/etc/yanoama.conf').read()
        config = json.loads(config_file)
    except Exception, e:
        print "There was an error in your configuration file (/etc/yanoama.conf)"
        raise e
    _ple_deployment = config.get('ple_deployment', {})
    sys.path.append(_ple_deployment['path']) 
    #import yanoama modules alternatively
    from yanoama.planetlab.planetlab import MyOps

import os

    #print api_server.AuthCheck(auth)
#    print ple.GetPeers(auth,None,['peer_id','peername'])
#    print "ple nodes: "+str(len(ple.GetNodes(auth,{'peer_id':None},['peer_id','hostname'])))
#    print "plc nodes: "+str(len(ple.GetNodes(auth,{'peer_id':1},['peer_id','hostname'])))
#    print "plj nodes: "+str(len(ple.GetNodes(auth,{'peer_id':2},['peer_id','hostname'])))

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

#nodes file stores a dictionary with the following format
#hostname:rtt
#def bootstrapNodesFiles():
#    config=ConfigObj('ple.conf')
#    api=PlanetLabAPI(config['host'],config['username'],config['password'])
#    ple_nodes={}
#    for node in (api.getPLEHostnames()):
#        ple_nodes[node['hostname']]=0
#    saveNodes(ple_nodes,'ple_nodes.pck')
#    plc_nodes={}
#    for node in (api.getPLCHostnames()):
#        plc_nodes[node['hostname']]=0
#    saveNodes(plc_nodes,'plc_nodes.pck')
#    nodes={}
#    for node in (api.getHostnames()):
#        nodes[node['hostname']]=0
#    saveNodes(nodes,'nodes.pck')

def getRTT(hostname):
    try:
        # subprocess.check_output(["sh get_rtt.sh "+hostname],stderr=subprocess.STDOUT,shell=True)
        #print "sh get_rtt.sh "+hostname
        #print Popen("sh get_rtt.sh "+hostname, stdout=PIPE,shell=True).communicate()[0]
        return (float(Popen("sh yanoama/system/get_rtt.sh "+hostname, stdout=PIPE,shell=True).communicate()[0]))
    except:
        #raise
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
        try:
            config_file = file('/etc/yanoama.conf').read()
            config = json.loads(config_file)
        except Exception, e:
            print "There was an error in your configuration file (/etc/yanoama.conf)"
            raise e
        _ple_deployment = config.get('ple_deployment', {})
        filename=_ple_deployment['path']+'/nodes.pck'
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
    log('done. ')
    sys.exit(0)

#inputfile = "nodes.tbl"

#if os.path.isfile(inputfile) and os.path.exists(inputfile):
#    print 'ok'
#else:
#    print 'to do'


#hostname="ple2.ipv6.lip6.fr"
#print hostname
#rtt=int(float(subprocess.check_output(["sh /tmp/get_rtt.sh "+hostname],stderr=subprocess.STDOUT,shell=True)))
#print rtt
