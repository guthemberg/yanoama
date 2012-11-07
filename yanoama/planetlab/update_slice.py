#! /usr/bin/env python

import traceback,time,pickle,os,subprocess,sys
sys.path.append('/home/guthemberg/Documents/workplace/yanoama/yanoama/planetlab/')
from datetime import datetime
from time import mktime
from planetlab import PlanetLabAPI
from configobj import ConfigObj
from socket import gethostbyname_ex,gethostname
try:
    import json
except ImportError:
    import simplejson as json

TUNNEL_HOST="localhost"
TUNNEL_PORT=8443
END_PORT=443
END_SERVER="www.planet-lab.eu"
SSH_PROXY="ple2.ipv6.lip6.fr"
PLE_MAIN_PLAYER=SSH_PROXY
USER="upmc_aren"
SLICE_NAME=USER
TUNNEL="%d:%s:%d"%(TUNNEL_PORT,END_SERVER,END_PORT)
SHIFT_TIME=8*7*24*60*60 #eight weeks in seconds
ORANGE_IP='10.193.128.101'
NODES_DB='nodes.pck'
TMP_DIR='/tmp'
PLE_CONF_FILE='/etc/ple.conf'

def is_at_orange_labs():
    ##there is a exeption here,
    ##if we are in Orange labs, set up a 
    #tunnel to avoid proxy headaches
    if ORANGE_IP in gethostbyname_ex(gethostname())[2]:
        return True
    return False

def get_ple_api():
    config=ConfigObj(PLE_CONF_FILE)
    api=None
    if is_at_orange_labs():
        api=PlanetLabAPI(config['username'],config['password'],TUNNEL_HOST,8443)
    else:
        api=PlanetLabAPI(config['username'],config['password'],config['host'])
    return api

def renew_slice():
    sys.stdout.write("[%s]:renew slice... "%(str(datetime.now())))
    api=get_ple_api()
    #api=PlanetLabAPI(config['username'],config['password'],config['host'],8443)
    #print len(getNodes(api, "upmc_aren"))
    #sys.exit(0)
    #update for eight weeks
    shift_time=SHIFT_TIME
    now = (datetime.utcnow())
    new_expire_time=(int(mktime(now.timetuple()))+shift_time)
    try:
        api.update(new_expire_time)
    except:
        print "Error:", sys.exc_info()[0]
        traceback.print_exc(file=sys.stdout)
      
    print "done."  

#return the hostnames of nodes that make part of the slice
def get_current_nodes(api,slice_name):
    return api.getSliceHostnames(slice_name)
  
# saves nodes list into /tmp/nodes.pck, 
# and returns true
# if its content seems ok
def download_nodes_list(hostname):
    nodes_list=[]
    filename='%s/%s'%(TMP_DIR,NODES_DB)
    #try to fetch the nodes db from the remote host
    subprocess.Popen(['scp', '-q','%s@%s:/home/%s/yanoama/%s'%(USER,hostname,USER,NODES_DB), filename ], stdout=subprocess.PIPE, close_fds=True)
    if os.path.isfile(filename):
        nodes_file = open(filename, "r") # read mode
        dictionary = pickle.load(nodes_file)
        nodes_file.close()
        try:        
            nodes_list=dictionary.keys()
        except:
            pass        
    #remove downloaded file
    subprocess.Popen(['rm', '-f',filename ], stdout=subprocess.PIPE, close_fds=True)
    return nodes_list
      
def update_nodes():
    sys.stdout.write("[%s]:update slice nodes... "%(str(datetime.now())))
    try:
        config_file = file('/etc/yanoama.conf').read()
        config = json.loads(config_file)
    except:
        print "There was an error in your configuration file (/etc/yanoama.conf)"
        traceback.print_exc(file=sys.stdout)
        print "failed."  
        return
        #print "There was an error in your configuration file (/etc/yanoama.conf)"
        #raise e
    
    
    _coordinators = config.get('coordinators', {})
    
    #get PLE API
    api=get_ple_api()

    for node in _coordinators.keys():
        fresh_nodes_list = download_nodes_list(node)
        if len(fresh_nodes_list)>0:
            sys.stdout.write("before there were %d nodes, "%(len(get_current_nodes(api, SLICE_NAME))))
            try:
                api.updateSliceNodes(SLICE_NAME, fresh_nodes_list)
                sys.stdout.write("now %d nodes, "%(len(get_current_nodes(api, SLICE_NAME))))
            except:
                traceback.print_exc(file=sys.stdout)
                print "failed."  
                return

            break
        
    
    #todo: download a list of nodes from coordinators list, then update our nodes list
    print "done."  
    return

if __name__ == '__main__':
    print "[%s]:update slice..."%(str(datetime.now()))
    
    if is_at_orange_labs():
        #run a tunnel in background
        subprocess.Popen(['ssh', '-f', '-L',TUNNEL,'%s@%s'%(USER,SSH_PROXY), '-N' ], stdout=subprocess.PIPE, close_fds=True)
        #wait five seconds before connecting to the API (for tunnel set-up)
        print "...zzz..."
        time.sleep(5)
    
    #main functions
    renew_slice()
    update_nodes()
    
    if is_at_orange_labs():
        #before say goodbye, shutdown the tunnel
        subprocess.Popen(['pkill', '-f',TUNNEL ], stdout=subprocess.PIPE, close_fds=True)
    print "[%s]:finished."%(str(datetime.now()))  
    sys.exit(0)
