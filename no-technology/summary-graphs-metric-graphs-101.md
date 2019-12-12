# Metric graphs 101: Summary graphs


*This is the second post in a series about visualizing monitoring data. This post focuses on summary graphs.*

In the [first part](https://www.datadoghq.com/blog/timeseries-metric-graphs-101/) of this series, we discussed timeseries graphs—visualizations that show infrastructure metrics evolving through time. In this post we cover summary graphs, which are visualizations that **flatten** a particular span of time to provide a summary window into your infrastructure:

-   [Single-value summaries](#singlevalue-summaries)
-   [Toplists](#toplists)
-   [Change graphs](#change-graphs)
-   [Host maps](#host-maps)
-   [Distributions](#distributions)

For each graph type, we’ll explain how it works and when to use it. But first, we’ll quickly discuss two concepts that are necessary to understand infrastructure summary graphs: aggregation across time (which you can think of as “time flattening” or “snapshotting”), and aggregation across space.


## Aggregation across time

To provide a summary view of your metrics, a visualization must flatten a timeseries into a single value by compressing the time dimension out of view. This *aggregation across time* can mean simply displaying the latest value returned by a metric query, or a more complex aggregation to return a computed value over a moving time window.

For example, instead of displaying only the latest reported value for a metric query, you may want to display the maximum value reported by each host over the past 60 minutes to surface problematic spikes:

{{< img src="redis-toplist1.png" alt="Redis latency graphs" popup="true" size="1x" >}}


## Aggregation across space

Not all metric queries make sense broken out by host, container, or other unit of infrastructure. So you will often need some *aggregation across space* to create a metric visualization that sensibly reflects your infrastructure. This aggregation can take many forms: aggregating metrics by messaging queue, by database table, by application, or by some attribute of your hosts themselves (operating system, availability zone, hardware profile, etc.).

Aggregation across space allows you to slice and dice your infrastructure to isolate exactly the metrics that make your key systems [observable](https://en.wikipedia.org/wiki/Observability).

Instead of listing peak Redis latencies at the host level as in the example above, it may be more useful to see peak latencies for each internal service that is built on Redis. Or you can surface only the maximum value reported by any one host in your infrastructure:

{{< img src="redis-toplist3.png" alt="Redis latency graphs" caption="Aggregation across space: grouping hosts by service name (top) or compressing a list of hosts to a single value (bottom)" size="1x" >}}

Aggregation across space is also useful in [timeseries graphs](https://www.datadoghq.com/blog/timeseries-metric-graphs-101/). For instance, it is hard to make sense of a host-level graph of web requests, but the same data is easily interpreted when the metrics are aggregated by availability zone:

{{< img src="redis-agg-space2.png" alt="Redis latency graphs" caption="From unaggregated (line graph, top) to aggregated across space (stacked area graph, bottom)" size="1x" >}}

The primary reason to [tag your metrics](https://www.datadoghq.com/blog/the-power-of-tagged-metrics/) is to enable aggregation across space.

## Single-value summaries

Single-value summaries display the current value of a given metric query, with conditional formatting (such as a green/yellow/red background) to convey whether or not the value is in the expected range. The value displayed by a single-value summary need not represent an instantaneous measurement. The widget can display the latest value reported, or an aggregate computed from all query values across the time window. These visualizations provide a narrow but unambiguous window into your infrastructure.

{{< img src="single-annotated4.png" alt="Host count widget" popup="true" size="1x" >}}

### When to use single-value summaries
<table>
<thead>
<tr class="header">
<th>What</th>
<th>Why</th>
<th>Example</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><strong><a href="https://www.datadoghq.com/blog/monitoring-101-collecting-data/">Work metrics</a></strong> from a given system</td>
<td>To make key metrics immediately visible</td>
<td style="width:300px">Web server requests per second{{< img src="nginx_req_g.png" alt="NGINX requests per second" popup="true" img_param="?w=300">}}</td>
</tr>
<tr class="even">
<td>Critical <strong><a href="https://www.datadoghq.com/blog/monitoring-101-collecting-data/">resource metrics</a></strong></td>
<td>To provide an overview of resource status and health at a glance</td>
<td>Healthy hosts behind load balancer{{< img src="elb_host_g.png" alt="Total ELB host count" popup="true" >}}</td>
</tr>
<tr class="odd">
<td><strong>Error metrics</strong></td>
<td>To quickly draw attention to potential problems</td>
<td>Fatal database exceptions{{< img src="cass_unavailable.png" alt="Cassandra unavailable exceptions" popup="true" >}}</td>
</tr>
<tr class="even">
<td>Computed <strong>metric changes</strong> as compared to previous values</td>
<td>To communicate key trends clearly</td>
<td>Hosts in use versus one week ago{{< img src="ec2_host_growth.png" alt="Increase in EC2 hosts" popup="true" >}}</td>
</tr>
</tbody>
</table>



## Toplists

[Toplists](https://www.datadoghq.com/blog/easy-ranking-new-top-lists/) are ordered lists that allow you to rank hosts, clusters, or any other segment of your infrastructure by their metric values. Because they are so easy to interpret, toplists are especially useful in high-level status boards.

Compared to single-value summaries, toplists have an additional layer of aggregation across space, in that the value of the metric query is broken out by group. Each group can be a single host or an aggregation of related hosts.

{{< img src="toplist-annotated2.png" alt="Max Redis latency per AZ" popup="true" size="1x" >}}

### When to use toplists
<table>
<thead>
<tr class="header">
<th>What</th>
<th>Why</th>
<th>Example</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><strong><a href="https://www.datadoghq.com/blog/monitoring-101-collecting-data/">Work or resource metrics</a></strong> taken from different hosts or groups</td>
<td>To spot outliers, underperformers, or resource overconsumers at a glance</td>
<td style="width:300px">Points processed per app server{{< img src="sobo_throughput.png" alt="Server toplist" popup="true" >}}</td>
</tr>
<tr class="even">
<td><strong>Custom metrics</strong> returned as a list of values</td>
<td>To convey KPIs in an easy-to-read format (e.g. for status boards on wall-mounted displays)</td>
<td>Versions of the Datadog agent in use{{< img src="agent_version.png" alt="Agent version toplist" popup="true" >}}</td>
</tr>
</tbody>
</table>

## Change graphs

Whereas toplists give you a summary of recent metric values, [change graphs](https://www.datadoghq.com/blog/metrics-better-or-worse-than-before/) compare a metric’s current value against its value at a point in the past.

The key difference between change graphs and other visualizations is that change graphs take two different timeframes as parameters: one for the size of the evaluation window and one to set the lookback window.

{{< img src="change-annotated6.png" alt="Login failures change graph" popup="true" size="1x" >}}

### When to use change graphs
<table>
<thead>
<tr class="header">
<th>What</th>
<th>Why</th>
<th>Example</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><strong>Cyclic metrics</strong> that rise and fall daily, weekly, or monthly</td>
<td>To separate metric trends from periodic baselines</td>
<td style="width:300px">Database write throughput, compared to same time last week{{< img src="cass_writes.png" alt="Cassandra write throughput" popup="true" >}}</td>
</tr>
<tr class="even">
<td><strong>High-level</strong> infrastructure metrics</td>
<td>To quickly identify large-scale trends</td>
<td>Total host count, compared to same time yesterday{{< img src="ec2_change.png" alt="EC2 host count change graph" popup="true" >}}</td>
</tr>
</tbody>
</table>


## Host maps

[Host maps](https://www.datadoghq.com/blog/introducing-host-maps-know-thy-infrastructure/) are a unique way to observe your entire infrastructure, or any slice of it, at a glance. However you slice and dice your infrastructure (by data center, by service name, by instance type, etc.), you will see each host in the selected group as a hexagon, color-coded and sized by any metrics reported by those hosts.

This particular visualization type is unique to Datadog. As such, it is specifically designed for infrastructure monitoring, in contrast to the general-purpose visualizations described elsewhere in this article.

{{< img src="hostmap-annotated4.png" alt="Host map by instance type" popup="true" size="1x" >}}

### When to use host maps
<table>
<thead>
<tr>
<th>
What

</th>
<th>
Why

</th>
<th>
Example

</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Resource utilization</strong> metrics</td>
<td>
To spot overloaded components at a glance
</td>
<td style="width:300px">
Load per app host, grouped by cluster{{< img src="load_cluster2.png" alt="Load per cluster host map" popup="true" >}}

</td>
</tr>
<tr>
<td>
</td>
<td colspan="2">
<hr>

</td>
</tr>
<tr>
<td>
</td>
<td>
To identify resource misallocation (e.g. whether any instances are over- or undersized)

</td>
<td>
CPU usage per EC2 instance type{{< img src="instance_hostmap.png" alt="CPU per instance type" popup="true" >}}

</td>
</tr>
<tr>
<td>
<strong>Error or other <a href="/blog/monitoring-101-collecting-data">work</a></strong> metrics

</td>
<td>
To quickly identify degraded hosts

</td>
<td>
HAProxy 5xx errors per server{{< img src="haproxy_5xx.png" alt="Server errors per HAProxy hosy" popup="true" >}}

</td>
</tr>
<tr>
<td>
<strong>Related<strong> metrics

</td>
<td>
To see correlations in a single graph

</td>
<td>
App server throughput versus memory used{{< img src="throughput-vs-memory.png" alt="Server errors per HAProxy host" popup="true" >}}

</td>
</tr>
</tbody>
</table>


## Distributions

[Distribution graphs](https://docs.datadoghq.com/graphing/#distribution) show a histogram of a metric’s value across a segment of infrastructure. Each bar in the graph represents a range of binned values, and its height corresponds to the number of entities reporting values in that range.

Distribution graphs are closely related to [heat maps](https://www.datadoghq.com/blog/timeseries-metric-graphs-101/#heat-maps). The key difference between the two is that heat maps show change over time, whereas distributions are a summary of a time window. Like heat maps, distributions handily visualize large numbers of entities reporting a particular metric, so they are often used to graph metrics at the individual host or container level.

{{< img src="distribution-annotated6.png" alt="Latency per web server" popup="true" size="1x" >}}

### When to use distributions
<table>
<thead>
<tr>
<th>
What

</th>
<th>
Why

</th>
<th>
Example

</th>
</tr>
</thead>
<tbody>
<tr>
<td>
<strong>Single metric</strong> reported by a large number of entities

</td>
<td>
To convey general health or status at a glance

</td>
<td style="width:300px">
Web latency per host{{< img src="latency-distro.png" alt="Latency per host distribution" popup="true" >}}

</td>
</tr>
<tr>
<td>
</td>
<td colspan="2">

<hr>

</td>
</tr>
<tr>
<td>
</td>
<td>
To see variations across members of a group

</td>
<td>
Uptime per host{{< img src="uptime.png" alt="Uptime per server distribution" popup="true" >}}

</td>
</tr>
</tbody>
</table>


## Wrap-up

Each of these specialized visualization types has unique benefits and use cases, as we’ve shown here. Understanding all the visualizations available to you, and when to use each type, will help you convey actionable information clearly in your dashboards.

In the next article in this series, we’ll explore common anti-patterns in metric visualization (and, of course, how to avoid them).
