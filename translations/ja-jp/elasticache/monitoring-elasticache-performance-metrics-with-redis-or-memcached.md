> *This post is part 1 of a 3-part series on monitoring Amazon ElastiCache. [Part 2](https://www.datadoghq.com/blog/collecting-elasticache-metrics-its-redis-memcached-metrics) explains how to collect its performance metrics, and [Part 3](https://www.datadoghq.com/blog/how-coursera-monitors-elasticache-and-memcached-performance) describes how Coursera monitors ElastiCache.*

*このポストは、Amazon ElastiCacheの監視について解説した3回シリーズのPart 1です。[Part 2](https://www.datadoghq.com/blog/collecting-elasticache-metrics-its-redis-memcached-metr)では、ElastiCacheからパフォーマンスメトリックを収集する方法を解説します。[Part 3](https://www.datadoghq.com/blog/how-coursera-monitors-elasticache-and-memcached-performance)では、[Coursera](https://www.coursera.org/)がElastiCacheを監視する方法について解説します。*


## What is Amazon ElastiCache?

> ElastiCache is a fully managed in-memory cache service offered by AWS. A cache stores often-used assets (such as files, images, css) to respond without hitting the backend and speed up requests. Using a cache greatly improves throughput and reduces latency of read-intensive workloads.

ElastiCacheは、AWSが提供するフルマネージドのインメモリキャッシュのサービスです。一般的にキャッシュストアは、ファイル、画像、CSSなどへのリクエストを、バックエンドに問い合わせをすることなく、スピーディーに応答するために使われます。キャッシュを使用すると、スループットが大幅に向上し、読み取りに集中した作業負荷のレイテンシを低く抑えることができます。


> AWS allows you to choose between [Redis](https://www.datadoghq.com/blog/how-to-monitor-redis-performance-metrics/) and [Memcached](https://www.datadoghq.com/blog/speed-up-web-applications-memcached/) as caching engine that powers ElastiCache. Among the thousands of Datadog customers using ElastiCache, Redis is much more commonly used than Memcached. But each technology presents unique advantages depending on your needs. [AWS explains here](http://docs.aws.amazon.com/AmazonElastiCache/latest/UserGuide/SelectEngine.html) how to determine which one is more adapted to your usage.

Amazon ElastiCacheには、キャッシュエンジンとして[Redis](https://www.datadoghq.com/blog/how-to-monitor-redis-performance-metrics/)か [Memcached](https://www.datadoghq.com/blog/speed-up-web-applications-memcached/)が選べるようになっています。数千ものElasticCahcheを使っているDatadogのお客様の間では、MemcachedよりRedisが多く採用されています。しかしながら、どちらのエンジンの技術も、ニーズに応じて、ユニークな利点を持っています。AWSでは、使い方によってどちらのエンジンが適しているかを判断する方法をこの[リンク先](http://docs.aws.amazon.com/AmazonElastiCache/latest/UserGuide/SelectEngine.html)で説明しています。


## Key metrics

> An efficient cache can significantly increase your application’s performance and user navigation speed. That’s why key performance metrics need to be well understood and continuously monitored, using both generic ElastiCache metrics collected from AWS CloudWatch but also native metrics from your chosen caching engine. The metrics you should monitor fall into four general categories:

> -   [Client metrics](#client-metrics)
> -   [Cache performance](#cache-metrics)
> -   [Memory metrics](#memory-metrics)
> -   [Other host-level metrics](#host-metrics)

効率的なキャッシュは、アプリケーションのパフォーマンスやユーザのナビゲーション速度を、大幅に向上させることができます。
このような理由から、主要なパフォーマンメトリクスを十分理解し、AWS CloudWatchから収集したElastiCacheメトリクスと、キャッシュエンジンから集取したネイティブメトリクスを使って、継続的に監視する必要があります。監視が必要なメトリクスは、次のカテゴリーの分類できます:

-   [クライアントメトリクス](#client-metrics)
-   [キャッシュパフォーマンス](#cache-metrics)
-   [メモリメトリクス](#memory-metrics)
-   [その他ホストレベルのメトリクス](#host-metrics)


### CloudWatch vs native cache metrics

> Metrics can be collected from ElastiCache through CloudWatch or directly from your cache engine (Redis or Memcached). Many of them can be collected from both sources: from CloudWatch and also from the cache. However, unlike CloudWatch metrics, native cache metrics are usually collected in real-time at higher resolution. For these reasons you should prefer monitoring native metrics, when they are available from your cache engine.

メトリクスは、ElastiCacheからCloudWatchを経由し集取するモノと、RedidsとMemcachedのキャッシュエンジンから直接集取するモノがあります。メトリクスに含まれる項目の多くは、CloudWatchとキャッシュの両方のソースから収集することができます。しかし、キャッシュエンジンから直接収集するネイティブメトリックは、CloudWatchから集取するメトリクスとは異なり、一般的に高い分解能でリアルタイムに収集することができます。これらの理由から、同一項目のメトリクスがキャッシュエンジンから集取可能な場合は、それらのネイティブメトリクスを監視することを推奨しています。


[![](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-elasticache/elasticache-vs-redis-or-memcached-metrics.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-elasticache/elasticache-vs-redis-or-memcached-metrics.png)

> For each metric discussed in this publication, we provide its name as exposed by Redis and Memcached, as well as the name of the equivalent metric available through AWS CloudWatch, where applicable.

この記事の中のメトリクス名は、RedisとMemcachedによって公開されているそのままの名前形式を作用しています。そして、それらのメトリクスがAWS CloudWatchからも提供されている場合は、同等のモノの名前も記載しています。


> If you are using Redis, we also published a [series of posts](https://www.datadoghq.com/blog/how-to-monitor-redis-performance-metrics/) focused exclusively on how to monitor Redis native performance metrics.

ElasticacheにRedisが使われている場合は、Redisから集取したネーティブメトリクスの監視に特化した記事の[シリーズ](https://www.datadoghq.com/blog/how-to-monitor-redis-performance-metrics/) も準備しています。


> This article references metric terminology introduced in [our Monitoring 101 series](https://www.datadoghq.com/blog/monitoring-101-collecting-data/), which provides a framework for metric collection and alerting.

この記事では、[Monitoring 101 series](https://www.datadoghq.com/blog/monitoring-101-collecting-data/)で紹介した”メトリクスの収集とアラートのフレームワーク”で解説した用語を採用しています。


### Client metrics

Client metrics measure the volume of client connections and requests.

クライアントのメトリックは、クライアント接続とリクエストの量を測定しています。

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

> **Number of commands** processed is a throughput measurement that will help you identify latency issues, especially with Redis, since it is single threaded and processes command requests sequentially. Unlike Memcached, native Redis metrics don’t distinguish between Set or Get commands. ElastiCache provides both for each technology.

**Number of commands**は、処理されたコマンドの数です。この値は、キャッシュのスループットの測定値で、レイテンシ問題を特定する際に役に立ちます。特にRedisの場合、シングルスレッドで、コマンドリクエストを順番に処理するして行くため、役に立ちます。更に、Memcachedのように、Redisのネイティブメトリクスは、SetとGetの区別がありません。最後に、CloudWatch経由で集取したElastiCacheメトリクスでは、それぞれの技術に対して、両方のメトリクスを集取することができます。


[![](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-elasticache/get-and-set-commands-elasticache.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-elasticache/get-and-set-commands-elasticache.png)

#### Metric to alert on:

> **Current connections**: While sudden changes might indicate application issues requiring investigation, you should track this metric primarily to make sure it never reaches the connections limit. If that happens new connections will be refused, so you should make sure your team is notified and can scale up way before that happens. If you are using Memcached, make sure the parameter **maxconns\_fast** has its default value 0 so that new connections are queued instead of being closed, as they are if **maxconns\_fast** is set to 1. AWS fixes the limit at 65,000 simultaneous connections for Redis ([**maxclients**](http://docs.aws.amazon.com/AmazonElastiCache/latest/UserGuide/ParameterGroups.Redis.html)**)** and Memcached ([**max\_simultaneous\_connections**](http://docs.aws.amazon.com/AmazonElastiCache/latest/UserGuide/ParameterGroups.Memcached.html)).

**Current connections**: このメトリクスに急激な変化が発生した場合、調査が必要なレベルのアプリの障害が発生している可能性があります。更に、コネクションが制限値に達しないようにするためにも、このメトリクスルを継続的に把握しておく必要があります。もしも、キャッシュへのコネクションが制限値に達すると、新しく発生したコネクションは、接続を拒否されます。従って、この状態が発生する前に、チームに通知し、スケールアップの対策がされている状態にしておく必要があります。Memcachedを使っているなら、最大接続制限に達したときに新しく発生したコネクションリクエストが、キューに溜まるように、**maxconns\_fast**が、`0`になっていることを今一度確認してください。尚、AWSは、Redis ([**maxclients**](http://docs.aws.amazon.com/AmazonElastiCache/latest/UserGuide/ParameterGroups.Redis.html)パラメーター) と、Memcached ([**max\_simultaneous\_connections**](http://docs.aws.amazon.com/AmazonElastiCache/latest/UserGuide/ParameterGroups.Memcached.html)パラメーター)で、同時接続数を65,000に制限してます。


> NOTE: ElastiCache also provides the **NewConnections** metric measuring the number of new connections accepted by the server during the selected period of time.

注：ElastiCacheは、選択された期間中にサーバーによって受け入れられた新しいコネクション数を測定する、**NewConnections**というメトリックも提供します。


### Cache performance

> By tracking performance metrics you will be able to know at a glance if your cache is working properly.

パフォーマンスメトリックを監視し続けることにより、キャッシュが正しく動作しているかを一目で把握できるようになります。


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

> Tracking **replication lag**, available only with Redis, helps to prevent serving stale data. Indeed, by automatically synchronizing data into a secondary cluster, replication ensures high availability, read scalability, and prevents data loss. Replicas contain the same data as the primary node so they can also serve read requests. The replication lag measures the time needed to apply changes from the primary cache node to the replicas. You can also look at the native Redis metric **master\_last\_io\_seconds\_ago** which measures the time (in seconds) since the last interaction between slave and master.

**replication lag**(Redisのみで提供されている)を監視することは、古くなったデータを配信することを防ぐことに役に立ちます。実際には、セカンダリクラスタにデータを自動的に同期させることで、可用性と読み込み性能のスケーラビリティを確保し、データの損失をも防ぐことができます。レプリカは、それ自身も読み出しリクエストに対応できるように、プライマリーノードと同じデータを保管しています。**replication lag**は、プライマリーキャッシュのノードから、レプリカに変更を適用するために必要な時間を測定しています。更に、Redisでは、スレーブとマスター間の最後の交信時間からの経過時間(秒)を計測している**master\_last\_io\_seconds\_ago**というネイティブメトリクスを監視することもできます。


#### Metric to alert on:

> **Cache** **hits** and **misses** measure the number of successful and failed lookups. With these two metrics you can calculate the **hit rate**: hits / (hits+misses), which reflects your cache efficiency. If it is too low, the cache’s size might be too small for the working data set, meaning that the cache has to evict data too often (see **evictions** metric [below](#memory-metrics)). In that case you should add more nodes which will increase the total available memory in your cluster so more data can fit in the cache. A high hit rate helps to reduce your application response time, ensure a smooth user experience and protect your databases which might not be able to address a massive amount of requests if the hit rate is too low.

**Cache**、 **hits**と**misses**は、ルックアップの成功および失敗の回数を測定しています。これら2つのメトリクスを基に、キャッシュの効率を表す**hit rate** ( hits / (hits+misses) )を計算することができます。もしも、この値が低過ぎる場合は、作業データセットに対して、キャッシュのサイズが小さすぎて、データが頻繁にキャッシュ外に追い出されていることを意味しています([下記](#memory-metrics)の**evictions** メトリクスを参照してください)。そのような場合は、ノードを追加し、クラスター内の利用可能なメモリの総量を増やし、データがキャッシュ内に収まる様にする必要があります。**hit rate**の高い値は、アプリのレスポンスタイムを短縮し、スムーズなユーザーエクスペリエンスを確保します。それに加え、膨大な量のリクエストを処理できないかもしれないデータベースの保護に役立ちます。


> \* NOTE: Latency is not available like other classic metrics, but still attainable: you will find all details about measuring latency for Redis [in this post](https://www.datadoghq.com/blog/how-to-collect-redis-metrics/), part of our series on Redis monitoring. Latency is one of the best ways to directly observe Redis performance. Outliers in the latency distribution could cause serious bottlenecks, since Redis is single-threaded—a long response time for one request increases the latency for all subsequent requests. Common causes for high latency include high CPU usage and swapping. [This publication](http://redis.io/topics/latency) from Redis discusses troubleshooting high latency in detail.

\* 注: 他の古典的なメトリクスのケースと異なり、レイテンシは、公開されていません。しかし、依然として類似のデータを手に入れることは可能です。先に紹介した、Redisの監視に特化したシリーズの一部でのポストで[レイテンシの計測方法について](https://www.datadoghq.com/blog/how-to-collect-redis-metrics/)紹介しています。レイテンシは、Redisのパフォーマンスを直接的に観察する最良の方法のです。レイテンシ分布の中に発生する異常に長いレイテンシは、深刻なボトルネックを発生する可能性があります。なぜならば、Redisは、単一スレッドで動作しているため、ある一つのリクエストの長いレスポンス時間は、それ以降のリクエストのレイテンシを増加させるからです。レイテンシの高い値の原因は、高いCPUの利用率とスワップの発生に関連していることが多いです。Redisサイトに掲載されている次の[刊行物](http://redis.io/topics/latency) には、レイテンシ値が高い場合のトラブルシューティング方法が詳しく解説されています。

> Unfortunately, Memcached does not provide a direct measurement of latency, so you will need to rely on throughput measurement via the number of commands processed, [described below](#client-metrics).

残念ながら、Memcachedには、レイテンシを直接計測した値を集取する方法がありません。従って、[下記に説明した](#client-metrics)、複数のコマンドの実行結果からのスループットの計測する必要があります。


### Memory metrics

> Memory is the essential resource for any cache, and neglecting to monitor ElastiCache’s memory metrics can have critical impact on your applications.

メモリは、キャッシュエンジンにとって非常に重要なリソースになります。ElastiCacheのメモリメトリクスを監視しないことは、アプリケーションに重大な影響を与える可能性があります。


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

> - **Memory usage** is critical for your cache performance. If it exceeds the total available system memory, the OS will start swapping old or unused sections of memory (see next paragraph). Writing or reading from disk is up to 100,000x slower than writing or reading from memory, severely degrading the performance of the cache.

- **Memory usage**は、キャッシュのパフォーマンスを把握するために重要なメトリクス。利用可能なシステムメモリの総量を超えると、OSは、使われていないか古いメモリのセクション(次の段落を参照)を、メモリからスワップ(退避)し始めます。ディスクへの書き込みやディスクからの読み込みには、メモリに対するそれらの操作の100,000倍程の時間が掛かります。そして、深刻なキャッシュの性能低下になります。


> - **Evictions** happen when the cache memory usage limit (**maxmemory** for Redis) is reached and the cache engine has to remove items to make space for new writes. Unlike the host memory, which leads to swap usage when exceeded, the cache memory limit is defined by your node type and number of nodes. The evictions follow the method defined in your cache configuration, such as [LRU for Redis](http://redis.io/topics/lru-cache). Evicting a large number of keys can decrease your hit rate, leading to longer latency times. If your eviction rate is steady and your cache hit rate isn’t abnormal, then your cache has probably enough memory. If the number of evictions is growing, you should increase your cache size by migrating to a larger node type (or adding more nodes if you use Memcached).

- **Evictions**は、キャッシュメモリの使用上限(Redisの場合、**maxmemory**)に達した際に、キャッシュエンジンが、新しい書き込みのためにスペースを確保しようとする際に発生します。ホストのメモリ総量を超えた場合のスワップと異なり、キャッシュメモリの制限は、ノードタイプとノード数によって決まります。エビクション(evictions)は、[”LRU for Redis”](http://redis.io/topics/lru-cache)の様な、キャッシュの設定で定義された方法によって実行されます。大量のキーのエビクトは、キャッシュのヒット率(hit rate)を低下させる可能性があり、長いレイテンシを発生させる可能性があります。エビクション率(eviction rate)が安定し、キャッシュのヒット率が異常値を示していない場合は、おそらくキャッシュには十分なメモリが割り当てられている状態です。もしも、エビクション数が増加している場合は、より大きなノードタイプへ移行しキャッシュサイズを増やす必要があります。(Memcachedを使用する場合は、ノートを追加することもできます)


> - **FreeableMemory**, tracking the host’s remaining memory, shouldn’t be too low, otherwise it will lead to Swap usage (see next paragraph).

- **FreeableMemory**は、ホスト上のメモリ残量を追跡しています。この値は、低すぎる値にならないよう保つ必要があります。この値が低くなるとOSがスワップを使い始めます。（次の段落を参照）


> - **SwapUsage** is a host-level metric that increases when the system runs out of memory and the operating system starts using disk to hold data that should be in memory. Swapping allows the process to continue to run, but severely degrades the performance of your cache and any applications relying on its data. According to AWS, [swap shouldn’t exceed 50MB with Memcached](http://docs.aws.amazon.com/AmazonElastiCache/latest/UserGuide/CacheMetrics.WhichShouldIMonitor.html). AWS makes no similar recommendation for Redis.

- **SwapUsage**は、システムがメモリ不足し、OSがメモリにあるべきデータを保持するためにディスクを使用し始めた時に増加するホストレベルのメトリクスです。スワップを発生させることによって、プロセスの実行を継続することができますが、キャッシュとメモリ上のデータに依存しているアプリのパフォーマンスを著しく低下させます。AWSによると、[Memcachedを使っている場合、スワップは50MBを越えないようにする必要があります](http://docs.aws.amazon.com/AmazonElastiCache/latest/UserGuide/CacheMetrics.WhichShouldIMonitor.html)。（尚、Redisに関しては、同様のアドバイスは公開されていません。）


> - The **memory fragmentation ratio** metric (available only with Redis) measures the ratio of memory used as seen by the operation system (**used\_memory\_rss**) to memory allocated by Redis (**used\_memory**). The operating system is responsible for allocating physical memory to each process. Its virtual memory manager handles the actual mapping, mediated by a memory allocator. For example, if your Redis instance has a memory footprint of 1GB, the memory allocator will first attempt to find a contiguous memory segment to store the data. If it can’t find one, the allocator divides the process’s data across segments, leading to increased memory overhead. A fragmentation ratio above 1.5 indicates significant memory fragmentation since Redis consumes 150 percent of the physical memory it requested. If the fragmentation ratio rises above 1.5, your memory allocation is inefficient and you should restart the instance. A fragmentation ratio below 1 means that Redis allocated more memory than the available physical memory and the operating system is swapping (see above).

- **memory fragmentation ratio**（Redisにのみ公開されているメトリクス）は、OSによって使われている物理メモリの量(**used\_memory\_rss**)と、Redisに使用されているメモリの量(**used\_memory**)の比率を測定しています。OSは、各プロセスに物理メモリを割り当てる役目を担っています。そしてOSの仮想メモリマネージャは、メモリアロケーターを使って、実際のマッピングの処理をしていきます。例えば、Redisのインスタンスが1ギガバイトのメモリフットプリントを有する場合、メモリアロケーターは、まず最初に、連続してデータを格納することのできるメモリセグメントを検索しようとします。もしも、そのようなセグメントを見つけることができない場合、アロケーターは、プロセスデータを各セグメントに分散して収納します。このプロセスデータの分散が、メモリのオーバーヘッドに繋がります。Redisの場合、要求した物理メモリの150%のメモリを消費するので、1.5以上の断片化率(fragmentation ratio)は、深刻なメモリの分断化を意味しています。従って、断片化率が1.5以上に上昇すると、メモリ割り当てが非効率的になり、インスタンスの再起動が必要になります。又、1.0以下の断片化率は、使用可能な物理メモリより多くのメモリがRedisに割り当てられ、OSがスワップをしていることを意味します。


### Other host-level metrics

> Host-level metrics for ElastiCache are only available through CloudWatch.

ElastiCacheのホストレベルのメトリックは、CloudWatchを介してのみ利用することができます。


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

> **CPU Utilization** at high levels can indirectly indicate high latency. You should interpret this metric differently depending on your cache engine technology.

**CPU Utilization**(CPU利用率)が高止まりしている場合は、間接的にレイテンシの値が高くなっていることがあります。このメトリクスは、キャッシュエンジンの技術に応じて、異なった解釈をする必要があります。


> All [AWS cache nodes](https://aws.amazon.com/elasticache/pricing/) with more than 2.78GB of memory or good network performance are multicore. Be aware that if you are using Redis, the extra cores will be idle since Redis is single-threaded. The actual CPU utilization will be equal to this metric’s reported value multiplied by the number of cores. For example a four-core Redis instance reporting 20 percent CPU utilization actually has 80 percent utilization on one core. Therefore you should define an alert threshold based on the number of processor cores in the cache node. AWS recommends that you set the alert threshold at 90 percent divided by the number of cores. If this threshold is exceeded due to heavy read workload, add more read replicas to scale up your cache cluster. If it’s mainly due to write requests, increase the size of your Redis cache instance.

[AWSキャッシュノード](https://aws.amazon.com/elasticache/pricing/)で、優れたネットワークパフォーマンスを持っているか、2.78ギガバイトを超えるメモリを持っている全てのノードは、マルチコアのインスタンスです。Redisを使用している場合、プロセスはシングルスレッドで動作するため、使われていないコアはアイドル状態になっていることに注意してください。従って、実際のCPU使用率は、メトリクスの集取している値にコアの数を乗じた値になります。例えば、20%のCPU使用率を報告している4コアRedisのインスタンスは、実際には1つのコアの上で80％のCPU使用率で動作しています。従って、アラートは、キャッシュノード内のプロセッサコア数に基づいて閾値を定義する必要があります。AWSでは、90%をコア数で割った値を閾値に設定することを推奨しています。読み込み中心のワークロードにより、この閾値を超える場合は、読み込み用のレプリカを追加し、キャッシュクラスターをスケールアップします。もしも、書き込みリクエストで閾値を超えるようなら、Redisのキャッシュインスタンスを更に大きなサイズに変更します。


> Memcached is multi-threaded so the CPU utilization threshold can be set at 90%. If you exceed that limit, scale up to a larger cache node type or add more cache nodes.

memcachedはマルチスレッドなので、CPU使用率の閾値を90％に設定することができます。もしも、その上限を超えるようなら、り大きなキャッシュノードタイプにスケールアップするか、キャッシュノードを追加し対応します。


## Correlate to see the full picture

> Most of these key metrics are directly linked together. For example, high memory usage can lead to swapping, increasing latency. That’s why you need to correlate these metrics in order to properly monitor ElastiCache.

これらのキーメトリクスのほとんどは、ダイレクトに関連してます。例えば、高いメモリ使用量は、スワッピングに繋がり、レイテンシを増加の原因になります。従って、ElastiCacheを間違いなく監視するためには、これらのメトリクスを相関させて状況を把握することが必要になってきます。


> Correlating metrics with events sent by ElastiCache, such as node addition failure or cluster creation, will also help you to investigate and to keep an eye on your cache cluster’s activity.

ノードの追加の失敗やクラスタの作成などの、ElastiCacheから送られてくるイベントを、メトリクスと相関しておくことは、キャッシュクラスタの活動を監視し、必要に応じて調査する場合に役に立ちます。


[![](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-elasticache/elasticache-dashboard.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-elasticache/elasticache-dashboard.png)

## Conclusion

> In this post we have explored the most important ElastiCache performance metrics. If you are just getting started with Amazon ElastiCache, monitoring the metrics listed below will give you great insight into your cache’s health and performance:

> -   [Number of current connections](#client-metrics)
> -   [Hit rate](#cache-metrics)
> -   [Memory metrics (especially evictions and swap usage)](#memory-metrics)
> -   [CPU Utilization](#host-metrics)

このポストでは、ElastiCacheの最も重要なパフォーマンスメトリックを見てきました。もしも、あなたがAmazon ElastiCacheの使用を開始したばかりなら、以下にリスト化したメトリクスを監視することは、キャッシュクラスターの健全性とパフォーマンスに関して優れた洞察力を提供してくれるでしょう。

-   [Number of current connections (現在のコネクション数)](#client-metrics)
-   [Hit rate (キャッシュヒット率)　](#cache-metrics)
-   [メモリメトリクス (特に、evictionsと、swap usage)](#memory-metrics)
-   [CPU Utilization (CPU利用率)](#host-metrics)


> [Part 2 of this series](https://www.datadoghq.com/blog/collecting-elasticache-metrics-its-redis-memcached-metrics) provides instructions for collecting all the metrics you need to monitor ElastiCache.

このシリーズの[Part 2](https://www.datadoghq.com/blog/collecting-elasticache-metrics-its-redis-memcached-metrics)では、ElastiCacheを監視すのに必要な全てのメトリックを収集する手順を解説していきます。
