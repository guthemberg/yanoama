#!/usr/bin/env python

from pymongo import MongoClient
from random import sample

'''
Created on 12 Mar 2013

@author: guthemberg
'''
try:
    import json
except ImportError:
    import simplejson as json

#looking for yanoama module
def get_install_path():
    try:
        config_file = file('/etc/yanoama.conf').read()
        config = json.loads(config_file)
    except Exception, e:
        print "There was an error in your configuration file (/etc/yanoama.conf)"
        raise e
    _ple_deployment = config.get('ple_deployment', {"path":"/home/upmc_aren/yanoama"})
    return (_ple_deployment['path']) 

import sys
try:
    from yanoama.core.essential import Essential,\
                                get_hostname
except ImportError:
    sys.path.append(get_install_path()) 
    from yanoama.core.essential import Essential,\
                                get_hostname


class Mongo:
    '''
    classdocs
    '''


    def __init__(self,hostname=get_hostname()):
        '''
        Constructor
        '''
        self.server=hostname
        self.kernel=Essential()    
        self.db_name =self.kernel.get_db_name()
        self.db_port = self.kernel.get_db_port()
        self.connection = MongoClient(hostname, self.db_port)
        self.db=self.connection[self.db_name]
    
    def convert_dict_keys_from_dots_to_colons(self,my_dict):
        #this assumes that 
        #keys are stringsjust the first key 
        #has colons
        converted_dict={}
        for key in my_dict.keys():
            converted_dict[key.replace('.',':')]=my_dict[key]
        return converted_dict

    def recover_dict_keys_from_colons_to_dots(self,my_dict):
        #this assumes that 
        #keys are stringsjust the first key 
        #has colons
        converted_dict={}
        for key in my_dict.keys():
            converted_dict[key.replace(':','.')]=my_dict[key]
        return converted_dict
    
    def cleanup_nodes(self,hostname_list,nodes):
        #clean up 
        for hostname in hostname_list:
            del nodes[hostname]
        return nodes

    def remove_indexes_nodes(self,indexes_list,nodes):
        #clean up 
        hostname_list=[]
        hostnames=nodes.keys()
        for index in indexes_list:
            hostname_list.append(nodes[hostnames[index]])
        return self.cleanup_nodes(hostname_list, nodes)
        
    def save_raw_nodes(self,nodes):
        #this randomly selects nodes 
        #first convert hostnames
        #comma-separated to dot-
        #separated, mongo db does
        #not accept keys with dots 
        latency=self.kernel.get_latency()
        group_size=self.kernel.get_group_size(self.server)
        converted_nodes=self.convert_dict_keys_from_dots_to_colons(nodes)
        too_far_nodes=[]
        #first clean up nodes that are too far
        for hostname in converted_nodes:
            if converted_nodes[hostname]>latency:
                too_far_nodes.append(hostname)
        #clean up 
        self.cleanup_nodes(too_far_nodes, converted_nodes)
        #pick nodes randomly
        start=0
        stop=len(converted_nodes)
        random_indexes=sample(xrange(start,stop),\
                              max(0,stop-group_size))
        self.remove_indexes_nodes(random_indexes, converted_nodes)
        nodes_latency_measurements=self.db.nodes_latency_measurements
        nodes_latency_measurements.drop()
        nodes_latency_measurements.insert(converted_nodes)

    def get_peers(self,hostname=get_hostname()):  
        """Connects to a coordinator MongoBD database
        and retrieves the list of member nodes of
        this storage domain. It gets information from
        db['nodes_latency_measurements'] entry. Port 
        number and  database name come from the main 
        configuration file (yanoama.conf)
    
        Keyword arguments:
        coordinator  -- coordinator to connect and
        retrieve information (default localhost)
    
        Returns:
        dictionary -- members information where keys 
        are the hostnames
    
        """
        if hostname == self.server:
            return self.recover_dict_keys_from_colons_to_dots(self.db['nodes_latency_measurements'].find_one({}, {'_id': False}).copy())
        else:
            connection = MongoClient(hostname, self.db_port)
            db=connection[self.db_name]
            return self.recover_dict_keys_from_colons_to_dots(db['nodes_latency_measurements'].find_one({}, {'_id': False}).copy())

    def save_peers(self,nodes):  
        """Save the current list of member nodes to the
        local instance of MongoDB database. Port and 
        database name come from the main configuration
        file (/etc/yanoama.conf). 
    
        Keyword arguments:
        nodes -- list of current members of this storage 
        domain
    
        """
        peers=self.db.peers
        peers.drop()
        peers.insert(self.convert_dict_keys_from_dots_to_colons(nodes))

    def am_i_a_member_of_this(self,coordinator):  
        """Checks if this node is member of the
        'coordinator' storage domain. Port and 
        database name come from the main configuration
        file (/etc/yanoama.conf). 
    
        Keyword arguments:
        nodes -- coordinator hostname
    
        Returns:
        boolean -- member or not
        """
        connection = MongoClient(coordinator, self.db_port)
        db = connection[self.db_name]
        recovered_peers = self.recover_dict_keys_from_colons_to_dots(db['peers'].find_one({}, {'_id': False}))
        return get_hostname() in recovered_peers.keys()
    
        