# Collecting Kafka performance metrics


*This post is part 2 of a 3-part series about monitoring Apache Kafka performance. [Part 1](/blog/monitoring-kafka-performance-metrics/) is about the key available Kafka performance metrics, and [Part 3](/blog/monitor-kafka-with-datadog/) details how to monitor Kafka with Datadog.*

If you’ve already read [our guide](/blog/monitoring-kafka-performance-metrics/) to key Kafka performance metrics, you’ve seen that Kafka provides a vast array of metrics on performance and resource utilization, which are available in a number of different ways. You've also seen that no Kafka performance monitoring solution is complete without also monitoring ZooKeeper. This post covers some different options for collecting [Kafka](#collecting-native-kafka-performance-metrics) and [ZooKeeper](#collecting-zookeeper-metrics) metrics, depending on your needs.

Like Tomcat, [Cassandra](/blog/how-to-monitor-cassandra-performance-metrics/), and other [Java applications](/blog/monitoring-jmx-metrics-with-datadog/), both Kafka and ZooKeeper expose metrics on availability and performance via JMX (Java Management Extensions).

Collecting native Kafka performance metrics
-------------------------------------------




-   [JConsole](#collecting-kafka-performance-metrics-with-jconsole), a GUI that ships with the Java Development Kit (JDK)
-   [JMX/Metrics integrations](#collecting-kafka-performance-metrics-via-jmxmetrics-integrations) with external graphing and monitoring tools and services
-   [Burrow](#monitoring-consumer-health-with-burrow) for monitoring consumer health



JConsole, and JMX, can collect all of the native Kafka performance metrics outlined in [part 1 of this series](/blog/monitoring-kafka-performance-metrics/), while Burrow is a more specialized tool focused on collecting consumer metrics. For host-level metrics, you should consider installing a [monitoring agent](https://docs.datadoghq.com/agent/basic_agent_usage/?tab=agentv6).



### Collecting Kafka performance metrics with JConsole


JConsole is a simple Java GUI that ships with the Java Development Kit (JDK). It provides an interface for exploring the full range of metrics Kafka emits via JMX. If the JDK was installed to a directory in your system path, you can start JConsole by running: `jconsole`.

Otherwise, check in `your_JDK_install_dir/bin`

To view metrics in JConsole, you can select the relevant local process or monitor a remote process using the node’s IP address (Kafka uses port 9999 for JMX by default), though it is recommended that you connect remotely, as JConsole can be resource-intensive:

{{< img src="jconsole-remote2.png" alt="Kafka performance - JConsole View" popup="true" size="1x" >}}

The **MBeans** tab brings up all the JMX paths available:

{{< img src="mbean-screen.png" alt="Kafka performance - MBean Tab" popup="true" size="1x" >}}

As you can see in the screenshot above, Kafka aggregates metrics by source. All the JMX paths for Kafka's key metrics can be found in [part 1](/blog/monitoring-kafka-performance-metrics/) of this series.

#### Consumers and producers


To collect JMX metrics from your consumers and producers, follow the same steps outlined above, replacing port 9999 with the JMX port for your producer or consumer, and the node's IP address.



### Collecting Kafka performance metrics via JMX/Metrics integrations


JConsole is a great lightweight tool that can provide metrics snapshots very quickly, but is not so well-suited to the kinds of big-picture questions that arise in a production environment: What are the long-term trends for my metrics? Are there any large-scale patterns I should be aware of? Do changes in performance metrics tend to correlate with actions or events elsewhere in my environment?

To answer these kinds of questions, you need a more sophisticated monitoring system. The good news is, virtually every major monitoring service and tool can collect JMX metrics from Kafka, whether via [JMX plugins](https://docs.datadoghq.com/integrations/java/); via pluggable [metrics reporter libraries](https://cwiki.apache.org/confluence/display/KAFKA/JMX+Reporters); or via [connectors](https://github.com/jmxtrans/jmxtrans) that write JMX metrics out to StatsD, Graphite, or other systems.

The configuration steps depend greatly on the particular monitoring tools you choose, but JMX is a fast route to your Kafka performance metrics using the MBean names mentioned in [part 1](/blog/monitoring-kafka-performance-metrics/) of this series.



### Monitoring consumer health with Burrow


In addition to the key metrics mentioned in part 1 of this series, you may want more detailed metrics on your consumers and consumer groups. For that, there is Burrow.

[Burrow](https://github.com/linkedin/Burrow/wiki/What-is-Burrow) is a specialized monitoring tool developed by [LinkedIn](https://engineering.linkedin.com/apache-kafka/burrow-kafka-consumer-monitoring-reinvented) specifically for consumer monitoring. Why do you need a separate tool to monitor consumer health when you have [`MaxLag`](/blog/monitoring-kafka-performance-metrics/#MaxLag)? (MaxLag represents the number of messages by which the consumer lags behind the producer.) Besides the fact that `MaxLag` has been removed in Kafka v0.9.0.0+, Burrow was built to solve the following shortcomings of simply monitoring consumer offset lag:



-   `MaxLag` is insufficient because it lasts only as long as the consumer is alive
-   spot checking topics conceals problems (like if a single thread of a consumer dies, it stops consuming a topic but other consumption continues, so the consumer may still appear to be healthy)
-   measuring lag for wildcard consumers can quickly become overwhelming with more than a handful of consumers
-   lag alone doesn't tell you the whole story



Enter Burrow.

{{< img src="burrow-arch3.png" alt="Kafka performance - Burrow architecture diagram" popup="true" size="1x" >}}

By consuming the special, internal Kafka topic *__consumer_offsets*, Burrow can act as a centralized service, separate from any single consumer, giving you an objective view of consumers based on both their committed offsets (across topics) and broker state.

#### Installation and configuration


Before we get started, you will need to [install and configure Go](https://golang.org/doc/install) (v1.6+). You can either use a dedicated machine to host Burrow or run it on another host in your environment. Next you'll need the [Go Package Manager](https://github.com/pote/gpm) (GPM) to automatically download Burrow's dependencies.

With Go and GPM installed, run the following commands to build and install burrow:




    go get github.com/linkedin/burrow
    cd $GOPATH/src/github.com/linkedin/burrow
    gpm install
    go install





Before you can use Burrow, you'll need to write a configuration file. Setting up a configuration is easy enough, but varies depending on your Kafka deployment. Below is a barebones, minimal configuration file for a local Kafka deployment with ZooKeeper as the offset storage backend:


	[general]
	logdir=/home/kafka/burrow/log

	[zookeeper]
	hostname=localhost

	[kafka "local"]
	broker=localhost
	zookeeper=localhost
	zookeeper-path=/kafka-cluster
	zookeeper-offsets=true # Set to false if using Kafka for offset storage

	[httpserver]
	server=on
	port=8000



For a complete overview of Burrow configuration options, check the [Burrow wiki](https://github.com/linkedin/Burrow/wiki/Configuration).

With Burrow configured, you can begin tracking consumer health by running: `$GOPATH/bin/burrow --config path/to/burrow.cfg`

If successful, with Burrow running you can begin querying its HTTP endpoints. For example, to see a list of your Kafka clusters, you can hit `/v2/kafka/` and see a JSON response:




    {
          "error": false,
          "message": "cluster list returned",
          "clusters": [
              "local"
          ]
      }





We've just scratched the surface of Burrow's functionality, which includes automated notifications via [HTTP](https://github.com/linkedin/Burrow/wiki/HTTP-Notifier) or [email](https://github.com/linkedin/Burrow/wiki/Email-Notifier). For a complete list of HTTP endpoints, refer to the [documentation](https://github.com/linkedin/Burrow/wiki/HTTP-Endpoint).

Kafka page cache
----------------


Most host-level metrics identified in part 1 can be collected with standard system utilities. Page cache, however, requires more. Linux kernels earlier than 3.13 may require compile-time flags to expose this metric. Also you’ll need to download a utility from [Brendan Gregg](http://www.brendangregg.com/blog/2014-12-31/linux-page-cache-hit-ratio.html):

Start by [downloading](https://github.com/brendangregg/perf-tools/blob/master/fs/cachestat) the `cachestat` script: `wget https://raw.githubusercontent.com/brendangregg/perf-tools/master/fs/cachestat` and make it executable `chmod +x cachestat`. Then, execute it like so `./cachestat <collection interval in seconds>`:



	$ ./cachestat 20
	Counting cache functions... Output every 20 seconds.
	    HITS   MISSES  DIRTIES    RATIO   BUFFERS_MB   CACHE_MB
	    5352        0      234   100.0%          103        165
	    5168        0      260   100.0%          103        165
	    6572        0      259   100.0%          103        165
	    6504        0      253   100.0%          103        165
	[...]





(In the output above *DIRTIES* are those pages that have been modified after entering the page cache.)



Collecting ZooKeeper metrics
----------------------------


Like Kafka, there are several ways you can collect metrics from ZooKeeper. We will focus on the two most popular, JConsole and the so-called ["four letter words"](https://zookeeper.apache.org/doc/trunk/zookeeperAdmin.html#The+Four+Letter+Words). Though we won't go into it here, the [`zktop` utility](https://github.com/phunt/zktop) is also a useful addition to your ZooKeeper monitoring arsenal. It provides a `top`-like interface to ZooKeeper.

Using only the four-letter words, you can collect all of the native ZooKeeper metrics listed in [part 1 of this series](/blog/monitoring-kafka-performance-metrics/) . If you are using JConsole, you can collect all but ZooKeeper's file descriptor metrics.



### Collecting ZooKeeper metrics with JConsole


To view ZooKeeper metrics in JConsole, you can select the `org.apache.zookeeper.server.quorum.QuorumPeerMain` process or monitor a remote process using the node’s IP address (ZooKeeper randomizes its JMX port by default):

{{< img src="zookeeper-jconsole.png" alt="Kafka performance - JConsole View" popup="true" size="1x" >}}

ZooKeeper's exact JMX path for metrics varies depending on your configuration, but invariably you can find them under the `org.apache.ZooKeeperService` MBean.

Using JMX, you can collect all of the metrics listed in part 1, with the exception of `zk_followers` and `zk_pending_syncs`. For those, you will need the [four letter words](#the-four-letter-words).



### The four letter words


ZooKeeper emits operational data in response to a limited set of commands known as "the four letter words". You can issue a four letter word to ZooKeeper via `telnet` or `nc`.

Though the most-used of the commands are: `stat`, `srvr`, `cons`, and `mntr`, the full command list is reproduced below with a short description and availability by version.

If you are on your ZooKeeper node, you can see all of the ZooKeeper metrics from [part 1](/blog/monitoring-kafka-performance-metrics/), including `zk_pending_syncs` and `zk_followers`, with: `echo mntr | nc localhost 2181`:



	zk_version  3.4.5--1, built on 06/10/2013 17:26 GMT
	zk_avg_latency  0
	zk_max_latency  0
	zk_min_latency  0
	zk_packets_received 70
	zk_packets_sent 69
	zk_outstanding_requests 0
	zk_server_state leader
	zk_znode_count   4
	zk_watch_count  0
	zk_ephemerals_count 0
	zk_approximate_data_size    27
	zk_followers    4                   - only exposed by the Leader
	zk_synced_followers 4               - only exposed by the Leader
	zk_pending_syncs    0               - only exposed by the Leader
	zk_open_file_descriptor_count 23    - only available on Unix platforms
	zk_max_file_descriptor_count 1024   - only available on Unix platforms






<table>
<thead>
<tr class="header">
<th>Word</th>
<th>Description</th>
<th>Version</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>conf</td>
<td>Show configuration details</td>
<td>3.3.0+</td>
</tr>
<tr class="even">
<td>cons</td>
<td>Show connection/session details for all connected clients</td>
<td>3.3.0+</td>
</tr>
<tr class="odd">
<td>crst</td>
<td>Reset statistics for all connections/sessions.</td>
<td>3.3.0+</td>
</tr>
<tr class="even">
<td>dump</td>
<td>Show all outstanding sessions and ephemeral nodes (Leader only).</td>
<td>pre 3.3.0</td>
</tr>
<tr class="odd">
<td>envi</td>
<td>Show information on server environment</td>
<td>pre 3.3.0</td>
</tr>
<tr class="even">
<td>ruok</td>
<td>Sanity check. The server will respond with <code>imok</code> if it is running.</td>
<td>pre 3.3.0</td>
</tr>
<tr class="odd">
<td>srst</td>
<td>Reset all server stats</td>
<td>pre 3.3.0</td>
</tr>
<tr class="even">
<td>srvr</td>
<td>Show all server details</td>
<td>pre 3.3.0</td>
</tr>
<tr class="odd">
<td>stat</td>
<td>Brief list of server and client details</td>
<td>pre 3.3.0</td>
</tr>
<tr class="even">
<td>wchs</td>
<td><em>Brief</em> information on <a href="https://zookeeper.apache.org/doc/trunk/zookeeperProgrammers.html#ch_zkWatches">watches</a> for the server</td>
<td>3.3.0+</td>
</tr>
<tr class="odd">
<td>wchc</td>
<td><em>Detailed</em> information on <a href="https://zookeeper.apache.org/doc/trunk/zookeeperProgrammers.html#ch_zkWatches">watches</a> for the server, <em>by session</em></td>
<td>3.3.0+</td>
</tr>
<tr class="even">
<td>wchp</td>
<td><em>Detailed</em> information on <a href="https://zookeeper.apache.org/doc/trunk/zookeeperProgrammers.html#ch_zkWatches">watches</a> <em>by path</em></td>
<td>3.3.0+</td>
</tr>
<tr class="odd">
<td>mntr</td>
<td>Display monitoring information</td>
<td>3.4.0+</td>
</tr>
</tbody>
</table>



*Commands available "pre 3.3.0" work through the latest version.*

Conclusion
----------


In this post we have covered a few of the ways to access Kafka and ZooKeeper metrics using simple, lightweight tools. For production-ready monitoring, you will likely want a dynamic monitoring system that ingests Kafka performance metrics as well as key metrics from every technology in your stack.

At Datadog, we have developed both Kafka and ZooKeeper integrations so that you can start collecting, graphing, and alerting on metrics from your clusters with a minimum of overhead. For more details, check out our guide to [monitoring Kafka performance metrics with Datadog](/blog/monitor-kafka-with-datadog/), or get started right away with a <a href="#" class="sign-up-trigger">free trial</a>.

*Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/kafka/collecting-kafka-performance-metrics.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues).*
