
from fabric.api import *
import os
import users
import bind
import dhcp
import puppet
import foreman

@task
def install():
    cmd = 'touch ~/zion_test/install'
    run(cmd)
    os.setup()
    users.create()
    bind.install()
    dhcp.install()
    puppet.install()
    foreman.install()