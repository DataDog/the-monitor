# Monitoring ActiveMQ with&nbsp;Datadog


As you operate and scale ActiveMQ, comprehensive monitoring will enable you to rapidly identify any bottlenecks and maintain the flow of data through your applications. Earlier in this series, we introduced some [key ActiveMQ metrics to watch][part-1], and looked at some [tools you can use to monitor ActiveMQ][part-2]. But to get a complete understanding of ActiveMQ's performance, you should monitor your broker and destinations alongside the client applications that send and receive messages, and the infrastructure that runs it all. In this post, we'll show you how you can monitor ActiveMQ and all its related systems using Datadog.

This post will show you how to: 

* [Configure ActiveMQ](#connecting-activemq-with-datadog) to send metrics to Datadog
* View ActiveMQ metrics in a [customizable dashboard](#viewing-activemq-metrics-in-datadog)
* Collect and analyze [ActiveMQ logs in Datadog](#bringing-in-activemq-logs)
* [Tag](#tagging-your-metrics) your ActiveMQ metrics
* [Create alerts](#using-alerts-to-stay-informed) in Datadog to keep you informed

First we'll walk through how to connect your ActiveMQ infrastructure to your Datadog account. If you're new to Datadog, but you'd like to follow along, here's a <a href="#" class="sign-up-trigger">free trial</a>.

{{< img src="activemq_dash4.png" popup="true" alt="Datadog's out-of-the-box ActiveMQ dashboard graphs many key metrics." wide="true" >}}

## Connecting ActiveMQ with Datadog
This section will describe how to configure ActiveMQ to send metrics to Datadog.
To do this, you'll need to enable JMX remote monitoring, install and configure the Agent, and enable the Datadog integration.

### Monitoring JMX remotely
ActiveMQ exposes metrics [via JMX][part-2-jmx-and-jconsole]. To make those metrics available to the Agent, you need to configure your ActiveMQ host to allow secure remote access to its MBean server, as shown in these documents by [Oracle][oracle-monitoring] and [Apache][apache-jmx-ssl]. Next, you're ready to install the Agent and integrate ActiveMQ with your Datadog account.

### Installing the Agent
The Datadog Agent is open source software that runs on your host and sends metrics, traces, and logs to your Datadog account. You can often install the Agent with just a single command—see the [Agent installation instructions for your host's OS][datadog-agent-instructions] for more information. 

When you've completed the installation, you should be able to see your ActiveMQ host in the [host map][datadog-host-map]. If you're already monitoring other hosts in Datadog, type your hostname in the **Filter by** field to limit the view to just your ActiveMQ host. 

{{< img src="activemq_dash5b.png" alt="This screenshot shows how your infrastructure list looks when you've used the filter field to identify your ActiveMQ host." wide="true" >}}

Your ActiveMQ host is now sending CPU, memory, and other system-level metrics to your Datadog account. Next we'll show you how to configure the Agent to collect and send Java and ActiveMQ metrics.

### Configuring Datadog's ActiveMQ integration
In addition to exposing metrics via JMX, ActiveMQ makes metrics available in XML pages within the Web Console. The Datadog Agent collects metrics from the Web Console instead of JMX when possible. See [our documentation][datadog-activemq-docs] for a list of metrics the Agent collects from each of these two data sources, JMX and the Web Console.

By default, our integration collects the most important key metrics mentioned in Part 1, but you can also configure the Agent to collect other metrics from JMX, depending on your setup and priorities.

The Agent includes two sample ActiveMQ configuration files, one for the JMX data source and one for the Web Console data source. It's easy to modify the ActiveMQ configuration to collect JMX metrics that aren't collected by default, and to avoid collecting those that you don't need. 

In this section, we'll show you how to use the JMX configuration file to designate which metrics to collect, and how to create additional configuration files to collect additional metrics. We'll also walk through how to update the Web Console's configuration file so the Agent can access that data source.

#### Data source: JMX
The Agent stores configuration files for all integrations under its **conf.d/** subdirectory. The location of this directory depends on your host's platform. See the [Agent documentation][datadog-agent-docs] to find your **conf.d/** directory.

To configure the Agent to collect JMX metrics from ActiveMQ, and from the JVM in which it runs, you'll need to edit the config file in the **conf.d/activemq.d/** directory. Copy the [**conf.yaml.example**][github-activemq-conf-yaml] file in that directory to **conf.yaml**.  This file defines which ActiveMQ metrics the Agent will retrieve via JMX.

Each metric to be collected is listed in this file as an `attribute`. The attribute names match those listed in the "JMX attribute" column of the [key metrics tables][part-1-key-metrics] in Part 1. Each `attribute` name is followed by an `alias` line (which specifies how the metric will be labeled in Datadog) and a [`metric_type`][datadog-metric-types] line (which determines how the metric will be interpreted and visualized in Datadog). 

You can comment out or delete any `attribute`—including its `alias` and `metric_type` lines—if you want the Agent to stop collecting that metric. In the example below, we have modified **conf.yaml** so that the `AverageEnqueueTime` metric won't be collected via JMX.

```
# activemq.d/conf.yaml
instances:

  ## @param host - string - required
  ## ActiveMQ host to connect to.
  #
  - host: localhost

  ## @param port - integer - required
  ## ActiveMQ port to connect to.
  #
    port: 1099
init_config:
[...]
  conf:
    - include:
        destinationType: Queue
        attribute:
#          AverageEnqueueTime:
#            alias: activemq.queue.avg_enqueue_time
#            metric_type: gauge
          ConsumerCount:
            alias: activemq.queue.consumer_count
            metric_type: gauge
          ProducerCount:
            alias: activemq.queue.producer_count
            metric_type: gauge

```

To add a new metric to be collected, you can add its information to **conf.yaml.** The sample code below, when added to **conf.yaml**, configures the Agent to also collect a `ProducerFlowControl` metric for the topics associated with this broker.

```
[...]
    - include:
        destinationType: Topic
        attribute:
          ProducerFlowControl:
            alias: activemq.topic.producer_flow_control
            metric_type: gauge
```

Alternatively, you can create new configuration files to specify any additional metrics to be collected. You can [name a new configuration file][datadog-checks-configuration-files] anything you like, and as long as it's a valid YAML file in the **conf.d/activemq.d/** directory, the Agent will read its contents. The sample code below, saved as **conf.d/activemq.d/broker_metrics.yaml**, configures the Agent to collect the broker's `TotalDequeueCount` and `TotalEnqueueCount` metrics we introduced in [Part 1][part-1-broker-metrics] of this series.

```
# activemq.d/broker_metrics.yaml

init_config:
  is_jmx: true

  conf:
    - include:
        destinationType: Broker
        attribute:
          TotalDequeueCount:
            alias: activemq.broker.dequeue_count
            metric_type: gauge
          TotalEnqueueCount:
            alias: activemq.broker.enqueue_count
            metric_type: gauge
```

[Restart the Agent][datadog-restart] to apply your configuration changes, then execute the [`status` command][datadog-status] to confirm your changes. Look for the `activemq` section in the status output, as shown below.
```
    activemq
      instance_name : activemq-localhost-1099
      message : 
      metric_count : 93
      service_check_count : 0
      status : OK
```

#### Data source: Web Console
ActiveMQ's built-in Web Console includes three pages of XML data feeds—one each to show metrics from queues, topics, and subscribers—which the Agent uses as a data source for some metrics. The screenshot below shows a Web Console page that serves as a data source for ActiveMQ topics.

{{< img src="web_console4.png" alt="Screenshot from the web console showing an XML data feed of topics metrics." wide="true" >}}

You'll need to configure the Agent to access these pages so it can collect metrics from them.  Inside **conf.d/** is an **activemq_xml.d/** subdirectory, which includes a [configuration file][datadog-checks-configuration-files] that tells the Agent how to find the ActiveMQ Web Console to use as a source for metric data. Copy the [**conf.yaml.example**][github-activemq-xml-conf-yaml] file in that directory to a new file named **conf.yaml**. Uncomment the `username` and `password` lines. Set `username` to **admin**, and update the password to match the one you created when [setting up the ActiveMQ Web Console][part-2-activemq-web-console] in Part 2 of this series. If you've [updated your ActiveMQ configuration][activemq-web-console] to use a port other than 8161, change the port on the `url` line to reflect that. Your **conf.yaml** should look like the example below:

```
# activemq_xml.d/conf.yaml

init_config:

instances:
  - url: http://localhost:8161
    username: admin
    password: <MY_PASSWORD>
```

[Restart the Agent][datadog-restart] so your configuration changes take effect. Now your Agent is collecting metrics from the ActiveMQ Web Console and forwarding them to your Datadog account.

Execute the Agent's [`status` command][datadog-status] to confirm that your configuration changes were successful. Look for an `activemq_xml` section in the `status` output, as shown below.

```
   activemq_xml (1.0.0)
      Total Runs: 15640
      Metric Samples: 114, Total: over 1M
      Events: 0, Total: 0
      Service Checks: 0, Total: 0
      Average Execution Time : 15ms
```

If you have more than one ActiveMQ host to monitor, repeat the Agent installation and configuration steps on all your hosts. You can also use a configuration management tool like [Ansible][datadog-ansible] or [Chef][datadog-chef] to automate the deployment and configuration of the Datadog Agent.

### Installing the ActiveMQ integration
You've now configured the Agent to collect ActiveMQ metrics from JMX and from the Web Console's XML pages. You've also configured the Agent to collect metrics about the JVM's resource usage and garbage collection activity. Next, you simply need to enable the ActiveMQ and Java integrations so you can visualize and monitor these metrics. 

Visit the [ActiveMQ integration tile][datadog-activemq-integration] in your Datadog account. Click the **Configuration** tab, then scroll down and click the **Install Integration** button. Repeat these steps for the [Java integration][datadog-java-integration]. 
Now that your Datadog account is configured to collect and display ActiveMQ metrics, you're ready to visualize and alert on them. The next section will show you how to start using dashboards in Datadog to view your ActiveMQ metrics.
## Viewing ActiveMQ metrics in Datadog

As soon as you've installed the Agent and enabled the ActiveMQ integration on your account, you'll see **ActiveMQ - Overview** on your [dashboard list][datadog-activemq-dashboard]. This dashboard displays the important [broker][part-1-broker-metrics] and [destination][part-1-destination-metrics] metrics we looked at in Part 1 of this series.

The **ActiveMQ - Overview** dashboard displays statistics and trends that help you track the performance of your messaging infrastructure. Each graph on the dashboard provides information about one or more important ActiveMQ metrics, and gives you a starting point to investigate potential problems.

To get even more out of your ActiveMQ dashboard, you can customize it to display metrics from related elements of your infrastructure, such as the JVM's memory usage and thread count.

{{< img src="activemq_dash6.png" alt="Screenshot of a customized ActiveMQ dashboard showing queue size, queue memory usage, heap memory usage, and JVM thread count." wide="true" >}}

To create a custom dashboard, first clone the **ActiveMQ - Overview** dashboard by clicking the gear in the top right and selecting **Clone Dashboard**.

{{< img src="activemq_dash7d.png" alt="Screenshot of the out-of-the-box ActiveMQ dashboard, highlighting the Clone Dash button." wide="true" >}}

Click the **Edit Board** button at the top of the page to start adding the widgets you need to [graph the data][datadog-graphing] that’s important to you. You can customize your dashboard with metrics, logs, and traces from any of Datadog's {{< translate key="integration_count" >}}+ integrations to get a unified view of your entire messaging infrastructure in a single pane of glass. 

The screenshot below shows how you can add a graph to your custom dashboard that displays heap memory usage on the host named **my-activemq-host**.

{{< img src="activemq_dash8.png" alt="Screenshot of the graph editor, showing a JVM heap memory metric." wide="true" >}}

If the metric data visualized on your dashboard indicates a potential problem, your logs can be a helpful source of further information. In the next section, we'll walk through how to collect and view ActiveMQ logs.

## Bringing in ActiveMQ logs

You can correlate logs with metrics to reveal context around anomalies you see on your dashboards. In this section, we'll show you how to use Datadog to collect and process your ActiveMQ logs, so you can search, graph, analyze, and alert on them.

### Enabling log collection

First, you'll need to configure the Agent to collect logs from your ActiveMQ host. Log collection is disabled in the Agent by default, so you'll need to enable it by editing the Agent’s configuration file (**datadog.yaml**). The path to this file differs across platforms, so consult the [Agent's documentation][datadog-agent-docs] for information specific to your OS. Open the file, then uncomment and update the `logs_enabled` line to read:

```
logs_enabled: true
```

Next, [restart the Agent][datadog-restart] to begin forwarding your host's logs to your Datadog account. 

### Configuring the integration

The Agent needs to be able to find and access your ActiveMQ logs. By default, ActiveMQ stores logs in the **data/** subdirectory of your ActiveMQ installation. You can find the path to this directory in the "MBeans" tab of [JConsole][part-2-jmx-and-jconsole]. You'll see it listed as the value of the broker's `DataDirectory` JMX attribute. 

{{< img src="jconsole4.png" wide="true" alt="Screenshot of JConsole's MBeans tab, highlighting the DataDirectory attribute.">}}

Make sure the `dd-agent` user has read access to the `DataDirectory` directory, so that the Agent can access the ActiveMQ logs. 

ActiveMQ is built on Java, so you can use Datadog's Java integration to collect and process your ActiveMQ logs. Create a Java configuration file named **java.yaml** in the Agent's **conf.d/** subdirectory and add the following content, making sure to replace `<DataDirectory>` with the correct path:

```
# conf.d/java.yaml

logs:
  - type: file
    path: <DataDirectory>/activemq.log 
    service: activemq
    source: java


```

The `service: activemq` line in **java.yaml** allows you to distinguish and disaggregate these logs from any other Java logs you may be collecting (and automatically associates your logs with [APM metrics and traces][datadog-java-apm] from the same service). You can also configure Datadog to collect logs from other Java applications on this host within the same **java.yaml** file—simply create additional `- type:` blocks as necessary, and differentiate each application by giving it a unique `service` value.

Note that **java.yaml** assigns a `source` value of `java` to the ActiveMQ logs, which will automatically trigger Datadog's Java log processing [pipeline][datadog-pipeline-docs] to process them. The pipeline applies parsing rules that extract log facets and attributes. This ultimately determines how each log will be displayed, and gives you powerful ways to [search and filter your logs in Datadog][datadog-log-search]. The Java log pipeline will require your ActiveMQ logs to be written in a particular format. In the next section, we'll configure ActiveMQ to format its logs to match the pattern expected by the Java log pipeline.


Datadog will automatically tag your ActiveMQ logs with the parameters listed in your YAML file (e.g., `service:activemq` and `source:java`), and you can easily include any additional tags that are useful to you. The example below extends the `java.yaml` file from above to include two custom tags, `team` and `category`.

```
# conf.d/java.yaml

logs:
  - type: file
    path: <DataDirectory>/activemq.log 
    service: activemq
    source: java
    tags:
      - 'team:development'
      - 'category:messaging'
```

To load your updated configuration, restart the Agent by using the appropriate [command][datadog-restart] for your OS.

### Formatting logs

Datadog's log processing [pipelines][datadog-pipeline-docs] parse incoming logs to extract attributes you can use as facets to search your logs. In this section, we'll walk through updating your ActiveMQ log format to make use of the Java log pipeline.

By default, ActiveMQ logs follow a format that looks similar to the one shown here:

```
2018-10-22 20:51:51,591 | WARN  | Memory Usage for the Broker (1024mb) is more than the maximum available for the JVM: 989 mb - resetting to 70% of maximum available: 692 mb | org.apache.activemq.broker.BrokerService | main
```

To format the logs for the Java log pipeline, edit **log4j.properties** in the **conf/** subdirectory of your ActiveMQ installation. Replace the line that begins with `log4j.appender.logfile.layout.ConversionPattern=` to read as follows:

```
log4j.appender.logfile.layout.ConversionPattern=%d{yyyy-MM-dd HH:mm:ss} %-5p %c{1}:%L - %m%n
```

This new pattern tells ActiveMQ to format each log similar to the one shown here:

```
2018-10-22 20:51:51 WARN  BrokerService:2188 - Memory Usage for the Broker (1024mb) is more than the maximum available for the JVM: 989 mb - resetting to 70% of maximum available: 692 mb
```

Datadog's log pipeline for Java will recognize this format and automatically process the logs.

To apply this change, restart ActiveMQ. See the [ActiveMQ documentation][apache-activemq-getting-started] for your platform's stop and start commands.

### Viewing logs

To see all your ActiveMQ logs, visit the [Log Explorer][datadog-log-explorer-activemq] page in your Datadog account. Click on any row to see full information about a log. 

{{< img src="activemq_dash9b.png" alt="Screenshot of the log explorer, showing detail of an ActiveMQ log." wide="true" >}}

This shows the full log text, and also highlights the information that was extracted by the Java log pipeline, including the host, service, timestamp, and severity level. 

Once your ActiveMQ logs are collected and processed, you can use [log analytics][datadog-log-analytics] to reveal patterns and trends that can help you troubleshoot issues in your messaging infrastructure. You can query and display important log data as a toplist or a timeseries graph. In the screenshot below, we've used the severity level and service facets to see a toplist of the ActiveMQ hosts that generated the most `WARN` logs over the past 15 minutes. These `WARN` logs could indicate, for example, a `MemoryUsage` error like the one in the screenshot above.

{{< img src="activemq_dash10a.png" alt="Screenshot of the log analytics view in log explorer." wide="true" >}}

It's easy to add any log analytics graph to a dashboard so that you can view it alongside other metrics. Just click the **Export** button in the top-right corner to add it to a new or existing dashboard.

Log analytics allows you to explore and visualize your ActiveMQ logs in powerful new ways. For guidance on using all of Datadog's log management features, see the [documentation][datadog-log-explorer].

## Tagging your metrics

Hopefully you've already begun [using tags][datadog-tagging] to monitor your infrastructure and applications in Datadog. You can [strategically use tags][datadog-the-power-of-tagged-metrics] to create highly focused dashboards and alerts that provide fine-grained insights into every layer of your ActiveMQ environment. 

Datadog automatically tags your ActiveMQ metrics with the name of the host, and applies other useful tags that vary depending on the source of the metric. For example, each `activemq.queue.size` metric is tagged with the `queue` it came from, and `activemq.topic.size` metrics automatically get tagged with the `topic`. 

In this section, we'll walk through how to use custom tags to add more dimensions to your metrics so you can filter and aggregate them to suit your monitoring needs. Because the Datadog Agent accesses ActiveMQ metrics from JMX and the Web Console, we'll show you how to tag metrics from both sources. But first we'll demonstrate how applying custom tags can help you better understand the performance of your ActiveMQ infrastructure.

### Using custom tags

If default tags like `host` or `topic` don't give you enough information to monitor what's important in your ActiveMQ infrastructure, you can apply custom tags to add dimensions to your metrics. Custom tags give you greater control over what you can visualize and monitor.

For example, if you were operating two ActiveMQ brokers—one to process orders for a product named `A` and another for a product named `B`—you could tag the brokers according to product. As your operation scales, the ordering process for each product could require multiple hosts, perhaps even from multiple cloud providers. But your `product` tag would still allow you to visualize metrics per product. You could then customize your ActiveMQ dashboard to graph the queue size of each product in a single view. The following screenshot illustrates this example.

{{< img src="activemq_dash11.png" alt="Screenshot of a timeseries graph showing queue counts for both product A and product B." wide="true" caption="In a system that uses multiple brokers to process orders for two different products, you can use custom tags to associate each broker’s traffic with a specific product. This then allows you to track trends in the queue volume per product, across any number of hosts." >}}

Using consistent tags across your ActiveMQ logs and metrics makes it easy to correlate them in your Datadog account. In the screenshot below, the graph plots the size of queues tagged `service:activemq`. You can click on any point in the timeseries graph to easily navigate to logs that share the same `service` tag and were generated around the same time. In the upcoming sections, we'll show you how to apply the `service:activemq` tag to ActiveMQ's Web Console and JMX metrics.

{{< img src="activemq_dash12b.png" alt="Screenshot of a graph that includes a context menu you can use to navigate to view related logs." wide="true" >}}

### Tagging metrics from the Web Console

To add custom tags to metrics that come from the ActiveMQ Web Console, you'll need to edit the **activemq_xml.d/conf.yaml** file you created earlier. The sample code below adds the same `service:activemq` tag we used in the log configuration section earlier. 

```
# activemq_xml.d/conf.yaml

instances:
  - url: http://localhost:8161
    username: admin
    password: <MY_PASSWORD>
    tags:
      - 'service:activemq'
```

The process for adding custom tags to ActiveMQ's JMX metrics is similar, as we'll demonstrate in the next section.

### Tagging metrics from JMX

To add custom tags to the metrics that come from JMX, edit the **conf.yaml** file in the **activemq.d/** subdirectory under **conf.d/**. The example below adds the same `service` tag we used earlier.

```
# activemq.d/conf.yaml

instances:
  - host: localhost
    port: 1099
    tags:
      - 'service:activemq'
```

[Restart the Agent][datadog-restart] to apply the revised configuration.
 
Once you've applied custom tags to your metrics, you can start using them to create more targeted graphs and alerts. In the next section, we'll walk through how to set up alerts in Datadog.

## Using alerts to stay informed

Alerts keep you informed of potential issues in your ActiveMQ infrastructure. You can use tags in your alert definitions to create more focused and actionable alerts. Using our custom `product` tag from the example in the previous section, the screenshot below illustrates how you could set up an alert that will trigger if the `QueueSize` metric rises above 10,000 only on queues tagged with `product:a`.

{{< img src="activemq_alert1.png" alt="Screenshot showing the controls you use to create a new alert." wide="true" >}}

You can set up alerts to automatically monitor any of the key ActiveMQ metrics we identified in Part 1 of this series. The example below shows a [forecast alert][datadog-forecast-monitoring] that will trigger if the broker's `TempPercentUsage` value is expected to rise above 80% in the next week. If this alert triggers, you may need to scale out your fleet of consumers to reduce the number of messages in the queue, or revise your broker configuration to increase the available storage space (`tempUsage`).

{{< img src="activemq_alert2e.png" alt="Screenshot showing the controls you use to create a new alert." wide="true" >}}

You can integrate your Datadog account with PagerDuty, Slack, and many other [notification][datadog-integration-notification] and [collaboration][datadog-integration-collaboration] services to make these alerts visible to your team. 

## Start monitoring

Monitoring ActiveMQ in isolation gives you only part of the information you need to keep your infrastructure performing well. You can use Datadog's dashboards, alerts, and log management features to monitor your whole messaging infrastructure—brokers, destinations, clients, and the hosts that run it all. If you're not already using Datadog, get started with a <a href="#" class="sign-up-trigger">free 14-day trial</a>.

_Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/activemq/monitoring-activemq-with-datadog.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues)._

[activemq-web-console]: http://activemq.apache.org/web-console.html
[apache-activemq-getting-started]: http://activemq.apache.org/version-5-getting-started.html#Version5GettingStarted-StartingActiveMQStartingActiveMQ
[apache-jmx-ssl]: https://db.apache.org/derby/docs/10.9/adminguide/radminjmxenablepwdssl.html
[datadog-activemq-dashboard]: https://app.datadoghq.com/dashboard/lists?q=activemq
[datadog-activemq-docs]: https://docs.datadoghq.com/integrations/activemq/
[datadog-activemq-integration]: https://app.datadoghq.com/account/settings#integrations/activemq
[datadog-agent-docs]: https://docs.datadoghq.com/agent/basic_agent_usage/
[datadog-agent-instructions]: https://app.datadoghq.com/account/settings#agent
[datadog-ansible]: https://www.datadoghq.com/blog/deploy-datadog-ansible-reporting/
[datadog-checks-configuration-files]: https://docs.datadoghq.com/agent/faq/agent-configuration-files/?tab=agentv6#checks-configuration-files-for-agent-6
[datadog-chef]: https://www.datadoghq.com/blog/deploying-datadog-with-chef-roles/
[datadog-forecast-monitoring]: https://docs.datadoghq.com/monitors/monitor_types/forecasts/
[datadog-graphing]: https://docs.datadoghq.com/graphing/
[datadog-host-map]: https://app.datadoghq.com/infrastructure/map
[datadog-integration-collaboration]: https://docs.datadoghq.com/integrations/#cat-collaboration
[datadog-integration-notification]: https://docs.datadoghq.com/integrations/#cat-notification
[datadog-java-apm]: https://www.datadoghq.com/blog/java-monitoring-apm/
[datadog-java-integration]: https://app.datadoghq.com/account/settings#integrations/java
[datadog-log-analytics]: https://docs.datadoghq.com/logs/explorer/analytics/
[datadog-log-explorer]: https://docs.datadoghq.com/logs/explorer/
[datadog-log-explorer-activemq]: https://app.datadoghq.com/logs?query=service%3Aactivemq
[datadog-log-search]: https://docs.datadoghq.com/logs/explorer/search/
[datadog-metric-types]: https://docs.datadoghq.com/developers/metrics/#metric-types
[datadog-pipeline-docs]: https://docs.datadoghq.com/logs/processing/pipelines/
[datadog-restart]: https://docs.datadoghq.com/agent/faq/agent-commands/?tab=agentv6#start-stop-restart-the-agent
[datadog-status]: https://docs.datadoghq.com/agent/faq/agent-commands/?tab=agentv6#agent-status-and-information
[datadog-tagging]: https://docs.datadoghq.com/tagging/
[datadog-the-power-of-tagged-metrics]: https://www.datadoghq.com/blog/the-power-of-tagged-metrics/ 
[github-activemq-conf-yaml]: https://github.com/DataDog/integrations-core/blob/master/activemq/datadog_checks/activemq/data/conf.yaml.example
[github-activemq-xml-conf-yaml]: https://github.com/DataDog/integrations-core/blob/master/activemq_xml/datadog_checks/activemq_xml/data/conf.yaml.example
[oracle-monitoring]: https://docs.oracle.com/javase/10/management/monitoring-and-management-using-jmx-technology.htm
[part-1]: /blog/activemq-architecture-and-metrics/
[part-2]: /blog/collecting-activemq-metrics/
[part-1-broker-metrics]: /blog/activemq-architecture-and-metrics/#broker-metrics
[part-1-destination-metrics]: /blog/activemq-architecture-and-metrics/#destination-metrics
[part-1-key-metrics]: /blog/activemq-architecture-and-metrics/#key-activemq-metrics
[part-2-jmx-and-jconsole]: /blog/collecting-activemq-metrics/#collecting-activemq-metrics-with-jmx-and-jconsole
[part-2-activemq-web-console]: /blog/collecting-activemq-metrics/#activemq-web-console
[yaml-documentation]: https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html
