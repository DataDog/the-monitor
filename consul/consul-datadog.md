# How to monitor Consul with Datadog
In [Part 1][part1], we walked you through key metrics for monitoring Consul, and in [Part 2][part2], we showed you how to use Consul's built-in monitoring tools to get insights from your cluster. In this post, we'll show you how you can use Datadog to visualize your Consul metrics in custom dashboards, analyze your Consul logs, and set up alerts on your cluster's availability and performance. With more than {{< translate key="integration_count" >}} [integrations][dd-integrations], Datadog gives you deep visibility into Consul—and all of the applications that rely on Consul for service discovery and dynamic configuration—in a single platform. We'll explain how to:

1. Set up the [Consul integration](#get-started-with-datadog-and-consul) 
2. Use [Datadog dashboards](#realtime-views-of-consul-cluster-status) to get visibility into multiple components of Consul—and the rest of your system
3. Collect, search, and analyze [Consul logs](#analyze-all-your-consul-logs-in-one-place)
4. Alert on unhealthy nodes and volatile leadership with [Consul monitors](#maintain-a-healthy-consul-cluster-with-datadog-alerts)

{{< img src="oob-dash.png" caption="The out-of-the-box dashboard for Consul." popup="true" border="true" >}}

## Get started with Datadog and Consul
The Datadog Agent is [open source software][dd-agent-github] that runs [on your hosts][dd-agent], reporting metrics, traces, and logs to Datadog. The Agent pulls Consul metrics as well as system metrics from each node in your cluster. To install the Agent on each of your Consul hosts, follow the instructions for your environment within your [Datadog account][dd-agent-install].

### Configure Consul metric collection
The Consul integration is [built into][integrations-core] the Datadog Agent, and requires only a few configuration changes, explained in the Datadog [documentation][dd-integration-config]. 

First, tell your Consul agents where to send their metrics. The Datadog Agent ingests metrics with an aggregation service called [DogStatsD][dogstatsd], and you will need to provide the address of this service to Consul. For each host you'd like to report metrics to Datadog, add the following to your Consul configuration (assuming DogStatsD is running locally on your Consul host):

{{< code-snippet lang="json" wrap="false" >}}
"telemetry": {
  "dogstatsd_addr": "127.0.0.1:8125"
}
{{</ code-snippet >}}

This instructs Consul to declare a [metrics sink for DogStatsD][go-metrics-dogstatsd] with the [Golang package][go-metrics-sinks] it uses to expose metrics, meaning that any metrics Consul generates will go to DogStatsD in addition to the default in-memory sink. The DogStatsD sink uses the [DogStatsD client for Golang][dogstatsd-go] to flush metrics [every 10 seconds][dogstatsd-flush] to Datadog, where they are retained for {{< translate key="retention" >}} (whereas Consul's default in-memory sink only has a one-minute retention period). Make sure to stop and restart Consul ([rather than running][consul-config-reload] `consul reload`) after changing your `telemetry` configuration.

Next, configure the Datadog Agent to access your Consul metrics by editing the **conf.yaml.example** [template file][dd-integration-example] in the **consul.d** subdirectory of your Datadog Agent (the location varies across platforms—refer to the [docs][dd-check-config]). Copy and rename this file as **conf.yaml**, and update it with the location of your Consul HTTP server. The Datadog Agent listens for Consul metrics locally from port 8500 by default. 

You can edit **conf.yaml** to collect additional metrics and events from Consul using options such as the following:

1. `self_leader_check: true`: emit events when a [new leader is elected](#maintain-a-healthy-consul-cluster)
2. `network_latency_checks: true`: collect the [estimated][consul-coords] duration of requests from a given node to others
3. `catalog_checks: true`: query the Consul catalog for counts of nodes and services; metrics will be tagged by `mode:leader` or `mode:follower` (as applicable), meaning that you can use these metrics to alert on the loss of a leader 

After making your changes, **conf.yaml** should resemble the following. You can find a full list of options within [**conf.yaml.example**][dd-integration-example].

{{< code-snippet lang="yaml" filename="conf.yaml" wrap="false" >}}
init_config:

instances:
    - url: http://localhost:8500
      self_leader_check: true
      network_latency_checks: true
      catalog_checks: true
{{</ code-snippet >}}

Datadog allows you to group and filter data using [tags][dd-tags]. The Consul integration tags all metrics with `consul_datacenter`, and we have shown how certain Consul metrics are tagged with `mode:leader` or `mode:follower`. 

You can also configure the Datadog Agent to tag all of the metrics from its local host, helping you isolate host-level metrics from your Consul cluster when creating alerts and visualizations. To do this, add a custom key-value pair to the `tags` section of your Agent [configuration file][dd-agent-config-file] (**datadog.yaml**). The Host Map shown [below](#realtime-views-of-consul-cluster-status) uses the host-level `consul_cluster` tag to visualize CPU utilization per host in the cluster.

{{< code-snippet lang="yaml" filename="datadog.yaml" wrap="false" >}}
tags:
  - consul_cluster:consul-demo
{{</ code-snippet >}}

[Restart the Datadog Agent][dd-agent-restart] to apply these configuration changes.

### Enable log collection
Consul's logs provide insights into internal operations such as membership changes and the status of Raft elections (see [Part 2][part2]), and aggregating and analyzing these logs with Datadog can help you diagnose issues. To [enable log collection][dd-consul-logs], revise your Datadog Agent [configuration file][dd-agent-config-file] (**datadog.yaml**) to include the following:

{{< code-snippet lang="yaml" filename="datadog.yaml" >}}
  logs_enabled: true
{{</ code-snippet >}}

Then update the `logs` section of your Consul integration configuration file (e.g., **consul.d/conf.yaml**) to include the following:

{{< code-snippet lang="yaml" filename="conf.yaml" >}}
instances:

# [...]

logs:
    - type: file
      path: <CONSUL_LOGS_DIRECTORY_PATH>/*
      source: consul
      service: <SERVICE_NAME>
{{</ code-snippet >}}

This configuration instructs Datadog to tail one or more files at the specified path. Consul automatically adds a timestamp to the name of the log file and rotates it every 24 hours (this is [configurable][consul-logs-rotate-dur]). You can use a [wildcard][dd-logs-wildcards] to configure Datadog to tail all log files (regardless of their names) within the chosen directory. 

Specifying a `source` is mandatory, and activates the out-of-the-box processing pipeline for Consul logs. The `service` key (which is also mandatory) adds a `service:` tag that you can use to group and filter your logs. You can also use this tag to correlate your Consul logs with metrics as well as [distributed traces][dd-apm] of requests to your applications. This can either be `consul` or a more specific categorization of your Consul deployment, such as  `consul-client`, `consul-server`, or `consul-demo`.

Once you've edited your configuration YAML, make sure the `dd-agent` user has [read access][dd-permission] to your log files, then [restart the Datadog Agent][dd-agent-restart] to apply the changes. You can verify that the Agent is reporting to Datadog by running the [`status` command][dd-agent-status] and looking for the `consul` section.

## Real-time views of Consul cluster status
Consul clusters are complex, and having an overview of all the components in a single dashboard can help you identify patterns and isolate issues. Datadog provides a number of ways to visualize your entire cluster at once, including an out-of-the-box dashboard that tracks [key metrics from your Consul environment][part1]. You can clone and customize this dashboard to correlate Consul and system-level metrics with information from more than {{< translate key="integration_count" >}} [other technologies][dd-integrations].
 
Datadog's [Host Map][dd-host-map] is a good starting point for visualizing resource utilization across your Consul cluster. You can group hosts by tag, making it clear when hosts belonging to a specific datacenter, service, or other part of your infrastructure require attention.

As shown below, you can filter the Host Map to display only those hosts that belong to a specific Consul cluster, using the custom `consul_cluster` tag. We can see how our hosts are performing in terms of a specific metric (in this case, CPU utilization). By identifying the scope of an issue—does it affect the whole cluster, or just a single host?—you can determine what to troubleshoot next.


{{< img src="hostmap.png" popup="true" border="true" >}}

You can then move to a detailed view of Consul metrics over time, and from different components within your cluster, using Datadog's [out-of-the-box dashboard][consul-oob-dash]. The [template variables][dd-template-vars] allow you to filter the entire dashboard to display metrics from a particular service or datacenter of your choice.



{{< img src="template-vars.png" popup="true" >}}

To bring more visibility into your own Consul environment, you can clone the dashboard to add other graph [widgets][dd-dashboard-widgets], or track data from any Datadog integration. You can show, for example, metrics from [SNMP][dd-snmp] and [DNS][dd-dns], allowing you to get more visibility into the possible causes of underperforming network connections. And if you set `network_latency_checks` to `true` within the Consul integration configuration file, you can create graphs that show network latency between a given node and others in the cluster (all metrics beginning with `consul.net` listed in [our documentation][dd-consul-metrics]).

The dashboard below combines Consul metrics with system-level metrics from each host in your cluster to provide context for troubleshooting. In this example, you can see that a drastic decline in RPCs did not accompany a rise in failed RPCs, but rather a system-wide period of unavailability.

{{< img src="consul-resource-dash.png" popup="true" border="true" >}}

If a particular Consul metric shows an unexpected change, you can click on the graph and navigate to logs from the same point in time. The next section will explain how to use Datadog log management to track and analyze all of your Consul logs.

{{< img src="logs-transition.png" border="true" >}}

## Analyze all your Consul logs in one place
Consul agents include a lot of valuable information in their logs [out of the box][part1-logs]. Since you'll have a whole cluster of agents reporting logs, collecting and analyzing them in a single platform is more efficient than SSHing into each node and reading log files locally when Consul encounters an issue. Using Datadog is also well-suited for the kind of dynamic cluster you would manage with Consul, as hosts continue to report logs even as they spin up, shut down, and change IPs, as long as they run a Datadog Agent configured to send logs to Datadog. 


{{< img src="log-explorer.png" popup="true" border="true" >}}

You may recall from [Part 2][part2] that Consul logs include several commonalities: a timestamp, the severity, the package that calls the logger, and a message, which can have various formats. Datadog's out-of-the-box processing pipeline automatically extracts attributes from your Consul logs, and enriches them with any tags specified in the `logs` section of your integration configuration file (**consul.d/conf.yaml**).


{{< img src="parsed-log.png" caption="Log collected by Datadog showing that a node hosting RabbitMQ has joined the cluster and synced its state." border="true" >}}

Since Consul's log messages are written in plain English and sometimes include variable values at different locations depending on the log, they can be difficult to aggregate. Datadog's [Log Patterns view][dd-log-patterns] can automatically find commonalities between logs, helping you figure out which kinds of logs are most common and where to take action first. 

For example, the Log Patterns view below indicates that logs carrying the message, `[WARN] manager: No servers available` are the most common over the chosen timeframe, meaning that we'll want to take further action to investigate why no server nodes have joined the cluster.

{{< img src="log-patterns.png" popup="true" border="true" >}}

## Maintain a healthy Consul cluster with Datadog alerts
While Consul already provides some automated monitoring in the form of health checks and watches, Datadog allows you to visualize all of your Consul data in context with the rest of your infrastructure, as well as to tailor your alerting strategy for your specific use case. Datadog can alert you of possible Consul incidents such as frequently failing health checks and unstable cluster leadership.

Rather than using [manual API and CLI commands][part2] to track your Consul health checks, you can let Datadog notify you of their status, and see any related metrics, traces, or logs in the same platform as the rest of your Consul data. Since Datadog monitors Consul health checks [automatically][dd-consul-checks] as Datadog [service checks][dd-service-check], you can set an alert when a certain number of checks fail within a specific period of time by [creating an integration monitor][dd-integration-monitor].

The alert below reviews Consul's last three node-level health checks (`last(3)`), counting them by status ("Alert," "OK," or "Warn") and triggering after one "Alert." You can also configure a similar alert for tracking failed service-level health checks by using the `consul_service_id` tag (pulled automatically from Consul based on the [ID of the service][consul-service-def]). A custom message gives teammates access to helpful documents and dashboards. You can use a [tag variable][dd-tag-vars] (such as `{{host.name}}`) in the dashboard link, so the incident responder can easily view metrics collected from the host that triggered the alert. 

{{< img src="alert-status.png" popup="true" border="true" >}}

Frequent leadership transitions can compromise the availability of Consul's strongly consistent data (see [Part 1][part1-leadership]), preventing cluster members from accessing network addresses and configuration details. Datadog [produces an event][dd-consul-events] whenever Consul elects a new leader (as long as `self_leader_check` is set to `true` in your Consul integration [configuration file](#get-started-with-datadog-and-consul)), making it possible to alert on a certain number of leadership transitions over a certain period of time. In the example below, we've used the `consul_datacenter` tag to trigger a separate alert for each Consul datacenter that breaches our threshold.

{{< img src="leadership-alert.png" popup="true" border="true" >}}

You can also alert on the loss of a leader node by using any Consul metric that includes the `mode` tag, which, as we [explained earlier](#configure-consul-metric-collection), can have either the value `leader` or `follower` depending on a server's state. Most of these metrics are available after enabling catalog-based checks, though you can also use the metric `consul.peers` to count the number of servers in the cluster by leader or follower status.

## Start monitoring Consul with Datadog
In this post, we've shown you how to use Datadog to get comprehensive visibility into your Consul clusters, regardless of how many hosts you're managing with Consul and how often they change. Datadog allows you to collect the output of Consul's built-in monitoring capabilities—telemetry, logs, and health checks—visualize them in a single platform, and alert on them to discover issues. If you're not already using Datadog, you can sign up for a <a href="#" class="sign-up-trigger">free trial</a> to start monitoring your Consul clusters—and all of the services that rely on them—in one platform.


<!--links-->
[consul-config-reload]: https://www.consul.io/docs/agent/options.html#reloadable-configuration
[consul-coords]: https://www.consul.io/docs/internals/coordinates.html
[consul-oob-dash]: https://app.datadoghq.com/screen/integration/83/consul---overview
[consul-logs-stdout]: https://support.hashicorp.com/hc/en-us/articles/115015668287-Where-are-my-Consul-logs-and-how-do-I-access-them
[consul-logs-rotate-dur]: https://www.consul.io/docs/agent/options.html#_log_rotate_duration
[consul-service-def]: https://www.consul.io/docs/agent/services.html
[dd-agent]: https://docs.datadoghq.com/agent/?tab=agentv6
[dd-agent-config-file]: https://docs.datadoghq.com/agent/guide/agent-configuration-files/?tab=agentv6#agent-main-configuration-file
[dd-agent-config-dir]: https://docs.datadoghq.com/agent/guide/agent-configuration-files/?tab=agentv6#agent-configuration-directory
[dd-agent-github]: https://github.com/DataDog/datadog-agent
[dd-agent-install]: https://app.datadoghq.com/account/settings#agent
[dd-agent-restart]: https://docs.datadoghq.com/agent/guide/agent-commands/?tab=agentv6#restart-the-agent
[dd-agent-status]: https://docs.datadoghq.com/agent/guide/agent-commands/?tab=agentv6#agent-status-and-information
[dd-apm]: https://docs.datadoghq.com/tracing/
[dd-check-config]: https://docs.datadoghq.com/agent/guide/agent-configuration-files/?tab=agentv6#checks-configuration-files-for-agent-6
[dd-consul-checks]: https://docs.datadoghq.com/integrations/consul/#service-checks
[dd-consul-events]: https://docs.datadoghq.com/integrations/consul/#events
[dd-consul-logs]: https://docs.datadoghq.com/integrations/consul/#log-collection
[dd-consul-metrics]: https://docs.datadoghq.com/integrations/consul/#metrics
[dd-dashboard-widgets]: https://docs.datadoghq.com/graphing/widgets/
[dd-dns]: https://docs.datadoghq.com/integrations/dns_check/
[dd-event-tags]: https://docs.datadoghq.com/integrations/consul/#events
[dd-host-map]: https://docs.datadoghq.com/graphing/infrastructure/hostmap/
[dd-integration-config]: https://docs.datadoghq.com/integrations/consul/#configuration
[dd-integration-example]: https://github.com/DataDog/integrations-core/blob/master/consul/datadog_checks/consul/data/conf.yaml.example
[dd-integration-monitor]: https://docs.datadoghq.com/monitors/monitor_types/integration/
[dd-integrations]: https://docs.datadoghq.com/integrations/
[dd-log-patterns]: https://www.datadoghq.com/blog/log-patterns/
[dd-logs-wildcards]: https://docs.datadoghq.com/logs/log_collection/?tab=tailexistingfiles#tail-multiple-directories-or-whole-directories-by-using-wildcards
[dd-permission]: https://docs.datadoghq.com/agent/faq/how-to-solve-permission-denied-errors/
[dd-service-check]: https://www.datadoghq.com/blog/alerting-101-status-checks/#service-checks
[dd-snmp]: https://docs.datadoghq.com/integrations/snmp/
[dd-tags]: https://docs.datadoghq.com/tagging/
[dd-tag-vars]: https://docs.datadoghq.com/monitors/notifications/?tab=is_alertis_warning#tag-variables
[dd-template-vars]: https://docs.datadoghq.com/graphing/dashboards/template_variables/
[dogstatsd]: https://docs.datadoghq.com/developers/dogstatsd/
[dogstatsd-flush]: https://docs.datadoghq.com/developers/dogstatsd/#how-it-works
[dogstatsd-go]: https://github.com/DataDog/datadog-go/tree/master/statsd
[go-metrics]: https://github.com/armon/go-metrics
[go-metrics-dogstatsd]: https://godoc.org/github.com/armon/go-metrics/datadog
[go-metrics-sinks]: https://github.com/armon/go-metrics#sinks
[integrations-core]: https://github.com/DataDog/integrations-core/tree/master/consul
[part1]: /blog/consul-metrics
[part1-leadership]: /blog/consul-metrics/#leadership-transitions
[part1-logs]: /blog/consul-metrics/#metrics-to-watch-consul-client-rpc-consul-client-rpc-exceeded-consul-client-rpc-failed-consul-rpc-cross-dc
[part2]: /blog/consul-monitoring-tools/
