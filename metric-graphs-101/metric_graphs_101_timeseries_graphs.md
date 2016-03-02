*This is the first post in a series about visualizing monitoring data. This post focuses on timeseries graphs.* 

In order to turn your metrics into actionable insights, it's important to choose the right visualization for your data. There is no one-size-fits-all solution: you can see different things in the same metric with different graph types.

To help you effectively visualize your metrics, this first post explores four different types of timeseries graphs, which have time on the x-axis and metric values on the y-axis:

* [Line graphs](#line-graphs)
* [Stacked area graphs](#area-graphs)
* [Bar graphs](#bar-graphs)
* [Heat maps](#heat-maps)

For each graph type, we'll explain how it works, when to use it, and when to use something else. 

<h2 class="anchor" id="line-graphs">Line graphs</h2>

<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/key_pg_classic.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/key_pg_classic.png" alt="Line graph" /></a>

Line graphs are the simplest way to translate metric data into visuals, but often they're used by default when a different graph would be more appropriate. For instance, a graph of wildly fluctuating metrics from hundreds of hosts quickly becomes harder to disentangle than steel wool.

### When to use line graphs
<table><thead>
<tr>
<th>What</th>
<th>Why</th>
<th colspan="2">Example</th>
</tr>
</thead><tbody>
<tr>
<td>The same metric reported by <strong>different scopes</strong></td>
<td>To spot outliers at a glance</td>
<td>CPU idle for each host in a cluster</td>
<td style="width: 335px!important;"><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/cpu_idle_host.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/cpu_idle_host.png" alt="CPU idle per host" /></a></td>
</tr>
<tr>
<td>Tracking <strong>single metrics</strong> from one source, or as an aggregate
<td>To clearly communicate a key metric&#39;s evolution over time</td>
<td>Median latency across all web servers</td>
<td><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/latency_spike.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/latency_spike.png" alt="Median webapp latency" /></a></td>
</tr>
<tr>
<td>Metrics for which <strong>unaggregated values</strong> from a particular slice of your infrastructure are especially valuable</td>
<td>To spot individual deviations into unacceptable ranges</td>
<td>Disk space utilization per database node</td>
<td><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/cass_disk_rising.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/cass_disk_rising.png" alt="Disk space per node" /></a></td>
</tr>
<tr>
<td><strong>Related metrics</strong> sharing the same units</td>
<td>To spot correlations at a glance</td>
<td>Latency for disk reads and disk writes on the same machine</td>
<td><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/disk_lat.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/disk_lat.png" alt="Read and write latency" /></a></td>
</tr>
<tr>
<td>Metrics that have a clear <strong>acceptable domain</strong></td>
<td>To easily spot unacceptable degradations</td>
<td>Latency for processing web requests</td>
<td><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/key_pg_lat.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/key_pg_lat.png" alt="Key page latency" /></a></td>
</tr>
</tbody></table>
 
<h3>When to use something else</h3>  

<table>
<thead>
<tr>
<th>What</th>
<th colspan="2">Example</th>
<th colspan="2">Instead use...</th>
</tr>
</thead>
<tbody>
<tr>
<td>Highly variable metrics reported by a <strong>large number of sources</strong></td>
<td>CPU from all hosts</td>
<td style="width: 335px!important;"><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/cpu_bad.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/cpu_bad.png" alt="Noisy CPU line graph" /></a></td>
<td>Heat maps to make noisy data more interpretable</td>
<td style="width: 335px!important;"><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/cpu_good.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/cpu_good.png" alt="CPU heat map" /></a></td>
</tr>
<tr>
<td>Metrics that are <strong>more actionable as aggregates</strong> than as separate data points</td>
<td>Web requests per second over dozens of web servers</td>
<td><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/nginx_bad.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/nginx_bad.png" alt="Web server requests per node" /></a></td>
<td>Area graphs to aggregate across tagged groups</td>
<td><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/nginx_good.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/nginx_good.png" alt="Web server requests per availability zone" /></a></td>
</tr>
<tr>
<td>Metrics that are <strong>often equal to zero</strong></td>
<td>Metrics tracking relatively rare S3 access errors</td>
<td><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/errors_bad.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/errors_bad.png" alt="Error count" /></a></td>
<td>Bar graphs to avoid jumpy interpolations</td>
<td><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/errors_good.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/errors_good.png" alt="Error count bar graph" /></a></td>
</tr>
</tbody>
</table>


<h2 class="anchor" id="area-graphs">Stacked area graphs</h2>

<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/areas_3.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/areas_3.png" alt="Area graph" /></a>

Area graphs are similar to line graphs, except the metric values are represented by two-dimensional bands rather than lines. Multiple timeseries can be summed together simply by stacking the bands, but too many bands makes the graph hard to interpret. If each band is only a pixel or two tall, the actionable information it conveys is minimal.

### When to use stacked area graphs

<table><thead>
<tr>
<th>What</th>
<th>Why</th>
<th colspan="2">Example</th>
</tr>
</thead><tbody>
<tr>
<td>The same metric from <strong>different scopes</strong>, stacked</td>
<td>To check both the sum and the contribution of each of its parts at a glance</td>
<td>Load balancer requests per availability zone</td>
<td style="width: 335px!important;"><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/elb_req.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/elb_req.png" alt="Load balancer requests per availability zone" /></a></td>
</tr>
<tr>
<td>Summing <strong>complementary metrics</strong> that share the same unit</td>
<td>To see how a finite resource is being utilized</td>
<td>CPU utilization metrics (user, system, idle, etc.)</td>
<td><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/cpu_spiky.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/cpu_spiky.png" alt="CPU utilization, stacked graph" /></a></td>
</tr>
</tbody></table>

<h3>When to use something else</h3>  

<table>
<thead>
<tr>
<th>What</th>
<th colspan="2">Example</th>
<th colspan="2">Instead use...</th>
</tr>
</thead>
<tbody>
<tr>
<td rowspan="2"><strong>Unaggregated metrics</strong> from large numbers of hosts, making the slices too thin to be meaningful</td>
<td rowspan="2">Throughput metrics across hundreds of app servers</td> 
<td rowspan="2" style="width: 335px!important;"><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/stack2_bad.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/stack2_bad.png" alt="Overloaded stacked area graph" /></a></td>
<td>Line graph or solid-color area graph to track total, aggregate value</td>
<td style="width: 335px!important;"><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/stack4_good.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/stack4_good.png" alt="Solid area graph" /></a></td>
</tr>
<tr>
<td>Heat maps to track host-level data</td>
<td><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/stack8_good.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/stack8_good.png" alt="Throughput heat map" /></a></td>

</tr>
<tr>
<td>Metrics that <strong>can't be added</strong> sensibly</td>
<td>System load across multiple servers</td>
<td><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/sys2_load_bad.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/sys2_load_bad.png" alt="Stacked system load graph" /></a></td>
<td>Line graphs, or heat maps for large numbers of hosts</td>
<td><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/sys2_load_good.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/sys2_load_good.png" alt="System load line graph" /></a></td>
</tr>
</tbody>
</table>

<h2 class="anchor" id="bar-graphs">Bar graphs</h2>

<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/errors_bars.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/errors_bars.png" alt="Bar graph" /></a>

In a bar graph, each bar represents a metric rollup over a time interval. This feature makes bar graphs ideal for representing counts. Unlike _gauge_ metrics, which represent an instantaneous value, _count_ metrics only make sense when paired with a time interval (e.g., 13 server errors in the past five minutes).

Bar graphs require no interpolation to connect one interval to the next, making them especially useful for representing sparse metrics. Like area graphs, they naturally accommodate stacking and summing of metrics.

### When to use bar graphs

<table><thead>
<tr>
<th>What</th>
<th>Why</th>
<th colspan="2">Example</th>
</tr>
</thead><tbody>
<tr>
<td><strong>Sparse metrics</strong> (e.g. metrics tracking rare events)</td>
<td>To convey metric values without jumpy or misleading interpolations</td>
<td>Blocked tasks in Cassandra&#39;s internal queues</td>
<td style="width: 335px!important;"><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/bar_blocked.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/bar_blocked.png" alt="Blocked tasks bar graph" /></a></td>
</tr>
<tr>
<td>Metrics that represent a <strong>count</strong> (rather than a gauge)</td>
<td>To convey both the total count and the corresponding time interval</td>
<td>Failed jobs, by data center (4-hour intervals)</td>
<td><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/failed_jobs2.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/failed_jobs2.png" alt="Failed jobs bar graph" /></a></td>
</tr>
</tbody></table>

<h3>When to use something else</h3>  

<table>
<thead>
<tr>
<th>What</th>
<th colspan="2">Example</th>
<th colspan="2">Instead use...</th>
</tr>
</thead>
<tbody>
<tr>
<td>Metrics that <strong>can't be added</strong> sensibly</td>
<td>Average latency per load balancer</td>
<td style="width: 335px!important;"><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/bar_bad.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/bar_bad.png" alt="Confusingly summed latency metrics" /></a></td>
<td>Line graphs to isolate timeseries from each host</td>
<td style="width: 335px!important;"><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/bar_good.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/bar_good.png" alt="Isolated latency metrics" /></a></td>
</tr>
<tr>
<td rowspan="2"><strong>Unaggregated metrics</strong> from large numbers of sources, making the slices too thin to be meaningful</td>
<td rowspan="2">Completed tasks across dozens of Cassandra nodes</td>
<td rowspan="2"><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/cass_bad.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/cass_bad.png" alt="Bar graph of completed tasks" /></a></td>
<td>Solid-color bars to track total, aggregate metric value</td>
<td><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/cass_good_bars.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/cass_good_bars.png" alt="Solid-color bar graph" /></a></td>
</tr>
<tr>
<td>Heat maps to track host-level values</td>
<td><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/cass_good_heat.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/cass_good_heat.png" alt="Heat map of completed tasks" /></a></td>
</tr>
</tbody>
</table>
 
<h2 class="anchor" id="heat-maps">Heat maps</h2>

<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/heat.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/heat.png" alt="Heat map" /></a>

Heat maps show the distribution of values for a metric evolving over time. Specifically, each column represents a distribution of values during a particular time slice. Each cell's shading corresponds to the number of entities reporting that particular value during that particular time.

Heat maps are essentially [distribution graphs](http://docs.datadoghq.com/graphing/#distribution), except that heat maps show change over time, and distribution graphs are a snapshot of a particular window of time. Distributions are covered in Part 2 of this series.

### When to use heat maps

<table><thead>
<tr>
<th>What</th>
<th>Why</th>
<th colspan="2">Example</th>
</tr>
</thead><tbody>
<tr>
<td rowspan="2"><strong>Single metric</strong> reported by a large number of groups</td>
<td>To convey general trends at a glance</td>
<td>Web latency per host</td>
<td style="width: 335px!important;"><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/web_latency_heat.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/web_latency_heat.png" alt="Webapp latency heat map" /></a></td>
</tr>
<tr>
<td>To see transient variations across members of a group</td>
<td>Requests received per host</td>
<td><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/web_req.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/web_req.png" alt="Requests per host heat map" /></a></td>
</tr>
</tbody></table>
  
<h3>When to use something else</h3>  
  
<table>
<thead>
<tr>
<th>What</th>
<th colspan="2">Example</th>
<th colspan="2">Instead use...</th>
</tr>
</thead>
<tbody>
<tr>
<td>Metrics coming from only a <strong>few individual sources</strong></td>
<td>CPU utilization across a small number of RDS instances</td>
<td style="width: 335px!important;"><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/heat_bad_rds.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/heat_bad_rds.png" alt="Sparse heat map of CPU" /></a></td>
<td>Line graphs to isolate timeseries from each host</td>
<td style="width: 335px!important;"><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/heat_good_rds.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/heat_good_rds.png" alt="Line graph of CPU" /></a></td>
</tr>
<tr>
<td>Metrics where <strong>aggregates matter more</strong> than individual values</td>
<td>Disk utilization per Cassandra column family</td>
<td><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/heat_bad_cf.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/heat_bad_cf.png" alt="Sparse heat map of CPU" /></a></td>
<td>Area graphs to sum values across a set of tags</td>
<td><a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/heat_good_cf.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-01-graphing-101/pt1/300/heat_good_cf.png" alt="Line graph of CPU" /></a></td>
</tr>
</tbody>
</table>

## Conclusion
By understanding the ideal use cases and limitations of each kind of timeseries graph, you can extract actionable information from your metrics more quickly.

In the next article in this series, we'll explore other methods of graphing and monitoring metrics, including change graphs, ranked lists, distributions, and other visualizations. 

---------------------------------------------------------

*Source Markdown for this series is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/metric-graphs-101/). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues).*
