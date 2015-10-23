
from fabric.api import *
from fabric.contrib import *
from .. zion_config_helper import ZionConfigHelper

# we need this in several methods below, making it s package level var
proxy_config_file = '/etc/foreman-proxy/settings.yml'

# TODO: I think this can be removed now that we are using oVirt
@task
def libvirt_dependencies():
    sudo("yum --assumeyes install libvirt")

@task
def install():
    sudo("yum --assumeyes install http://yum.theforeman.org/releases/1.4.2/el6/x86_64/foreman-release.rpm")
    sudo("yum --assumeyes install foreman-installer")
    sudo("yum --assumeyes install foreman-ovirt")
    sudo("echo include foreman_installer | puppet apply --modulepath /usr/share/foreman-installer")

# TODO: leaving in all the libvirt specific stuff for now
# even though it doesn't apply now that we are using oVirt on another machine
# to host the VMs
@task
def configure_libvirt():
    sudo("service libvirtd start")
    # set up a bridged interface
    sudo("virsh iface-bridge eth0 br0")
    __add_certs_to_conf()
    __deploy_polkit_conf()
    # TODO: I think now that we are switching to use oVirt, this is not needed
    __setup_storage_pool()
    # TODO: I think now that we are switching to use oVirt, this is not needed
    sudo("service libvirtd restart")
    # we need to dissble this (not sure why actually)
    sudo("service dnsmasq stop")
    sudo("chkconfig dnsmasq off")

def __add_certs_to_conf():
    # TODO: for fuck's sake, this is not doing anything....
    libvirtd_config_file = '/etc/libvirt/libvirtd.conf'
    new_libvirtd_config_lines = key_file = '''"/var/lib/puppet/ssl/private_keys/zion.tinisi.local.pem"\\
cert_file = "/var/lib/puppet/ssl/certs/zion.tinisi.local.pem"\\
ca_file = "/var/lib/puppet/ssl/certs/ca.pem"'''
    search_string = '''# TLS x509 certificate configuration\\
#\\
'''
    replace_string = search_string + '\\n\\n' + new_libvirtd_config_lines
    files.sed(libvirtd_config_file, search_string, replace_string, use_sudo=True, backup='.zion_bak')

def __deploy_polkit_conf():
    # no data yet, but stubbing this out to make it easier later
    data = {};
    # put the Policy Kit auth file in place
    filename = env.absolute_path_to_zion + '/src/zion/fabfile/foreman/templates/50-se.tmtowtdi-libvirt-local-access.pkla'
    destination = '/etc/polkit-1/localauthority/50-local.d/50-se.tmtowtdi-libvirt-local-access.pkla'
    files.upload_template(filename, destination, context=data, use_sudo=True, backup=True)
    sudo('chown root:root ' + destination)
    sudo('chmod g=r ' + destination)

def __setup_storage_pool():
    local_pool_file = env.absolute_path_to_zion + '/src/zion/fabfile/foreman/templates/pool.xml'
    put(local_path=local_pool_file, remote_path=None, use_sudo=True)
# not sure I need this?
#    sudo("mkdir /var/lib/libvirt/filesystems")
    sudo("virsh pool-define pool.xml")
    sudo("virsh pool-autostart default")

@task
def configure_foreman():
    __add_foreman_to_suduers()
    __add_dhcp_to_proxy_config()
    __enable_dns_proxy()
    __enable_dhcp_proxy()
    __add_proxy_user_to_groups()
    __setup_dhcp_folder_perms()

def __add_foreman_to_suduers():
    sudoer_temp_file = '/etc/sudoers.zion_temp'
    sudoer_file = '/etc/sudoers'
    # make a working file to mess with
    sudo('cp -p ' + sudoer_file + ' ' + sudoer_temp_file)
    sudoer_file = '/etc/sudoers'
    new_suduer_lines = '''Defaults:foreman-proxy !requiretty\\
foreman-proxy ALL = NOPASSWD: /usr/bin/puppet'''
    search_string = '# %users  localhost=/sbin/shutdown -h now'
    replace_string = search_string + '\\n\\n' + new_suduer_lines
    files.sed(sudoer_temp_file, search_string, replace_string, use_sudo=True, backup='.zion_bak')
    # verify that the resulting file is OK according to visudo
    sudo('visudo -c -q -f ' + sudoer_temp_file)
    # and copy it back in place
    sudo('cp -p ' + sudoer_temp_file + ' ' + sudoer_file)
    # clean up (our temp file, leave the backup created by files.uncomment())
    sudo('rm ' + sudoer_temp_file)

def __add_dhcp_to_proxy_config():
    new_proxy_config_lines = ''':dhcp_key_name: omapi_key\\
:dhcp_key_secret: ''' + __get_dhcp_key()
    search_string = '#:dhcp_leases: /var/lib/dhcpd/dhcpd\\.leases'
    replace_string = search_string + '\\n\\n' + new_proxy_config_lines
    files.sed(proxy_config_file, search_string, replace_string, use_sudo=True, backup='.zion_bak')
    # NOTE: using sed instead of the uncomment() method because I was getting a mysterious sed error
    # (I think the lack of spaces after the comment in the original document was messing up Fabric)
    files.sed(proxy_config_file, '#:dhcp_config: /etc/dhcpd', ':dhcp_config: /etc/dhcp/dhcpd', use_sudo=True, backup='.zion_bak')    
    files.sed(proxy_config_file, '#:dhcp_leases: /var/lib/dhcpd/dhcpd', ':dhcp_leases: /var/lib/dhcpd/dhcpd', use_sudo=True, backup='.zion_bak')    
    # aparently permissions are important
    sudo('chgrp foreman-proxy /etc/dhcp')
    sudo('chgrp foreman-proxy /etc/dhcp/dhcpd.conf')

def __get_dhcp_key():
    # this assumes that the one key we want to use has been generated and
    # and left in current user's home directory
    # get the secret string from the formatted key file
    return sudo("sudo cat Komapi_key.+*.private |grep ^Key|cut -d ' ' -f2-")

def __enable_dhcp_proxy():
    # the positional arguments for this are file, search, replace
    files.sed(proxy_config_file, ':dhcp: false', ':dhcp: true', use_sudo=True, backup='.zion_bak')
    # NOTE: using sed instead of the uncomment() method because I was getting a mysterious sed error
    # (I think the lack of spaces after the comment in the original document was messing up Fabric)
    files.sed(proxy_config_file, '#:log_level: DEBUG', ':log_level: DEBUG', use_sudo=True, backup='.zion_bak')    

def __enable_dns_proxy():
    files.sed(proxy_config_file, ':dns: false', ':dns: true', use_sudo=True, backup='.zion_bak')
    files.sed(proxy_config_file, ':dns_key: /etc/rndc.key', ':dns_key: ' + __get_dns_key_path(), use_sudo=True, backup='.zion_bak')
    # __get_dns_key_path() put the .private and .key
    # chgrp named
    # chmod g+r

def __get_dns_key_path():
    # this assumes that the one key is in a chrooted etc
    return sudo('ls /var/named/chroot/etc/Kf*.key')

def __add_proxy_user_to_groups():
    sudo('usermod -a -G dhcpd foreman-proxy')
    sudo('usermod -a -G named foreman-proxy')

def __setup_dhcp_folder_perms():
    # TODO: this is clearly not right
    # need to figger out more precise perms
    sudo('chmod o=rx /etc/dhcp')
