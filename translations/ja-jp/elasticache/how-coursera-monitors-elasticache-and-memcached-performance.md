# [翻訳作業中]

> *This post is part 3 of a 3-part series on monitoring Amazon ElastiCache.* [*Part 1*](https://www.datadoghq.com/blog/monitoring-elasticache-performance-metrics-with-redis-or-memcached) *explores the key ElastiCache performance metrics, and* [*Part 2*](https://www.datadoghq.com/blog/collecting-elasticache-metrics-its-redis-memcached-metrics) *explains how to collect those metrics.*

*この投稿は、監視はAmazon ElastiCacheに3回シリーズの第3部です。第1部では、キーElastiCache・パフォーマンス・メトリックを探り、そして第2部では、これらのメトリックを収集する方法について説明します。*


> [Coursera](https://www.coursera.org/) launched its online course platform in 2013, and quickly became a leader in online education. With more than 1,000 courses and millions of students, Coursera uses [ElastiCache](https://aws.amazon.com/elasticache/) to cache course metadata, as well as membership data for courses and users, helping to ensure a smooth user experience for their growing audience. In this article we take you behind the scenes with Coursera’s engineering team to learn their best practices and tips for using ElastiCache, keeping it performant, and monitoring it with Datadog.

コーセラは、2013年に同社のオンラインコースのプラットフォームを立ち上げ、かつ迅速にオンライン教育のリーダーとなりました。 1,000以上のコースや学生の何百万人で、コーセラは彼らの成長の聴衆のためのスムーズなユーザーエクスペリエンスを確保するために支援し、コースやユーザーのためのコースのメタデータだけでなく、会員のデータをキャッシュするElastiCacheを使用しています。この記事では、それがパフォーマンスの維持、ElastiCacheを使用して、そしてDatadogでそれを監視するために彼らのベストプラクティスやヒントを学ぶためにコーセラのエンジニアリングチームとの舞台裏あなたを取ります。


## Why monitoring ElastiCache is crucial

> ElastiCache is a critical piece of Coursera’s cloud infrastructure. Coursera uses ElastiCache as a read-through cache on top of [Cassandra](https://www.datadoghq.com/blog/how-to-monitor-cassandra-performance-metrics/). They decided to use [Memcached](https://www.datadoghq.com/blog/speed-up-web-applications-memcached/) as the backing cache engine because they only needed a simple key-value cache, because they found it easier than [Redis](https://www.datadoghq.com/blog/how-to-monitor-redis-performance-metrics/) to manage with its simpler model, and because it is multi-threaded.

> Among other uses, they cache most of the elements on a course page, such as title, introduction video, course description, and other information about the course.

> If ElastiCache is not properly monitored, the cache could run out of memory, leading to evicted items. This in turn could impact the hit rate, which would increase the latency of the application. That’s why Coursera’s engineers continuously monitor ElastiCache. They use [Datadog](https://www.datadoghq.com/) so they can correlate all the relevant ElastiCache performance metrics with metrics from other parts of their infrastructure, all in one place. They can spot at a glance if their cache is the root cause of any application performance issue, and set up advanced alerts on crucial metrics.

ElastiCacheはコーセラのクラウドインフラストラクチャの重要な部分です。コー​​セラはカサンドラの上に、リードスルーキャッシ​​ュとしてElastiCacheを使用しています。彼らは、単純なキーと値のキャッシュを必要とするので、彼らはその単純なモデルで管理するのRedisよりも、それが簡単に見つけたので、バッキングキャッシュエンジンとしてのMemcachedを使用することを決定し、それがあるため、マルチスレッド。

他の用途の中で、彼らは、タイトル、紹介ビデオ、コースの説明、そしてもちろんに関するその他の情報として、コースページの要素のほとんどをキャッシュします。

ElastiCacheが適切に監視されていない場合は、キャッシュが追い出された項目につながる、メモリが不足する可能性があります。これにより、アプリケーションの待ち時間を増加させるヒット率を、影響を与える可能性があります。コー​​セラのエンジニアが継続的にElastiCacheを監視する理由です。彼らはすべて一箇所に、インフラの他の部分からのメトリックに関連するすべてのElastiCache・パフォーマンス・メトリックを相関させることができるので、彼らはDatadogを使用しています。彼らは、キャッシュは、任意のアプリケーションのパフォーマンスの問題の根本的な原因である場合一目で発見し、非常に重要な指標に高度なアラートを設定することができます。


[![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/screenboard.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/screenboard.png)

## Key metrics for Coursera

### CPU Utilization

> Since, unlike Redis, Memcached’s CPU can go up to 90 percent without impacting the performance, it is not a metric that Coursera alerts on. Nonetheless, they track it to facilitate investigation of problems.

Redisのとは異なり、MemcachedののCPUがパフォーマンスに影響を与えることなく、90パーセントに上がることができ、ので、それはコーセラが上の警告メトリックではありません。それにもかかわらず、彼らは問題の調査を容易にするために、それを追跡します。

### Memory

> Memory metrics, on the other hand, are critical and are closely monitored. By making sure the memory allocated to the cache is always higher than the **memory usage**, Coursera’s engineering team avoids **evictions**. Indeed they want to keep a very high **hit rate** in order to ensure optimal performance, but also to protect their databases. Coursera’s traffic is so high that their backend wouldn’t be able to address the massive amount of requests it would get if the cache hit rate were to decrease significantly.

メモリメトリックは、一方で、重要であり、厳密に監視されます。キャッシュに割り当てられたメモリは常にメモリ使用量よりも高くなっていることを確認することにより、コーセラのエンジニアリングチームは、立ち退きを避けることができます。実際、彼らは順番最適なパフォーマンスを確保するだけでなく、自分のデータベースを保護するために非常に高いヒット率を維持したいです。コーセラのトラフィックは、そのバックエンドは、キャッシュヒット率が著しく低下した場合、それはなるだろう要求の膨大な量に対処することができないほど高いです。


> They tolerate some swap usage for one of their cache clusters but it remains far below the 50-megabyte limit AWS recommends when using Memcached (see [part 1](https://www.datadoghq.com/blog/monitoring-elasticache-performance-metrics-with-redis-or-memcached)).

（パート1を参照）彼らは、キャッシュ・クラスタのいずれかのいくつかのスワップの使用量を許容するが、それは遠くのMemcachedを使用するときにAWSを推奨50 MBの限界を下回ったままです。

[![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/memory.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/memory.png)

### Get and Set

> Coursera uses a consistent hashing mechanism, which means that keys are distributed evenly across the nodes of a cluster. Thus monitoring Get and Set commands, broken down by node, allows them to check if nodes are all healthy, and if the traffic is well balanced among nodes. If a node has significantly more gets than its peers, this may indicate that it is hosting one or more hot keys (items requested with extreme frequency as compared to the others). A very hot key can max out the capacity of a node, and adding more nodes may not help, since the hot key will still be hosted on a single node. Nodes with higher throughput performance may be required.

コーセラは、キーがクラスタのノード間で均等に分散されていることを意味し、一貫したハッシュメカニズムを、使用しています。このように取得および設定は、ノードごとに分け、コマンド監視、ノードがすべて正常であるかどうかを確認するためにそれらを可能にし、トラフィックがノード間でバランスのとれている場合。ノードがかなり多くのピアより取得した場合、これは（他のものと比較して、極端な頻度で要求されたアイテム）を、それが一つ以上のホットキーをホストしていることを示すことができます。ホットキーは、まだ単一ノード上でホストされるため、ノードの容量、追加以上のノードアウト非常にホットキー缶maxは、助けないかもしれません。より高いスループット性能を有するノードが必要とされ得ます。


### Network

> Coursera also tracks network throughput because ElastiCache is so fast that it can easily saturate the network. A bottleneck would prevent more bytes from being sent despite available CPU and memory. That’s why Coursera needs to visualize these network metrics broken down by host and by cluster separately to be able to quickly investigate and act before saturation occurs.

ElastiCacheは、それが簡単にネットワークを飽和することができるように高速であるため、コーセラは、ネットワークのスループットを追跡します。ボトルネックは、利用可能なCPUとメモリにもかかわらず、送信されてからより多くのバイトを防止するであろう。コーセラはすぐに調査し、飽和が発生する前に行動することができるようにホストによって、別途、クラスタごとに分け、これらのネットワークのメトリックを視覚化する必要がある理由です。


### Events

> Lastly, seeing ElastiCache events along with cache performance metrics allows them to keep track of cache activities—such as cluster created, node added, or node restarted—and their impact on performance.

最後に、キャッシュ・パフォーマンス・メトリックと共にElastiCacheのイベントを見ること、それらがキャッシュ活動 - など作成したクラスタ、追加したノード、またはノードの再起動、およびパフォーマンスへの影響などを追跡することができます。


![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/events.png)

## Alerting via the right channel

### Critical alerts

> Some metrics are critical, and Coursera’s engineers want to make sure they never exceed a certain threshold. Datadog alerts allow them to send notifications via their usual communication channels (PagerDuty, chat apps, emails…) so they can target specific teams or people, and quickly act before a metric goes out of bounds.

> Coursera’s engineers have set up alerts on eviction rate, available memory, hit rate, and swap usage.

> Datadog alerts can also be configured to trigger on host health, whether services or processes are up or down, events, [outliers](https://www.datadoghq.com/blog/introducing-outlier-detection-in-datadog/), and more.

いくつかの指標が重要であり、かつコーセラのエンジニアは、彼らが一定のしきい値を超えないことを確認したいです。 Datadogアラートが（...、PagerDutyアプリ、電子メール、チャット）、彼らの通常の通信チャネルを介して通知を送信することを可能にするので、特定のチームや人を対象とし、メトリックが範囲外になる前に、迅速に行動することができます。

コーセラのエンジニアは立ち退き率、使用可能なメモリ、ヒット率、およびスワップの使用状況に関するアラートを設定しています。

サービスまたはプロセスが上下、イベント、外れ値、さらにあるかどうかDatadogアラートはまた、宿主の健康にトリガするように構成することができます。


[![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/monitor-type.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/monitor-type.png)

> For example, as explained in [part 1](https://www.datadoghq.com/blog/monitoring-elasticache-performance-metrics-with-redis-or-memcached) of this series, where we detail the key ElastiCache metrics and which ones to alert on, CPU usage shouldn’t exceed 90 percent with Memcached. Here is how an alert can be triggered any time any individual node sees its CPU utilization approaching this threshold:

たとえば、として私たち詳細キーElastiCache指標とものは、上の警告するCPU使用率はMemcachedの90％を超えてはなりません、このシリーズのパート1で説明しました。ここでは、アラートは、個々のノードがこのしきい値に近づいてCPU使用率を見て、任意の時間をトリガすることができる方法です。


[![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/define-metric.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/define-metric.png)

### The right communication channel

> Coursera uses [PagerDuty](https://www.datadoghq.com/blog/pagerduty/) for critical issues, and [Slack](https://www.datadoghq.com/blog/collaborate-share-track-performance-slack-datadog/) or email for low-priority problems. When configuring an alert, you can define a custom message (including suggested fixes or links to internal documentation), the people or team that will be notified, and the specific channel by which the alert will be sent. For example, you can send the notification to the people on-call via PagerDuty and to a specific Slack channel:

コーセラは重要な問題、および優先度の低い問題のスラックや電子メールのためPagerDutyを使用しています。アラートを設定する場合、あなたは、通知されます人々またはチーム、およびアラートが送信されることにより、特定のチャネル（修正案または内部ドキュメントへのリンクを含む）カスタムメッセージを定義することができます。たとえば、PagerDutyを経由して、特定のスラックチャネルにオンコール人への通知を送信することができます。


[![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/alert-msg.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/alert-msg.png)

## Why Datadog?

> Using Datadog allows Coursera to track all the metrics they need from the different parts of their infrastructure, in one place, with any relevant type of visualization. Thus they can spot at a glance any potential issue related to their cache and quickly find the root cause.

> By creating [timeboards](http://help.datadoghq.com/hc/en-us/articles/204580349-What-is-the-difference-between-a-ScreenBoard-and-a-TimeBoard-) they can overlay events from a specific service like ElastiCache and correlate them with performance metrics from other parts of their infrastructure.

> Datadog also makes it easy to collect and monitor native cache metrics from Redis or Memcached, in addition to generic ElastiCache metrics from Amazon, for even deeper insight into cache performance.

> If you’re using ElastiCache and Datadog already, we hope that these tips help you gain improved visibility into what’s happening in your cache. If you don’t yet have a Datadog account, you can start tracking your cache’s health and performance today with a [free trial](https://app.datadoghq.com/signup).

使用Datadogはコーセラが視覚化の任意の関連タイプで、一つの場所に彼らは、インフラストラクチャのさまざまな部分から必要なすべてのメトリックを、追跡することができます。したがって、彼らは一目で自分のキャッシュに関連する潜在的な問題を発見することができ、迅速に根本的な原因を見つけます。

timeboardsを作成することにより、彼らはElastiCacheのような特定のサービスからイベントをオーバーレイすることができ、それらのインフラストラクチャの他の部分からのパフォーマンスメトリックでそれらを関連付けます。

Datadogはまた、それが簡単に収集し、キャッシュのパフォーマンスへのより深い洞察力のために、アマゾンからの一般的なElastiCacheの指標に加えて、Redisのか、Memcachedの由来の天然キャッシュ・メトリックを監視することが可能になります。

あなたは既にElastiCacheとDatadogを使用している場合は、我々はこれらのヒントは、あなたのキャッシュに何が起こっているかに改善された可視性を得るのを助けることを願っています。あなたはまだDatadogアカウントをお持ちでない場合は、無料の試用版を使用してキャッシュの健康とパフォーマンス今日の追跡を開始することができます。


## Acknowledgments

> We want to thank the Coursera team, and especially [Daniel Chia](https://twitter.com/DanielChiaJH), who worked with us to share their monitoring techniques for Amazon ElastiCache.

私たちは、コーセラチームに感謝したい、とAmazon ElastiCacheのための彼らの監視技術を共有するために私たちと一緒に働いて、特にダニエル・チア、。