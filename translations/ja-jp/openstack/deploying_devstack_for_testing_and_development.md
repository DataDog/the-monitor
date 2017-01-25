## What is DevStack?
This article will show you how to get a full OpenStack stack running in just two commands using [DevStack]. DevStack is not intended to be a general OpenStack installer, but is a great option for dev/test.

Because it was made for development and testing, DevStack takes most of the decision making [out of the installation process][decisions], presenting you with a default installation environment that Just Works&trade;.

## Motivation
Although DevStack _does_ make it easier to get an OpenStack environment up and running, it is not without its pain points. In my case, I needed an environment that I could remotely deploy and tear down daily, using a cloud provider to host my installation. After spending a sizable chunk of time over the course of a few days, I realized I could cut down my redeployment times considerably with a set of scripts that could customize my installation. 

With some additional tooling, I was able to build a nearly fully automated solution that has cut deployment times down and ensures a completely reproducible build by other members of my team.

## Prerequisites
The DevStack installation target should be based on an Ubuntu or Debian image. If you are deploying to a cloud environment, we have included additional instructions for deploying to either [DigitalOcean](#do-setup) or [AWS](#aws-setup) as the hosting provider.

Perhaps the fastest way to get a one-off deployment working quickly is to create a droplet (at least 4GB of RAM recommended) from the DigitalOcean web interface and follow the [vanilla VM setup](#vanilla-setup) steps below. The same steps can be used to host your DevStack deployment on a different platform. 

Choose your setup from the following:  

- [Vanilla VM setup](#vanilla-setup)  
- [AWS setup](#aws-setup)  
- [DigitalOcean setup with Tugboat](#do-setup)  

No matter where you host your deployment, it is recommended that you read through [vanilla VM setup](#vanilla-setup) so you have an idea of the changes being made to your system.

<div class="anchor" id="vanilla-setup" />

## Vanilla VM setup
The DevStack documentation [strongly suggests][virtual-caveat] using a disposable virtual machine to host the project, as DevStack makes a considerable number of changes to its host system.

Once you [download][stack_setup] the _stack\_setup.sh_ script described below, getting up DevStack can be done in two commands:  

```
./stack_setup.sh
sudo -iu stack bash /usr/local/src/devstack/stack.sh
```

### stack_setup.sh
The _stack\_setup.sh_ [script][stack_setup] prepares the local environment for DevStack installation. You can download the script with `wget`: `wget https://raw.githubusercontent.com/DataDog/the-monitor/master/openstack/devstack/stack_setup.sh`

After downloading the script, don't forget to make it executable with `chmod +x stack_setup.sh`

Before _stack\_setup.sh_ can do anything interesting, it performs some housekeeping: updating apt repositories, and installing [git]. This step is especially necessary for DigitalOcean users, as the default Ubuntu install does not have git and usually has an outdated package list.

Next, the script clones the Kilo release of DevStack into `/usr/local/src/devstack` and creates a **stack** user with the bundled _create-stack-user.sh_ script from the **tools** directory. Creating a separate user to run DevStack is necessary, as the installation scripts will [refuse to run as root][sanity-checks]. 

After creating the new user, the script creates a **local.conf** file, used to configure your deployment. It sets up and configures OpenStack notifications so you can view OpenStack events immediately, using the popular [StackTach] tool or [a custom listener][custom-listener]. 

Most importantly, it sets defaults for the admin, database, [RabbitMQ], and Horizon passwords, as well as the service token to bootstrap Keystone. The DevStack documentation recommends [pre-set][recommendations] passwords to simplify the installation process. If you would like to change the defaults, modify the password options in the _stack\_setup.sh_ script. The default password is: `devstack`.

Finally, the script changes ownership of all files in the **devstack** directory (and subdirectories) to the **stack** user. 

<div class="anchor" id="stack-script" />

### stack.sh
The final step in deploying DevStack is running the _stack.sh_ script as the **stack** user. This script handles the actual deployment of DevStack. It is [highly recommended][stack.sh] that you carefully read the script contents to better understand the changes OpenStack will make to your system. No user interaction should be needed until the script finishes.

<div class="anchor" id="aws-setup" />

## AWS deployment
Deploying on AWS requires you to manually create an EC2 instance to host your deployment, as well as open up several ports for OpenStack to use.

[![Deploy DevStack on AWS - Instance Size choice][instance-size]][instance-size]

The minimum instance size to host DevStack is **m4.large**. Although smaller instance types _could_ host DevStack, over the course of our tests we found the network performance of smaller instance sizes to be inadequate. We also used the **Ubuntu Server 14.04 LTS (HVM), SSD Volume Type** image for our test deployment.

To ensure access to the outside world, assign a public IP address to your instance like in the screenshot below:
![Deploy DevStack on AWS - Assign Public IP][pub-ip]

Last but not least, you must open up access to a number of ports in order for DevStack to successfully install. You _could_ just open up your instance to all internet traffic, but configuring a security group is a good idea if you'd like to restrict outside access to your deployment.

Create a security group with the following ports open for ingress: 22, 80, 443, 3306, 5000, 5672, 5900 - 5999, 6000 - 6002, 6080 - 6082, 8000, 8003, 8080, 8386, 8773 - 8777, 9191, 9292, 9696, 35357. Refer to the [OpenStack documentation][port-doc] for more information on OpenStack service ports.
[![Deploy DevStack on AWS - Configure Port Access][http-port]][http-port]

Once launched, open up a terminal on your local machine. Use [scp] to copy the `stack_setup.sh` script to your EC2 instance: `scp stack_setup.sh ubuntu@<your instance IP>:~`. The previous command will upload the setup script to `/home/ubuntu/setup_script.sh` on your instance.

Next, `ssh` into your instance and run the script as root:

```
ssh ubuntu@<your instance IP>  
ubuntu@<your instance IP>:~$ sudo ./stack_setup.sh
```
Once the script executes, you will have a copy of the DevStack project in `/usr/local/src/devstack` and a new **stack** user.

Then, you just need to [execute](#stack-script) `stack.sh` as the **stack** user.

```
sudo -iu stack bash /usr/local/src/devstack/stack.sh
```

The script should take ~20 minutes to execute. When it is finished, continue on to [Success](#success) to get started with your new deployment.

<div class="anchor" id="do-setup" />

## DigitalOcean deployment with Tugboat
If you have a DigitalOcean droplet running, you can simply run the [vanilla VM setup](#vanilla-setup) steps to install OpenStack. 

If you want to automate the _entire_ OpenStack setup, including provisioning machines, you can do that on DigitalOcean using [Tugboat][tugboat]. If you plan on doing a lot of OpenStack testing, chances are you'll break some things along the way. With Tugboat, you can quickly and easily deploy and tear down your stack, so you have a fresh deployment to hack on daily. The next section of this article explains how to use Tugboat to create and setup a droplet running DevStack.
### Tugboat configuration
[Tugboat][tugboat] is a handy package that allows you to manage your DigitalOcean account from the command line. We will take advantage of its powerful features to create an appropriately sized droplet to host our DevStack deployment.

Tugboat requires Ruby 1.9 or higher. Check for a compatible version with `ruby -v`. Once you've upgraded Ruby or verified your version, installation is a single command: `gem install tugboat`. 

Tugboat needs an authentication token from DigitalOcean—you can grab yours [here][do-auth]. You can only view your token once upon creation, so make sure you store it somewhere as you will need it in the next step.

With authentication token in hand, run `tugboat authorize`. You should see a series of prompts, reproduced below. You need only to enter your access token and a path to an SSH key; the defaults should suffice for the rest. 

```
user@testing:~$ tugboat authorize
Note: You can get your Access Token from https://cloud.digitalocean.com/settings/tokens/new

Enter your access token: <your access token>
Enter your SSH key path (optional, defaults to ~/.ssh/id_rsa):
Enter your SSH user (optional, defaults to root):
Enter your SSH port number (optional, defaults to 22):

To retrieve region, image, size and key ID's, you can use the corresponding tugboat command, such as `tugboat images`.
Defaults can be changed at any time in your ~/.tugboat configuration file.

Enter your default region (optional, defaults to nyc1):
Enter your default image ID or image slug (optional, defaults to ubuntu-14-04-x64):
Enter your default size (optional, defaults to 512mb)):
Enter your default ssh key IDs (optional, defaults to none, comma separated string):
Enter your default for private networking (optional, defaults to false):
Enter your default for enabling backups (optional, defaults to false):

Authentication with DigitalOcean was successful!
```
If you see **"Authentication with DigitalOcean was successful!"**, you're good to go.

After authenticating, make sure to set a default SSH key. You can get a list of your SSH key IDs with `tugboat keys`.

```
Name: tutum-70159d08-bfe8-44de-b0a1-4ce0d2dd9682, (id: 1529470), fingerprint: c4:b0:f2:b0:a7:9f:89:d0:c5:ae:b5:5c:f3:de:a0:69
Name: DO-webserver, (id: 1532126), fingerprint: 37:75:95:7d:93:4f:e0:fd:01:4a:ba:e4:2e:be:6d:c7
```
For example, if you wanted to use the DO-webserver key listed in the output above, open up tugboat's configuration file at **~/.tugboat** and change the value of `ssh_key` to `1532126`.

### deploy_droplet.py
_deploy\_droplet.py_ is a Python [script][deploy_droplet-script] that creates an appropriately sized droplet on DigitalOcean to host DevStack. You need only to provide a name for your droplet, which you can supply either as a command line parameter or as input at the prompt.
You can download the script with the following command: `wget https://raw.githubusercontent.com/DataDog/the-monitor/master/openstack/devstack/deploy_droplet.py`

Once downloaded, make the script executable and then run deploy_droplet.py  

```
chmod +x deploy_droplet.py
./deploy_droplet.py <your_droplet_name>
```

which should produce output resembling the following:

```
$ ./deploy_droplet.py devstack-test
Queueing creation of droplet 'devstack-test'...Droplet created!
Droplet fuzzy name provided. Finding droplet ID...done, 9591284 (devstack-test)
Waiting for droplet to become active................done (30s)
IP: 107.170.165.252
Run the following (in order):
ssh root@107.170.165.252 'bash -s' < stack_setup.sh
ssh root@107.170.165.252
sudo -iu stack bash /usr/local/src/devstack/stack.sh
```

As you can see from the above output, the script creates the droplet, returns its IP address, and lists a series of commands to execute in order on the newly created instance. Simply copy-paste the commands to set up OpenStack. If you'd like more information on the work performed in each step of the script, jump to [vanilla VM setup](#vanilla-setup). Otherwise, [skip ahead](#success) to start using your new deployment.

<div class="anchor" id="success" />

## Success

Wherever you chose to deploy DevStack, once setup is complete you should be greeted with output like the following:

```
Horizon is now available at http://107.170.165.252/
Keystone is serving at http://107.170.165.252:5000/
The default users are: admin and demo
The password: devstack
```
To access statistics about your deployment, including number of instances and quota usage, navigate to the Horizon address listed in the output.

![Deploy DevStack Horizon Dash Screen][horizon-dash]
_Log in as the **admin** user with password: **devstack**_

## Conclusion
On average, you should expect the following approximate execution times for the various steps listed in this post:  
- _deploy\_stack.py_: ~20-60 seconds
- _stack\_setup.sh_: ~1 minute  
- _stack.sh_: ~16-26 minutes  
- **Approximate total execution time**: < 30 minutes  

Of course, your actual installation time will vary depending on your network speed.

If you've been following along on your own machine, you should now have a DevStack deployment ready for use. To learn how to monitor an OpenStack deployment, check out our [three-part series][part 1].

[custom-listener]: https://www.datadoghq.com/blog/collecting-metrics-notifications-openstack-nova/#Notifications

[decisions]: http://docs.openstack.org/developer/devstack/overview.html



[deploy_droplet-script]: https://raw.githubusercontent.com/DataDog/the-monitor/master/openstack/devstack/deploy_droplet.py
[stack_setup]: https://raw.githubusercontent.com/DataDog/the-monitor/master/openstack/devstack/stack_setup.sh



[horizon-dash]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-OpenStack/devstack/horizon-dash.png

[instance-size]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-OpenStack/devstack/instance-size.png

[http-port]:  https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-OpenStack/devstack/devstack-ports1.png

[pub-ip]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-OpenStack/devstack/public-ip.png


[DevStack]: https://wiki.openstack.org/wiki/DevStack

[do-auth]: https://cloud.digitalocean.com/settings/applications

[git]: https://git-scm.com/about

[GitHub]: https://github.com/openstack

[port-doc]: http://docs.openstack.org/kilo/config-reference/content/firewalls-default-ports.html

[RabbitMQ]: https://www.datadoghq.com/blog/openstack-monitoring-nova/#rabbitmq-metrics

[recommendations]: https://github.com/openstack-dev/devstack/blob/master/doc/source/configuration.rst#minimal-configuration

[sanity-checks]: http://docs.openstack.org/developer/devstack/stack.sh.html#configuration

[scp]: http://linux.die.net/man/1/scp

[stack.sh]: http://docs.openstack.org/developer/devstack/stack.sh.html

[StackTach]: https://stacktach.readthedocs.org/

[tugboat]: https://github.com/pearkes/tugboat

[virtual-caveat]: https://github.com/openstack-dev/devstack#devstack-execution-environment



[part 1]: https://www.datadoghq.com/blog/openstack-monitoring-nova/
[part 2]: https://www.datadoghq.com/blog/collecting-metrics-notifications-openstack-nova/
[part 3]: https://www.datadoghq.com/blog/openstack-monitoring-datadog/
