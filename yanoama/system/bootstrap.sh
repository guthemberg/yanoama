####bootstrap script

##overview
#1st: pre-install checkings
#2nd step: download and install yanoama

###1st step: pre-install checkings
##clean up, check/stop pilot,cron start,install git
#go to home
HOME=~
YANOAMA_HOME=${HOME}/yanoama
cd $HOME
#check if the system has required python version
#that means 2.6.x or higher
python_version_flag=`python -c 'import sys; print("%i" % (sys.hexversion<=0x02060000))'`
echo "python version check result: $python_version_flag"
#check if pilot is running and try to stop
if [ `pgrep -f pilotd|wc -l` -ge 1 ] && [ $python_version_flag -eq 0 ]; then
  chmod +x ${YANOAMA_HOME}/contrib/yanoama/pilotd
  sudo ${YANOAMA_HOME}/contrib/yanoama/pilotd stop
fi
#requirement, start cron
sudo /sbin/service crond start
#cleanup user cron
crontab -r
#install required packages
sudo yum --nogpgcheck -y -d0 -e0 --quiet install git-core 

###2nd step: check,download/update and (re)install yanoama
##check if yanoama is already installed
##if yes, update sources, otherwise,
##fetch sources from github, 
##then install conf files, 
##start pilot, and launch amen 
if [ -d $YANOAMA_HOME ]; then
  cd $YANOAMA_HOME
  git pull
  cd $HOME
else
  #remove old installation
  #rm -rf $YANOAMA_HOME
  git clone git://github.com/guthemberg/yanoama
fi

##install required packages (in three parts: a,b,c)
#(a)MONGO DB
#http://docs.mongodb.org/manual/tutorial/install-mongodb-on-red-hat-centos-or-fedora-linux/
#last visit 5 March 2013
if [ `uname -m` == "x86_64" ]; then
  ##64 bits 
  sudo cp ${YANOAMA_HOME}/contrib/mongodb/fedora/10gen.repo.x86_64 /etc/yum.repos.d/10gen.repo
else 
  ##32 bits 
  sudo cp ${YANOAMA_HOME}/contrib/mongodb/fedora/10gen.repo.i686 /etc/yum.repos.d/10gen.repo
fi
#(b) other packages
sudo yum --nogpgcheck -y -d0 -e0 --quiet install git-core python-simplejson mongo-10gen mongo-10gen-server pytz gcc sysstat python-devel
#(c) pymongo
CUR_DIR=`pwd`
cd /tmp
git clone git://github.com/mongodb/mongo-python-driver.git pymongo
cd pymongo
sudo python setup.py install
cd $CUR_DIR

#for any update, run "git pull"
#copy the main script and conf file
#cp yanoama/monitoring/get_rtt.py ./
#conf file installation must be the first
#action after fetching sources
sudo cp ${YANOAMA_HOME}/config/yanoama.conf /etc/
#deployment of yanoama system  
#based on nodes role:
#(a) coordinator: get_rtt (cron), peering (cron), 
#                 mongodb
#       
#(b) peer:        membership(cron), amen(agent as
#                 a daemon)  
echo -n "Installing role..."    
python ${YANOAMA_HOME}/yanoama/system/install_role.py
#updatting /etc/services
if [ ! -e "/etc/services.origin" ]; then
  sudo cp /etc/services /etc/services.origin 
fi
if [ -e "/tmp/services" ]; then
  cat /etc/services.origin /tmp/services > /tmp/services.1
  sudo cp /tmp/services.1 /etc/services
  rm -rf /tmp/services /tmp/services.1
fi
#updating role
ROLE_FILE="/tmp/role"
if [ -e "$ROLE_FILE" ]; then
  if [ `cat $ROLE_FILE` = "coordinator" ]; then
	  sudo cp ${YANOAMA_HOME}/contrib/mongodb/mongod.conf /etc/mongod.conf
	  sudo /sbin/chkconfig mongod on
    if [ `pgrep -f mongod|wc -l` -ge 1 ]; then
	    sudo /sbin/service mongod restart
    else
	    sudo /sbin/service mongod start
    fi
  fi
  sudo cp $ROLE_FILE /etc/
  rm $ROLE_FILE
fi
echo " done."    

#run pilot daemon for all nodes (peers and coordinators)
chmod +x ${YANOAMA_HOME}/contrib/yanoama/pilotd
log_dir=/usr/local/yanoama
if [ ! -d "$log_dir" ]; then
  sudo mkdir $log_dir
  sudo touch ${log_dir}/pilot.log
  sudo ${YANOAMA_HOME}/contrib/yanoama/pilotd start
elif [ $python_version_flag -eq 0 ]; then
  #if there is python right version
  echo "running the server."
  sudo ${YANOAMA_HOME}/contrib/yanoama/pilotd start
elif [ $python_version_flag -eq 1 ]; then
  #wait 2 minutes before restart (for cleaning up connection stalled connections)
  echo -n "sleeping (2min)... "
  if [ `pgrep -f pilotd|wc -l` -ge 1 ]; then
    sudo ${YANOAMA_HOME}/contrib/yanoama/pilotd stop
  fi
  sleep 120
  echo "get up."
  sudo ${YANOAMA_HOME}/contrib/yanoama/pilotd start
fi
echo "done."

