# How to monitor Redis performance metrics

*This post is part 1 of a 3-part series on Redis monitoring. [Part 2](https://www.datadoghq.com/blog/how-to-collect-redis-metrics) is about collecting Redis metrics, and [Part 3](http://www.datadoghq.com/blog/monitor-redis-using-datadog/) details how to monitor Redis with Datadog.*

## What is Redis?

Redis is a popular in-memory key/value data store. Known for its performance and simple onboarding, Redis has found uses across industries and use cases, including as a:

-   **Database:** as an alternative to a traditional disk-based database, Redis trades durability for speed, though asynchronous disk persistence is available. Redis offers a rich set of data primitives and an unusually extensive list of commands.
-   **Message queue:** Redis’s blocking list commands and low latency make it a good backend for a message broker service.
-   **Memory cache:** Configurable key eviction policies, including the popular Least Recently Used policy, make Redis a great choice as a cache server. Unlike a traditional cache, Redis also allows persistence to disk to improve reliability.

Redis is available as a free, open-source product. Commercial support is available, as is fully managed Redis-as-a-service.

Redis is employed by many high-traffic websites and applications such as Twitter, GitHub, Docker, Pinterest, Datadog, and Stack Overflow.

## Key Redis performance metrics

Monitoring Redis can help catch problems in two areas: resource issues with Redis itself, and problems arising elsewhere in your supporting infrastructure.

In this article we go though the most important Redis metrics in each of the following categories:

-   [Performance metrics](#performance-metrics)
-   [Memory metrics](#memory-metrics)
-   [Basic activity metrics](#basic-activity-metrics)
-   [Persistence metrics](#persistence-metrics)
-   [Error metrics](#error-metrics)

Note that we use metric terminology [introduced in our Monitoring 101 series](https://www.datadoghq.com/blog/monitoring-101-collecting-data/), which provides a basic framework for metric collection and alerting.

<div class="anchor" id="performance-metrics"></div>

### Performance metrics

Along with low error rates, good performance is one of the best top-level indicators of system health. Poor performance is most commonly caused by memory issues, as described in the [Memory section](#memory-metrics).

| **Name**                     | **Description**                                           | **[Metric Type](https://www.datadoghq.com/blog/monitoring-101-collecting-data/)** |
|------------------------------|-----------------------------------------------------------|-----------------------------------------------------------------------------------|
| latency                      | Average time for the Redis server to respond to a request | Work: Performance                                                                     |
| instantaneous\_ops\_per\_sec | Total number of commands processed per second             | Work: Throughput                                                                  |
| hit rate (calculated)        | keyspace\_hits / (keyspace\_hits + keyspace\_misses)      | Work: Success                                                                     |

#### Metric to alert on: latency

Latency is the measurement of the time it takes between a client request and the actual server response. Tracking latency is the most direct way to detect changes in Redis performance. Due to the single-threaded nature of Redis, outliers in your latency distribution could cause serious bottlenecks. A long response time for one request increases the latency for all subsequent requests.

Once you have determined that latency is an issue, there are several measures you can take to diagnose and address performance problems. Refer to the section “Using the latency command to improve performance” on page 14 in our white-paper, *[Understanding the Top 5 Redis Performance Metrics](http://go.datadoghq.com/top-5-redis-performance-metrics-guide)*.

[![Redis Latency graph](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-redis/1-img1.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-redis/1-img1.png)

#### Metric to watch: instantaneous\_ops\_per\_sec

Tracking the throughput of commands processed is critical for diagnosing causes of high latency in your Redis instance. High latency can be caused by a number of issues, from a backlogged command queue, to slow commands, to network link overutilization. You could investigate by measuring the number of commands processed per second—if it remains nearly constant, the cause is not a computationally intensive command. If one or more slow commands are causing the latency issues you would see your number of commands per second drop or stall completely.

A drop in the number of commands processed per second as compared to historical norms could be a sign of either low command volume or slow commands blocking the system. Low command volume could be normal, or it could be indicative of problems upstream. Identifying slow commands is detailed in [Part 2](https://www.datadoghq.com/blog/how-to-collect-redis-metrics) about Collecting Redis Metrics.

[![Redis Commands per second graph](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-redis/1-img2.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-redis/1-img2.png)

#### Metric to watch: hit rate

When using Redis as a cache, monitoring the cache hit rate can tell you if your cache is being used effectively or not. A low hit rate means that clients are looking for keys that no longer exist. Redis does not offer a hit rate metric directly. We can still calculate it like this:

<div style="font-size: 1.2em;">
$$HitRate={keyspace\_hits}/{(keyspace\_hits+keyspace\_misses)}$$
</div>

The `keyspace_misses` metric is discussed in the [Error metrics section](#error-metrics).

A low cache hit rate can be caused by a number of factors, including data expiration and insufficient memory allocated to Redis (which could cause key eviction). Low hit rates could cause increases in the latency of your applications, because they have to fetch data from a slower, alternative resource.

<div class="anchor" id="memory-metrics"></div>

### Memory metrics

| **Name**                  | **Description**                                                                | **[Metric Type](https://www.datadoghq.com/blog/monitoring-101-collecting-data/)** |
|---------------------------|--------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| used\_memory              | Total number of bytes allocated by Redis                                       | Resource: Utilization                                                             |
| mem\_fragmentation\_ratio | Ratio of memory allocated by the operating system to memory requested by Redis | Resource: Saturation                                                              |
| evicted\_keys             | Number of keys removed due to reaching the maxmemory limit                     | Resource: Saturation                                                              |
| blocked\_clients          | Number of clients pending on a blocking call  (BLPOP, BRPOP, BRPOPLPUSH)       | Other                                                                             |

<div class="anchor" id="used-memory-metric"></div>

#### Metric to watch: used\_memory

Memory usage is a critical component of Redis performance. If `used_memory` exceeds the total available system memory, the operating system will begin swapping old/unused sections of memory. Every swapped section is written to disk, severely impacting performance. Writing or reading from disk is up to 5 orders of magnitude (100,000x!) slower than writing or reading from memory (0.1 µs for memory vs. 10 ms for disk).

You can configure Redis to remain confined to a specified amount of memory. Setting the `maxmemory` directive in the redis.conf file gives you direct control over Redis’s memory usage. Enabling `maxmemory` requires you to configure an eviction policy for Redis to determine how it should free up memory. Read more about configuring the maxmemory-policy directive in the [evicted\_keys section](#evicted-keys-metric).

[![Redis Memory used by host](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-redis/1-img3.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-redis/1-img3.png)

*This “flat line” pattern is common for Redis when it is used as a cache; all available memory is consumed, and old data is evicted at the same rate that new data is inserted*

#### Metric to alert on: mem\_fragmentation\_ratio

The `mem_fragmentation_ratio` metric gives the ratio of memory used as seen by the operating system to memory allocated by Redis.

<div style="font-size: 1.2em;">
$$MemoryFragmentationRatio={Used\_Memory\_RSS}/{(Used\_Memory)}$$
</div>

The operating system is responsible for allocating physical memory to each process. The operating system’s virtual memory manager handles the actual mapping, mediated by a memory allocator.

What does this mean? If your Redis instance has a memory footprint of 1GB, the memory allocator will first attempt to find a contiguous memory segment to store the data. If no contiguous segment is found, the allocator must divide the process’s data across segments, leading to increased memory overhead.

Tracking fragmentation ratio is important for understanding your Redis instance’s performance. A fragmentation ratio greater than 1 indicates fragmentation is occurring. A ratio in excess of 1.5 indicates excessive fragmentation, with your Redis instance consuming 150% of the physical memory it requested. A fragmentation ratio below 1 tells you that Redis needs more memory than is available on your system, which leads to swapping. Swapping to disk will cause significant increases in latency (see [used memory](#used-memory-metric)). Ideally, the operating system would allocate a contiguous segment in physical memory, with a fragmentation ratio equal to 1 or slightly greater.

If your server is suffering from a fragmentation ratio above 1.5, restarting your Redis instance will allow the operating system to recover memory previously unusable due to fragmentation. In this case, an [alert as a notification](https://www.datadoghq.com/blog/monitoring-101-alerting/#levels-of-urgency) is probably sufficient.

If, however, your Redis server has a fragmentation ratio below 1, you may want to [alert as a page](https://www.datadoghq.com/blog/pagerduty/) so that you can quickly increase available memory or reduce memory usage.

<div class="anchor" id="evicted-keys-metric"></div>

#### Metric to alert on: evicted\_keys (Cache only)

If you are using Redis as a cache, you may want to configure it to automatically purge keys upon hitting the `maxmemory` limit. If you are using Redis as a database or a queue, you may prefer swapping to eviction, in which case you can skip this metric.

Tracking key eviction is important because Redis processes each operation sequentially, meaning that evicting a large number of keys can lead to lower hit rates and thus longer latency times. If you are using [TTL](http://redis.io/commands/ttl), you may not expect to ever evict keys. In this case, if this metric is consistently above zero, you are likely to see an increase in latency in your instance. Most other configurations that don’t use TTL will eventually run out of memory and start evicting keys. So long as your response times are acceptable, a stable eviction rate is acceptable.

You can configure the key expiration policy with the command:

<table>
<colgroup>
<col width="50%" />
<col width="50%" />
</colgroup>
<tbody>
<tr class="odd">
<td align="left"><div class="crayon-nums-content" style="font-size: 14px !important; line-height: 18px !important;">
<div class="crayon-num" data-line="crayon-55e8aa22d0113005575096-1">
1
</div>
<div class="crayon-num" data-line="crayon-55e8aa22d0113005575096-2">
2
</div>
<div class="crayon-num" data-line="crayon-55e8aa22d0113005575096-3">
3
</div>
</div></td>
<td align="left"><div class="crayon-pre" style="font-size: 14px !important; line-height: 18px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;">
<div id="crayon-55e8aa22d0113005575096-1" class="crayon-line">
 
</div>
<div id="crayon-55e8aa22d0113005575096-2" class="crayon-line">
redis-cli CONFIG SET maxmemory-policy &lt;policy&gt;
</div>
<div id="crayon-55e8aa22d0113005575096-3" class="crayon-line">
 
</div>
</div></td>
</tr>
</tbody>
</table>

where `policy`; is one of the following:

-   **volatile-lru** removes the least recently used key among the ones with an expiration set
-   **volatile-ttl** removes a key with the shortest remaining time to live among the ones with an expiration set
-   **volatile-random** removes a random key among the ones with an expiration set.
-   **allkeys-lru** removes the least recently used key from the set of all keys
-   **allkeys-random** removes a random key from the set of all keys

NOTE: For performance reasons, Redis does not actually sample from the entire keyspace, when using an LRU or TTL policy. Redis first samples a random subset of the keyspace, and applies the eviction strategy on the sample. Generally, newer (&gt;=3) versions of Redis employ and LRU sampling strategy that is a closer approximation of true LRU.

<h4 id="blocked-clients" class="anchor">Metric to watch: blocked_clients</h4>

Redis offers a number of blocking commands which operate on lists. BLPOP, BRPOP, and BRPOPLPUSH are blocking variants of the commands LPOP, RPOP, and RPOPLPUSH, respectively. When the source list is non-empty, the commands perform as expected. However, when the source list is empty, the blocking commands will wait until the source is filled, or a timeout is reached.

An increase in the number of blocked clients waiting on data could be a sign of trouble. Latency or other issues could be preventing the source list from being filled. Although a blocked client in itself is not cause for alarm, if you are seeing a consistently nonzero value for this metric you should investigate.

<div class="anchor" id="basic-activity-metrics"></div>

### Basic activity metrics

| **Name**                       | **Description**                                                 | **[Metric Type](https://www.datadoghq.com/blog/monitoring-101-collecting-data/)** |
|--------------------------------|-----------------------------------------------------------------|-----------------------------------------------------------------------------------|
| connected\_clients             | Number of clients connected to Redis                            | Resource: Utilization                                                             |
| connected\_slaves              | Number of slaves connected to current master instance           | Other                                                                             |
| master\_last\_io\_seconds\_ago | Time in seconds since last interaction between slave and master | Other                                                                             |
| keyspace                       | Total number of keys in your database                           | Resource: Utilization                                                             |

#### Metric to alert on: connected\_clients

Because access to Redis is usually mediated by an application (users do not generally directly access the database), for most uses, there will be reasonable upper and lower bounds for the number of connected clients. If the number leaves the normal range, this could indicate a problem. If it is too low, upstream connections may have been lost, and if it is too high, the large number of concurrent client connections could overwhelm your server’s ability to handle requests.

Regardless, the maximum number of client connections is always a limited resource—whether by operating system, Redis’s configuration, or network limitations. Monitoring client connections helps you ensure you have enough free resources available for new clients or an administrative session.

#### Metric to alert on: connected\_slaves

If your database is read-heavy, you are probably making use of the master-slave database replication features available in Redis. In this case, monitoring the number of connected slaves is key. Should the number of connected slaves change unexpectedly, it could indicate a down host or problem with the slave instance.
 [![Redis Master-Slave](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-redis/1-img4.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-redis/1-img4.png)

NOTE: In the diagram above, the Redis Master would show that it has two connected slaves, and the first children would each report that they, too, have two connected slaves each. Because the secondary slaves are not directly connected to Redis Master, they are not included in Redis Master’s `connected_slaves`.

#### Metric to alert on: master\_last\_io\_seconds\_ago

When using Redis’s replication features, slave instances regularly check in with their master. A long time interval without communication could indicate a problem on your master Redis server, on the slave, or somewhere in between. You also run the risk of slaves serving old data that may have been changed since the last sync. Minimizing disruption of master-slave communication is critical due to the way Redis performs synchronization. When a slave connects to a master, whether for the first time or a reconnection, it sends a SYNC command. The SYNC command causes the master to immediately begin a background save of the database to disk, while buffering all new commands received that will modify the dataset. The data is sent to the client along with the buffered commands when the background save is complete. Each time a slave performs a SYNC, it can cause a significant spike in latency on the master instance.

#### Metric to watch: keyspace

Keeping track of the number of keys in your database is generally a good idea. As an in-memory data store, the larger the keyspace, the more physical memory Redis requires to ensure optimal performance. Redis will continue to add keys until it reaches the `maxmemory` limit, at which point it then begins evicting keys at the same rate new ones come in. This results in a “flat line” graph, like the one [above](#used-memory-metric).

If you are using Redis as a cache and see keyspace saturation as in the graph above coupled with a low hit rate, you may clients requesting old or evicted data. Tracking your number of `keyspace_misses` over time will help you pinpoint the cause.

Alternatively, if you are using Redis as a database or queue, volatile keys may not be an option. As your keyspace grows, you may want to consider adding memory to your box or splitting your dataset across hosts, if possible. Adding more memory is a simple and effective solution. When more resources are needed than one box can provide, partitioning or sharding your data allows you to combine the resources of many computers. With a partitioning plan in place, Redis can store more keys without evictions or swapping. However, applying a partitioning plan is much more challenging than swapping in a few memory sticks. Thankfully, the Redis documentation has a great section on implementing a partitioning scheme with your Redis instances, read more [here](http://redis.io/topics/partitioning).

[![Redis Keys by host](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-redis/1-img5.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-redis/1-img5.png)

<div class="anchor" id="persistence-metrics"></div>

### Persistence metrics

|                                 |                                                   |                                                                                   |
|---------------------------------|---------------------------------------------------|-----------------------------------------------------------------------------------|
| **Name**                        | **Description**                                   | **[Metric Type](https://www.datadoghq.com/blog/monitoring-101-collecting-data/)** |
| rdb\_last\_save\_time           | Unix timestamp of last save to disk               | Other                                                                             |
| rdb\_changes\_since\_last\_save | Number of changes to the database since last dump | Other                                                                             |

Enabling persistence can be necessary, especially if you are using Redis’s replication features. Because the slaves blindly copy any changes made to the master, if your master instance were to restart (without persistence), all slaves connected to it will copy its now-empty dataset.

Persistence may not be necessary if you are using Redis as a cache or in a use case where loss of data would be inconsequential.

#### Metrics to watch: rdb\_last\_save\_time and rdb\_changes\_since\_last\_save

Generally, it is a good idea to keep an eye on the volatility of your data set. Excessively long time intervals between writes to disk could cause data loss in the event of server failure. Any changes made to the data set between the last save time and time of failure are lost.

Monitoring `rdb_changes_since_last_save` gives you more insight into your data volatility. Long time intervals between writes are not a problem if your data set has not changed much in that interval. Tracking both metrics gives you a good idea of how much data you would lose should failure occur at a given point in time.

<div class="anchor" id="error-metrics"></div>

### Error metrics

Redis error metrics can alert you to anomalistic conditions. The following metrics track common errors:

| **Name**                           | **Description**                                                 | **[Metric Type](https://www.datadoghq.com/blog/monitoring-101-collecting-data/)** |
|------------------------------------|-----------------------------------------------------------------|-----------------------------------------------------------------------------------|
| rejected\_connections              | number of connections rejected due to hitting maxclient limit   | Resource: Saturation                                                              |
| keyspace\_misses                   | number of failed lookups of keys                                | Resource: Errors / Other                                                          |
| master\_link\_down\_since\_seconds | time in seconds of the link between master and slave being down | Resource: Errors                                                                  |

**Metric to alert on: rejected\_connections**

Redis is capable of handling many active connections, with a default of 10,000 client connections available. You can set the maximum number of connections to a different value, by altering the `maxclient` directive in redis.conf. Any new connection attempts will be disconnected if your Redis instance is currently at its maximum number of connections.

[![Redis Keys by host](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-redis/1-img6.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-redis/1-img6.png)

Note that your system may not support the number of connections you request with the `maxclient` directive. Redis checks with the kernel to determine the number of available file descriptor. If the number of available file descriptors is smaller than `maxclient` + 32 (Redis reserves 32 file descriptors for its own use), then the `maxclient` directive is ignored and the number of available file descriptors is used.

Refer to the documentation on [redis.io](http://redis.io/topics/clients) for more information on how Redis handles client connections.

#### Metric to alert on: keyspace\_misses

Every time Redis does a lookup of a key, there are only two possible outcomes: the key exists, or the key does not. Looking up a nonexistent key causes the keyspace\_misses counter to be incremented. A consistently nonzero value for this metric means that clients are attempting to find keys in your database which do not exist. If you are not using Redis as a cache, `keyspace_misses` should be at or near zero. Note that any blocking operation (BLPOP, BRPOP, and BRPOPLPUSH) called on an empty key will result in the `keyspace_misses` being incremented.

#### Metric to alert on: master\_link\_down\_since\_seconds

This metric is only available when the connection between a master and its slave has been lost. Ideally, this value should never exceed zero–the master and slave should be in constant communication to ensure the slave is not serving up stale data. A large time interval between connections should be addressed. Remember, upon reconnecting, your master Redis instance will need to devote resources to updating the data on the slave, which can cause an increase in latency.

**Conclusion**

In this post we’ve mentioned some of the most useful metrics you can monitor to keep tabs on your Redis servers. If you are just getting started with Redis, monitoring the metrics in the list below will provide good visibility into the health and performance of your database infrastructure:

-   [Number of commands processed per second](#performance-metrics)
-   [Latency](#performance-metrics)
-   [Memory fragmentation ratio](#memory-metrics)
-   [Evictions](#memory-metrics)
-   [Rejected clients](#error-metrics)

Eventually you will recognize additional metrics that are particularly relevant to your own infrastructure and use cases. Of course, what you monitor will depend on the tools you have and the metrics available to you. See the [companion post](https://www.datadoghq.com/blog/how-to-collect-redis-metrics) for step-by-step instructions on collecting Redis performance metrics.

