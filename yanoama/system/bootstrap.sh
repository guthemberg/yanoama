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
if [ `uname -m` == "x86_64" ]; then
  ##64 bits 
  sudo cp ${YANOAMA_HOME}/contrib/mongodb/fedora/10gen.repo.x86_64 /etc/yum.repos.d/10gen.repo
else 
  ##32 bits 
  sudo cp ${YANOAMA_HOME}/contrib/mongodb/fedora/10gen.repo.i686 /etc/yum.repos.d/10gen.repo
fi
sudo yum -y -d0 -e0 --quiet install git-core python-simplejson mongo-10gen mongo-10gen-server pytz gcc sysstat python-devel
CUR_DIR=`pwd`
cd /tmp
git clone git://github.com/mongodb/mongo-python-driver.git pymongo
cd pymongo
sudo python setup.py install
cd $CUR_DIR
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
#for any update, run "git pull"
#copy the main script and conf file
#cp yanoama/monitoring/get_rtt.py ./
#conf file installation must be the first
#action after fetching sources
sudo cp ${YANOAMA_HOME}/config/yanoama.conf /etc/
#install script into the cron and copy get rtt script #cp yanoama/monitoring/get_rtt.py ./
#similar to hosts
python ${YANOAMA_HOME}/yanoama/system/install_cron.py
python ${YANOAMA_HOME}/yanoama/system/install_hosts.py
#run pilot daemon
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
##installing/running amen, it requires mongodb
#installing requirement:monogodb
MONODB_HOME=/usr/local/mongodb
if [ ! -d "$MONODB_HOME" ]; then
  ##if mongodn dorectory does not exist build it
  sudo mkdir /usr/local/mongodb /usr/local/mongodb/data /usr/local/mongodb/bin && sudo touch /var/log/mongodb.log
fi
##checking architecture
CUR_DIR=`pwd`
if [ `uname -m` == "x86_64" ]; then
  ##64 bits 
  cd /tmp http://fastdl.mongodb.org/linux/mongodb-linux-x8664-2.2.0.tgz && gzip -cd mongodb-linux-x86_64-2.2.0.tgz | tar xf - && sudo cp mongodb-linux-x86_64-2.2.0/bin/mongod /usr/local/mongodb/bin/
else 
  ##32 bits 
  cd /tmp http://fastdl.mongodb.org/linux/mongodb-linux-x8664-2.2.0.tgz && gzip -cd mongodb-linux-x86_64-2.2.0.tgz | tar xf - && sudo cp mongodb-linux-x86_64-2.2.0/bin/mongod /usr/local/mongodb/bin/
fi
cd $CUR_DIR
#amen
##
echo "done."

