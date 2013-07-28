
from fabric.api import *
import os
import users
import bind
import dhcp
import puppet
import foreman
from zion_config_helper import ZionConfigHelper

@task
def pre_install():
    # this should be all the steps that must be run as root
    os.enable_sudo()
    # os.disable_remote_root()

@task
def install():
    zch = ZionConfigHelper(env.zion_config_file, env.host)
    string = '''
host ip: %(ip)s
debug: %(debug)s 
''' % {
    'ip': zch.get_host_conf('ip'),
   	'debug': str(zch.get_conf('debug'))
    }
    __cat_string_to_file(string, '~/zion_test/install')
    os.setup()
    users.create()
    bind.install()
    dhcp.install()
    puppet.install()
    foreman.install()

def __cat_string_to_file(string, file):
    cmd = 'cat <<< "' + string + '" > ' + file
    run(cmd)