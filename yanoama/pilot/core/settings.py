from yanoama.pilot import defaults

class Settings(object):

#    HOST=""
#    PORT=49126
    def __init__(self):
        # update this dict from the defaults dictionary (but only for ALL_CAPS settings)
        for setting in dir(defaults):
            if setting == setting.upper():
                setattr(self, setting, getattr(defaults, setting))

