#how to run: sh get_rtt.sh [HOSTNAME/IP]
#output: rtt in milliseconds OR -1 if failed

#it send FIVE TCP SYN packets to SSH port for testing connectivity and returns the RTT in milliseconds, or 0.0 if it fails
paping -c 5 -p 22 $1|grep Minimum|cut -d= -f2|cut -d, -f1|sed 's/ms//g'|sed 's/ //g'
