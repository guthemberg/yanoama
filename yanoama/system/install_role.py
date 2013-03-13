#!/usr/bin/env python

try:
    import json
except ImportError:
    import simplejson as json

import subprocess
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

import os
import sys

try:
    from yanoama.core.essential import Essential, \
                    install_cron_job, get_hostname
except ImportError:
    sys.path.append(get_install_path()) 
    #import yanoama modules alternatively
    from yanoama.core.essential import Essential, \
                    install_cron_job, get_hostname



#deployment is based on the node role
#that's either coordinator or peer
if __name__ == '__main__':
    """Deploy yanoama based on the node role,
    either peer or coordinator.

    """
    kernel=Essential()
    #update services file with temp file, 
    #rest must be done by command line
    temp_services_file='/tmp/services'
    f = open(temp_services_file, 'w')  
    f.write('#local services'+'\n')
    f.write('pilot\t\t'+str(kernel.get_pilot_port())+'/tcp\n')
    f.write('mongo\t\t'+str(kernel.get_db_port())+'/tcp\n')
    f.write('mongo_replication\t\t'+str(kernel.get_db_replication_port())+'/tcp\n')
    f.close()
    
    if get_hostname() in kernel.get_coordinators().keys():
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
        kernel.install_runnable_script('/yanoama/monitoring/get_rtt.py')
        #install as a cron job
        install_cron_job("get_rtt.py > /tmp/get_rtt_output.log 2>&1")
        ##    peering.py
        kernel.install_runnable_script('/yanoama/system/peering.py')
        #install as a cron job for running twice a day
        install_cron_job("peering.py > /tmp/peering_output.log 2>&1",\
                         'TWICE_A_DAY')
        #set role
        temp_services_file='/tmp/role'
        f = open(temp_services_file, 'w')  
        f.write('coordinator')
        f.close()
        
        #(2) install amen in coordinator: mongodb 
        #based on
        #http://docs.mongodb.org/manual/tutorial/install-mongodb-on-red-hat-centos-or-fedora-linux/
        #last visit 5 March 2013
        #listen on 39167 port
        
        #subprocess.Popen(['sudo','cp',DEPLOYMENT_PATH+'/contrib/mongodb/mongod.conf','/etc/mongod.conf'], stdout=subprocess.PIPE, close_fds=True)
        #subprocess.Popen(['sudo','/sbin/chkconfig','mongod','on'], stdout=subprocess.PIPE, close_fds=True)
        #subprocess.Popen(['sudo','/sbin/service','mongod','start'], stdout=subprocess.PIPE, close_fds=True)    
    
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
        kernel.install_runnable_script('/yanoama/system/membership.py')
        install_cron_job("membership.py > /tmp/membership_output.log 2>&1")

        #(2) instal/run amen monitoring agent
        #default dir for storing objects/videos
        if os.path.exists(kernel.get_storage_path()):
            subprocess.Popen(['rm','-rf',kernel.get_storage_path()], stdout=subprocess.PIPE, close_fds=True)
        subprocess.Popen(['mkdir',kernel.get_storage_path()], stdout=subprocess.PIPE, close_fds=True)
        #install amen agent/deamon in this peer
        if not os.path.exists(kernel.get_amen_home()):
            subprocess.Popen(['sudo','mkdir',kernel.get_amen_home()],stdout=subprocess.PIPE, close_fds=True)
            subprocess.Popen(['sudo','mkdir',kernel.get_amen_home()+'/bin'],stdout=subprocess.PIPE, close_fds=True)
            subprocess.Popen(['sudo','touch',kernel.get_amen_home()+'/amend.log'],stdout=subprocess.PIPE, close_fds=True)
        subprocess.Popen(['sudo','cp',kernel.get_deployment_path()+'/contrib/amen/amend',kernel.get_amen_home()+'/bin/'],stdout=subprocess.PIPE, close_fds=True)
        #run daemon
        subprocess.Popen(['sudo','chmod','+x',kernel.get_amen_home()+'/bin/amend'],stdout=subprocess.PIPE, close_fds=True)
        subprocess.Popen(['sudo',kernel.get_amen_home()+'/bin/amend','start'],stdout=subprocess.PIPE, close_fds=True)
        #set role
        temp_services_file='/tmp/role'
        f = open(temp_services_file, 'w')  
        f.write('peer')
        f.close()
            
        print "outside"