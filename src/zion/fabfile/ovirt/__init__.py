
from fabric.api import *

@task
def install():
    # oVirt here we come!
    sudo("yum --assumeyes localinstall http://resources.ovirt.org/pub/yum-repo/ovirt-release35.rpm")
    sudo("yum --assumeyes install ovirt-engine-setup-plugin-allinone")
    # TODO: would like to use the command to generate an answer file and make this less interactive
    # tried with current version, and script doesn't generate a complete answer file.
    # So, giving up for now, this part is just gonna have to be interactive.
    sudo("sudo engine-setup")
