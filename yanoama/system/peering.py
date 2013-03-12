#!/usr/bin/env python


from pymongo import Connection
import subprocess

try:
    import json
except ImportError:
    import simplejson as json

from datetime import datetime


def get_db_name_and_port():
    """Gets MongoDB database name and port
    from configuration file (/etc/yanoama.conf).

    Returns:
    string,int -- database name and port 

    """
    try:
        config_file = file('/etc/yanoama.conf').read()
        config = json.loads(config_file)
    except Exception, e:
        print "There was an error in your configuration file (/etc/yanoama.conf)"
        raise e
    _amen = config.get('amen', {})
    _backend = _amen.get('backend', {})
    _mongo = _backend.get('mongo', {})    
    return _mongo.get('db_name','yanoama'),_mongo.get('port',39167)

def get_coordinators():
    """Returns the list of coordinators 
    from configuration file (/etc/yanoama.conf).
    
    Returns:
    list of strings -- list of coordinators' 
    hostnames

    """
    try:
        config_file = file('/etc/yanoama.conf').read()
        config = json.loads(config_file)
    except Exception, e:
        print "There was an error in your configuration file (/etc/yanoama.conf)"
        raise e
    _coordinators = config.get('coordinators', {})
    HOSTNAME = subprocess.Popen(['hostname'], stdout=subprocess.PIPE, close_fds=True)\
    .communicate()[0].rstrip()
    del _coordinators[HOSTNAME]
    return _coordinators.keys()


def get_peers(coordinator='localhost'):  
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
    db_name,port=get_db_name_and_port()
    connection = Connection(coordinator, port)
    db = connection[db_name]
    return db['nodes_latency_measurements'].find_one({}, {'_id': False})

def save_to_db(nodes):  
    """Save the current list of member nodes to the
    local instance of MongoDB database. Port and 
    database name come from the main configuration
    file (/etc/yanoama.conf). 

    Keyword arguments:
    nodes -- list of current members of this storage 
    domain

    """
    db_name,port=get_db_name_and_port()
    connection = Connection('localhost', port)
    db = connection[db_name]
    peers=db.peers
    peers.drop()
    peers.insert(nodes)

def log(msg):
    """Print out a message to the standard
    output along with now-time information. 

    Keyword arguments:
    msg -- log message to be printed

    """
    now = datetime.now()
    print now.strftime("%Y-%m-%d %H:%M")+': '+msg

if __name__ == '__main__':
    local_peers=get_peers()
    for coordinator in get_coordinators():
        peers=get_peers(coordinator)
        to_be_removed=[]
        for hostname in peers.keys():
            if local_peers[hostname]>peers[hostname]:
                to_be_removed.append(hostname)
        for hostname in to_be_removed:
            del local_peers[hostname]
    save_to_db(local_peers)
    #log/print out to the standard output
    log('current number of members:'+len(local_peers.keys())+', done.')
