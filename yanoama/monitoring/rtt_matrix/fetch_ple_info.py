import pickle,sys,socket,subprocess,os,random
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
    
    yanoama_home_dir=sys.argv[1]
    ple_conf=sys.argv[2]
    host_table_file=sys.argv[3]
    print "[%s]:update membership..."%(str(datetime.now()))    
    ple_lib_path=yanoama_home_dir+'/yanoama/planetlab'
    sys.path.append(ple_lib_path)
    
    from planetlab import PlanetLabAPI
    config=ConfigObj(ple_conf)
    ple = PlanetLabAPI(config['username'],config['password'],config['host'])
    ple_nodes=ple.getSliceHostnames(config['slice'])

    print "a sample node: "    
    list_of_login_bases=[]
    host_table={}
    list_of_nodes=""
    for node in ple_nodes:
        site_info=ple.getHostSite(node)
        if site_info['login_base'] not in list_of_login_bases:
            host_table[node]=site_info
            list_of_nodes=node+" "
            
    print "list size: "+str(len(host_table))
    sys.stdout.write(list_of_nodes)
    print ""
    save_object_to_file(host_table, host_table_file)
    sys.exit(0)

    matrix_file="/home/upmc_aren/host_table.pck"
    matrix={}
    
    for node in ple_nodes:
        matrix[node]=-1.0

    save_object_to_file(matrix, matrix_file)

    for node in matrix:        
        ((Popen("sh "+"/home/upmc_aren/yanoama/monitoring/setup_basics.sh "+node, stdout=PIPE,shell=True).communicate()[0]))
