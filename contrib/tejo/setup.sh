#!/bin/sh

install_cron_job ()
{
	script_name=$1
	new_job_file=$2
	crontab -l | grep -v "$script_name" > /tmp/current_crontab
	cat $new_job_file >> /tmp/current_crontab
	crontab /tmp/current_crontab 
}

get_root_dir()
{
	root_dir="$HOME"
#	if [ -e /etc/tejo.conf ]
#	then
#		root_dir=`grep root_dir /etc/tejo.conf |cut -f2 -d=`
#		if [ `expr length $root_dir` -eq 0 ]
#		then
#			root_dir="$HOME"
#		fi
#	fi
	printf "$root_dir"
}

get_tejo()
{
	root_dir=`get_root_dir`
	home_dir=${root_dir}/tejo	
	if [ -d "$home_dir" ]; then
		cd $home_dir
		git pull
	else
		cd "$root_dir"
		git clone git://github.com/guthemberg/tejo
	fi
}

get_yanoama()
{
	root_dir=`get_root_dir`
	home_dir=${root_dir}/yanoama	
	if [ -d "$home_dir" ]; then
		cd $home_dir
		git pull
	else
		cd "$root_dir"
		git clone git://github.com/guthemberg/yanoama
	fi
}

get_parameter()
{
	parameter=""
	if [ ! -e /etc/tejo.conf ]
	then
		get_tejo
		root_dir="`get_root_dir`"
		parameter=`grep "$1" "$root_dir"/tejo/contrib/tejo/tejo.conf.sample |cut -f2 -d=`
	else
		parameter=`grep "$1" /etc/tejo.conf |cut -f2 -d=`
	fi
	printf "$parameter"


}

get_home_dir()
{
	printf "${HOME}/tejo"
}



#gen python file
generate_pythonrc()
{
	cd `get_root_dir`
	printf "# ~/.pythonrc\n# enable syntax completion\ntry:\n  import readline\nexcept ImportError:\n  print('Module readline not available.')\nelse:\n  import rlcompleter\n  readline.parse_and_bind('tab: complete')" |tee .pythonrc 
}

install_basic_packages_fedora()
{
	sudo yum update
	if [ "$?" -eq 1 ]
	then
		sudo sed -i 's/https/http/g' /etc/yum.repos.d/*
		sudo yum update
	fi
	
	cd /tmp
	#rm -rf jre-7u75-linux-i586.rpm* jdk-7u75-linux-i586.rpm*
	if [ ! -e /tmp/jre-7u75-linux-i586.rpm ]
	then
		wget --no-check-certificate http://eu-monitor-001.cloudapp.net/jre-7u75-linux-i586.rpm -O /tmp/jre-7u75-linux-i586.rpm		
	fi
#	if [ ! -e /tmp/jdk-7u75-linux-i586.rpm ]
#	then
#		wget --no-check-certificate http://eu-monitor-001.cloudapp.net/jdk-7u75-linux-i586.rpm -O /tmp/jdk-7u75-linux-i586.rpm
#	fi
	sudo rpm -Uvh /tmp/jre-7u75-linux-i586.rpm
	#sudo rpm -Uvh /tmp/jdk-7u75-linux-i586.rpm
			
	sudo yum --nogpgcheck -y -d0 -e0 --quiet install ant ant-nodeps ant-junit \
		ant-scripts ant-javadoc ant-trax gcc gcc-c++ valgrind ntp  git-core \
		git-all python-httplib2 python-setuptools python-devel ccache  \
		make automake pymongo bc screen apr apr-devel e2fsprogs-devel \
		expat expat-devel pcre-devel zlib-devel python-configobj
	#select the right java version 1.7
	sudo alternatives --install /usr/bin/java java /usr/java/jre1.7.0_75/bin/java 200000
	sudo alternatives --install /usr/bin/javaws javaws /usr/java/jre1.7.0_75/bin/javaws 200000
	#sudo alternatives --install /usr/bin/javac javac /usr/java/jdk1.7.0_75/bin/javac 200000
	cd
}
	
#install_java_fedora()
#{
	#	cd /tmp
	#	rm -rf jre-7u75-linux-i586.rpm* jdk-7u75-linux-i586.rpm*
	#	wget http://homepages.laas.fr/gdasilva/jre-7u75-linux-i586.rpm
	#	wget http://homepages.laas.fr/gdasilva/jdk-7u75-linux-i586.rpm
#	sudo rpm -Uvh /home/upmc_aren/tejo/contrib/java/jre-7u75-linux-i586.rpm
#	sudo rpm -Uvh /home/upmc_aren/tejo/contrib/java/jdk-7u75-linux-i586.rpm
#	sudo alternatives --install /usr/bin/java java /usr/java/jre1.7.0_75/bin/java 200000
#	sudo alternatives --install /usr/bin/javaws javaws /usr/java/jre1.7.0_75/bin/javaws 200000
#	sudo alternatives --install /usr/bin/javac javac /usr/java/jdk1.7.0_75/bin/javac 200000
#}

perform_common_settings()
{

		host_location=$1
		domain=$2
		node_type=$3
		qrouter=$4
		module=$5

		get_tejo
		
		root_dir=`get_root_dir`
		home_dir="$root_dir/${module}"
		moimeme=`whoami`
		sed "s|LOCATION|$host_location|g" ${home_dir}/contrib/tejo/tejo.conf.sample|sed "s|USER|${moimeme}|g"|sed "s|MY_DOMAIN|$domain|g"|sed "s|TYPE|$node_type|g"|sed "s|QROUTER|$qrouter|g"|sed "s|WL_TARGET|$qrouter|g" > /tmp/tejo.conf
		sudo mv /tmp/tejo.conf /etc/
			
		
		if [ ! -e ${root_dir}/.bashrc.original ]
		then
			cp ${root_dir}/.bashrc ${root_dir}/.bashrc.original
		fi
		cp ${home_dir}/contrib/fedora/os/bashrc ${root_dir}/.bashrc
		
		#sudo update-rc.d cron defaults
		
		generate_pythonrc
		
		#enable cron
		sudo /sbin/service crond start
		sudo /sbin/chkconfig crond on
				
}

install_confuse()
{
	cur_dir=`pwd`
	cd /tmp
	home_dir="`get_home_dir`"
	cp ${home_dir}/contrib/fedora/confuse/confuse-2.7.tar.gz ./
	tar xzf confuse-2.7.tar.gz
	cd confuse-2.7
	sudo ./configure --enable-shared
	sudo make
	sudo make install
	cd /tmp
	sudo rm -rf confuse-2.7*
	sudo cp /contrib/fedora/os/etc/ld.so.conf /etc/ld.so.conf
	sudo /sbin/ldconfig
	cd $cur_dir
}

install_gmond_from_sources()
{
	cur_dir=`pwd`
	cd /tmp
	home_dir="`get_home_dir`"
	cp ${home_dir}/contrib/fedora/ganglia/ganglia-3.7.1.tar.gz ./
	tar -xzf ganglia-3.7.1.tar.gz
	cd ganglia-3.7.1
	./configure
	make
	sudo make install
	cd /tmp
	sudo rm -rf ganglia-3.7.1*
	cd $cur_dir
	
}

#this function assumes that
#sources are VMs
#target is monitor
install_ganglia_monitor()
{

	
	location=$1
	node_type=$2
	aggregator=$3
	
	
	#install ganglia and get tejo
	#this allows to install required packages 
	sudo yum --nogpgcheck -y -d0 -e0 --quiet install ganglia-gmond ganglia-gmond-python ganglia-devel
	get_tejo
	
	home_dir="`get_home_dir`"
	gmond_conf_dir=""
	dst_conf_file="/etc/ganglia/gmond.conf"
	if [ `rpm -qa|grep ganglia-gmond-python|wc -l` -eq 1 ]
	then
		sudo /sbin/service gmond restart
		if [ ! -e /etc/ganglia/gmond.conf.original ]
		then
			sudo cp /etc/ganglia/gmond.conf /etc/ganglia/gmond.conf.original
		fi
		gmond_conf_dir=`/usr/sbin/gmond -t|grep conf.d|cut -f2 -d\'|cut -f1-4 -d/`
		if [ ! -d "$gmond_conf_dir" ]
		then
			gmond_conf_dir=`/usr/sbin/gmond -t|grep conf.d|cut -f2 -d\"|cut -f1-4 -d/`
		fi
		cp ${home_dir}/contrib/fedora/ganglia/gmond.conf.sample /tmp/gmond.conf.1

	else
		sudo /sbin/service gmond stop
		sudo yum --nogpgcheck -y -d0 -e0 --quiet remove ganglia-gmond ganglia-gmond-python ganglia-devel
		install_confuse
		install_gmond_from_sources
		if [ ! -e /usr/local/etc/gmond.conf ]
		then
			sudo su -c "/usr/local/sbin/gmond -t > /usr/local/etc/gmond.conf"
		fi
		if [ ! -e /usr/local/etc/gmond.conf.original ]
		then
			sudo cp /usr/local/etc/gmond.conf /usr/local/etc/gmond.conf.original
		fi
		sudo cp ${home_dir}/contrib/fedora/ganglia/init.d/gmond /etc/init.d/
		sudo chmod guo+x /etc/init.d/gmond
		#sudo update-rc.d gmond defaults
		sudo /sbin/service gmond restart
		gmond_conf_dir=`/usr/local/sbin/gmond -t|grep conf.d|cut -f2 -d\"|cut -f1-5 -d/`
		dst_conf_file="/usr/local/etc/gmond.conf"
		python_modules_dir=`grep python_modules ${gmond_conf_dir}/modpython.conf|cut -f2 -d=|sed "s|\"||g"`
		if [ ! -e $python_modules_dir ]
		then
			sudo mkdir -p $python_modules_dir
		fi
		sed "s|etc\/ganglia|usr\/local\/etc|g" ${home_dir}/contrib/fedora/ganglia/gmond.conf.sample > /tmp/gmond.conf.1
	fi

#	echo 'deb http://ftp.univ-pau.fr/linux/mirrors/debian/ wheezy main'| sudo tee /etc/apt/sources.list.d/ganglia.list
#	sudo gpg --keyserver pgpkeys.mit.edu --recv-key  8B48AD6246925553
#	sudo gpg --keyserver pgpkeys.mit.edu --recv-key  6FB2A1C265FFB764
#	sudo gpg -a --export 6FB2A1C265FFB764 | sudo apt-key add -
#	sudo gpg -a --export 8B48AD6246925553 | sudo apt-key add -
#	sudo apt-get -q -y update
#	sudo DEBIAN_FRONTEND=noninteractive apt-get -q -y install ganglia-modules-linux ganglia-monitor ganglia-monitor-python
#	if [ -e /etc/ganglia/conf.d/diskusage.pyconf ]
#	then
#		sudo mv /etc/ganglia/conf.d/diskusage.pyconf /etc/ganglia/conf.d/diskusage.pyconf.disabled
#	fi	
	#	sudo service ganglia-monitor restart
	#	sudo rm /etc/apt/sources.list.d/ganglia.list
	#	sudo apt-get -q -y update
		
#	if [ -e /etc/ganglia/conf.d/tcpconn.pyconf.disabled ]
#	then
#		sudo mv /etc/ganglia/conf.d/tcpconn.pyconf.disabled /etc/ganglia/conf.d/tcpconn.pyconf
#	fi
		


		
	case "$node_type" in
		"vm")
			source="VMs"
			gmond_port="`get_parameter default_gmond_port`"
			sed "s|LOCATION|$location|g" ${home_dir}/contrib/fedora/ganglia/gmond.conf.sample | sed "s|SOURCE|$source|g" | sed "s|PORT|$gmond_port|g" | sed "s|TARGET|$aggregator|g" > /tmp/gmond.conf
						
			sudo cp ${home_dir}/contrib/fedora/ganglia/vm/*.pyconf ${gmond_conf_dir}/
			sudo cp ${home_dir}/contrib/fedora/ganglia/vm/*.py `grep python_modules ${gmond_conf_dir}/modpython.conf|cut -f2 -d=|sed "s|\"||g"`/
	
						
			;;
			
		*)
			source="workload"
			gmond_port=`get_parameter wl_gmond_port`
			sed "s|LOCATION|$location|g" /tmp/gmond.conf.1 | sed "s|SOURCE|$source|g" | sed "s|PORT|$gmond_port|g" | sed "s|TARGET|$aggregator|g" > /tmp/gmond.conf
			sudo cp ${home_dir}/contrib/fedora/ganglia/wl/*.pyconf ${gmond_conf_dir}/
			sudo cp ${home_dir}/contrib/fedora/ganglia/wl/*.py `grep python_modules ${gmond_conf_dir}/modpython.conf|cut -f2 -d=|sed "s|\"||g"`/
			;;
		
	esac

	sudo mv /tmp/gmond.conf $dst_conf_file
				
	#enabled by default	
	#sudo update-rc.d ganglia-monitor defaults
	
	sudo /sbin/chkconfig gmond on
	
	sudo /sbin/service gmond restart
}

install_workload_cron()
{
	get_tejo
	
	home_dir="`get_home_dir`"
	install_cron_job "/tmp/experiment_outputs/" "${home_dir}/contrib/fedora/mongodb/cron.job"
	install_cron_job "pkill -f ycsb-0.1.4" "${home_dir}/contrib/fedora/mongodb/cron.job.2"
	
	#	min=`shuf -i 0-59 -n 1`
	#	hour=`shuf -i 0-23 -n 1`
	#	sed "s|HOMEDIR|$location|g" ${home_dir}/tejo/common/experiments_scripts/peers/cron.job|sed "s|HOUR|$hour|g"|sed "s|MIN|$min|g" > /tmp/cron.job
	min=`shuf -i 0-59 -n 1`
	sed "s|HOMEDIR|$home_dir|g" ${home_dir}/tejo/common/monitoring/cron.job|sed "s|MIN|$min|g" > /tmp/cron.job
	install_cron_job "wlrtt.py" "/tmp/cron.job"
	
	sed "s|HOMEDIR|$home_dir|g" "${home_dir}/contrib/pl/cron.job"|sed "s|HOMEDIR|$home_dir|g" > /tmp/cron.job
	install_cron_job "peering_wrapper.sh" "/tmp/cron.job"

	sed "s|HOMEDIR|$home_dir|g" "${home_dir}/contrib/pl/croncheck.job" > /tmp/cron.job
	install_cron_job "check_workload.sh" "/tmp/cron.job"
	
	sed "s|HOMEDIR|$home_dir|g" "${home_dir}/contrib/pl/cronchecklatency.job" > /tmp/cron.job
	install_cron_job "check_latency.py" "/tmp/cron.job"
		
}

install_paping ()
{

	CUR_DIR=`pwd`
	cd /tmp

	home_dir="`get_home_dir`"
		
	dist_vesion="linux_x86"
	dist_file="paping_1.5.5_x86_linux.tar.gz"
	if [ "`uname -m`" = "x86_64" ]; then
		dist_vesion="linux_x86-64"
		dist_file="paping_1.5.5_x86-64_linux.tar.gz"
	fi

	cp ${home_dir}/contrib/paping/${dist_vesion}/${dist_file} ./
	tar xzf ${dist_file}
	chmod guo+x paping
	sudo mv paping /bin/
		
			
	cd $CUR_DIR

}

handle_script_inputs ()
{
#	##nice dynamic loop
#	get_list () 
#	{
#	        printf "bola gato mesa"
#	}
#	
#	index=1
#	par_1="teste"
#	for element in `get_list`
#	do
#	        eval "par_`printf ${index}`=$element"
#	        index=`expr $index + 1`
#	done
#	
#	echo "param1: $par_1 , param2: $par_2 , param3: $par_3"
#	
#	exit 1
	
	node_type=""
	aggregator=""
	default_domain=""
	node_location=""
	force_setup="no"
	

	case $# in
		8) 
			option=""
			for parameter in $*
			do
				case "$parameter" in
					"-l")
						option="l"	
						;;
					"-d")
						option="d"	
						;;
					"-t")
						option="t"	
						;;
					"-a")
						option="a"	
						;;
					*)
						case "$option" in
							"l")
								node_location=$parameter
								;;
								
							"d")
								default_domain=$parameter
								;;
								
							"t")
								node_type=$parameter
								;;
								
							"a")
								aggregator=$parameter
								;;
								
																																																																
								
						esac
						;;
				esac
			done
			
			if [ `expr length $node_type` -eq 0 -o `expr length $aggregator` -eq 0 -o `expr length $default_domain` -eq 0 -o `expr length $node_location` -eq 0 ]
			then
				exit 1
			fi
			
			;;


		10) 
			option=""
			for parameter in $*
			do
				case "$parameter" in
					"-l")
						option="l"	
						;;
					"-d")
						option="d"	
						;;
					"-t")
						option="t"	
						;;
					"-a")
						option="a"	
						;;
					"-f")
						option="f"	
						;;
					*)
						case "$option" in
							"l")
								node_location=$parameter
								;;
								
							"d")
								default_domain=$parameter
								;;
								
							"t")
								node_type=$parameter
								;;
								
							"a")
								aggregator=$parameter
								;;
								
							"f")
								force_setup=$parameter
								;;
								
																																																																																																																																
								
						esac
						;;
				esac
			done
			
			if [ `expr length $node_type` -eq 0 -o `expr length $aggregator` -eq 0 -o `expr length $default_domain` -eq 0 -o `expr length $node_location` -eq 0 ]
			then
				exit 1
			fi
			
			;;


		6) 
			option=""
			for parameter in $*
			do
				case "$parameter" in
					"-l")
						option="l"	
						;;
					"-d")
						option="d"	
						;;
					"-t")
						option="t"	
						;;
					*)
						case "$option" in
							"l")
								node_location=$parameter
								;;
								
							"d")
								default_domain=$parameter
								;;
								
							"t")
								node_type=$parameter
								;;								
						esac
						;;
				esac
			done
			
			aggregator="non_applicable"
			
			if [ `expr length $node_type` -eq 0 -o `expr length $default_domain` -eq 0 -o `expr length $node_location` -eq 0 ]
			then
				exit 1
			fi
			
			;;
			
						
		*) 
		exit 1
		;;
	esac

	printf "$node_type $aggregator $default_domain $node_location $force_setup"
	
}

###main

node_type=""
aggregator=""
default_domain=""
node_location=""
force_setup="no"

parameters="`handle_script_inputs $*`"
if [ ! "$?" -eq 0 ]
then
	printf "unexpected inputs, try: sh setup.sh { -l location -d default_domain -t { { vm -a aggregator_server } | { workload -a aggregator_server } | monitor } [ -f {yes|no}] }\n"
	exit 1
fi


index=1
for parameter in `printf "$parameters"`
do
	case $index in
		1)
			node_type=$parameter
			;;
		2)
			aggregator=$parameter
			;;
		3)
			default_domain=$parameter
			;;
		4)
			node_location=$parameter
			;;
		5)
			force_setup=$parameter
			;;
	esac
	index=`expr $index + 1` 
done

echo "list of parameters:"
echo "node_type:$node_type"
echo "aggregator:$aggregator"
echo "default_domain:$default_domain"
echo "node_location:$node_location"
echo "force_setup:$force_setup"

## check if the node has already been installed
if [ "$force_setup" = "no" ]
then
	if [ -e `get_home_dir` ]
	then
		cd `get_home_dir`
		git pull
		printf "peer is running: "
		sh `get_home_dir`/tejo/common/experiments_scripts/peers/check_running_peer.sh
		if [ $? -eq 0 ]
		then
			echo "KO, nothing to do do (if you may want to force a setup, try -f yes param), bye."
			exit 0
		else
			echo "OK."
		fi

	#checking if node id dead
		if [ -e /etc/tejo.conf ]
		then
			workload_death_file=`grep workload_death_file /etc/tejo.conf|cut -d= -f2`
			if [ -e $workload_death_file ]
			then
				printf "check peer liveness: "
		        state=`python -c "import pickle;import sys ; sys.stdout.write(str(pickle.load( open( '$workload_death_file', 'rb' ) )))"`
		        if [ $? -eq 0 ]
		        then
			        if [ $state = "True" ]
			        then
			        	sh `get_home_dir`/tejo/common/experiments_scripts/ycsb/stop.sh
						echo "KO, peer is dead (if you may want to force a setup, try -f yes param), bye."
						exit 0
					else
						echo "OK."
					fi		        	
		        fi
			fi
			
			
			
		fi
	fi
else
		echo "forcing peer installation." 
fi

rm /tmp/*.pck
rm /home/`whoami`/*.pck

echo -n "(0) installing basic packages..."
install_basic_packages_fedora
get_tejo
get_yanoama
install_paping
#get_tejo
#install_java_fedora
echo " (0) done."


echo -n "(1) common setup..."
perform_common_settings "$node_location" "$default_domain" "$node_type" "$aggregator" "tejo"
echo " (1) done."


case "$node_type" in
        "vm")
				echo -n "(2) installing dummynet..."
                install_dummynet
				echo " (2) done."
				#echo -n "(3) installing mongodb..."
                #install_mongodb
				#echo " (3) done."
				echo -n "(3) installing ganglia for vms..."
                install_ganglia_monitor "$node_location" "$node_type" "$aggregator"
				echo " (3) done."
                ;;
        "monitor")
				echo -n "(2) installing postgres..."
        		install_postgres
				echo " (2) done."
				echo -n "(3) installing ganglia for monitor..."
                install_ganglia_aggregator "$node_location"
                install_ganglia_poller_web
				echo " (3) done."
                ;;
        "workload")
				echo -n "(2) installing ganglia for workload..."
                install_ganglia_monitor "$node_location" "$node_type" "$aggregator"
                install_workload_cron
                #getting rtt once
				python `get_home_dir`/tejo/common/monitoring/wlrtt.py
				sh `get_home_dir`/tejo/common/experiments_scripts/ycsb/stop.sh
                touch `get_parameter mongo_active_wl_file`
				echo " (2) done."
                ;;
        *)
                echo 'unkown host type'
                echo "$node_type"
                ;;
esac
		
exit 0	
#end main



