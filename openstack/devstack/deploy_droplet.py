#!/usr/bin/env python
import os  # For running system commands
import sys  # For command line arguments

# Find your SSH key ID using 'tugboat keys'


def main(args):
    if args == '':
        args = raw_input("You must name your droplet: ")
        main(args)
    tug_com = "tugboat create " + args + " -s 4gb -i 14782728"
    # -s 4gb is the instance RAM size, -i 14782728 is the Ubuntu 14.04 x64 image
    # You can see a list of images with "tugboat images"
    os.system(tug_com)
    # Wait for droplet to become active
    os.system("tugboat wait " + args + " -s")
    # Give it a couple of seconds after it reports activity
    os.system("sleep 8")
    t = os.popen("tugboat droplets | grep " + args)
    t = t.read()
    IP = t[t.find('ip') + 4 : t.find(',')] # Flake8 complains, but the space is for clarity
    print "IP: " + IP

    command_to_run = "ssh root@" + IP + " 'bash -s' < stack_setup.sh"
    print "Run the following (in order): \n" + command_to_run
    print "ssh root@" + IP
    print "cd /usr/local/src/devstack && su stack"
    print "./stack.sh"

if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except IndexError:
        name = raw_input("Name your droplet: ")
        main(name)
