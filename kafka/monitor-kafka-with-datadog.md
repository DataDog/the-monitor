# Monitoring Kafka with Datadog


*This post is the final part of a 3-part series on how to monitor Kafka. [Part 1](https://www.datadoghq.com/blog/monitoring-kafka-performance-metrics/) explores the key metrics available from Kafka, and [Part 2](https://www.datadoghq.com/blog/collecting-kafka-performance-metrics/) is about collecting those metrics on an ad hoc basis.*

To implement ongoing, meaningful monitoring, you will need a dedicated system that allows you to store, visualize, and correlate your Kafka metrics with the rest of your infrastructure.

Kafka deployments often rely on additional software packages not included in the Kafka codebase itself, in particular Apache ZooKeeper. A comprehensive monitoring implementation includes all the layers of your deployment, including host-level metrics when appropriate, and not just the metrics emitted by Kafka itself.

{{< img src="dash1.png" alt="Monitor Kafka - Kafka dashboard" popup="true" >}}

With Datadog, you can collect Kafka metrics for visualization, alerting, and full-infrastructure correlation. Datadog will automatically collect the key metrics discussed in parts [one](https://www.datadoghq.com/blog/monitoring-kafka-performance-metrics/) and [two](https://www.datadoghq.com/blog/collecting-kafka-performance-metrics/) of this series, and make them available in a template dashboard, as seen above.

Integrating Datadog, Kafka and ZooKeeper
----------------------------------------



### Verify Kafka and ZooKeeper


Before you begin, you must verify that Kafka is configured to report metrics via JMX, and that you can communicate with ZooKeeper, usually on port 2181. For Kafka, that means confirming that the `JMX_PORT` environment variable is set before starting your broker (or consumer or producer), and then confirming that you can connecting to that port with [JConsole](https://www.datadoghq.com/blog/collecting-kafka-performance-metrics/#jconsole).

For ZooKeeper, you can run this one-liner which uses the [4-letter word](https://www.datadoghq.com/blog/collecting-kafka-performance-metrics/#4-letter-words) `ruok`: `echo ruok | nc <ZooKeeperHost> 2181`. If ZooKeeper responds with `imok`, you are ready to install the Agent.

### Install the Datadog Agent


The Datadog Agent is the [open source software](https://github.com/DataDog/dd-agent) that collects and reports metrics from your hosts so that you can view and monitor them in Datadog. Installing the agent usually takes just a single command.

Installation instructions for a variety of platforms are available [here](https://app.datadoghq.com/account/settings#agent).

As soon as the Agent is up and running, you should see your host reporting metrics in your [Datadog account](https://app.datadoghq.com/infrastructure).

{{< img src="default-host.png" alt="Monitor Kafka - Host reporting in" popup="true" size="1x" >}}

### Configure the Agent


Next you will need to create an Agent configuration file for both ZooKeeper and Kafka. You can find the location of the Agent configuration directory for your OS [here](https://docs.datadoghq.com/agent/). In that directory, you will find sample configuration files for both [Kafka](https://github.com/DataDog/integrations-core/blob/master/kafka/datadog_checks/kafka/data/conf.yaml.example) (**kafka.yaml.example**, **kafka_consumer.yaml.example**) and [ZooKeeper](https://github.com/DataDog/integrations-core/blob/master/zk/datadog_checks/zk/data/conf.yaml.example) (**zk.yaml.example**).

On your brokers, copy these files to **kafka.yaml**, **kafka_consumer.yaml**, respectively.

On producers and consumers, copy only **kafka.yaml**. On your ZooKeeper nodes, **zk.yaml**.

If you are using ZooKeeper's default configuration, you shouldn't need to change anything in **zk.yaml**.

#### kafka.yaml


The default `kafka.yaml` file includes settings to collect all of the metrics mentioned in [part one](https://www.datadoghq.com/blog/monitoring-kafka-performance-metrics/) of this series. If you'd like to collect more MBeans, check out our [JMX documentation](https://docs.datadoghq.com/integrations/java/) for more information on adding your own.

You can use the example configuration provided whether you are monitoring your brokers, producers, consumers, or all three. Just change the host and port appropriately.

Though you *could* monitor the entirety of your deployment from one host, it is recommended that you install the Agent on each of your producers, consumers and brokers, and configure each separately.

Besides configuring your hosts, you may also need to modify: `port`, `user`, and `password`. At this point you can also add tags to the host (like `consumer0`, `broker201`, etc.), and all of the metrics it reports will bear that tag. After making your changes, save and close the file.

#### kafka_consumer.yaml


In order to get broker and consumer offset information into Datadog, you must modify **kafka_consumer.yaml** on a *broker* (despite the name *kafka_consumer*) to match your setup. Specifically, you should uncomment and change `kafka_connect_str` to point to a Kafka broker (often localhost), and `zk_connect_str` to point to ZooKeeper.

The next step is to configure the consumer groups for which you'd like to collect metrics. Start by changing `my_consumer` to the name of your consumer group. Then configure the topics and partitions to watch, by changing `my_topic` to the name of your topic, and placing the partitions to watch in the adjacent array, separated by commas. You can then add more consumer groups or topics, as needed. Be mindful of your whitespace, as YAML files are whitespace-sensitive. After configuring your consumer groups, save and close the file.

### Verify configuration settings


To check that Datadog, Kafka, and ZooKeeper are properly integrated, first [restart the Agent](https://docs.datadoghq.com/agent/), and then run the Datadog `info` command. The command for each platform is available [here](https://docs.datadoghq.com/agent/). If the configuration is correct, you will see a section resembling the one below in the `info` output:


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


### Enable the integration


Next, click the Kafka and ZooKeeper **Install Integration** buttons inside your Datadog account, under the *Configuration* tab in the [Kafka integration settings](https://app.datadoghq.com/account/settings#integrations/kafka) and [ZooKeeper integration settings](https://app.datadoghq.com/account/settings#integrations/zookeeper).

{{< inline-cta text="Analyze Kafka metrics alongside data from the rest of your stack with Datadog." btn-text="Try it free" data-event-category="Signup" signup="true" >}}

Metrics!
--------


Once the Agent begins reporting metrics, you will see a comprehensive Kafka dashboard among your [list of available dashboards in Datadog](https://app.datadoghq.com/dash/list).

The default Kafka dashboard, as seen at the top of this article, displays the key metrics highlighted in our [introduction on how to monitor Kafka](https://www.datadoghq.com/blog/monitoring-kafka-performance-metrics/).

You can easily create a more comprehensive dashboard to monitor your entire web stack by adding additional graphs and metrics from your other systems. For example, you might want to graph Kafka metrics alongside [metrics from HAProxy](https://www.datadoghq.com/blog/monitoring-haproxy-performance-metrics), or alongside host-level metrics such as memory usage on application servers. To start building a custom dashboard, clone the default Kafka dashboard by clicking on the gear on the upper right of the dashboard and selecting **Clone Dash**.

{{< img src="clone-dash.png" alt="Monitor Kafka - Clone dash" popup="true" >}}

Alerting
--------


Once Datadog is capturing and visualizing your metrics, you will likely want to [set up some alerts](https://docs.datadoghq.com/monitors/) to be automatically notified of potential issues.

With our powerful [outlier detection](https://www.datadoghq.com/blog/introducing-outlier-detection-in-datadog/) feature, you can get alerted on the things that matter. For example, you can set an alert if a particular producer is experiencing an increase in latency while the others are operating normally.

Datadog can monitor individual hosts, containers, services, processes—or virtually any combination thereof. For instance, you can view all of your Kafka brokers, consumers, producers, or all hosts in a certain availability zone, or even a single metric being reported by all hosts with a specific tag.

Conclusion
----------


In this post we’ve walked you through integrating Kafka with Datadog to visualize your [key metrics](https://www.datadoghq.com/blog/monitoring-kafka-performance-metrics/) and [notify the right team](https://docs.datadoghq.com/monitors/notifications/) whenever your infrastructure shows signs of trouble.

If you’ve followed along using your own Datadog account, you should now have improved visibility into what’s happening in your environment, as well as the ability to create automated alerts tailored to your infrastructure, your usage patterns, and the metrics that are most valuable to your organization.

If you don’t yet have a Datadog account, you can <a href="#" class="sign-up-trigger">sign up for a free trial</a> and start to monitor Kafka right away.
___
*Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/kafka/monitor-kafka-with-datadog.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues).*
