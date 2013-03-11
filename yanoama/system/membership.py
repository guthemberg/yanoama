#!/usr/bin/env python

from pymongo import Connection
try:
    import json
except ImportError:
    import simplejson as json
import subprocess
import os
from datetime import datetime

def get_db_name_and_port():
    """Gets port and database name information
    from the main configuration file
    file (/etc/yanoama.conf). 

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
    return _mongo.get('db_name','yanoama'),\
        _mongo.get('port',39167)

def am_i_a_member_of_this(coordinator):  
    """Checks if this node is member of the
    'coordinator' storage domain. Port and 
    database name come from the main configuration
    file (/etc/yanoama.conf). 

    Keyword arguments:
    nodes -- coordinator hostname

    Returns:
    boolean -- member or not
    """
    db_name,port=get_db_name_and_port()
    connection = Connection(coordinator, port)
    db = connection[db_name]
    HOSTNAME = subprocess.Popen(['HOSTNAME'], stdout=subprocess.PIPE, close_fds=True)\
    .communicate()[0].rstrip()
    return HOSTNAME in db['peers'].find_one({}, {'_id': False}).keys()

def get_all_coordinators():
    """Gets the list of coordinators from 
    the main configuration file (/etc/yanoama.conf). 

    Returns:
    list of strings -- coordinators hostnames

    """
    try:
        config_file = file('/etc/yanoama.conf').read()
        config = json.loads(config_file)
    except Exception, e:
        print "There was an error in your configuration file (/etc/yanoama.conf)"
        raise e
    _coordinators = config.get('coordinators', {})
    return _coordinators.keys()

def get_coordinator_ip(coordinator):
    """Gets the ip address of a specific 
    coordinator from the list available on
    the main configuration file 
    (/etc/yanoama.conf). 

    Keyword arguments:
    coordinator -- coordinator hostname

    Return
    string -- ip address
    """
    try:
        config_file = file('/etc/yanoama.conf').read()
        config = json.loads(config_file)
    except Exception, e:
        print "There was an error in your configuration file (/etc/yanoama.conf)"
        raise e
    _coordinators = config.get('coordinators', {})
    return _coordinators[coordinator]['ip']

def build_hosts_file(coordinator=None):
    """Creates /etc/hosts file based on 
    coordinator. If coordinator is None,
    there will be no coordinator entry,
    otherwise resolve its name and add
    a coordinator entry to /etc/hosts. 

    Keyword arguments:
    coordinator -- hostname

    """
    hosts_file='/etc/hosts'
    hosts_origin_file='/etc/hosts.origin'
    temp_hosts_file='/tmp/hosts'
    temp_file='/tmp/hosts_1'
    #check if /etc/hosts.origin exists 
    if not os.path.exists(hosts_origin_file):
        subprocess.Popen(['sudo','cp', '-f',hosts_file,hosts_origin_file], \
                         stdout=subprocess.PIPE, close_fds=True)
    if coordinator is None:
        subprocess.Popen(['sudo','cp', '-f',hosts_origin_file,hosts_file], \
                         stdout=subprocess.PIPE, close_fds=True)
    else:
        f = open(temp_file, 'w')  
        f.write(get_coordinator_ip(coordinator)+'\t\t'+coordinator+'\n')
        f.close()
        #check if /etc/hosts.origin exists 
        output_file=open(temp_hosts_file,'w')
        subprocess.Popen(['sudo','cat',temp_file,hosts_origin_file], \
                         stdout=output_file, close_fds=True)
        output_file.close()
        subprocess.Popen(['sudo','cp', '-f',temp_hosts_file,hosts_file], \
                         stdout=subprocess.PIPE, close_fds=True)
        #clean up
        subprocess.Popen(['sudo','rm', temp_file,temp_hosts_file], \
                             stdout=subprocess.PIPE, close_fds=True)

#print out a message along with
#time to the standard output
#args:
#msg: message to be printed
def log(msg):
    """Print out a message to the standard
    output along with now-time information. 

    Keyword arguments:
    msg -- log message to be printed

    """
    now = datetime.now()
    print now.strftime("%Y-%m-%d %H:%M")+': '+msg

#checks a hostname exists in the hosts file
def check_hostname(hostname='coordinator',\
                      hosts_file='/etc/hosts'):
    """Check if a hostname exists in  hosts
    file. 

    Keyword arguments:
    hostname -- hostname to check (default coordinator)
    hosts_file -- local hosts db (default /etc/hosts)

    Returns:
    string -- information about a hostname, or
    'unknown' if it is not found in the hosts file
    
    """
    grep_host_output=subprocess.\
    Popen(['grep',hostname,hosts_file],\
           stdout=subprocess.PIPE,close_fds=True).\
           communicate()[0].rstrip()
    if len(grep_host_output)==0:
        return 'unknown'
    return grep_host_output
                                      
    
if __name__ == '__main__':
    for coordinator in get_all_coordinators():
        if am_i_a_member_of_this(coordinator):
            build_hosts_file(coordinator)
            return
    build_hosts_file()
    hostname='coordinator'
    log(hostname+' ('+check_hostname(hostname)+'), done.')
