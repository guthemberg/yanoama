####bootstrap script
#go to home
cd ~
#remove old installation
rm -rf yanoama
#requirement, start cron
sudo /sbin/service crond start
#cleanup user cron
crontab -r
#install git and json module
sudo yum -y -d0 -e0 --quiet install git-core python-simplejson
#download yanoama through git
git clone git://github.com/guthemberg/yanoama
cd yanoama
#for any update, run "git pull"
#copy the main script and conf file
#cp yanoama/monitoring/get_rtt.py ./
sudo cp config/yanoama.conf /etc/
#install script into the cron and copy get rtt script #cp yanoama/monitoring/get_rtt.py ./
python yanoama/system/install_cron.py
