---

*This post is part 4 of a 4-part series on monitoring Hadoop health and performance. [Part 1](https://www.datadoghq.com/blog/hadoop-architecture-overview/) gives a general overview of Hadoop's architecture and subcomponents, [Part 2](https://www.datadoghq.com/blog/monitor-hadoop-metrics/) dives into the key metrics to monitor, and [Part 3](https://www.datadoghq.com/blog/collecting-hadoop-metrics/) details how to monitor Hadoop performance natively.*

If you’ve already read our post on collecting Hadoop metrics, you’ve seen that you have several options for ad hoc performance checks. For a more comprehensive view of your cluster's health and performance, however, you need a monitoring system that continually collects Hadoop statistics, events, and metrics, that lets you identify both recent and long-term performance trends, and that can help you quickly resolve issues when they arise.

This post will show you how to set up detailed Hadoop monitoring by installing the Datadog Agent on your Hadoop nodes.

{{< img src="default-dash2.png" alt="Hadoop dashboard image" popup="true" >}}

With Datadog, you can collect Hadoop metrics for visualization, alerting, and full-infrastructure correlation. Datadog will automatically collect the key metrics discussed in parts [two](https://www.datadoghq.com/blog/monitor-hadoop-metrics/) and [three](https://www.datadoghq.com/blog/collecting-hadoop-metrics/) of this series, and make them available in a [template dashboard](https://www.datadoghq.com/dashboarding/), as seen above.

## Integrating Datadog, Hadoop, and ZooKeeper

### Verify Hadoop and ZooKeeper status
Before you begin, you should verify that all Hadoop components, including ZooKeeper, are up and running.

#### Hadoop
To verify that all of the Hadoop processes are started, run `sudo jps` on your NameNode, ResourceManager, and DataNodes to return a list of the running services.

Each service should be running a process which bears its name, i.e. `NameNode` on NameNode, etc:

    [hadoop@sandbox ~]$ sudo jps
      2354 NameNode
      [...]

#### ZooKeeper
For ZooKeeper, you can run this one-liner which uses the [4-letter-word](https://zookeeper.apache.org/doc/trunk/zookeeperAdmin.html#The+Four+Letter+Words) `ruok`:

`echo ruok | nc <ZooKeeperHost> 2181`

If ZooKeeper responds with `imok`, you are ready to install the Agent.

### Install the Datadog Agent
The Datadog Agent is the [open source software](https://github.com/DataDog/dd-agent) that collects and reports metrics from your hosts so that you can view and monitor them in Datadog. Installing the Agent usually takes just a single command.

Installation instructions for a variety of platforms are available [here](https://app.datadoghq.com/account/settings#agent).

As soon as the Agent is up and running, you should see your host reporting metrics in your [Datadog account](https://app.datadoghq.com/infrastructure).

{{< img src="default-host.png" alt="Agent reporting in" popup="true" size="1x" >}}

### Configure the Agent
Next you will need to create Agent configuration files for your Hadoop infrastructure. In the [Agent configuration directory](http://docs.datadoghq.com/guides/basic_agent_usage/), you will find template configuration files for the NameNode, DataNodes, MapReduce, YARN, and ZooKeeper. If your services are running on their default ports (50075 for DataNodes, 50070 for NameNode, 8088 for the ResourceManager, and 2181 for ZooKeeper), you can copy the templates without modification to create your config files.

On your NameNode:<br>
`cp hdfs_namenode.yaml.example hdfs_namenode.yaml`

On your DataNodes:<br>
`cp hdfs_namenode.yaml.example hdfs_namenode.yaml`

On your (YARN) ResourceManager:<br>
`cp mapreduce.yaml.example mapreduce.yaml`<br>
`cp yarn.yaml.example yarn.yaml`

Lastly, on your ZooKeeper nodes:<br>
`cp zk.yaml.example zk.yaml`

*Windows users: use copy in place of cp*

### Verify configuration settings
To verify that all of the components are properly integrated, on each host [restart the Agent](http://docs.datadoghq.com/guides/basic_agent_usage/) and then run the Datadog [`info`](http://docs.datadoghq.com/guides/basic_agent_usage/) command. If the configuration is correct, you will see a section resembling the one below in the `info` output,:

    Checks
      
      ======
      [...]
          hdfs_datanode
          -------------
            - instance #0 [OK]
            - Collected 10 metrics, 0 events & 2 service checks
          hdfs_namenode
          -------------
            - instance #0 [OK]
            - Collected 23 metrics, 0 events & 2 service checks
      
          mapreduce
          ---------
            - instance #0 [OK]
            - Collected 4 metrics, 0 events & 2 service checks
      
          yarn
          ----
            - instance #0 [OK]
            - Collected 38 metrics, 0 events & 4 service checks


### Enable the integrations


Next, click the **Install Integration** button for [HDFS](https://app.datadoghq.com/account/settings#integrations/hdfs), [MapReduce](https://app.datadoghq.com/account/settings#integrations/mapreduce), [YARN](https://app.datadoghq.com/account/settings#integrations/yarn), and [ZooKeeper](https://app.datadoghq.com/account/settings#integrations/zookeeper) under the *Configuration* tab in each technology's integration settings page.

{{< img src="install-integration.png" alt="Install Hadoop integration" size="1x" >}}

Show me the metrics!
--------------------


Once the Agent begins reporting metrics, you will see a comprehensive Hadoop dashboard among your [list of available dashboards in Datadog](https://app.datadoghq.com/dash/list).

The Hadoop dashboard, as seen at the top of this article, displays the key metrics highlighted in our [introduction on how to monitor Hadoop](https://www.datadoghq.com/blog/hadoop-architecture-overview/).

{{< img src="zk-dash.png" alt="ZooKeeper dashboard image" popup="true" >}}

The default ZooKeeper dashboard above displays the key metrics highlighted in our [introduction on how to monitor Hadoop](https://www.datadoghq.com/blog/hadoop-architecture-overview/).

You can easily create a more comprehensive dashboard to monitor your entire data-processing infrastructure by adding additional graphs and metrics from your other systems. For example, you might want to graph Hadoop metrics alongside metrics from [Cassandra](https://www.datadoghq.com/blog/how-to-monitor-cassandra-performance-metrics/) or [Kafka](https://www.datadoghq.com/blog/monitoring-kafka-performance-metrics/), or alongside host-level metrics such as memory usage on application servers. To start building a custom dashboard, clone the template Hadoop dashboard by clicking on the gear on the upper right of the dashboard and selecting **Clone Dash**.

{{< img src="clone-dash.png" alt="Clone dashboard image" popup="true" >}}

Alerting
--------


Once Datadog is capturing and visualizing your metrics, you will likely want to [set up some alerts](http://docs.datadoghq.com/guides/monitoring/) to be automatically notified of potential issues.

Datadog can monitor individual hosts, containers, services, processes—or virtually any combination thereof. For instance, you can view all of your DataNodes, NameNodes, and containers, or all nodes in a certain availability zone, or even a single metric being reported by all hosts with a specific tag. Datadog can also monitor Hadoop events, so you can be notified if jobs fail or take abnormally long to complete.

Start monitoring today
----------------------


In this post we’ve walked you through integrating Hadoop with Datadog to visualize your [key metrics](https://www.datadoghq.com/blog/hadoop-architecture-overview/) and [set alerts](http://docs.datadoghq.com/guides/monitoring/) so you can keep your Hadoop jobs running smoothly. If you’ve followed along using your own Datadog account, you should now have improved visibility into your data-processing infrastructure, as well as the ability to create automated alerts tailored to the metrics and events that are most important to you. If you don’t yet have a Datadog account, you can <a href="#" class="sign-up-trigger">sign up for a free trial</a> and start monitoring Hadoop right away.

*Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/hadoop/monitoring_hadoop_with_datadog.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues).*
