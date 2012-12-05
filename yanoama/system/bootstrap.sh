####bootstrap script
#go to home
HOME=~
YANOAMA_HOME=${HOME}/yanoama
cd $HOME
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
python ${YANOAMA_HOME}/yanoama/system/install_cron.py
#run pilot daemon
sudo mkdir /usr/local/yanoama
sudo touch /usr/local/yanoama/pilot.log
chmod +x ${YANOAMA_HOME}/contrib/yanoama/pilotd
sudo pkill -f pilotd && sudo rm -rf /var/run/pilotd.pid
sudo ${YANOAMA_HOME}/contrib/yanoama/pilotd start

