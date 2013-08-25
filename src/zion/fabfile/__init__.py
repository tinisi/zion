
from fabric.api import *
import os
import dhcp
import bind
import puppet
import foreman
from zion_config_helper import ZionConfigHelper

@task
def pre_install():
    # this should be all the steps that must be run as root
 	os.enable_sudo()
 	os.add_users()

@task
def install():
#    os.ssh_lockdown()
#    os.update()
#    os.add_repos()
#    os.configure_selinux()
#    os.configure_iptables()
#    bind.install()
	# NOTE: bind needs to be installed before dhcp
	# because of depdendency on dnssec-keygen
#    dhcp.install()
    puppet.install()
#    foreman.install()
