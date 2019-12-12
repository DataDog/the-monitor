# How to collect Redis metrics


*This post is part 2 of a 3-part series on Redis monitoring. [Part 1](https://www.datadoghq.com/blog/how-to-monitor-redis-performance-metrics) explores the key metrics available in Redis, and [Part 3](https://www.datadoghq.com/blog/monitor-redis-using-datadog) details how Datadog can help you monitor Redis.*

Getting the Redis metrics you need
----------------------------------

Redis provides extensive monitoring out of the box. As mentioned in the first post of this series, the `info` command in the Redis command line interface gives you a snapshot of Redis's current performance. When you want to dig deeper, Redis provides a number of other tools that offer a more detailed look at specific metrics.

### redis-cli info

Redis provides most of its diagnostic tools through its command line interface. To enter the Redis cli, run:  `$ redis-cli` in your terminal.

Entering `info` at the prompt gives you all the Redis metrics currently available at a glance. It is useful to pipe the output to a file or less. Below is some truncated output:

```
redis> info
# Server
redis_version:3.1.999
redis_git_sha1:bcb4d091
redis_git_dirty:1
redis_build_id:78a2361cc4e1c559
redis_mode:standalone
os:Linux 3.18.5-x86_64-linode52 x86_64

# Clients
connected_clients:8
client_longest_output_list:0
client_biggest_input_buf:0
blocked_clients:0

# Memory
used_memory:10532216
used_memory_human:10.04M
used_memory_rss:13107200
used_memory_rss_human:12.50M
used_memory_peak:10971672
used_memory_peak_human:10.46M
total_system_memory:4196720640
total_system_memory_human:3.91G
used_memory_lua:24576
used_memory_lua_human:24.00K
maxmemory:3221225472
maxmemory_human:3.00G
maxmemory_policy:unknown
mem_fragmentation_ratio:1.24
mem_allocator:jemalloc-3.6.0
```

Adding an optional `<section>` argument returns information on that section only. For example running `info clients` will return information in the \#Clients section below:

```
redis> info clients
# Clients
connected_clients:8
client_longest_output_list:0
client_biggest_input_buf:0
blocked_clients:0
```

The sections are as follows:



-   `Server`: General information about the Redis server
-   `Stats`: General statistics
-   `Memory`: Memory consumption information
-   `Clients`: Client connections section
-   `Persistence`: RDB and AOF information
-   `Replication`: Master/slave replication information
-   `CPU`: CPU consumption statistics
-   `Commandstats`: Redis command statistics
-   `Cluster`: Redis Cluster information
-   `Keyspace`: Database related statistics



#### Key metrics

In [Part 1](https://www.datadoghq.com/blog/how-to-monitor-redis-performance-metrics) of this series, we mentioned several Redis metrics worth monitoring. Here’s where to find them with the `info` command:



<table>
<tbody>
<tr>
<td>
<strong>Section</strong>

</td>
<td>
<strong>Metric</strong>

</td>
</tr>
<tr>
<td>
<code>Stats</code>

</td>
<td>
instantaneous_ops_per_sec<br>
hit rate*<br>
evicted_keys<br>
rejected_connections<br>
keyspace_misses
</td>
</tr>
<tr>
<td>
<code>Memory</code>

</td>
<td>
used_memory<br>
mem_fragmentation_ratio
</td>
</tr>
<tr>
<td>
<code>Clients</code>

</td>
<td>
blocked_clients<br>
connected_clients

</td>
</tr>
<tr>
<td>
<code>Persistence</code>

</td>
<td>
rdb_last_save_time<br>
rdb_changes_since_last_save

</td>
</tr>
<tr>
<td>
<code>Replication</code>

</td>
<td>
master_link_down_since<br>
connected_slaves<br>
master_last_io_seconds_ago

</td>
</tr>
<tr>
<td>
<code>Keyspace</code>

</td>
<td>
keyspace size

</td>
</tr>
<tr>
<td style="text-align: left;" colspan="2">
*The only exception is the hit rate, which must be calculated using the <strong>keyspace_hits</strong> and <strong>keyspace_misses</strong> metrics from the Stats section like this:<br>
<code>HitRate=keyspace_hits/(keyspace_hits+keyspace_misses)</code>

</td>
</tr>
</tbody>
</table>



#### Dedicated monitoring

The `info` command is useful as a standalone tool to check on the health of your Redis server at a glance. However, if Redis is a critical part of your service, you will certainly want to graph its performance over time, correlate its metrics with other metrics across your infrastructure, and be alerted to any issues as they arise. To do this would require integrating Redis’s metrics with a dedicated monitoring service.

### Latency

Some latency is inherent in every environment, but high latency can have a number of causes. Network speeds, other host processes, and computationally intense commands all can bring your response times to a crawl. Luckily, Redis offers a variety of tools to help you diagnose latency issues:



-   **Slowlog:** a running log listing commands which exceed a specified execution time; extremely useful.
-   **Latency monitor:** a powerful feature that tracks latency spikes over time which you can correlate with the slowlog to track down commands which take long to process; very useful for identifying latency spike times.
-   **Network latency:** a point tool that measures latency introduced by the network; limited scope of use.
-   **Intrinsic latency:** a measurement of the base latency of your server; limited scope of use.
-   **Latency doctor:** an analysis tool that reports latency issues and provides possible solutions.



#### Slowlog

The Redis slowlog is a log of all commands which exceed a specified run time. Network latency is not included in the measurement, just the time taken to actually execute the command. When used in combination with the latency monitor, the slowlog can give you a low-level view of the commands causing increases in latency.

##### Configuring the slowlog



<table>
<tbody>
<tr class="odd">
<td><strong>Directive</strong></td>
<td><strong>Effect</strong></td>
</tr>
<tr class="even">
<td>slowlog-log-slower-than</td>
<td>Execution time (in µs) command must exceed to be logged (set to 0 for all commands)</td>
</tr>
<tr class="odd">
<td>slowlog-max-len</td>
<td>Maximum number of entries in the slowlog</td>
</tr>
</tbody>
</table>



You can configure slowlog with two directives in your redis.conf: slowlog-log-slower-than and slowlog-max-len. You can also configure the directives while the Redis server is running, using the `config set` command, followed by the directive and any arguments. By default, running `slowlog get` returns the entire contents of the slowlog. To limit your output, specify the number of entries after the get parameter.

Each entry in the slowlog contains four fields: a slowlog entry ID, the Unix timestamp of when the command was run, the execution time in microseconds, and an array with the command itself, along with any arguments. See the example output below:

```
redis> slowlog get 2
1) 1) (integer) 21    # Unique ID
   2) (integer) 1439419285  # Unix timestamp
   3) (integer) 19    # Execution time in microseconds
   4) 1) "sleep"    # Command
2) 1) (integer) 20
   2) (integer) 1439418163
   3) (integer) 22
   4) 1) "slowlog"    # Command
      2) "get"      # Argument 1
      3) "18"     # Argument 2
```

Redis versions 4.0 and higher include two additional fields: client IP/port and the client name if it's been set via the `client setname` command. 

Finally, to clear the slowlog run: `slowlog reset`.

#### Latency monitor

Latency monitoring is a relatively new feature introduced in Redis 2.8.13 that helps you troubleshoot latency problems. This tool logs latency spikes on your server, and the events that cause them. Though the [Redis documentation](http://redis.io/topics/latency-monitor) does not give a full list of the latency events Redis reports on, it does give a short overview of event types. The aptly named `fast-command` is the event name for commands executed in linear and O(log N) times while the command event measures latency of the other commands.

You must enable latency monitoring before you can use it, by setting the **latency-monitor-threshold** directive in your redis.conf. Alternatively, in the redis-cli, run:

    redis> config set latency-monitor-threshold <time in milliseconds>

After setting the threshold, you will be able to confirm that latency monitor is working  by running the `latency latest` command in your redis-cli.

```
redis> latency latest
1) 1) "command"           # Event name
   2) (integer) 1439479413  # Unix timestamp
   3) (integer) 381   # Latency of latest event
   4) (integer) 6802    # All time maximum latency
```

Although the output is not very fine-grained, you can use the timestamps alongside other metrics you are collecting. Correlating the output from latency latest and your slowlog could give you the information you need to better pinpoint the causes of latency issues in your environment.

The latency monitor also offers rudimentary graphing, outputting ASCII graphs to the terminal. You can use it to spot trends in a specific latency event without having to involve other tools. To see a graph of the command event type, run the following from within the redis-cli: `latency graph <event-type>`

{{< img src="2-img1.png" alt="latency graph event-type " popup="true" size="1x" >}}

The graph is normalized between the minimum and maximum response times with vertical labels. The times beneath each column represent the time since that event occurred. In the above output, the leftmost column shows the oldest event (which also happens to be the fastest event), occurring 24 seconds ago.

The latency monitor offers historical data by event as well, returning up to 160 elements as latency-timestamp pairs. To access the latency history of a given event, run: `latency history <event-name>`.

```
redis> latency history command
1) 1) (integer) 1425038819   # Unix timestamp
   2) (integer) 383      # Execution time (in ms)
2) 1) (integer) 1425038944
   2) (integer) 4513
[...]
```

Finally, to reset all events and logged latency spikes, run `latency reset <optional-event-name>`. Running the command without an event name clears the entire history.

#### Network latency

While checking the intrinsic latency gives you the bare minimum response time of your instance, it does not take the network into account. Redis provides a tool to check your network latency, essentially pinging your server and measuring the response time. To check your network latency, run the following in a terminal on a client host:

    $ redis-cli --latency -h <Redis IP> -p <Redis port>

The above command will continue running until manually stopped, continuously updating values for the minimum, maximum, and average latency (in milliseconds) measured so far.

#### Intrinsic latency

Redis 2.8.7 introduced a feature to the redis-cli allowing you to measure your intrinsic, or baseline latency. On your server, change to your Redis directory and run the following:


```
$ ./redis-cli --intrinsic-latency <seconds to execute benchmark>
 
Max latency so far: 1 microseconds.
Max latency so far: 16 microseconds.
Max latency so far: 50 microseconds.
```

#### Latency doctor

The `latency doctor` command is a more robust automated reporting tool that analyzes the Redis instance for potential latency issues. It returns detailed metrics and, if possible, suggestions for how to troubleshoot and fix problems. If latency spikes are detected, the latency doctor can provide statistics such as the average wait time for events, the average time between spikes, and the max latency measured. Based on its internal analysis, the latency doctor may give plain-English advice on further steps to take to uncover and fix causes of latency.

### Memory

Optimizing memory usage is a key aspect of maintaining Redis performance. Redis 4 added new `memory` commands that provide more detailed information about memory consumption. These include:

-   `memory doctor`: similar to the `latency doctor` tool, a feature that outputs memory consumption issues and provides possible solutions.
-   `memory usage <key> [samples <count>]`: an estimate of the amount of memory used by the given key. The optional `samples` argument specifies how many elements of an aggregate datatype to sample to approximate the total size. The default is 5.
-   `memory stats`: a detailed report of your instance's memory usage; similar to the memory section of `info`, it pulls in other client- and replication-related metrics.
-   `memory malloc-stats`: a detailed breakdown of the allocator's internal statistics.

**Conclusion**
--------------

Redis’s many tools offer a wealth of data on its performance. For spot-checking the health of your server or looking into causes of significant latency, Redis’s built-in tools are more than enough for the job.

With so many metrics exposed, getting the information you want all in one place can be a challenge. Luckily, Datadog can help take the pain out of the process. At Datadog, we have built an integration with Redis so you can begin collecting and monitoring its metrics with a minimum of setup. Learn how Datadog can help you to monitor Redis in the [next and final part](https://www.datadoghq.com/blog/monitor-redis-using-datadog) of this series of articles.

------------------------------------------------------------------------

*Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/redis/how_to_collect_redis_metrics.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues).*

