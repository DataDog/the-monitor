_This post is the final part of a 3-part series on Kafka monitoring. [Part 1][part1] explores the key metrics available from Kafka, and [Part 2][part2] is about collecting those metrics on an ad hoc basis._

To implement ongoing, meaningful monitoring, you will need a dedicated system that allows you to store, visualize, and correlate your Kafka metrics with the rest of your infrastructure. 

Kafka deployments often rely on additional software packages not included in the Kafka codebase itself, in particular Apache ZooKeeper. A comprehensive monitoring implementation includes all the layers of your deployment, including host-level metrics when appropriate, and not just the metrics emitted by Kafka itself.

[![Kafka dashboard][dash]][dash]

With Datadog, you can collect Kafka metrics for visualization, alerting, and full-infrastructure correlation. Datadog will automatically collect the key metrics discussed in parts [one][part1] and [two][part2] of this series, and make them available in a template dashboard, as seen above.

## Integrating Datadog, Kafka and ZooKeeper

### Verify Kafka and ZooKeeper
Before you begin, you must verify that Kafka is configured to report metrics via JMX, and that you can communicate with ZooKeeper, usually on port 2181. For Kafka, that means confirming that the `JMX_PORT` environment variable is set before starting your broker (or consumer or producer), and then confirming that you can connecting to that port with [JConsole][kafka-jconsole]. For ZooKeeper, you can run this one-liner which uses the [4-letter word][4-letter-word] `ruok`: `echo ruok | nc <ZooKeeperHost> 2181`. If ZooKeeper responds with `imok`, you are ready to install the Agent.

### Install the Datadog Agent
The Datadog Agent is the [open source software][agent-source] that collects and reports metrics from your hosts so that you can view and monitor them in Datadog. Installing the agent usually takes just a single command.

Installation instructions for a variety of platforms are available [here][install].

As soon as the Agent is up and running, you should see your host reporting metrics in your [Datadog account][infra].

[![Host reporting in][default-host]][default-host]

### Configure the Agent
Next you will need to create an Agent configuration file for both ZooKeeper and Kafka. You can find the location of the Agent configuration directory for your OS [here][agent-config-dir]. In that directory, you will find sample configuration files for both [Kafka][kafka-yaml] (**kafka.yaml.example**, **kafka_consumer.yaml.example**) and [ZooKeeper][zookeeper-yaml] (**zk.yaml.example**). On your brokers, copy these files to **kafka.yaml**, **kafka_consumer.yaml**, respectively. On producers and consumers, copy only **kafka.yaml**. On your ZooKeeper nodes, **zk.yaml**. If you are using ZooKeeper's default configuration, you shouldn't need to change anything in **zk.yaml**.

#### kafka.yaml
The default `kafka.yaml` file includes settings to collect all of the metrics mentioned in [part one][part1] of this series. If you'd like to collect more MBeans, check out our [JMX documentation][jmx-doc] for more information on adding your own. 

You can use the example configuration provided whether you are monitoring your brokers, producers, consumers, or all three. Just change the host and port appropriately.

Though you _could_ monitor the entirety of your deployment from one host, it is recommended that you install the Agent on each of your producers, consumers and brokers, and configure each separately.

Besides configuring your hosts, you may also need to modify: `port`, `user`, and `password`.  At this point you can also add tags to the host (like `consumer0`, `broker201`, etc.), and all of the metrics it reports will bear that tag. After making your changes, save and close the file.

#### kafka_consumer.yaml
In order to get broker and consumer offset information into Datadog, you must modify **kafka_consumer.yaml** on a _broker_ (despite the name _kafka\_consumer_) to match your setup. Specifically, you should uncomment and change `kafka_connect_str` to point to a Kafka broker (often localhost), and `zk_connect_str` to point to ZooKeeper. 

The next step is to configure the consumer groups for which you'd like to collect metrics. Start by changing `my_consumer` to the name of your consumer group. Then configure the topics and partitions to watch, by changing `my_topic` to the name of your topic, and placing the partitions to watch in the adjacent array, separated by commas. You can then add more consumer groups or topics, as needed. Be mindful of your whitespace, as YAML files are whitespace-sensitive. After configuring your consumer groups, save and close the file.

### Verify configuration settings
To check that Datadog, Kafka, and ZooKeeper are properly integrated, first [restart the Agent][restart-agent], and then run the Datadog `info` command. The command for each platform is available [here][info-com]. If the configuration is correct, you will see a section resembling the one below in the `info` output:

```
Checks
======

  [...]
  
    kafka
    -----
      - instance #kafka-localhost-9999 [OK] collected 34 metrics
      - Collected 34 metrics, 0 events & 0 service checks

    kafka_consumer
    --------------
      - instance #0 [OK]
      - Collected 1 metric, 0 events & 1 service check

    zk
    --
      - instance #0 [OK]
      - Collected 23 metrics, 0 events & 2 service checks
```

### Enable the integration
Next, click the Kafka and ZooKeeper **Install Integration** buttons inside your Datadog account, under the _Configuration_ tab in the [Kafka integration settings][kafka-integration] and [ZooKeeper integration settings][zookeeper-integration].

## Metrics!
Once the Agent begins reporting metrics, you will see a comprehensive Kafka dashboard among your [list of available dashboards in Datadog][dash-list].

The default Kafka dashboard, as seen at the top of this article, displays the key metrics highlighted in our [introduction to Kafka monitoring][part1].

You can easily create a more comprehensive dashboard to monitor your entire web stack by adding additional graphs and metrics from your other systems. For example, you might want to graph Kafka metrics alongside [metrics from HAProxy][haproxy-metrics], or alongside host-level metrics such as memory usage on application servers. To start building a custom dashboard, clone the default Kafka dashboard by clicking on the gear on the upper right of the dashboard and selecting **Clone Dash**.

[![Clone dash][clone-dash]][clone-dash]

## Alerting
Once Datadog is capturing and visualizing your metrics, you will likely want to [set up some alerts][alerting] to be automatically notified of potential issues.

With our powerful [outlier detection][outlier-detection] feature, you can get alerted on the things that matter. For example, you can set an alert if a particular producer is experiencing an increase in latency while the others are operating normally.

Datadog can monitor individual hosts, containers, services, processes—or virtually any combination thereof. For instance, you can view all of your Kafka brokers, consumers, producers, or all hosts in a certain availability zone, or even a single metric being reported by all hosts with a specific tag.

## Conclusion
In this post we’ve walked you through integrating Kafka with Datadog to visualize your [key metrics][part1] and [notify the right team][alerting] whenever your infrastructure shows signs of trouble.

If you’ve followed along using your own Datadog account, you should now have improved visibility into what’s happening in your environment, as well as the ability to create automated alerts tailored to your infrastructure, your usage patterns, and the metrics that are most valuable to your organization.

If you don’t yet have a Datadog account, you can [sign up for a free trial][signup] and start monitoring Kafka right away.

[part1]: https://www.datadoghq.com/blog/how-to-monitor-kafka-performance-metrics/ 
[part2]: https://www.datadoghq.com/blog/collecting-kafka-performance-metrics/  
[part3]: https://www.datadoghq.com/blog/monitor-kafka-with-datadog/  

[agent-config-dir]: https://docs.datadoghq.com/guides/basic_agent_usage/
[agent-source]: https://github.com/DataDog/dd-agent
[alerting]: https://docs.datadoghq.com/guides/monitoring/
[dash-list]: https://app.datadoghq.com/dash/list
[haproxy-metrics]: https://www.datadoghq.com/blog/monitoring-haproxy-performance-metrics
[info-com]: https://docs.datadoghq.com/guides/basic_agent_usage/
[infra]: https://app.datadoghq.com/infrastructure
[install]: https://app.datadoghq.com/account/settings#agent
[jmx-doc]: https://docs.datadoghq.com/integrations/java/
[kafka-integration]: https://app.datadoghq.com/account/settings#integrations/kafka

[kafka-yaml]: https://github.com/DataDog/dd-agent/blob/master/conf.d/kafka.yaml.example
[outlier-detection]: https://www.datadoghq.com/blog/introducing-outlier-detection-in-datadog/
[restart-agent]: https://docs.datadoghq.com/guides/basic_agent_usage/
[signup]: https://app.datadoghq.com/signup
[zookeeper-integration]: https://app.datadoghq.com/account/settings#integrations/zookeeper
[zookeeper-yaml]: https://github.com/DataDog/dd-agent/blob/master/conf.d/zk.yaml.example

[4-letter-word]: https://www.datadoghq.com/blog/collecting-kafka-performance-metrics/#4-letter-words

[kafka-jconsole]: https://www.datadoghq.com/blog/collecting-kafka-performance-metrics/#jconsole

<IMAGES>

[clone-dash]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-02-kafka/three/clone-dash.png
[dash]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-02-kafka/three/dash1.png
[default-host]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-02-kafka/default-host.png
[kafka-integration-img]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-02-kafka/three/kafka-enable-integration.png
[zookeeper-integration-img]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-02-kafka/three/zookeeper-integration.png