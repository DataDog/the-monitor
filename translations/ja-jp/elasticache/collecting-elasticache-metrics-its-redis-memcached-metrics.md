> *This post is part 2 of a 3-part series on monitoring Amazon ElastiCache. [Part 1](https://www.datadoghq.com/blog/monitoring-elasticache-performance-metrics-with-redis-or-memcached) explores its key performance metrics, and [Part 3](https://www.datadoghq.com/blog/how-coursera-monitors-elasticache-and-memcached-performance) describes how Coursera monitors ElastiCache.*

*このポストは、Amazon ElastiCacheの監視について解説した3回シリーズのPart 2です。[Part 1](https://www.datadoghq.com/blog/monitoring-elasticache-performance-metrics-with-redis-or-memcached)では、ElastiCacheのキーメトリクスを解説しました。[Part 3](https://www.datadoghq.com/blog/how-coursera-monitors-elasticache-and-memcached-performance)では、CourseraがElastiCacheを監視する方法について解説します。*


> Many ElastiCache metrics can be collected from AWS via CloudWatch or directly from the cache engine, whether Redis or Memcached. When that’s the case, as discussed in [Part 1](https://www.datadoghq.com/using-elb-cloudwatch-metrics-to-detect-latency/), you should favor monitoring the native cache metric to ensure higher resolution and greater awareness and responsiveness. Therefore this article covers three different ways to access ElastiCache metrics from AWS CloudWatch, as well as the collection of native metrics from both caching engines:
> 
> -   CloudWatch metrics
>     -   [Using the AWS Management Console](#console)
>     -   [Using the command line interface (CLI)](#cli)
>     -   [Using a monitoring tool that accesses the CloudWatch API](#tool)
> -   Caching engine metrics
>     -   [Redis](#redis)
>     -   [Memcached](#memcached)

ElastiCacheメトリクスの多くは、Redis又はMemcachedのどちらを選択したかに関わらず、CloudWatchとキャッシュエンジンそれ自体の両方から集取することができます。そのようなケースでは、[Part 1](https://www.datadoghq.com/using-elb-cloudwatch-metrics-to-detect-latency/)で説明したように、より高い解像度と応答性を確保するために、ネイティブのキャッシュメトリクスを監視するべきです。従ってこの記事では、まず、AWS CloudWatchを経由しElastiCacheメトリクスにアクセスする3つの方法を解説し、次に両キャッシュエンジンのネイティブメトリクスの収集方法を解説していきます:

- CloudWatchのメトリックス
	- [AWS管理コンソールを使用する方法](#console)
	- [コマンドラインインタフェース(CLI)を使用する方法](#cli)
	- [監視ツールを使用して、CloudWatchのAPIにアクセスする方法](#tool)
- キャッシュエンジンのメトリクス
	- [Redisの場合](#redis)
	- [Memcachedの場合](#memcached)


## Using the AWS Management Console

> Using the online management console is the simplest way to monitor your cache with CloudWatch. It allows you to set up basic automated alerts and to get a visual picture of recent changes in individual metrics. Of course, you won’t be able to access native metrics from your cache engine, but their CloudWatch equivalent is sometimes available (see [Part 1](https://www.datadoghq.com/blog/monitoring-elasticache-performance-metrics-with-redis-or-memcached)).

オンライン管理コンソールは、CloudWatchで、キャッシュの状態を監視する最も簡単な方法です。この管理コンソールを使うことで、基本的な自動アラートを設定したり、個々のメトリックの最近の変化を可視化することができます。勿論、キャッシュエンジンからのネイティブメトリクスにはアクセスすることはできませんが、同等のメトリクスをCloudWatch経由で使用できることができます。(詳細は、[Part 1](https://www.datadoghq.com/blog/monitoring-elasticache-performance-metrics-with-redis-or-memcached)参照)


### Graphs

> Once you are signed in to your AWS account, you can open the [CloudWatch console](https://console.aws.amazon.com/cloudwatch/home#metrics:) and then browse the metrics related to the different AWS services.

AWSアカウントにサインインしたら[CloudWatchのコンソール](https://console.aws.amazon.com/cloudwatch/home#metrics:) を開き、AWSが提供する各種サービスのページへ移動します。


[![](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-elasticache/2-1.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-elasticache/2-1.png)

> By clicking on the ElastiCache Metrics category, you will see the list of available metrics:

ElastiCacheメトリクスを表示するためのカテゴリ項目をクリックすると、公開されているメトリクスのリストが表示されます。

[![](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-elasticache/2-2.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-elasticache/2-2.png)

> You can also view these metrics per cache cluster:

キャッシュクラスター単位で、これらのメトリクスを閲覧することも可能です。

[![](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-elasticache/2-3.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-elasticache/2-3.png)

> Just select the checkbox next to the metrics you want to visualize, and they will appear in the graph at the bottom of the console:

メトリクスの横にあるボックスにチェックマークを付けると、コンソールの下部のエリアにグラフが表示されます:


[![](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-elasticache/2-4.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-elasticache/2-4.png)

### Alerts

> With the CloudWatch Management Console you can also create simple alerts that trigger when a metric crosses a specified threshold.

CloudWatchの管理コンソールを使用すると、メトリクスが設定した閾値を超えたときに動作する基礎的なアラートを作成することができます。

> Click on the “Create Alarm” button at the right of your graph, and you will be able to set up the alert and configure it to notify a list of email addresses.

グラフの右側にある“Create Alarm”ボタンをクリックすると、アラートを作成し、リスト化したメールアドレスへ通知をするための設定ができます。


[![](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-elasticache/2-5.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-elasticache/2-5.png)

## Using the CloudWatch Command Line Interface

> You can also retrieve metrics related to your cache from the command line. First you will need to install the CloudWatch Command Line Interface (CLI) by following [these instructions](http://docs.aws.amazon.com/AmazonCloudWatch/latest/cli/SetupCLI.html). You will then be able to query for any CloudWatch metric, using different filters.

コマンドラインからロードバランサーに関連するメトリックを取得することもできます。これを行うには、[次の手順に従って](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html)、AWS Command Line Interface (CLI) をインストール必要があります。インストールが完了すれば、異なるコマンドオプションを使って、CloudWatchのメトリックを参照することができるようになります。


> Command line queries can be useful for spot checks and ad hoc investigations when you can’t, or don’t want to, use a browser.

コマンドラインからの問い合わせは、スポットチェックや臨時の調査が発生した場合に、ブラウザーが使えない又は使いたくない場合に、非常に便利です。


> For example, if you want to know the CPU utilization statistics for a cache cluster, you can use the CloudWatch command **mon-get-stats** with the parameters you need:

例えば、キャッシュクラスタのCPU使用率の統計情報を知りたい場合は、CloudWatchの**mon-get-stats**コマンドにパラメーターを付して問い合わせすることができます。


> (on Linux)

(Linuxの場合）


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

CloudWatch CLIで、実行できるコマンドの一覧は、[次のリンク](http://docs.aws.amazon.com/AmazonCloudWatch/latest/cli/CLIReference.html)から参照できます。


## Monitoring tool integrated with CloudWatch

> The third way to collect CloudWatch metrics is via a dedicated monitoring tool that offers extended monitoring functionality, such as:

> -   Correlation of CloudWatch metrics with metrics from the caching engine and from other parts of your infrastructure
> -   Dynamic slicing, aggregation, and filters on metrics
> -   Historical data access
> -   Sophisticated alerting mechanisms

CloudWatchのメトリックを収集するための第三の方法は、以下のような拡張された監視機能を持っている専用の監視ツールを使用する方法です。例えば:

- キャッシュ・エンジンからのメトリックやインフラの他の部分からのメトリクスと、CloudWatchのメトリックを相関する
- メトリクスを、動的に分割したり、集計したり、フィルターしたりする
- 過去のデータアクセスをする
- 精巧なメカニズムによるアラートができる


> CloudWatch can be integrated with outside monitoring systems via API, and in many cases the integration only needs to be enabled once to deliver metrics from all your AWS services.

CloudWatchは、APIを介して外部監視システムと連携することができます。多くの場合、この連携の設定を一度だけ済ませれば、AWSの全てのサービスからメトリクスを集取することができるようになります。


## Collecting native Redis or Memcached metrics

> CloudWatch’s ElastiCache metrics can give you good insight about your cache’s health and performance. However, as explained in [Part 1](https://www.datadoghq.com/blog/monitoring-elasticache-performance-metrics-with-redis-or-memcached), supplementing CloudWatch metrics with native cache metrics provides a fuller picture with higher-resolution data.

CloudWatchより収集したElastiCacheメトリックは、キャッシュの健全性とパフォーマンスついてすぐれた洞察を与えてくれます。[Part 1](https://www.datadoghq.com/blog/monitoring-elasticache-performance-metrics-with-redis-or-memcached)で解説したように、ネーティブのキャッシュメトリクスで、CloudWatchからのメトリクスを補うと、高い解像度で完全な状況が把握ができるようになります。


### Redis

> Redis provides extensive monitoring out of the box. The `info` command in the Redis command line interface gives you a snapshot of current cache performance. If you want to dig deeper, Redis also provides a number of tools offering a more detailed look at specific metrics. You will find all the information you need in [our recent post about collecting Redis metrics](https://www.datadoghq.com/blog/how-to-collect-redis-metrics/).

Redisは、初期インストールのままでも広範囲のメトリクスを提供しています。Redisのコマンドラインインターフェイスにある`info`コマンドでは、キャッシュの直近のパフォーマンスを把握することができます。もしも、深く調査したい場合は、Redisには、特定のメトリクスを詳細に解析するための多くのツールが用意されいます。これらのツールに関しては、次のリンク先の[Redisメトリクスの収集に関する直近のポスト](https://www.datadoghq.com/blog/how-to-collect-redis-metrics/)を参照してください。


> For spot-checking the health of your server or looking into causes of significant latency, Redis’s built-in tools offer good insights.

サーバーの健全性に関するスポットチェックや、非常に長いレイテンシの原因究明については、Redisに同胞されているツールを使うことで十分な洞察をえることができます。


> However, with so many metrics exposed, getting the information you want all in one place can be a challenge. Moreover, accessing data history and correlating Redis metrics with metrics from other parts of your infrastructure can be essential. That’s why using a monitoring tool integrating with Redis, such as Datadog, will help to take the pain out of your monitoring work.

しかし、非常に多くのメトリクスが公開されているので、必要な全ての情報を一カ所に集めることは大変な作業かもしれまません。更に、過去のデーターにアクセスしたり、インフラの他部位から収集したメトリクスとRedisメトリクスを相関することも必要になってくるでしょう。従って、Datadogなどのような、Redisと連携した監視ツールは、監視作業の手間の軽減に大幅に役立ちます。


### Memcached

> Memcached is more limited than Redis when it comes to monitoring. The most useful tool is the stats command, which returns a snapshot of Memcached metrics. Here is an example of its output:

監視という観点では、Memcachedは、Redisより制約を受けています。最も有用なツールでは、Memcachedメトリクスのスナップショットを返答するstatsコマンドです。以下が、その出力の例です。


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

Memcachedに対して実行できるコマンドの詳細を知りたい場合は、[GitHub上のドキュメント](https://github.com/memcached/memcached/blob/master/doc/protocol.txt)を参照してください。


> Obviously, you can’t rely only on this snapshot to properly monitor Memcached performance; it tells you nothing about historical values or acceptable bounds, and it is not easy to quickly digest and understand the raw data. From a devops perspective, Memcached is largely a black box, and it becomes even more complex if you run multiple or distributed instances. Other basic tools like [memcache-top](http://code.google.com/p/memcache-top/) (for a changing, real-time snapshot) are useful but remain very limited.

当然ながら、Memcachedのパフォーマンスを適切に監視するために、スナップショットに依存することはできません。スナップショットは、過去の値や容認範囲については把握することができできません。そして、生のデーターを整理し、理解することは容易ではありません。DevOpsの観点からは、Memcachedは、大部分がブラックボックスです。そして、複数や分散インスタンスのMemcachedを運用する場合、状況は、更に複雑になります。[memcache-top](http://code.google.com/p/memcache-top/)のような他の基本ツールを使うこともできますが、機能は非常に限られています。


> Thus if you are using Memcached as your ElastiCache engine, like Coursera does (see [Part 3](https://www.datadoghq.com/blog/how-coursera-monitors-elasticache-and-memcached-performance)), you should use CloudWatch or a dedicated monitoring tool that integrates with [Memcached](https://www.datadoghq.com/blog/speed-up-web-applications-memcached/), such as Datadog.

ElastiCacheエンジンとしてMemcachedの使用している場合には、Courseraが実施しているように、CloudWachを採用するか、Memcachedと直接連携できる専用監視ツールを採用する必要があります。(詳細は、[Part 3](https://www.datadoghq.com/blog/how-coursera-monitors-elasticache-and-memcached-performance)を参照)


## Conclusion

> In this post we have walked through how to use CloudWatch to collect, visualize, and alert on ElastiCache metrics, as well as how to access higher-resolution, native cache metrics from Redis or Memcached.

この記事では、CloudWatchを使ってElastiCacheのメトリックを収集し、視覚化する方法と、メトリクスが閾値を超えた場合にアラートを発生させる方法を解説してきました。更に、RedisとMemcachedの、高い解像度で収集できるネイティブキャッシュメトリクスへアクセスする方法も解説してきました。


> In the [next and final part of this series](https://www.datadoghq.com/blog/how-coursera-monitors-elasticache-and-memcached-performance) we take you behind the scenes with Coursera’s engineering team to learn their best practices and tips for using ElastiCache and monitoring its performance with Datadog.

このシリーズの[Part 3][(https://www.datadoghq.com/blog/how-coursera-monitors-elasticache-and-memcached-performance)では、Courseraのエンジニアリングチームの実際のケースを基に、Datadogを使ったElastiCacheのパフォーマンスの監視方法とElastiCacheの運用方法のベストプラクティスとティップスを解説していきます。