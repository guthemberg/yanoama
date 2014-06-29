#!/bin/bash

#initscript for AREN

cd /tmp
rm -rf bootstrap.sh 
wget https://github.com/guthemberg/aren/raw/master/yanoama/system/bootstrap.sh
sh bootstrap.sh
