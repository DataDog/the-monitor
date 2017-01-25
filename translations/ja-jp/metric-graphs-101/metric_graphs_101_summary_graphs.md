*This is the second post in a series about visualizing monitoring data. This post focuses on summary graphs.* 

In the [first part][part-1] of this series, we discussed timeseries graphs—visualizations that show infrastructure metrics evolving through time. In this post we cover summary graphs, which are visualizations that ​**flatten**​ a particular span of time to provide a summary window into your infrastructure:

* [Single-value summaries](#single-value-summaries)
* [Toplists](#toplists)
* [Change graphs](#change-graphs)
* [Host maps](#host-maps)
* [Distributions](#distributions)

For each graph type, we’ll explain how it works and when to use it. But first, we’ll quickly discuss two concepts that are necessary to understand infrastructure summary graphs: aggregation across time (which you can think of as "time flattening" or "snapshotting"), and aggregation across space.

## Aggregation across time

To provide a summary view of your metrics, a visualization must flatten a timeseries into a single value by compressing the time dimension out of view. This *aggregation across time* can mean simply displaying the latest value returned by a metric query, or a more complex aggregation to return a computed value over a moving time window. 

For example, instead of displaying only the latest reported value for a metric query, you may want to display the maximum value reported by each host over the past 60 minutes to surface problematic spikes:

[![Redis latency graphs][toplevel-agg-time]][toplevel-agg-time]

## Aggregation across space

Not all metric queries make sense broken out by host, container, or other unit of infrastructure. So you will often need some *aggregation across space* to sensibly visualize your metrics. This aggregation can take many forms: aggregating metrics by messaging queue, by database table, by application, or by some attribute of your hosts themselves (operating system, availability zone, hardware profile, etc.). 

Aggregation across space allows you to slice and dice your infrastructure to isolate exactly the metrics that matter most to you. 

Instead of listing peak Redis latencies at the host level as in the example above, it may be more useful to see peak latencies for each internal service that is built on Redis. Or you can surface only the maximum value reported by any one host in your infrastructure:

![Redis latency graphs][toplevel-agg-snapshot] *Aggregation across space: grouping hosts by service name (top) or compressing a list of hosts to a single value (bottom)*

Aggregation across space is also useful in [timeseries graphs][part-1]. For instance, it is hard to make sense of a host-level graph of web requests, but the same data is easily interpreted when the metrics are aggregated by availability zone:

![Redis latency graphs][toplevel-agg-timeseries] *From unaggregated (line graph, top) to aggregated across space (stacked area graph, bottom)*

The primary reason to [tag your metrics][value-of-tagging] is to enable aggregation across space.

## Single-value summaries

Single-value summaries display the current value of a given metric query, with conditional formatting (such as a green/yellow/red background) to convey whether or not the value is in the expected range. The value displayed by a single-value summary need not represent an instantaneous measurement. The widget can display the latest value reported, or an aggregate computed from all query values across the time window.

[![Host count widget][single-annotated]][single-annotated]

### When to use single-value summaries

<table>
<thead>
<tr>
<th>What</th>
<th>Why</th>
<th>Example</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong><a href="https://www.datadoghq.com/blog/monitoring-101-collecting-data/">Work metrics</a></strong> from a given system</td>
<td>To make key metrics immediately visible</td>
<td>Web server requests per second<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/nginx_req_g.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/300/nginx_req_g.png" alt="NGINX requests per second" /></a></td>
</tr>
<tr>
<td>Critical <strong><a href="https://www.datadoghq.com/blog/monitoring-101-collecting-data/">resource metrics</a></strong></td>
<td>To provide an overview of resource status and health at a glance</td>
<td>Healthy hosts behind load balancer<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/elb_host_g.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/300/elb_host_g.png" alt="Total ELB host count" /></a></td>
</tr>
<tr>
<td><strong>Error metrics</strong></td>
<td>To quickly draw attention to potential problems</td>
<td>Fatal database exceptions<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/cass_unavailable.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/300/cass_unavailable.png" alt="Cassandra unavailable exceptions" /></a></td>
</tr>
<tr>
<td>Computed <strong>metric changes</strong> as compared to previous values</td>
<td>To communicate key trends clearly</td>
<td>Hosts in use versus one week ago<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/ec2_host_growth.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/300/ec2_host_growth.png" alt="Increase in EC2 hosts" /></a></td>
</tr>
</tbody>
</table>

## Toplists

[Toplists][toplists] are ordered lists that allow you to rank hosts, clusters, or any other segment of your infrastructure by their metric values. Because they are so easy to interpret, toplists are especially useful in high-level status boards. 

Compared to single-value summaries, toplists have an additional layer of aggregation across space, in that the value of the metric query is broken out by group. Each group can be a single host or an aggregation of related hosts.

[![Max Redis latency per AZ][toplist-annotated]][toplist-annotated]

### When to use toplists

<table>
<thead>
<tr>
<th>What</th>
<th>Why</th>
<th>Example</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong><a href="https://www.datadoghq.com/blog/monitoring-101-collecting-data/">Work or resource metrics</a></strong> taken from different hosts or groups</td>
<td>To spot outliers, underperformers, or resource overconsumers at a glance</td>
<td>Points processed per app server<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/sobo_throughput.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/300/sobo_throughput.png" alt="Server toplist" /></a></td>
</tr>
<tr>
<td><strong>Custom metrics</strong> returned as a list of values</td>
<td>To convey KPIs in an easy-to-read format (e.g. for status boards on wall-mounted displays)</td>
<td>Versions of the Datadog agent in use<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/agent_version.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/300/agent_version.png" alt="Agent version toplist" /></a></td>
</tr>
</tbody>
</table>

## Change graphs

Whereas toplists give you a summary of recent metric values, [change graphs][change-graphs] compare a metric's current value against its value at a point in the past. 

The key difference between change graphs and other visualizations is that change graphs take two different timeframes as parameters: one for the size of the evaluation window and one to set the lookback window. 

[![Login failures change graph][change-annotated]][change-annotated]

### When to use change graphs

<table>
<thead>
<tr>
<th>What</th>
<th>Why</th>
<th>Example</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Cyclic metrics</strong> that rise and fall daily, weekly, or monthly</td>
<td>To separate metric trends from periodic baselines</td>
<td>Database write throughput, compared to same time last week<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/cass_writes.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/300/cass_writes.png" alt="Cassandra write throughput" /></a></td>
</tr>
<tr>
<td><strong>High-level</strong> infrastructure metrics</td>
<td>To quickly identify large-scale trends</td>
<td>Total host count, compared to same time yesterday<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/ec2_change.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/300/ec2_change.png" alt="EC2 host count change graph" /></a></td>
</tr>
</tbody>
</table>

## Host maps

[Host maps][hostmaps] are a unique way to see your entire infrastructure, or any slice of it, at a glance. However you slice and dice your infrastructure (by data center, by service name, by instance type, etc.), you will see each host in the selected group as a hexagon, color-coded and sized by any metrics reported by those hosts.

This particular visualization type is unique to Datadog. As such, it is specifically designed for infrastructure monitoring, in contrast to the general-purpose visualizations described elsewhere in this article.

[![Host map by instance type][hostmap-annotated]][hostmap-annotated]

### When to use host maps

<table>
<thead>
<tr>
<th>What</th>
<th>Why</th>
<th>Example</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Resource utilization</strong> metrics</td>
<td>To spot overloaded components at a glance</td>
<td>Load per app host, grouped by cluster<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/load_cluster2.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/300/load_cluster2.png" alt="Load per cluster host map" /></a></td>
</tr>
<tr>
<td></td>
<td colspan="2">
<hr />
</td>
</tr>
<tr>
<td></td>
<td>To identify resource misallocation (e.g. whether any instances are over- or undersized)</td>
<td>CPU usage per EC2 instance type<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/instance_hostmap.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/300/instance_hostmap.png" alt="CPU per instance type" /></a></td>
</tr>
<tr>
<td><strong>Error or other <a href="https://www.datadoghq.com/blog/monitoring-101-collecting-data/">work</a></strong> metrics</td>
<td>To quickly identify degraded hosts</td>
<td>HAProxy 5xx errors per server<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/haproxy_5xx.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/300/haproxy_5xx.png" alt="Server errors per HAProxy hosy" /></a></td>
</tr>
<tr>
<td><strong>Related</strong> metrics</td>
<td>To see correlations in a single graph</td>
<td>App server throughput versus memory used<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/throughput-vs-memory.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/300/throughput-vs-memory.png" alt="Server errors per HAProxy host" /></a></td>
</tr>
</tbody>
</table>

## Distributions

[Distribution graphs][distribution-docs] show a histogram of a metric's value across a segment of infrastructure. Each bar in the graph represents a range of binned values, and its height corresponds to the number of entities reporting values in that range.

Distribution graphs are closely related to [heat maps][part-1-heat-maps]. The key difference between the two is that heat maps show change over time, whereas distributions are a summary of a time window. Like heat maps, distributions handily visualize large numbers of entities reporting a particular metric, so they are often used to graph metrics at the individual host or container level. 

[![Latency per web server][distribution-annotated]][distribution-annotated]

### When to use distributions

<table>
<thead>
<tr>
<th>What</th>
<th>Why</th>
<th>Example</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Single metric</strong> reported by a large number of entities</td>
<td>To convey general health or status at a glance</td>
<td>Web latency per host<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/latency-distro.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/300/latency-distro.png" alt="Latency per host distribution" /></a></td>
</tr>
<tr>
<td></td>
<td colspan="2">
<hr />
</td>
</tr>
<tr>
<td></td>
<td>To see variations across members of a group</td>
<td>Uptime per host<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/uptime.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/300/uptime.png" alt="Uptime per server distribution" /></a></td>
</tr>
</tbody>
</table>

## Wrap-up

Each of these specialized visualization types has unique benefits and use cases, as we've shown here. Understanding all the visualizations available to you, and when to use each type, will help you convey actionable information clearly in your dashboards.

In the next article in this series, we'll explore common anti-patterns in metric visualization (and, of course, how to avoid them).


[part-1]: https://www.datadoghq.com/blog/timeseries-metric-graphs-101/
[toplists]: https://www.datadoghq.com/blog/easy-ranking-new-top-lists/
[change-graphs]: https://www.datadoghq.com/blog/metrics-better-or-worse-than-before/
[hostmaps]: https://www.datadoghq.com/blog/introducing-host-maps-know-thy-infrastructure/
[distribution-docs]: http://docs.datadoghq.com/graphing/#distribution
[part-1-heat-maps]: https://www.datadoghq.com/blog/timeseries-metric-graphs-101/#heat-maps
[toplevel-agg-time]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/redis-toplist1.png
[toplevel-agg-timeseries]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/redis-agg-space2.png
[toplevel-agg-snapshot]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/redis-toplist3.png
[value-of-tagging]: https://www.datadoghq.com/blog/the-power-of-tagged-metrics/
[single-annotated]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/single-annotated4.png
[toplist-annotated]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/toplist-annotated2.png
[change-annotated]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/change-annotated6.png
[hostmap-annotated]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/hostmap-annotated4.png
[distribution-annotated]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-01-graphing-101/pt2/distribution-annotated6.png
