#this script computes rtt, loss, and jitter for a set of nodes
#nodes should be listed in (host_table.pck) dictionary file
#to be passed as argument
import pickle,sys,os,socket,math
from datetime import datetime
from time import time
#from planetlab import Monitor
from configobj import ConfigObj
from subprocess import PIPE, Popen 


#main
MAX_LENGTH=int(math.pow(2,20))
RTT_KEY='rtt'
JITTER_KEY='jitter'
LOSS_KEY='loss'
LIST_OF_KEYS=[RTT_KEY,LOSS_KEY,JITTER_KEY]

def getMeasurements(hostname,yanoama_homedir,list_of_keys):
    #we assume that the sequence of values of the output of the following
    #script is LIST_OF_KEYS=[RTT_KEY,LOSS_KEY,JITTER_KEY]
    script_path=yanoama_homedir+"/yanoama/monitoring/get_rtt_loss_jitter.sh"
    try:
        measurements={}
        output_string=(Popen("sh "+script_path+" "+hostname, stdout=PIPE,shell=True).communicate()[0])
        index=0
        for measurement in test_string.split(','):
            measurements[list_of_keys[index]]=float(measurement)
            index=index+1
        return measurements
    except:
        return None

def getRTT(hostname,yanoama_homedir):
    script_path=yanoama_homedir+"/yanoama/monitoring/get_rtt.sh"
    try:
        return (float(Popen("sh "+script_path+" "+hostname, stdout=PIPE,shell=True).communicate()[0]))
    except:
        return -1

def save_object_to_file(myobject,output_file):
    f = open(output_file,'w')
    pickle.dump(myobject, f)
    f.close()

def load_object_from_file(input_file):
    return pickle.load( open( input_file, "rb" ) )

def add_measurement_to_table(mytable,peer_key,list_of_keys,max_lentgh,measurements):
    for list_key in list_of_keys:
        measurement=measurements[list_key]      
        if not len(mytable[peer_key][list_key])<max_lentgh:
            (mytable[peer_key][list_key]).pop(0)
        (mytable[peer_key][list_key]).append(measurement)
    return mytable
    

#todo
##get more information about the nodes and
##especially, collect multiple information about the latencies
yanoama_homedir=(sys.argv[1])
host_table=load_object_from_file(sys.argv[2])
myhostname=(socket.gethostname())
matrix_file="/home/upmc_aren/"+myhostname+"_rtt_matrix.pck"
matrix=None
if os.path.isfile(matrix_file):
    try:
        matrix=load_object_from_file(matrix_file)
    except:
        sys.exit(1)
else:
    matrix={}
    for node in host_table:
        #legacy code, there was a single entry per node, the smallest measurements
        #this was when there was a sigle measurement, the rtt
        #matrix[node]=-1
        #the the code was update to have many sample for a single node
        #since 2 June 2016, rtt,loss, and jitter have been measured
        #in a dictionary, where the name of the metric is its key
        matrix[node]={RTT_KEY:[],LOSS_KEY:[],JITTER_KEY:[]}
    

total_nodes=len(host_table)
prepered_nodes=1
for peer in host_table:
    sys.stdout.write('(%d/%d)%s: '%(prepered_nodes,total_nodes,peer))
    prepered_nodes=prepered_nodes+1
    if peer not in matrix:
        #matrix[peer]=-1
        matrix[peer]={RTT_KEY:[],LOSS_KEY:[],JITTER_KEY:[]}
    #it is not a dict
    if not isinstance(matrix[peer], dict):
        if isinstance(matrix[peer], list):
            #we suppose in this case that the previous object is a 
            #list of measurements of rtt
            rtt_meausrements=matrix[peer]
            matrix[peer]={RTT_KEY:rtt_meausrements,LOSS_KEY:[],JITTER_KEY:[]}
        elif isinstance(matrix[peer], (int,float,long)):
            if matrix[peer] > 0.0:
                mes=matrix[peer]
                matrix[peer]={RTT_KEY:[mes],LOSS_KEY:[],JITTER_KEY:[]}
            else:
                matrix[peer]={RTT_KEY:[],LOSS_KEY:[],JITTER_KEY:[]}
        else:
            matrix[peer]={RTT_KEY:[],LOSS_KEY:[],JITTER_KEY:[]}
            
    if peer != myhostname:
        measurements=getMeasurements(peer,yanoama_homedir,LIST_OF_KEYS)
        if measurements is not None:
            matrix=add_measurement_to_table(matrix, peer, LIST_OF_KEYS, MAX_LENGTH, measurements)
#         if rtt > 0.0:
#             if not len(matrix[peer])<MAX_LENGTH:
#                 matrix[peer].pop(0)
#             (matrix[peer]).append(rtt)
                
    print "done."
    
save_object_to_file(matrix, matrix_file)

