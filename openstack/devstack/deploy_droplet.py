#!/usr/bin/env python
import os  # For running system commands & env vars
import sys  # For command line arguments

# Find your SSH key ID using 'tugboat keys'

# Try to get values from environment variables
try:
    RAM = os.environ['DO_RAM_SIZE']
    IMAGE = os.environ['DO_IMAGE']

except KeyError:
    RAM = "4gb"  # Minimum required RAM to host ~2 instances
    # You can see a list of sizes with "tugboat sizes"
    IMAGE = "14782728"  # Ubuntu 14.04 x64 image
    # You can see a list of images with "tugboat images"


def main(args):
    if args == '':
        args = raw_input("You must name your droplet: ")
        main(args)
    tug_com = "tugboat create " + args + " -s " + RAM + " -i " + IMAGE

    os.system(tug_com)
    # Wait for droplet to become active
    os.system("tugboat wait " + args + " -s")
    # Give it a couple of seconds after it reports activity
    os.system("sleep 8")
    t = os.popen("tugboat droplets | grep " + args)
    t = t.read()
    IP = t[t.find('ip') + 4 : t.find(',')]
    print "IP: " + IP

    command_to_run = "ssh root@" + IP + " 'bash -s' < stack_setup.sh"
    print "Run the following (in order): \n" + command_to_run
    print "ssh root@" + IP
    print "cd /usr/local/src/devstack"
    print "sudo -u stack ./stack.sh"

if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except IndexError:
        name = raw_input("Name your droplet: ")
        main(name)
