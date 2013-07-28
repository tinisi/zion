
import json

class ZionConfigHelper:
    """
    This helper class will return shared config or config for the current host.
    The config file should be a json document with this shape:
    {
        "shared_conf": {
            "key": "value"
        },
        "host_conf": {
            "env.host": {
                "key": "value"
            }
        }
    }        
    """
    def __init__(self, config_file, host):
        # set the host attribute
        self.host=host
        # import the config file
        with open(config_file) as config_file:
            self.zion_conf = json.load(config_file)

    def get_conf(self, key):
        return self.zion_conf['shared_conf'][key]

    def get_host_conf(self, key):
        return self.zion_conf['host_conf'][self.host][key]
