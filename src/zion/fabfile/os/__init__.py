
from fabric.api import *
from fabric.contrib import *
from .. zion_config_helper import ZionConfigHelper

# these must be run as root

@task
def enable_sudo():
    sudoer_temp_file = '/etc/sudoers.zion_temp'
    sudoer_bak_file = '/etc/sudoers.zion_bak'
    # make an extra paranoid backup
    run('cp -p /etc/sudoers ' + sudoer_bak_file)
    # make a working file to mess with
    run('cp -p /etc/sudoers ' + sudoer_temp_file)
    # remove a comment to allow sudo for all members of wheel
    files.uncomment(sudoer_temp_file, '%wheel[\t]+ALL=\(ALL\)[\t]+ALL')
    # verify that the resulting file is OK according to visudo
    sudo('visudo -c -q -f ' + sudoer_temp_file)
    # and copy it back in place
    run('cp -p ' + sudoer_temp_file + ' /etc/sudoers')
    # clean up (our file and the one visudo makes automagically)
    run('rm ' + sudoer_temp_file)
    run('rm ' + sudoer_temp_file + '.bak')

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

# these can be run as a user with sudo poswer

@task
def setup():
  run('touch ~/zion_test/os.setup')
