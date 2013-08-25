
from fabric.api import *

@task
def libvirt_dependencies():
    sudo("yum --assumeyes install ruby-libvirt")
    sudo("yum --assumeyes install libvirt")
    sudo("service libvirtd restart")

@task
def install():
    sudo("yum --assumeyes -y install http://yum.theforeman.org/releases/1.1/el6/i386/foreman-release-1.1stable-3.el6.noarch.rpm")
    sudo("yum --assumeyes -y install foreman-installer")
    sudo("echo include foreman_installer | puppet apply --modulepath /usr/share/foreman-installer")

@task
def configure_libvirt():
    sudo("virsh iface-bridge eth0 br0")

@task
def configure_foremant():
    pass