# Metric graphs 101: Timeseries graphs


*This is the first post in a series about visualizing monitoring data. This post focuses on timeseries graphs.*

[Observability](https://en.wikipedia.org/wiki/Observability) is not just about *having* monitoring data—that data must be easily available and interpretable. Choosing the right visualization for your data is an important part of providing human-readable representations of the health and performance of your systems. There is no one-size-fits-all solution: you can see different things in the same metric with different graph types.

To help you effectively visualize your metrics, this first post explores four different types of timeseries graphs, which have time on the x-axis and metric values on the y-axis:



-   [Line graphs](#line-graphs)
-   [Stacked area graphs](#stacked-area-graphs)
-   [Bar graphs](#bar-graphs)
-   [Heat maps](#heat-maps)



For each graph type, we'll explain how it works, when to use it, and when to use something else.

## Line graphs


{{< img src="key-pg-classic.png" alt="Line graph" popup="true" img_param="?w=900&fit=min" pop_param="?w=1090&fit=min" size="1x" >}}

Line graphs are the simplest way to translate metric data into visuals, but often they're used by default when a different graph would be more appropriate. For instance, a graph of wildly fluctuating metrics from hundreds of hosts quickly becomes harder to disentangle than steel wool. It's nearly impossible to draw any useful conclusions about your systems from a graph like that.

### When to use line graphs




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
<td>The same metric reported by <strong>different scopes</strong></td>
<td>To spot outliers at a glance</td>
<td>CPU idle for each host in a cluster{{< img src="cpu-idle-host.png" alt="CPU idle per host" popup="true" >}}</td>
</tr>
<tr class="even">
<td>Tracking <strong>single metrics</strong> from one source, or as an aggregate</td>
<td>To clearly communicate a key metric's evolution over time</td>
<td>Median latency across all web servers{{< img src="latency-spike.png" alt="Median webapp latency" popup="true" >}}</td>
</tr>
<tr class="odd">
<td>Metrics for which <strong>unaggregated values</strong> from a particular slice of your infrastructure are especially valuable</td>
<td>To spot individual deviations into unacceptable ranges</td>
<td>Disk space utilization per database node{{< img src="cass-disk-rising.png" alt="Disk space per node" popup="true" >}}</td>
</tr>
<tr class="even">
<td><strong>Related metrics</strong> sharing the same units</td>
<td>To spot correlations within a system</td>
<td>Latency for disk reads and disk writes on the same machine{{< img src="disk-lat.png" alt="Read and write latency" popup="true" >}}</td>
</tr>
<tr class="odd">
<td>Metrics that have a clear <strong>acceptable domain</strong></td>
<td>To easily spot unacceptable degradations</td>
<td>Latency for processing web requests{{< img src="key-pg-lat.png" alt="Key page latency" popup="true" >}}</td>
</tr>
</tbody>
</table>



### When to use something else




<table>
<thead>
<tr class="header">
<th>What</th>
<th>Example</th>
<th>Instead use...</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Highly variable metrics reported by a <strong>large number of sources</strong></td>
<td>CPU from all hosts{{< img src="cpu-bad.png" alt="Noisy CPU line graph" popup="true" >}}</td>
<td>Heat maps to make noisy data more interpretable{{< img src="cpu-good.png" alt="CPU heat map" popup="true" >}}</td>
</tr>
<tr class="even">
<td>Metrics that are <strong>more actionable as aggregates</strong> than as separate data points</td>
<td>Web requests per second over dozens of web servers{{< img src="nginx-bad.png" alt="Web server requests per node" popup="true" >}}</td>
<td>Area graphs to aggregate across tagged groups{{< img src="nginx-good.png" alt="Web server requests per availability zone" popup="true" >}}</td>
</tr>
<tr class="odd">
<td>Metrics that are <strong>often equal to zero</strong></td>
<td>Metrics tracking relatively rare S3 access errors{{< img src="errors-bad.png" alt="Error count" popup="true" >}}</td>
<td>Bar graphs to avoid jumpy interpolations{{< img src="errors-good.png" alt="Error count bar graph" popup="true" >}}</td>
</tr>
</tbody>
</table>



## Stacked area graphs

{{< img src="areas-3.png" alt="Area graph" popup="true" size="1x" >}}

Area graphs are similar to line graphs, except the metric values are represented by two-dimensional bands rather than lines. Multiple timeseries can be summed together simply by stacking the bands, but too many bands makes the graph hard to interpret. If each band is only a pixel or two tall, the information conveyed is minimal.

### When to use stacked area graphs




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
<td>The same metric from <strong>different scopes</strong>, stacked</td>
<td>To check both the sum and the contribution of each of its parts at a glance</td>
<td>Load balancer requests per availability zone{{< img src="elb-req.png" alt="Load balancer requests per availability zone" popup="true" >}}</td>
</tr>
<tr class="even">
<td>Summing <strong>complementary metrics</strong> that share the same unit</td>
<td>To see how a finite resource is being utilized</td>
<td>CPU utilization metrics (user, system, idle, etc.){{< img src="cpu-spiky.png" alt="CPU utilization, stacked graph" popup="true" >}}</td>
</tr>
</tbody>
</table>



### When to use something else




<table>
<colgroup>
<col width="33%" />
<col width="33%" />
<col width="33%" />
</colgroup>
<thead>
<tr class="header">
<th>What</th>
<th>Example</th>
<th>Instead use...</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><strong>Unaggregated metrics</strong> from large numbers of hosts, making the slices too thin to be meaningful</td>
<td>Throughput metrics across hundreds of app servers{{< img src="stack2-bad.png" alt="Overloaded stacked area graph" popup="true" >}}</td>
<td>Line graph or solid-color area graph to track total, aggregate value{{< img src="stack4-good.png" alt="Solid area graph" popup="true" >}}
<hr />
Heat maps to track host-level data{{< img src="stack8-good.png" alt="Throughput heat map" popup="true" >}}</td>
</tr>
<tr class="even">
<td>Metrics that <strong>can't be added</strong> sensibly</td>
<td>System load across multiple servers{{< img src="sys4-load-bad.png" alt="Stacked system load graph" popup="true" >}}</td>
<td>Line graphs, or heat maps for large numbers of hosts{{< img src="sys4-load-good.png" alt="System load line graph" popup="true" >}}</td>
</tr>
</tbody>
</table>



## Bar graphs

{{< img src="errors-bars.png" alt="Bar graph" popup="true" size="1x" >}}

In a bar graph, each bar represents a metric rollup over a time interval. This feature makes bar graphs ideal for representing counts. Unlike *gauge* metrics, which represent an instantaneous value, *count* metrics only make sense when paired with a time interval (e.g., 13 server errors in the past five minutes).

Bar graphs require no interpolation to connect one interval to the next, making them especially useful for representing sparse metrics. Like area graphs, they naturally accommodate stacking and summing of metrics.

### When to use bar graphs




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
<td><strong>Sparse metrics</strong> (e.g. metrics tracking rare events)</td>
<td>To convey metric values without jumpy or misleading interpolations</td>
<td>Blocked tasks in Cassandra's internal queues{{< img src="bar-blocked.png" alt="Blocked tasks bar graph" popup="true" >}}</td>
</tr>
<tr class="even">
<td>Metrics that represent a <strong>count</strong> (rather than a gauge)</td>
<td>To convey both the total count and the corresponding time interval</td>
<td>Failed jobs, by data center (4-hour intervals){{< img src="failed-jobs2.png" alt="Failed jobs bar graph" popup="true" >}}</td>
</tr>
</tbody>
</table>



### When to use something else




<table>
<colgroup>
<col width="33%" />
<col width="33%" />
<col width="33%" />
</colgroup>
<thead>
<tr class="header">
<th>What</th>
<th>Example</th>
<th>Instead use...</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Metrics that <strong>can't be added</strong> sensibly</td>
<td>Average latency per load balancer{{< img src="bar-bad.png" alt="Confusingly summed latency metrics" popup="true" >}}</td>
<td>Line graphs to isolate timeseries from each host{{< img src="bar-good.png" alt="Isolated latency metrics" popup="true" >}}</td>
</tr>
<tr class="even">
<td><strong>Unaggregated metrics</strong> from large numbers of sources, making the slices too thin to be meaningful</td>
<td>Completed tasks across dozens of Cassandra nodes{{< img src="cass-bad.png" alt="Bar graph of completed tasks" popup="true" >}}</td>
<td>Solid-color bars to track total, aggregate metric value{{< img src="cass-good-bars.png" alt="Solid-color bar graph" popup="true" >}}
<hr />
Heat maps to track host-level values{{< img src="cass-good-heat.png" alt="Heat map of completed tasks" popup="true" >}}</td>
</tr>
</tbody>
</table>



## Heat maps

{{< img src="heat.png" alt="Heat map" popup="true" size="1x" >}}

Heat maps show the distribution of values for a metric evolving over time. Specifically, each column represents a distribution of values during a particular time slice. Each cell's shading corresponds to the number of entities reporting that particular value during that particular time.

Heat maps are essentially [distribution graphs](https://docs.datadoghq.com/graphing/#distribution), except that heat maps show change over time, and distribution graphs are a snapshot of a particular window of time. Distributions are covered in Part 2 of this series.

### When to use heat maps




<table>
<colgroup>
<col width="33%" />
<col width="33%" />
<col width="33%" />
</colgroup>
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
<strong>Single metric</strong> reported by a large number of groups

</td>
<td>
To convey general trends at a glance

</td>
<td style="width: 335px!important;">
Web latency per host{{< img src="web-latency-heat.png" alt="Webapp latency heat map" popup="true" >}}

</td>
</tr>
<tr>
<td>
</td>
<td colspan="2">

</td>
</tr>
<tr>
<td>
</td>
<td>
To see transient variations across members of a group

</td>
<td>
Requests received per host{{< img src="web-req.png" alt="Requests per host heat map" popup="true" >}}

</td>
</tr>
</tbody>
</table>




### When to use something else



<table>
<thead>
<tr class="header">
<th>What</th>
<th>Example</th>
<th>Instead use...</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Metrics coming from only a <strong>few individual sources</strong></td>
<td>CPU utilization across a small number of RDS instances{{< img src="heat-bad-rds.png" alt="Sparse heat map of CPU" popup="true" >}}</td>
<td>Line graphs to isolate timeseries from each host{{< img src="heat-good-rds.png" alt="Line graph of CPU" popup="true" >}}</td>
</tr>
<tr class="even">
<td>Metrics where <strong>aggregates matter more</strong> than individual values</td>
<td>Disk utilization per Cassandra column family{{< img src="heat-bad-cf.png" alt="Sparse heat map of CPU" popup="true" >}}</td>
<td>Area graphs to sum values across a set of tags{{< img src="heat-good-cf.png" alt="Line graph of CPU" popup="true" >}}</td>
</tr>
</tbody>
</table>



## Conclusion

By understanding the ideal use cases and limitations of each kind of timeseries graph, you can present actionable information from your metrics more clearly, thereby providing observability into your systems.

In [the next article](/blog/summary-graphs-metric-graphs-101/) in this series, we'll explore other methods of graphing and monitoring metrics, including change graphs, ranked lists, distributions, and other visualizations.

------------------------------------------------------------------------


*Source Markdown for this series is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/metric-graphs-101/). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues).*

