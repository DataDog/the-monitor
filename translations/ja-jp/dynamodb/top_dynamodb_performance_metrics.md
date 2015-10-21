# Top DynamoDB Performance Metrics

*This post is part 1 of a 3-part series on monitoring Amazon DynamoDB. [Part 2](https://www.datadoghq.com/blog/how-to-collect-dynamodb-metrics) explains how to collect its metrics, and [Part 3](https://www.datadoghq.com/blog/how-medium-monitors-dynamodb-performance) describes the strategies Medium uses to monitor DynamoDB.*

## What is DynamoDB?

Amazon DynamoDB is a fully managed [NoSQL](https://en.wikipedia.org/wiki/NoSQL) database cloud service, part of the AWS portfolio. Fast and easily scalable, it is meant to serve applications which require very low latency, even when dealing with large amounts of data. It supports both document and key-value store models, and has properties of both a database and a distributed hash table.

Each table of data created in DynamoDB is synchronously replicated across three availability zones (AZs) to ensure high availability and data durability.

With a flexible data model, high performance, reliability, and a simple but powerful API, DynamoDB is widely used by websites, mobile apps, games, and IoT devices. It is also used internally at Amazon to power many of its services, including S3.

Amazon’s [original paper](http://www.allthingsdistributed.com/2007/10/amazons_dynamo.html) on DynamoDB inspired the creation of several other datastores including Cassandra, Aerospike, Voldemort and Riak.

## Key DynamoDB metrics

In order to correctly provision DynamoDB, and to keep your applications running smoothly, it is important to understand and track key performance metrics in the following areas:

-   **[Requests and throttling](#requests-throttling)**
-   **[Errors](#errors)**
-   [**Global Secondary Index** creation](#gsi)

This article references metric terminology introduced in [our Monitoring 101 series](https://www.datadoghq.com/blog/monitoring-101-collecting-data/), which provides a framework for metric collection and alerting.

[![DynamoDB monitoring dashboard](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/1-01.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/1-01.png)

### What DynamoDB can’t see

Most DynamoDB API clients [automatically implement retries](http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ErrorHandling.html#APIRetries). This is great because if, for example, a request fails due to throttling, it may eventually succeed without sending your application an error. However because retries are completely managed on the client side, DynamoDB can’t track them.

[![DynamoDB requests retries](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/1-02b.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/1-02b.png)

All the metrics discussed in this first post can be collected from DynamoDB via AWS CloudWatch, as detailed in the [second post](https://www.datadoghq.com/blog/how-to-collect-dynamodb-metrics) of this series. But since DynamoDB is not aware of retries, metrics do not capture the full lifetime of a request. This means, for example, that  `SuccessfulRequestLatency` only measures the latency of a successful query attempt and doesn’t add latency for retried failures. This can add complexity to your database performance analysis, but other good monitoring strategies exist, such as those employed by Medium, as described in [Part 3](https://www.datadoghq.com/blog/how-medium-monitors-dynamodb-performance).

### Requests and throttling

#### Terminology:

Many DynamoDB metrics are defined on the basis of a *unit*.

-   A *unit* of read capacity represents one “strongly consistent” read request **per second** or two “eventually consistent” reads per second, for items up to 4 KB. See [DynamoDB FAQ](http://aws.amazon.com/dynamodb/faqs/) for the definitions of “strongly” and “eventually consistent”.
-   A *unit* of write capacity represents one write request per second for items as large as 1 KB.

A single request can result in multiple read or write “events”, all consuming throughput. For example:

-   A `BatchGetItem` request which reads five items results in five `GetItem` events.
-   A `PutItem` request (write) on a table with two [global secondary indexes](#gsi) triggers three events: one write in the table, and one in each of the two indexes.

#### Key metrics:

Metrics related to read and write queries should be monitored for each DynamoDB table separately.


| **Name**                       | **Description**                                                                                                                                                      | [**Metric Type**](https://www.datadoghq.com/blog/monitoring-101-collecting-data/) |
|--------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| SuccessfulRequest-Latency      | Response time (in ms) of successful requests in the selected time period (min, max, avg). Also can report an estimated number of successful requests (data samples). | Work: Performance                                                                 |
| ConsumedRead-CapacityUnits     | Number of read capacity *units* consumed during the selected time period (min, max, avg, sum).                                                                       | Resource: Utilization                                                             |
| ConsumedWrite-CapacityUnits    | Number of write capacity *units* consumed during the selected time period (min, max, avg, sum).                                                                      | Resource: Utilization                                                             |
| ProvisionedRead-CapacityUnits  | Number of read capacity *units* you provisioned for a table (or a global secondary index) during the selected time period (min, max, avg, sum).                      | Other                                                                             |
| ProvisionedWrite-CapacityUnits | Number of write capacity *units* you provisioned for a table (or a global secondary index) during the selected time period (min, max, avg, sum).                     | Other                                                                             |
| ReadThrottleEvents             | Number of read events which exceeded your provisioned read throughput in the selected time period (sum).                                                             | Resource: Saturation                                                              |
| WriteThrottleEvents            | Number of write events which exceeded your provisioned write throughput in the selected time period (sum).                                                           | Resource: Saturation                                                              |
| ThrottledRequests              | Number of user requests containing at least 1 event that exceeded your provisioned throughput in the selected time period (sum).                                     | Resource: Saturation                                                              |

`ThrottledRequests` is not necessarily incremented every time `ReadThrottleEvents` or `WriteThrottleEvents` are. The diagrams below illustrate several such scenarios.

[![Batch Read Requests](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/1-03b.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/1-03b.png)

[![Write Requests](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/1-04b.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/1-04b.png)

[![Batch Write Requests](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/1-05b.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/1-05b.png)

*GSI: [Global Secondary Indexes](#gsi)*

#### Metrics to alert on:

-   `SuccessfulRequestLatency`: If you see this number increasing above normal levels, you should quickly investigate since it can significantly impact your application’s performance. It can be caused by network issues, or requests taking too much time due to your table design. In this case, using [Global Secondary Indexes](#gsi) can help maintain reasonable performance.
     **As described above, `SuccessfulRequestLatency` only measures successful request attempts. So requests that were retried because of throttling, but then succeeded, will likely still appear to be within normal latency ranges, despite taking longer to complete.**

<!-- -->

-   `ConsumedReadCapacityUnits` and `ConsumedWriteCapacityUnits`: Tracking changes in read and write consumed capacity allows you to spot abnormal peaks or drops in read/write activities. In particular you can make sure they don’t exceed their provisioned capacity (`ProvisionedReadCapacityUnits` and `ProvisionedWriteCapacityUnits`), which would result in throttled requests. You might want to set up a first alert before you consume your entire capacity—it could trigger at a threshold of 80% for example. This would give you time to scale up capacity before any requests are throttled. This safety margin is especially useful since CloudWatch metrics might be collected with a slight delay, so your requests might be throttled before you know you have exceeded capacity. As discussed in [Part 3](http://www.datadoghq.com/blog/how-medium-monitors-dynamodb-performance), automatic table partitioning can confound your ability to anticipate throttling, so we take you behind the scenes with [Medium’s engineering team](https://medium.com/medium-eng), to learn their tricks for avoiding throttling.
-   `ReadThrottleEvents` and `WriteThrottleEvents`: These metrics should always be equal to zero. If your provisioned read or write throughput is exceeded by one event, the request is throttled and a 400 error (Bad request) will be returned to the API client, but not necessarily to your application thanks to retries. Note that the `UserErrors` metric mentioned below won’t be incremented.

When a request gets throttled, the DynamoDB API client can automatically retry it. As mentioned above however, this means that there is no DynamoDB metric which increments when the request completely fails after all its retries—DynamoDB does not know if another retry will be attempted.

The most important thing you can do to keep DynamoDB healthy is ensure that you always have enough provisioned throughput for your application. As explained, this can be tricky. Some independent tools, such as [Dynamic DynamoDB](https://aws.amazon.com/blogs/aws/auto-scale-dynamodb-with-dynamic-dynamodb/), can help somewhat by automatically adjusting your provisioned capacity according to the consumption variations. However these tools should be configured very carefully since your costs will be impacted.

[![Consumed throughput and throttling graphs](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/1-06.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/1-06.png)

 

As you can see on these graphs, consumed capacity can briefly spike above 100%. This is because DynamoDB allows a small amount of “burst capacity”. When a table’s throughput is not fully used, DynamoDB saves a portion of this unused capacity for eventual future “bursts” of read or write throughput. However you can’t know exactly how much is available, it can be consumed very quickly, and AWS can use it for background maintenance tasks without warning. For these reasons, it is a bad idea to rely on burst capacity when provisioning your throughput.

#### Catching throttled requests:

If your application needs to catch throttled read/write requests, look for error code `ProvisionedThroughputExceededException`, not `ThrottlingException`. The `ThrottlingException` error code is reserved for [DDL](https://en.wikipedia.org/wiki/Data_definition_language) requests (i.e CreateTable, UpdateTable, DeleteTable).

### Errors


| **Name**                        | **Description**                                                                | [**Metric Type**](https://www.datadoghq.com/blog/monitoring-101-collecting-data/) |
|---------------------------------|--------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| ConditionalCheck-FailedRequests | Number of failed conditional write attempts in the selected time period.       | Other                                                                             |
| UserErrors                      | Number of requests generating an HTTP 400 error in the selected time period.   | Work: Error                                                                       |
| SystemErrors                    | Number of requests resulting in an HTTP 500 error in the selected time period. | Work: Error                                                                       |

#### Metrics to alert on:

-   `ConditionalCheckFailedRequests`: During a write request like PutItem, UpdateItem or DeleteItem operations, you can define a [logical condition](http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Expressions.SpecifyingConditions.html) that defines whether the item can be modified or not: e.g. the item can be updated only if it’s not marked as “protected”. This logical condition has to return “true” to allow the operation to proceed. If it returns “false”, this metric is incremented and a 400 error (Bad request) is returned. Note that it doesn’t increment `UserErrors`.
-   `UserErrors`: If your client application is interacting correctly with DynamoDB, this metric should always be equal to zero. It is incremented for any 400 error [listed here](http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ErrorHandling.html#APIError) except for `ProvisionedThroughputExceededException, ThrottlingException,` and `ConditionalCheckFailedException`. It is usually due to a client error such as an authentication failure.
-   `SystemErrors`: This metric should always be equal to zero. If it is not, you may want to get involved—perhaps restarting portions of the service, temporarily disabling some functionality in your application, or getting in touch with AWS support.

[![System Errors graph](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/1-07.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/1-07.png)

 

### Global Secondary Index creation

#### What is a Global Secondary Index?

When creating a new table, you have to select its primary key. If you need to query by other attributes, the request might take a long time. Indeed some of them will need to scan the entire table to retrieve the information requested. To speed up non-primary-key queries, DynamoDB offers [Global Secondary Indexes](http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GSI.html) (GSI) which increase the performance of these queries on non-key attributes.

#### Key metrics to watch when creating a GSI

When creating a Global Secondary Index from a table, DynamoDB has to allocate resources for this new index and then backfill attributes from the table to the GSI which consumes some of your provisioned capacity. This process can take a long time, especially for large tables, so you should monitor related metrics during GSI creation.


| **Name**                          | **Description**                                                               | [**Metric Type**](https://www.datadoghq.com/blog/monitoring-101-collecting-data/) |
|-----------------------------------|-------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| OnlineIndexConsumedWrite-Capacity | Number of write capacity *units* consumed when creating a new GSI on a table. | Resource: Utilization                                                             |
| OnlineIndexPercentage-Progress    | Percentage of completion of the creation of a new GSI.                        | Other                                                                             |
| OnlineIndexThrottleEvents         | Number of write throttling events that happened when creating a new GSI.      | Resource: Saturation                                                              |

`OnlineIndexPercentageProgress` allows you to follow the progress of the creation of a Global Secondary Index. You should keep an eye on this metric and correlate it with the rest of your DynamoDB metrics to make sure the index creation doesn’t impact overall performance. If the index takes too much time to build, it might be due to throttled events so you should check the `OnlineIndexThrottleEvents` metric.

#### Metrics to watch when creating a GSI:

-   `OnlineIndexConsumedWriteCapacity`: This metric should be monitored when a new GSI is being created so you can be aware if you didn’t provisioned enough capacity. If that’s the case, incoming write requests happening during the index building phase might be throttled which will severely slow down its creation and cause upstream delays or problems. You should then adjust the index’s write capacity using the [`UpdateTable` operation](http://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_UpdateTable.html), which can be done even if the index is still being built.
     NOTE: This metric doesn’t take into account ordinary write throughput consumed during index creation.
-   `OnlineIndexThrottleEvents`: Write-throttled events happening when adding a new Global Secondary Index to a table can dramatically slow down its creation. If this metric is not equal to zero, adjust the index’s write capacity using [`UpdateTable`](http://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_UpdateTable.html). You can prevent throttling by properly monitoring `OnlineIndexConsumedWriteCapacity`.
     NOTE: The `WriteThrottleEvents` metric doesn’t count the throttle events happening during the GSI creation.

## Conclusion

In this post we have explored the most important metrics you should monitor to keep tabs on Amazon DynamoDB performance. If you are just getting started with DynamoDB, monitoring the metrics listed below will give you great insight into your database’s health and performance. Most importantly they will help you identify when it is necessary to tune the provisioned read and write capacities in order to maintain good application performance.

-   [Request latency](#requests-throttling)
-   [Consumed vs. provisioned throughputs (read and write)](#requests-throttling)
-   [Errors](#errors)
-   [Write consumed throughput when creating a Global Secondary Index](#gsi)

Remember to monitor all your tables individually for better insight and understanding.

[Part 2 of this post](https://www.datadoghq.com/blog/how-to-collect-dynamodb-metrics) provides instructions for collecting all the metrics you need from DynamoDB.






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
