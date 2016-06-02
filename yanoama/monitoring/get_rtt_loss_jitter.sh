#!/bin/sh

#how to run: sh get_rtt_loss_jitter.sh [HOSTNAME/IP]
#output: rtt,loss,jitter where rtt and jitter in milliseconds and loss in percentage OR -1,-1-,1 if failed

#it send FIVE icmp packets for testing connectivity and returns the RTT in milli seconds, or -1 if it fails
ping_result=`ping -i 0.2 -qc 5 $1  2> /dev/null`
rtt=`echo $ping_result |tail -n1|cut -d= -f2|cut -d/ -f1|awk -F" " '{ if(length($1)>0) printf "%s", $1; else printf "%s", "-1" }'`
if [ `echo $ping_result |grep loss|wc -l` -gt 0 ]
then
  packet_loss=`echo $ping_result |grep loss|cut -d, -f3|cut -d\% -f1|awk -F" " '{ if(length($1)>0) printf "%s", $1; else printf "%s", "-1" }'`
else
  packet_loss=-1
fi
jitter=`echo $ping_result |tail -n1|cut -d= -f2|cut -d/ -f4|cut -d" " -f1|awk -F" " '{ if(length($1)>0) printf "%s", $1; else printf "%s", "-1" }'`

printf "%s" "${rtt},${packet_loss},${jitter}"