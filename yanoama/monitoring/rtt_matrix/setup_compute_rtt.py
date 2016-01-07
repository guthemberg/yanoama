import pickle,sys,socket,subprocess,os,git,random
from datetime import datetime
from time import time
#from planetlab import Monitor
from configobj import ConfigObj

def save_object_to_file(myobject,output_file):
    f = open(output_file,'w')
    pickle.dump(myobject, f)
    f.close()

def load_object_from_file(input_file):
    return pickle.load( open( input_file, "rb" ) )


if __name__ == '__main__':
    
    print "[%s]:update membership..."%(str(datetime.now()))    
    ple_lib_path='/home/upmc_aren/yanoama/planetlab'
    sys.path.append(ple_lib_path)
    
    from planetlab import PlanetLabAPI
    config=ConfigObj("/etc/ple.conf")
    ple = PlanetLabAPI(config['username'],config['password'],config['host'])
    ple_nodes=ple.getSliceHostnames(config['slice'])

    matrix_file="/home/upmc_aren/rtt_matrix.pck"
    matrix={}
    
    for node in ple_nodes:
        matrix[node]=-1.0

    save_object_to_file(matrix, matrix_file)

    for node in matrix:        
        ((Popen("sh "+"/home/upmc_aren/yanoama/monitoring/setup_basics.sh "+node, stdout=PIPE,shell=True).communicate()[0]))
