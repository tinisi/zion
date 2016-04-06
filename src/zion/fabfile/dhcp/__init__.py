
from fabric.api import *
from fabric.contrib import *
from .. zion_config_helper import ZionConfigHelper

@task
def install():
    # install the package
    sudo("yum --assumeyes install dhcp")
    # set up the config file
    __generate_config(env.host)
    # and turn on the service
    sudo('chkconfig --levels 235 dhcpd on')

def __generate_config(current_host):
    # prep the data packet that will be merged with the template
    zch = ZionConfigHelper(env.zion_config_file, current_host)
    data = zch.get_host_conf('dhcp_conf')
    # need to add a couple keys to our dict
    data['routers'] = zch.get_host_conf('gateway')
    # TODO: not sure if this should be a comma list, only one value now, so it doesn't matter
    # TODO: also, this conflates two things, might want to move this to dhcp_conf key,
    # instead of reusing the main name server for the host
    data['domain_name_servers'] = ','.join(zch.get_host_conf('nameservers'))
    # TODO: this should be same as dns_domain, I should add a dhcp specific config
    data['domain_name'] = zch.get_host_conf('full_domain_name')
    # TODO: this happens to work, but should probably be in the dhcp_conf object
    data['next_server'] = zch.get_host_conf('ip')
    # first we have to make the key
    __generate_dhcp_key()
    # then use this method to extract it from the file
    data['secret'] = __get_dhcp_key()
    # and finally, the upload template call to put my file in place
    filename = env.absolute_path_to_zion + '/src/zion/fabfile/dhcp/templates/dhcpd.conf'
    destination = '/etc/dhcp/dhcpd.conf'
    files.upload_template(filename, destination, context=data, use_sudo=True, backup=True)
    sudo('chown root:root ' + destination)
    sudo('chmod g=r ' + destination)

def __generate_dhcp_key():
    # make a key to use in the config
    # NOTE: this requires bind be installed first so we can use the dnssec-keygen utility
    sudo('dnssec-keygen -r /dev/urandom -a HMAC-MD5 -b 512 -n HOST omapi_key')

def __get_dhcp_key():
    # this assumes that the one key we want to use has been generated and
    # and left in current user's home directory
    # get the secret string from the formatted key file
    return sudo("sudo cat Komapi_key.+*.private |grep ^Key|cut -d ' ' -f2-")
