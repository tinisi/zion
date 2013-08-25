
from fabric.api import *
from fabric.contrib import *
from .. zion_config_helper import ZionConfigHelper

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
    # set up all the configs
    __generate_configs(env.host)
    # and re-start it!
    sudo('service named restart')

def __generate_configs(current_host):
    '''
    These are the files we need to set up:

    in this folder:
        /var/named/chroot/etc/named
    these files:
        ip_sub_dot_db (for example 192.168.0.db)
        domain.tld_dot_db (for example tinisi.com.db)

    in this folder:
        /var/named/chroot/etc
    these files:
        foreman.key
        name.conf
        named.rfc1912.zones
    '''
    # set up some useful shared vars
    template_dir = env.absolute_path_to_zion + '/src/zion/fabfile/bind/templates'
    # being a little lazy, all the config share the same merge dict
    data = __get_config_dict(current_host)

    # first we'll deal with the files for our chroot'ed etc/names
    destination_dir_named = '/var/named/chroot/etc/named'
    
    ip_sub_template_full_path = template_dir + '/ip_sub_dot_db'
    ip_sub_file_name = data['ip_sub'] + '.db'
    ip_sub_full_path = destination_dir_named + '/' + ip_sub_file_name
    files.upload_template(ip_sub_template_full_path, ip_sub_full_path, context=data, use_sudo=True, backup=True)
    
    domain_template_full_path = template_dir + '/domain.tld_dot_db'
    domain_file_name = data['full_domain_name'] + '.db'
    domain_full_path = destination_dir_named + '/' + domain_file_name
    files.upload_template(domain_template_full_path, domain_full_path, context=data, use_sudo=True, backup=True)
    
    # and the files that just live in the chrooted etc
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

def __get_config_dict(current_host):
    zch = ZionConfigHelper(env.zion_config_file, current_host)
    return {
        "dns_admin_email":__get_dns_admin_email(),
        "foreman_dns_key":__get_foreman_dns_key(),
        "dns_hostname":__get_dns_hostname(current_host),
        "reverse_ip_sub":__get_reverse_ip_sub(current_host),
        "ip_sub":__get_ip_sub(current_host),
        "dns_domain_name":__get_dns_domain_name(current_host),
        "domain_sub": __get_domain_sub(current_host),
        "full_domain_name": zch.get_host_conf('full_domain_name'),
        "ip": zch.get_host_conf('ip')
    }

def __get_foreman_dns_key():
    # dir to put the key in
    key_path = '/var/named/chroot/etc'
    # TODO: using run here instead of sudo() because otherwise this command echo's sudo password (bug?)
    run('sudo dnssec-keygen  -K ' + key_path + ' -a HMAC-MD5 -b 128 -n HOST foreman')
    # sudo('dnssec-keygen  -K ' + key_path + ' -a HMAC-MD5 -b 128 -n HOST foreman')
    secret = sudo("cat " + key_path + "/Kforeman.+*.private |grep ^Key|cut -d ' ' -f2-")
    return secret

def __get_dns_admin_email():
    zch = ZionConfigHelper(env.zion_config_file, env.host)
    admin_email = zch.get_host_conf('admin_email')
    # just replace the @ with a dot to make the odd bind config format
    return admin_email.replace('@','.')

def __get_dns_domain_name(current_host):
    zch = ZionConfigHelper(env.zion_config_file, current_host)
    fqdn = zch.get_host_conf('full_domain_name')
    # convert it into a list
    fqdn_list = fqdn.split('.')
    # remove the first item
    fqdn_list.pop(0)
    # join the results back to a dot delimited string
    return '.'.join(fqdn_list)

def __get_dns_hostname(current_host):
    zch = ZionConfigHelper(env.zion_config_file, current_host)
    fqdn = zch.get_host_conf('full_domain_name')
    # convert it into a list
    fqdn_list = fqdn.split('.')
    # return the first item
    return fqdn_list[0]

def __get_ip_sub(current_host):
    zch = ZionConfigHelper(env.zion_config_file, current_host)
    ip = zch.get_host_conf('ip')
    # convert it into a list
    ip_list = ip.split('.')
    # remove the last item
    ip_list.pop()
    # join the results back to a dot delimited string
    return '.'.join(ip_list)

def __get_reverse_ip_sub(current_host):
    zch = ZionConfigHelper(env.zion_config_file, current_host)
    ip = zch.get_host_conf('ip')
    # convert it into a list
    ip_list = ip.split('.')
    # remove the last item
    ip_list.pop()
    # and flip it
    ip_list.reverse()
    # join the results back to a dot delimited string
    return '.'.join(ip_list)

def __get_domain_sub(current_host):
    zch = ZionConfigHelper(env.zion_config_file, current_host)
    fqdn = zch.get_host_conf('full_domain_name')
    # convert it into a list
    fqdn_list = fqdn.split('.')
    # remove the last item
    fqdn_list.pop()
    # join the results back to a dot delimited string
    return '.'.join(fqdn_list)
