import subprocess

"""
run few command on remote node in yanoama

commands are coded two comma-separated 
integers only

codes list:

0,0: update main source
0,1: start daemon
0,2: stop daemon
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
        if command == 0 and param == 1:
            output = subprocess.Popen(['sudo','/home/upmc_aren/monitoring/amen/amend','start'], \
                                      stdout=subprocess.PIPE, close_fds=True).communicate()[0]
        elif command == 0 and param == 2:
            output = subprocess.Popen(['sudo','/home/upmc_aren/monitoring/amen/amend','stop'], \
                                      stdout=subprocess.PIPE, close_fds=True).communicate()[0]
        elif command == 0 and param == 0:
            output = subprocess.Popen(['git','pull'], \
                                      cwd='/home/upmc_aren/yanoama', \
                                      stdout=subprocess.PIPE, close_fds=True).communicate()[0]
            output += subprocess.Popen(['sudo','/home/upmc_aren/yanoama/contrib/yanoama/pilotd','stop'], \
                                      stdout=subprocess.PIPE, close_fds=True).communicate()[0]
            output += subprocess.Popen(['sudo','/home/upmc_aren/yanoama/contrib/yanoama/pilotd','start'], \
                                      stdout=subprocess.PIPE, close_fds=True).communicate()[0]
#        elif cmd == "get_date":
#            output = subprocess.Popen(['date'], \
#                                      stdout=subprocess.PIPE, close_fds=True).communicate()[0] 
        return output
