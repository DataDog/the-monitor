# How to monitor Docker resource metrics


*This post is part 2 in a 4-part series about monitoring Docker. [Part 1](/blog/the-docker-monitoring-problem/) discusses the novel challenge of monitoring containers instead of hosts, [part 3](/blog/how-to-collect-docker-metrics) covers the nuts and bolts of collecting Docker resource metrics, and [part 4](/blog/iheartradio-monitors-docker/) describes how the largest TV and radio outlet in the U.S. monitors Docker. This article describes in detail the resource metrics that are available from Docker.*

Docker is like a host
---------------------


As discussed in [part 1](/blog/the-docker-monitoring-problem/) of this series, Docker can rightly be classified as a type of mini-host. Just like a regular host, it runs work on behalf of resident software, and that work uses CPU, memory, I/O, and network resources. However, Docker containers run inside cgroups which don't report the exact same metrics you might expect from a host. This article will discuss the resource metrics that *are* available. The [next article](/blog/how-to-collect-docker-metrics) in this series covers three different ways to collect Docker resource metrics.

Key Docker resource metrics
---------------------------



### CPU




<table>
<thead>
<tr class="header">
<th><strong>Name</strong></th>
<th><strong>Description</strong></th>
<th><strong><a href="/blog/monitoring-101-collecting-data/">Metric type</a></strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>user CPU</td>
<td>Percent of time that CPU is under direct control of processes</td>
<td>Resource: Utilization</td>
</tr>
<tr class="even">
<td>system CPU</td>
<td>Percent of time that CPU is executing system calls on behalf of processes</td>
<td>Resource: Utilization</td>
</tr>
<tr class="odd">
<td>throttling (count)</td>
<td>Number of CPU throttling enforcements for a container</td>
<td>Resource: Saturation</td>
</tr>
<tr class="even">
<td>throttling (time)</td>
<td>Total time that a container's CPU usage was throttled</td>
<td>Resource: Saturation</td>
</tr>
</tbody>
</table>



#### Standard metrics


Just like a traditional host, Docker containers report **system CPU** and **user CPU** usage. It probably goes without saying that if your container is performing slowly, CPU is one of the first resources you'll want to look at.

As with all Docker resource metrics, you will typically collect the metrics [differently](/blog/how-to-collect-docker-metrics) than you would from an ordinary host. Another key difference with containers: unlike a traditional host, Docker does not report nice, idle, iowait, or irq CPU time.

#### Throttling


If Docker has plenty of CPU capacity, but you still suspect that it is compute-bound, you may want to check a container-specific metric: CPU throttling.

If you do not specify any scheduling priority, then available CPU time will be split evenly between running containers. If some containers don't need all of their allotted CPU time, then it will be made proportionally available to other containers.

You can optionally control the share of CPU time each container should have relative to others using the same CPU(s) by specifying [CPU shares](https://docs.docker.com/engine/reference/run/#cpu-share-constraint).

Going one step further, you can actively throttle a container. In some cases, a container's default or declared number of CPU shares would entitle it to more CPU time than you want it to have. If, in those cases, the container attempts to actually use that CPU time, a [CPU quota constraint](https://docs.docker.com/engine/reference/run/#cpu-quota-constraint) will tell Docker when to throttle the container's CPU usage. Note that the CPU quota and CPU period are both expressed in microseconds (not milliseconds nor nanoseconds). So a container with a 100,000 microsecond period and a 50,000 microsecond quota would be throttled if it attempted to use more than half of the CPU time during its 0.1s periods.

Docker can tell you the number of times throttling was enforced for each container, as well as the total time that each container was throttled.

As discussed in the next article, CPU metrics can be collected from [pseudo-files](/blog/how-to-collect-docker-metrics/#pseudo-files-cpu), the [stats command](/blog/how-to-collect-docker-metrics/#stats-cpu) (basic CPU usage metrics), or from the [API](/blog/how-to-collect-docker-metrics/#api-cpu).

{{< img src="p2-divider-1.png" alt="Docker metrics visual break" >}}

### Memory


Just as you would expect, Docker can report on the amount of memory available to it, and the amount of memory it is using.



<table>
<thead>
<tr class="header">
<th><strong>Name</strong></th>
<th><strong>Description</strong></th>
<th><strong><a href="/blog/monitoring-101-collecting-data/">Metric type</a></strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Memory</td>
<td>Memory usage of a container</td>
<td>Resource: Utilization</td>
</tr>
<tr class="even">
<td>RSS</td>
<td>Non-cache memory for a process (stacks, heaps, etc.)</td>
<td>Resource: Utilization</td>
</tr>
<tr class="odd">
<td>Cache memory</td>
<td>Data from disk cached in memory</td>
<td>Resource: Utilization</td>
</tr>
<tr class="even">
<td>Swap</td>
<td>Amount of swap space in use</td>
<td>Resource: Saturation</td>
</tr>
</tbody>
</table>



**Used memory** can be decomposed into:



-   **RSS** (resident set size) is data that belongs to a process: stacks, heaps, etc. RSS itself can be further decomposed into active and inactive memory (`active_anon` and `inactive_anon`). Inactive RSS memory is swapped to disk when necessary.
-   **cache memory** reflects data stored on disk that is currently cached in memory. Cache can be further decomposed into active and inactive memory (`active_file`, `inactive_file`). Inactive memory may be reclaimed first when the system needs memory.



Docker also reports on the amount of **swap** currently in use.

Additional metrics that may be valuable in investigating performance or stability issues include page faults, which can represent either segmentation faults or fetching data from disk instead of memory (`pgfault` and `pgmajfault`, respectively).

Deeper documentation of memory metrics is [here](http://blog.docker.com/2013/10/gathering-lxc-docker-containers-metrics/#memory-metrics).

As with a traditional host, when you have performance problems, some of the first metrics you'll want to look at include memory availability and swap usage.

As discussed in the next article, memory metrics can be collected from [pseudo-files](/blog/how-to-collect-docker-metrics/#pseudo-files-memory), the [stats command](/blog/how-to-collect-docker-metrics/#stats-memory) (basic memory usage metrics), or from the [API](/blog/how-to-collect-docker-metrics/#api-memory).

{{< img src="p2-divider-2.png" alt="Docker metrics visual break" >}}

### I/O


For each block device, Docker reports the following two metrics, decomposed into four counters: by reads versus writes, and by synchronous versus asynchronous I/O.



<table>
<thead>
<tr class="header">
<th><strong>Name</strong></th>
<th><strong>Description</strong></th>
<th><strong><a href="/blog/monitoring-101-collecting-data/">Metric type</a></strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>I/O serviced</td>
<td>Count of I/O operations performed, regardless of size</td>
<td>Resource: Utilization</td>
</tr>
<tr class="even">
<td>I/O service bytes</td>
<td>Bytes read or written by the cgroup</td>
<td>Resource: Utilization</td>
</tr>
</tbody>
</table>



Block I/O is shared, so it is a good idea to track the host's queue and service times in addition to the container-specific I/O metrics called out above. If queue lengths or service times are increasing on a block device that your container uses, your container's I/O will be affected.

As discussed in the next article, I/O metrics can be collected from [pseudo-files](/blog/how-to-collect-docker-metrics/#pseudo-files-io), the [stats command](/blog/how-to-collect-docker-metrics/#stats-memory) (bytes read and written), or from the [API](/blog/how-to-collect-docker-metrics/#api-io).

### Network


Just like an ordinary host, Docker can report several different network metrics, each of them divided into separate metrics for inbound and outbound network traffic:



<table>
<thead>
<tr class="header">
<th><strong>Name</strong></th>
<th><strong>Description</strong></th>
<th><strong><a href="/blog/monitoring-101-collecting-data/">Metric type</a></strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Bytes</td>
<td>Network traffic volume (send/receive)</td>
<td>Resource: Utilization</td>
</tr>
<tr class="even">
<td>Packets</td>
<td>Network packet count (send/receive)</td>
<td>Resource: Utilization</td>
</tr>
<tr class="odd">
<td>Errors (receive)</td>
<td>Packets received with errors</td>
<td>Resource: Error</td>
</tr>
<tr class="even">
<td>Errors (transmit)</td>
<td>Errors in packet transmission</td>
<td>Resource: Error</td>
</tr>
<tr class="odd">
<td>Dropped</td>
<td>Packets dropped (send/receive)</td>
<td>Resource: Error</td>
</tr>
</tbody>
</table>



As discussed in the next article, network metrics can be collected from [pseudo-files](/blog/how-to-collect-docker-metrics/#pseudo-files-network), the [stats command](/blog/how-to-collect-docker-metrics/#stats-network) (bytes sent and received), or from the [API](/blog/how-to-collect-docker-metrics/#api-network).

{{< img src="p2-divider-3.png" alt="Docker metrics visual break" >}}

Up next
-------


Docker can report all the basic resource metrics you'd expect from a traditional host: CPU, memory, I/O, and network. However, some specific metrics you might expect (such as nice, idle, iowait, or irq CPU time) are not available, and others metrics are unique to containers, such as CPU throttling.

The commands used to collect resource metrics from Docker are different from the commands used on a traditional host, so the next article in this series covers the three main approaches to Docker resource metrics collection. [Read on...](/blog/how-to-collect-docker-metrics)

------------------------------------------------------------------------


*Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/docker/2_how_to_monitor_docker_resource_metrics.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/datadog/the-monitor/issues).*

