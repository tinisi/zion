
# Instructions #

This is the master check list for installing Project Zion

### Before you get started

1. Pick an IP and hostname for your server
1. Get your server physically connected to your local network
1. Add an entry to your hosts file if your hostname isn't being provided by a "real" DNS record
1. Pick a password for root

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

**You should now be able to log on locally as root.**

### Verify you can log in from your workstation

1. Run:
	ssh {your.hostname} -l root
1. Accept the key (unless you suspect Ninjas in have already compromised Project Zion!!!)

### Run the pre-install Fabric Script

fab pre_install --hosts={your.hostname} -u root

This step must be run as root. Once it is complete you will have a user with sudo privs.

Ummm, you do have at least one user in your config.json that has been added to the group wheel, right?

### Verify you can log in from your workstation as a user with sudo

1. Run:
	ssh {your.hostname} -l {a user in the group wheel}
1. Accept the key (unless you suspect...)
1. Run:
	sudo ls /etc
1. Read the disclaimer with the reference to Spider Man
1. Enter the password and hopefully you'll see a list of all the files in etc

### Run the main Fabric Script

fab install --hosts={your.hostname} -u {a user in the group wheel}
