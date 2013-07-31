
from fabric.api import *
from fabric.contrib import *
from .. zion_config_helper import ZionConfigHelper

# these MUST be run as root

@task
def enable_sudo():
    sudoer_temp_file = '/etc/sudoers.zion_temp'
    # make a working file to mess with
    run('cp -p /etc/sudoers ' + sudoer_temp_file)
    # remove a comment to allow sudo for all members of wheel
    files.uncomment(sudoer_temp_file, '%wheel[\t]+ALL=\(ALL\)[\t]+ALL', backup='.zion_bak')
    # verify that the resulting file is OK according to visudo
    sudo('visudo -c -q -f ' + sudoer_temp_file)
    # and copy it back in place
    run('cp -p ' + sudoer_temp_file + ' /etc/sudoers')
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
            run('usermod --append --groups %(groupString)s %(name)s' % {"groupString":','.join(user['groups']), "name":user['name'] })

# these can be run as a user with sudo user

@task
def ssh_lockdown():
    # we are gonna guts it and work on this one in place (no temp file and swap)
    sshd_config_file = '/etc/ssh/sshd_config'
    # since I have three changes to the same file, making numbered backup extensions
    files.sed(sshd_config_file, '#PermitRootLogin yes', 'PermitRootLogin no', use_sudo=True, backup='.zion_bak_1')
    files.sed(sshd_config_file, '#UseDNS yes', 'UseDNS no', use_sudo=True, backup='.zion_bak_2')
    files.uncomment(sshd_config_file, 'Port 22', use_sudo=True, backup='.zion_bak_3')
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
