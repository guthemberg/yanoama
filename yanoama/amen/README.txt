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
##follow the online tutorial in
#http://docs.mongodb.org/manual/tutorial/install-mongodb-on-red-hat-centos-or-fedora-linux/
##legacy way to install (almost manually)
sudo mkdir /usr/local/mongodb /usr/local/mongodb/data /usr/local/mongodb/bin && sudo touch /var/log/mongodb.log
#[CHECK THE HOST ARCHITECTURE 32/64bits; here bellow we assume linux/fedora/32bits] 
cd /tmp http://fastdl.mongodb.org/linux/mongodb-linux-x8664-2.2.0.tgz && gzip -cd mongodb-linux-x86_64-2.2.0.tgz | tar xf - && sudo cp mongodb-linux-x86_64-2.2.0/bin/mongod /usr/local/mongodb/bin/
sudo cp amen/contrib/mongodb/rpm/mongodb /etc/init.d/
sudo chmod +x /etc/init.d/mongodb
sudo cp amen/contrib/mongodb/mongodb.conf /etc/ 


##simple tutorial for pymongo

#INSERTING COLLECTIONS
import pymongo
from pymongo import Connection
connection = Connection('planetlab01.alucloud.com', 39167)
db = connection['amen']
tests=db.tests
tests.insert({'key':'value'})
tests.insert({'bola':'gato'})
print 'done.'

#READING
import pymongo
from pymongo import Connection
connection = Connection('planetlab01.alucloud.com', 39167)
db = connection['amen']
print db['tests'].find_one()
for obj in db['tests'].find({}, {'_id': False}):
        for key in obj.keys():
                print key
print 'done.'

#DROP/DELETE/REMOVE
import pymongo
from pymongo import Connection
connection = Connection('planetlab01.alucloud.com', 39167)
db = connection['amen']
tests=db['tests']
tests.drop()
print 'done.'

##further references
#http://api.mongodb.org/python/2.0/tutorial.html
#http://stackoverflow.com/questions/3895572/pymongo-pythonmongodb-drop-collection-gridfs
#http://stackoverflow.com/questions/12345387/removing-id-element-from-pymongo-results-python-mongodb-flask