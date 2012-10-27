import xmlrpclib
#working with http data. further information in http://docs.python.org/3.1/howto/urllib2.html
import urllib
#bola

class PlanetLabAPI:
    #api
    auth=None
    api=None
    
    def __init__(self,host,username,password):
        self.auth = { 'AuthMethod' : 'password',
                 'Username' : username,
                 'AuthString' : password
        }
        self.api=xmlrpclib.ServerProxy("https://%s:443/PLCAPI/"%host,allow_none=True)

    def getPLEHostnames(self):
        return (self.api.GetNodes(self.auth,{'peer_id':None},['hostname']))

    def getHostnames(self):
        return (self.api.GetNodes(self.auth,None,['hostname']))

    def getPLCHostnames(self):
        return (self.api.GetNodes(self.auth,{'peer_id':1},['hostname']))

    def update(self,expire_time):
        return (self.api.UpdateSlice(self.auth,'upmc_aren',{'expires':expire_time}))
    
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
        ple_nodes_status = urllib.urlopen(self.myops_ple_url+query)
        line=ple_nodes_status.readline()
        #get rid of header
        if line.split(',')[0] == 'hostname' and line.split(',')[1] == 'observed_status':
            line=ple_nodes_status.readline()
        while line:
            if len(line.split(',')) == 3:
                self.status_table[line.split(',')[0]]=line.split(',')[1]
            line=ple_nodes_status.readline()            

        #PLC information
        plc_nodes_status = urllib.urlopen(self.myops_plc_url+query)
        line=plc_nodes_status.readline()
        #get rid of header
        if line.split(',')[0] == 'hostname' and line.split(',')[1] == 'observed_status':
            line=plc_nodes_status.readline()
        while line:
            if len(line.split(',')) == 3:
                self.status_table[line.split(',')[0]]=line.split(',')[1]
            line=plc_nodes_status.readline()            

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
    
