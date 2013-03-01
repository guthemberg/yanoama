AMEN - adaptive monitoring for edge networks

Amen agent:
	#pre-install requirements
	sudo yum -y -d0 -e0 --quiet install git-core
    sudo yum -y -d0 -e0 --quiet install git-core
    cd /tmp && git clone git://github.com/mongodb/mongo-python-driver.git pymongo
    cd pymongo/
    sudo python setup.py install
    sudo yum -y -d0 -e0 --quiet install pytz gcc sysstat python-devel
	
	#copy and edit config
	sudo cp -s config/amen.conf /etc/ 
	#logs
	sudo mkdir /usr/local/amen
	sudo touch /usr/local/amen/amend.log
	#run daemon
	chmod +x ./contrib/amen/amend
	sudo contrib/amen/amend start
	

	
#files ok
#amen/amen/system/daemon.py
#amen/amen/core/settings.py
#amen/amen/defaults.py
#amen/amen/core/__init__.py
#amen/amen/system/runner.py
#amen/amen/backend/mongodb.py


#####Installing MongoDB
sudo mkdir /usr/local/mongodb /usr/local/mongodb/data /usr/local/mongodb/bin && sudo touch /var/log/mongodb.log
#[CHECK THE HOST ARCHITECTURE 32/64bits; here bellow we assume linux/fedora/32bits] 
cd /tmp http://fastdl.mongodb.org/linux/mongodb-linux-x8664-2.2.0.tgz && gzip -cd mongodb-linux-x86_64-2.2.0.tgz | tar xf - && sudo cp mongodb-linux-x86_64-2.2.0/bin/mongod /usr/local/mongodb/bin/
sudo cp amen/contrib/mongodb/rpm/mongodb /etc/init.d/
sudo chmod +x /etc/init.d/mongodb
sudo cp amen/contrib/mongodb/mongodb.conf /etc/ 
