---
authors:
- email: paul.gottschling@datadoghq.com
  name: Paul Gottschling
  image: paulgottschling.jpg

blog/category:
- series datadog
blog/tag:
- rabbitmq
- amqp
- message broker
- performance
date: 2018-01-24T00:00:00Z
description: "See your RabbitMQ performance metrics in the context of your infrastructure with Datadog."
draft: false
image: 160509_RabbitMQ-03.png
meta_title: RabbitMQ monitoring with Datadog
preview_image: 160509_RabbitMQ-03.png
slug: monitoring-rabbitmq-performance-with-datadog
technology: rabbitmq
title: Monitoring RabbitMQ performance with Datadog
series: rabbitmq-monitoring
---
In Part 2 of this series, we've seen how RabbitMQ [ships with tools][part2] for monitoring different aspects of your application: how your queues handle message traffic, how your nodes consume memory, whether your consumers are operational, and so on. While RabbitMQ plugins and built-in tools give you a view of your messaging setup in isolation, RabbitMQ weaves through the very design of your applications. To better understand your applications, you need to see how RabbitMQ performance relates to the rest of your stack.

Datadog gives you an all-at-once view of key RabbitMQ metrics, out of the box, with our RabbitMQ dashboard. You can also set alerts to notify you when the availability of your messaging setup is at stake. In this post we'll show you how to set up comprehensive monitoring using Datadog's RabbitMQ integration.

{{< img src="rabbitmq-performance-screenboard.png" alt="RabbitMQ Performance - Out-of-the-box screenboard for RabbitMQ" popup="true" wide="true" >}}

## Installing the Agent
The Datadog Agent checks your host for RabbitMQ performance metrics and sends them to Datadog. The Agent can also capture metrics and trace requests from the rest of the systems running on your hosts. Instructions for installing the Agent are [here][install-agent]. For some systems this only takes a single command. Check our [documentation][agent-docs] for more details on the Agent.

## Integrating Datadog with RabbitMQ
The RabbitMQ integration is based on the [management plugin][management-plugin] (see [Part 2][part2]), which creates a [web server][http-api] that reports metrics from its host node and any nodes clustered with it. To configure the integration, first [enable][part2management] the RabbitMQ management plugin. Then follow the integration's [instructions][install-integration] for adding a configuration file.

You'll want to edit the configuration file to reflect the setup of your hosts. A basic config looks like this:

```
init_config:

instances:
    -  rabbitmq_api_url: http://localhost:15672/api/
       rabbitmq_user: datadog
       rabbitmq_pass: some_password
```
The configuration file gives the Agent access to the management API. Within the `instances` section, change `rabbitmq_api_url` to match the address of the management web server, which should have permission to accept requests from the Agent's domain (see [Part 2][part2api]). Monitoring a cluster of RabbitMQ nodes requires that only one node exposes metrics to the Agent. The node will aggregate data from its peers in the cluster. For RabbitMQ versions 3.0 and later, port 15672 is the default.

While an API URL is required, a user is optional. If you provide one, make sure you've declared it within the server. Follow [this][rabbitmq-users] documentation to create users and assign privileges. If your system has more than 100 nodes or 200 queues, you'll want to specify the nodes and queues the Agent will check. See our [template][template-config] for examples of how to do this, along with other configuration options.

Once you've [restarted the Agent][agent-restart], RabbitMQ should be reporting metrics, events, and service checks to Datadog. Verify this by running the [info command][agent-info] and making sure the "Checks" section has an entry for "rabbitmq".

```
    rabbitmq (5.21.0)
    -----------------
      - instance #0 [OK]
      - Collected 33 metrics, 0 events & 2 service checks
```

Since the integration is based on the RabbitMQ management plugin, it gathers most of the same metrics. See [Part 1][part1] for what this entails, and our [documentation][rabbitmq-integration-docs] for a full list of metrics.

The integration tags node-level metrics with the name of a node and queue-level metrics with the name of a queue. You can graph metrics by node or queue to help you diagnose RabbitMQ performance issues and compare metrics across your application.

## The RabbitMQ dashboard
Because the RabbitMQ integration gathers metrics from the management plugin, it can take data that the plugin reports as static values and plot it over time. 

For instance, the integration can use Datadog's built-in tags to visualize the memory consumption of either one or all of your queues. This example uses the demo application from [Part 2][part2], which handles data related to different boroughs in New York City. Our application queries an API, publishes the resulting JSON to a queue, consumes from the queue to aggregate the data by borough, then publishes to a final queue, where the data waits for a database to store it.

{{< img src="rabbitmq-performance-mem-by-queue.png" alt="RabbitMQ Performance - Top list of memory use by RabbitMQ queue" >}}

Graphing memory consumption is especially useful because of the way RabbitMQ handles the sizes of messages (see [Part 1][part1-connection-performance]). You can see whether your messages take up more memory as they're processed, even as queue depths remain constant.

You can also use the RabbitMQ integration to correlate metrics for your queues with system-level metrics outside the scope of the RabbitMQ management plugin. The integration's [out-of-the-box timeboard][timeboard] makes it easy to compare your network traffic, system load, system memory, and CPU usage with the state of your queues over time.

## Alerts
Once you are collecting and visualizing RabbitMQ metrics, you can set alerts in Datadog to notify your team of performance issues.

As we've discussed in [Part 1][part1], RabbitMQ will [block connections][alarms] when its nodes use too many resources. With Datadog, you can identify resource shortages and use alerts to give your team time to respond.

To do this, determine the level of memory or disk use at which RabbitMQ will start blocking connections. You may want to check your [configuration file][config-rabbitmq] for the value of `vm_memory_high_watermark` or `disk_free_limit`. Then set an alert to trigger when that threshold is approaching. In the screenshot below, we've set an alert threshold for memory use at 35 percent, a bit less than the 40-percent threshold at which RabbitMQ triggers an internal alarm.

In the example below, our Datadog alert is set to trigger on a _percentage_ of available memory, which is the unit that RabbitMQ uses for its own internal [memory alarms][memory-alarms]. RabbitMQ's [disk alarm][disk-alarms] is different, based on the absolute number of bytes available, so you would use a single metric, `rabbitmq.node.disk_free`, to set a Datadog alert for disk usage. 

{{< img alt="RabbitMQ Performance - Setting an alert for memory alarms" src="rabbitmq-performance-advanced-rabbitmq-alert.png" popup="true" wide="true" >}}

Datadog will notify your team using the channel of your choice (Slack, PagerDuty, OpsGenie, etc.) when RabbitMQ approaches its disk or memory limit.

With Datadog [forecasts][forecasts], you can predict when RabbitMQ will reach a resource threshold and set alerts for a certain time in advance. For example, you can fire off a notification two weeks before RabbitMQ is likely to set a disk alarm, giving your team enough time to take action.

{{< img src="rabbitmq-performance-forecast-graph.png" alt="RabbitMQ Performance - Setting a forecast alert" >}}

## Distributed messaging, unified monitoring
In this post, we've shown how to install the Datadog Agent and the RabbitMQ integration. We've learned how to view RabbitMQ metrics in the context of your infrastructure, and how to alert your team of approaching resource issues.

Using Datadog, you can observe all aspects of your RabbitMQ setup, all in one place. And with more than {{< translate key="integration_count" >}} supported integrations for out-of-the-box monitoring, it's possible to see your RabbitMQ performance metrics alongside those of related systems like [OpenStack][monitor-openstack]. If you don’t yet have a Datadog account, you can sign up for a <a href="#" class="sign-up-trigger">free trial</a> and start monitoring your applications and infrastructure today.

[agent-docs]: https://docs.datadoghq.com/agent/

[agent-info]: https://help.datadoghq.com/hc/en-us/articles/203764635-Agent-Status-and-Information

[agent-restart]: https://help.datadoghq.com/hc/en-us/articles/203764515-Start-Stop-Restart-the-Datadog-Agent

[alarms]: https://www.rabbitmq.com/alarms.html

[amqp-reference]: https://www.rabbitmq.com/amqp-0-9-1-reference.html

[bunny]: https://github.com/ruby-amqp/bunny

[config-rabbitmq]: https://www.rabbitmq.com/configure.html

[ddtrace]: https://github.com/DataDog/dd-trace-rb

[disk-alarms]: https://www.rabbitmq.com/disk-alarms.html

[distributed-tracing]: http://www.rubydoc.info/gems/ddtrace/#Distributed_Tracing

[event-exchange]: https://www.rabbitmq.com/event-exchange.html

[forecasts]: https://www.datadoghq.com/blog/forecasts-datadog/

[http-api]:https://www.rabbitmq.com/management.html#http-api

[install-agent]: https://app.datadoghq.com/account/settings#agent

[install-integration]: https://docs.datadoghq.com/integrations/rabbitmq/#connect-the-agent

[integration-events]: https://docs.datadoghq.com/integrations/rabbitmq/#events

[management-plugin]: http://www.rabbitmq.com/management.html

[manual-instrumentation]: http://www.rubydoc.info/gems/ddtrace/#Manual_Instrumentation

[memory-alarms]: https://www.rabbitmq.com/memory.html

[monitor-openstack]: https://www.datadoghq.com/blog/openstack-monitoring-datadog/

[part1]: /blog/rabbitmq-monitoring/

[part1-connection-performance]: /blog/rabbitmq-monitoring/#connection-performance

[part2]: /blog/rabbitmq-monitoring-tools/

[part2api]: /blog/rabbitmq-monitoring-tools/#http-api

[part2management]: /blog/rabbitmq-monitoring-tools/#the-management-plugin

[rabbitmq-users]: https://www.rabbitmq.com/rabbitmqctl.8.html#User_Management

[rabbitmq-integration-docs]: https://docs.datadoghq.com/integrations/rabbitmq/

[ruby-distrib-tracing]: http://www.rubydoc.info/gems/ddtrace/#Distributed_Tracing

[template-config]: https://github.com/DataDog/integrations-core/blob/master/rabbitmq/conf.yaml.example

[timeboard]: https://app.datadoghq.com/dash/integration/37/rabbitmq---metrics