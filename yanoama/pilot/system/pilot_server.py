#!/usr/bin/env python


import SocketServer
from threading import Thread

import subprocess

"""
run few command on remote node in yanoama

commands are coded two comma-separated 
integers only

codes list:

0,0: update main sources
0,1: bootstrap
0,2: shutdown (kill pilot and amend)
0,3: start amen daemon
0,4: stop amen daemon
9,9: get date for testing
"""
class LinuxSystemConsole(object):
    
    def getHostname(self):
        return (subprocess.Popen(['hostname'], \
                                  stdout=subprocess.PIPE, close_fds=True).communicate()[0]).strip() 
        
        
    def run(self,cmd):
        output = "unknown "
        args=cmd.split(',')
        if len(args)!=2:
            return output
        try:
            command=int(args[0])
            param=int(args[1])
        except ValueError:
            return output
        """
        maintenance codes:
        
        0,0: update main sources
        0,1: bootstrap
        0,2: shutdown/kill pilot
        0,3: start amen daemon
        0,4: stop amen daemon
        """
        if command == 0 :
            if param == 0:
                output = self.update_sources()
            elif param == 1:
                self.clenup_temp_scripts()
                script_name='bootstrap.sh'
#                script_wrapper_name='bootstrap_wrapper.sh'
                dest_dir='/tmp/'
                bootstrap_source_script='/home/upmc_aren/yanoama/yanoama/system/'+script_name
#                bootstrap_source_script_wrapper='/home/upmc_aren/yanoama/yanoama/system/'+script_wrapper_name
                self.update_sources()
                self.copy_file(bootstrap_source_script, dest_dir)
#                self.copy_file(bootstrap_source_script_wrapper, dest_dir)
                self.run_shell_script(dest_dir+script_name)
                output="restarting."
            elif param == 2:
                output = self.kill('pilotd')
            elif param == 3:
                output = self.start_amend()
            elif param == 4:
                output = self.stop_amend()
        elif command == 9 and param == 9:
            output =  self.get_date()
        return output
    
    def update_sources(self):
        return subprocess.Popen(['git','pull'], \
                              cwd='/home/upmc_aren/yanoama', \
                              stdout=subprocess.PIPE, close_fds=True).communicate()[0]
                              
    def get_date(self):
        return subprocess.Popen(['date'], \
                                      stdout=subprocess.PIPE, close_fds=True).communicate()[0]

    def copy_file(self,source_file,destination_path):
        return subprocess.Popen(['cp','-f',source_file,destination_path], \
                                      stdout=subprocess.PIPE, close_fds=True).communicate()[0]

    def kill(self,process_name):
        output = subprocess.Popen(['sudo', 'pkill', '-f', process_name], \
                                      stdout=subprocess.PIPE, close_fds=True).communicate()[0]
        if process_name=="pilotd":
            subprocess.Popen(['sudo', 'rm', '-rf', "/var/run/pilotd.pid"], \
                                      stdout=subprocess.PIPE, close_fds=True).communicate()[0]
        return output

    def start_amend(self):
        return subprocess.Popen(['sudo','/home/upmc_aren/monitoring/amen/amend','start'], \
                                      stdout=subprocess.PIPE, close_fds=True).communicate()[0]
                                      
    def stop_amend(self):
        return subprocess.Popen(['sudo','/home/upmc_aren/monitoring/amen/amend','stop'], \
                                      stdout=subprocess.PIPE, close_fds=True).communicate()[0]
    def run_shell_script(self,full_path_to_shell):
        return subprocess.Popen(['sh',full_path_to_shell], \
                                      stdout=subprocess.PIPE, close_fds=True)
    def clenup_temp_scripts(self):
        return subprocess.Popen(['sudo','rm','-rf','/tmp/*.sh'], \
                                      stdout=subprocess.PIPE, close_fds=True).communicate()[0]
                                      
class PilotServer(SocketServer.BaseRequestHandler):

    bsize=1024

    def handle(self):
        console = LinuxSystemConsole()
        data = self.request.recv(self.bsize)
        output = console.run(data.strip())
        self.request.send(output[:min(len(output),self.bsize)]) 
        return
        
    def finish(self):
        self.request.send('bye ' + str(self.client_address) + '\n')


class service(SocketServer.BaseRequestHandler):
    def handle(self):
        data = 'dummy'
        print "Client connected with ", self.client_address
        while len(data):
            data = self.request.recv(1024)
            self.request.send(data)

        print "Client exited"
        self.request.close()


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

t = ThreadedTCPServer(('',1520), PilotServer)
t.serve_forever()