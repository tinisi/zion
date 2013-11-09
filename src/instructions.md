
# Instructions #

This is the master check list for installing Project Zion.

The default instructions for this project require two "bare metal" computers, one for The Foreman (and named and dhcpd) which will be used to monitor and provison virtual machines, and another for oVirt which will be the actual host for the VMs. The Foreman is just a ruby web application, and that machine will also need to run bind and dhcpd.

Only the oVirt machine needs much in the way or horsepower. If you have one fairly new and powerful computer, it might be possible to run The Foreman on a VM, not covering the details of that architecture here.

Since this is really a basement "do it yourself" project, I am not going to get too detailed on the hardware requirements. I'll specify the range of what I am using and you'll have to check The Foreman and oVirt web sites for more details.

*DISCLAIMER: As of this writing, I am 99% sure this is all working correctly, however I have NOT managed to provision a new VM from The Foreman using oVirt as a "Compute Resource." The Foreman appears to be able to call the oVirt API, and I can see VMs I have "manually" created using oVirt alone, but my initial tests using the default Puppet provisioning templates are not working for me. I am hoping I just need to learn more about these Puppet scripts and I'll be golden.*

### The Foreman machine - hardware requirements

1. You probably need at least 1GB of RAM
1. 500GB of hard drive should be enough
1. Pretty much any machine that can run 64 bit CentOS should work
1. This machine does not need to have a CPU that supports virtualization

### oVirt machine - hardware requirements

1. You probably need at least 4GB of RAM
1. At least 1TB or more hard drive, I have 2TB so plenty of room for VM images and storage
1. Go to your BIOS editing app (usually holding down F12 should get you there)
	* Make sure that virtualization capability is active
	* Also verify that you have a CPU in one of these families:
		* Intel Westmere Family
		* Intel Nehalem Family
		* Intel Penryn Family
		* Intel Conroe Family
		* AMD Opteron G3
		* AMD Opteron G2
		* AMD Opteron G1

### Before you get started

1. Get your servers physically connected to your local network
1. Pick an IP and hostname for both servers
1. Take note of some other name server you can use on The Foreman box during install, and to forward requests to after your local name server is up
1. Add an entry to your workstation's hosts file for The Foreman box, you can provide name service for the oVirt machine on The Foreman box once it is up
1. Pick a password for root on both machines

## The Foreman machine and the oVirt machine

### Install CentOS 6.4 64bit Minimal from CD-ROM

1. Download CentOS-6.4-x86_64-minimal.iso (on 5/13/2013 when I downloaded it, the checksum was: 4a5fa01c81cc300f4729136e28ebe600)
1. Burn it to a CD
1. Put it in the CD drive, and hold down F12 to pick the CD ROM as boot device (might be different for your BIOS)
1. Boot from the CD drive one way or another
1. Proceed with minimal install with all default settings or obvious common sense choices except as noted below
1. Enter your hostname when prompted
1. On that same screen, click "Configure Network" button
1. Add the appropriate fixed IP that matches your hostname
1. Specify a DNS server you can get to from your local network
1. Check the box with label "Connect Automatically" (this will make network available on boot)
1. Fill in the rest of the usual network stuff
1. Proceed with the install
1. Choose to use all space (I assume this is NOT a dual boot computer)
1. Proceed with the install

### Verify you can log in from your workstation as root

1. Run:
	ssh {your.hostname} -l root
1. Accept the key (unless you suspect Ninjas in have already compromised Project Zion!!!)

### Run the pre-install Fabric Script

cd src/zion  
fab pre_install --hosts={your.hostname} -u root

This step must be run as root. Once it is complete you should have a user with sudo privs.

_(Ummm, you do have at least one user in your config.json for each server that will be added to the group wheel, right?)_

### Verify you can log in from your workstation as a user with sudo

1. Run:
	ssh {your.hostname} -l {a user in the group wheel}
1. Accept the key (unless you suspect...)
1. Run:
	sudo ls /etc
1. Read the disclaimer with the reference to Spider Man
1. Enter the password and hopefully you'll see a list of all the files in etc

## The Foreman machine

### Run the main Fabric Action to install The Foreman and friends

cd src/zion  
fab install_foreman --hosts={your.foreman.hostname} -u {a user in the group wheel}  
*(this is pretty much hands free)*

### On your workstation

1. Comment out or delete the nosts file record you made for temporary name resolution for your The Foreman machine
1. Set the IP address of The Foreman machine as your name server
1. Verify you can get to the hostname of your The Foreman machine with your web browser, your new server issued its own SSL certificate, so depending on your browser you'll have to accept the un-trusted certificate
1. You should see a nicely formatted log in screen, verify thast you can log in with user "admin" and password "changeme"
1. I would stop there and proceed with the oVirt install and set up
1. Note that you now have a new dhcp server on your local network, which likely means you have two
1. You may want to turn off your other dhcp server (on your DSL modem perhaps,) of course there are other ways to set up your local network, like making a separate subnet for all this, for now I am going to let this damn project take over our home network

## The oVirt machine

### Run the main Fabric Action to install oVirt all in one flavor

*NOTE: oVirt all in one install requires the ability to ssh as root from the server back to the same server. You might want to check that the name server on The Foreman box works, both the host and reverse record need to be there for this install to work. If you are using host files for resolution of the oVirt machines name, you should stop here and edit the hosts file on the server now.*

cd src/zion  
fab install_ovirt --hosts={your.ovirt.hostname} -u {a user in the group wheel}  
*(the last stage of this is an interactive installer, you can pretty much accept defaults)*  
*(I tried to make this non-interactive, set up an answer file, didn't work, don't ask...)*  

## oVirt and The Foreman set up

### On your workstation

1. Verify you can get to the hostname of your oVirt machine with your web browser, this server also issued its own SSL certificate, so depending on your browser you'll have to accept the un-trusted certificate
1. You should be on a nicely formatted page branded with oVirt stuff, click on the Administrative Pages link to get started
1. This is the best quick start article I have found for next steps. It is written with Fedora as a target, but everything about using the web app to make new VMs is of course the same on CentOS. I followed steps 5, 6 and 7.
[http://community.redhat.com/up-and-running-with-ovirt-3-3](http://community.redhat.com/up-and-running-with-ovirt-3-3/)
1. Once you have the minimum stuff set up on oVirt, a host, a data center and storage you can theoretically use The Foreman for everything else
1. This main site for The Foreman:  
[http://www.theforeman.org/](http://www.theforeman.org/)
1. As I said in the disclaimer, I have not managed to provision a new machine from The Foreman, I did manage to make a new host using oVirt, in short this requires uploading an installer ISO image and then doing the operating system install step by step "manually" using a console
1. I am on a Mac workstation and the Console link in the oVIrt admin area just downloads a .vv file. Apparently as of this writing the web based Spice or VNC console supported by  oVirt is an optional experimental feature, and I haven't gotten it working yet. I managed to get a connection by downloading an app called Chicken of the VNC (link below) and then opening up that .vv file in a text editor and getting the display port from the file and entering it into Chicken.  
[http://sourceforge.net/projects/chicken/](http://sourceforge.net/projects/chicken/)
1. You will have to either use a hosts file or set up a DNS entry for any new VMs you make using the oVirt interface, notice that once your The Foreman machine is set up, you shuuld be able to add new host entries to the config key "bind_conf" hosts list and re-run JUST the action configure_hosts
1. Although I was NOT able to provision a new machine using The Foreman, I did get it to see all the VMs I created "manually" using the oVirt once I set up the "Compute Resource" and the web based console biult into The Foreman worked great, so that's cool ;-)
