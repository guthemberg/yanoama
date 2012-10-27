from datetime import datetime
from time import mktime
from planetlab import PlanetLabAPI
from configobj import ConfigObj
import sys

if __name__ == '__main__':
    config=ConfigObj('ple.conf')
    api=PlanetLabAPI(config['host'],config['username'],config['password'])
    #update for eight weeks
    shift_time=8*7*24*60*60 #eight weeks in seconds
    now = (datetime.utcnow())
    new_expire_time=(int(mktime(now.timetuple()))+shift_time)
    api.update(new_expire_time)
    sys.exit(0)
