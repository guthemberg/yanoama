#!/home/upmc_aren/python_env/bin/python


import traceback,time,pickle,os,subprocess,sys
sys.path.append('/home/guthemberg/Documents/workplace/yanoama/yanoama/planetlab/')
from datetime import datetime
from time import mktime
from planetlab import PlanetLabAPI
from configobj import ConfigObj
import socket

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

def get_main_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('google.com', 0))
    return s.getsockname()[0]
    
def is_at_orange_labs():
    ##there is a exeption here,
    ##if we are in Orange labs, set up a 
    #tunnel to avoid proxy headaches
    #if ORANGE_IP in gethostbyname_ex(gethostname())[2]:
    if ORANGE_IP == get_main_ip():
        #print gethostbyname_ex(gethostname())[2]
        #print "ORANGE! :(
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
    config=ConfigObj(PLE_CONF_FILE)
    key=config['key']
    #try to fetch the nodes db from the remote host
    #scp_output = subprocess.Popen(['scp', '-q','-i',key,'%s@%s:/home/%s/yanoama/%s'%(USER,hostname,USER,NODES_DB), filename ], stdout=subprocess.PIPE, close_fds=True).communicate()[0]
    scp_output = subprocess.Popen(['scp', '-i',key,'%s@%s:/home/%s/yanoama/%s'%(USER,hostname,USER,NODES_DB), filename ], stdout=subprocess.PIPE, close_fds=True).communicate()[0]
    if len(scp_output)>0: 
        sys.stdout.write(" .. (scp output: %s ... )"%(scp_output))
    if os.path.isfile(filename):
        nodes_file = open(filename, "r") # read mode
        dictionary = pickle.load(nodes_file)
        nodes_file.close()
        try:
            #sys.stdout.write(" (dic len: %d )"%(len(dictionary)))
            nodes_list=dictionary.keys()
        except:
            sys.stdout.write(" (error in loading the dictionary )")
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

    if len(_coordinators.keys())==0:
        sys.stdout.write(" no coordinators ")
    for hostname in _coordinators.keys():
        fresh_nodes_list = download_nodes_list(hostname)
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
        else:
            sys.stdout.write("empty list in %s... "%(hostname))
        
    
    #todo: download a list of nodes from coordinators list, then update our nodes list
    print "done."  
    return

if __name__ == '__main__':
    print "[%s]:update slice..."%(str(datetime.now()))
    
    config=ConfigObj(PLE_CONF_FILE)
    key=config['key']
    if is_at_orange_labs():
        #create config file for orange labs
        subprocess.Popen(['cp','/home/guthemberg/.ssh/config_that_works','/home/guthemberg/.ssh/config'], stdout=subprocess.PIPE, close_fds=True)
        #run a tunnel in background
        subprocess.Popen(['ssh','-f','-i',key,'-L',TUNNEL,'%s@%s'%(USER,SSH_PROXY),'-N' ], stdout=subprocess.PIPE, close_fds=True)
        #wait five seconds before connecting to the API (for tunnel set-up)
        print "...zzz..."
        time.sleep(5)
    else:
        #delete config for orange
        subprocess.Popen(['rm','-f','/home/guthemberg/.ssh/config'], stdout=subprocess.PIPE, close_fds=True)
    
    #main functions
    renew_slice()
    update_nodes()
    
    if is_at_orange_labs():
        #before say goodbye, shutdown the tunnel
        subprocess.Popen(['pkill', '-f',TUNNEL ], stdout=subprocess.PIPE, close_fds=True)
    print "[%s]:finished."%(str(datetime.now()))  
    sys.exit(0)
