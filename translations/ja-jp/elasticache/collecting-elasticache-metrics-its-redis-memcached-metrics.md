# [翻訳作業中]

> *This post is part 2 of a 3-part series on monitoring Amazon ElastiCache. [Part 1](https://www.datadoghq.com/blog/monitoring-elasticache-performance-metrics-with-redis-or-memcached) explores its key performance metrics, and [Part 3](https://www.datadoghq.com/blog/how-coursera-monitors-elasticache-and-memcached-performance) describes how Coursera monitors ElastiCache.*

*この投稿は、監視はAmazon ElastiCacheに3回シリーズの第2部です。パート1は、その主要なパフォーマンス指標を探り、そして第3部は、コーセラがElastiCacheを監視する方法について説明します。*


> Many ElastiCache metrics can be collected from AWS via CloudWatch or directly from the cache engine, whether Redis or Memcached. When that’s the case, as discussed in [Part 1](https://www.datadoghq.com/using-elb-cloudwatch-metrics-to-detect-latency/), you should favor monitoring the native cache metric to ensure higher resolution and greater awareness and responsiveness. Therefore this article covers three different ways to access ElastiCache metrics from AWS CloudWatch, as well as the collection of native metrics from both caching engines:
> 
> -   CloudWatch metrics
>     -   [Using the AWS Management Console](#console)
>     -   [Using the command line interface (CLI)](#cli)
>     -   [Using a monitoring tool that accesses the CloudWatch API](#tool)
> -   Caching engine metrics
>     -   [Redis](#redis)
>     -   [Memcached](#memcached)

多くElastiCacheメトリックはRedisのまたはMemcachedのかを、キャッシュエンジンからCloudWatchのを介して、または直接AWSから採取することができます。それはケースだときはパート1で説明したように、あなたは、より高い解像度と大きな意識と応答性を確保するために、ネイティブのキャッシュ・メトリックを監視好むべきです。そこでこの記事では、3つの異なるAWS CloudWatchのからElastiCacheメトリックにアクセスする方法だけでなく、両方のキャッシュエンジンからのネイティブメトリックの収集について説明します。

- CloudWatchのメトリックス
	- AWS管理コンソールを使用しました
	- コマンドラインインタフェースを使用して、（CLI）
	- CloudWatchのAPIをアクセス監視ツールを使用して、
- キャッシュエンジンの指標
	- Redisの
	- memcachedの


## Using the AWS Management Console

> Using the online management console is the simplest way to monitor your cache with CloudWatch. It allows you to set up basic automated alerts and to get a visual picture of recent changes in individual metrics. Of course, you won’t be able to access native metrics from your cache engine, but their CloudWatch equivalent is sometimes available (see [Part 1](https://www.datadoghq.com/blog/monitoring-elasticache-performance-metrics-with-redis-or-memcached)[)](http://www.datadoghq.com/blog/monitoring-elasticache-performance-metrics-with-redis-or-memcached).

オンライン管理コンソールを使用すると、CloudWatchのを使用してキャッシュを監視する最も簡単な方法です。それはあなたが基本的な自動化されたアラートを設定すると、個々のメトリックの最近の変化を視覚的に把握することができます。もちろん、あなたがあなたのキャッシュエンジンからネイティブメトリクスにアクセスすることはできませんが、彼らのCloudWatchの同等物は、（パート1を参照）時に使用可能です。


### Graphs

> Once you are signed in to your AWS account, you can open the [CloudWatch console](https://console.aws.amazon.com/cloudwatch/home#metrics:) and then browse the metrics related to the different AWS services.

あなたのAWSアカウントにサインインしたら、CloudWatchのコンソールを開き、別のAWSサービスに関連するメトリックを閲覧することができます。


[![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/2-1.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/2-1.png)

> By clicking on the ElastiCache Metrics category, you will see the list of available metrics:

ElastiCacheメトリックカテゴリをクリックすると、使用可能なメトリックのリストが表示されます。

[![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/2-2.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/2-2.png)

> You can also view these metrics per cache cluster:

また、キャッシュ・クラスタごとにこれらの指標を見たことができます。

[![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/2-3.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/2-3.png)

> Just select the checkbox next to the metrics you want to visualize, and they will appear in the graph at the bottom of the console:

ちょうどあなたが視覚化するメトリックの隣にあるチェックボックスを選択し、それらは、コンソールの下部にあるグラフに表示されます。


[![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/2-4.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/2-4.png)

### Alerts

> With the CloudWatch Management Console you can also create simple alerts that trigger when a metric crosses a specified threshold.

> Click on the “Create Alarm” button at the right of your graph, and you will be able to set up the alert and configure it to notify a list of email addresses.

CloudWatchの管理コンソールを使用すると、また、メトリックが指定されたしきい値を超えたときにトリガする単純なアラートを作成することができます。

グラフの右側にある「アラームを作成」ボタンをクリックすると、アラートを設定し、電子メールアドレスのリストを通知するように設定することができるようになります。


[![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/2-5.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-elasticache/2-5.png)

## Using the CloudWatch Command Line Interface

> You can also retrieve metrics related to your cache from the command line. First you will need to install the CloudWatch Command Line Interface (CLI) by following [these instructions](http://docs.aws.amazon.com/AmazonCloudWatch/latest/cli/SetupCLI.html). You will then be able to query for any CloudWatch metric, using different filters.

> Command line queries can be useful for spot checks and ad hoc investigations when you can’t, or don’t want to, use a browser.

> For example, if you want to know the CPU utilization statistics for a cache cluster, you can use the CloudWatch command **mon-get-stats** with the parameters you need:

> (on Linux)

また、コマンドラインからあなたのキャッシュに関連するメトリックを取得することができます。まず、これらの指示に従うことにより、CloudWatchのコマンドラインインタフェース（CLI）をインストールする必要があります。その後、別のフィルタを使用して、任意のCloudWatchのメトリックを照会することができるようになります。

コマンドラインクエリは、スポットチェックやアドホック調査はできませんので、または、ブラウザを使用しないために有用であり得ます。

キャッシュ・クラスタのCPU使用率の統計情報を知りたい場合たとえば、あなたが必要なパラメータを持つCloudWatchのコマンド月-取得-統計情報を使用することができます。

（Linuxの場合）



``` lang:sh
mon-get-stats CPUUtilization \
    --dimensions="CacheClusterId=yourcachecluster,CacheNodeId=0004" \
    --statistics=Average \
    --namespace="AWS/ElastiCache" \
    --start-time 2015-08-13T00:00:00 \
    --end-time 2015-08-14T00:00:00 \
    --period=60
```

> [Here](http://docs.aws.amazon.com/AmazonCloudWatch/latest/cli/CLIReference.html) are all the commands you can run with the CloudWatch CLI.

ここでは、CloudWatchのCLIで実行できるすべてのコマンドがあります。


## Monitoring tool integrated with CloudWatch

> The third way to collect CloudWatch metrics is via a dedicated monitoring tool that offers extended monitoring functionality, such as:

> -   Correlation of CloudWatch metrics with metrics from the caching engine and from other parts of your infrastructure
> -   Dynamic slicing, aggregation, and filters on metrics
> -   Historical data access
> -   Sophisticated alerting mechanisms

> CloudWatch can be integrated with outside monitoring systems via API, and in many cases the integration only needs to be enabled once to deliver metrics from all your AWS services.

CloudWatchのメトリックを収集するための第三の方法は、以下のように拡張された監視機能を提供しています専用の監視ツールを使用して次のとおりです。

- キャッシング・エンジンからのメトリックを持つと、インフラストラクチャの他の部分からCloudWatchのメトリックの相関
- メトリックの動的スライシング、集計、およびフィルタ
- 過去のデータアクセス
- 洗練されたアラートメカニズム

CloudWatchのは、APIを介して外部監視システムと統合し、多くの場合、統合は、すべてのあなたのAWSサービスからのメトリックを提供するために、一度有効にする必要がありますすることができます。


## Collecting native Redis or Memcached metrics

> CloudWatch’s ElastiCache metrics can give you good insight about your cache’s health and performance. However, as explained in [Part 1](https://www.datadoghq.com/blog/monitoring-elasticache-performance-metrics-with-redis-or-memcached), supplementing CloudWatch metrics with native cache metrics provides a fuller picture with higher-resolution data.

CloudWatchののElastiCacheメトリックは、あなたのキャッシュの健康とパフォーマンスに関する良い洞察力を与えることができます。しかし、としては、天然のキャッシュ指標と高解像度データとのより完全な画像をCloudWatchのメトリックを提供補う、パート1で説明しました。


### Redis

> Redis provides extensive monitoring out of the box. The `info` command in the Redis command line interface gives you a snapshot of current cache performance. If you want to dig deeper, Redis also provides a number of tools offering a more detailed look at specific metrics. You will find all the information you need in [our recent post about collecting Redis metrics](https://www.datadoghq.com/blog/how-to-collect-redis-metrics/).

> For spot-checking the health of your server or looking into causes of significant latency, Redis’s built-in tools offer good insights.

> However, with so many metrics exposed, getting the information you want all in one place can be a challenge. Moreover, accessing data history and correlating Redis metrics with metrics from other parts of your infrastructure can be essential. That’s why using a monitoring tool integrating with Redis, such as Datadog, will help to take the pain out of your monitoring work.

Redisのは、箱から出して大規模な監視を提供します。 Redisのコマンドラインインターフェイスで、infoコマンドを使用すると、現在のキャッシュパフォーマンスのスナップショットを提供します。あなたは深く掘るしたい場合は、Redisのは、特定のメトリックで、より詳細な外観を提供するツールが多数用意されています。あなたはRedisのメトリックの収集についての我々の最近の記事で必要なすべての情報を見つけるでしょう。

スポットチェック、サーバーの健康状態を、または重要な待ち時間の原因を探して、Redisののビルトインツールは、良好な洞察を提供しています。

非常に多くのメトリックが露出してしかし、一箇所ですべての必要な情報を得ることは挑戦することができます。また、インフラストラクチャの他の部分からのメトリックでRedisのメトリックをデータ履歴にアクセスし、相関が不可欠であることができます。 、このようなDatadogなどのRedis、との統合監視ツールを使用して、監視作業のうち、痛みを取るのに役立ちます理由です。

### Memcached

> Memcached is more limited than Redis when it comes to monitoring. The most useful tool is the stats command, which returns a snapshot of Memcached metrics. Here is an example of its output:

それが監視に来るときのMemcachedはRedisのより制限されています。最も有用なツールでは、memcachedのメトリックのスナップショットを返しstatsコマンド、です。ここでは、その出力の例を示します。


``` lang:sh
stats

STAT pid 14868
STAT uptime 175931
STAT time 1220540125
STAT version 1.2.2
STAT pointer_size 32
STAT rusage_user 620.299700
STAT rusage_system 1545.703017
STAT curr_items 228
STAT total_items 779
STAT bytes 15525
STAT curr_connections 92
STAT total_connections 1740
STAT connection_structures 165
STAT cmd_get 7411
STAT cmd_set 28445156
STAT get_hits 5183
STAT get_misses 2228
STAT evictions 0
STAT bytes_read 2112768087
STAT bytes_written 1000038245
STAT limit_maxbytes 52428800
STAT threads 1
END
```

> If you need more details about the commands you can run with Memcached, you can check their [documentation on Github](https://github.com/memcached/memcached/blob/master/doc/protocol.txt).
> 
> Obviously, you can’t rely only on this snapshot to properly monitor Memcached performance; it tells you nothing about historical values or acceptable bounds, and it is not easy to quickly digest and understand the raw data. From a devops perspective, Memcached is largely a black box, and it becomes even more complex if you run multiple or distributed instances. Other basic tools like [memcache-top](http://code.google.com/p/memcache-top/) (for a changing, real-time snapshot) are useful but remain very limited.
> 
> Thus if you are using Memcached as your ElastiCache engine, like Coursera does (see [Part 3](https://www.datadoghq.com/blog/how-coursera-monitors-elasticache-and-memcached-performance)), you should use CloudWatch or a dedicated monitoring tool that integrates with [Memcached](https://www.datadoghq.com/blog/speed-up-web-applications-memcached/), such as Datadog.

あなたがのMemcachedを使用して実行できるコマンドの詳細が必要な場合は、GitHubの上で自分のドキュメントをチェックすることができます。

もちろん、あなたが適切にmemcachedのパフォーマンスを監視するためにのみ、このスナップショットに依存することはできません。それはあなたの履歴値または許容可能な範囲については何も伝えていない、そしてすぐに消化し、生データを理解することは容易ではありません。 DevOpsチームの観点から、memcachedのは、大部分がブラックボックスであり、あなたが複数または分散のインスタンスを実行する場合にはさらに複雑になります。 memcacheのトップのような他の基本的なツールは、（変更のために、リアルタイムのスナップショット）が有用であるが、非常に限られたままです。

あなたはElastiCacheエンジンとしてMemcachedの使用しているしたがって場合コーセラが行うよう、あなたがCloudWatchのかなどDatadogなどのMemcachedと統合専用の監視ツールを使用する必要があります（第3部を参照してください）。


## Conclusion

> In this post we have walked through how to use CloudWatch to collect, visualize, and alert on ElastiCache metrics, as well as how to access higher-resolution, native cache metrics from Redis or Memcached.
 
> In the [next and final part of this series](https://www.datadoghq.com/blog/how-coursera-monitors-elasticache-and-memcached-performance) we take you behind the scenes with Coursera’s engineering team to learn their best practices and tips for using ElastiCache and monitoring its performance with Datadog.

同様に高解像度、Redisのかmemcachedの由来の天然キャッシュメトリクスにアクセスする方法として、この記事では、収集し可視化するCloudWatchの使用方法を歩いていると、ElastiCacheメトリクスに警告。

このシリーズの次のと最後の部分では、ElastiCacheを使用し、Datadogとその性能を監視するために彼らのベストプラクティスやヒントを学ぶためにコーセラのエンジニアリングチームとの舞台裏あなたを取ります。