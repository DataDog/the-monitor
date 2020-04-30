If you’ve already read [our guide](/blog/monitoring-kafka-performance-metrics/) to key Kafka performance metrics, you’ve seen that Kafka provides a vast array of metrics on performance and resource utilization, which are available in a number of different ways. You've also seen that no Kafka performance monitoring solution is complete without also monitoring ZooKeeper. This post covers some different options for collecting [Kafka](#collect-native-kafka-performance-metrics) and [ZooKeeper](#collect-zookeeper-metrics) metrics, depending on your needs.

Like [Tomcat](/blog/tomcat-architecture-and-performance/), [Cassandra](/blog/how-to-monitor-cassandra-performance-metrics/), and other [Java applications](/blog/monitoring-jmx-metrics-with-datadog/), both Kafka and ZooKeeper expose metrics on availability and performance via Java Management Extensions (JMX).

## Collect native Kafka performance metrics
In this post, we'll show you how to use the following tools to collect metrics from Kafka and ZooKeeper:

-   [JConsole](#collect-kafka-performance-metrics-with-jconsole), a GUI that ships with the Java Development Kit (JDK)
-   [JMX](#collect-kafka-performance-metrics-via-jmx) with external graphing and monitoring tools and services
-   [Burrow](#monitor-consumer-health-with-burrow) for monitoring consumer health

JConsole and JMX can collect all of the native Kafka performance metrics outlined in [Part 1 of this series](/blog/monitoring-kafka-performance-metrics/), while Burrow is a more specialized tool that allows you to monitor the status and offsets of all your consumers. For host-level metrics, you should consider installing a [monitoring agent](https://docs.datadoghq.com/agent/basic_agent_usage/?tab=agentv6).

### Collect Kafka performance metrics with JConsole
JConsole is a simple Java GUI that ships with the JDK. It provides an interface for exploring the full range of metrics Kafka emits via JMX. Because JConsole can be resource-intensive, you should run it on a dedicated host and collect Kafka metrics remotely. 

First, you need to designate a port that JConsole can use to collect JMX metrics from your Kafka host. Edit Kafka's startup script—**bin/kafka-run-class.sh**—to include the value of the JMX port by adding the following parameters to the `KAFKA_JMX_OPTS` variable:

{{< code-snippet wrap="false" lang="text" >}}
-Dcom.sun.management.jmxremote.port=<MY_JMX_PORT> -Dcom.sun.management.jmxremote.rmi.port=<MY_JMX_PORT> -Djava.rmi.server.hostname=<MY_IP_ADDRESS>
{{< /code-snippet >}}

Restart Kafka to apply these changes.

Next, launch JConsole on your dedicated monitoring host. If the JDK is installed to a directory in your system path, you can start JConsole with the command  `jconsole`. Otherwise, look for the JConsole executable in the **bin/** subdirectory of your JDK installation.

In the JConsole UI, specify the IP address and JMX port of your Kafka host. The example below shows JConsole connecting to a Kafka host at 192.0.0.1, port 9999:

{{< img src="jconsole-remote2.png" alt="JConsole's New Connection view includes remote process, username, and password fields you can use to connect to a remote node to monitor Kafka performance." border="true" size="1x" >}}

The **MBeans** tab brings up all the JMX paths available:

{{< img src="mbeans-tab.png" alt="JConsole's MBean tab shows relevant JMX paths such as kafka.server and kafka.cluster" popup="true" border="true" >}}

As you can see in the screenshot above, Kafka aggregates metrics by source. All the JMX paths for Kafka's key metrics can be found in [Part 1](/blog/monitoring-kafka-performance-metrics/) of this series.

#### Consumers and producers
To collect JMX metrics from your consumers and producers, follow the same steps outlined above, replacing port 9999 with the JMX port for your producer or consumer, and the node's IP address.

### Collect Kafka performance metrics via JMX
JConsole is a great lightweight tool that can provide metrics snapshots very quickly, but is not so well-suited to the kinds of big-picture questions that arise in a production environment: What are the long-term trends for my metrics? Are there any large-scale patterns I should be aware of? Do changes in performance metrics tend to correlate with actions or events elsewhere in my environment?

To answer these kinds of questions, you need a more sophisticated monitoring system. Fortunately, many monitoring services and tools can collect JMX metrics from Kafka, whether via [JMX plugins](https://docs.datadoghq.com/integrations/java/); via pluggable [metrics reporter libraries](https://cwiki.apache.org/confluence/display/KAFKA/JMX+Reporters); or via [connectors](https://github.com/jmxtrans/jmxtrans) that write JMX metrics out to StatsD, Graphite, or other systems.

The configuration steps depend greatly on the particular monitoring tools you choose, but JMX is a fast route to viewing Kafka performance metrics using the MBean names mentioned in [Part 1](/blog/monitoring-kafka-performance-metrics/) of this series.

### Monitor consumer health with Burrow
In addition to the key metrics mentioned in Part 1 of this series, you may want more detailed metrics on your consumers. For that, there is Burrow.

[Burrow](https://github.com/linkedin/Burrow/wiki) is a specialized monitoring tool developed by [LinkedIn](https://engineering.linkedin.com/apache-kafka/burrow-kafka-consumer-monitoring-reinvented) specifically for Kafka consumer monitoring. Burrow gives you visibility into Kafka's offsets, topics, and consumers.

By consuming the special internal Kafka topic `__consumer_offsets`, Burrow can act as a centralized service, separate from any single consumer, giving you an objective view of consumers based on both their committed offsets (across topics) and broker state.

#### Installation and configuration
Before we get started, you will need to [install and configure Go](https://golang.org/doc/install) (v1.11+). You can either use a dedicated machine to host Burrow or run it on one of the hosts in your Kafka deployment.

With Go installed, run the following commands to build and install Burrow:

{{< code-snippet lang="bash" wrap="false" >}}
    go get github.com/linkedin/burrow
    cd $GOPATH/src/github.com/linkedin/burrow
    go mod tidy
    go install
{{< /code-snippet >}}

Before you can use Burrow, you'll need to write a configuration file. Your Burrow configuration will vary depending on your Kafka deployment. Below is a minimal configuration file for a local Kafka deployment:

{{< code-snippet wrap="false" lang="text" filename="burrow.cfg" >}}
[zookeeper]
servers=["localhost:2181" ]

[httpserver.mylistener]
address=":8080"

[cluster.local]
class-name="kafka"
servers=[ "localhost:9091", "localhost:9092", "localhost:9093" ]

[consumer.myconsumers]
class-name="kafka"
cluster="local"
servers=[ "localhost:9091", "localhost:9092", "localhost:9093" ]
offsets-topic="__consumer_offsets"
{{< /code-snippet >}}

For a complete overview of Burrow configuration options, check the [Burrow wiki](https://github.com/linkedin/Burrow/wiki/Configuration).

With Burrow configured, you can begin tracking consumer health by running this command: 

{{< code-snippet lang="bash" wrap="false" >}}
$GOPATH/bin/burrow --config-dir /path/to/config-directory
{{< /code-snippet >}}

Now you can begin querying [Burrow's HTTP endpoints](https://github.com/linkedin/Burrow/wiki/HTTP-Endpoint). For example, to see a list of your Kafka clusters, you can hit `http://localhost:8080/v3/kafka` and see a JSON response like the one shown here:

{{< code-snippet lang="json" wrap="false" >}}
{
	"error": false,
	"message": "cluster list returned",
	"clusters": ["local"],
	"request": {
		"url": "/v3/kafka",
		"host": "mykafkahost"
	}
}
{{< /code-snippet >}}

We've just scratched the surface of Burrow's functionality, which includes automated notifications via [HTTP](https://github.com/linkedin/Burrow/wiki/Notifier-HTTP) or [email](https://github.com/linkedin/Burrow/wiki/Notifier-Email). For more details about Burrow, refer to the [documentation](https://github.com/linkedin/Burrow/wiki/).

## Monitor Kafka's page cache
Most host-level metrics identified in [Part 1](/blog/monitoring-kafka-performance-metrics/) can be collected with standard system utilities. Page cache, however, requires more. Linux kernels earlier than 3.13 may require compile-time flags to expose this metric. Also, you’ll need to download the [cachestat](https://github.com/brendangregg/perf-tools/blob/master/fs/cachestat) script created by [Brendan Gregg](http://www.brendangregg.com/blog/2014-12-31/linux-page-cache-hit-ratio.html) : 

{{< code-snippet lang="text" wrap="false" >}}
wget https://raw.githubusercontent.com/brendangregg/perf-tools/master/fs/cachestat
{{< /code-snippet >}}

Next, make the script executable:

{{< code-snippet lang="text" wrap="false" >}}
chmod +x cachestat
{{< /code-snippet >}}

Then you can execute it with `./cachestat <collection interval in seconds>`. You should see output that looks similar to this example:

{{< code-snippet lang="bash" wrap="false" >}}
Counting cache functions... Output every 20 seconds.
	    HITS   MISSES  DIRTIES    RATIO   BUFFERS_MB   CACHE_MB
	    5352        0      234   100.0%          103        165
	    5168        0      260   100.0%          103        165
	    6572        0      259   100.0%          103        165
	    6504        0      253   100.0%          103        165
	[...]
{{< /code-snippet >}}

(The values in the **DIRTIES** column show the number of pages that have been modified after entering the page cache.)

## Collect ZooKeeper metrics
In this section, we'll look at three tools you can use to collect metrics from ZooKeeper: JConsole, ZooKeeper's "four letter words," and the ZooKeeper AdminServer. Using only the four-letter words or the AdminServer, you can collect all of the native ZooKeeper metrics listed in [Part 1 of this series](/blog/monitoring-kafka-performance-metrics/#zookeeper-metrics). If you are using JConsole, you can collect all but the `followers` and `open_file_descriptor_count` metrics.

(In addition to these, the `zktop` utility—which provides a `top`-like interface to ZooKeeper—is also a useful tool for monitoring your ZooKeeper ensemble. We won't cover `zktop` in this post; see [the documentation](https://github.com/phunt/zktop) to learn more about it.)

### Use JConsole to view JMX metrics
To view ZooKeeper metrics in JConsole, you can select the `org.apache.zookeeper.server.quorum.QuorumPeerMain` process if you're monitoring a local ZooKeeper server. By default, ZooKeeper allows only local JMX connections, so to monitor a remote server, you need to manually designate a JMX port. You can specify the port by adding it to ZooKeeper's **bin/zkEnv.sh** file as an environment variable, or you can include it in the command you use to start ZooKeeper, as in this example:

{{< code-snippet wrap="false" lang="text" >}}
JMXPORT=9993 bin/zkServer.sh start
{{< /code-snippet >}}

Note that to enable remote monitoring of a Java process, you'll need to set the `java.rmi.server.hostname` property. See the [Java documentation](https://docs.oracle.com/en/java/javase/14/management/monitoring-and-management-using-jmx-technology.html#GUID-F08985BB-629A-4FBF-A0CB-8762DF7590E0) for guidance. 

Once ZooKeeper is running and sending metrics via JMX, you can connect your JConsole instance to the remote server, as shown here:

{{< img src="zookeeper-jconsole-overview.png" alt="JConsole's Overview tab helps you monitor Kafka performance by tracking metrics like heap memory usage, thread count, class count, and CPU usage." popup="true" border="true" >}}

ZooKeeper's exact JMX path for metrics varies depending on your configuration, but invariably you can find them under the `org.apache.ZooKeeperService` MBean.

{{< img src="zookeeper-jconsole-mbeans.png" alt="A screenshot shows JConsole connected to ZooKeeper, showing the MBeans tab." border="true" >}}

Using JMX, you can collect most of the metrics listed in Part 1 of this series. To collect them all, you will need to use the [four-letter words](#the-four-letter-words) or the ZooKeeper [AdminServer](#the-adminserver).

### The four-letter words
ZooKeeper emits operational data in response to a limited set of commands known as ["the four-letter words."](https://zookeeper.apache.org/doc/current/zookeeperAdmin.html#sc_4lw) Four-letter words are being deprecated in favor of the [AdminServer](#the-adminserver), and as of ZooKeeper version 3.5, you need to explicitly whitelist each four-letter word before you can use it. To add one or more four-letter words to the whitelist, specify them in the **zoo.cfg** file in the **conf** subdirectory of your ZooKeeper installation. For example, add this line to the end of the file to allow use of the `mntr` and `ruok` words:

{{< code-snippet wrap="false" lang="text" filename="zoo.cfg" >}}
4lw.commands.whitelist=mntr, ruok
{{< /code-snippet >}}

You can issue a four-letter word to ZooKeeper via `telnet` or `nc`. For example, now that we've added it to the whitelist, we can use the `mntr` word to get some details about the ZooKeeper server:

{{< code-snippet wrap="false" lang="text" >}}
echo mntr | nc localhost 2181
{{< /code-snippet >}}

ZooKeeper responds with information similar to the example shown here:

{{< code-snippet wrap="false" lang="text" >}}
zk_version	3.5.7-f0fdd52973d373ffd9c86b81d99842dc2c7f660e, built on 02/10/2020 11:30 GMT
zk_avg_latency	0
zk_max_latency	0
zk_min_latency	0
zk_packets_received	12
zk_packets_sent	11
zk_num_alive_connections	1
zk_outstanding_requests	0
zk_server_state	standalone
zk_znode_count	5
zk_watch_count	0
zk_ephemerals_count	0
zk_approximate_data_size	44
zk_open_file_descriptor_count	67
zk_max_file_descriptor_count	1048576
{{< /code-snippet >}}
### The AdminServer
As of ZooKeeper version 3.5, the [AdminServer](https://zookeeper.apache.org/doc/r3.5.7/zookeeperAdmin.html#sc_adminserver) replaces the four-letter words. You can access all the same information about your ZooKeeper ensemble using the AdminServer's HTTP endpoints. To see the available endpoints, send a request to the `commands` endpoint on the local ZooKeeper server:

{{< code-snippet lang="text" wrap="false" >}}
curl http://localhost:8080/commands
{{< /code-snippet >}}

You can retrieve information from a specific endpoint with a similar command, specifying the name of the endpoint in the URL, as shown here:

 {{< code-snippet lang="text" wrap="false" >}}
curl http://localhost:8080/<ENDPOINT>
{{< /code-snippet >}}

AdminServer sends its output in JSON format. For example, the AdminServer's `monitor` endpoint serves a similar function to the `mntr` word we called earlier. Sending a request to `http://localhost:8080/commands/monitor` yields an output that looks like this:

{{< code-snippet lang="json" wrap="false" >}}
{
  "version" : "3.5.7-f0fdd52973d373ffd9c86b81d99842dc2c7f660e, built on 02/10/2020 11:30 GMT",
  "avg_latency" : 0,
  "max_latency" : 0,
  "min_latency" : 0,
  "packets_received" : 36,
  "packets_sent" : 36,
  "num_alive_connections" : 0,
  "outstanding_requests" : 0,
  "server_state" : "standalone",
  "znode_count" : 5,
  "watch_count" : 0,
  "ephemerals_count" : 0,
  "approximate_data_size" : 44,
  "open_file_descriptor_count" : 68,
  "max_file_descriptor_count" : 1048576,
  "last_client_response_size" : -1,
  "max_client_response_size" : -1,
  "min_client_response_size" : -1,
  "command" : "monitor",
  "error" : null

}
{{< /code-snippet >}}
## Production-ready Kafka performance monitoring 
In this post, we have covered a few ways to access Kafka and ZooKeeper metrics using simple, lightweight tools. For production-ready monitoring, you will likely want a dynamic monitoring system that ingests Kafka performance metrics as well as key metrics from every technology in your stack. In [Part 3](/blog/monitor-kafka-with-datadog) of this series, we'll show you how to use Datadog to collect and view metrics—as well as logs and traces—from your Kafka deployment. 

Datadog integrates with Kafka, ZooKeeper, and more than {{< translate key="integration_count" >}} other technologies, so that you can analyze and alert on metrics, logs, and distributed request traces from your clusters. For more details, check out our guide to [monitoring Kafka performance metrics with Datadog](/blog/monitor-kafka-with-datadog/), or get started right away with a <a href="#" class="sign-up-trigger">free trial</a>.

## Acknowledgments
Thanks to Dustin Cote at [Confluent](https://www.confluent.io/) for generously sharing his Kafka expertise for this article.

*Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/kafka/collecting-kafka-performance-metrics.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues).*
