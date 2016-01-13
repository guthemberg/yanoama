import pickle,sys,socket,subprocess,os,random
from datetime import datetime
from time import time
#from planetlab import Monitor
from configobj import ConfigObj
import numpy as np
import matplotlib.pyplot as plt

from sklearn.cluster import MiniBatchKMeans


def save_object_to_file(myobject,output_file):
    f = open(output_file,'w')
    pickle.dump(myobject, f)
    f.close()

def load_object_from_file(input_file):
    return pickle.load( open( input_file, "rb" ) )

def cleanup_measurements(host_table,list_of_nodes):
    measurements=[]
    for node in host_table:
        if node in list_of_nodes:
            if host_table[node]>0.0:
                measurements.append(host_table[node])
            else:
                measurements.append(0.0)
            
    return measurements

if __name__ == '__main__':
    
    measuremants_dir=sys.argv[1]
    list_of_nodes=(sys.argv[2]).split(" ")
#    host_table=load_object_from_file(sys.argv[3])
    file_table_suffix="_rtt_matrix.pck"
    
    host_measurements=[]
    for node in list_of_nodes:
        if len(node)>0:
            node_table=load_object_from_file(measuremants_dir+"/"+node+file_table_suffix)
            host_measurements.append(cleanup_measurements(node_table, list_of_nodes))
        
    inertia=-1.0
    best_n=3
    best_mbk=None
    gain=0
    last_inertia=0
    initian_inertia=0
    acc_gain=0
    last_acc_gain=0
    diff_acc_gain=0
    for n_clusters in range(1,16):
        mbk = MiniBatchKMeans(init='k-means++', n_clusters=n_clusters, n_init=10, verbose=0)
        X=np.array(host_measurements,dtype=float)
        mbk.fit(X)
        if inertia == -1.0:
            inertia=mbk.inertia_
            best_n=n_clusters
            best_mbk=mbk
            last_inertia=mbk.inertia_
            initian_inertia=last_inertia
        elif mbk.inertia_<inertia:
            inertia=mbk.inertia_
            best_n=n_clusters
            best_mbk=mbk
            gain=abs((inertia-last_inertia)/(last_inertia))
            acc_gain=abs((inertia-initian_inertia)/(initian_inertia))
            # WE NEED TO FIX THIS diff_
            last_acc_gain=acc_gain
            last_inertia=mbk.inertia_
        print "number of clusters: %d, inertia: %.4f, gain: %.4f, acc. gain: %.4f"%(n_clusters,mbk.inertia_,gain,acc_gain)
    
    #save objects
    save_object_to_file(list_of_nodes, "/tmp/nodes_list.pck")
    save_object_to_file(best_mbk, "/tmp/mbk.pck")
        
    sys.exit(0)
    
#     
#     # Compute clustering with MiniBatchKMeans
# 
# mbk = MiniBatchKMeans(init='k-means++', n_clusters=3, batch_size=batch_size,
#                       n_init=10, max_no_improvement=10, verbose=0)
# t0 = time.time()
# mbk.fit(X)
# t_mini_batch = time.time() - t0
# mbk_means_labels = mbk.labels_
# mbk_means_cluster_centers = mbk.cluster_centers_
# mbk_means_labels_unique = np.unique(mbk_means_labels)