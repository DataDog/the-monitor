Kafka deployments often rely on additional software packages not included in the Kafka codebase itself—in particular, Apache ZooKeeper. A comprehensive monitoring implementation includes all the layers of your deployment so you have visibility into your Kafka cluster and your ZooKeeper ensemble, as well as your producer and consumer applications and the hosts that run them all. To implement ongoing, meaningful monitoring, you will need a platform where you can collect and analyze your Kafka metrics, logs, and distributed request traces alongside monitoring data from the rest of your infrastructure.

{{< img src="dash1.png" alt="Monitor Kafka - Kafka dashboard" popup="true" border="true" >}}

With Datadog, you can collect metrics, logs, and traces from your Kafka deployment to visualize and alert on the performance of your entire Kafka stack. Datadog automatically collects many of the key metrics discussed in [Part 1](/blog/monitoring-kafka-performance-metrics/) of this series, and makes them available in a template dashboard, as seen above.

## Integrating Datadog, Kafka, and ZooKeeper
In this section, we'll describe how to install the Datadog Agent to collect metrics, logs, and traces from your Kafka deployment. First you'll need to ensure that Kafka and ZooKeeper are sending JMX data, then install and configure the Datadog Agent on each of your producers, consumers, and brokers.

### Verify Kafka and ZooKeeper
Before you begin, you must verify that Kafka is [configured to report metrics via JMX](/blog/collecting-kafka-performance-metrics#collect-kafka-performance-metrics-with-jconsole). Confirm that Kafka is sending JMX data to your chosen JMX port, and then connect to that port with JConsole.

Similarly, check that ZooKeeper is sending JMX data to its designated port by connecting with JConsole. You should see data from the MBeans described in [Part 1](/blog/monitoring-kafka-performance-metrics/). 

### Install the Datadog Agent
The Datadog Agent is [open source software](https://github.com/DataDog/datadog-agent) that collects metrics, logs, and distributed request traces from your hosts so that you can view and monitor them in Datadog. Installing the Agent usually takes just a [single command](https://app.datadoghq.com/account/settings#agent).

Install the Agent on each host in your deployment—your Kafka brokers, producers, and consumers, as well as each host in your ZooKeeper ensemble. Once the Agent is up and running, you should see each host reporting metrics in your [Datadog account](https://app.datadoghq.com/infrastructure).

{{< img src="kafka-host.png" alt="Datadog helps you Monitor Kafka. Once you've installed the Agent, Datadog's infrastructure page displays your Kafka hosts' status, CPU usage, I/O wait time, load, and running apps." popup="true" >}}

### Configure the Agent
Next you will need to create Agent configuration files for both Kafka and ZooKeeper. You can find the location of the Agent configuration directory for your OS [here](https://docs.datadoghq.com/agent/guide/agent-configuration-files/?tab=agentv6v7#agent-configuration-directory). In that directory, you will find sample configuration files for Kafka and ZooKeeper. To monitor Kafka with Datadog, you will need to edit both the [Kafka](https://github.com/DataDog/integrations-core/blob/master/kafka/datadog_checks/kafka/data/conf.yaml.example) and [Kafka consumer](https://github.com/DataDog/integrations-core/blob/master/kafka_consumer/datadog_checks/kafka_consumer/data/conf.yaml.example) Agent integration files. (See [the documentation](https://docs.datadoghq.com/integrations/faq/troubleshooting-and-deep-dive-for-kafka/#datadog-kafka-integrations) for more information on how these two integrations work together.) The configuration file for the Kafka integration is in the **kafka.d/** subdirectory, and the Kafka consumer integration's configuration file is in the **kafka_consumer.d/** subdirectory. The  [ZooKeeper integration](https://github.com/DataDog/integrations-core/blob/master/zk/datadog_checks/zk/data/conf.yaml.example) has its own configuration file, located in the **zk.d/** subdirectory.

On each host, copy the sample YAML files in the relevant directories (the **kafka.d/** and **kafka_consumer.d/** directories on your brokers, and the **zk.d/** directory on ZooKeeper hosts) and save them as **conf.yaml**.

The **kafka.d/conf.yaml** file includes a list of Kafka metrics to be collected by the Agent. You can use this file to configure the Agent to monitor your brokers, producers, and consumers. Change the `host` and `port` values (and `user` and `password`, if necessary) to match your setup. 

You can add [tags](https://docs.datadoghq.com/tagging/) to the YAML file to apply custom dimensions to your metrics. This allows you to search and filter your Kafka monitoring data in Datadog. Because a Kafka deployment is made up of multiple components—brokers, producers, and consumers—it can be helpful to use some tags to identify the deployment as a whole, and other tags to distinguish the role of each host. The sample code below uses a `role` tag to indicate that these metrics are coming from a Kafka broker, and a `service` tag to place the broker in a broader context. The service value here—`signup_processor`—could be shared by this deployment's producers and consumers.

{{< code-snippet lang="text" wrap="false" >}}
    tags:
      - role: broker
      - service: signup_processor
{{< /code-snippet >}}



Next, in order to get broker and consumer offset information into Datadog, modify the  **kafka_consumer/conf.yaml** file to match your setup. If your Kafka endpoint differs from the default (`localhost:9092`), you'll need to update the `kafka_connect_str` value in this file. If you want to monitor specific consumer groups within your cluster, you can specify them in the `consumer_groups` value; otherwise, you can set `monitor_unlisted_consumer_groups` to `true` to tell the Agent to fetch offset values from all consumer groups.
#### Collect Kafka and ZooKeeper logs
You can also configure the Datadog Agent to collect logs from Kafka and ZooKeeper. The Agent's log collection is disabled by default, so first you'll need to modify the Agent's [configuration file](https://docs.datadoghq.com/agent/guide/agent-configuration-files/?tab=agentv6v7) to set `logs_enabled: true`. 

Next, in Kafka's **conf.yaml** file, uncomment the [`logs`](https://github.com/DataDog/integrations-core/blob/master/kafka/datadog_checks/kafka/data/conf.yaml.example#L94-L115) section and modify it if necessary to match your broker's configuration. Do the same in ZooKeeper's **conf.yaml** file, updating the [tags](https://github.com/DataDog/integrations-core/blob/master/zk/datadog_checks/zk/data/conf.yaml.example#L20-L27) section and the [logs](https://github.com/DataDog/integrations-core/blob/master/zk/datadog_checks/zk/data/conf.yaml.example#L45-L65) section to direct the Agent to collect and tag your ZooKeeper logs and send them to Datadog.

In both of the **conf.yaml** files, you should modify the `service` tag to use a common value so that Datadog aggregates logs from all the components in your Kafka deployment. Here is an example of how this looks in a Kafka configuration file that uses the same `service` tag we applied to Kafka metrics in the previous section:

{{< code-snippet lang="text" wrap="false" >}}
logs:
  - type: file
    path: /var/log/kafka/server.log
    source: kafka
    service: signup_processor
{{< /code-snippet >}}

Note that the default `source` value in the Kafka configuration file is `kafka`. Similarly, ZooKeeper's configuration file contains `source: zookeeper`. This allows Datadog to apply the appropriate [integration pipeline](https://docs.datadoghq.com/logs/processing/pipelines/) to parse the logs and extract key attributes.

You can then filter your logs to display only those from the `signup_processor` service, making it easy to correlate logs from different components in your deployment so you can troubleshoot quickly. 
 #### Collect distributed traces
Datadog APM and distributed tracing gives you [expanded visibility](https://www.datadoghq.com/blog/announcing-apm/) into the performance of your services by measuring request volume and latency. You create graphs and alerts to monitor your APM data, and you can visualize the activity of a single request in a flame graph like the one shown below to better understand the sources of latency and errors.

{{< img src="datadog-kafka-traces.png" alt="A flame graph in Datadog APM shows a request trace from a Kafka consumer." border="true" >}}

Datadog APM can [trace  requests](https://docs.datadoghq.com/tracing/setup/java/#networking-framework-compatibility) to and from Kafka clients, and will automatically instrument popular languages and web frameworks. This means you can collect traces without modifying the source code of your producers and consumers. See the [documentation](https://docs.datadoghq.com/tracing/setup/) for guidance on getting started with APM and distributed tracing.


### Verify configuration settings
To check that Datadog, Kafka, and ZooKeeper are properly integrated, first [restart the Agent](https://docs.datadoghq.com/agent/guide/agent-commands/?tab=agentv6v7), and then run the [`status`](https://docs.datadoghq.com/agent/) command. If the configuration is correct, the output will contain a section resembling the one below:

{{< code-snippet lang="text" wrap="false" >}}
	Running Checks
	======

	  [...]



    kafka_consumer (2.3.0)
    ----------------------
      Instance ID: kafka_consumer:55722fe61fb7f11a [OK]
      Configuration Source: file:/etc/datadog-agent/conf.d/kafka_consumer.d/conf.yaml
      Total Runs: 1
      Metric Samples: Last Run: 0, Total: 0
      Events: Last Run: 0, Total: 0
      Service Checks: Last Run: 0, Total: 0
      Average Execution Time : 13ms


	  [...]

    zk (2.4.0)
    ----------
      Instance ID: zk:8cd6317982d82def [OK]
      Configuration Source: file:/etc/datadog-agent/conf.d/zk.d/conf.yaml
      Total Runs: 1,104
      Metric Samples: Last Run: 29, Total: 31,860
      Events: Last Run: 0, Total: 0
      Service Checks: Last Run: 1, Total: 1,104
      Average Execution Time : 6ms
      metadata:
        version.major: 3
        version.minor: 5
        version.patch: 7
        version.raw: 3.5.7-f0fdd52973d373ffd9c86b81d99842dc2c7f660e
        version.release: f0fdd52973d373ffd9c86b81d99842dc2c7f660e
        version.scheme: semver

========
JMXFetch
========

  Initialized checks
  ==================
    kafka
      instance_name : kafka-localhost-9999
      message : 
      metric_count : 61
      service_check_count : 0
      status : OK
{{< /code-snippet >}}
### Enable the integration
Next, click the Kafka and ZooKeeper **Install Integration** buttons inside your Datadog account, under the **Configuration** tab in the [Kafka integration settings](https://app.datadoghq.com/account/settings#integrations/kafka) and [ZooKeeper integration settings](https://app.datadoghq.com/account/settings#integrations/zookeeper).

{{< inline-cta text="Analyze Kafka metrics alongside data from the rest of your stack with Datadog." btn-text="Try it free" data-event-category="Signup" signup="true" >}}
## Monitoring your Kafka deployment in Datadog
Once the Agent begins reporting metrics from your deployment, you will see a comprehensive Kafka dashboard among your [list of available dashboards in Datadog](https://app.datadoghq.com/dashboard/lists).

The default Kafka dashboard, as seen at the top of this article, displays the key metrics highlighted in our [introduction on how to monitor Kafka](/blog/monitoring-kafka-performance-metrics/).

You can easily create a more comprehensive dashboard to monitor your entire web stack by adding additional graphs and metrics from your other systems. For example, you might want to graph Kafka metrics alongside [metrics from HAProxy](https://www.datadoghq.com/blog/monitoring-haproxy-performance-metrics) or host-level metrics such as memory usage. To start customizing this dashboard, clone it by clicking on the gear in the upper right and selecting **Clone dashboard...**.

{{< img src="clone-dashboard.png" alt="A screenshot shows the menu in the upper right of the Kafka dashboard and highlights the Clone dashboard link." popup="true" border="true" >}}

You can click on a graph in the dashboard to quickly view related logs or traces. Or you can navigate to the [Log Explorer](https://docs.datadoghq.com/logs/explorer/?tab=logsearch) to search and filter your Kafka and ZooKeeper logs—along with logs from any other technologies you're monitoring with Datadog. The screenshot below shows a stream of logs from a Kafka deployment and highlights a log showing Kafka identifying a log segment to be deleted in accordance with its configured retention policy. You can use Datadog [Log Analytics](https://docs.datadoghq.com/logs/explorer/analytics/?tab=timeseries) and create [log-based metrics](https://www.datadoghq.com/blog/log-based-metrics/) to gain insight into the performance of your entire technology stack.

{{< img src="datadog-kafka-zookeeper-logs.png" alt="Log Explorer shows a list of ZooKeeper and Kafka logs, and highlights a Kafka log that details Kafka's action loading a log partition." border="true" popup="true" >}}

Once Datadog is capturing and visualizing your metrics, logs, and APM data, you will likely want to [set up some alerts](https://docs.datadoghq.com/monitors/) to be automatically notified of potential issues.

With our powerful [outlier detection](https://www.datadoghq.com/blog/introducing-outlier-detection-in-datadog/) feature, you can get alerted on the things that matter. For example, you can set an alert to notify you if a particular producer is experiencing an increase in latency while the others are operating normally.
## Get started monitoring Kafka with Datadog 
In this post, we’ve walked you through integrating Kafka with Datadog to monitor [key metrics](/blog/monitoring-kafka-performance-metrics/), logs, and traces from your environment.  If you’ve followed along using your own Datadog account, you should now have improved visibility into Kafka health and performance, as well as the ability to create automated alerts tailored to your infrastructure, your usage patterns, and the data that is most valuable to your organization.

If you don’t yet have a Datadog account, you can <a href="#" class="sign-up-trigger">sign up for a free trial</a> and start to monitor Kafka right away.
___
*Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/kafka/monitor-kafka-with-datadog.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues).*

