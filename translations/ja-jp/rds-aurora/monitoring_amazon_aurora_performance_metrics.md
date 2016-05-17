# [翻訳作業中]

*This post is part 1 of a 3-part series about monitoring the Aurora database service on Amazon RDS. [Part 2][part-2] is about collecting metrics from Aurora, and [Part 3][part-3] details how to monitor Aurora with Datadog.*

この投稿は、Amazon RDS上オーロラデータベースサービスの監視を約3回シリーズの第1部です。第2部では、オーロラからメトリックを収集する程度であり、第3部はDatadogでオーロラを監視する方法について詳しく説明します。

## What is Aurora?

[Amazon Aurora][aurora] is a MySQL-compatible database offered on RDS (Relational Database Service), a hosted database service in the AWS cloud. RDS users can choose from several well-known database engines that are also available as standalone products, including MySQL, Oracle, SQL Server, Postgres, and MariaDB, but Aurora is only available on RDS.

Aurora offers unique features such as auto-scaling storage, extremely low-latency replication, and rapid automated failover to a standby instance. Amazon advertises throughput enhancements of up to 5x as compared to MySQL running on similar hardware. Aurora users also have access to an expanded suite of [monitoring metrics][aurora-metrics] as compared to other RDS users. Aurora exposes not just system- and disk-level metrics but also crucial metrics on query throughput and latency, as detailed below.

アマゾンオーロラは、RDS（リレーショナルデータベースサービス）、AWSクラウドでホストされたデータベース・サービスで提供されるMySQLの互換性データベースです。 RDSユーザーは、MySQLのは、Oracle、SQL Serverの、Postgresの、およびMariaDBを含むスタンドアロン製品として入手可能であるいくつかのよく知られているデータベースエンジンから選択することができますが、オーロラは、RDS上でのみ使用可能です。

オーロラは、このようなスタンバイ・インスタンスへの自動スケーリングストレージ、超低レイテンシーのレプリケーション、および迅速な自動フェイルオーバーなどのユニークな機能を提供しています。アマゾンは、MySQLが同様のハードウェア上で実行されていると比較して5倍までのスループットの拡張機能をアドバタイズします。オーロラのユーザーは、他のRDSのユーザーと比較して、モニタリング指標の拡大スイートへのアクセス権を持っています。以下に詳述するようにオーロラは、システム - とディスクレベルの指標だけでなく、クエリのスループットとレイテンシに重要なメトリックだけでなく、公開されます。


## Key metrics for Amazon Aurora

To keep your applications running smoothly, it is important to understand and track performance metrics in the following areas:

* [Query throughput](#query-throughput)
* [Query performance](#query-performance)
* [Resource utilization](#resource-utilization)
* [Connections](#connection-metrics)
* [Read replica metrics](#read-replica-metrics)

RDS exposes dozens of high-level metrics, and Aurora users can access literally hundreds more from the MySQL-compatible database engine. With so many metrics available, it's not always easy to tell what you should focus on. In this article we'll highlight key metrics in each of the above areas that together give you a detailed view of your database's performance.

RDS metrics (as opposed to storage engine metrics) are available through Amazon CloudWatch, and many are available regardless of which database engine you use. Engine metrics, on the other hand, can be accessed from the database instance itself. [Part 2 of this series][part-2] explains how to collect both types of metrics. CloudWatch Aurora metrics are available at one-minute intervals; database engine metrics can be collected at even higher resolution.

This article references metric terminology introduced in [our Monitoring 101 series][metric-101], which provides a framework for metric collection and alerting.

スムーズに実行しているアプリケーションを維持するには、以下の分野でのパフォーマンス・メトリックを理解し、追跡することが重要です。

クエリのスループット
クエリのパフォーマンス
リソースの活用
接続
レプリカメトリックを読みます
RDSは、高レベルのメトリックの数十を公開し、そしてオーロラのユーザーは、MySQL互換のデータベースエンジンから文字通り数百以上にアクセスすることができます。利用可能なので、多くの指標では、それはあなたが焦点を当てるべきかを伝えることは必ずしも容易ではありません。この記事では、一緒にあなたのデータベースのパフォーマンスの詳細を与える上記の各分野における主要な指標を強調表示します。

RDSメトリックは（ストレージエンジンの指標とは対照的に）はAmazon CloudWatchのを介して利用可能であり、多くは関係なく、使用するデータベースエンジンの利用可能です。エンジンメトリックは、一方で、データベースインスタンス自体からアクセスすることができます。このシリーズの第2回では、メトリックの両方のタイプを収集する方法について説明します。 CloudWatchのオーロラメトリックは1分間隔でご利用いただけます。データベースエンジンの指標は、より高い分解能で収集することができます。

この記事の参照メトリック用語は、メトリック収集と警告するためのフレームワークを提供し、当社のモニタリング101シリーズで導入されました。


### Compatibility with MySQL and MariaDB

Because Aurora is compatible with MySQL 5.6, standard MySQL administration and monitoring tools, such as the `mysql` command line interface, will generally work with Aurora without modification. And most of the strategies outlined here also apply to MySQL and MariaDB on RDS. But there are some key differences between the database engines. For instance, Aurora has auto-scaling storage, so it does not expose a metric tracking free storage space. And the version of MariaDB (10.0.17) available on RDS at the time of this writing is not fully compatible with some of the metric collection tools detailed in [Part 2][part-2] of this series. MySQL users should check out our three-part series on [monitoring MySQL on RDS][mysql-rds].

オーロラは、MySQL5.6と互換性があるため、標準のMySQLの管理と、そのようなmysqlのコマンドラインインタフェースとして監視ツールは、一般的に変更することなく、オーロラで動作します。そして、ここで概説した戦略のほとんどはまた、RDS上でMySQLとMariaDBに適用されます。しかし、データベースエンジンとの間にいくつかの重要な違いがあります。例えば、オーロラは、自動スケーリングストレージを持っているので、メトリックの追跡空き容量を公開しません。そして、この記事の執筆時点でRDS上でMariaDB（10.0.17）利用可能のバージョンは、このシリーズのパート2で詳述メトリック収集ツールのいくつかと完全に互換性がありません。 MySQLのユーザーがRDSにMySQLを監視する上で、当社の3回シリーズをチェックアウトする必要があります。


<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-11-aurora/aurora-ootb-dash-2.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-11-aurora/aurora-ootb-dash-2.png"></a>

<!--<h3 class="anchor" id="query-throughput">Query throughput</h3>-->

### <a class="anchor" id="query-throughput"></a>Query throughput

| **Metric description** | **CloudWatch name** | **MySQL name** | [**Metric&nbsp;type**][metric-101] |
|:----------------------:|:-------------------:|:--------------:|:-------------|
| Queries | Queries (per second) | Queries (count) | Work: Throughput |
| Reads | SelectThroughput (per second) | Com\_select + Qcache\_hits (count) | Work: Throughput |
| Writes | DMLThroughput (per second) | Com\_insert + Com\_update + Com\_delete (count) | Work: Throughput |

Your primary concern in monitoring any system is making sure that its [work is being done][collecting-data] effectively. A database's work is running queries, so the first priority in any monitoring strategy should be making sure that queries are being executed.

You can also monitor the breakdown of read and write commands to better understand your database's read/write balance and identify potential bottlenecks. Those metrics can be collected directly from Amazon CloudWatch or computed by summing native MySQL metrics from the database engine. In MySQL metrics, reads increment one of two status variables, depending on whether or not the read is served from the query cache:

任意のシステムを監視する中であなたの主な関心事は、その作業が効率的に行われていることを確認しています。データベースの仕事は、クエリを実行しているので、任意の監視戦略における最優先事項は、クエリが実行されていることを確認するべきです。

あなたはまた、より良いあなたのデータベースの読み取り/書き込みのバランスを理解し、潜在的なボトルネックを特定するための読み取りおよび書き込みコマンドの内訳を監視することができます。これらの指標は、Amazon CloudWatchのから直接収集したり、データベースエンジンからネイティブMySQLのメトリックを合計することによって計算することができます。 MySQLのメトリックでは、読み出しは、クエリキャッシュから提供されているか否かに応じて、2つの状態変数の増分1を読み込みます。


    Reads = `Com_select` + `Qcache_hits`

Writes increment one of three status variables, depending on the command:

コマンドに応じて、3つのステータス変数の増分1を書き込みます：


    Writes = `Com_insert` + `Com_update` + `Com_delete`

In CloudWatch metrics, all DML requests (inserts, updates, and deletes) are rolled into the `DMLThroughput` metric, and all `SELECT` statements are incorporated in the `SelectThroughput` metric, whether or not the query is served from the query cache.

CloudWatchのメトリックでは、すべてのDML要求（挿入、更新、削除）はDMLThroughputメトリックにロールバックされ、すべてのSELECT文は、クエリは、クエリキャッシュから提供されているかどうか、SelectThroughputメトリックに組み込まれています。


#### Metric to alert on: Queries per second

The current rate of queries will naturally rise and fall, and as such is not always an actionable metric based on fixed thresholds alone. But it is worthwhile to alert on sudden changes in query volume—drastic drops in throughput, especially, can indicate a serious problem.

クエリの現在のレートは、自然に立ち上がりおよび立ち下がり、そのように常に単独の固定しきい値に基づいて実用的なメトリックではないでしょう。しかし、それはスループットのクエリボリューム抜本的な滴の急激な変化に警告する価値がある、特に、深刻な問題を示すことができます。


<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-11-aurora/questions_2.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-11-aurora/questions_2.png"></a>

<h3 class="anchor" id="query-performance">Query performance</h3>

### <a class="anchor" id="query-performance"></a>Query performance

| **Metric description** | **CloudWatch name** | **MySQL name** | [**Metric&nbsp;type**][metric-101] |
|:----------------------:|:-------------------:|:--------------:|:-------------|
| Read query latency, in milliseconds | SelectLatency | - | Work: Performance |
| Write query latency, in milliseconds | DMLLatency | - | Work: Performance |
| Queries exceeding `long_query_time` limit | - | Slow_queries | Work: Performance |
| Query errors | - | (Only available via database query) | Work: Error |

The Aurora-only metrics for `SELECT` latency and DML (insert, update, or delete) latency capture a critical measure of query performance. Along with query volume, latency should be among the top metrics monitored for almost any use case.

MySQL (and therefore Aurora) also features a `Slow_queries` metric, which increments every time a query's execution time exceeds the number of seconds specified by the `long_query_time` parameter. To modify `long_query_time` (or any other database parameter), simply log in to the AWS Console, navigate to the RDS Dashboard, and select the parameter group that your RDS instance belongs to. You can then filter to find the parameter you want to edit.

SELECTレイテンシとDML（挿入、更新、または削除）待ち時間キャプチャクエリのパフォーマンスの重要な指標のためのオーロラメトリックのみ。クエリのボリュームに加えて、待ち時間はほぼすべてのユースケースについて監視トップの指標の一つである必要があります。

MySQLの（したがって、オーロラ）も、クエリの実行時間がlong_query_timeパラメータで指定した秒数を超えるたびに増加しSlow_queriesメトリックを備えています。 long_query_time（または他のデータベース・パラメータ）を変更するには、単に、AWS ConsoleにログインRDSダッシュボードに移動し、あなたのRDSインスタンスが属するパラメータグループを選択します。その後、編集したいパラメータを見つけるためにフィルタリングすることができます。


<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-11-aurora/parameter-groups.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-11-aurora/parameter-groups.png"></a>

For a deeper look into query performance, the MySQL [performance schema][performance-schema] (which is compatible with Aurora but is disabled by default) also stores valuable statistics, including query latency, from the database server. Though you can query the performance schema directly, it is easier to use Mark Leith’s [sys schema][sys-schema], which provides convenient views, functions, and procedures to gather metrics from MySQL or Aurora. For instance, to find the execution time of all the different statement types executed by each user:

クエリのパフォーマンスに深く一見のために、（オーロラと互換性がありますが、デフォルトでは無効になって）MySQLの性能スキーマは、データベース・サーバーからのクエリの待機時間を含め、貴重な統計情報を、記憶しています。あなたが直接パフォーマンススキーマを照会することができますが、MySQLやオーロラからメトリックを収集するために便利なビュー、関数、およびプロシージャを提供してマークリースのSYSスキーマを使用する方が簡単です。たとえば、各ユーザーによって実行されたすべての異なるステートメントの種類の実行時間を見つけるために：


<pre class="lang:mysql">
mysql> select * from sys.user_summary_by_statement_type;
</pre>

Or, to find the slowest statements (those in the 95th percentile by runtime):

または、最も遅いステートメント（ランタイムによって95パーセンタイルのもの）を見つけるために：


<pre class="lang:mysql">
mysql> select * from sys.statements_with_runtimes_in_95th_percentile\G
</pre>

Many useful usage examples are detailed in the sys schema [documentation][sys-schema].

To enable the performance schema, you must set the `performance_schema` parameter to 1 in the database instance's parameter group using the AWS console. If not enabled, this change requires an instance reboot. More about enabling the performance schema and installing the sys schema in [Part 2][part-2] of this series.

The performance schema and sys schema also allow you to quickly assess how many queries generated errors or warnings:

多くの有用な使用例は、SYSスキーマのドキュメントに詳述されています。

パフォーマンスのスキーマを有効にするには、AWSコンソールを使用して、データベース・インスタンスのパラメータグループ内の1にperformance_schemaパラメータを設定する必要があります。有効でない場合は、この変更は、インスタンスの再起動が必要です。パフォーマンスのスキーマを有効にし、このシリーズのパート2で、SYSスキーマのインストールの詳細。

パフォーマンスのスキーマおよびSYSスキーマはまた、あなたがすぐにエラーや警告が発生したどのように多くのクエリを評価することができます：


<pre class="lang:mysql">
mysql> SELECT SUM(errors) FROM sys.statements_with_errors_or_warnings;
</pre>

#### Metrics to alert on

* Latency: Slow reads or writes will necessarily add latency to any application that relies on Aurora. If your queries are executing more slowly than expected, evaluate your RDS [resource metrics](#resource-utilization). Aurora users also have a number of caching options to expedite transactions, from making more RAM available for the [buffer pool][buffer-pool] used by InnoDB (usually by upgrading to a larger instance), to enabling or expanding the [query cache][query-cache] that serves identical queries from memory, to using an application-level cache such as Memcached or [Redis][redis].

* `Slow_queries`: How you define a slow query (and therefore how you configure the `long_query_time` parameter) will depend heavily on your use case and performance requirements. If the number of slow queries reaches worrisome levels, you will likely want to identify the actual queries that are executing slowly so you can optimize them. You can do this by querying the sys schema or by configuring Aurora to log all slow queries. More information on enabling and accessing the slow query log is available [in the RDS documentation][slow-log]. <pre class="lang:mysql">mysql> SELECT * FROM mysql.slow_log LIMIT 10\G
*************************** 1. row ***************************
    start_time: 2015-11-13 11:09:14
     user_host: gob[gob] @  [x.x.x.x]
    query_time: 00:00:03
     lock_time: 00:00:00
     rows_sent: 2844047
 rows_examined: 3144071
            db: employees
last_insert_id: 0
     insert_id: 0
     server_id: 1656409327
      sql_text: select * from employees left join salaries using (emp_no)
     thread_id: 21260
</pre>

* Query errors: A sudden increase in query errors can indicate a problem with your client application or your database. You can use the sys schema to quickly explore which queries may be causing problems. For instance, to list the 10 normalized statements that have returned the most errors:<pre class="lang:mysql">mysql> SELECT * FROM sys.statements_with_errors_or_warnings ORDER BY errors DESC LIMIT 10\G</pre>

<!--<h3 class="anchor" id="resource-utilization">Resource utilization</h3>-->

### <a class="anchor" id="resource-utilization"></a>Resource utilization

#### Disk I/O metrics
| **Name** | **Description** | [**Metric&nbsp;type**][metric-101] | **Availability** |
|:--------:|:---------------:|:---------------:|:------------:|
| ReadIOPS | Read I/O operations per second | Resource: Utilization | CloudWatch |
| WriteIOPS | Write I/O operations per second | Resource: Utilization | CloudWatch |
| DiskQueueDepth | I/O operations waiting for disk access | Resource: Saturation | CloudWatch |
| ReadLatency | Milliseconds per read I/O operation | Resource: Other | CloudWatch |
| WriteLatency | Milliseconds per write I/O operation | Resource: Other | CloudWatch |

#### CPU, memory, and network metrics
| **Name** | **Description** | [**Metric&nbsp;type**][metric-101] | **Availability** |
|:--------:|:---------------:|:---------------:|:------------:|
| CPUUtilization | Percent CPU utilized | Resource: Utilization | CloudWatch |
| FreeableMemory | Available RAM in gigabytes | Resource: Utilization | CloudWatch |
| NetworkReceive<br>Throughput | Client network traffic to the Aurora instance, in megabytes per second | Resource: Utilization | CloudWatch |
| NetworkTransmit<br>Throughput | Client network traffic from the Aurora instance, in megabytes per second | Resource: Utilization | CloudWatch |

As Baron Schwartz, co-author of *[High Performance MySQL][mysql-book],* often notes, a database needs four fundamental resources: CPU, memory, disk, and network. Any of these can become a performance bottleneck—for a look at how difference RDS instance types can be constrained by their available resources, check out [this 2013 talk][bottlenecks] by Amazon's Grant McAlister.

Whenever your database instance experiences performance problems, you should check metrics pertaining to the four fundamental resources to look for bottlenecks. Though you cannot access the full suite of system-level metrics that are available for EC2, CloudWatch does make available metrics on all four of these resources. For the most part, these metrics are most useful for [investigating (rather than detecting)][investigation] performance issues.

CPU、メモリ、ディスク、およびネットワーク：男爵シュワルツ、高性能のMySQLの共著者は、しばしば指摘したように、データベースは、4の基本的なリソースを必要とします。これらは、パフォーマンスのボトルネックの差分RDSインスタンスタイプは、それらの利用可能なリソースによって制約することができる方法を見になっAmazonのグラントMcAlisterことで、この2013年の話をチェックアウトすることができます。

データベース・インスタンスは、パフォーマンスの問題を経験するたび、あなたはボトルネックを探すために、4の基本的なリソースに関連する指標を確認する必要があります。あなたがEC2で利用可能なシステム・レベルのメトリックの完全なスイートにアクセスすることはできませんが、CloudWatchのは、これらのリソースのすべての4つ上の使用可能なメトリックを作るん。ほとんどの部分については、これらの指標は、パフォーマンスの問題を調査する（というよりも検出）のために最も有用です。


<!--<h4 class="anchor" id="disk-i/o-metrics">Disk I/O metrics</h4>-->

#### <a class="anchor" id="disk-i/o-metrics"></a>Disk I/O metrics

CloudWatch makes available RDS metrics on read and write IOPS, which indicate how much your database is interacting with backing storage. If your storage volumes cannot keep pace with the volume of read and write requests, you will start to see I/O operations queuing up. The `DiskQueueDepth` metric measures the length of this queue at any given moment.

Note that there will not be a one-to-one correspondence between queries and disk operations—queries that can be served from memory will bypass disk, for instance, and queries that return a large amount of data can involve more than one I/O operation.

In addition to I/O throughput metrics, RDS offers `ReadLatency` and `WriteLatency` metrics. These metrics do not capture full query latency—they only measure how long your I/O operations are taking at the disk level.

For read-heavy applications, one way to overcome I/O limitations is to [create a read replica][read-replica] of the database to serve some of the client read requests. Aurora allows you to create up to 15 replicas for every primary instance. For more, see the [section below](#read-replica-metrics) on metrics for read replicas.

CloudWatchのは、読み取りに利用できるRDSメトリックを行い、データベースがバッキングストレージと対話しているどの程度を示すIOPSを、書きます。お使いのストレージボリュームが読み取りおよび書き込み要求の量のペースを保つことができない場合は、最大キューイングI / O操作を確認するために開始されます。 DiskQueueDepthメトリック措置いつなんどきでも、このキューの長さ。

大量のデータが複数を含むことができる返すクエリおよび例えば、ディスクをバイパスしますメモリから提供することができますディスク操作-クエリ、およびクエリの間に1対1の対応が存在しないことに注意してくださいI / O操作。

I / Oスループットの測定基準に加えて、RDSはReadLatencyとWriteLatencyメトリックを提供しています。これらの指標は、完全なクエリの待機時間 - 彼らはあなたのI / O操作は、ディスクレベルで取っているどのくらいの時間を測定キャプチャしません。

読み取り重用途のために、I / Oの制限を克服する一つの方法は、クライアントのいくつかは、読み取り要求提供するために、データベースのリードレプリカを作成することです。オーロラは、あなたがすべてのプライマリインスタンスのための15のレプリカまで作成することができます。詳細については、読み取りレプリカのメトリックについては、以下のセクションを参照してください。


#### CPU metrics

High CPU utilization is not necessarily a bad sign. But if your database is performing poorly while metrics for IOPS and network are in normal ranges, and while the instance appears to have sufficient memory, the CPUs of your chosen instance type may be the bottleneck.

高いCPU使用率が必ずしも悪い兆候ではありません。しかし、あなたのデータベースが不十分な実行している場合IOPSおよびネットワークのメトリックは、正常範囲にあり、インスタンスが十分なメモリを持っているように見えますが、あなたの選択したインスタンス・タイプのCPUがボトルネックになる可能性があります。


#### Memory metrics

Databases perform best when most of the working set of data can be held in memory. For this reason, you should monitor `FreeableMemory` to ensure that your database instance is not memory-constrained. AWS advises that you use the ReadIOPS metric to determine whether the working set is largely in memory:

> To tell if your working set is almost all in memory, check the ReadIOPS metric (using AWS CloudWatch) while the DB instance is under load. The value of ReadIOPS should be small and stable.

データのワーキングセットのほとんどはメモリに保持することができたときにデータベースが最適行います。このような理由から、あなたのデータベースインスタンスがメモリに制約がないことを確認するためにFreeableMemoryを監視する必要があります。 AWSは、設定作業がメモリに大部分があるかどうかを決定するメトリックReadIOPSを使用することを助言します：

あなたのワーキングセットがメモリ内のほぼすべてのであれば、教えてDBインスタンスに負荷がかかっている間（AWS CloudWatchのを使用して）メトリックReadIOPSを確認します。 ReadIOPSの値が小さく、安定していなければなりません。


#### Network metrics
Unlike other RDS database engines, Aurora's network throughput metrics do not include network traffic from the database instances to the storage volumes. The `NetworkReceiveThroughput` and `NetworkTransmitThroughput` metrics therefore track only network traffic to and from clients.

他のRDSのデータベースエンジンとは異なり、オーロラのネットワークスループットの測定基準は、ストレージボリュームにデータベース・インスタンスからのネットワークトラフィックが含まれていません。 NetworkReceiveThroughputとNetworkTransmitThroughputメトリックは、そのためにクライアントからのネットワークトラフィックのみを追跡します。


#### Metrics to alert on

* `DiskQueueDepth`: It is not unusual to have some requests in the disk queue, but investigation may be in order if this metric starts to climb, especially if latency increases as a result. (Time spent in the disk queue adds to read and write latency.)

DiskQueueDepth：、それは、ディスクキュー内のいくつかの要求を持つことは珍しいことではありませんが、このメトリック開始を登る場合、調査は順序であってもよい場合は特に、結果として、待ち時間が増加します。 （時間は、キューが読み取りおよびレイテンシを書くために追加されたディスクで過ごしました。）


<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-11-aurora/disk-queue.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-11-aurora/disk-queue.png"></a>

<!--<h3 class="anchor" id="connection-metrics">Connection metrics</h3>-->

### <a class="anchor" id="connection-metrics"></a>Connection metrics

| **Metric description** | **CloudWatch name** | **MySQL name** | [**Metric&nbsp;type**][metric-101] |
|:----------------------:|:-------------------:|:--------------:|:-------------|
| Open database connections | DatabaseConnections | Threads\_connected | Resource: Utilization |
| Currently running connections | - | Threads\_running | Resource: Utilization |
| Failed connection attempts | LoginFailures (per second) | Aborted\_connects (count) | Resource: Error |
| Count of connections refused due to server error | - | Connection\_errors\_<br>internal | Resource: Error |
| Count of connections refused due to `max_connections` limit | - | Connection\_errors\_<br>max_connections | Resource: Error |

Monitoring how many client connections are in use is critical to understanding your database's activity and capacity. Aurora has a configurable connection limit; the default value depends on the memory of the database's instance class in bytes, according to the formula:

多くのクライアント接続が使用中であるかを監視することで、データベースの活動や能力を理解するために重要です。オーロラは、設定可能な接続の制限があります。デフォルト値は、式に従って、バイト単位でデータベースのインスタンスクラスのメモリに依存します。

`log(DBInstanceClassMemory/8187281408)*1000`

The `max_connections` parameter can be checked or modified via the database instance's parameter group using the RDS dashboard in the AWS console. You can also check the current value of `max_connections` by querying the Aurora instance itself (see [part 2][part-2] of this series for more on connecting to RDS instances directly):

MAX_CONNECTIONSパラメータがオンまたはAWSコンソールでRDSのダッシュボードを使用して、データベース・インスタンスのパラメータ群を経由して変更することができます。また、オーロラインスタンス自体が（直接インスタンスをRDSへの接続の詳細については、このシリーズのパート2を参照）照会することにより、MAX_CONNECTIONSの現在の値を確認することができます。

<pre class="lang:mysql">
mysql> SELECT @@max_connections;
+-------------------+
| @@max_connections |
+-------------------+
|              1000 |
+-------------------+
1 row in set (0.00 sec)
</pre>

To monitor how many connections are in use, CloudWatch exposes a `DatabaseConnections` metric tracking open connections, and the database engine exposes a similar `Threads_connected` metric. The `Threads_running` metric provides additional visibility by isolating the threads that are actively processing queries.

If your server reaches the `max_connections` limit and starts to refuse connections, `Connection_errors_max_connections` will be incremented, as will the `Aborted_connects` metric tracking all failed connection attempts. CloudWatch also tracks failed connections via the `LoginFailures` metric.

Aurora's database engine exposes a variety of other metrics on connection errors, which can help you identify client issues as well as serious issues with the database instance itself. The metric `Connection_errors_internal` is a good one to watch, because it is incremented when the error comes from the server itself. Internal errors can reflect an out-of-memory condition or the server's inability to start a new thread.

使用中の接続数を監視するには、CloudWatchのは、開いている接続を追跡するメトリックDatabaseConnectionsを公開して、データベースエンジンは、同様のThreads_connectedメトリックを公開します。 Threads_runningメトリックは、積極的にクエリを処理しているスレッドを単離することによって、追加の可視性を提供します。

サーバーがMAX_CONNECTIONS限界に達し、接続を拒否するために開始した場合、すべての接続の試みを失敗した追跡メトリックAborted_connectsを意志として、Connection_errors_max_connectionsは、インクリメントされます。 CloudWatchのもメトリックLoginFailuresを経由して失敗した接続を追跡します。

オーロラのデータベースエンジンは、データベース・インスタンス自体でクライアントの問題と同様に深刻な問題を識別するのに役立ちます接続エラー上の他のメトリック、さまざまなを公開しています。エラーがサーバー自体から来るとき、それがインクリメントされるため、メトリックConnection_errors_internalは、見て良いものです。内部エラーは、メモリ不足の状態か、新しいスレッドを開始するには、サーバーのできないことを反映することができます。


#### Metrics to alert on

* Open database connections: If a client attempts to connect to Aurora when all available connections are in use, Aurora will return a "Too many connections" error and increment `Connection_errors_max_connections`. To prevent this scenario, you should monitor the number of open connections and make sure that it remains safely below the configured limit.

* Failed connection attempts: If this metric is increasing, your clients are probably trying and failing to connect to the database. Dig deeper with metrics such as `Connection_errors_max_connections` and `Connection_errors_internal` to diagnose the problem.

開いているデータベース接続：クライアントは、利用可能なすべての接続が使用中のときにオーロラに接続しようとすると、オーロラは「あまりにも多くの接続"エラーを返すとConnection_errors_max_connectionsをインクリメントします。このシナリオを回避するには、開いている接続の数を監視し、それが安全に構成された制限を下回ったままでいることを確認する必要があります。

接続の試行を失敗しました：このメトリックが増加している場合、クライアントは、おそらくしようとしてデータベースに接続するために失敗しています。問題を診断するためにそのようなConnection_errors_max_connectionsやConnection_errors_internalなどの指標で深く掘ります。


<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/threads_connected_2.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/threads_connected_2.png"></a>

<!--<h3 class="anchor" id="read-replica-metrics">Read replica metrics</h3>-->

<a class="anchor" id="read-replica-metrics"></a>Read replica metrics

| **Name** | **Description** | [**Metric&nbsp;type**][metric-101] | **Availability** |
|:--------:|:---------------:|:---------------:|:------------:|
| AuroraReplicaLag | Number of milliseconds by which replica trails primary instance | Other | CloudWatch |

Aurora supports the creation of up to 15 read replicas from the master instance. These replicas are assigned a separate endpoint, so you can point client applications to read from a replica rather than from the source instance. You can also monitor the replica's connections, throughput, and query performance, just as you would for an ordinary RDS instance.

The lag time for any read replica is captured by the CloudWatch metric `AuroraReplicaLag`. This metric is usually not actionable, although if the lag is consistently very long, you should investigate your settings and resource usage.

Note that this is a significantly different metric than the generic RDS metric `ReplicaLag`, which applies to other database engines. Because Aurora instances all read from the same virtual storage volume, the `AuroraReplicaLag` tracks the lag in page cache updates from primary to replica rather than the lag in applying all write operations from the primary instance to the replica.

オーロラは、マスター・インスタンスから最大15のリードレプリカの作成をサポートします。あなたはレプリカからではなく、ソース・インスタンスからの読み取りにクライアントアプリケーションを指すことができますので、これらのレプリカは、個別のエンドポイントが割り当てられています。ちょうどあなたが普通のRDSインスタンスの場合と同じように、あなたはまた、レプリカの接続、スループット、およびクエリのパフォーマンスを監視することができます。

任意のタイムラグはレプリカがCloudWatchのメトリックAuroraReplicaLagによって捕捉されるお読みください。ラグは一貫して非常に長い場合、あなたはあなたの設定やリソースの使用状況を調査する必要がありますが、このメトリックは、通常、実用ではありません。

これは他のデータベースエンジンに適用される一般的なRDSメトリックReplicaLag、より有意に異なるメトリックであることに注意してください。オーロラのインスタンスはすべて同じ仮想ストレージ・ボリュームから読み取るので、AuroraReplicaLagは、レプリカへのプライマリからページキャッシュの更新の遅れではなく、すべてのレプリカにプライマリ・インスタンスからの書き込み操作を適用する際の遅れを追跡します。


<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-11-aurora/replica-lag.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-11-aurora/replica-lag.png"></a>

## Conclusion

In this post we have explored the most important metrics you should monitor to keep tabs on performance for Amazon Aurora. If you are just getting started with Aurora, monitoring the metrics listed below will give you great insight into your database’s activity and performance. They will also help you to identify when it is necessary to upgrade your instance type or add read replicas to maintain good application performance.

* [Query throughput](#query-throughput)
* [Query latency and errors](#query-performance)
* [Disk queue depth](#disk-i/o-metrics)
* [Client connections and errors](#connection-metrics)

[Part 2][part-2] of this series provides instructions for collecting all the metrics you need from CloudWatch and from the Aurora instance itself.

この記事では、我々はあなたがアマゾンオーロラのパフォーマンス上のタブを保つために監視する必要があり、最も重要なメトリックを検討しています。あなただけのオーロラの使用を開始している場合は、以下に示す評価指標を監視することは、あなたのデータベースのアクティビティとパフォーマンスに優れた洞察力を与えるだろう。彼らはまた、あなたのインスタンスタイプをアップグレードするか、優れたアプリケーションのパフォーマンスを維持するために、リードレプリカを追加する必要があるときに識別するのに役立ちます。

* [クエリのスループット]（＃クエリスループット）
* [クエリの待ち時間とエラー]（＃クエリ・パフォーマンス）
* [ディスクキューの深さ]（＃ディスクI / O-メトリクス）
* [クライアント接続とエラー]（＃接続-メトリクス）

[パート2]この一連のあなたがCloudWatchのからとオーロラインスタンス自体から必要なすべてのメトリックを収集するための手順を説明します[-2パート]。


- - -

*Source Markdown for this post is available [on GitHub][markdown]. Questions, corrections, additions, etc.? Please [let us know][issues].*


[part-2]: https://www.datadoghq.com/blog/how-to-collect-aurora-metrics
[part-3]: https://www.datadoghq.com/blog/monitor-aurora-using-datadog
[aurora]: https://aws.amazon.com/rds/aurora/
[metric-101]: https://www.datadoghq.com/blog/monitoring-101-collecting-data/
[performance-schema]: https://dev.mysql.com/doc/refman/5.6/en/performance-schema.html
[buffer-pool]: https://dev.mysql.com/doc/refman/5.6/en/innodb-buffer-pool.html
[query-cache]: https://dev.mysql.com/doc/refman/5.6/en/query-cache.html
[redis]: https://www.datadoghq.com/blog/how-to-monitor-redis-performance-metrics/
[sys-schema]: https://github.com/MarkLeith/mysql-sys/
[iops]: http://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html#USER_PIOPS.Realized
[storage]: http://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html#d0e9920
[slow-log]: http://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_LogAccess.Concepts.MySQL.html#USER_LogAccess.MySQL.Generallog
[connection-errors]: https://dev.mysql.com/doc/refman/5.6/en/server-status-variables.html#statvar_Connection_errors_xxx
[bottlenecks]: https://www.youtube.com/watch?v=t6Os_bBNJE0&t=16m12s
[working-set]: http://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html#CHAP_BestPractices.Performance.RAM
[investigation]: https://www.datadoghq.com/blog/monitoring-101-investigation/
[read-replica]: http://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Aurora.Replication.html
[mysql-book]: http://shop.oreilly.com/product/0636920022343.do
[markdown]: https://github.com/DataDog/the-monitor/blob/master/rds-aurora/monitoring_amazon_aurora_performance_metrics.md
[issues]: https://github.com/DataDog/the-monitor/issues
[collecting-data]: https://www.datadoghq.com/blog/monitoring-101-collecting-data/#work-metrics
[mysql-rds]: https://www.datadoghq.com/blog/monitoring-rds-mysql-performance-metrics/
[aurora-metrics]: http://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Aurora.Monitoring.html
