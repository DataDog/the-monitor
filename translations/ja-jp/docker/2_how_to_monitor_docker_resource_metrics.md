*This post is part 2 in a 4-part series about monitoring Docker. [Part 1][part-1] discusses the novel challenge of monitoring containers instead of hosts, [part 3][part-3] covers the nuts and bolts of collecting Docker metrics, and [part 4][part-4] describes how the largest TV and radio outlet in the U.S. monitors Docker. This article describes in detail the resource metrics that are available from Docker.*

## Docker is like a host
As discussed in [part 1][part-1] of this series, Docker can rightly be classified as a type of mini-host. Just like a regular host, it runs work on behalf of resident software, and that work uses CPU, memory, I/O, and network resources. However, Docker containers run inside cgroups which don't report the exact same metrics you might expect from a host. This article will discuss the resource metrics that *are* available. The [next article][part-3] in this series covers three different ways to collect Docker metrics.

## Key Docker metrics
### CPU

| **Name** | **Description** | **[Metric type][types]** |
|:---:|:---:|:---:|
| user CPU | Percent of time that CPU is under direct control of processes  | Resource: Utilization |
| system CPU | Percent of time that CPU is executing system calls on behalf of processes | Resource: Utilization |
| throttling (count) | Number of CPU throttling enforcements for a container | Resource: Saturation |
| throttling (time) | Total time that a container's CPU usage was throttled | Resource: Saturation |

#### Standard metrics
Just like a traditional host, Docker containers report **system CPU** and **user CPU** usage. It probably goes without saying that if your container is performing slowly, CPU is one of the first resources you'll want to look at.

As with all Docker metrics, you will typically collect the metrics [differently][part-3] than you would from an ordinary host. Another key difference with containers: unlike a traditional host, Docker does not report nice, idle, iowait, or irq CPU time.

<h4 class="anchor" id="throttling">Throttling</h4>
If Docker has plenty of CPU capacity, but you still suspect that it is compute-bound, you may want to check a container-specific metric: CPU throttling.

If you do not specify any scheduling priority, then available CPU time will be split evenly between running containers. If some containers don't need all of their allotted CPU time, then it will be made proportionally available to other containers.

You can optionally control the share of CPU time each container should have relative to others using the same CPU(s) by specifying [CPU shares](https://docs.docker.com/reference/run/#cpu-share-constraint). 

Going one step further, you can actively throttle a container. In some cases, a container's default or declared number of CPU shares would entitle it to more CPU time than you want it to have. If, in those cases, the container attempts to actually use that CPU time, a [CPU quota constraint](https://docs.docker.com/reference/run/#cpu-quota-constraint) will tell Docker when to throttle the container's CPU usage. Note that the CPU quota and CPU period are both expressed in microseconds (not milliseconds nor nanoseconds). So a container with a 100,000 microsecond period and a 50,000 microsecond quota would be throttled if it attempted to use more than half of the CPU time during its 0.1s periods.

Docker can tell you the number of times throttling was enforced for each container, as well as the total time that each container was throttled.

As discussed in the next article, CPU metrics can be collected from [pseudo-files][part-3-pseudo-files-cpu], the [stats command][part-3-stats-cpu] (basic CPU usage metrics), or from the [API][part-3-api-cpu].

![Visual break](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-03-container-monitoring/p2_divider_1.png)
### Memory
Just as you would expect, Docker can report on the amount of memory available to it, and the amount of memory it is using. 

| **Name** | **Description** | **[Metric type][types]** |
|:---:|:---:|:---:|
| Memory | Memory usage of a container | Resource: Utilization |
| RSS | Non-cache memory for a process (stacks, heaps, etc.) | Resource: Utilization |
| Cache memory | Data from disk cached in memory | Resource: Utilization |
| Swap | Amount of swap space in use | Resource: Saturation |

**Used memory** can be decomposed into:

* **RSS** (resident set size) is data that belongs to a process: stacks, heaps, etc. RSS itself can be further decomposed into active and inactive memory (`active_anon` and `inactive_anon`). Inactive RSS memory is swapped to disk when necessary.
* **cache memory** reflects data stored on disk that is currently cached in memory. Cache can be further decomposed into active and inactive memory (`active_file`, `inactive_file`). Inactive memory may be reclaimed first when the system needs memory.

Docker also reports on the amount of **swap** currently in use.

Additional metrics that may be valuable in investigating performance or stability issues include page faults, which can represent either segmentation faults or fetching data from disk instead of memory (`pgfault` and `pgmajfault`, respectively).

Deeper documentation of memory metrics is [here][memory-metrics-doc].

As with a traditional host, when you have performance problems, some of the first metrics you'll want to look at include memory availability and swap usage.

As discussed in the next article, memory metrics can be collected from [pseudo-files][part-3-pseudo-files-memory], the [stats command][part-3-stats-memory] (basic memory usage metrics), or from the [API][part-3-api-memory].

![Visual break](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-03-container-monitoring/p2_divider_2.png)
### I/O

For each block device, Docker reports the following two metrics, decomposed into four counters: by reads versus writes, and by synchronous versus asynchronous I/O.

| **Name** | **Description** | **[Metric type][types]** |
|:---:|:---:|:---:|
| I/O serviced | Count of I/O operations performed, regardless of size | Resource: Utilization |
| I/O service bytes | Bytes read or written by the cgroup | Resource: Utilization |

Block I/O is shared, so it is a good idea to track the host's queue and service times in addition to the container-specific I/O metrics called out above. If queue lengths or service times are increasing on a block device that your container uses, your container's I/O will be affected.

As discussed in the next article, I/O metrics can be collected from [pseudo-files][part-3-pseudo-files-io], the [stats command][part-3-stats-memory] (bytes read and written), or from the [API][part-3-api-io].

### Network

Just like an ordinary host, Docker can report several different network metrics, each of them divided into separate metrics for inbound and outbound network traffic:

| **Name** | **Description** | **[Metric type][types]** |
|:---:|:---:|:---:|
| Bytes | Network traffic volume (send/receive) | Resource: Utilization |
| Packets | Network packet count (send/receive) | Resource: Utilization |
| Errors (receive) | Packets received with errors | Resource: Error |
| Errors (transmit) | Errors in packet transmission | Resource: Error |
| Dropped | Packets dropped (send/receive) | Resource: Error |

As discussed in the next article, network metrics can be collected from [pseudo-files][part-3-pseudo-files-network], the [stats command][part-3-stats-network] (bytes sent and received), or from the [API][part-3-api-network].

![Visual break](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-03-container-monitoring/p2_divider_3.png)
## Up next
Docker can report all the basic resource metrics you'd expect from a traditional host: CPU, memory, I/O, and network. However, some specific metrics you might expect (such as nice, idle, iowait, or irq CPU time) are not available, and others metrics are unique to containers, such as CPU throttling.

The commands used to collect resource metrics from Docker are different from the commands used on a traditional host, so the next article in this series covers the three main approaches to Docker metrics collection. [Read on...][part-3]
- - -

*Source Markdown for this post is available [on GitHub][markdown]. Questions, corrections, additions, etc.? Please [let us know][issues].*


<iframe width="100%" height="100" style="border: 0;" src="https://go.pardot.com/l/38172/2015-03-02/h6c2r" scrolling="no" type="text/html" frameborder="0" allowtransparency="true"></iframe>

[markdown]: https://github.com/DataDog/the-monitor/blob/master/docker/2_how_to_monitor_docker_resource_metrics.md
[issues]: https://github.com/datadog/the-monitor/issues
[part-1]: https://www.datadoghq.com/blog/the-docker-monitoring-problem/
[part-3]: https://www.datadoghq.com/blog/how-to-collect-docker-metrics
[part-4]: https://www.datadoghq.com/blog/iheartradio-monitors-docker/
[part-3-pseudo-files-cpu]: https://www.datadoghq.com/blog/how-to-collect-docker-metrics/#pseudo-files-cpu
[part-3-pseudo-files-memory]: https://www.datadoghq.com/blog/how-to-collect-docker-metrics/#pseudo-files-memory
[part-3-pseudo-files-io]: https://www.datadoghq.com/blog/how-to-collect-docker-metrics/#pseudo-files-io
[part-3-pseudo-files-network]: https://www.datadoghq.com/blog/how-to-collect-docker-metrics/#pseudo-files-network
[part-3-stats-cpu]: https://www.datadoghq.com/blog/how-to-collect-docker-metrics/#stats-cpu
[part-3-stats-memory]: https://www.datadoghq.com/blog/how-to-collect-docker-metrics/#stats-memory
[part-3-stats-network]: https://www.datadoghq.com/blog/how-to-collect-docker-metrics/#stats-network
[part-3-api-cpu]: https://www.datadoghq.com/blog/how-to-collect-docker-metrics/#api-cpu
[part-3-api-memory]: https://www.datadoghq.com/blog/how-to-collect-docker-metrics/#api-memory
[part-3-api-io]: https://www.datadoghq.com/blog/how-to-collect-docker-metrics/#api-io
[part-3-api-network]: https://www.datadoghq.com/blog/how-to-collect-docker-metrics/#api-network
[memory-metrics-doc]: http://blog.docker.com/2013/10/gathering-lxc-docker-containers-metrics/#memory-metrics
[types]: https://www.datadoghq.com/blog/monitoring-101-collecting-data/
