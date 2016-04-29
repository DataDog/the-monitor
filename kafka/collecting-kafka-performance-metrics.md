
_This post is part 2 of a 3-part series about monitoring Apache Kafka. [Part 1][part1] is about the key performance metrics available from Kafka, and [Part 3][part3] details how to monitor Kafka with Datadog._

If you’ve already read [our guide][part1] to key Kafka metrics, you’ve seen that Kafka provides a vast array of metrics on performance and resource utilization, which are available in a number of different ways. You've also seen that no Kafka monitoring solution is complete without also monitoring ZooKeeper. This post covers some different options for collecting [Kafka](#jconsole) and [ZooKeeper](#zookeeper) metrics, depending on your needs.

Like Tomcat, [Cassandra], and other [Java applications][jmx-dd], both Kafka and ZooKeeper expose metrics on availability and performance via JMX (Java Management Extensions). 

## Collecting native Kafka metrics

- [JConsole](#jconsole), a GUI that ships with the Java Development Kit (JDK)
- [JMX/Metrics integrations](#jmx) with external graphing and monitoring tools and services
- [Burrow](#burrow) for monitoring consumer health

JConsole, and JMX, can collect all of the native Kafka metrics outlined in [part 1 of this series][part1], while Burrow is a more specialized tool focused on collecting consumer metrics. For host-level metrics, you should consider installing a [monitoring agent][agent].

<div class="anchor" id="jconsole" />

### Collecting Kafka metrics with JConsole

JConsole is a simple Java GUI that ships with the Java Development Kit (JDK). It provides an interface for exploring the full range of metrics Kafka emits via JMX. If the JDK was installed to a directory in your system path, you can start JConsole by running: `jconsole`.
Otherwise, check in `your_JDK_install_dir/bin`

To view metrics in JConsole, you can select the relevant local process or monitor a remote process using the node’s IP address (Kafka uses port 9999 for JMX by default),  though it is recommended that you connect remotely, as JConsole can be resource-intensive:

[![JConsole View][jconsole-screen]][jconsole-screen]

The **MBeans** tab brings up all the JMX paths available:

[![MBean Tab][mbean-screen]][mbean-screen]

As you can see in the screenshot above, Kafka aggregates metrics by source. All the JMX paths for Kafka's key metrics can be found in [part 1][part1] of this series.

#### Consumers and producers
To collect JMX metrics from your consumers and producers, follow the same steps outlined above, replacing port 9999 with the JMX port for your producer or consumer, and  the node's IP address.

<div class="anchor" id="jmx" />

### Collecting Kafka metrics via JMX/Metrics integrations

JConsole is a great lightweight tool that can provide metrics snapshots very quickly, but is not so well-suited to the kinds of big-picture questions that arise in a production environment: What are the long-term trends for my metrics? Are there any large-scale patterns I should be aware of? Do changes in performance metrics tend to correlate with actions or events elsewhere in my environment?

To answer these kinds of questions, you need a more sophisticated monitoring system. The good news is, virtually every major monitoring service and tool can collect JMX metrics from Kafka, whether via [JMX plugins]; via pluggable [metrics reporter libraries][reporter-libraries]; or via [connectors] that write JMX metrics out to StatsD, Graphite, or other systems.

The configuration steps depend greatly on the particular monitoring tools you choose, but JMX is a fast route to your Kafka metrics using the MBean names mentioned in [part 1][part1] of this series.

<div class="anchor" id="burrow" />

### Monitoring consumer health with Burrow
In addition to the key metrics mentioned in part 1 of this series, you may want more detailed metrics on your consumers and consumer groups. For that, there is Burrow.

[Burrow][what-is-burrow] is a specialized monitoring tool developed by [LinkedIn][burrow-linkedin] specifically for consumer monitoring. Why do you need a separate tool to monitor consumer health when you have [`MaxLag`][consumer-lag]? (MaxLag represents the number of messages by which the consumer lags behind the producer.) Besides the fact that `MaxLag` has been removed in Kafka v0.9.0.0+, Burrow was built to solve the following shortcomings of simply monitoring consumer offset lag: 

- `MaxLag` is insufficient because it lasts only as long as the consumer is alive
- spot checking topics conceals problems (like if a single thread of a consumer dies, it stops consuming a topic but other consumption continues, so the consumer may still appear to be healthy)
- measuring lag for wildcard consumers can quickly become overwhelming with more than a handful of consumers
- lag alone doesn't tell you the whole story

Enter Burrow.  

[![Burrow architecture diagram][burrow-arch]][burrow-arch] 
<change the "Offset commit" to include an optional (dotted) arrow to ZooKeeper, as Burrow can work with Kafka deployments that use ZooKeeper for offset storage>

By consuming the special, internal Kafka topic __\_consumer\_offsets_, Burrow can act as a centralized service, separate from any single consumer, giving you an objective view of consumers based on both their committed offsets (across topics) and broker state.

#### Installation and configuration
Before we get started, you will need to [install and configure Go][go-install] (v1.6+). You can either use a dedicated machine to host Burrow or run it on another host in your environment. Next you'll need the [Go Package Manager][gpm] (GPM) to automatically download Burrow's dependencies.

With Go and GPM installed, run the following commands to build and install burrow:

```
go get github.com/linkedin/burrow
cd $GOPATH/src/github.com/linkedin/burrow
gpm install
go install
```

Before you can use Burrow, you'll need to write a configuration file. Setting up a configuration is easy enough, but varies depending on your Kafka deployment. Below is a barebones, minimal configuration file for a local Kafka deployment with ZooKeeper as the offset storage backend:

```
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
```

For a complete overview of Burrow configuration options, check the [Burrow wiki][burrow-conf].

With Burrow configured, you can begin tracking consumer health by running: `$GOPATH/bin/burrow --config path/to/burrow.cfg`

If successful, with Burrow running you can begin querying its HTTP endpoints. For example, to see a list of your Kafka clusters, you can hit `/v2/kafka/` and see a JSON response:
 
```
{
    "error": false,
    "message": "cluster list returned",
    "clusters": [
        "local"
    ]
}
```

We've just scratched the surface of Burrow's functionality, which includes automated notifications via [HTTP][notif-http] or [email][notif-email]. For a complete list of HTTP endpoints, refer to the [documentation][burrow-api].

## Kafka page cache
Most host-level metrics identified in part 1 can be collected with standard system utilities. Page cache, however, requires more. Linux kernels earlier than 3.13 may require compile-time flags to expose this metric. Also you’ll need to download a utility from [Brendan Gregg][cachestat-doc]:

Start by [downloading][cachestat-dl] the `cachestat` script: `wget https://raw.githubusercontent.com/brendangregg/perf-tools/master/fs/cachestat` and make it executable `chmod +x cachestat`. Then, execute it like so `./cachestat <collection interval in seconds>`:

```
$ ./cachestat 20
Counting cache functions... Output every 20 seconds.
    HITS   MISSES  DIRTIES    RATIO   BUFFERS_MB   CACHE_MB
    5352        0      234   100.0%          103        165
    5168        0      260   100.0%          103        165
    6572        0      259   100.0%          103        165
    6504        0      253   100.0%          103        165
[...]
    
```
(In the output above _DIRTIES_ are those pages that have been modified after entering the page cache.)

<div class="anchor" id="zookeeper" />

## Collecting ZooKeeper metrics
Like Kafka, there are several ways you can collect metrics from ZooKeeper. We will focus on the two most popular, JConsole and the so-called ["four letter words"][4-letter-words]. Though we won't go into it here, the [`zktop` utility][zktop] is also a useful addition to your ZooKeeper monitoring arsenal. It provides a `top`-like interface to ZooKeeper. 

Using only the four-letter words, you can collect all of the native ZooKeeper metrics listed in [part 1 of this series][part1] . If you are using JConsole, you can collect all but ZooKeeper's file descriptor metrics.

<div class="anchor" id="jconsole-zoo" />

### Collecting ZooKeeper metrics with JConsole
To view ZooKeeper metrics in JConsole, you can select the `org.apache.zookeeper.server.quorum.QuorumPeerMain` process or monitor a remote process using the node’s IP address (ZooKeeper randomizes its JMX port by default):

[![JConsole View][zookeeper-screen]][zookeeper-screen]

ZooKeeper's exact JMX path for metrics varies depending on your configuration, but invariably you can find them under the `org.apache.ZooKeeperService` MBean.

Using JMX, you can collect all of the metrics listed in part 1, with the exception of `zk_followers` and `zk_pending_syncs`. For those, you will need the [four letter words](#4-letter-words).

<div class="anchor" id="4-letter-words" />

### The four letter words
ZooKeeper responds to a small set of commands known as "the four letter words". Each command is composed of—you guessed it—four letters. You can issue the commands to ZooKeeper via `telnet` or `nc`. 

Though the most-used of the commands are: `stat`, `srvr`,  `cons`, and `mntr`,  the full command list is reproduced below with a short description and availability by version. 

If you are on your ZooKeeper node, you can see all of the ZooKeeper metrics from [part 1][part1], including `zk_pending_syncs` and `zk_followers`, with: `echo mntr | nc localhost 2181`:

```
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
```

|Word| Description | Version|
|:--:|:--:|:--:|
|conf| Print details about serving configuration.|3.3.0+|
|cons| List full connection/session details for all clients connected to this server. Includes information on numbers of packets received/sent, session id, operation latencies, last operation performed |3.3.0+|
|crst| Reset connection/session statistics for all connections.|3.3.0+|
|dump|Lists the outstanding sessions and ephemeral nodes (Leader only).|pre 3.3.0|
|envi|Print details about serving environment|pre 3.3.0|
|ruok|Tests if server is running in a non-error state. The server will respond with `imok` if it is running. |pre 3.3.0|
|srst|Reset server statistics.|pre 3.3.0|
|srvr|Lists full details for the server.|pre 3.3.0|
|stat|Lists brief details for the server and connected clients.| pre 3.3.0|
|wchs|Lists _brief_ information on [watches] for the server|3.3.0+|
|wchc|Lists _detailed_ information on [watches] for the server, _by session_.|3.3.0+|
|wchp|Lists _detailed_ information on [watches] for the server, _by path_. |3.3.0+|
|mntr|Outputs a list of variables that could be used for monitoring the health of the cluster.|3.4.0+|

*Commands available "pre 3.3.0" work through the latest version.*

## Conclusion
In this post we have covered a few of the ways to access Kafka and ZooKeeper metrics using simple, lightweight tools. For production-ready monitoring, you will likely want a dynamic monitoring system that ingests Kafka metrics as well as key metrics from every technology in your stack.

At Datadog, we have developed both Kafka and ZooKeeper integrations so that you can start collecting, graphing, and alerting on metrics from your clusters with a minimum of overhead. For more details, check out our guide to [monitoring Kafka metrics with Datadog][part3], or get started right away with a [free trial][signup].

[signup]: https://app.datadoghq.com/signup

[4-letter-words]: https://zookeeper.apache.org/doc/trunk/zookeeperAdmin.html#The+Four+Letter+Words
[agent]: http://docs.datadoghq.com/guides/basic_agent_usage/
[burrow-api]: https://github.com/linkedin/Burrow/wiki/HTTP-Endpoint
[burrow-conf]: https://github.com/linkedin/Burrow/wiki/Configuration
[burrow-linkedin]: https://engineering.linkedin.com/apache-kafka/burrow-kafka-consumer-monitoring-reinvented
[Cassandra]: https://www.datadoghq.com/blog/how-to-monitor-cassandra-performance-metrics/
[cachestat-dl]: https://github.com/brendangregg/perf-tools/blob/master/fs/cachestat
[cachestat-doc]: http://www.brendangregg.com/blog/2014-12-31/linux-page-cache-hit-ratio.html
[connectors]: https://github.com/jmxtrans/jmxtrans
[go-download]: https://golang.org/dl/
[go-install]: https://golang.org/doc/install
[gpm]: https://github.com/pote/gpm
[jmx-dd]: https://www.datadoghq.com/blog/monitoring-jmx-metrics-with-datadog/
[JMX plugins]: http://docs.datadoghq.com/integrations/java/
[notif-email]: https://github.com/linkedin/Burrow/wiki/Email-Notifier
[notif-http]: https://github.com/linkedin/Burrow/wiki/HTTP-Notifier
[reporter-libraries]: https://cwiki.apache.org/confluence/display/KAFKA/JMX+Reporters
[watches]: https://zookeeper.apache.org/doc/trunk/zookeeperProgrammers.html#ch_zkWatches
[what-is-burrow]: https://github.com/linkedin/Burrow/wiki/What-is-Burrow
[zktop]: https://github.com/phunt/zktop

<IMAGES>

[burrow-arch]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-02-kafka/burrow-arch3.png
[jconsole-screen]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-02-kafka/jconsole-remote2.png
[mbean-screen]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-02-kafka/mbean-screen.png
[zookeeper-screen]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-02-kafka/zookeeper-jconsole.png

[part1]: https://www.datadoghq.com/blog/how-to-monitor-kafka-performance-metrics/ 
[part2]: https://www.datadoghq.com/blog/collecting-kafka-performance-metrics/  
[part3]: https://www.datadoghq.com/blog/monitor-kafka-with-datadog/  

[consumer-lag]: https://www.datadoghq.com/blog/how-to-monitor-kafka-performance-metrics/#MaxLag