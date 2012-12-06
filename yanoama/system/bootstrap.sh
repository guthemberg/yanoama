####bootstrap script
#go to home
HOME=~
YANOAMA_HOME=${HOME}/yanoama
cd $HOME
#check if the system has required python version
#that means 2.6.x or higher
python_version_flag=`python -c 'import sys; print("%i" % (sys.hexversion<=0x02060000))'`
#check if pilot is running and try to stop
if [ `pgrep -f pilotd|wc -l` -ge 1 ] && [ $python_version_flag -eq 0 ]; then
  sudo ${YANOAMA_HOME}/contrib/yanoama/pilotd stop
fi
#remove old installation
rm -rf $YANOAMA_HOME
#requirement, start cron
sudo /sbin/service crond start
#cleanup user cron
crontab -r
#install git and json module
sudo yum -y -d0 -e0 --quiet install git-core python-simplejson
#download yanoama through git
git clone git://github.com/guthemberg/yanoama
#for any update, run "git pull"
#copy the main script and conf file
#cp yanoama/monitoring/get_rtt.py ./
sudo cp ${YANOAMA_HOME}/config/yanoama.conf /etc/
#install script into the cron and copy get rtt script #cp yanoama/monitoring/get_rtt.py ./
#similar to hosts
python ${YANOAMA_HOME}/yanoama/system/install_cron.py
python ${YANOAMA_HOME}/yanoama/system/install_hosts.py
#run pilot daemon
if [ ! -d "$DIRECTORY" ]; then
  sudo mkdir /usr/local/yanoama
  sudo touch /usr/local/yanoama/pilot.log
  chmod +x ${YANOAMA_HOME}/contrib/yanoama/pilotd
  sudo ${YANOAMA_HOME}/contrib/yanoama/pilotd start
elif [ $python_version_flag -eq 0 ]; then
  #if there is python right version
  chmod +x ${YANOAMA_HOME}/contrib/yanoama/pilotd
  sudo ${YANOAMA_HOME}/contrib/yanoama/pilotd start
elif [ $python_version_flag -eq 1 ]; then
  #wait 2 minutes before restart (for cleaning up connection stalled connections)
  sleep 120
  chmod +x ${YANOAMA_HOME}/contrib/yanoama/pilotd
  sudo ${YANOAMA_HOME}/contrib/yanoama/pilotd start
fi

