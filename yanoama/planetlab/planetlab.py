#!/home/upmc_aren/python_env/bin/python

import sys
import xmlrpclib
#working with http data. further information in http://docs.python.org/3.1/howto/urllib2.html
from urllib2 import urlopen
import subprocess
#bola

class PlanetLabAPI:
    #api
    auth=None
    api=None
    
    def __init__(self,username,password,host,port=443):
        self.auth = { 'AuthMethod' : 'password',
                 'Username' : username,
                 'AuthString' : password
        }
        self.api=xmlrpclib.ServerProxy("https://%s:%d/PLCAPI/"%(host,port),allow_none=True)

    def getPLEHostnames(self):
        return (self.api.GetNodes(self.auth,{'peer_id':None},['hostname']))

    def getHostnames(self):
        return (self.api.GetNodes(self.auth,None,['hostname']))

    def getNodesIdsAndNames(self):
        nodes=(self.api.GetNodes(self.auth,None,['node_id','hostname']))
        nodes_dic={}
        for node in nodes:
            nodes_dic[node['node_id']]=node['hostname']
        return nodes_dic

    def getPLCHostnames(self):
        return (self.api.GetNodes(self.auth,{'peer_id':1},['hostname']))

    def getBootNodes(self):
        return (self.api.GetNodes(self.auth,{'boot_state':'boot'},['hostname']))

    def getSliceHostnames(self,slice_name):
        node_ids = (self.api.GetSlices(self.auth,slice_name,['node_ids']))[0]['node_ids']
        nodes_dic=self.getNodesIdsAndNames()
        #print nodes_dic.keys()
        #print len(nodes_dic.keys())
        #print node_ids
        hostnames=[]
        for node_id in nodes_dic.keys():
            if node_id in node_ids:
                hostnames.append(nodes_dic[node_id])
        return hostnames

    def getHostSite(self,hostname):
        site_id = int((self.api.GetNodes(self.auth,hostname,['site_id']))[0]['site_id'])
        return (self.api.GetSites(self.auth,site_id,['login_base','name','peer_id','longitude','latitude']))[0]
        
    def update(self,expire_time):
        return (self.api.UpdateSlice(self.auth,'upmc_aren',{'expires':expire_time}))

    def updateSliceNodes(self,slice_name,nodes):
        return (self.api.UpdateSlice(self.auth,slice_name,{'nodes':nodes}))
    
class MyOps:
    status_table=None
    myops_ple_url=""
    myops_plc_url=""
    
    def __init__(self):
        self.status_table={}
        self.myops_plc_url="http://monitor.planet-lab.org/monitor/"
        self.myops_ple_url="http://www.planet-lab.eu/monitor/"
            
    def getNodesStatus(self):
        #query output
        #hostname,observed_status,
        #planetlab-3.dis.uniroma1.it,BOOT, #this string has length equal to 3 
        query="query?object=nodes&nodehistory_hostname=&hostname=on&observed_status=on&rpmvalue=&tg_format=plain"
        #query output
        #hostname,observed_status,
        #planetlab-3.dis.uniroma1.it,BOOT,
        
        self.status_table={}
        
        #PLE information
        try:
            
            ple_nodes_status = urlopen(self.myops_ple_url+query)
            line=ple_nodes_status.readline()
            #get rid of header
            if line.split(',')[0] == 'hostname' and line.split(',')[1] == 'observed_status':
                line=ple_nodes_status.readline()
            while line:
                if len(line.split(',')) == 3:
                    self.status_table[line.split(',')[0]]=line.split(',')[1]
                line=ple_nodes_status.readline()            
        except:
            print 'MyOps failed to get nodes from %s '%(self.myops_ple_url+query)

        #print self.status_table
        
        #PLC information
        try:
            plc_nodes_status = urlopen(self.myops_plc_url+query)
            line=plc_nodes_status.readline()
            #get rid of header
            if line.split(',')[0] == 'hostname' and line.split(',')[1] == 'observed_status':
                line=plc_nodes_status.readline()
            while line:
                if len(line.split(',')) == 3:
                    self.status_table[line.split(',')[0]]=line.split(',')[1]
                line=plc_nodes_status.readline()            
        except:
            print 'MyOps failed to get nodes from %s '%(self.myops_plc_url+query)

        return self.status_table

    #return a node table, key is hostname and value (initial RTT) a 0
    def getAvailableNodes(self):
        self.getNodesStatus()
        nodes={}
        for hostname in self.status_table.keys():
            if "measurement-lab.org" in hostname:
                continue
            if self.status_table[hostname]=='BOOT':
                nodes[hostname]=0
        return nodes
    

class Monitor:
    status_table=None
    myops_ple_url=""
    myops_plc_url=""
    
    def __init__(self,username,password,host,slice,key,checked_nodes={}):
        self.slice=slice
        self.key=key
        self.api=PlanetLabAPI(username,password,host)
        self.checked_nodes=checked_nodes
        
    def isNodeHealthy(self,hostname):
        #print hostname
        cmd=subprocess.Popen(['nc', '-z', '-w', '5', hostname, '22'],stdout=subprocess.PIPE,close_fds=True)
        cmd.communicate()[0].strip()
        if cmd.returncode == 0:
            return True
        return False
    
    def isGoodNode(self,hostname):
        target='%s@%s'%(self.slice,hostname)
        cmd=subprocess.Popen(['ssh', '-i', self.key, '-o', 'StrictHostKeyChecking=no', '-o', 'PasswordAuthentication=no', '-o','ConnectTimeout=5' ,'-o', 'ServerAliveInterval=5',target,'pwd'],stdout=subprocess.PIPE,close_fds=True)
        cmd.communicate()[0].strip()
        if cmd.returncode == 0:
            return True
        return False
            
        
    def getHealthyNodes(self):
        nodes={}
        nodes_on_boot=self.api.getBootNodes()
        for hostname in nodes_on_boot:
            if hostname['hostname'] not in self.checked_nodes:
                if self.isNodeHealthy(hostname['hostname']):
                    nodes[hostname['hostname']]=0
        return nodes
    
    def cleanUpNodesList(self):
        slice_nodes=self.api.getSliceHostnames(self.slice)
        sys.stdout.write(" nodes before %d... "%(len(slice_nodes)))
        for hostname in self.api.getSliceHostnames(self.slice):
            if not self.isGoodNode(hostname):
                print 'BAD NODE:%s'%hostname
                slice_nodes.remove(hostname)
        sys.stdout.write(" nodes after %d... "%(len(slice_nodes)))
        self.api.updateSliceNodes(self.slice, slice_nodes)
                
            
                
    
