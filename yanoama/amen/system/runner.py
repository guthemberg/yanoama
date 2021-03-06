from yanoama.amen.system.collector import system_info_collector, process_info_collector
from yanoama.amen.core import settings
from yanoama.amen.utils.dates import unix_utc_now
import sys

class Runner(object):
    
    def __init__(self):
        self.active_checks = settings.SYSTEM_CHECKS
        #self.process_checks = settings.PROCESS_CHECKS

    def system(self):
        
        system_info_dict = {}
        
        now = unix_utc_now() # unix time
        
        ##table (* index)
        ##node 
        #ts(*),hostname(*),tx,rx,storage_usage,num_obj
        ##object
        #oid(*),length,owners
        ##swarm 
        #ts(*),oid,tx,rx,hostname
        if 'node' in self.active_checks and sys.platform != 'darwin':
            node = system_info_collector.get_node_info(settings.STORAGE_PATH)

            if node != False:
                node['time'] = now
                system_info_dict['node'] = node

        elif 'memory' in self.active_checks:
            memory = system_info_collector.get_memory_info()

            if memory != False:
                memory['time'] = now
                system_info_dict['memory'] = memory

        elif 'cpu' in self.active_checks:
            cpu = system_info_collector.get_cpu_utilization()

            if cpu != False:
                cpu['time'] = now
                system_info_dict['cpu'] = cpu

        elif 'loadavg' in self.active_checks:
            loadavg = system_info_collector.get_load_average()

            if loadavg != False:
                loadavg['time'] = now
                system_info_dict['loadavg'] = loadavg


        elif 'disk' in self.active_checks:
            disk = system_info_collector.get_disk_usage()

            if disk != False:
                disk['time'] = now
                system_info_dict['disk'] = disk


        return system_info_dict

    # empty dictionary, used when stopping the daemon to avoid chart bugs
    def empty(self):
        empty_dict = {}
        now = unix_utc_now()
        for check in self.active_checks:
            empty_dict[check] = {'time': now, 'last': 1}

        return empty_dict

    #def processes(self):
    #    now = unix_utc_now()

    #    process_info_dict = {}
    #    for process in self.process_checks:
    #        process_info_dict[process]  = process_info_collector.check_process(process)
    #        process_info_dict[process]['time'] = now

    #    return process_info_dict

runner = Runner()
            

