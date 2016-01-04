# Collecting monitoring data from OpenStack Nova
_This post is Part 2 of a 3-part series on monitoring OpenStack's computation module, Nova. [Part 1] explores the key metrics available in Nova, and [Part 3] shows you how to monitor OpenStack with Datadog._

## Digging into Nova  
OpenStack Nova offers a variety of sources from which you can collect operational data for monitoring. To get the complete picture of your OpenStack deployment, you will need to combine data collected from various channels.  

In this post, we will show you how to get information from each of the following categories:  

- [Nova metrics, including hypervisor, server, and tenant metrics](#NovaMetrics)  
- [RabbitMQ metrics](#RabbitMQ)  
- [Notifications](#Notifications)  
- [Service and process checks](#APIChecks)  

 <div class="anchor" id="NovaMetrics" />

### Collecting Nova metrics  
_Metrics collection_ is done at the source, usually by a [monitoring agent](https://github.com/DataDog/dd-agent) running on the node in question. The agent collects chronologically ordered data points in a timeseries. Collection of timeseries metrics over extended periods gives you the historical context needed to identify what changed, how it changed, and potential causes of the change. Historical baselines are crucial: It is hard to know if something is broken if you don't know what a healthy system looks like. 

Although OpenStack now ships with its own metering module ([Ceilometer]), it was [not built for monitoring][leveraging-ceilometer]. Ceilometer was created with the intent of capturing and storing critical billing messages. While some Ceilometer data may be a useful supplement to your collected metrics, simply querying Ceilometer is not enough to get useful, actionable information about your OpenStack deployment.  

Nova offers three different means by which you can collect metrics. You can use:  

- **API** for Nova server metrics and tenant metrics  
- **MySQL** for some Nova server metrics, tenant metrics  
- **[CLI](#CLI)** for hypervisor, server, and tenant metrics  

Arguably the most efficient method to use is the CLI (command line interface)—it is a one-stop solution to getting all the metrics mentioned in [the first part][Part 1] of this series.  

#### Collecting Nova metrics from the API or MySQL  

Many of Nova's metrics can be extracted using either the Nova API or an SQL query. For example, to find the total number of VCPUs for a given tenant:  

* you _could_ query the API using **GET** on the `/v2/<tenant-id>/os-hypervisors/statistics` endpoint  
    **OR**  
* run the following SQL query in the `nova` database: `select ifnull(sum(vcpus), 0) from compute_nodes where deleted=0`  

The main advantages of querying SQL versus the API are faster execution times and lower overhead. However, not all metrics are available via SQL, and future changes to the SQL schema could break queries, whereas API calls should be more resilient to changes.

Some metrics, like the number of running instances per Compute node, are only available via API endpoint. Thankfully, the Nova API is [well-documented][nova-api] with more than 100 endpoints available—everything from SSH keys to virtual machine image metadata is only a request away. In addition to informational endpoints, the API can also be used to manage your OpenStack deployment. You can add hosts, update quotas, and more—all over HTTP.

Before you can use the API, you must [acquire an authentication token][api-auth]. You can use `curl` or a similar client to get one like so (change your_password to your admin user password and localhost to your Horizon host): 

```
curl -i \
  -H "Content-Type: application/json" \
  -d '
{ "auth": {
    "identity": {
      "methods": ["password"],
      "password": {
        "user": {
          "name": "admin",
          "domain": { "id": "default" },
          "password": "your_password"
        }
      }
    }
  }
}' \
  http://localhost:5000/v3/auth/tokens ; echo
```

The above command should return a token in the response header:

```
HTTP/1.1 201 Created
Date: Tue, 08 Dec 2015 19:45:36 GMT
Server: Apache/2.4.7 (Ubuntu)
X-Subject-Token: 3939c299ba0743eb94b6f4ff6ff97f6d
Vary: X-Auth-Token
x-openstack-request-id: req-6bf29782-f0a7-4970-b819-5a1c36640d4c
Content-Length: 297
Content-Type: application/json

```

Note the `X-Subject-Token` field in the output above: this is the authentication token.

When it comes to retrieving Nova server metrics, you must use the API. The API endpoint for Nova server metrics is: `/v2.1/​<tenant-id>​/servers/​<server-id>/diagnostics`. Using `curl` and the authentication token acquired above, the request would look something like:

```
curl -H "X-Subject-Token: 3939c299ba0743eb94b6f4ff6ff97f6d" http://localhost:5000/v2.1/<tenant-id>/servers/<server-id>/diagnostics
```

which produces output like below:

```
[...]
{
    "cpu0_time": 17300000000,
    "memory": 524288,
    "vda_errors": -1,
    "vda_read": 262144,
    "vda_read_req": 112,
    "vda_write": 5778432,
    "vda_write_req": 488,
    "vnet1_rx": 2070139,
    "vnet1_rx_drop": 0,
    "vnet1_rx_errors": 0,
    "vnet1_rx_packets": 26701,
    "vnet1_tx": 140208,
    "vnet1_tx_drop": 0,
    "vnet1_tx_errors": 0,
    "vnet1_tx_packets": 662
}
```

<div class="anchor" id="CLI" />

#### Collecting Nova metrics using Nova's CLI 
If you don't want to get your hands dirty in API calls or SQL, or are worried about compatibility with future versions, OpenStack provides a command line client for Nova, aptly dubbed `nova`. There are a [large number][nova-client-ref] of available commands, ranging from metric-gathering methods to administrative tools.
  
The information returned is tenant-dependent, so specify your tenant name, either as a command line argument (`--os-tenant-name <your-tenant-name>`) or as an environment variable (`export OS_TENANT_NAME=<your-tenant-name>`). If the command line complains about a missing username or authentication URL, you can also include them either as additional command line arguments or environment variables, [following the pattern above][env-var].

All but one of the hypervisor metrics from [part 1][Part 1] of this series can be retrieved with a single command (in this example, the tenant name is _testing_): 

```
root@compute-0:~# nova --os-tenant-name testing hypervisor-stats
+----------------------+-------+
| Property             | Value |
+----------------------+-------+
| count                | 2     |
| current_workload     | 1     |
| disk_available_least | 341   |
| free_disk_gb         | 342   |
| free_ram_mb          | 2914  |
| local_gb             | 342   |
| local_gb_used        | 0     |
| memory_mb            | 4002  |
| memory_mb_used       | 1088  |
| running_vms          | 1     |
| vcpus                | 2     |
| vcpus_used           | 1     |
+----------------------+-------+
```
The only hypervisor metric not covered by the previous command is `hypervisor_load`, which you can view by running `uptime` on your compute node.  

Getting tenant metrics is just as easy and can be had with the following command:  
 
```
nova quota-show --tenant <tenant-id>
+-----------------------------+-------+
| Quota                       | Limit |
+-----------------------------+-------+
| instances                   | 10    |
| cores                       | 20    |
| ram                         | 51200 |
| floating_ips                | 10    |
| fixed_ips                   | -1    |
| metadata_items              | 128   |
| injected_files              | 5     |
| injected_file_content_bytes | 10240 |
| injected_file_path_bytes    | 255   |
| key_pairs                   | 100   |
| security_groups             | 10    |
| security_group_rules        | 20    |
| server_groups               | 10    |
| server_group_members        | 10    |
+-----------------------------+-------+
```
_Note that the command `nova quota-show` requires you pass the tenant id and **not** the tenant name_

As you can see from the examples above, the Nova CLI is a very powerful tool to add to your monitoring arsenal. With just a handful of commands, you can collect all of the metrics mentioned in [part 1] of this series. To make sure you get the most out of this dynamic tool, check out the [documentation][nova-client-ref] for a list of all available commands with explanations.

<div class="anchor" id="RabbitMQ" />

### Collecting metrics from RabbitMQ  

RabbitMQ provides a convenient command line client `rabbitmqctl` for accessing its metrics. As described in [part 1][Part 1] of this series, there are four RabbitMQ metrics that are of particular interest for OpenStack monitoring:  

- count: number of active queues  
- memory: size of queues in bytes  
- consumer_utilisation: percentage of time consumers can receive new messages from queue  
- consumers: number of consumers by queue  

#### count  
To get a count of the current number of queues, you can run a command such as `rabbitmqctl list_queue name | wc -l` which pipes the output of `rabbitmqctl` into the UNIX word count program—the optional `-l` flag forces `wc` to return only the line count. Because `rabbitmqctl`'s output includes two extraneous text lines, to get your total number of active queues, subtract two from the number returned by the previous command.

#### memory  
Extracting the size of queues in memory requires a similar command. Running `rabbitmqctl list_queues name memory | grep compute` will show you the memory size of all Nova-related queues (in bytes), like in the output below:  

```
[...]
compute	9096
compute.node0	 9096
compute_fanout_ec3d52fdbe194d89954a3935a8090157 21880
```

#### consumer_utilisation
Are you noticing a pattern with these commands? To get the consumer utilization rates for all queues, run `rabbitmqctl list_queues name consumer_utilisation`, which produces output resembling the following (recall that a utilization rate of 1.0, or 100 percent, means that the queue never has to wait for its consumers): 

```
Listing queues ...
aliveness-test
cert	1.0
cert.devstack	1.0
cert_fanout_c0a7360141564001b0656bf4cd947dab	1.0
cinder-scheduler	1.0
cinder-scheduler.devstack	1.0
[...]
```

#### consumers
Last but not least, to get a count of the active consumers for a given queue, run: `rabbitmqctl list_queues name consumers | grep compute`. 
 
You should see something like this:  

```
[...]
compute	1
compute.node0 	1
compute_fanout_ec3d52fdbe194d89954a3935a8090157   1
```
Remember, few queues should have zero consumers.
<div class="anchor" id="Notifications" />

### Collecting Notifications  
[Notifications][notification system] are emitted on [events][monitoring-101-events] such as instance creation, instance deletion, and resizing operations. Built around an [AMQP] pipeline (typically [RabbitMQ]), Nova is configured to emit notifications on [about 80 events][paste-events]. A number of tools have emerged that collect OpenStack events, but OpenStack's own [StackTach] leads the pack in terms of feature-completeness and documentation. StackTach is especially useful because it needs no updates to handle new events, meaning it can continue to track events in the face of module upgrades.

If you’re just interested in a quick-and-dirty notification listener you can build around, check out this [gist]. Listening in on events requires the `kombu` Python package. [This script][virtualenv] will create a virtual environment and run the event listener. The OpenStack documentation has [additional resources][roll-your-own-listener] on crafting your own notification listener.

The truncated snippet below is an example of notification payloads received after initiating termination of an instance:

```
================================================================================
{ 
[...]

 'event_type': 'compute.instance.delete.start',
 'message_id': '45731b78-ceba-48a4-b80c-3ef971dd632d',
 'payload': {             
'image_meta': {             
'progress': u'',
            'ramdisk_id': 'd768f34d-bb21-4afa-97ed-8d7143a43751',
            'reservation_id': 'r-gz5vu80w',
            'root_gb': 1,
            'state': 'active',
            'state_description': 'deleting',
            'tenant_id': '3fb0de5c53434c54829b7150129dec61',
            'terminated_at': u'',
            'user_id': 'adf56761cda54d4c99de59dc50fd6c06',
            'vcpus': 1},
 'priority': 'INFO',
 'publisher_id': 'compute.devstack',
 'timestamp': '2015-11-24 18:22:51.665797'}

================================================================================
{
[...]

 'event_type': 'compute.instance.delete.end',
 'message_id': '207d6503-2e28-4ec4-97e7-1f3a2a67f6ba',
 'payload': {
             'image_meta': {
             'progress': u'',
             'ramdisk_id': 'd768f34d-bb21-4afa-97ed-8d7143a43751',
             'reservation_id': 'r-gz5vu80w',
             'root_gb': 1,
             'state': 'deleted',
             'state_description': u'',
             'tenant_id': '3fb0de5c53434c54829b7150129dec61',
             'terminated_at': '2015-11-24T18:22:53.479747',
             'user_id': 'adf56761cda54d4c99de59dc50fd6c06',
             'vcpus': 1},
 'priority': 'INFO',
 'publisher_id': 'compute.devstack',
 'timestamp': '2015-11-24 18:22:53.848974'}
```
By comparing the timestamps from both events, you can see it took approximately 2.2 seconds to destroy the instance.

Note that in the snippet above there are _two_ notifications emitted: one when initiating instance termination and one that signals the successful completion of a termination operation. This is a common pattern for events in OpenStack: emit one notification when the operation has begun, and another upon completion.

When combined with collected metrics, notifications give valuable perspective and insight into the potential causes for changes in system behavior. For example, you can measure hypervisor task execution time with events, and correlate that information with the API response time. (_For the curious:_ [in practice][api-vs-load] excessive load on the hypervisor does not appear to affect API response time much.)

<div class="anchor" id="APIChecks" />

### Service and API checks 
_Service checks_ and _API checks_ are used to determine if a service is responsive. API checks generally **GET** or **POST** to a specific API endpoint and verify the response.   

There are a number of tests you can perform to check the health of the Nova API. However, all tests generally boil down to one of two categories: simple or intrusive.  

A simple API check reads (usually static) data from an endpoint and verifies that the information received is as expected. A simple API check would be polling the quota information for a project with a **GET** request to `/v2.1/​<tenant-id>​/limits`.

Intrusive checks modify the state of the receiving endpoint. A typical intrusive check might start by setting a value and optionally following with a request to read or verify the newly created value. Some kind of cleanup would then follow to remove the added values.

An intrusive check for the Nova API would be something like creating and deleting a key pair, with the following set of API calls (checking the status codes returned):  

* **POST** `/v2.1/<tenant-id>/os-keypairs '{"keypair": {"name": "test"}}'`  
* **DELETE** `/v2.1/<tenant-id>/os-keypairs/test`  


## Conclusion
In this article we've discussed a number of ways to check the health of your Compute cluster. 
  
With so much data available from disparate sources, getting the information you want all in one place can be a challenge. Luckily, Datadog can help take the pain out of the process. At Datadog, we have built an integration with Nova so you can begin collecting and monitoring its metrics with a minimum of setup.  

Follow along to [part 3][Part 3] to learn how Datadog can help you monitor Nova.

<iframe width="100%" height="100" style="border: 0;" src="https://go.pardot.com/l/38172/2015-03-02/h6c2r" scrolling="no" type="text/html" frameborder="0" allowtransparency="true"></iframe>

[Part 1]: http://datadoghq.com/blog/openstack-monitoring-nova
[Part 2]: http://datadoghq.com/blog/collecting-metrics-notifications-openstack-nova
[Part 3]: http://datadoghq.com/blog/openstack-monitoring-datadog

[AMQP]: http://docs.openstack.org/developer/nova/rpc.html
[api-auth]: http://docs.openstack.org/developer/keystone/api_curl_examples.html
[architecture]: http://docs.openstack.org/developer/nova/architecture.html

[api-vs-load]: https://javacruft.wordpress.com/2014/06/18/168k-instances/
[Ceilometer]: https://wiki.openstack.org/wiki/Telemetry
[Datadog events]: http://docs.datadoghq.com/guides/dogstatsd/#events
[env-var]: https://wiki.openstack.org/wiki/CLIAuth
[gist]: https://gist.github.com/vagelim/64b355b65378ecba15b0

[paste-events]: http://paste.openstack.org/show/54140/

[leveraging-ceilometer]: https://wiki.openstack.org/wiki/MONaaS

[monitoring-101-events]: https://www.datadoghq.com/blog/monitoring-101-collecting-data#events

[notification system]: https://wiki.openstack.org/wiki/NotificationSystem
[nova-api]: http://developer.openstack.org/api-ref-compute-v2.1.html
[nova-client-ref]: http://docs.openstack.org/cli-reference/content/novaclient_commands.html

[RabbitMQ]: https://app.datadoghq.com/account/settings#integrations/rabbitmq

[roll-your-own-listener]: http://docs.openstack.org/developer/taskflow/notifications.html

[StackTach]: http://stacktach.readthedocs.org/

[virtualenv]: https://gist.github.com/vagelim/98c8792ba12dc8f90341

