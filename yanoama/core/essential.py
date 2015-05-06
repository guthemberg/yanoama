#!/usr/bin/env python
'''
Created on 12 Mar 2013

@author: guthemberg
'''
from subprocess import PIPE, Popen 
from datetime import datetime
import pickle
import subprocess
from random import sample
from time import sleep
import os
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
    from yanoama.planetlab.planetlab import MyOps 
    from yanoama.planetlab.planetlab import Monitor 
except ImportError:
    sys.path.append(get_install_path()) 
    from yanoama.planetlab.planetlab import MyOps 
    from yanoama.planetlab.planetlab import Monitor 


class Essential:
    '''
    classdocs
    '''


    def __init__(self,conf_file='/etc/yanoama.conf'):
        '''
        Constructor
        '''
        try:
            config_file = file(conf_file).read()
            config = json.loads(config_file)
        except Exception, e:
            print "There was an error in your configuration file (/etc/yanoama.conf)"
            raise e
        _amen = config.get('amen', {})
        self.amen_home=_amen['home']
        _backend = _amen.get('backend', {})
        _mongo = _backend.get('mongo', {})    
        self.db_name= _mongo.get('db_name','yanoama')
        self.db_port=_mongo.get('port',39167)
        self.db_replication_port=_mongo.get('replication_port',40167)
        self.coordinators=config.get('coordinators', {})
        _ple_deployment = config.get('ple_deployment', {})
        self.deployment_path=_ple_deployment['path']
        self.storage_path = _ple_deployment['storage_path']
        _pilot = config.get('pilot', {})
        self.pilot_port=_pilot.get('port',44444)

    def get_group_size(self,coordinator):
        return self.coordinators.get(coordinator).get('group_size')
    
    def is_coordinator(self,hostname):
        return hostname in self.coordinators
    
    def get_deployment_path(self):
        return self.deployment_path

    def get_coordinators(self,hostname_exception=None):
        """Gets the list of coordinators from 
        the main configuration file (/etc/yanoama.conf). 
    
        Keyword arguments:
        hostname_exception -- hostname to be deleted from 
        the returned list 

        Returns:
        list of strings -- coordinators hostnames
    
        """
        coordinators_copy=self.coordinators.copy()
        if hostname_exception is not None:
            del coordinators_copy[hostname_exception]
        return coordinators_copy

    def get_coordinator_ip(self,coordinator):
        """Gets the ip address of a specific 
        coordinator from the list available on
        the main configuration file 
        (/etc/yanoama.conf). 
    
        Keyword arguments:
        coordinator -- coordinator hostname
    
        Return
        string -- ip address
        """
        return self.coordinators[coordinator]['ip']
    
    def get_pilot_port(self):
        return self.pilot_port

    def get_storage_path(self):
        return self.storage_path

    def get_amen_home(self):
        return self.amen_home
    
    def get_db_name(self):
        return self.db_name    

    def get_db_port(self):
        return self.db_port

    def get_db_replication_port(self):
        return self.db_replication_port

    def get_latency(self,coordinator=''):
        if len(coordinator)==0:
            coordinator = Popen(['hostname'], \
                             stdout=PIPE, \
                             close_fds=True).\
                             communicate()[0].rstrip()
        return float(self.coordinators.get(coordinator).\
                     get('latency'))
        
    def install_runnable_script(self,script,\
                                dst_dir='/bin/'):
        """Install a script to a directory of the local
        path and make it runnable, where script is a relative
        path of deployment_path.
    
        Keyword arguments:
        script -- path to the script relative to 
        deployment path 
        deployment_path -- where yanoama is installed 
        (default DEPLOYMENT_PATH global)
        dst_dir -- destination path to install this 
        script (default '/bin')
    
        """
        subprocess.Popen(['sudo','cp',\
                          self.deployment_path+\
                          '/'+script,\
                          dst_dir],\
                         stdout=subprocess.PIPE, \
                         close_fds=True)
        sleep(1)
        #making it runnable
        subprocess.Popen(['sudo','chmod', 'guo+x',\
                          (dst_dir+'/'+script.split('/')[-1])],\
                         stdout=subprocess.PIPE,\
                         close_fds=True)
    
def log_to_file(msg,logfile):
    nodes_file = open(logfile, "a") # read mode
    now = datetime.now()
    nodes_file.write(now.strftime("%Y-%m-%d %H:%M")+': '+msg)
    nodes_file.close()

def log(msg):
    """Print out a message to the standard
    output along with now-time information. 

    Keyword arguments:
    msg -- log message to be printed

    """
    now = datetime.now()
    print now.strftime("%Y-%m-%d %H:%M")+': '+msg

#see bootstratNodesFile() for having information about the file format
def readNodes(filename):
    nodes_file = open(filename, "r") # read mode
    dictionary = pickle.load(nodes_file)
    nodes_file.close()
    return dictionary

#see bootstratNodesFile() for having information about the file format
def saveNodes(dictionary,filename):
    nodes_file = open(filename, "w") # write mode
    pickle.dump(dictionary, nodes_file)
    nodes_file.close()

##gets a comma-separated samples as a
#string for cron jobs
def get_cron_time_samples(start,stop,samples):
    """Get a comma-separated samples as a 
    string for cron jobs. 

    Keyword arguments:
    start -- start integer to sample
    stop -- stop integer to sample
    samples -- number of samples

    Returns:
    string -- comma-separated list of samples
    from the start-stop range 
    
    """
    return str(sample(xrange(start,stop),samples)).\
        replace(' ','').\
        replace(']','').replace('[','')
        
#this installs a cron job to the local
#cron. the frequency might be once, twice
#a day.
#args: 
#job: string with cron job
#frequency: how many daily calls,
#    default is ONCE_A_DAY
def install_cron_job(job,frequency='ONCE_A_DAY'):
    """Add a job to the local
    crontable. the frequency might be once, twice 
    a day.. 

    Keyword arguments:
    job -- command or job from cron
    frequency -- to run this job (default ONCE_A_DAY)
    """
    
    minute=get_cron_time_samples(0, 60, 1)
    hour=""
    if(frequency=='TWICE_A_DAY'):
        #twice a day
        #once a day
        hour= get_cron_time_samples(0, 24, 2)
    else:
        #once a day
        hour=get_cron_time_samples(0, 8, 1)
    mystring = str(minute)+"       "+str(hour)+\
    "     *       *       *       "+job
    cron_temp_file='/tmp/cron.temp'
    #first backup current jobs
    current_jobs=subprocess.\
        Popen(['crontab', '-l'], \
          stdout=subprocess.PIPE, close_fds=True).communicate()[0]
    f = open(cron_temp_file, 'w')  
    if len(current_jobs)>0:
        f.write(current_jobs)
    f.write(mystring+'\n')
    f.close()
    sleep(1)
    subprocess.Popen(['crontab',cron_temp_file], \
                    stdout=subprocess.PIPE, \
                    close_fds=True)
    
    sleep(1)
    #clean up
    subprocess.Popen(['rm', cron_temp_file], \
                         stdout=subprocess.PIPE, close_fds=True)
    
def get_hostname():
    return subprocess.Popen(['hostname'], \
                            stdout=subprocess.PIPE,\
                            close_fds=True).\
                            communicate()[0].rstrip()

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
    kernel=Essential()
    #check if /etc/hosts.origin exists 
    if not os.path.exists(hosts_origin_file):
        subprocess.Popen(['sudo','cp', '-f',hosts_file,hosts_origin_file], \
                         stdout=subprocess.PIPE, close_fds=True)
    sleep(1)
    if coordinator is None:
        subprocess.Popen(['sudo','cp', '-f',hosts_origin_file,hosts_file], \
                         stdout=subprocess.PIPE, close_fds=True)
        sleep(1)
    else:
        f = open(temp_file, 'w')  
        f.write(kernel.get_coordinator_ip(coordinator)+'\t\t'+coordinator+'\n')
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

def getRTT(hostname):
    try:
        return (float(Popen("sh "+get_install_path()+"/yanoama/monitoring/get_rtt.sh "+hostname, stdout=PIPE,shell=True).communicate()[0]))
    except:
        return -1

def online():
    rtt=getRTT('www.google.com')
    if rtt==-1 :
        return False
    return True


def getIntialNodes(username,password,host,cmd_args):
    nodes={}
    filename=''
    if len(cmd_args) > 1:
        filename=cmd_args[1]+'_nodes.pck'
        nodes=readNodes(filename)
    else:
        filename=get_install_path()+'/nodes.pck'
        if os.path.isfile(filename):
            nodes=readNodes(filename)
        else:
            try:
                myops_nodes=MyOps().getAvailableNodes()
                monitor_nodes=Monitor(username,password,host,myops_nodes.keys()).getHealthyNodes()
                nodes=dict(myops_nodes.items()+monitor_nodes.items())
            except:
                print 'FATAL EEROR: failed to get myops or monitor information: nodes=MyOps().getAvailableNodes(). bye.'
                sys.exit(-1)
    return nodes,filename

def checkNodes(nodes,myops_nodes,bad_nodes,new_nodes=None):
    if new_nodes is not None:
        for hostname in new_nodes:
            rtt=getRTT(hostname)
            if rtt>0.0 :
                nodes[hostname]=rtt
        return
            
    for hostname in nodes:
        if "measurement-lab.org" in hostname:
            bad_nodes.append(hostname)
            continue
        c_rtt = float(nodes[hostname])
        rtt=getRTT(hostname)
        if rtt>0.0 :
            if c_rtt==0.0 :
                nodes[hostname]=rtt
            elif rtt<c_rtt:
                nodes[hostname]=rtt
        else:
            bad_nodes.append(hostname)
        #if it is in myops nodes, remove it
        try:
            del myops_nodes[hostname]
        except:
            pass
