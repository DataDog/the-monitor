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

#### Key metrics

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

[![latency graph event-type ](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-redis/2-img1.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-redis/2-img1.png)

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

With so many metrics exposed, getting the information you want all in one place can be a challenge. Luckily, Datadog can help take the pain out of the process. At Datadog, we have built an integration with Redis so you can begin collecting and monitoring its metrics with a minimum of setup. Learn how Datadog can help you to monitor Redis in the [next and final part](https://www.datadoghq.com/blog/monitor-redis-using-datadog) of this series of articles.









この投稿は、Redisのモニタリングの3回シリーズの第2部です。パート1はDatadogあなたはRedisのを監視することができますどのようにキーRedisの中で使用可能なメトリック、およびパート3の詳細を探ります。
あなたが必要とRedisのメトリックを取得
Redisのは、箱から出して大規模な監視を提供します。このシリーズの最初の記事で述べたように、Redisのコマンドラインインターフェイスで、infoコマンドを使用すると、Redisのの現在のパフォーマンスのスナップショットを提供します。あなたは深く掘るしたい場合は、Redisのは、特定のメトリックでは、より詳細な外観を提供する他のツールの数を提供します。
Redisの-CLI情報
Redisのは、コマンドライン・インタフェースを介して、その診断ツールのほとんどを提供します。 RedisのCLIを入力するには、実行します。$ Redisの-CLIを使用している端末で。
プロンプトで情報を入力すると、あなたに一目で現在利用可能なすべてのRedisのメトリックを提供します。これは、パイプにファイル以下に出力に便利です。以下は、いくつかの切り捨てられた出力は、次のとおりです。
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
 
Redisの>情報
＃サーバー
redis_version：3.1.999
redis_git_sha1：bcb4d091
redis_git_dirty：1
redis_build_id：78a2361cc4e1c559
redis_mode：スタンドアロン
OS：Linuxの3.18.5-x86_64で-linode52 x86_64で
 
＃クライアント
connected_clients：8
client_longest_output_list：0
client_biggest_input_buf：0
blocked_clients：0
 
＃メモリ
used_memory：10532216
used_memory_human：10.04M
used_memory_rss：13107200
used_memory_rss_human：12.50M
used_memory_peak：10971672
used_memory_peak_human：10.46M
total_system_memory：4196720640
total_system_memory_human：3.91G
used_memory_lua：24576
used_memory_lua_human：24.00K
maxmemory：3221225472
maxmemory_human：3.00G
maxmemory_policy：不明
mem_fragmentation_ratio：1.24
mem_allocator：jemalloc-3.6.0
 
オプションの<section>の引数を追加すると、そのセクションのみの情報を返します。たとえば、以下の#Clientsセクションの情報が返されます情報クライアントを実行しています：
1
2
3
4
5
6
7
8
 
Redisの>情報クライアント
＃クライアント
connected_clients：8
client_longest_output_list：0
client_biggest_input_buf：0
blocked_clients：0
 
項目は以下のとおりです。
サーバー：Redisのサーバーに関する一般情報
統計：一般的な統計情報
メモリ：メモリ消費情報
クライアント：クライアント接続セクション
永続性：RDBとAOF情報
レプリケーション：マスター/スレーブレプリケーション情報
CPU：CPUの消費統計
Commandstats：Redisのコマンドの統計情報
クラスタ：Redisのクラスタ情報
キースペース：データベース関連の統計
主要指標
この連載の第1回では、監視の価値いくつかのRedisのメトリックを述べました。 infoコマンドでそれらを見つけるためにのはここです：
第メトリック
統計instantaneous_ops_per_sec
ヒット率*
evicted_keys
rejected_connections
keyspace_misses
メモリused_memory
mem_fragmentation_ratio
クライアントblocked_clients
connected_clients
持続性rdb_last_save_time
rdb_changes_since_last_save
レプリケーションmaster_link_down_since
connected_slaves
master_last_io_seconds_ago
キースペースキースペースサイズ
*唯一の例外は、このような統計情報部からのkeyspace_hitsとkeyspace_missesメトリックを使用して計算する必要があり、ヒット率は、次のとおりです。

ヒット率=
keyspace_hits
（keyspace_hits + keyspace_misses）
専用の監視
infoコマンドは、一目であなたのRedisのサーバーの正常性を確認するために、スタンドアロンのツールと​​して有用です。 Redisのは、サービスの重要な部分である場合は、あなたは確かに、時間をかけてその性能をグラフ化、インフラストラクチャ全体で他のメトリックとそのメトリックを相関し、それらが発生し、任意の問題に注意を喚起することになるでしょう。これを行うには、専用の監視サービスとRedisののメトリクスを統合する必要になります。
レイテンシ
いくつかの待ち時間はすべての環境に固有のものであるが、高遅延は、多くの原因を持つことができます。ネットワーク速度、他のホストプロセス、計算強烈なコマンドは、すべてのクロー​​ルにあなたの応答時間をもたらすことができます。幸いなことに、Redisのは、あなたが遅延の問題を診断するのに役立つさまざまなツールを提供しています：
Slowlog：指定された実行時間を超えてコマンドを一覧表示する実行ログ。非常に便利。
レイテンシーモニター：プロセスに時間がかかるのコマンドを追跡するためにあなたがslowlogと相関することができます時間をかけて、待ち時間のスパイクを追跡する強力な機能。待ち時間のスパイク時間を特定するために非常に有用。
ネットワーク遅延：ネットワークによって生じる遅延を測定ポイントツール。使用の制限された範囲。
組み込み待ち時間：サーバーの基本待ち時間の測定;使用の制限された範囲。
Slowlog
Redisののslowlogは、指定された実行時間を超えたすべてのコマンドのログです。ネットワーク遅延を測定、実際にコマンドを実行するのにかかる時間だけでは含まれていません。待ち時間モニタと組み合わせて使用​​する場合、slowlogはあなたの待ち時間の増加を引き起こしたコマンドの低レベルのビューを与えることができます。
slowlogの設定
指令の影響
slowlog-ログ遅いよりも実行時間（マイクロ秒単位）コマンドは、（すべてのコマンドのために0に設定）ログインする越えなければなりません
slowlogのエントリのslowlog-MAX-LEN最大数
slowlog-ログ遅いよりとslowlog-MAX-LEN：あなたのredis.confで2つのディレクティブでslowlogを設定することができます。 Redisのサーバーが稼働している間は、また、指令と任意の引数が続くのconfig setコマンドを使用して、ディレクティブを設定することができます。デフォルトでは、slowlog GETを実行するとslowlogの内容全体が返されます。あなたの出力を制限するには、GETパラメータの後のエントリ数を指定します。
slowlogエントリID、コマンドが実行されたときのUNIXタイムスタンプ、マイクロ秒単位の実行時間、および任意の引数と一緒にコマンド自体を持つ配列、：slowlogの各エントリには、4つのフィールドが含まれています。以下の出力例を参照してください。
1
2
3
4
5
6
7
8
9
10
11
12
13
 
Redisの> slowlog GET 2
1）1）（整数）21＃一意のID
   2）（整数）1439419285＃Unixタイムスタンプ
   3）（整数）マイクロ秒単位の19＃実行時間
   4）1）「スリープ」＃コマンド
2）1）（整数）20
   2）（整数）1439418163
   3）（整数）22
   4）1）「slowlog "＃コマンド
      2）＃引数1 "GET"
      3）「18」＃引数2
 
slowlogリセット：最後に、slowlogランをクリアします
レイテンシーモニター
レイテンシーモニタリングはレイテンシーの問題のトラブルシューティングに役立ちますRedisの2.8.13で導入された比較的新しい機能です。このツールは、待ち時間のサーバー上のスパイク、およびそれらの原因となるイベントをログに記録します。 Redisのドキュメントは、Redisのはについて報告待ち時間のイベントの完全なリストを与えるものではありませんが、それはイベントの種類の簡単な概要を与えるん。適切な名前高速コマンドが線形とで実行されたコマンドのイベント名はO（log n）時間が、他のコマンドのコマンドイベントを測定待ち時間。
あなたがredis.confでレイテンシーモニターしきい値のディレクティブを設定することによって、それを使用する前に、待ち時間の監視を有効にする必要があります。また、Redisの-CLIで、次のコマンドを実行します
1
2
3
 
Redisの>設定セットの待ち時間モニターしきい値<ミリ秒単位の時間>
 
しきい値を設定した後、あなたはレイテンシーモニターはあなたのRedisの-CLIでの待ち時間、最新のコマンドを実行して動作していることを確認することができるようになります。
1
2
3
4
5
6
7
 
Redisの>待ち時間最新
1）1） "コマンド"＃イベント名
   2）（整数）1439479413＃Unixタイムスタンプ
   3）（整数）の最新イベントの381＃レイテンシ
   4）（整数）6802＃すべての時間の最大待ち時間
 
出力は非常にきめ細かいありませんが、あなたが収集している他のメトリックと一緒にタイムスタンプを使用することができます。待ち時間最新とあなたのslowlogからの出力を相関させること、あなたがより良いあなたの環境で遅延の問題の原因を特定するために必要な情報を与えることができます。
レイテンシーモニターは、端末へのASCIIグラフを出力し、初歩的なグラフを提供しています。あなたは他のツールが関与することなく、特定の遅延のイベントの傾向を発見するためにそれを使用することができます。待ち時間グラフ<イベント型>：コマンドイベントタイプのグラフを表示するには、Redisの-CLI内から次のコマンドを実行します
待ち時間グラフイベント型
グラフは縦ラベル付きの最小値と最大応答時間の間に正規化されます。各列の下の時間は、そのイベントが発生してからの時間を表しています。上記の出力では、一番左の列は、24秒前に発生する、（も最速イベントであることを起こる）、最も古いイベントを示しています。
待ち時間モニタは、遅延のタイムスタンプのペアで160要素まで戻って、同様のイベントによって履歴データを提供しています。特定のイベントの待ち時間履歴にアクセスするには、実行します。待ち時間歴史を<イベント名>
1
2
3
4
5
6
7
8
 
Redisの>待ち時間historyコマンド
1）1）（整数）1425038819＃Unixタイムスタンプ
   ミリ秒で2）（整数）383＃実行時間（）
2）1）（整数）1425038944
   2）（整数）4513
[...]
 
最後に、すべてのイベントをリセットし、待ち時間のスパイク、実行待ち時間リセット<オプション・イベント名>をログに記録します。イベント名を指定せずにコマンドを実行すると、全体の履歴をクリアします。
ネットワーク遅延
固有の待ち時間をチェックすると、あなたのインスタンスの最低限の応答時間を与えるが、それは考慮にネットワークを負いません。 Redisのは、基本的にサーバーにpingを実行し、応答時間を測定し、あなたのネットワークレイテンシを確認するためのツールを提供します。あなたのネットワークの遅延を確認するには、クライアントホスト上のターミナルで次のコマンドを実行します。
1
2
3
 
$のRedisの-CLI --latency -h <RedisのIP> -p <Redisのポート>
 
手動で継続的に、これまでに測定（ミリ秒単位）の最小値、最大値、および平均待ち時間の値を更新し、停止するまで上記のコマンドは実行を継続します。
組み込み待ち時間
Redisの2.8.7は、あなたの本質的な、またはベースラインのレイテンシを測定することを可能にするRedisの-CLIの機能が導入されました。あなたのサーバー上で、あなたのRedisのディレクトリに変更し、次のコマンドを実行します。
1
2
3
4
5
6
7
 
$ ./redis-cli --intrinsic-待ち時間が<秒は、ベンチマークを実行します>
 
これまでの最大待ち時間：1マイクロ秒。
これまでの最大待ち時間：16マイクロ秒。
これまでの最大待ち時間：50マイクロ秒。
 
まとめ
Redisのの多くのツールは、その性能上のデータの富を提供しています。サーバーの健康や重要な待ち時間の原因を調べてをスポットチェックするために、Redisのの内蔵ツールは、ジョブのための十分以上です。
非常に多くのメトリックが露出すると、一箇所ですべての必要な情報を得ることは挑戦することができます。幸いなことに、Datadogは、プロセスのうち、痛みを取ることができます。セットアップを最小限に抑えて、そのメトリックの収集と監視を開始できるようDatadogで、我々はRedisのとの統合を構築しています。 Datadogはこの一連の記事の次のと最後の部分でRedisのを監視するのを助けることができる方法を学びます。
この記事のソース値下げはGitHubの上で利用可能です。ご質問、訂正、追加、など？私たちに知らせてください。
