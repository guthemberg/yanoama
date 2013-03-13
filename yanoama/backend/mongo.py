#!/usr/bin/env python

from pymongo import MongoClient

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


    def __init__(self,hostname='localhost'):
        '''
        Constructor
        '''
        self.localhost=hostname
        self.kernel=Essential()    
        self.db_name =self.kernel.get_db_name()
        self.db_port = self.kernel.get_db_port()
        self.hostname=hostname
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
    
    def save_raw_nodes(self,nodes): 
        #first convert hostnames
        #comma-separated to dot-
        #separated, mongo db does
        #not accept keys with dots 
        converted_nodes=self.convert_dict_keys_from_dots_to_colons(nodes)
        latency=self.kernel.get_latency()
        too_far_nodes=[]
        for hostname in converted_nodes.keys():
            if converted_nodes[hostname]<latency:
                too_far_nodes.append(hostname)
        #clean up bad nodes
        for hostname in too_far_nodes:
            del converted_nodes[hostname]
        nodes_latency_measurements=self.db.nodes_latency_measurements
        nodes_latency_measurements.drop()
        nodes_latency_measurements.insert(converted_nodes)

    def get_peers(self,hostname='localhost'):  
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
        if hostname == self.hostname:
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
    
        