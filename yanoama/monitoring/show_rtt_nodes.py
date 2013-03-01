import sys
import pickle


##this shows the content of nodes files
##how to call it:
#python show_rrt_nodes.py nodes.pck |sort -t, -k1 -nr|less
#this prints out the list of nodes
#and sort it based on rrt time in
#decrescent order
filename=sys.argv[1]

myfile = open(filename, "r") # read mode
dictionary = pickle.load(myfile)
myfile.close()
for node in dictionary:
        print str(dictionary[node])+","+node
print len(dictionary)