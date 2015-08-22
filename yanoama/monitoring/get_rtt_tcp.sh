#how to run: sh get_rtt.sh [HOSTNAME/IP] [PORT=22]
#output: rtt in milliseconds OR -1 if failed

port=22
if [ $# -eq 2 ]
then
	port=$2
fi

#it send FIVE TCP SYN packets to SSH port for testing connectivity and returns the RTT in milliseconds, or 0.0 if it fails
paping --nocolor -c 5 -p $port $1|grep Minimum|cut -d= -f2|cut -d, -f1|sed 's/ms//g'|sed 's/ //g'
