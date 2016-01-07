import pickle,sys,os,socket
from datetime import datetime
from time import time
#from planetlab import Monitor
from configobj import ConfigObj
from subprocess import PIPE, Popen 



def getRTT(hostname):
    try:
        return (float(Popen("sh "+"/home/upmc_aren/yanoama/monitoring/get_rtt.sh "+hostname, stdout=PIPE,shell=True).communicate()[0]))
    except:
        return -1

def save_object_to_file(myobject,output_file):
    f = open(output_file,'w')
    pickle.dump(myobject, f)
    f.close()

def load_object_from_file(input_file):
    return pickle.load( open( input_file, "rb" ) )


#main

myhostname=(socket.gethostname())
matrix_file="/home/upmc_aren/rtt_matrix.pck"
matrix=None
if os.path.isfile(matrix_file):
    try:
        matrix=load_object_from_file(matrix_file)
    except:
        sys.exit(1)


for peer in matrix:
    if peer != myhostname:
        rtt=getRTT(peer)
        if rtt > 0:
            if matrix[peer] > 0 and matrix[peer]>rtt:
                matrix[peer]=rtt
    
save_object_to_file(matrix, matrix_file)
