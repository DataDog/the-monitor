# How to collect Redis metrics

*This post is part 2 of a 3-part series on Redis monitoring. [Part 1](https://www.datadoghq.com/blog/how-to-monitor-redis-performance-metrics) explores the key metrics available in Redis, and [Part 3](https://www.datadoghq.com/blog/monitor-redis-using-datadog) details how Datadog can help you monitor Redis.*

## Getting the Redis metrics you need

Redis provides extensive monitoring out of the box. As mentioned in the first post of this series, the info command in the Redis command line interface gives you a snapshot of Redis’s current performance. When you want to dig deeper, Redis provides a number of other tools that offer a more detailed look at specific metrics.

### redis-cli info

Redis provides most of its diagnostic tools through its command line interface. To enter the Redis cli, run:  `$ redis-cli` in your terminal.

Entering info at the prompt gives you all the Redis metrics currently available at a glance. It is useful to pipe the output to a file or less. Below is some truncated output:

<table>
<colgroup>
<col width="50%" />
<col width="50%" />
</colgroup>
<tbody>
<tr class="odd">
<td align="left"><div class="crayon-pre" style="font-size: 14px !important; line-height: 18px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;">
<div id="crayon-55e8b13111902362993737-1" class="crayon-line">
 
</div>
<div id="crayon-55e8b13111902362993737-2" class="crayon-line">
redis&gt; info
</div>
<div id="crayon-55e8b13111902362993737-3" class="crayon-line">
# Server
</div>
<div id="crayon-55e8b13111902362993737-4" class="crayon-line">
redis_version:3.1.999
</div>
<div id="crayon-55e8b13111902362993737-5" class="crayon-line">
redis_git_sha1:bcb4d091
</div>
<div id="crayon-55e8b13111902362993737-6" class="crayon-line">
redis_git_dirty:1
</div>
<div id="crayon-55e8b13111902362993737-7" class="crayon-line">
redis_build_id:78a2361cc4e1c559
</div>
<div id="crayon-55e8b13111902362993737-8" class="crayon-line">
redis_mode:standalone
</div>
<div id="crayon-55e8b13111902362993737-9" class="crayon-line">
os:Linux 3.18.5-x86_64-linode52 x86_64
</div>
<div id="crayon-55e8b13111902362993737-10" class="crayon-line">
 
</div>
<div id="crayon-55e8b13111902362993737-11" class="crayon-line">
# Clients
</div>
<div id="crayon-55e8b13111902362993737-12" class="crayon-line">
connected_clients:8
</div>
<div id="crayon-55e8b13111902362993737-13" class="crayon-line">
client_longest_output_list:0
</div>
<div id="crayon-55e8b13111902362993737-14" class="crayon-line">
client_biggest_input_buf:0
</div>
<div id="crayon-55e8b13111902362993737-15" class="crayon-line">
blocked_clients:0
</div>
<div id="crayon-55e8b13111902362993737-16" class="crayon-line">

</div>
<div id="crayon-55e8b13111902362993737-17" class="crayon-line">
# Memory
</div>
<div id="crayon-55e8b13111902362993737-18" class="crayon-line">
used_memory:10532216
</div>
<div id="crayon-55e8b13111902362993737-19" class="crayon-line">
used_memory_human:10.04M
</div>
<div id="crayon-55e8b13111902362993737-20" class="crayon-line">
used_memory_rss:13107200
</div>
<div id="crayon-55e8b13111902362993737-21" class="crayon-line">
used_memory_rss_human:12.50M
</div>
<div id="crayon-55e8b13111902362993737-22" class="crayon-line">
used_memory_peak:10971672
</div>
<div id="crayon-55e8b13111902362993737-23" class="crayon-line">
used_memory_peak_human:10.46M
</div>
<div id="crayon-55e8b13111902362993737-24" class="crayon-line">
total_system_memory:4196720640
</div>
<div id="crayon-55e8b13111902362993737-25" class="crayon-line">
total_system_memory_human:3.91G
</div>
<div id="crayon-55e8b13111902362993737-26" class="crayon-line">
used_memory_lua:24576
</div>
<div id="crayon-55e8b13111902362993737-27" class="crayon-line">
used_memory_lua_human:24.00K
</div>
<div id="crayon-55e8b13111902362993737-28" class="crayon-line">
maxmemory:3221225472
</div>
<div id="crayon-55e8b13111902362993737-29" class="crayon-line">
maxmemory_human:3.00G
</div>
<div id="crayon-55e8b13111902362993737-30" class="crayon-line">
maxmemory_policy:unknown
</div>
<div id="crayon-55e8b13111902362993737-31" class="crayon-line">
mem_fragmentation_ratio:1.24
</div>
<div id="crayon-55e8b13111902362993737-32" class="crayon-line">
mem_allocator:jemalloc-3.6.0
</div>
<div id="crayon-55e8b13111902362993737-33" class="crayon-line">
 
</div>
</div></td>
</tr>
</tbody>
</table>

Adding an optional `<section> `argument returns information on that section only. For example running `info clients` will return information in the \#Clients section below:

<table>
<colgroup>
<col width="50%" />
<col width="50%" />
</colgroup>
<tbody>
<tr class="odd">
<td align="left"><div class="crayon-pre" style="font-size: 14px !important; line-height: 18px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;">
<div id="crayon-55e8b13111918804225385-1" class="crayon-line">
 
</div>
<div id="crayon-55e8b13111918804225385-2" class="crayon-line">
redis&gt; info clients
</div>
<div id="crayon-55e8b13111918804225385-3" class="crayon-line">
# Clients
</div>
<div id="crayon-55e8b13111918804225385-4" class="crayon-line">
connected_clients:8
</div>
<div id="crayon-55e8b13111918804225385-5" class="crayon-line">
client_longest_output_list:0
</div>
<div id="crayon-55e8b13111918804225385-6" class="crayon-line">
client_biggest_input_buf:0
</div>
<div id="crayon-55e8b13111918804225385-7" class="crayon-line">
blocked_clients:0
</div>
<div id="crayon-55e8b13111918804225385-8" class="crayon-line">
 
</div>
</div></td>
</tr>
</tbody>
</table>

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

#### Key Redis metrics

In [Part 1](https://www.datadoghq.com/blog/how-to-monitor-redis-performance-metrics) of this series, we mentioned several Redis metrics worth monitoring. Here’s where to find them with the `info` command:

**Section**

**Metric**

`Stats`

instantaneous\_ops\_per\_sec
 hit rate\*
 evicted\_keys
 rejected\_connections
 keyspace\_misses

`Memory`

used\_memory
 mem\_fragmentation\_ratio

`Clients`

blocked\_clients
 connected\_clients

`Persistence`

rdb\_last\_save\_time
 rdb\_changes\_since\_last\_save

`Replication`

master\_link\_down\_since
 connected\_slaves
 master\_last\_io\_seconds\_ago

`Keyspace`

keyspace size

\*The only exception is the hit rate, which must be calculated using the **keyspace\_hits** and **keyspace\_misses** metrics from the Stats section like this:
 $$HitRate={keyspace\\\_hits}/{(keyspace\\\_hits+keyspace\\\_misses)}$$

#### Dedicated monitoring

The `info` command is useful as a standalone tool to check on the health of your Redis server at a glance. However, if Redis is a critical part of your service, you will certainly want to graph its performance over time, correlate its metrics with other metrics across your infrastructure, and be alerted to any issues as they arise. To do this would require integrating Redis’s metrics with a dedicated monitoring service.

### Latency

Some latency is inherent in every environment, but high latency can have a number of causes. Network speeds, other host processes, and computationally intense commands all can bring your response times to a crawl. Luckily, Redis offers a variety of tools to help you diagnose latency issues:

-   **Slowlog:** a running log listing commands which exceed a specified execution time; extremely useful.
-   **Latency monitor:** a powerful feature that tracks latency spikes over time which you can correlate with the slowlog to track down commands which take long to process; very useful for identifying latency spike times.
-   **Network latency:** a point tool that measures latency introduced by the network; limited scope of use.
-   **Intrinsic latency:** a measurement of the base latency of your server; limited scope of use.

#### Slowlog

The Redis slowlog is a log of all commands which exceed a specified run time. Network latency is not included in the measurement, just the time taken to actually execute the command. When used in combination with the latency monitor, the slowlog can give you a low-level view of the commands causing increases in latency.

##### Configuring the slowlog

| **Directive**           | **Effect**         
|-------------------------|-------------------------------------------------------------------------------------|                                                                 |
| slowlog-log-slower-than | Execution time (in µs) command must exceed to be logged (set to 0 for all commands) |
| slowlog-max-len         | Maximum number of entries in the slowlog                                            |

You can configure slowlog with two directives in your redis.conf: slowlog-log-slower-than and slowlog-max-len. You can also configure the directives while the Redis server is running, using the `config set` command, followed by the directive and any arguments. By default, running `slowlog get` returns the entire contents of the slowlog. To limit your output, specify the number of entries after the get parameter.

Each entry in the slowlog contains four fields: a slowlog entry ID, the Unix timestamp of when the command was run, the execution time in microseconds, and an array with the command itself, along with any arguments. See the example output below:

<table>
<colgroup>
<col width="50%" />
<col width="50%" />
</colgroup>
<tbody>
<tr class="odd">
<td align="left"><div class="crayon-pre" style="font-size: 14px !important; line-height: 18px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;">
<div id="crayon-55e8b13111927231725597-1" class="crayon-line">
 
</div>
<div id="crayon-55e8b13111927231725597-2" class="crayon-line">
redis&gt; slowlog get 2
</div>
<div id="crayon-55e8b13111927231725597-3" class="crayon-line">
1) 1) (integer) 21 # Unique ID
</div>
<div id="crayon-55e8b13111927231725597-4" class="crayon-line">
   2) (integer) 1439419285 # Unix timestamp
</div>
<div id="crayon-55e8b13111927231725597-5" class="crayon-line">
   3) (integer) 19 # Execution time in microseconds
</div>
<div id="crayon-55e8b13111927231725597-6" class="crayon-line">
   4) 1) &quot;sleep&quot; # Command
</div>
<div id="crayon-55e8b13111927231725597-7" class="crayon-line">
2) 1) (integer) 20
</div>
<div id="crayon-55e8b13111927231725597-8" class="crayon-line">
   2) (integer) 1439418163
</div>
<div id="crayon-55e8b13111927231725597-9" class="crayon-line">
   3) (integer) 22
</div>
<div id="crayon-55e8b13111927231725597-10" class="crayon-line">
   4) 1) &quot;slowlog&quot; # Command
</div>
<div id="crayon-55e8b13111927231725597-11" class="crayon-line">
      2) &quot;get&quot; # Argument 1
</div>
<div id="crayon-55e8b13111927231725597-12" class="crayon-line">
      3) &quot;18&quot; # Argument 2
</div>
<div id="crayon-55e8b13111927231725597-13" class="crayon-line">
 
</div>
</div></td>
</tr>
</tbody>
</table>

Finally, to clear the slowlog run: `slowlog reset`

#### Latency monitor

Latency monitoring is a relatively new feature introduced in Redis 2.8.13 that helps you troubleshoot latency problems. This tool logs latency spikes on your server, and the events that cause them. Though the [Redis documentation](http://redis.io/topics/latency-monitor) does not give a full list of the latency events Redis reports on, it does give a short overview of event types. The aptly named `fast-command` is the event name for commands executed in linear and O(log N) times while the command event measures latency of the other commands.

You must enable latency monitoring before you can use it, by setting the **latency-monitor-threshold** directive in your redis.conf. Alternatively, in the redis-cli, run:

<table>
<colgroup>
<col width="50%" />
<col width="50%" />
</colgroup>
<tbody>
<tr class="odd">
<td align="left"><div class="crayon-pre" style="font-size: 14px !important; line-height: 18px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;">
<div id="crayon-55e8b13111933773112447-1" class="crayon-line">
 
</div>
<div id="crayon-55e8b13111933773112447-2" class="crayon-line">
<span class="crayon-v">redis</span><span class="crayon-o">&gt;</span><span class="crayon-h"> </span><span class="crayon-e">config </span><span class="crayon-e">set </span><span class="crayon-v">latency</span><span class="crayon-o">-</span><span class="crayon-v">monitor</span><span class="crayon-o">-</span><span class="crayon-v">threshold</span><span class="crayon-h"> </span><span class="crayon-o">&lt;</span><span class="crayon-r">time</span><span class="crayon-h"> </span><span class="crayon-st">in</span><span class="crayon-h"> </span><span class="crayon-v">milliseconds</span><span class="crayon-o">&gt;</span>
</div>
<div id="crayon-55e8b13111933773112447-3" class="crayon-line">
 
</div>
</div></td>
</tr>
</tbody>
</table>

After setting the threshold, you will be able to confirm that latency monitor is working  by running the **latency latest** command in your redis-cli.

<table>
<colgroup>
<col width="50%" />
<col width="50%" />
</colgroup>
<tbody>
<tr class="odd">
<td align="left"><div class="crayon-pre" style="font-size: 14px !important; line-height: 18px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;">
<div id="crayon-55e8b1311193c290410125-1" class="crayon-line">
 
</div>
<div id="crayon-55e8b1311193c290410125-2" class="crayon-line">
redis&gt; latency latest
</div>
<div id="crayon-55e8b1311193c290410125-3" class="crayon-line">
1) 1) &quot;command&quot;         # Event name
</div>
<div id="crayon-55e8b1311193c290410125-4" class="crayon-line">
   2) (integer) 1439479413 # Unix timestamp
</div>
<div id="crayon-55e8b1311193c290410125-5" class="crayon-line">
   3) (integer) 381 # Latency of latest event
</div>
<div id="crayon-55e8b1311193c290410125-6" class="crayon-line">
   4) (integer) 6802 # All time maximum latency
</div>
<div id="crayon-55e8b1311193c290410125-7" class="crayon-line">
 
</div>
</div></td>
</tr>
</tbody>
</table>

Although the output is not very fine-grained, you can use the timestamps alongside other metrics you are collecting. Correlating the output from latency latest and your slowlog could give you the information you need to better pinpoint the causes of latency issues in your environment.

The latency monitor also offers rudimentary graphing, outputting ASCII graphs to the terminal. You can use it to spot trends in a specific latency event without having to involve other tools. To see a graph of the command event type, run the following from within the redis-cli: `latency graph <event-type>`

[![latency graph event-type ](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-redis/2-img1.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-redis/2-img1.png)

The graph is normalized between the minimum and maximum response times with vertical labels. The times beneath each column represent the time since that event occurred. In the above output, the leftmost column shows the oldest event (which also happens to be the fastest event), occurring 24 seconds ago.

The latency monitor offers historical data by event as well, returning up to 160 elements as latency-timestamp pairs. To access the latency history of a given event, run: `latency history <event-name>`

<table>
<colgroup>
<col width="50%" />
<col width="50%" />
</colgroup>
<tbody>
<tr class="odd">
<td align="left"><div class="crayon-pre" style="font-size: 14px !important; line-height: 18px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;">
<div id="crayon-55e8b13111943155842143-1" class="crayon-line">
 
</div>
<div id="crayon-55e8b13111943155842143-2" class="crayon-line">
redis&gt; latency history command
</div>
<div id="crayon-55e8b13111943155842143-3" class="crayon-line">
1) 1) (integer) 1425038819   # Unix timestamp
</div>
<div id="crayon-55e8b13111943155842143-4" class="crayon-line">
   2) (integer) 383      # Execution time (in ms)
</div>
<div id="crayon-55e8b13111943155842143-5" class="crayon-line">
2) 1) (integer) 1425038944
</div>
<div id="crayon-55e8b13111943155842143-6" class="crayon-line">
   2) (integer) 4513
</div>
<div id="crayon-55e8b13111943155842143-7" class="crayon-line">
[...]
</div>
<div id="crayon-55e8b13111943155842143-8" class="crayon-line">
 
</div>
</div></td>
</tr>
</tbody>
</table>

Finally, to reset all events and logged latency spikes, run `latency reset <optional-event-name>`. Running the command without an event name clears the entire history.

#### Network latency

While checking the intrinsic latency gives you the bare minimum response time of your instance, it does not take the network into account. Redis provides a tool to check your network latency, essentially pinging your server and measuring the response time. To check your network latency, run the following in a terminal on a client host:

<table>
<colgroup>
<col width="50%" />
<col width="50%" />
</colgroup>
<tbody>
<tr class="odd">

<td align="left"><div class="crayon-pre" style="font-size: 14px !important; line-height: 18px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;">
<div id="crayon-55e8b1311194a026854170-1" class="crayon-line">
 
</div>
<div id="crayon-55e8b1311194a026854170-2" class="crayon-line">
$ redis-cli --latency -h &lt;Redis IP&gt; -p &lt;Redis port&gt;
</div>
<div id="crayon-55e8b1311194a026854170-3" class="crayon-line">
 
</div>
</div></td>
</tr>
</tbody>
</table>

The above command will continue running until manually stopped, continuously updating values for the minimum, maximum, and average latency (in milliseconds) measured so far.

#### Intrinsic latency

Redis 2.8.7 introduced a feature to the redis-cli allowing you to measure your intrinsic, or baseline latency. On your server, change to your Redis directory and run the following:

<table>
<colgroup>
<col width="50%" />
<col width="50%" />
</colgroup>
<tbody>
<tr class="odd">

<td align="left"><div class="crayon-pre" style="font-size: 14px !important; line-height: 18px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;">
<div id="crayon-55e8b13111950152872673-1" class="crayon-line">
 
</div>
<div id="crayon-55e8b13111950152872673-2" class="crayon-line">
$ ./redis-cli --intrinsic-latency &lt;seconds to execute benchmark&gt;
</div>
<div id="crayon-55e8b13111950152872673-3" class="crayon-line">
 
</div>
<div id="crayon-55e8b13111950152872673-4" class="crayon-line">
Max latency so far: 1 microseconds.
</div>
<div id="crayon-55e8b13111950152872673-5" class="crayon-line">
Max latency so far: 16 microseconds.
</div>
<div id="crayon-55e8b13111950152872673-6" class="crayon-line">
Max latency so far: 50 microseconds.
</div>
<div id="crayon-55e8b13111950152872673-7" class="crayon-line">
 
</div>
</div></td>
</tr>
</tbody>
</table>

## **Conclusion**

Redis’s many tools offer a wealth of data on its performance. For spot-checking the health of your server or looking into causes of significant latency, Redis’s built-in tools are more than enough for the job.

With so many Redis metrics exposed, getting the information you want all in one place can be a challenge. Luckily, Datadog can help take the pain out of the process. At Datadog, we have built an integration with Redis so you can begin collecting and monitoring its metrics with a minimum of setup. Learn how Datadog can help you to monitor Redis metrics in the [next and final part](https://www.datadoghq.com/blog/monitor-redis-using-datadog) of this series of articles.

