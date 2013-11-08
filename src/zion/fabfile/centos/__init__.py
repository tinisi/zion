
from fabric.api import *
from fabric.contrib import *
from .. zion_config_helper import ZionConfigHelper

# these MUST be run as root

@task
def enable_sudo():
    sudoer_temp_file = '/etc/sudoers.zion_temp'
    sudoer_file = '/etc/sudoers'
    # make a working file to mess with
    run('cp -p ' + sudoer_file + ' ' + sudoer_temp_file)
    # remove a comment to allow sudo for all members of wheel
    # TODO: add step at the end to do this:
    # files.comment(sudoer_temp_file, '%wheel[\t]+ALL=\(ALL\)[\t]+NOPASSWD:[ ]+ALL', backup='.zion_bak')
    # files.uncomment(sudoer_temp_file, '%wheel[\t]+ALL=\(ALL\)[\t]+ALL', backup='.zion_bak')
    files.uncomment(sudoer_temp_file, '%wheel[\t]+ALL=\(ALL\)[\t]+NOPASSWD:[ ]+ALL', backup='.zion_bak')
    # verify that the resulting file is OK according to visudo
    run('visudo -c -q -f ' + sudoer_temp_file)
    # and copy it back in place
    run('cp -p ' + sudoer_temp_file + ' ' + sudoer_file)
    # clean up (our temp file, leave the backup created by files.uncomment())
    run('rm ' + sudoer_temp_file)

@task
def add_users():
    # userdel --force --remove tinisi
    zch = ZionConfigHelper(env.zion_config_file, env.host)
    users = zch.get_host_conf('users')

    # loop over all the user objects
    for user in users:
        # first create a locked user
        run('useradd %(name)s' % user)
        # and now set the password
        run('echo %(password)s| passwd %(name)s --stdin $1' % user)
        # if there are groups, add them
        if 'groups' in user: 
            run('usermod --append --groups %(group_string)s %(name)s' % {"group_string":','.join(user['groups']), "name":user['name'] })

# these should be run as a user with sudo

@task
def ssh_lockdown(allow_remote_root=False):
    # we are gonna guts it and work on this one in place (no temp file and swap)
    sshd_config_file = '/etc/ssh/sshd_config'
    # since I have three changes to the same file, making numbered backup extensions
    files.sed(sshd_config_file, '#UseDNS yes', 'UseDNS no', use_sudo=True, backup='.zion_bak_2')
    files.uncomment(sshd_config_file, 'Port 22', use_sudo=True, backup='.zion_bak_3')
    # this one takes an argument, defaults to True
    if not allow_remote_root:
        files.sed(sshd_config_file, '#PermitRootLogin yes', 'PermitRootLogin no', use_sudo=True, backup='.zion_bak_1')    
    # and restart the service to pick up the changes
    sudo('service sshd restart')

@task
def update():
    # list what is installed so we know what happened
    sudo('yum list installed')
    # this command returns 100 when there are any updates, so only showing a warning
    with settings(warn_only=True):
        sudo('yum check-update')
    # just go for it!
    sudo('yum --assumeyes update')
    # and then another list to compare
    sudo('yum list installed')

@task
def add_repos():
    sudo('rpm -ivh http://download.fedoraproject.org/pub/epel/6/i386/epel-release-6-8.noarch.rpm')
    sudo('rpm -ivh http://yum.puppetlabs.com/el/6/products/i386/puppetlabs-release-6-6.noarch.rpm')

@task
def configure_selinux():
    # this is clearly wrong, but SELinux default rules break chroot'ed named
    # TODO: figure out a rule set that will work with chrooted bind and whatever else we need
    selinux_config_file = '/etc/selinux/config'
    # the positional arguments for this are file, search, replace
    files.sed(selinux_config_file, 'SELINUX=enforcing', 'SELINUX=permissive', use_sudo=True, backup='.zion_bak')    
    sudo('setenforce Permissive')

@task
def configure_iptables():
    # this is clearly wrong, but breaks chroot'ed named
    # TODO: figure out a rule set that will work for the final full suite
    sudo('service iptables save')
    sudo('service iptables stop')
    sudo('chkconfig iptables off')

@task
def restart_services():
    # restart everything we care about
    with settings(warn_only=True):
        sudo('service libvirtd restart')
        sudo('service messagebus restart')
        sudo('service named restart')
        sudo('service dhcpd restart')
        sudo('service foreman-proxy restart')
        sudo('service foreman restart')
