
from fabric.api import *
import centos
import dhcp
import bind
import puppet
import foreman
import ovirt
from zion_config_helper import ZionConfigHelper

@task
def pre_install():
    # this should be all the steps that must be run as root
    centos.enable_sudo()
    centos.add_users()

@task
def install_ovirt():
    centos.ssh_lockdown(allow_remote_root=True)
    centos.update()
    centos.add_repos()
    centos.configure_selinux()
    centos.configure_iptables()
    bind.replace_resolv()
    ovirt.install()

@task
def install_foreman():
    centos.ssh_lockdown()
    centos.update()
    centos.add_repos()
    centos.configure_selinux()
    centos.configure_iptables()
    bind.install()
    # this should only be run once ever in the life of a server
    # and BEFORE configure_server(), which hoovers up the key
    bind.generate_foreman_dns_key()
    bind.configure_server()
    bind.configure_hosts()
    bind.restart_named()
    # TODO: add a test and abort if no fqdn at this point
    bind.replace_resolv()
    # NOTE: bind needs to be installed before dhcp
    # because of dependency on dnssec-keygen
    dhcp.install()
    # seems like The Foreman should install this...but whatever
    puppet.install()
    # TODO: I think this is not needed now what we are using oVirt
    # leaving here for now
    foreman.libvirt_dependencies()
    foreman.install()
    # TODO: only SOME of this method needs be run now that we are using oVrt
    # I'll refactor later
    foreman.configure_libvirt()
    foreman.configure_foreman()

@task
def restart_foreman_services():
    centos.restart_services()

@task
def configure_hosts():
    bind.configure_hosts()
    bind.restart_named()

@task
def debug_scratch():
    pass
