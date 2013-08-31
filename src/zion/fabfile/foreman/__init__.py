
from fabric.api import *
from fabric.contrib import *
from .. zion_config_helper import ZionConfigHelper

@task
def libvirt_dependencies():
    sudo("yum --assumeyes install libvirt")
    sudo("yum --assumeyes install foreman-libvirt")

@task
def install():
    sudo("yum --assumeyes -y install http://yum.theforeman.org/releases/1.1/el6/i386/foreman-release-1.1stable-3.el6.noarch.rpm")
    sudo("yum --assumeyes -y install foreman-installer")
    sudo("echo include foreman_installer | puppet apply --modulepath /usr/share/foreman-installer")

@task
def configure_libvirt():
    # set up a bridged interface
    sudo("virsh iface-bridge eth0 br0")
    __deploy_polkit_conf()
    __add_foreman_to_suduers()
    __setup_storage_pool()
    # and restart again
    sudo("service libvirtd restart")

def __deploy_polkit_conf():
    # no data yet, but stubbing this out to make it easier later
    data = {};
    # put the Policy Kit auth file in place
    filename = env.absolute_path_to_zion + '/src/zion/fabfile/foreman/templates/50-se.tmtowtdi-libvirt-local-access.pkla'
    destination = '/etc/polkit-1/localauthority/50-local.d/50-se.tmtowtdi-libvirt-local-access.pkla'
    files.upload_template(filename, destination, context=data, use_sudo=True, backup=True)
    sudo('chown root:root ' + destination)
    sudo('chmod g=r ' + destination)

def __add_foreman_to_suduers():
    sudoer_file = '/etc/sudoers'
    new_suduer_lines = '''Defaults:foreman-proxy !requiretty\
foreman-proxy ALL = NOPASSWD: /usr/bin/puppet'''
    search_string = '# %users  localhost=/sbin/shutdown -h now'
    replace_string = search_string + '\\n\\n' + new_suduer_lines
    files.sed(sudoer_file, search_string, replace_string, use_sudo=True, backup='.zion_bak')

def __setup_storage_pool():
    local_pool_file = env.absolute_path_to_zion + '/src/zion/fabfile/foreman/templates/pool.xml'
    put(local_path=local_pool_file, remote_path=None, use_sudo=True)
    sudo("mkdir /var/lib/libvirt/filesystems")
    sudo("virsh pool-define pool.xml")
    sudo("virsh pool-autostart default")

@task
def configure_foreman():
    __add_dhcp_to_proxy_config()
    __enable_dns_proxy()
    __enable_dhcp_proxy()
    __add_proxy_user_to_groups()
    __setup_dhcp_folder_perms()

def __add_dhcp_to_proxy_config():
    proxy_config_file = '/etc/foreman-proxy/settings.yml'
    new_proxy_config_lines = ''':dhcp_key_name: omapi_key\\
:dhcp_key_secret: ''' + __get_dhcp_key()
    search_string = '#:dhcp_leases: /var/lib/dhcpd/dhcpd.leases'
    replace_string = search_string + '\\n\\n' + new_proxy_config_lines
    files.sed(proxy_config_file, search_string, replace_string, use_sudo=True, backup='.zion_bak')
    files.uncomment(proxy_config_file, ':dhcp_config: /etc/dhcpd.conf', use_sudo=True, backup='.zion_bak')
    files.uncomment(proxy_config_file, ':dhcp_leases: /var/lib/dhcpd/dhcpd.leases', use_sudo=True, backup='.zion_bak')

def __get_dhcp_key():
    # this assumes that the one key we want to use has been generated and
    # and left in current user's home directory
    # get the secret string from the formatted key file
    return sudo("sudo cat Komapi_key.+*.private |grep ^Key|cut -d ' ' -f2-")

def __enable_dhcp_proxy():
    proxy_config_file = '/etc/foreman-proxy/settings.yml'
    # the positional arguments for this are file, search, replace
    files.sed(proxy_config_file, ':dhcp: false', ':dhcp: true', use_sudo=True, backup='.zion_bak')
    files.sed(proxy_config_file, '#:dhcp_subnets: \[192.168.205.0/255.255.255.128, 192.168.205.128/255.255.255.128\]', ':dhcp_subnets: [192.168.0.0/255.255.255.0]', use_sudo=True, backup='.zion_bak')
    files.uncomment(proxy_config_file, ':log_level: DEBUG', use_sudo=True, backup='.zion_bak')

def __enable_dns_proxy():
    files.sed(proxy_config_file, ':dns: false', ':dns: true', use_sudo=True, backup='.zion_bak')
    files.sed(proxy_config_file, ':dns_key: /etc/rndc.key', ':dns_key: ' + __get_dns_key_path(), use_sudo=True, backup='.zion_bak')

def __get_dns_key_path():
    # this assumes that the one key is in a chrooted etc
    return sudo('ls /var/named/chroot/etc/Kf*.private')

def __add_proxy_user_to_groups():
    sudo('usermod -a -G dhcpd foreman-proxy')
    sudo('usermod -a -G named foreman-proxy')

def __setup_dhcp_folder_perms():
    # TODO: this is clearly not right
    # need to figger out more precise perms
    sudo('chmod o=rx /etc/dhcp')
