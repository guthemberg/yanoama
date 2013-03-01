from configobj import ConfigObj
from yanoama.planetlab.planetlab import MyOps
from yanoama.planetlab.planetlab import PlanetLabAPI

##print available nodes from api 
#checking their availability through MyOps

myops_nodes=MyOps().getAvailableNodes()

config=ConfigObj('ple.conf')
api=PlanetLabAPI(config['host'],config['username'],config['password'])
api_nodes=[]
for node in (api.getHostnames()):
    api_nodes.append(node['hostname'])
#print api_nodes
#print 'outro'
#print MyOps().getAvailableNodes()
for node in (MyOps().getAvailableNodes()):
    if node not in api_nodes and "measurement-lab.org" not in node:
        print node
