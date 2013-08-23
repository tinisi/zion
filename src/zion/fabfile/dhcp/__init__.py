
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

def __generate_config():
    # prep the data packet that will be merged with the template
    zch = ZionConfigHelper(env.zion_config_file, current_host)
    data = zch.get_host_conf('dhcp_conf')
    # need to add a couple keys to our dict
    data['routers'] = zch.get_host_conf('gateway')
    # TODO: not sure if this should be a comma list, only one value now, so it doesn't matter
    data['domain_name_servers'] = ','.join(zch.get_host_conf('dns_servers'))
    data['domain_name'] = zch.get_host_conf('domain_name')
    data['next_server'] = zch.get_host_conf('ip')
    # this one needs to be made
    data['secret'] = __get_dhcp_key()
    # and finally, the upload template call to put my file in place
    filename = env.absolute_path_to_zion + '/src/zion/fabfile/dhcp/templates/dhcpd.conf'
    destination = '/etc/dhcp/dhcpd.conf'
    files.upload_template(filename, destination, context=data, use_sudo=True, backup=True)
    sudo('chown root:root /etc/dhcp/dhcpd.conf')
    sudo('chmod g=r /etc/dhcp/dhcpd.conf')

def __get_dhcp_key():
    # make a key to use in the config
    # NOTE: this requires bind be installedd first so we can use the dnssec-keygen utility
    sudo('dnssec-keygen -r /dev/urandom -a HMAC-MD5 -b 512 -n HOST omapi_key')
    # get the secret string from the formatted key file
    return sudo("sudo cat Komapi_key.+*.private |grep ^Key|cut -d ' ' -f2-")