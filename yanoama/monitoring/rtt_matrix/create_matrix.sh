#!/bin/sh

workdir=$1
script_dir=$2
key=${HOME}/.ssh/id_rsa_cloud
myuser='upmc_aren'

list_of_node=`printf "import pickle,sys\nfor node in pickle.load( open( \"${workdir}/host_table.pck\", \"rb\" ) ): sys.stdout.write(node+\" \")"|python`


#downloading files
ssh_test_parameters="-o ConnectTimeout=10 -o ServerAliveInterval=10"
ssh_credentials="-i $key -o StrictHostKeyChecking=no -o PasswordAuthentication=no"
measurements_dir=${workdir}/measurements
existing_nodes=""
total_number_of_existing_nodes=0
mkdir -p $measurements_dir 
for node in `printf "$list_of_node"`
do
	target="${myuser}@${node}"
	ssh $ssh_credentials $ssh_test_parameters $target hostname
	if [ $? -eq 0 ]
	then
		measurements_file=/home/${myuser}/${node}_rtt_matrix.pck
		scp $ssh_credentials ${target}:$measurements_file ${measurements_dir}/
		number_of_nodes=`printf "import pickle,sys\nsys.stdout.write(str(len(pickle.load( open( \"${measurements_dir}/${node}_rtt_matrix.pck\", \"rb\" )))))"|python`
		if [ $number_of_nodes -gt 0 ]
		then
			existing_nodes="$existing_nodes $node"
			total_number_of_existing_nodes=`expr $total_number_of_existing_nodes + 1`
		fi
			
	fi
		
done

ls ${measurements_dir}/ |wc -l
echo $total_number_of_existing_nodes
#echo $existing_nodes

python ${script_dir}/reload.py ${measurements_dir} "$existing_nodes"
exit 0
