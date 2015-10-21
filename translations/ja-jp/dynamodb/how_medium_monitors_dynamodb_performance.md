#How Medium Monitors DynamoDB Performance
*This post is the last of a 3-part series on monitoring Amazon DynamoDB. [Part 1](https://www.datadoghq.com/blog/top-dynamodb-performance-metrics) explores its key performance metrics, and [Part 2](https://www.datadoghq.com/blog/how-to-collect-dynamodb-metrics) explains how to collect these metrics.*

[Medium](https://medium.com/) launched to the public in 2013 and has grown quickly ever since. Growing fast is great for any company, but requires continuous infrastructure scaling—which can be a significant challenge for any engineering team (remember the [fail whale](https://en.wikipedia.org/wiki/Twitter#Outages)?). Anticipating their growth, Medium used DynamoDB as one of its primary data stores, which successfully helped them scale up rapidly. In this article we share with you DynamoDB lessons that Medium learned over the last few years, and discuss the tools they use to monitor DynamoDB and keep it performant.

## **Throttling: the primary challenge**

As explained in [Part 1](https://www.datadoghq.com/blog/top-dynamodb-performance-metrics), throttled requests are the most common cause of high latency in DynamoDB, and can also cause user-facing errors. Properly monitoring requests and provisioned capacity is essential for Medium in order to ensure an optimal user experience.

### Simple view of whole-table capacity

Medium uses Datadog to track the number of reads and writes per second on each of their tables, and to compare the actual usage to provisioned capacity. A snapshot of one of their Datadog graphs is below. As you can see, except for one brief spike their actual usage is well below their capacity.

[![DynamoDB Read Capacity](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/3-01.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/3-01.png)

### Invisibly partitioned capacity

Unfortunately, tracking your remaining whole-database capacity is only the first step toward accurately anticipating throttling. Even though you can provision a specific amount of capacity for a table (or a [Global Secondary Index](http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GSI.html)), the actual request-throughput limit can be much lower. As described by AWS [here](http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GuidelinesForTables.html#GuidelinesForTables.Partitions), DynamoDB automatically partitions your tables behind the scenes, and divides their provisioned capacity equally among these smaller partitions.

That’s not a big issue if your items are accessed uniformly, with each key requested at about the same frequency as others. In this case, your requests will be throttled about when you reach your provisioned capacity, as expected.

However, some elements of a Medium “story” can’t be cached, so when one of them goes viral, some of its assets are requested extremely frequently. These assets have “hot keys” which create an extremely uneven access pattern. Since Medium’s tables can go up to 1 TB and can require tens of thousands of reads per second, they are highly partitioned. For example, if Medium has provisioned 1000 reads per second for a particular table, and this table is actually split into 10 partitions, then a popular post will be throttled at 100 requests per second at best, even if other partitions’ allocated throughput are never consumed.

The challenge is that the AWS console does not expose the number of partitions in a DynamoDB table even if [partitioning is well documented](http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GuidelinesForTables.html#GuidelinesForTables.Partitions). In order to anticipate throttling of hot keys, Medium calculates the number of partitions it expects per table, using the formula described in the AWS documentation. Then they calculate the throughput limit of each partition by dividing their total provisioned capacity by the expected number of partitions.

Next Medium logs each request, and feeds the log to an ELK stack ([Elasticsearch](https://www.elastic.co/products/elasticsearch), [Logstash](https://www.elastic.co/products/logstash), and [Kibana](https://github.com/elastic/kibana)) so that they can track the hottest keys. As seen in the snapshot below (bottom chart), one post on Medium is getting more requests per second than the next 17 combined. If the number of requests per second for that post starts to approach their estimated partitioned limit, they can take action to increase capacity.

[![Kibana screenshot](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/3-02.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/3-02.png)

Note that since partitioning is automatic and invisible, two “semi-hot” posts could be in the same partition. In that case, they may be throttled even before this strategy would predict.

[Nathaniel Felsen](https://medium.com/@faitlezen) from Medium describes in detail, [in this post](https://medium.com/medium-eng/how-medium-detects-hotspots-in-dynamodb-using-elasticsearch-logstash-and-kibana-aaa3d6632cfd), how his team tackles the “hot key” issue.

### The impact on Medium’s users

Since it can be difficult to predict when DynamoDB will throttle requests on a partitioned table, Medium also tracks how throttling is affecting its users.

DynamoDB’s API [automatically retries its queries](http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ErrorHandling.html#APIRetries) if they are throttled so the vast majority of Medium’s throttled requests eventually succeed.

Using Datadog, Medium created the two graphs below. The bottom graph tracks each throttled request “as seen by CloudWatch”. The top graph, “as seen by the apps”, tracks requests that failed, despite retries. Note that there are about two orders of magnitude more throttling events than failed requests. That means retries work, which is good since throttling may only slow down page loads, while failed requests can cause user-facing issues.

[![Throttling CloudWatch vs. application](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/3-03.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/3-03.png)

In order to track throttling as seen by the app, Medium created a custom throttling metric: Each time that Medium’s application receives an error response from DynamoDB, it checks [the type of error](http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ErrorHandling.html). If it’s a **ProvisionedThroughputExceededException**, it increments the custom metric. The metric is reported to Datadog via [DogStatsD](http://docs.datadoghq.com/guides/dogstatsd/), which implements the [StatsD](https://www.datadoghq.com/blog/statsd/) protocol (along with a few extensions for Datadog features). This approach also has the secondary benefit of providing real-time metrics and alerts on user-facing errors, rather than waiting through the slight [delay in information from CloudWatch metrics](http://docs.datadoghq.com/integrations/aws/#metrics-delayed).

In any event, Medium still has some DynamoDB-throttled requests. To reduce throttling frequency, they use [Redis](https://www.datadoghq.com/blog/how-to-monitor-redis-performance-metrics/) as a cache in front of DynamoDB, which at the same time lowers consumed throughput and cost.

## Alerting the right people with the right tool

[Properly alerting](https://www.datadoghq.com/blog/monitoring-101-alerting/) is essential to resolve issues as quickly as possible and preserve application performance. Medium uses Datadog’s alerting features:

-   When a table on “staging” or “development” is impacted, only email notifications to people who are on call, and also send them [Slack](https://www.datadoghq.com/blog/collaborate-share-track-performance-slack-datadog/) messages.
-   When a table on “prod” is impacted, a page alert is also sent via [PagerDuty](https://www.datadoghq.com/blog/end-end-reliability-testing-pagerduty-datadog/).

Since Datadog alerts can be triggered by any metric (including custom metrics), they set up alerts on their production throttling metrics which are collected by their application for each table:

[![Throttling alert](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/3-04.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/3-04.png)

Throttled requests reported by their application mean they failed even after several retries, which means potential user-facing impact. So they send a high-priority alert, set up with the right channels and an adapted message:

[![Throttling alert configuration](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/3-05.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/3-05.png)

## Saving money

By properly monitoring DynamoDB, Medium’s IT team can scale up easily and avoid most throttled requests to ensure an excellent user experience on their platform. But monitoring also helps them identify when they can scale down. Automatically tuning up and down the provisioned throughput for each table is on their road map and will help to optimize their infrastructure expenses.

## Tracking backups

Medium’s engineering team created a Last\_Backup\_Age custom metric which they submit to Datadog via statsd. This metric helps Medium ensure that DynamoDB tables are backed up regularly, which reduces the risk of data loss. They graph the evolution of this metric on their Datadog dashboard and trigger an alert if too much time passes between backups.

## Acknowledgements

We want to thank the Medium teams who worked with us to share their monitoring techniques for Amazon DynamoDB.

If you’re using DynamoDB and Datadog already, we hope that these strategies will help you gain improved visibility into what’s happening in your databases. If you don’t yet have a Datadog account, you can [start tracking](http://docs.datadoghq.com/integrations/aws/) DynamoDB performance today with a [free trial](https://app.datadoghq.com/signup).






この投稿は、Amazon DynamoDBのを監視するには3回シリーズの最後です。第1部では、その主要なパフォーマンス指標を探求し、第2部では、これらのメトリックを収集する方法について説明します。
培地は、2013年に一般公開されて以来、急速に成長してきました。急速に成長すると、すべての企業のための素晴らしいですが、継続的なインフラの拡大縮小 - 任意のエンジニアリングチームにとって重要な課題（失敗クジラを覚えていますか？）することができますする必要があります。彼らの成長を見越して、中には成功した彼らは急速にスケールアップを助け、そのプライマリ・データ・ストアの一つとして、DynamoDBのを使用していました。この記事では、中には、過去数年間で学んだあなたDynamoDBのレッスンと共有し、彼らはDynamoDBのを監視し、パフォーマンスのそれを維持するために使用するツールについて説明します。
スロットリング：主な課題
パート1で説明したように、スロットル要求がDynamoDBの中で高遅延の最も一般的な原因であり、また、ユーザー向けのエラーが発生する可能性があります。適切に要求を監視し、プロビジョニングされた容量は、最適なユーザーエクスペリエンスを確保するために中型のために不可欠です。
全テーブル容量の単純なビュー
培地を読み込み、そのテーブルのそれぞれで毎秒書き込み、プロビジョニングされた容量に実際の使用状況を比較するための数を追跡するDatadogを使用しています。そのDatadogグラフの1のスナップショットは以下の通りです。あなたが見ることができるように、1短い以外は、実際の使用状況がよく能力を下回っているスパイク。
DynamoDBの読み取り能力
目に見えないパーティションの容量
残念ながら、あなたの残りの全データベースの容量を追跡することは正確に調整を先取りに向けた最初のステップです。あなたが提供するテーブルの容量の特定の量（またはグローバルセカンダリインデックス）は、実際の要求スループットの制限がはるかに低くなることができたとしても。ここでは、AWSによって説明したように、DynamoDBのは自動的に舞台裏であなたのテーブルを分割し、均等にこれらのより小さなパーティション間で彼らのプロビジョニング容量を分割します。
あなたの項目が他の人と同じ周波数付近で要求された各キーに、一様にアクセスされた場合には大きな問題ではありません。あなたのプロビジョニング容量に達すると予想されるように、このケースでは、あなたの要求は、約絞られます。
しかし、中 "物語"のいくつかの要素をキャッシュすることはできませんので、そのうちの一つがウイルスになったとき、その資産の一部は、非常に頻繁に要求されています。これらの資産は、非常に不均一なアクセスパターンを作成する「ホットキー」を持っています。ミディアムのテーブルが1 TBまで行くことができますし、数十秒あたり読み込み数千のを必要とすることができるので、彼らは非常に仕切られています。ミディアム1000は、特定のテーブルの1秒当たりの読み取り、このテーブルは、実際に10のパーティションに分割されたプロビジョニングした場合たとえば、その後、人気の記事は決してありませんしても、他のパーティション」に割り当てられたスループット場合、せいぜい毎秒100の要求に絞られます消費しました。
課題は、AWSコンソールは分割が十分に文書化されている場合でもDynamoDBのテーブルにパーティションの数を公開しないことです。ホットキーの調整を予測するためには、中には、AWSのマニュアルに記載の式を使用して、それはテーブルごとに期待するパーティションの数を計算します。その後、彼らは、パーティションの期待数でその合計プロビジョニング容量を分割し、各パーティションのスループット限界を計算します。
次の中には、各要求を記録し、彼らが最もホットキーを追跡できるようにELKスタック（Elasticsearch、Logstash、およびKibana）にログを送ります。以下のスナップショット（下のグラフ）に見られるように、媒体上の1つのポストを組み合わせる次の17より毎秒多くの要求を得ています。その記事の1秒あたりの要求数が見積パーティション限界に近づくために開始した場合、彼らは容量を増やすために行動を取ることができます。
Kibanaスクリーンショット
パーティショニングは、自動と見えないことから、二つの「半ホット」の記事が同じパーティションにあることができることに注意してください。その場合、それらは、この戦略が予測する前であっても絞られてもよいです。
ミディアムからナサニエルFelsenは彼のチームは、「ホットキー」の問題に取り組んでどのように、この記事では、詳細に説明しています。
ミディアムのユーザーへの影響
それはDynamoDBのパーティション表上の要求を絞ります時期を予測することが困難な場合があるので、中にも調整がそのユーザーにどのように影響するかを追跡します。
ミディアムのスロットル要求の大半は、最終的に成功したので、彼らが絞られている場合DynamoDBののAPIは自動的にそのクエリを再試行します。
Datadogを使用して、中には以下の二つのグラフを作成しました。下のグラフの各トラックは、「CloudWatchのから見た」要求を絞ります。 「アプリケーションから見た「上のグラフは、再試行にもかかわらず、失敗した要求を追跡します。失敗した要求よりも大きさよりスロットルイベントの約2オーダーがあることに注意してください。それが失敗した要求は、ユーザーが直面している問題が発生する可能性がありますしながら、スロットルのみ、ページのロードが遅くなる可能性があるので良いですが、再試行作業を意味します。
アプリケーション対CloudWatchのを絞ります
アプリによって見られるようにスロットルを追跡するために、中には、カスタムのスロットルメトリックを作成：中のアプリケーションは、DynamoDBのからエラー応答を受信するたびに、エラーのタイプをチェックします。それはProvisionedThroughputExceededExceptionだ場合は、カスタム・メトリックをインクリメントします。メトリックは、（Datadog機能のいくつかの拡張機能とともに）StatsDプロトコルを実装DogSt​​atsD、経由Datadogに報告されます。このアプローチは、ユーザ側のエラーでリアルタイムのメトリックおよびアラートを提供するのではなく、CloudWatchのメトリックからの情報に若干の遅延を介して待っているの第2の利点があります。
いずれにせよ、培地はまだいくつかのDynamoDBの-絞り要求を有しています。スロットリング頻度を減らすために、彼らは同時に、スループットとコストを消費して低下DynamoDBの、目の前でキャッシュとしてRedisのを使用しています。
適切なツールを適切な人に警告
適切に警告可​​能な限り迅速に問題を解決し、アプリケーションのパフォーマンスを維持するために不可欠です。ミディアムはDatadogのアラート機能を使用しています。
「ステージング」または「開発」のテーブルが影響を受ける場合には、唯一のコールを受けている人への通知を電子メールで送信し、またそれらにスラックメッセージを送信します。
「PROD」の表が影響されている場合、ページの警告もPagerDutyを介して送信されます。
Datadogアラートは（カスタムメトリックを含む）任意の測定基準によってトリガすることができるので、各テーブルへの応用によって収集され、その生産スロットルのメトリックにアラートを設定します：
スロットルアラート
そのアプリケーションによって報告されたスロットル要求は、彼らが潜在的なユーザー向けな影響を意味し、いくつかの再試行後でも失敗を意味します。そこで、彼らは右チャンネルと適合したメッセージで設定優先度の高いアラートを送信：
アラート構成のスロットリング
お金を節約
適切DynamoDBのを監視することにより、中のITチームは、簡単にスケールアップし、そのプラットフォーム上で優れたユーザーエクスペリエンスを確保するための最も絞ら要求を回避することができます。しかし、監視はまた、彼らはスケールダウンすることができたときに、それらが識別するのに役立ちます。自動的にチューニングし、各テーブルのプロビジョニングされたスループットダウン彼らのロードマップ上にあり、そのインフラの費用を最適化するのに役立ちます。
トラッキングのバックアップ
ミディアムのエンジニアリングチームは、彼らがstatsd経由Datadogに提出Last_Backup_Ageカスタムメトリックを作成しました。このメトリックは、ミディアム、データ損失のリスクを低減する、DynamoDBのテーブルは定期的にバックアップされていることを確認するのに役立ちます。彼らはDatadogのダッシュボードにこのメトリックの進化をグラフとあまりにも多くの時間がバックアップの間を通過すると、アラートをトリガーします。
謝辞
我々は、Amazon DynamoDBのための彼らの監視技術を共有するために私たちと一緒に働いていた中、チームに感謝したいと思います。
すでにDynamoDBのとDatadogを使用している場合、我々はこれらの戦略は、あなたのデータベースで何が起こっているかに改善された可視性を得るのを助けることを願っています。あなたはまだDatadogアカウントをお持ちでない場合は、無料試用版で、今日DynamoDBの性能の追跡を開始することができます。
 
この記事のソース値下げはGitHubの上で利用可能です。ご質問、訂正、追加、など？私たちに知らせてください。
