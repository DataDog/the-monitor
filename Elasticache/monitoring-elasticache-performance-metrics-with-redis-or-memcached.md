*This post is part 1 of a 3-part series on monitoring Amazon ElastiCache. [Part 2](https://www.datadoghq.com/blog/collecting-elasticache-metrics-its-redis-memcached-metrics) explains how to collect its performance metrics, and [Part 3](https://www.datadoghq.com/blog/how-coursera-monitors-elasticache-and-memcached-performance) describes how Coursera monitors ElastiCache.*

## What is Amazon ElastiCache?

ElastiCache is a fully managed in-memory cache service offered by AWS. A cache stores often-used assets (such as files, images, css) to respond without hitting the backend and speed up requests. Using a cache greatly improves throughput and reduces latency of read-intensive workloads.

AWS allows you to choose between [Redis](https://www.datadoghq.com/blog/how-to-monitor-redis-performance-metrics/) and [Memcached](https://www.datadoghq.com/blog/speed-up-web-applications-memcached/) as caching engine that powers ElastiCache. Among the thousands of Datadog customers using ElastiCache, Redis is much more commonly used than Memcached. But each technology presents unique advantages depending on your needs. [AWS explains here](http://docs.aws.amazon.com/AmazonElastiCache/latest/UserGuide/SelectEngine.html) how to determine which one is more adapted to your usage.

## Key metrics

An efficient cache can significantly increase your application’s performance and user navigation speed. That’s why key performance metrics need to be well understood and continuously monitored, using both generic ElastiCache metrics collected from AWS CloudWatch but also native metrics from your chosen caching engine. The metrics you should monitor fall into four general categories:

-   [Client metrics](#client-metrics)
-   [Cache performance](#cache-metrics)
-   [Memory metrics](#memory-metrics)
-   [Other host-level metrics](#host-metrics)

### CloudWatch vs native cache metrics

Metrics can be collected from ElastiCache through CloudWatch or directly from your cache engine (Redis or Memcached). Many of them can be collected from both sources: from CloudWatch and also from the cache. However, unlike CloudWatch metrics, native cache metrics are usually collected in real-time at higher resolution. For these reasons you should prefer monitoring native metrics, when they are available from your cache engine.

[![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/elasticache-vs-redis-or-memcached-metrics.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/elasticache-vs-redis-or-memcached-metrics.png)

For each metric discussed in this publication, we provide its name as exposed by Redis and Memcached, as well as the name of the equivalent metric available through AWS CloudWatch, where applicable.

If you are using Redis, we also published a [series of posts](https://www.datadoghq.com/blog/how-to-monitor-redis-performance-metrics/) focused exclusively on how to monitor Redis native performance metrics.

This article references metric terminology introduced in [our Monitoring 101 series](https://www.datadoghq.com/blog/monitoring-101-collecting-data/), which provides a framework for metric collection and alerting.

### Client metrics

Client metrics measure the volume of client connections and requests.

<table>
<tbody>
<tr>
<td rowspan="2"><b>Metric description</b></td>
<td colspan="3"><b>Name</b></td>
<td rowspan="2"><a href="https://www.datadoghq.com/blog/monitoring-101-collecting-data/" target="_blank"><b>Metric Type</b></a></td>
</tr>
<tr>
<td><b>Redis</b></td>
<td><b>Memcached</b></td>
<td><b>CloudWatch</b></td>
</tr>
<tr>
<td>Number of current <b>client</b> <b>connections</b> to the cache</td>
<td>connected_clients</td>
<td>curr_connections</td>
<td>CurrConnections</td>
<td>Resource: Utilization</td>
</tr>
<tr>
<td>Number of <b>Get commands</b> received by the cache</td>
<td>&#8211;</td>
<td>cmd_get</td>
<td>GetTypeCmds (Redis), CmdGet (Memcached)</td>
<td>Work: Throughput</td>
</tr>
<tr>
<td>Number of <b>Set commands</b> received by the cache</td>
<td>&#8211;</td>
<td>cmd_set</td>
<td>SetTypeCmds (Redis), CmdSet (Memcached)</td>
<td>Work: Throughput</td>
</tr>
</tbody>
</table>

**Number of commands** processed is a throughput measurement that will help you identify latency issues, especially with Redis, since it is single threaded and processes command requests sequentially. Unlike Memcached, native Redis metrics don’t distinguish between Set or Get commands. ElastiCache provides both for each technology.

[![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/get-and-set-commands-elasticache.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/get-and-set-commands-elasticache.png)

#### Metric to alert on:

**Current connections**: While sudden changes might indicate application issues requiring investigation, you should track this metric primarily to make sure it never reaches the connections limit. If that happens new connections will be refused, so you should make sure your team is notified and can scale up way before that happens. If you are using Memcached, make sure the parameter **maxconns\_fast** has its default value 0 so that new connections are queued instead of being closed, as they are if **maxconns\_fast** is set to 1. AWS fixes the limit at 65,000 simultaneous connections for Redis ([**maxclients**](http://docs.aws.amazon.com/AmazonElastiCache/latest/UserGuide/ParameterGroups.Redis.html)**)** and Memcached ([**max\_simultaneous\_connections**](http://docs.aws.amazon.com/AmazonElastiCache/latest/UserGuide/ParameterGroups.Memcached.html)).

NOTE: ElastiCache also provides the **NewConnections** metric measuring the number of new connections accepted by the server during the selected period of time.

### Cache performance

By tracking performance metrics you will be able to know at a glance if your cache is working properly.

<table>
<tbody>
<tr>
<td rowspan="2"><b>Metric description</b></td>
<td colspan="3"><b>Name</b></td>
<td rowspan="2"><a href="https://www.datadoghq.com/blog/monitoring-101-collecting-data/" target="_blank"><b>Metric Type</b></a></td>
</tr>
<tr>
<td><b>Redis</b></td>
<td><b>Memcached</b></td>
<td><b>CloudWatch</b></td>
</tr>
<tr>
<td><b>Hits</b>: Number of requested files that were served from the cache without requesting to the backend</td>
<td>keyspace_hits</td>
<td>get_hits</td>
<td>CacheHits (Redis), GetHits (Memcached)</td>
<td>Other</td>
</tr>
<tr>
<td><b>Misses</b>: Number of times a request was answered by the backend because the item was not cached</td>
<td>keyspace_misses</td>
<td>get_misses</td>
<td>CacheMisses (Redis), GetMisses (Memcached)</td>
<td>Other</td>
</tr>
<tr>
<td><b>Replication Lag</b>: Time taken for a cache replica to update changes made in the primary cluster</td>
<td>&#8211;</td>
<td>&#8211;</td>
<td>ReplicationLag (Redis)</td>
<td>Other</td>
</tr>
<tr>
<td><b>Latency</b>: Time between the request being sent and the response being received from the backend</td>
<td>See * below</td>
<td>&#8211;</td>
<td>&#8211;</td>
<td>Work: Performance</td>
</tr>
</tbody>
</table>

Tracking **replication lag**, available only with Redis, helps to prevent serving stale data. Indeed, by automatically synchronizing data into a secondary cluster, replication ensures high availability, read scalability, and prevents data loss. Replicas contain the same data as the primary node so they can also serve read requests. The replication lag measures the time needed to apply changes from the primary cache node to the replicas. You can also look at the native Redis metric **master\_last\_io\_seconds\_ago** which measures the time (in seconds) since the last interaction between slave and master.

#### Metric to alert on:

**Cache** **hits** and **misses** measure the number of successful and failed lookups. With these two metrics you can calculate the **hit rate**: hits / (hits+misses), which reflects your cache efficiency. If it is too low, the cache’s size might be too small for the working data set, meaning that the cache has to evict data too often (see **evictions** metric [below](#memory-metrics)). In that case you should add more nodes which will increase the total available memory in your cluster so more data can fit in the cache. A high hit rate helps to reduce your application response time, ensure a smooth user experience and protect your databases which might not be able to address a massive amount of requests if the hit rate is too low.

\* NOTE: Latency is not available like other classic metrics, but still attainable: you will find all details about measuring latency for Redis [in this post](https://www.datadoghq.com/blog/how-to-collect-redis-metrics/), part of our series on Redis monitoring. Latency is one of the best ways to directly observe Redis performance. Outliers in the latency distribution could cause serious bottlenecks, since Redis is single-threaded—a long response time for one request increases the latency for all subsequent requests. Common causes for high latency include high CPU usage and swapping. [This publication](http://redis.io/topics/latency) from Redis discusses troubleshooting high latency in detail.

Unfortunately, Memcached does not provide a direct measurement of latency, so you will need to rely on throughput measurement via the number of commands processed, [described below](#client-metrics).

### Memory metrics

Memory is the essential resource for any cache, and neglecting to monitor ElastiCache’s memory metrics can have critical impact on your applications.

<table>
<tbody>
<tr>
<td rowspan="2"><b>Metric description</b></td>
<td colspan="3"><b>Name</b></td>
<td rowspan="2"><a href="https://www.datadoghq.com/blog/monitoring-101-collecting-data/" target="_blank"><b>Metric Type</b></a></td>
</tr>
<tr>
<td><b>Redis</b></td>
<td><b>Memcached</b></td>
<td><b>CloudWatch</b></td>
</tr>
<tr>
<td><b>Memory usage</b>: Total number of bytes allocated by the cache engine</td>
<td>used_memory</p>
<p>&nbsp;</td>
<td>bytes</p>
<p>&nbsp;</td>
<td>BytesUsedForCache (Redis), BytesUsedForCacheItems (Memcached)</td>
<td>Resource: Utilization</td>
</tr>
<tr>
<td><b>Evictions</b>: Number of (non-expired) items evicted to make space for new writes</td>
<td>evicted_keys</td>
<td>evictions</td>
<td>Evictions</td>
<td>Resource: Saturation</td>
</tr>
<tr>
<td>The amount of free memory available on the host.</td>
<td>&#8211;</td>
<td>&#8211;</td>
<td>FreeableMemory</td>
<td>Resource: Utilization</td>
</tr>
<tr>
<td><b>Swap Usage</b></td>
<td>&#8211;</td>
<td>&#8211;</td>
<td>SwapUsage</td>
<td>Resource: Saturation</td>
</tr>
<tr>
<td><b>Memory fragmentation ratio</b>: Ratio of memory used (as seen by the operating system) to memory allocated by Redis</td>
<td>mem_fragmentation_ratio</td>
<td>&#8211;</td>
<td>&#8211;</td>
<td>Resource: Saturation</td>
</tr>
</tbody>
</table> 

#### Metrics to alert on:

-   **Memory usage** is critical for your cache performance. If it exceeds the total available system memory, the OS will start swapping old or unused sections of memory (see next paragraph). Writing or reading from disk is up to 100,000x slower than writing or reading from memory, severely degrading the performance of the cache.
-   **Evictions** happen when the cache memory usage limit (**maxmemory** for Redis) is reached and the cache engine has to remove items to make space for new writes. Unlike the host memory, which leads to swap usage when exceeded, the cache memory limit is defined by your node type and number of nodes. The evictions follow the method defined in your cache configuration, such as [LRU for Redis](http://redis.io/topics/lru-cache). Evicting a large number of keys can decrease your hit rate, leading to longer latency times. If your eviction rate is steady and your cache hit rate isn’t abnormal, then your cache has probably enough memory. If the number of evictions is growing, you should increase your cache size by migrating to a larger node type (or adding more nodes if you use Memcached).
-   **FreeableMemory**, tracking the host’s remaining memory, shouldn’t be too low, otherwise it will lead to Swap usage (see next paragraph).
-   **SwapUsage** is a host-level metric that increases when the system runs out of memory and the operating system starts using disk to hold data that should be in memory. Swapping allows the process to continue to run, but severely degrades the performance of your cache and any applications relying on its data. According to AWS, [swap shouldn’t exceed 50MB with Memcached](http://docs.aws.amazon.com/AmazonElastiCache/latest/UserGuide/CacheMetrics.WhichShouldIMonitor.html). AWS makes no similar recommendation for Redis.
-   The **memory fragmentation ratio** metric (available only with Redis) measures the ratio of memory used as seen by the operation system (**used\_memory\_rss**) to memory allocated by Redis (**used\_memory**). The operating system is responsible for allocating physical memory to each process. Its virtual memory manager handles the actual mapping, mediated by a memory allocator. For example, if your Redis instance has a memory footprint of 1GB, the memory allocator will first attempt to find a contiguous memory segment to store the data. If it can’t find one, the allocator divides the process’s data across segments, leading to increased memory overhead. A fragmentation ratio above 1.5 indicates significant memory fragmentation since Redis consumes 150 percent of the physical memory it requested. If the fragmentation ratio rises above 1.5, your memory allocation is inefficient and you should restart the instance. A fragmentation ratio below 1 means that Redis allocated more memory than the available physical memory and the operating system is swapping (see above).

### Other host-level metrics

Host-level metrics for ElastiCache are only available through CloudWatch.

<table>
<tbody>
<tr>
<td><b>Metric description</b></td>
<td><b>Name in CloudWatch</b></td>
<td><a href="https://www.datadoghq.com/blog/monitoring-101-collecting-data/" target="_blank"><b>Metric Type</b></a></td>
</tr>
<tr>
<td>CPU utilization</td>
<td>CPUUtilization</td>
<td>Resource: Utilization</td>
</tr>
<tr>
<td>Number of bytes read from the network by the host</td>
<td>NetworkBytesIn</td>
<td>Resource: Utilization</td>
</tr>
<tr>
<td>Number of bytes written to the network by the host</td>
<td>NetworkBytesOut</td>
<td>Resource: Utilization</td>
</tr>
</tbody>
</table>

#### Metric to alert on:

**CPU Utilization** at high levels can indirectly indicate high latency. You should interpret this metric differently depending on your cache engine technology.

All [AWS cache nodes](https://aws.amazon.com/elasticache/pricing/) with more than 2.78GB of memory or good network performance are multicore. Be aware that if you are using Redis, the extra cores will be idle since Redis is single-threaded. The actual CPU utilization will be equal to this metric’s reported value multiplied by the number of cores. For example a four-core Redis instance reporting 20 percent CPU utilization actually has 80 percent utilization on one core. Therefore you should define an alert threshold based on the number of processor cores in the cache node. AWS recommends that you set the alert threshold at 90 percent divided by the number of cores. If this threshold is exceeded due to heavy read workload, add more read replicas to scale up your cache cluster. If it’s mainly due to write requests, increase the size of your Redis cache instance.

Memcached is multi-threaded so the CPU utilization threshold can be set at 90%. If you exceed that limit, scale up to a larger cache node type or add more cache nodes.

## Correlate to see the full picture

Most of these key metrics are directly linked together. For example, high memory usage can lead to swapping, increasing latency. That’s why you need to correlate these metrics in order to properly monitor ElastiCache.

Correlating metrics with events sent by ElastiCache, such as node addition failure or cluster creation, will also help you to investigate and to keep an eye on your cache cluster’s activity.

[![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/elasticache-dashboard.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/elasticache-dashboard.png)

## Conclusion

In this post we have explored the most important ElastiCache performance metrics. If you are just getting started with Amazon ElastiCache, monitoring the metrics listed below will give you great insight into your cache’s health and performance:

-   [Number of current connections](#client-metrics)
-   [Hit rate](#cache-metrics)
-   [Memory metrics (especially evictions and swap usage)](#memory-metrics)
-   [CPU Utilization](#host-metrics)

[Part 2 of this series](https://www.datadoghq.com/blog/collecting-elasticache-metrics-its-redis-memcached-metrics) provides instructions for collecting all the metrics you need to monitor ElastiCache.
