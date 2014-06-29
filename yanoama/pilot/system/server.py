#! /usr/bin/python
#-------------------------------------------------------------------------------
# Name:        server.py
# Purpose:     Pilot server for remote commands on planetlab nodes
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

import SocketServer


from _linux import LinuxSystemConsole
console = LinuxSystemConsole()


connections={}


class ThreadedTCPRequestHandler(SocketServer.StreamRequestHandler):

    bsize=1024

    def setup(self):
        SocketServer.StreamRequestHandler.setup(self)

    def handle(self):
        data = self.request.recv(self.bsize)
        output = console.run(data.strip())
        self.request.send(output[:min(len(output),self.bsize)]) 
        return
        
    def finish(self):
        self.request.send('bye ' + str(self.client_address) + '\n')


#if __name__ == '__main__':
#    server = SocketServer.ThreadingTCPServer((host, port), ThreadedTCPRequestHandler)
#
#    print 'waiting for commands on %s:%s...' % (host, port)
#    server.serve_forever()