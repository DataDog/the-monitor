# [翻訳作業中]

> *This post is part 3 of a 3-part series on monitoring Amazon ElastiCache.* [*Part 1*](https://www.datadoghq.com/blog/monitoring-elasticache-performance-metrics-with-redis-or-memcached) *explores the key ElastiCache performance metrics, and* [*Part 2*](https://www.datadoghq.com/blog/collecting-elasticache-metrics-its-redis-memcached-metrics) *explains how to collect those metrics.*

*このポストは、Amazon ElastiCacheの監視について解説した3回シリーズのPart 3です。[Part 1](https://www.datadoghq.com/blog/monitoring-elasticache-performance-metrics-with-redis-or-memcached)では、ElastiCacheのキーメトリクスを解説しました。[Part 2](https://www.datadoghq.com/blog/collecting-elasticache-metrics-its-redis-memcached-metr)では、ElastiCacheからパフォーマンスメトリックを収集する方法を解説しました。*


> [Coursera](https://www.coursera.org/) launched its online course platform in 2013, and quickly became a leader in online education. With more than 1,000 courses and millions of students, Coursera uses [ElastiCache](https://aws.amazon.com/elasticache/) to cache course metadata, as well as membership data for courses and users, helping to ensure a smooth user experience for their growing audience. In this article we take you behind the scenes with Coursera’s engineering team to learn their best practices and tips for using ElastiCache, keeping it performant, and monitoring it with Datadog.

[Coursera](https://www.coursera.org/)は、2013年にオンラインコースのプラットフォームを立ち上げました。その後、急速にオンライン教育のリーダーへと成長していきました。Courseraは、1,000以上のコースと数百万人の学生に配信するコースのメタデーターのキャッシュするだけではなく、ユーザーやコースの会員データーのキャッシュにも[ElastiCache](https://aws.amazon.com/elasticache/)を使用しています。Elasticacheは、日々増加する視聴者のスムーズなユーザー体験を保証してくれています。この記事では、Courseraのエンジニアリングチームの実際のケースを基に、Datadogを使ったElastiCacheのパフォーマンスの監視方法とElastiCacheの運用方法のベストプラクティスとティップスを解説していきます。


## Why monitoring ElastiCache is crucial

> ElastiCache is a critical piece of Coursera’s cloud infrastructure. Coursera uses ElastiCache as a read-through cache on top of [Cassandra](https://www.datadoghq.com/blog/how-to-monitor-cassandra-performance-metrics/). They decided to use [Memcached](https://www.datadoghq.com/blog/speed-up-web-applications-memcached/) as the backing cache engine because they only needed a simple key-value cache, because they found it easier than [Redis](https://www.datadoghq.com/blog/how-to-monitor-redis-performance-metrics/) to manage with its simpler model, and because it is multi-threaded.

ElastiCacheは、Courseraのクラウドインフラの重要な構成要素です。Courseraでは、[Cassandra](https://www.datadoghq.com/blog/how-to-monitor-cassandra-performance-metrics/)の上にElastiCacheを設置し、読み込み専用のキャッシュとして使っています。Courseraでは、次のような理由で、[Memcached](https://www.datadoghq.com/blog/speed-up-web-applications-memcached/)をバックエンドキャッシュに採用しています。まず、単純なキーと値のキャッシュが必要出会ったこと、Courseraのような単純なモデルでは[Redis](https://www.datadoghq.com/blog/how-to-monitor-redis-performance-metrics/)より簡単に管理ができること、最後に、マルチスレッドであることです。


> Among other uses, they cache most of the elements on a course page, such as title, introduction video, course description, and other information about the course.

多くの用途の中でも、コースページ上の要素である、タイトル、紹介ビデオ、コース説明などほとんどの情報をキャッシュしています。


> If ElastiCache is not properly monitored, the cache could run out of memory, leading to evicted items. This in turn could impact the hit rate, which would increase the latency of the application. That’s why Coursera’s engineers continuously monitor ElastiCache. They use [Datadog](https://www.datadoghq.com/) so they can correlate all the relevant ElastiCache performance metrics with metrics from other parts of their infrastructure, all in one place. They can spot at a glance if their cache is the root cause of any application performance issue, and set up advanced alerts on crucial metrics.

もしも、Elasticacheが適切に監視されていないと、キャッシュシステムのメモリーが不足し、コンテンツアイテムのエビクト(追い出し)が発生する可能性が出てきます。このことにより、キャッシュのヒット率(hit rate)に影響を与える可能性があることになります。Courseraでは、ElastiCacheのパフォーマンスメトリクスと、インフラの他の構成要素から収集したメトリクスを、同じ場所に表示し、相関させて状況を把握するためにDatadogを使っています。Courseraのエンジニアは、アプリのパフォーマンス問題がキャッシュに起因しているかを、一目で判断することができます。そして、決定的に重要なメトリクスには、高度な判定基準をもったアラートも設定しています。


[![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/screenboard.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/screenboard.png)

## Key metrics for Coursera

### CPU Utilization

> Since, unlike Redis, Memcached’s CPU can go up to 90 percent without impacting the performance, it is not a metric that Coursera alerts on. Nonetheless, they track it to facilitate investigation of problems.

Redisとは異なり、Memcachedは、CPU利用率が90%になってもパフォーマンスに影響を与えることは有りません。そして、Courseraは、このメトリクスについては、アラートを設定していません。それでもやはり、障害発生時の調査を補助するためにこのメトリクスを監視はしています。


### Memory

> Memory metrics, on the other hand, are critical and are closely monitored. By making sure the memory allocated to the cache is always higher than the **memory usage**, Coursera’s engineering team avoids **evictions**. Indeed they want to keep a very high **hit rate** in order to ensure optimal performance, but also to protect their databases. Coursera’s traffic is so high that their backend wouldn’t be able to address the massive amount of requests it would get if the cache hit rate were to decrease significantly.

CPU使用率のケースとは反対に、メモリーに関するメトリクスは、重要視しており、厳密に監視しています。Courseraのエンジニアチームは、**evictions**(エビクション)が派生しないように、キャッシュに割り当てられたメモリーの値が、**memory usage**の値よりも常に上にあることを確保しています。確かに、最高の性能をだし続けるために**hit rate**(ヒット率)を維持したいのですが、それと当時にデータベースを保護するのも目的です。Courseraで発生しているトラフィックは著し多く、キャッシュの**hit rate**(ヒット率)が著しく低下した場合、そのバックエンドの発生するであろう膨大な量のリクエストに対処できなくなるでしょう。


> They tolerate some swap usage for one of their cache clusters but it remains far below the 50-megabyte limit AWS recommends when using Memcached (see [part 1](https://www.datadoghq.com/blog/monitoring-elasticache-performance-metrics-with-redis-or-memcached)).

Courseraのキャッシュクラスタでは、スワップも発生していますが、AWSが推奨しているMemcachd採用時の50MBの限界を大幅に下回っています。([Part 1](https://www.datadoghq.com/blog/monitoring-elasticache-performance-metrics-with-redis-or-memcached)参照)


[![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/memory.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/memory.png)

### Get and Set

> Coursera uses a consistent hashing mechanism, which means that keys are distributed evenly across the nodes of a cluster. Thus monitoring Get and Set commands, broken down by node, allows them to check if nodes are all healthy, and if the traffic is well balanced among nodes. If a node has significantly more gets than its peers, this may indicate that it is hosting one or more hot keys (items requested with extreme frequency as compared to the others). A very hot key can max out the capacity of a node, and adding more nodes may not help, since the hot key will still be hosted on a single node. Nodes with higher throughput performance may be required.

Courseraでは、コンシステントハッシュ法(consistent hashing mechanism)を使っています。この方法では、クラスター内のノードに、キーが均等に分散して配置されていることを意味します。従って、ノード毎に分けたGetとSetのコマンドの実行状況を監視することは、全てのノードが正常で、且つ、トラフィックがノード間で均等に処理されているかのチェックになります。もしも、他のノードに比べ一つノードが著しく多いGETを処理していたら、そのノードは、ホットキー(他と比べて、極端な頻度でリクエストを受けるキー)をホストしていることを意味します。

著しくリクエストされるホットキーは、そのノードが持つ容量を使い果たしてしまうこともあります。そして、そのホットキーは、1台のノードにしか保存されないため、クラスターへのノードの追加は、改善にはならないかもしれません。より高いスループット性能を持つノードへの変更が必要になります。


### Network

> Coursera also tracks network throughput because ElastiCache is so fast that it can easily saturate the network. A bottleneck would prevent more bytes from being sent despite available CPU and memory. That’s why Coursera needs to visualize these network metrics broken down by host and by cluster separately to be able to quickly investigate and act before saturation occurs.

Elasticacheは、ネットワークを簡単に飽和させるほど高速なため、Courseraではネットワークのスループットも監視しています。ネットワークのボトルネックの発生は、利用可能なCPUパワーとメモリーがあるにもかかわらず、データーが送信されることの妨害になります。従って、Courseraでは、素早い調査の目的とネットワークの飽和が発生する前に行動を起こす機械を作るために、ホスト単位とクラスター単位に分類した、ネットワークメトリクスを可視化をしました。


### Events

> Lastly, seeing ElastiCache events along with cache performance metrics allows them to keep track of cache activities—such as cluster created, node added, or node restarted—and their impact on performance.

最後に、キャッシュのパフォーマンスメトリクスと共に、ElastiCacheのイベントを見ることは、キャッシュで起きている各イベント(クラスターの作成、ノードの追加/再起動)と、そのイベントの与えるパフォーマンスへの影響などを把握することに役立ちました。


![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/events.png)

## Alerting via the right channel

### Critical alerts

> Some metrics are critical, and Coursera’s engineers want to make sure they never exceed a certain threshold. Datadog alerts allow them to send notifications via their usual communication channels (PagerDuty, chat apps, emails…) so they can target specific teams or people, and quickly act before a metric goes out of bounds.

いくつかのメトリクスは致命的です。Courseraのエンジニアは、これらのメトリクスについては、絶対に閾値を超えないようにしていました。
Datadogのアラートには、Courseraのエンジニアが日常使っている通信チャネル(PagerDuty、チャット、電子メールなど)に対して通知を送る機能があり、手に負えない状況になる前に迅速な対応処置ができるようになりました。


> Coursera’s engineers have set up alerts on eviction rate, available memory, hit rate, and swap usage.

Courseraのエンジニアは、エビクション率(eviction rate)、使用可能なメモリ量、ヒット率(hit rate)、およびスワップ使用量に、アラートを設定しています。


> Datadog alerts can also be configured to trigger on host health, whether services or processes are up or down, events, [outliers](https://www.datadoghq.com/blog/introducing-outlier-detection-in-datadog/), and more.

Datadogのアラートは、多岐に渡る項目につい手設定することができます。例えば、ホストの状態、サービス又はプロセスの動作状況、イベント、そして[outliers](https://www.datadoghq.com/blog/introducing-outlier-detection-in-datadog/)(グループから外れている値)などの項目に設定することができます。


[![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/monitor-type.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/monitor-type.png)

> For example, as explained in [part 1](https://www.datadoghq.com/blog/monitoring-elasticache-performance-metrics-with-redis-or-memcached) of this series, where we detail the key ElastiCache metrics and which ones to alert on, CPU usage shouldn’t exceed 90 percent with Memcached. Here is how an alert can be triggered any time any individual node sees its CPU utilization approaching this threshold:

例えば、このシリーズの[part 1](https://www.datadoghq.com/blog/monitoring-elasticache-performance-metrics-with-redis-or-memcached)の”Elasticacheのキーメトリクスとアラートの必要な項目"で説明したように、MemcachedのCPU使用率は、90%を越える内容に維持しておきべきです。以下は、個々のノードのCPU使用率が予め設定した閾値に近づいた場合に動作するアラートの設定例です:


[![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/define-metric.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/define-metric.png)

### The right communication channel

> Coursera uses [PagerDuty](https://www.datadoghq.com/blog/pagerduty/) for critical issues, and [Slack](https://www.datadoghq.com/blog/collaborate-share-track-performance-slack-datadog/) or email for low-priority problems. When configuring an alert, you can define a custom message (including suggested fixes or links to internal documentation), the people or team that will be notified, and the specific channel by which the alert will be sent. For example, you can send the notification to the people on-call via PagerDuty and to a specific Slack channel:

Courseraでは、致命的な問題には、[PagerDuty](https://www.datadoghq.com/blog/pagerduty/)を使用しています。そして、緊急性の低い問題には、[Slack](https://www.datadoghq.com/blog/collaborate-share-track-performance-slack-datadog/)や電子メールを使用しています。Datadogのアラートを設定する際には、通知を受ける人やチーム、アラートを送信するチャネルを指定して、カスタムメッセージ（障害への対応方法や内部のドキュメントへのリンクを含む）を定義することができます。例えば、オンコールで待機してるメンバーへPagerDutyを使って通知し、補足としてSlackの特定チャネルへアラートを送信する場合は、以下のようになります:


[![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/alert-msg.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/alert-msg.png)

## Why Datadog?

> Using Datadog allows Coursera to track all the metrics they need from the different parts of their infrastructure, in one place, with any relevant type of visualization. Thus they can spot at a glance any potential issue related to their cache and quickly find the root cause.




使用Datadogはコーセラが視覚化の任意の関連タイプで、一つの場所に彼らは、インフラストラクチャのさまざまな部分から必要なすべてのメトリックを、追跡することができます。したがって、彼らは一目で自分のキャッシュに関連する潜在的な問題を発見することができ、迅速に根本的な原因を見つけます。


> By creating [timeboards](http://help.datadoghq.com/hc/en-us/articles/204580349-What-is-the-difference-between-a-ScreenBoard-and-a-TimeBoard-) they can overlay events from a specific service like ElastiCache and correlate them with performance metrics from other parts of their infrastructure.

timeboardsを作成することにより、彼らはElastiCacheのような特定のサービスからイベントをオーバーレイすることができ、それらのインフラストラクチャの他の部分からのパフォーマンスメトリックでそれらを関連付けます。


> Datadog also makes it easy to collect and monitor native cache metrics from Redis or Memcached, in addition to generic ElastiCache metrics from Amazon, for even deeper insight into cache performance.

Datadogはまた、それが簡単に収集し、キャッシュのパフォーマンスへのより深い洞察力のために、アマゾンからの一般的なElastiCacheの指標に加えて、Redisのか、Memcachedの由来の天然キャッシュ・メトリックを監視することが可能になります。


> If you’re using ElastiCache and Datadog already, we hope that these tips help you gain improved visibility into what’s happening in your cache. If you don’t yet have a Datadog account, you can start tracking your cache’s health and performance today with a [free trial](https://app.datadoghq.com/signup).

あなたは既にElastiCacheとDatadogを使用している場合は、我々はこれらのヒントは、あなたのキャッシュに何が起こっているかに改善された可視性を得るのを助けることを願っています。あなたはまだDatadogアカウントをお持ちでない場合は、無料の試用版を使用してキャッシュの健康とパフォーマンス今日の追跡を開始することができます。


## Acknowledgments

> We want to thank the Coursera team, and especially [Daniel Chia](https://twitter.com/DanielChiaJH), who worked with us to share their monitoring techniques for Amazon ElastiCache.

Courseraが持っていたAmazon ElastiCacheの監視テクニックを我々と共有してくださったことを、Courseraのチームと特に[Daniel Chia](https://twitter.com/DanielChiaJH)氏に感謝します。