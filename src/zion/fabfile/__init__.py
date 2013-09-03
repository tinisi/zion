
from fabric.api import *
import centos
import dhcp
import bind
import puppet
import foreman

@task
def pre_install():
    # this should be all the steps that must be run as root
 	centos.enable_sudo()
 	centos.add_users()

@task
def install():
    centos.ssh_lockdown()
    centos.update()
    centos.add_repos()
    centos.configure_selinux()
    centos.configure_iptables()
    bind.install()
    # NOTE: bind needs to be installed before dhcp
    # because of depdendency on dnssec-keygen
    dhcp.install()
    puppet.install()
    foreman.libvirt_dependencies()
    foreman.install()
    foreman.configure_libvirt()
    foreman.configure_foreman()
