#!/bin/bash

#initscript for AREN

cd /tmp
rm -rf bootstrap.sh 
wget --no-check-certificate https://github.com/guthemberg/yanoama/raw/master/yanoama/system/bootstrap.sh
sh bootstrap.sh
