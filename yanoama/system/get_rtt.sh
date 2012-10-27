#how to run: sh get_rtt.sh [HOSTNAME/IP]
#output: rtt in milliseconds OR -1 if failed

#it send FIVE icmp packets for testing connectivity and returns the RTT in milli seconds, or -1 if it fails
ping_result=`ping -qc 5 $1  2> /dev/null` ; echo $ping_result |tail -n1|cut -d= -f2|cut -d/ -f1|awk -F" " '{ if(length($1)>0) printf "%s", $1; else printf "%s", "-1" }'
