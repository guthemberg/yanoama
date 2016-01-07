#!/bin/sh

install_cron_job ()
{
	script_name=$1
	new_job_file=$2
	crontab -l | grep -v "$script_name" > /tmp/current_crontab
	cat $new_job_file >> /tmp/current_crontab
	crontab /tmp/current_crontab 
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
			
	sudo yum --nogpgcheck -y -d0 -e0 --quiet install ant ant-nodeps ant-junit \
		ant-scripts ant-javadoc ant-trax gcc gcc-c++ valgrind ntp  git-core \
		git-all python-httplib2 python-setuptools python-devel ccache  \
		make automake pymongo bc screen apr apr-devel e2fsprogs-devel \
		expat expat-devel pcre-devel zlib-devel python-configobj
	cd
}

get_yanoama()
{
	home_dir=$1	
	if [ -d "$home_dir" ]; then
		cd $home_dir
		git pull
	else
		cd "$root_dir"
		git clone git://github.com/guthemberg/yanoama
	fi
}

#gen python file
generate_pythonrc()
{
	cd
	printf "# ~/.pythonrc\n# enable syntax completion\ntry:\n  import readline\nexcept ImportError:\n  print('Module readline not available.')\nelse:\n  import rlcompleter\n  readline.parse_and_bind('tab: complete')" |tee .pythonrc 
}

perform_common_settings()
{
		home_dir=$1
		#sudo update-rc.d cron defaults
		
		generate_pythonrc
		
		#enable cron
		sudo /sbin/service crond start
		sudo /sbin/chkconfig crond on
			
		crontab -l
		
		if [ $? -eq 0 ]
		then
			echo "user crontab is working."
		else
			if [ ! -e /etc/pam.d/crond.original ]
			then
				sudo cp /etc/pam.d/crond /etc/pam.d/crond.original
			fi
			
			sudo cp ${home_dir}/monitoring/rtt_matrix/pl_fedora/crond /etc/pam.d/crond
			sudo /sbin/service crond restart
			echo "user crontab was fixed."
		fi
				
}

#main

#this fetches informations about nodes that will
#compute the rtt matrix then setup each one of them
#this requires a key and a file /etc/ple.conf (ple
#credentials)


key=${HOME}/.ssh/id_rsa_cloud
yanoama_home_dir=/home/upmc_aren/yanoama
local_yanoama_home_dir=$yanoama_home_dir
ple_conf=/etc/ple.conf

if [ $HOME = '/home/upmc_aren' ]
then
	pwd
	# install_basic_packages_fedora
	#	get_yanoama $yanoama_home_dir
else
	local_yanoama_home_dir=${HOME}/git/yanoama	
fi

python ${local_yanoama_home_dir}/yanoama/monitoring/rtt_matrix/fetch_ple_info.py

exit 0


target=$1
cd

ssh -i $key -o StrictHostKeyChecking=no -o PasswordAuthentication=no -o ConnectTimeout=5 -o ServerAliveInterval=5 $target "pwd"
if [ $? -eq 0 ]
then
	install_basic_packages_fedora
	get_yanoama
	python ${yanoama_home_dir}/yanoama/monitoring/compute_rtt_matrix.py
	perform_common_settings "$yanoama_home_dir"
	install_cron_job "compute_rtt_matrix.py" "${yanoama_home_dir}/yanoama/monitoring/cron.job"
fi

echo "performing $vm..."
scp -i $RSA_KEY -o StrictHostKeyChecking=no ${setup_scritp_path}/setup.sh user@${vm}:/tmp/
scp -i $RSA_KEY -o StrictHostKeyChecking=no ${setup_scritp_path}/enac_setup_wrapper.sh  user@${vm}:/tmp/
ssh -i $RSA_KEY -o StrictHostKeyChecking=no user@${vm} "sh /tmp/enac_setup_wrapper.sh ${vm}"
echo "$vm done."


    key=${root_dir}/.ssh/id_rsa_cloud
    echo $target
    ssh -i $key -o StrictHostKeyChecking=no -o PasswordAuthentication=no -o ConnectTimeout=5 -o ServerAliveInterval=5 $target "pwd"

	if [ $? -eq 0 ]
	then
		ts=`date`
echo "[$ts]$peer_to_setup" >> /tmp/peers_to_setup_history.log
/bin/sh $home_dir/contrib/pl/setup.sh $peer_to_setup $workload_force_setup
#	target="workload_user@peer_to_setup"
#	checking_result=`ssh -i ${root_dir}/.ssh/id_rsa_cloud -o StrictHostKeyChecking=no -o PasswordAuthentication=no -o ConnectTimeout=60 -o ServerAliveInterval=60 $target sh /home/${workload_user}/tejo/tejo/common/experiments_scripts/peers/check_running_peer.sh`
#	if [ $? -eq 0 ]
#	then
#		python $home_dir/tejo/common/experiments_scripts/peers/setup_peers.py $peer_to_setup
exit 0
#	else
#		exit 1
#	fi
else
	python $home_dir/tejo/common/experiments_scripts/peers/setup_peers.py $peer_to_setup True
fi

