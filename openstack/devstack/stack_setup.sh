#!/bin/bash
if [[ $(whoami)  != 'root' ]]; then echo "Run as root"; exit; fi
apt-get update && apt-get install git -y
cd /usr/local/src || echo "/usr/local/src does not exist"
git clone -b stable/newton https://github.com/openstack-dev/devstack.git
cd devstack || exit
sed -i 's/HOST_IP=${HOST_IP:-}/HOST_IP=`dig +short myip.opendns.com @resolver1.opendns.com`/g' stackrc
./tools/create-stack-user.sh
echo "[[local|localrc]]
disable_service n-net
enable_service q-svc
enable_service q-agt
enable_service q-dhcp
enable_service q-l3
enable_service q-meta
enable_service n-cauth

# We don't need no stinkin' Tempest
disable_service tempest

# Enable the ceilometer services
enable_service ceilometer-acompute,ceilometer-acentral,ceilometer-collector,ceilometer-api

#Configure events for both Stacktach and custom listener
notification_driver=nova.openstack.common.notifier.rpc_notifier
notification_topics=notifications,monitor
notify_on_state_change=vm_and_task_state
notify_on_any_change=True
instance_usage_audit=True
instance_usage_audit_period=hour

# Password configuration below
ADMIN_PASSWORD=devstack
DATABASE_PASSWORD=devstack
RABBIT_PASSWORD=devstack
SERVICE_PASSWORD=devstack
SERVICE_TOKEN=a682f596-76f3-11e3-b3b2-e716f9080d50

HOST_IP=`dig +short myip.opendns.com @resolver1.opendns.com`
" >> local.conf

chown -R stack:stack .
