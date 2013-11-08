
# Project Zion #
6/2/2013

## Requirement

Create a completely reproducible process for building a Linux server that uses The Foreman and Puppet to provision virtual machines.

This is *not* meant to be a production ready server for hosting VMs.

I want to be able to provision VMs on a local machine using the exact same versions of all dependencies as my hosting provider and then follow the same process to provision a production VM in their environment.

As long as I use the exact same versions of all major systems this should allow me to have a development environment (at the level of the guest VMs) that closely matches production.

## Dependencies

1. A human with programming skills and motivation.
1. A workstation in which said human would like to program
1. A local network
1. Two computers capable of running CentOS 6.4 64bit
1. One of these machines can be pretty lightweight, and one needs some guts
1. One machine needs a CPU in one of these families:
	* Intel Westmere Family
	* Intel Nehalem Family
	* Intel Penryn Family
	* Intel Conroe Family
	* AMD Opteron G3
	* AMD Opteron G2
	* AMD Opteron G1
1. Project Zion instructions and scripts

## Why Zion?

OK, yeah, it is a Matrix reference, and only sort of tongue in cheek. I am on a quest to own the whole stack! Of course I could just get an account on Rackspace and pay them a few bucks, but that would be too easy. I want to control Zion level too...
