#!/usr/bin/env python

try:
    import json
except ImportError:
    import simplejson as json

import subprocess
from random import sample
import os

##this script checks the role of the node
#and installs cron and amen (for coordinator) 
try:
    config_file = file('/etc/yanoama.conf').read()
    config = json.loads(config_file)
except:
    print "There was an error in your configuration file (/etc/yanoama.conf)"
    raise


#globals
_coordinators = config.get('coordinators', {})
_ple_deployment = config.get('ple_deployment', {})
DEPLOYMENT_PATH=_ple_deployment['path']
_amen = config.get('amen', {})
STORAGE_PATH = _ple_deployment['storage_path']
AMEN_HOME=_amen['home']
HOSTNAME = subprocess.Popen(['hostname'], \
                            stdout=subprocess.PIPE,\
                            close_fds=True).\
                            communicate()[0].rstrip()
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
        f.write(current_jobs+'\n')
    f.write(mystring)
    f.close()
    subprocess.Popen(['crontab',cron_temp_file], \
                    stdout=subprocess.PIPE, \
                    close_fds=True)
    #remove temporary cron backup file
    #clean up
    #subprocess.Popen(['rm', cron_temp_file], \
    #                     stdout=subprocess.PIPE, close_fds=True)
    
def install_runnable_script(script,\
                            deployment_path=DEPLOYMENT_PATH,\
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
                      deployment_path+\
                      '/'+script,\
                      dst_dir],\
                     stdout=subprocess.PIPE, \
                     close_fds=True)
    #making it runnable
    subprocess.Popen(['sudo','chmod', 'guo+x',\
                      (dst_dir+'/'+script.split('/')[-1])],\
                     stdout=subprocess.PIPE,\
                     close_fds=True)

#deployment is based on the node role
#that's either coordinator or peer
if __name__ == '__main__':
    """Deploy yanoama based on the node role,
    either peer or coordinator.

    """
    if HOSTNAME in _coordinators.keys():
        """this is a coordinator
        #here the two-step installation procedure
        #1) install cron jobs: get_rtt.py and
        #                    peering.py
        #2) install mongodb database as part of amen
        #                    monitoring system.
    
        """
        #
        #
        #(1)installing cron jobs
        ##    get_rtt
        install_runnable_script('/yanoama/monitoring/get_rtt.py')
        #install as a cron job
        install_cron_job("get_rtt.py > /tmp/get_rtt_output.log 2>&1")
        ##    peering.py
        install_runnable_script('/yanoama/system/peering.py')
        #install as a cron job for running twice a day
        install_cron_job("peering.py > /tmp/peering_output.log 2>&1",\
                         'TWICE_A_DAY')
        #(2) install amen in coordinator: mongodb 
        #based on
        #http://docs.mongodb.org/manual/tutorial/install-mongodb-on-red-hat-centos-or-fedora-linux/
        #last visit 5 March 2013
        #listen on 39167 port
        subprocess.Popen(['sudo','cp',DEPLOYMENT_PATH+'/contrib/mongodb/mongod.conf','/etc/mongod.conf'], stdout=subprocess.PIPE, close_fds=True)
        subprocess.Popen(['sudo','/sbin/chkconfig','mongod','on'], stdout=subprocess.PIPE, close_fds=True)
        subprocess.Popen(['sudo','/sbin/service','mongod','start'], stdout=subprocess.PIPE, close_fds=True)    
    
    else:
        """peer/storage node role
        #two-step installation procedure
        #1) install cron jobs: membership.py
        #                    
        #2) install and run amen agent (daemon)
        """
        #
        #
        #(1) install membership script
        install_runnable_script('/yanoama/system/membership.py')
        install_cron_job("membership.py > /tmp/membership_output.log 2>&1")

        #(2) instal/run amen monitoring agent
        #default dir for storing objects/videos
        if os.path.exists(STORAGE_PATH):
            subprocess.Popen(['rm','-rf',STORAGE_PATH], stdout=subprocess.PIPE, close_fds=True)
        subprocess.Popen(['mkdir',STORAGE_PATH], stdout=subprocess.PIPE, close_fds=True)
        #install amen agent/deamon in this peer
        if not os.path.exists(AMEN_HOME):
            subprocess.Popen(['sudo','mkdir',AMEN_HOME],stdout=subprocess.PIPE, close_fds=True)
            subprocess.Popen(['sudo','mkdir',AMEN_HOME+'/bin'],stdout=subprocess.PIPE, close_fds=True)
            subprocess.Popen(['sudo','touch',AMEN_HOME+'/amend.log'],stdout=subprocess.PIPE, close_fds=True)
        subprocess.Popen(['sudo','cp',DEPLOYMENT_PATH+'/contrib/amen/amend',AMEN_HOME+'/bin/'],stdout=subprocess.PIPE, close_fds=True)
        #run daemon
        subprocess.Popen(['sudo','chmod','+x',AMEN_HOME+'/bin/amend'],stdout=subprocess.PIPE, close_fds=True)
        subprocess.Popen(['sudo',AMEN_HOME+'/bin/amend','start'],stdout=subprocess.PIPE, close_fds=True)
            
        print "outside"