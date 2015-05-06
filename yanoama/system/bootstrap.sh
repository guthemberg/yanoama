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
#that means 2.7.x or higher
python_version_flag=`python -c 'import sys; print("%i" % (sys.hexversion<=0x02070000))'`

echo "python version check result: $python_version_flag"

# if version is lower, upgrade it
#requirements
sudo yum --nogpgcheck -y -d0 -e0 --quiet groupinstall "Development tools"
sudo yum --nogpgcheck -y -d0 -e0 --quiet install zlib-devel nc bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel

#1 means python older than 2.7, so upgrade is required
if [ [ $python_version_flag -eq 1 ]; then
	CUR_DIR=`pwd`
	cd /tmp
	if [ ! -e "/etc/ld.so.conf.origin" ]; then
	  sudo cp /etc/ld.so.conf /etc/ld.so.conf.origin 
	fi
	sudo su -c 'cp /etc/ld.so.conf.origin /etc/ld.so.conf'
	sudo su -c "echo '/usr/local/lib' >> /etc/ld.so.conf"
	wget https://www.python.org/ftp/python/2.7.8/Python-2.7.8.tgz
	tar xf Python-2.7.8.tgz
	cd Python-2.7.8
	./configure --prefix=/usr/local --enable-unicode=ucs4 --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib"
	cd /tmp
	wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py
	sudo su -c '/usr/local/bin/python2.7 ez_setup.py'
	sudo easy_install-2.7 pip
	sudo pip2.7 install virtualenv
#sudo easy_install pip
#cd /tmp
#git clone git://github.com/mongodb/mongo-python-driver.git pymongo
#cd pymongo
#sudo python setup.py install
	cd $CUR_DIR
#activating python 2.7
	virtualenv --python=python2.7 ~/python_env
	source ~/python_env/bin/activate
else
	mkdir -p ~/python_env/bin/
	ln -s /usr/bin/python ~/python_env/bin/
	ln -s /usr/bin/pip ~/python_env/bin/
fi

#check if pilot is running and try to stop
if [ `pgrep -f pilotd|wc -l` -ge 1 ] && [ $python_version_flag -eq 0 ]; then
  chmod +x ${YANOAMA_HOME}/contrib/yanoama/pilotd
  sudo ${YANOAMA_HOME}/contrib/yanoama/pilotd stop
fi
#requirement, start cron
sudo /sbin/service crond start
sudo /sbin/chkconfig crond on
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
#last visit 29 June 2014
if [ `uname -m` == "x86_64" ]; then
  ##64 bits 
sudo cp ${YANOAMA_HOME}/contrib/mongodb/fedora/mongodb.repo.x86_64 /etc/yum.repos.d/mongodb.repo
else 
  ##32 bits 
sudo cp ${YANOAMA_HOME}/contrib/mongodb/fedora/mongodb.repo.i686 /etc/yum.repos.d/mongodb.repo
fi
#(b) other packages
sudo yum --nogpgcheck -y -d0 -e0 --quiet install git-core python-simplejson mongodb-org mongodb-org-server pytz gcc sysstat python-devel
	
#(c) pymongo
echo -n 'working versions:'
pip --version
python --version

sudo ~/python_env/bin/pip install pymongo
sudo ~/python_env/bin/pip install simple_json
sudo ~/python_env/bin/pip install configobj

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
	#setup mongodb
	##saving /etc/mongod.conf
	if [ ! -e "/etc/mongod.conf.orig" ]; then
		sudo cp /etc/mongod.conf /etc/mongod.conf.orig
	fi
	##change bind ip
	MYIP=$(grep `hostname` /etc/hosts|cut -d' ' -f1)
	MYPORT=`python /home/upmc_aren/yanoama/yanoama/system/get_conf_info.py db_port`
	sudo sed -i "s/^\(bind_ip\s*=\s*\).*\$/\1$MYIP/" /etc/mongod.conf
	## uncomment a line
	sudo sed -i "s,#\(port=27017\),\1,g" /etc/mongod.conf
	sudo sed -i "s/^\(port\s*=\s*\).*\$/\1$MYPORT/" /etc/mongod.conf
	#	  sudo cp ${YANOAMA_HOME}/contrib/mongodb/mongod.conf /etc/mongod.conf
	sudo /sbin/chkconfig mongod on
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

