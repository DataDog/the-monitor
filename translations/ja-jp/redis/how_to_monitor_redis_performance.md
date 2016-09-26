＃[翻訳作業中]

# How to monitor Redis performance metrics

*This post is part 1 of a 3-part series on Redis monitoring. [Part 2](https://www.datadoghq.com/blog/how-to-collect-redis-metrics) is about collecting Redis metrics, and [Part 3](http://www.datadoghq.com/blog/monitor-redis-using-datadog/) details how to monitor Redis with Datadog.*

## What is Redis?

> Redis is a popular in-memory key/value data store. Known for its performance and simple onboarding, Redis has found uses across industries and use cases, including as a:

Redisは、メモリー上で動作するキーバリュー型のデータストアです。そして、高いパフォーマンスと簡単に導入できることで知られています。Redisは、次のようなユースケースで使われていることが多いです:

> - **Database:** as an alternative to a traditional disk-based database, Redis trades durability for speed, though asynchronous disk persistence is available. Redis offers a rich set of data primitives and an unusually extensive list of commands.
> - **Message queue:** Redis’s blocking list commands and low latency make it a good backend for a message broker service.
> - **Memory cache:** Configurable key eviction policies, including the popular Least Recently Used policy, make Redis a great choice as a cache server. Unlike a traditional cache, Redis also allows persistence to disk to improve reliability.

- **Database:** 従来のディスクベースのデータベースの代用として、採用されます。Redisは、非同期でのディスクへの永続保存が可能ですが、高いスピードを確保するために耐久性を一部犠牲にして動作します。Redisは、多くの基本データを提供し、それらを操作するための膨大な規模のコマンドリストを持っています。
- **Message queue:** Redisに実装されているブロックリスト・コマンドと短いレイテンシは、メッセージを仲介するサービスに最適なバックエンドになります。
- **Memory cache:** Redisには、設定可能なキーイベクションのポリシーやリーストリーセントのポリシーが存在するので、キャッシュサーバーしても素晴らしい選択です。伝統的なキャッシュとは異なり、Redisは、ディスクに対しキャッシュ情報を保存することができるので、信頼せも高いです。

> Redis is available as a free, open-source product. Commercial support is available, as is fully managed Redis-as-a-service.

Redisは、オープンソースとして無償で提供されている他、完全に管理されたRedis-as-a-serviceとして商業的に提供されています。

> Redis is employed by many high-traffic websites and applications such as Twitter, GitHub, Docker, Pinterest, Datadog, and Stack Overflow.

Redisは、Twitter、GitHub、Docker、 Ponterest、 Datadog、 Stack Overflowなど、高いトラフィックを処理しているWebサイトで採用されています。

## Key Redis Metrics

> Monitoring Redis can help catch problems in two areas: resource issues with Redis itself, and problems arising elsewhere in your supporting infrastructure.

Redisを監視することにより、次の二つの分野の問題を検知することができます:

  - Redisが消費しているリソースの問題
  - Redisを実行しているインフラの別の部分で起きている問題

> In this article we go though the most important Redis metrics in each of the following categories:

このポストでは、次に示したカテゴリー基づき、Redisの最重要メトリクスについて解説していきます:

-   [Performance metrics](#performance-metrics)
-   [Memory metrics](#memory-metrics)
-   [Basic activity metrics](#basic-activity-metrics)
-   [Persistence metrics](#persistence-metrics)
-   [Error metrics](#error-metrics)

Note that we use metric terminology [introduced in our Monitoring 101 series](https://www.datadoghq.com/blog/monitoring-101-collecting-data/), which provides a basic framework for metric collection and alerting.

### Performance metrics

Along with low error rates, good performance is one of the best top-level indicators of system health. Poor performance is most commonly caused by memory issues, as described in the [Memory section](#memory-metrics).

| **Name**                     | **Description**                                           | **[Metric Type](https://www.datadoghq.com/blog/monitoring-101-collecting-data/)** |
|------------------------------|-----------------------------------------------------------|-----------------------------------------------------------------------------------|
| latency                      | Average time for the Redis server to respond to a request | Work: Latency                                                                     |
| instantaneous\_ops\_per\_sec | Total number of commands processed per second             | Work: Throughput                                                                  |
| hit rate (calculated)        | keyspace\_hits / (keyspace\_hits + keyspace\_misses)      | Work: Success                                                                     |

#### Metric to alert on: latency

Latency is the measurement of the time it takes between a client request and the actual server response. Tracking latency is the most direct way to detect changes in Redis performance. Due to the single-threaded nature of Redis, outliers in your latency distribution could cause serious bottlenecks. A long response time for one request increases the latency for all subsequent requests.

Once you have determined that latency is an issue, there are several measures you can take to diagnose and address performance problems. Refer to the section “Using the latency command to improve performance” on page 14 in our white-paper, *[Understanding the Top 5 Redis Performance Metrics](http://go.datadoghq.com/top-5-redis-performance-metrics-guide)*.

[![Redis Latency graph](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-redis/1-img1.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-redis/1-img1.png)

#### Metric to watch: instantaneous\_ops\_per\_sec

Tracking the throughput of commands processed is critical for diagnosing causes of high latency in your Redis instance. High latency can be caused by a number of issues, from a backlogged command queue, to slow commands, to network link overutilization. You could investigate by measuring the number of commands processed per second—if it remains nearly constant, the cause is not a computationally intensive command. If one or more slow commands are causing the latency issues you would see your number of commands per second drop or stall completely.

A drop in the number of commands processed per second as compared to historical norms could be a sign of either low command volume or slow commands blocking the system. Low command volume could be normal, or it could be indicative of problems upstream. Identifying slow commands is detailed in [Part 2](https://www.datadoghq.com/blog/how-to-collect-redis-metrics) about Collecting Redis Metrics.

[![Redis Commands per second graph](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-redis/1-img2.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-redis/1-img2.png)

#### Metric to watch: hit rate

When using Redis as a cache, monitoring the cache hit rate can tell you if your cache is being used effectively or not. A low hit rate means that clients are looking for keys that no longer exist. Redis does not offer a hit rate metric directly. We can still calculate it like this:

<span style="font-size: 1.2em;">
 $$HitRate={keyspace\\\_hits}/{(keyspace\\\_hits+keyspace\\\_misses)}$$</span>

The `keyspace_misses` metric is discussed in the [Error metrics section](#error-metrics).

A low cache hit rate can be caused by a number of factors, including data expiration and insufficient memory allocated to Redis (which could cause key eviction). Low hit rates could cause increases in the latency of your applications, because they have to fetch data from a slower, alternative resource.

### Memory metrics

| **Name**                  | **Description**                                                                | **[Metric Type](https://www.datadoghq.com/blog/monitoring-101-collecting-data/)** |
|---------------------------|--------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| used\_memory              | Total number of bytes allocated by Redis                                       | Resource: Utilization                                                             |
| mem\_fragmentation\_ratio | Ratio of memory allocated by the operating system to memory requested by Redis | Resource: Saturation                                                              |
| evicted\_keys             | Number of keys removed due to reaching the maxmemory limit                     | Resource: Saturation                                                              |
| blocked\_clients          | Number of clients pending on a blocking call  (BLPOP, BRPOP, BRPOPLPUSH)       | Other                                                                             |

#### Metric to watch: used\_memory

Memory usage is a critical component of Redis performance. If `used_memory` exceeds the total available system memory, the operating system will begin swapping old/unused sections of memory. Every swapped section is written to disk, severely impacting performance. Writing or reading from disk is up to 5 orders of magnitude (100,000x!) slower than writing or reading from memory (0.1 µs for memory vs. 10 ms for disk).

You can configure Redis to remain confined to a specified amount of memory. Setting the `maxmemory` directive in the redis.conf file gives you direct control over Redis’s memory usage. Enabling `maxmemory` requires you to configure an eviction policy for Redis to determine how it should free up memory. Read more about configuring the maxmemory-policy directive in the [evicted\_keys section](#evicted-keys-metric).

[![Redis Memory used by host](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-redis/1-img3.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-redis/1-img3.png)

*This “flat line” pattern is common for Redis when it is used as a cache; all available memory is consumed, and old data is evicted at the same rate that new data is inserted*

#### Metric to alert on: mem\_fragmentation\_ratio

The `mem_fragmentation_ratio` metric gives the ratio of memory used as seen by the operating system to memory allocated by Redis.
 <span style="font-size: 1.2em;">
 $$MemoryFragmentationRatio={Used\\\_Memory\\\_RSS}/{(Used\\\_Memory)}$$</span>

The operating system is responsible for allocating physical memory to each process. The operating system’s virtual memory manager handles the actual mapping, mediated by a memory allocator.

What does this mean? If your Redis instance has a memory footprint of 1GB, the memory allocator will first attempt to find a contiguous memory segment to store the data. If no contiguous segment is found, the allocator must divide the process’s data across segments, leading to increased memory overhead.

Tracking fragmentation ratio is important for understanding your Redis instance’s performance. A fragmentation ratio greater than 1 indicates fragmentation is occurring. A ratio in excess of 1.5 indicates excessive fragmentation, with your Redis instance consuming 150% of the physical memory it requested. A fragmentation ratio below 1 tells you that Redis needs more memory than is available on your system, which leads to swapping. Swapping to disk will cause significant increases in latency (see [used memory](#used-memory-metric)). Ideally, the operating system would allocate a contiguous segment in physical memory, with a fragmentation ratio equal to 1 or slightly greater.

If your server is suffering from a fragmentation ratio above 1.5, restarting your Redis instance will allow will allow the operating system to recover memory previously unusable due to fragmentation. In this case, an [alert as a notification](https://www.datadoghq.com/blog/monitoring-101-alerting/#levels-of-urgency) is probably sufficient.

If, however, your Redis server has a fragmentation ratio below 1, you may want to [alert as a page](https://www.datadoghq.com/blog/pagerduty/) so that you can quickly increase available memory or reduce memory usage.

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

#### Metric to watch: blocked\_clients

Redis offers a number of blocking commands which operate on lists. BLPOP, BRPOP, and BRPOPLPUSH are blocking variants of the commands LPOP, RPOP, and RPOPLPUSH, respectively. When the source list is non-empty, the commands perform as expected. However, when the source list is empty, the blocking commands will wait until the source is filled, or a timeout is reached.

An increase in the number of blocked clients waiting on data could be a sign of trouble. Latency or other issues could be preventing the source list from being filled. Although a blocked client in itself is not cause for alarm, if you are seeing a consistently nonzero value for this metric you should investigate.

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
 [![Redis Master-Slave](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-redis/1-img4.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-redis/1-img4.png)

NOTE: In the diagram above, the Redis Master would show that it has two connected slaves, and the first children would each report that they, too, have two connected slaves each. Because the secondary slaves are not directly connected to Redis Master, they are not included in Redis Master’s `connected_slaves`.

#### Metric to alert on: master\_last\_io\_seconds\_ago

When using Redis’s replication features, slave instances regularly check in with their master. A long time interval without communication could indicate a problem on your master Redis server, on the slave, or somewhere in between. You also run the risk of slaves serving old data that may have been changed since the last sync. Minimizing disruption of master-slave communication is critical due to the way Redis performs synchronization. When a slave connects to a master, whether for the first time or a reconnection, it sends a SYNC command. The SYNC command causes the master to immediately begin a background save of the database to disk, while buffering all new commands received that will modify the dataset. The data is sent to the client along with the buffered commands when the background save is complete. Each time a slave performs a SYNC, it can cause a significant spike in latency on the master instance.

#### Metric to watch: keyspace

Keeping track of the number of keys in your database is generally a good idea. As an in-memory data store, the larger the keyspace, the more physical memory Redis requires to ensure optimal performance. Redis will continue to add keys until it reaches the `maxmemory` limit, at which point it then begins evicting keys at the same rate new ones come in. This results in a “flat line” graph, like the one [above](#used-memory-metric).

If you are using Redis as a cache and see keyspace saturation as in the graph above coupled with a low hit rate, you may clients requesting old or evicted data. Tracking your number of `keyspace_misses` over time will help you pinpoint the cause.

Alternatively, if you are using Redis as a database or queue, volatile keys may not be an option. As your keyspace grows, you may want to consider adding memory to your box or splitting your dataset across hosts, if possible. Adding more memory is a simple and effective solution. When more resources are needed than one box can provide, partitioning or sharding your data allows you to combine the resources of many computers. With a partitioning plan in place, Redis can store more keys without evictions or swapping. However, applying a partitioning plan is much more challenging than swapping in a few memory sticks. Thankfully, the Redis documentation has a great section on implementing a partitioning scheme with your Redis instances, read more [here](http://redis.io/topics/partitioning).

[![Redis Keys by host](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-redis/1-img5.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-redis/1-img5.png)

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

### Error metrics

Redis error metrics can alert you to anomalistic conditions. The following metrics track common errors:

| **Name**                           | **Description**                                                 | **[Metric Type](https://www.datadoghq.com/blog/monitoring-101-collecting-data/)** |
|------------------------------------|-----------------------------------------------------------------|-----------------------------------------------------------------------------------|
| rejected\_connections              | number of connections rejected due to hitting maxclient limit   | Resource: Saturation                                                              |
| keyspace\_misses                   | number of failed lookups of keys                                | Resource: Errors / Other                                                          |
| master\_link\_down\_since\_seconds | time in seconds of the link between master and slave being down | Resource: Errors                                                                  |

**Metric to alert on: rejected\_connections**

Redis is capable of handling many active connections, with a default of 10,000 client connections available. You can set the maximum number of connections to a different value, by altering the `maxclient` directive in redis.conf. Any new connection attempts will be disconnected if your Redis instance is currently at its maximum number of connections.

[![Redis Keys by host](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-redis/1-img6.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-redis/1-img6.png)

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

Eventually you will recognize additional metrics that are particularly relevant to your own infrastructure and use cases. Of course, what you monitor will depend on the tools you have and the metrics available to you. See the [companion post](https://www.datadoghq.com/blog/how-to-collect-redis-metrics) for step-by-step instructions on collecting Redis metrics.


この投稿は、Redisのモニタリングの3回シリーズの第1部です。第2部ではDatadogとRedisのを監視する方法Redisのメトリック、およびパート3の詳細を収集についてです。
Redisのは何ですか？
Redisのは、人気のインメモリキー/値のデータ・ストアです。そのパフォーマンスとシンプルなオンボーディングで知られ、Redisのはとして含む、産業やユースケース全体で使用を発見しました：
データベース：非同期ディスクの永続性が使用可能ですが、従来のディスクベースのデータベースに代わるものとして、Redisのは、速度のため耐久性の売買を行っています。 Redisのは、データプリミティブの豊富なセットとコマンドの非常に大規模なリストを提供しています。
メッセージキュー：Redisののブロックリストのコマンドと低レイテンシは、メッセージブローカサービスの良いバックエンドにします。
メモリキャッシュ：人気の最低使用ポリシーを含む設定可能なキー立ち退きポリシーは、Redisのキャッシュサーバとして素晴らしい選択肢となっています。伝統的なキャッシュとは異なり、Redisのも信頼性を向上させるためにディスクに永続性を可能にします。
Redisのは、フリー、オープンソース製品として提供されています。完全にRedisのサービスとして管理されるように商用サポートは、提供されています。
Redisのは、ツイッター、GitHubに、デッカー、Pinterest、Datadog、およびスタックオーバーフローなど多くの高トラフィックのウェブサイトやアプリケーションで採用されています。
キーRedisのメトリック
リソースの問題Redisの自体に、あなたのサポートインフラストラクチャ内の他の場所で発生する問題：Redisのは、2つの領域でのキャッチの問題を助けることができる監視。
この記事では、次の各カテゴリの中で最も重要なRedisのメトリックかかわらずアクセスしてください。
パフォーマンスメトリック
メモリメトリック
基本的な活動指標
持続性の指標
エラーメトリック
我々はメトリック収集とアラートのための基本的なフレームワークを提供し、当社のモニタリング101シリーズで導入されたメトリックの用語を使用することに注意してください。
パフォーマンスメトリック
低エラーレートに加えて、良好なパフォーマンスは、システムヘルスの最高のトップレベルの指標の一つです。メモリ・セクションで説明したように、パフォーマンスの低下は、最も一般的には、メモリの問題によって引き起こされます。
名前説明メトリックタイプ
Redisのサーバが要求作業に応答するまでの待ち時間の平均時間：パフォーマンス
二作目あたりに処理されたコマンドのinstantaneous_ops_per_sec総数：スループット
ヒット率（計算）keyspace_hits /（keyspace_hits + keyspace_misses）ワーク：成功
待ち時間：に警告するメトリック
待ち時間は、クライアントの要求と実際のサーバ応答の間にかかる時間を測定することです。トラッキング待ち時間はRedisの性能の変化を検出するための最も直接的な方法です。 Redisのためのシングルスレッドの性質のために、あなたの待ち時間分布の異常値は、重大なボトルネックを引き起こす可能性があります。 1要求に対する長い応答時間は、その後のすべての要求のための待ち時間が増加します。
あなたは待ち時間が問題であることを確認したら、いくつかのあなたが診断するために取ることができる対策とアドレスのパフォーマンスの問題があります。トップ5 Redisのパフォーマンス・メトリックを理解し、当社のホワイトペーパーでは、14ページの「パフォーマンスを向上させるための待ち時間コマンドを使用する」を参照してください。
Redisのレイテンシグラフ
監視するメトリック：instantaneous_ops_per_sec
処理されたコマンドのスループットを追跡するあなたのRedisのインスタンスで高遅延の原因を診断するために重要です。高遅延は、リンクoverutilizationをネットワークに、コマンドを遅らせるために、バックログコマンドキューから、多くの問題によって引き起こされる場合があります。それは原因が計算集約コマンドではない、ほぼ一定のままであれば第二あなたは当たりに処理コマンドの数を測定することにより、調査ができます。一つ以上の遅いコマンドが待ち時間の問題を引き起こしている場合、あなたは番目のドロップあたりのコマンドのあなたの番号を参照するか、完全に失速します。
歴史的な規範と比較して、秒あたりに処理するコマンドの数の低下は、低コマンドボリュームまたはシステムを遮断遅いコマンドのいずれかの兆候である可能性があります。低コマンドボリュームが正常であるか、またはそれは上流の問題を示すことができました。遅いのコマンドを識別することはRedisのメトリックの収集についてパート2に詳述されています。
2番目のグラフあたりのRedisのコマンド
監視するメトリック：ヒット率
キャッシュとしてRedisのを使用する場合は、あなたのキャッシュが効果的かを使用している場合は、キャッシュヒット率を監視することを伝えることができます。低ヒット率は、クライアントがもはや存在しないキーを探していることを意味します。 Redisのは、直接ヒット率メトリックを提供していません。我々はまだこのようにそれを計算することができます。

ヒット率=
keyspace_hits
（keyspace_hits + keyspace_misses）
keyspace_missesメトリックは、エラーメトリックのセクションで説明します。
低キャッシュヒット率は、データの有効期限と（キー立ち退きを引き起こす可能性があります）Redisのに割り当てられたメモリ不足など、多くの要因によって引き起こされる場合があります。彼らは遅く、代替リソースからデータをフェッチする必要があるため、低ヒット率は、アプリケーションの待ち時間の増加を引き起こす可能性があります。
メモリメトリック
名前説明メトリックタイプ
Redisのリソースによって割り当てられたバイトのused_memory総数：利用
Redisのリソースによって要求されたメモリへのオペレーティングシステムによって割り当てられたメモリのmem_fragmentation_ratio比：彩度
evicted_keysによるmaxmemory制限リソースに達するまで除去キーの数：彩度
blocked_clientsブロッキング呼び出しに保留中のクライアントの数（BLPOP、BRPOP、BRPOPLPUSH）その他
監視するメトリック：used_memory
メモリ使用量は、Redisの性能の重要なコンポーネントです。 used_memoryは、総利用可能なシステムメモリを超える場合は、オペレーティング・システムは、メモリの古い/未使用セクションをスワップを開始します。すべてのスワップセクションは、パフォーマンスが大幅に影響を与え、ディスクに書き込まれます。書き込みまたはディスクからの読み取りは、5桁（100,000！）メモリの読み書きよりも遅い（ディスク用の10ミリ対メモリの0.1マイクロ秒）までです。
あなたは指定された量のメモリに閉じ込めたままにRedisのを設定することができます。 redis.confファイルにmaxmemoryディレクティブを設定すると、あなたのRedisののメモリ使用量を直接制御することができます。 maxmemoryを有効にすると、それはメモリを解放する方法を決定するためにRedisのための立ち退きポリシーを設定する必要があります。 evicted_keysセクションでmaxmemoryポリシーディレクティブの設定については、こちらをご覧ください。
Redisのメモリホストで使用されます
それがキャッシュとして使用されている場合、この「フラットライン」パターンは、Redisのための一般的です。すべての利用可能なメモリが消費され、古いデータが新しいデータが挿入されるのと同じ速度で追い出されます
mem_fragmentation_ratio：に警告するためのメトリック
Redisのによって割り当てられたメモリへのオペレーティングシステムによって見られるようにmem_fragmentation_ratioメトリックが使用するメモリの割合を示します。

MemoryFragmentationRatio =
Used_Memory_RSS
（Used_Memory）
オペレーティングシステムは、各プロセスに物理メモリを割り当てる責任があります。オペレーティングシステムの仮想メモリマネージャは、メモリアロケータによって媒介実際のマッピングを処理します。
これは何を意味するのでしょうか？あなたのRedisのインスタンスが1ギガバイトのメモリフットプリントを持っている場合は、メモリアロケータは、最初にデータを保存するために連続したメモリ・セグメントを見つけるためにしようとします。何の連続セグメントが見つからない場合、アロケータは増加したメモリのオーバーヘッドにつながる、セグメントでプロセスのデータを分割しなければなりません。
断片化率を追跡するあなたのRedisのインスタンスのパフォーマンスを理解するために重要です。 1より大きい断片化率は、断片化が発生していることを示しています。 1.5を超える比は、Redisのインスタンスは、それが要求された物理メモリの150％を消費して、過度の断片化を示しています。 1以下の断片化率はRedisのがスワッピングにつながるシステム上で利用できるよりも多くのメモリを必要としていることを示しています。ディスクへのスワップと、待ち時間の大幅な増加を（使用メモリを参照）が発生します。理想的には、オペレーティング・システムは、1またはわずかに大きいに等しいフラグメンテーション比で、物理メモリ内の連続した​​セグメントを割り当てることになります。
サーバーが1.5を超える断片化率に苦しんでいる場合は、オペレーティング・システムが断片化のために以前に使用不可能なメモリを回復することができますことができますあなたのRedisのインスタンスを再起動します。この場合には、アラート通知など、おそらく十分です。
しかし、あなたのRedisのサーバーが1以下の断片化率を持っている場合、あなたはすぐに使用可能なメモリを増やすか、メモリ使用量を減らすことができるようにページとして警告することができます。
メトリックに警告する：evicted_keys（キャッシュのみ）
あなたがキャッシュとしてRedisのを使用している場合は、自動的にmaxmemory限界を打つ時にキーを削除するように設定することもできます。データベースやキューとしてRedisのを使用している場合、あなたはこのメトリックをスキップすることができ、その場合には立ち退きにスワップ好むかもしれません。
Redisのは、多数のキーを立ち退かすると低いヒット率、したがって、より長い待ち時間につながることができますことを意味し、各操作を順次処理するための鍵立ち退きを追跡することが重要です。あなたはTTLを使用している場合、あなたは今までのキーを立ち退かせることを期待しないことがあります。この場合、このメトリックは、あなたの場合の待ち時間の増加を参照してくださいする可能性があり、一貫してゼロ以上である場合。 TTLは、最終的にメモリ不足と鍵を追い出しが開始されます使用していない他のほとんどの構成。限りあなたの応答時間が許容されるように、安定した立ち退き率が許容可能です。
あなたはコマンドを使用して、キーの有効期限ポリシーを設定できます。
1
2
3

Redisの-CLI CONFIG SET maxmemoryポリシー<ポリシー>

どこポリシー。次のいずれかです。
揮発性LRUは、有効期限が設定されたものの中で最も最近使用されたキーを削除します
揮発性-TTLは、有効期限が設定されたものの中で生活する最短の残りの時間を持つキーを削除します
揮発性ランダムには有効期限が設定されたものの中でランダムキーを削除します。
allkeys-LRUは、すべてのキーのセットから少なくとも最近使用されたキーを削除します
allkeysランダムは、すべてのキーのセットからランダムなキーを削除します
注：LRUまたはTTLポリシーを使用すると、パフォーマンス上の理由から、Redisのは、実際には、全体のキースペースからサンプリングしません。 Redisの最初のサンプル鍵空間のランダムなサブセット、およびサンプルの立ち退き戦略を適用します。一般的に、新しい（> = 3）Redisののバージョンが使用し、真のLRUの近い近似であるLRUのサンプリング戦略。
監視するメトリック：blocked_clients
Redisのは、リストを操作するコマンドをブロックの数を提供しています。 BLPOP、BRPOP、およびBRPOPLPUSHは、それぞれのコマンドのLPOP、RPOP、およびRPOPLPUSHの変異体をブロックしています。ソースリストが空でない場合に予想されるように、コマンドが実行されます。ソースリストが空である場合、放射源が充填され、またはタイムアウトに達するまでは、遮断コマンドを待機します。
データを待っているブロックされたクライアントの数の増加は、トラブルの兆候である可能性があります。遅延やその他の問題が充填されてからソースリストを防止することができます。自体にブロックされたクライアントは、アラームの原因とされていませんが、あなたがこのメトリックの一貫ゼロ以外の値を見ている場合は、調査する必要があります。
基本的な活動指標
名前説明メトリックタイプ
Redisのリソースに接続しているクライアントの数をconnected_clients：使用率
その他の現在のマスター・インスタンスに接続されているスレーブのconnected_slaves数
スレーブと他のマスターとの間の最後の対話からの秒数で時間をmaster_last_io_seconds_ago
データベースリソースのキーのキースペース総数：利用
メトリックに警告する：connected_clientsを
Redisのへのアクセスは、通常、アプリケーションによって媒介されるので、（ユーザーが、一般的に、データベースに直接アクセスしません）ほとんどの用途のために、接続しているクライアントの数のための合理的な上限と下限が存在することになります。数が正常範囲を離れる場合は、問題が発生している可能性があります。それが低すぎると、上流の接続が失われた可能性があり、それが高すぎると、同時クライアント接続多数の要求を処理するためのサーバの能力を圧倒する可能性があります。
いずれにしても、クライアント接続の最大数は常に制限されたオペレーティングシステム、Redisのの設定、またはネットワークの制限によりリソースかどうか。クライアント接続を監視することは、あなたが新しいクライアントまたは管理セッションのために利用できる十分な空きリソースがあることを確認するのに役立ちます。
メトリックに警告する：connected_slavesを
データベースが読み取り重いされている場合、あなたはおそらくRedisの中で利用可能なマスター・スレーブデータベースのレプリケーション機能を利用しています。この場合、接続されたスレーブの数を監視するキーです。接続されたスレーブの数が予想外に変更する必要があり、それがスレーブ・インスタンスにダウンしたホストまたは問題を示している可能性があります。
Redisのマスタースレーブ
注：上記の図では、Redisのマスターは、2つの接続された奴隷を持っていることを示すであろうし、最初の子どもたちは、それぞれ彼らは、あまりにも、2つの接続されたスレーブそれぞれを持っていることを報告します。二次奴隷が直接Redisのマスターに接続されていないので、それらはRedisの修士connected_slavesに含まれていません。
master_last_io_seconds_ago：に警告するメトリック
Redisのの複製機能を使用する場合は、スレーブ・インスタンスは、定期的にマスターにチェックイン。通信せずに長い時間間隔がスレーブ上、またはどこかの間に、あなたのマスターRedisのサーバーに問題がある可能性があります。また、最後の同期以降に変更されている可能性があり、古いデータを提供するスレーブの危険性があります。マスター・スレーブ通信の中断を最小限にすることは、Redisのは、同期を実行する方法に重大です。スレーブがマスタに接続すると、最初の時間または再接続するかどうか、それはSYNCコマンドを送信します。 SYNCコマンドは、すべての新しいコマンドをバッファリングすると、そのデータセットを変更します受けながらマスターはすぐに、ディスクへのデータベースの保存背景を開始させます。セーブ背景が完了すると、データがバッファリングされたコマンドと一緒にクライアントに送信されます。スレーブがSYNCを実行するたびに、マスタインスタンスの待ち時間が大幅にスパイクを引き起こす可能性があります。
監視するメトリック：キースペース
データベース内のキーの数を追跡することは一般的に良いアイデアです。インメモリデータストアとして、キースペースが大きいほど、より多くの物理メモリRedisのは、最適なパフォーマンスを確保するために必要です。それは、新しいものが入ってくるのと同じ速度で鍵を立ち退か始まり、その時点でRedisのは、それがmaxmemory制限に達するまでキーを追加していきます。これは、上記のような、「フラットライン」のグラフになります。
あなたがキャッシュとしてRedisのを使用して、低ヒット率と相まって上のグラフのように鍵空間彩度を参照している場合は、クライアントが古いか、追い出されたデータを要求することがあります。時間をかけてkeyspace_missesのあなたの数を追跡すると、原因を特定するのに役立ちます。
データベースやキューとしてRedisのを使用している場合あるいは、揮発性キーはオプションではないかもしれません。あなたのキースペースが大きくなるにつれて、あなたは、可能な場合は、あなたのボックスにメモリを追加したり、ホスト間でデータセットを分割することを検討してください。より多くのメモリを追加することは簡単で効果的なソリューションです。より多くのリソースを1つのボックスが提供できるよりも必要とされている場合には、分割したり、データをシャーディングでは、多くのコンピュータのリソースを組み合わせることができます。代わりにパーティション化計画では、Redisのは立ち退きやスワッピングなしで複数のキーを格納することができます。しかし、分割計画を適用することで、いくつかのメモリスティックに交換するよりもはるかに困難です。ありがたいことに、Redisのドキュメントは、よりここに読み、あなたのRedisのインスタンスとパーティションスキームの実装に大きなセクションがあります。
ホストによるRedisのキー
持続性の指標
名前説明メトリックタイプ
最後のrdb_last_save_time Unixタイムスタンプは、他のディスクに保存
最後のダンプその他以来のデータベースへの変更のrdb_changes_since_last_save数
持続性を有効にすると、Redisのの複製機能を使用している場合は特に、必要になることができます。スレーブは盲目的マスター・インスタンスが（持続性なし）を再起動した場合、マスターに加えられた変更をコピーするので、それに接続されているすべてのスレーブは、空になったデータセットをコピーします。
あなたがキャッシュとしてやデータの損失は取るに足らないようになり、ユースケースにRedisのを使用している場合、永続性は必要ではないかもしれません。
監視するメトリック：rdb_last_save_timeとrdb_changes_since_last_save
一般的に、それはあなたのデータセットのボラティリティに目を維持することをお勧めします。ディスクへの書き込みの間に過度に長い時間間隔は、サーバの障害発生時にデータの損失を引き起こす可能性があります。保存前回と失敗の時間との間のデータ・セットに加えた変更は失われます。
監視rdb_changes_since_last_saveは、あなたのデータの変動にもっと洞察力を与えます。データセットは、その区間であまり変化していない場合は、書き込みの間に長い時間間隔は問題ではありません。両方のメトリックを追跡することは、あなたが障害が任意の時点で発生すべき失うことになるどのくらいのデータの良いアイデアを提供します。
エラーメトリック
Redisのエラーメトリックは変則条件を警告することができます。次のメトリックは、一般的なエラーを追跡：
名前説明メトリックタイプ
rejected_connectionsによるmaxclient制限リソースを打つに拒否された接続の数：彩度
エラー/その他：キーリソースの失敗したルックアップの回数をkeyspace_misses
マスタとスレーブは、リソースをダウンしているとの間のリンクの時間を秒単位でmaster_link_down_since_seconds：エラー
メトリックに警告する：rejected_connectionsを
Redisのは、利用可能な万クライアント接続のデフォルトで、多くのアクティブな接続を処理することが可能です。あなたはredis.confにmaxclientディレクティブを変更することによって、異なる値に最大接続数を設定することができます。あなたのRedisのインスタンスが接続の最大数に現在ある場合は、任意の新しい接続試行が切断されます。
ホストによるRedisのキー
お使いのシステムは、あなたがmaxclientディレクティブで要求する接続の数をサポートしていない可能性があることに注意してください。 Redisのは、使用可能なファイル記述子の数を決定するためにカーネルをチェックします。利用可能なファイル記述子の数は、maxclient + 32（Redisのは、自身が使用するための32のファイル記述子を留保）よりも小さい場合、maxclientディレクティブは無視され、使用可能なファイル記述子の数が使用されます。
Redisのは、クライアント接続を処理する方法の詳細については、redis.io上のドキュメントを参照してください。
メトリックに警告する：keyspace_missesを
Redisのは、キーのルックアップを行うたびに、2つだけの可能な結果があります：キーが存在する場合、またはキーがありません。存在しないキーを見るとkeyspace_missesカウンタがインクリメントされます。このメトリックの一貫ゼロ以外の値は、クライアントが存在しないデータベース内のキーを検索しようとしていることを意味します。あなたがキャッシュとしてRedisのを使用していない場合、keyspace_missesはゼロまたはその付近でなければなりません。空のキーで呼び出される任意のブロッキング操作（BLPOP、BRPOP、およびBRPOPLPUSH）がインクリメントされkeyspace_missesとなることに注意して下さい。
メトリックに警告する：master_link_down_since_secondsを
このメトリックは、マスターとそのスレーブ間の接続が失われた場合にのみ使用可能です。理想的には、この値はゼロマスタとスレーブは、スレーブが古いデータを提供していないことを確認するために一定の通信である必要があります超えないようにしてください。接続の間に大きな時間間隔に対処する必要があります。覚えておいて、再接続時に、インスタンスRedisのマスターは、待ち時間の増加を引き起こすことができ、スレーブにデータを更新する資源を投入する必要があります。
まとめ
この記事では、我々はあなたのRedisのサーバー上のタブを保つために監視することができる最も有用な測定基準のいくつかを述べました。あなただけのRedisの使用を開始している場合は、下のリストにメトリックを監視すると、データベース・インフラストラクチャの健全性とパフォーマンスに優れた可視性を提供します：
秒あたりに処理コマンドの数
レイテンシ
メモリの断片化率
立ち退き
拒否されたクライアント
最終的にあなたがあなた自身のインフラストラクチャと使用例に特に関連している、他の指標を認識します。もちろん、あなたが監視何を持っているツールと使用可能なメトリックに依存します。 Redisのメトリックを収集する手順のためのコンパニオンの記事を参照してください。
この記事のソース値下げはGitHubの上で利用可能です。ご質問、訂正、追加、など？私たちに知らせてください。
