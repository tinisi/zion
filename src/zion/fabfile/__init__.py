
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
    # os.enable_sudo()
    os.add_users()

@task
def install():
#    os.ssh_lockdown()
    os.update()
#    users.create()
#    bind.install()
#    dhcp.install()
#    puppet.install()
#    foreman.install()
