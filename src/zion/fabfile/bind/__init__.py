
from fabric.api import *
from fabric.contrib import *
from .. zion_config_helper import ZionConfigHelper
from datetime import date

# we need these in several methods below, making it s package level var
# the folder where the foreman key lives, since the name will be different
foreman_key_path = '/var/named/chroot/etc'
template_dir = env.absolute_path_to_zion + '/src/zion/fabfile/bind/templates'

host_record = '%(host_name)s  IN  A  %(ip)s\n'
reverse_record = '%(host_ip)s  IN  PTR  %(full_domain_name)s.\n'

@task
def install():
    # bind and some additions and utils we'll need
    sudo("yum --assumeyes install bind-utils")
    sudo("yum --assumeyes install bind-libs")
    sudo("yum --assumeyes install bind")
    sudo("yum --assumeyes install bind-chroot")
    # set it to start automagically
    sudo('chkconfig --level 35 named on')
    sudo('service named start')
    # we need to stop it now or the conf file will be locked
    sudo('service named stop')

@task
def generate_foreman_dns_key():
    # NOTE: using run here instead of sudo() because otherwise this command echo's sudo password (Fabric bug?)
    run('sudo dnssec-keygen  -K ' + foreman_key_path + ' -a HMAC-MD5 -b 128 -n HOST foreman')

@task
def configure_server():
    '''
    This sets up the server, with no files for host and reverse pointers.

    These are the files we need to set up:

    in this folder:
        /var/named/chroot/etc
    these files:
        foreman.key
        name.conf
    '''
    current_host = env.host

    # being a little lazy, all the config share the same merge dict
    data = __get_server_config_dict(current_host)
    
    # the files that just live in the chrooted etc
    destination_dir_etc = '/var/named/chroot/etc'

    # for all of these, I don't need to generate a file name, and it can be same local and on server
    foreman_file_name = 'foreman.key'    
    foreman_template_full_path = template_dir + '/' + foreman_file_name
    foreman_full_path = destination_dir_etc + '/' + foreman_file_name
    files.upload_template(foreman_template_full_path, foreman_full_path, context=data, use_sudo=True, backup=True)
    # need to make this readable for foreman process
    sudo('chmod o+r ' + foreman_full_path)

    named_file_name = 'named.conf'    
    named_template_full_path = template_dir + '/' + named_file_name
    named_full_path = destination_dir_etc + '/' + named_file_name
    files.upload_template(named_template_full_path, named_full_path, context=data, use_sudo=True, backup=True)

@task
def configure_hosts():
    '''
    This method can safely be used after initial install
    to update the hosts managed by this server,
    picking up whatever is in the current config file.

    These are the files we need to set up:

    in this folder:
        /var/named/chroot/etc/named
    these files:
        ip_sub_dot_db (for example 192.168.0.db)
        domain.tld_dot_db (for example tinisi.com.db)
    '''
    current_host = env.host

    # the files for our chroot'ed etc/names
    destination_dir_named = '/var/named/chroot/etc/named'

    data = __get_host_config_dict(current_host)

    ip_sub_template_full_path = template_dir + '/ip_sub_dot_db'
    ip_sub_file_name = data['ip_sub'] + '.db'
    ip_sub_full_path = destination_dir_named + '/' + ip_sub_file_name
    files.upload_template(ip_sub_template_full_path, ip_sub_full_path, context=data, use_sudo=True, backup=True)

    domain_template_full_path = template_dir + '/domain.tld_dot_db'
    domain_file_name = data['dns_domain'] + '.db'
    domain_full_path = destination_dir_named + '/' + domain_file_name
    files.upload_template(domain_template_full_path, domain_full_path, context=data, use_sudo=True, backup=True)

@task
def restart_named():
    with settings(warn_only=True):
        sudo('service named restart')

@task
def replace_resolv():
    zch = ZionConfigHelper(env.zion_config_file, env.host)
    resolv_file_template_full_path = env.absolute_path_to_zion + '/src/zion/fabfile/bind/templates/resolv.conf'
    remote_resolv_file = '/etc/resolv.conf'
    # TODO: make this handle one to n name servers in the list,
    # for now randomly using the first
    data = { "nameserver": zch.get_host_conf('nameservers')[0] }
    files.upload_template(resolv_file_template_full_path, remote_resolv_file, context=data, use_sudo=True, backup=True)

def __get_server_config_dict(current_host):
    zch = ZionConfigHelper(env.zion_config_file, current_host)
    return {
        "dns_admin_email":__get_dns_admin_email(),
        "foreman_dns_key":__get_foreman_dns_key(),
        "reverse_ip_sub":__get_reverse_ip_sub(current_host),
        "ip_sub": zch.get_host_conf('bind_conf')['subnet'],
        "forwarders": ','.join(zch.get_host_conf('bind_conf')['forwarders']),
        "dns_domain": zch.get_host_conf('bind_conf')['dns_domain']
    }

def __get_host_config_dict(current_host):
    zch = ZionConfigHelper(env.zion_config_file, current_host)
    # need to add some calculated values to each of thes
    hosts = zch.get_host_conf('bind_conf')['hosts']
    # mutate the config list of host dicts, with computed values for other keys,
    # and create a single string for each
    host_records = ''
    reverse_records = ''
    for host in hosts:
        host['full_domain_name'] = host['host_name'] + '.' + zch.get_host_conf('bind_conf')['dns_domain']
        host['ip'] = zch.get_host_conf('bind_conf')['subnet'] + '.' + host['host_ip']
        host_records  = host_records + host_record % host
        reverse_records = reverse_records + reverse_record % host        
    # start with the server config dict
    hosts_config_dict = __get_server_config_dict(current_host)
    # add the two strings we just made with host and reverse records for one to n hosts
    hosts_config_dict['host_records'] = host_records
    hosts_config_dict['reverse_records'] = reverse_records
    hosts_config_dict['dns_serial_no'] = __get_dns_serial_no()
    hosts_config_dict['full_domain_name'] = current_host
    hosts_config_dict['nameserver_hostname'] = __get_nameserver_hostname(current_host)

    return hosts_config_dict

def __get_foreman_dns_key():
    secret = sudo("cat " + foreman_key_path + "/Kforeman.+*.private |grep ^Key|cut -d ' ' -f2-")
    return secret

def __get_dns_admin_email():
    zch = ZionConfigHelper(env.zion_config_file, env.host)
    admin_email = zch.get_host_conf('admin_email')
    # just replace the @ with a dot to make the odd bind config format
    return admin_email.replace('@','.')

def __get_reverse_ip_sub(current_host):
    zch = ZionConfigHelper(env.zion_config_file, current_host)
    subnet = zch.get_host_conf('bind_conf')['subnet']
    # convert it into a list
    subnet_list = subnet.split('.')
    # and flip it
    subnet_list.reverse()
    # join the results back to a dot delimited string
    return '.'.join(subnet_list)

def __get_dns_serial_no():
    today = date.today()
    return today.strftime("%Y%m%d01")

def __get_nameserver_hostname(current_host):
    # just return the first item
    current_host_list = current_host.split('.')
    # and the first item is what we need
    return current_host_list.pop(0)
