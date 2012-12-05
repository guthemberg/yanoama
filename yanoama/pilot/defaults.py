from yanoama.pilot.system._linux import LinuxSystemConsole

try:
    import json
except ImportError:
    import simplejson as json

DEFAULT_CONF_FILE='/etc/yanoama.conf'

try:
    config_file = file(DEFAULT_CONF_FILE).read()
    config = json.loads(config_file)
except Exception, e:
    print "There was an error in your configuration file ("+DEFAULT_CONF_FILE+")"
    raise e

# host and port to listen
pilot= config.get('pilot', {})
HOST = pilot.get('host', LinuxSystemConsole().getHostname())
PORT = pilot.get('port', 49127)
