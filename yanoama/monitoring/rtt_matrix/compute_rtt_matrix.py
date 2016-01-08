import pickle,sys,os,socket
from datetime import datetime
from time import time
#from planetlab import Monitor
from configobj import ConfigObj
from subprocess import PIPE, Popen 



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


#main
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
        matrix[node]=-1
    

total_nodes=len(host_table)
prepered_nodes=1
for peer in host_table:
    sys.stdout.write('(%d/%d)%s: '%(prepered_nodes,total_nodes,peer))
    prepered_nodes=prepered_nodes+1
    if peer not in matrix:
        matrix[peer]=-1
    if peer != myhostname:
        rtt=getRTT(peer,yanoama_homedir)
        if rtt > 0:
            if matrix[peer] > 0 and matrix[peer]>rtt:
                matrix[peer]=rtt
    print "done."
    
save_object_to_file(matrix, matrix_file)

