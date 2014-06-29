#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:        client.py
# Purpose:     Pilot client for remote commands on planetlab nodes
#
# Author:      Guthemberg Silvestre
#
# License:
#===============================================================================
# Copyright (c) <2012>, <Guthemberg Silvestre>
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met: 
# 
# 1. Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer. 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution. 
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies, 
# either expressed or implied, of the FreeBSD Project.
#===============================================================================

import sys
import socket
from time import gmtime, strftime
try:
    import json
except ImportError:
    import simplejson as json


class ClientSocket():
    
    
    rbufsize = -1
    wbufsize = 0


    def __init__(self, address):
        if type(address) == type(()) and (type(address[0]) == type(u"") or type(address[0]) == type('')) and type(address[1]) == type(1):
            pass
        else:
            print ('Address is of incorrect type. \n' +
                  'Must be (serverHost (str), serverPort (int)).')
            sys.exit(1)

        self.address = address
        
        
    def run(self,cmd="date"):
        # Create a socket (SOCK_STREAM means a TCP socket)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            # Connect to server and send data
            sock.connect(self.address)
            sock.sendall(cmd + "\n")
        
            # Receive data from the server and shut down
            received = sock.recv(1024)
        finally:
            sock.close()
        print "%s. %s,%s" % (strftime("%Y-%m-%d %H:%M:%S", gmtime()),\
               "    Sent:     "+(cmd),"    received: " +(received.strip()))

def get_pilot_port():
    try:
        config_file = file('/etc/yanoama.conf').read()
        config = json.loads(config_file)
    except Exception, e:
        print "There was an error in your configuration file (/etc/yanoama.conf)"
        raise e
    _pilot = config.get('pilot', {'port':44444})
    return (_pilot['port']) 


def main():
    if len(sys.argv) != 3:
        print "run as: client.py host cmd"
        sys.exit(1)
    host=sys.argv[1]
    cmd=sys.argv[2]
    
    address = (host, get_pilot_port())

    console = ClientSocket(address)
    console.run(cmd)


if __name__ == '__main__':
    main()