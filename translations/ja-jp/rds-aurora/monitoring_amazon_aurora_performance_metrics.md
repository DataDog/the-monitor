> *This post is part 1 of a 3-part series about monitoring the Aurora database service on Amazon RDS. [Part 2][part-2] is about collecting metrics from Aurora, and [Part 3][part-3] details how to monitor Aurora with Datadog.*

*このポストは、Amazon RDS上のAuroraデータベースの監視について解説した3回シリーズのPart 1です。[Part 2][part-2]では、Auroraからメトリクスを収集する方法を解説します。[Part 3][part-3]では、Datadogを使ってAuroraを監視する方法について解説します。*

## What is Aurora?

> [Amazon Aurora][aurora] is a MySQL-compatible database offered on RDS (Relational Database Service), a hosted database service in the AWS cloud. RDS users can choose from several well-known database engines that are also available as standalone products, including MySQL, Oracle, SQL Server, Postgres, and MariaDB, but Aurora is only available on RDS.

[Amazon Aurora][aurora]は、AWS上に構築されたRDS(リレーショナルデータベースサービス)上で提供されているMySQL互換のデータベースです。RDSユーザーは、MySQL、Oracle、SQL Server、Postgres、MariaDBを含む、スタンドアロン製品としても入手可能なデータベースからエンジンを選択することができます。しかしながら、Auroraは、RDS上でしか提供されていません。


> Aurora offers unique features such as auto-scaling storage, extremely low-latency replication, and rapid automated failover to a standby instance. Amazon advertises throughput enhancements of up to 5x as compared to MySQL running on similar hardware. Aurora users also have access to an expanded suite of [monitoring metrics][aurora-metrics] as compared to other RDS users. Aurora exposes not just system- and disk-level metrics but also crucial metrics on query throughput and latency, as detailed below.

Auroraは、自動的にスケールするストレージ、超低レイテンシのレプリケーション、スタンバイ・インスタンスへの迅速な自動フェイルオーバーなど、ユニークな機能を提供しています。Amazonは、同等のハードウェアの上で動作するMySQLに比べて5倍のスループットを持っているとも公表しています。Auroraのユーザーは、他のデータベースエンジンを使っているユーザーと比較して、多くの種類の[監視メトリクス][aurora-metrics]を、手に入れることができます。Aurora上では、`system-`や、 `disk-level`などのインスタンに関連したメトリクスだけではなく、以下に記載したようにスループットやレイテンシなのどきわめて重要なメトリクスも提供されています。


## Key metrics for Amazon Aurora

> To keep your applications running smoothly, it is important to understand and track performance metrics in the following areas:

> * [Query throughput](#query-throughput)
> * [Query performance](#query-performance)
> * [Resource utilization](#resource-utilization)
> * [Connections](#connection-metrics)
> * [Read replica metrics](#read-replica-metrics)

アプリケーションをスムーズの動作し続けるように維持するには、以下の各分野を理解し、パフォーマンス・メトリクスを追跡することが重要です。

* [クエリのスループット](#query-throughput)
* [クエリのパフォーマンス](#query-performance)
* [リソースの活用状況](#resource-utilization)
* [コネクション](#connection-metrics)
* [Read replica metrics](#read-replica-metrics)


> RDS exposes dozens of high-level metrics, and Aurora users can access literally hundreds more from the MySQL-compatible database engine. With so many metrics available, it's not always easy to tell what you should focus on. In this article we'll highlight key metrics in each of the above areas that together give you a detailed view of your database's performance.

RDSは、数十ものハイレベル・メトリクスを公開しています。そして、Auroraのユーザーは、MySQL互換のデータベースエンジンの数百以上のメトリクスにアクセスすることができます。そして、あまりにも多くのメトリクスを収集できるので、どのメトリクスに注目するべきかを判断するのに困ってしまいます。この記事では、データベースのパフォーマンスを詳しく把握する目的で、上記の各エリアのキーメトリクスに焦点をあてて解説していきます。


> RDS metrics (as opposed to storage engine metrics) are available through Amazon CloudWatch, and many are available regardless of which database engine you use. Engine metrics, on the other hand, can be accessed from the database instance itself. [Part 2 of this series][part-2] explains how to collect both types of metrics. CloudWatch Aurora metrics are available at one-minute intervals; database engine metrics can be collected at even higher resolution.

RDSメトリクスは、Amazon CloudWatchを経由して収集できます。そして、大半のRDSのメトリクスは、データベスエンジンの選択にに関わらず、集取することができます。一方で、データベース・エンジンのネーティブなメトリクスは、ベータベースのインスタンスから直接集取することができます。[このシリーズのPart 2][part-2]では、これらのメトリクスの収集の方法を解説します。CloudWatchを経由したAuroraのRDSメトリクスは、1分間隔で収集することができます。データベース・エンジンからのネイティブメトリクスは、更に高い解像度で集取することができます。


> This article references metric terminology introduced in [our Monitoring 101 series][metric-101], which provides a framework for metric collection and alerting.

この記事では、[Monitoring 101 series][metric-101]内の”メトリクスの収集とアラートのフレームワーク”で解説した用語を採用しています。


### Compatibility with MySQL and MariaDB

> Because Aurora is compatible with MySQL 5.6, standard MySQL administration and monitoring tools, such as the `mysql` command line interface, will generally work with Aurora without modification. And most of the strategies outlined here also apply to MySQL and MariaDB on RDS. But there are some key differences between the database engines. For instance, Aurora has auto-scaling storage, so it does not expose a metric tracking free storage space. And the version of MariaDB (10.0.17) available on RDS at the time of this writing is not fully compatible with some of the metric collection tools detailed in [Part 2][part-2] of this series. MySQL users should check out our three-part series on [monitoring MySQL on RDS][mysql-rds].

基本的にAuroraは、MySQL 5.6と互換性があります。従って、`mysql`から始まるCLIなど、標準的なMySQLの管理ツールや監視ツールは、Auroraでも変更なしで使うことができます。更に、ここで解説している監視の戦略の多くは、RDS上のMySQLやMariaDBにも適用することができるはずです。しかし、各データベース・エンジンには、いくつかの重要な違いあるのも認識しておく必要があります。例えば、Auroraでは、ストレージが自動的にスケールするので、ストレージの空き容量に関するメトリクスを提供していません。更にこの記事を書いている時点で、RDS上で使うことのできるMariaDBのバージョン(10.0.17)は、MySQLのワークベンチツールやsys schemaと完全に互換していません。これらの状況については、このシリーズの[Part 2][part-2]で詳しく解説することにします。又、RDS上でMySQLを採用しているなら、[monitoring MySQL on RDS][mysql-rds]の3回シリーズも併せ参照すると良いかもしれません。


<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-11-aurora/aurora-ootb-dash-2.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-11-aurora/aurora-ootb-dash-2.png"></a>

<!--<h3 class="anchor" id="query-throughput">Query throughput</h3>-->

### <a class="anchor" id="query-throughput"></a>Query throughput

| **Metric description** | **CloudWatch name** | **MySQL name** | [**Metric&nbsp;type**][metric-101] |
|:----------------------:|:-------------------:|:--------------:|:-------------|
| Queries | Queries (per second) | Queries (count) | Work: Throughput |
| Reads | SelectThroughput (per second) | Com\_select + Qcache\_hits (count) | Work: Throughput |
| Writes | DMLThroughput (per second) | Com\_insert + Com\_update + Com\_delete (count) | Work: Throughput |

> Your primary concern in monitoring any system is making sure that its [work is being done][collecting-data] effectively. A database's work is running queries, so the first priority in any monitoring strategy should be making sure that queries are being executed.

システムを監視する場合に、最も注目するべきことは、["仕事"が効率的に処理されている][collecting-data]ことを確認することです。データベースの"仕事"は、クエリを実行することです。従って、データベースの監視戦略の上で最優先事項は、クエリが実行されていることを確認することになります。


> You can also monitor the breakdown of read and write commands to better understand your database's read/write balance and identify potential bottlenecks. Those metrics can be collected directly from Amazon CloudWatch or computed by summing native MySQL metrics from the database engine. In MySQL metrics, reads increment one of two status variables, depending on whether or not the read is served from the query cache:

又、データベースの読み取り/書き込みのバランスを理解し潜在的なボトルネックを特定するため、読み取りと書き込みコマンドの内訳を監視することもできます。これらのメトリクスは、Amazon CloudWatchのから直接収集したり、データベース・エンジンから直接集取したMySQLのメトリックを計算することで収集することができます。 MySQLからのメトリクスの場合、読み込みの実行は、クエリキャッシュから読み込めているか否かに応じて、`Com_select`か`Qcache_hits`のどちらかのステータス変数に加算されいきます:


Reads = `Com_select` + `Qcache_hits`

> Writes increment one of three status variables, depending on the command:

書き込みは、コマンドの内容に応じ`Com_insert`, `Com_update`, `Com_delete`のステータス変数に加算されていきます:


    Writes = `Com_insert` + `Com_update` + `Com_delete`

> In CloudWatch metrics, all DML requests (inserts, updates, and deletes) are rolled into the `DMLThroughput` metric, and all `SELECT` statements are incorporated in the `SelectThroughput` metric, whether or not the query is served from the query cache.

CloudWatchのメトリクスの場合、すべてのDMLリクエスト(inserts, updates, deletes)は、`DMLThroughput`メトリクスにまとめられます。更に、クエリへの応答がクエリキャッシュから来ていたとしても、すべての`SELECT`文は、`SelectThroughput`メトリクスにまとめられます。


#### Metric to alert on: Queries per second

> The current rate of queries will naturally rise and fall, and as such is not always an actionable metric based on fixed thresholds alone. But it is worthwhile to alert on sudden changes in query volume—drastic drops in throughput, especially, can indicate a serious problem.

クエリの実行レートは、当然ながら変動します。そして、固定された閾値のみでは、アクションを起こすための十分なメトリクス監視とはいいがたいでしょう。そこで、クエリの量の突然の変化には、アラートを設定しておくとよいでしょう。特に、スループットの急激な低下は、深刻な問題を提起していることがあるので注意しましょう。


<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-11-aurora/questions_2.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-11-aurora/questions_2.png"></a>

<!--<h3 class="anchor" id="query-performance">Query performance</h3>-->

### <a class="anchor" id="query-performance"></a>Query performance

| **Metric description** | **CloudWatch name** | **MySQL name** | [**Metric&nbsp;type**][metric-101] |
|:----------------------:|:-------------------:|:--------------:|:-------------|
| Read query latency, in milliseconds | SelectLatency | - | Work: Performance |
| Write query latency, in milliseconds | DMLLatency | - | Work: Performance |
| Queries exceeding `long_query_time` limit | - | Slow_queries | Work: Performance |
| Query errors | - | (Only available via database query) | Work: Error |

> The Aurora-only metrics for `SELECT` latency and DML (insert, update, or delete) latency capture a critical measure of query performance. Along with query volume, latency should be among the top metrics monitored for almost any use case.

Auroraにのみある、`SELECT`レイテンシとDMLレイテンシのメトリクスは、クエリのパフォーマンスを測るうえできわめて重要なメトリクスです。それらに加え、クエリのボリュームと共にレイテンシは、ほとんど全てのユースケースで監視されているべき項目になります。


> MySQL (and therefore Aurora) also features a `Slow_queries` metric, which increments every time a query's execution time exceeds the number of seconds specified by the `long_query_time` parameter. To modify `long_query_time` (or any other database parameter), simply log in to the AWS Console, navigate to the RDS Dashboard, and select the parameter group that your RDS instance belongs to. You can then filter to find the parameter you want to edit.

MySQL(そしてAuroraも)は、`Slow_queries`というメトリクスを公開しています。このクエリは、`long_query_time`パラメータで指定した秒数を越える度に増加していきます。デフォルトで`long_query_time`は、10秒に設定されていますが、AWSコンソール上で変更することができます。`long_query_time`（または他のMySQLパラメータ）を変更するには、AWSコンソールにログインし、RDSのダッシュボードに移動し、RDSインスタンスが属するパラメータグループを選択します。次に、編集したいパラメータを検索します。


<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-11-aurora/parameter-groups.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-11-aurora/parameter-groups.png"></a>

> For a deeper look into query performance, the MySQL [performance schema][performance-schema] (which is compatible with Aurora but is disabled by default) also stores valuable statistics, including query latency, from the database server. Though you can query the performance schema directly, it is easier to use Mark Leith’s [sys schema][sys-schema], which provides convenient views, functions, and procedures to gather metrics from MySQL or Aurora. For instance, to find the execution time of all the different statement types executed by each user:

クエリのパフォーマンスを更に深く検証したい場合は、MySQLのperformance schema(Auroraと互換性があり、基本では無効になっています)を使います。performance schemaには、クエリのレイテンシなど、データベースの貴重な統計情報が保存されています。performance schemaへは、直にアクセスすることはできますが、Mark Leith氏が公開している[sys schema][sys-schema]を使う方が簡単です。このsys schemaは、MySQLからメトリクスを収集する際に、便利なビュー、関数、および手順を提供してくれます。例えば、ユーザー毎に異なるタイプのステートメントの実行時間を知りたい場合:


<pre class="lang:mysql">
mysql> select * from sys.user_summary_by_statement_type;
</pre>

> Or, to find the slowest statements (those in the 95th percentile by runtime):

又は、最も遅いステートメントを見つけることもできます(ランタイムによる95パーセンタイル値):


<pre class="lang:mysql">
mysql> select * from sys.statements_with_runtimes_in_95th_percentile\G
</pre>

> Many useful usage examples are detailed in the sys schema [documentation][sys-schema].

sys schemaの他の便利な使用例に関しては、[ドキュメント][sys-schema]を参照してください。


> To enable the performance schema, you must set the `performance_schema` parameter to 1 in the database instance's parameter group using the AWS console. If not enabled, this change requires an instance reboot. More about enabling the performance schema and installing the sys schema in [Part 2][part-2] of this series.

performance schemaを有効にするには、AWSコンソールから、そのデータベース・インスタンスのパラメータグループに対する`performance_schema`パラメータの値を1に設定する必要があります。無効になっていた場合に設定を反映するためには、インスタンスを再起動する必要があります。performance schemの有効活用とsys schemaのインストールに関しては、このシリーズの[Part 2][part-2]で解説します。


> The performance schema and sys schema also allow you to quickly assess how many queries generated errors or warnings:

performance schemaおよびsys schemaを活用すると、エラーや警告の発生状況を素早く確認することもできます:


<pre class="lang:mysql">
mysql> SELECT SUM(errors) FROM sys.statements_with_errors_or_warnings;
</pre>

#### Metrics to alert on

> * Latency: Slow reads or writes will necessarily add latency to any application that relies on Aurora. If your queries are executing more slowly than expected, evaluate your RDS [resource metrics](#resource-utilization). Aurora users also have a number of caching options to expedite transactions, from making more RAM available for the [buffer pool][buffer-pool] used by InnoDB (usually by upgrading to a larger instance), to enabling or expanding the [query cache][query-cache] that serves identical queries from memory, to using an application-level cache such as Memcached or [Redis][redis].


* Latency: 遅い読み取り又は書き込みは、Auroraに依存しているアプリケーションのレイテンシ値を大きくします。もしもクエリの実行に予想していたよりも長い時間がかかっている状態では、RDSの[リソースメトリクス](#resource-utilization)を検証するとよいでしょう。そして、Auroraのユーザーには、トランスアクションをスピードアップするための幾つかのキャッシュオプションが用意されています。InnoDBが使っている[buffer pool][buffer-pool]により多くのRAMを用意する(通常は、インスタンスのサイズを大きくします)、同一内容のクエリをメモリーで処理するために、 [クエリ用のキャッシュ][query-cache]を準備したり拡張したりする、Memcached や [Redis][redis]などのアプリケーション・レベルのキャッシュを使用するなどがあります。


> * `Slow_queries`: How you define a slow query (and therefore how you configure the `long_query_time` parameter) will depend heavily on your use case and performance requirements. If the number of slow queries reaches worrisome levels, you will likely want to identify the actual queries that are executing slowly so you can optimize them. You can do this by querying the sys schema or by configuring Aurora to log all slow queries. More information on enabling and accessing the slow query log is available [in the RDS documentation][slow-log].

* `Slow_queries`: どのようにスロークエリを定義するか(そして、`long_query_tim`のパラメータ値)は、ユースケースと性能要求に大きく依存しています。スロークエリの数が気になるレベルに達した場合、最適化をするために、実際に処理に時間の掛かっているそれらのクエリを特定したくなることでしょう。この特定は、sys schemaにクエリを送信するか、スロークエリログを記録する設定をMySQLに施すことにより実現することができます。スロークエリログの有効化とアクセスの方法についての詳しい情報については、[RDSのドキュメント][slow-log]を参照してください。<pre class="lang:mysql">mysql> SELECT * FROM mysql.slow_log LIMIT 10\G
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

> * Query errors: A sudden increase in query errors can indicate a problem with your client application or your database. You can use the sys schema to quickly explore which queries may be causing problems. For instance, to list the 10 normalized statements that have returned the most errors:

* Query errors: クエリエラーの急激な増加は、クライアントアプリまたはデータベースに問題があることを暗示ていることがあります。このようなケースでは、sys schemaを使って、どのクエリが問題を起こしているかを調べることができます。例えば以下では、エラーを返している量の多い正規化ステートメントの上位10個のリストが取得できます:


	<pre class="lang:mysql">mysql> SELECT * FROM sys.statements_with_errors_or_warnings ORDER BY errors DESC LIMIT 10\G</pre>

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

> As Baron Schwartz, co-author of *[High Performance MySQL][mysql-book],* often notes, a database needs four fundamental resources: CPU, memory, disk, and network. Any of these can become a performance bottleneck—for a look at how difference RDS instance types can be constrained by their available resources, check out [this 2013 talk][bottlenecks] by Amazon's Grant McAlister.

*[High Performance MySQL][mysql-book]*の共著者のBaron Schwartz氏は、しばしば、次のように指摘してます。ベータベースには、４つの基本的なリソースが必要です: それらは、CPU、メモリ、ディスク、ネットワークです。これらのどれもが、ボトルネックになる可能性を持っています。RDSインスタンスタイプのリソースの差異による制約(ボトルネックの状況)の詳細に関しては、AmazonのGrant McAlister氏による[2013年のプレゼンテーション][bottlenecks]を、是非参照してください。


> Whenever your database instance experiences performance problems, you should check metrics pertaining to the four fundamental resources to look for bottlenecks. Though you cannot access the full suite of system-level metrics that are available for EC2, CloudWatch does make available metrics on all four of these resources. For the most part, these metrics are most useful for [investigating (rather than detecting)][investigation] performance issues.

データベース・インスタンスにパフォーマンス問題が発生した場合、ボトルネックの原因を見つけ出すために、先の4つの基本メトリクスのどれによって制約を受けているかを確認する必要があります。EC2で収集可能なシステムレベルのメトリクスのように全のメトリクスにはアクセスすることはできませんが、CloudWatch上には、これらの4つの基本的メトリクスが公開されています。そして大抵の場合、これらのメトリクスは、パフォーマンス問題を検知するというよりは、ボトルネックの原因を調査する際に最も活用できます。

<!--<h4 class="anchor" id="disk-i/o-metrics">Disk I/O metrics</h4>-->

#### <a class="anchor" id="disk-i/o-metrics"></a>Disk I/O metrics

> CloudWatch makes available RDS metrics on read and write IOPS, which indicate how much your database is interacting with backing storage. If your storage volumes cannot keep pace with the volume of read and write requests, you will start to see I/O operations queuing up. The `DiskQueueDepth` metric measures the length of this queue at any given moment.

CloudWatch上では、RDSメトリクスとして、データベースがバッキングストレージが、どこ程度連動して動いているかを示すために、読み取りと書き込みのIOPSを公開しています。お使いのストレージボリュームが、読み取りおよび書き込みリクエストの発生量にペースを保つことができない場合は、I/Oの操作はキューに溜まっていきます。`DiskQueueDepth`メトリクスは、特定タイミングのこのキューの長さを計測します。

RDSメトリクスとして

> Note that there will not be a one-to-one correspondence between queries and disk operations—queries that can be served from memory will bypass disk, for instance, and queries that return a large amount of data can involve more than one I/O operation.

クエリの量とディスク操作の量には、1対1の関係にはありません。メモリーからクエリの結果を提供することができる場合は、ディスクへのアクセスはバイパスされます。更に、大量のデータを返すクエリでは、複数のI/Oの操作に関係しています。


> In addition to I/O throughput metrics, RDS offers `ReadLatency` and `WriteLatency` metrics. These metrics do not capture full query latency—they only measure how long your I/O operations are taking at the disk level.

I/Oスループットに関するメトリクスに加えて、RDSは`ReadLatency`と`WriteLatency`のメトリクスを提供しています。これらのメトリクスは、クエリの完全なレイテンシを計測していません。これらのメトリクスは、ディスクレベルでのI/Oの操作にどれくらいの時間が掛かっているかを計測しています。


> For read-heavy applications, one way to overcome I/O limitations is to [create a read replica][read-replica] of the database to serve some of the client read requests. Aurora allows you to create up to 15 replicas for every primary instance. For more, see the [section below](#read-replica-metrics) on metrics for read replicas.

ベータベースからの読み取りが多いアプリで、I/Oの制限を克服する一つの方法は、クライアントの読み込みリクエストを処理するための[読み込み用のレプリカ(複製)を作る][read-replica]ことです。Auroraは、プライマリーインスタンス1台毎に、15台のレプリカを作成できるようになっています。尚、読み取りレプリカのメトリクスの詳細については、[以下のセクション](#read-replica-metrics)を参照してください。


#### CPU metrics

> High CPU utilization is not necessarily a bad sign. But if your database is performing poorly while metrics for IOPS and network are in normal ranges, and while the instance appears to have sufficient memory, the CPUs of your chosen instance type may be the bottleneck.

高いCPUの利用率は、必ずしも悪いこと兆候ではありません。しかし、IOPSとネットワークが制限値以内にあり、メモリーも十分に確保できている状態では、選択しているインスタンスのCPUがボトルネックになっているかもしれません。


#### Memory metrics

> Databases perform best when most of the working set of data can be held in memory. For this reason, you should monitor `FreeableMemory` to ensure that your database instance is not memory-constrained. AWS advises that you use the ReadIOPS metric to determine whether the working set is largely in memory:

> > To tell if your working set is almost all in memory, check the ReadIOPS metric (using AWS CloudWatch) while the DB instance is under load. The value of ReadIOPS should be small and stable.

データベースは、処理をしているデータの全てがメモリー内に保持されている場合、最高の性能を発揮します。このような理由から、データベースがメモリーから制約を受けていないことを確認するために、`FreeableMemory`を監視する必要があります。AWSでは、必要なデータの大半がメモリー内にロードできているかを判断するのにReadIOPSメトリクスを使うことを推奨しています:

> 必要なでーたーがメモリ内のほぼ全てロードされているかを判断するためには、データベースインスタンスに負荷の掛かっている状態で、AWS CloudWatch経由で、ReadIOPSメトリクスをチェックします。ReadIOPSの値は、小さく、安定している必要があります。


#### Network metrics
> Unlike other RDS database engines, Aurora's network throughput metrics do not include network traffic from the database instances to the storage volumes. The `NetworkReceiveThroughput` and `NetworkTransmitThroughput` metrics therefore track only network traffic to and from clients.

RDS上の他のデータベースエンジンとは異なり、Auroraのネットワーク・スループットのメトリクスは、ストレージボリュームとデータベースインスタンス間のネットワーク・トラフィックが含まれていません。そのため、`NetworkReceiveThroughput`メトリクスと`NetworkTransmitThroughput`メトリクスは、クライアントとデータベースのインスタンスクラスタ間のネットワークトラフィックのみを計測しています。


#### Metrics to alert on

> * `DiskQueueDepth`: It is not unusual to have some requests in the disk queue, but investigation may be in order if this metric starts to climb, especially if latency increases as a result. (Time spent in the disk queue adds to read and write latency.)

- `DiskQueueDepth`： ディスクキューにリクエストが溜まっていることは珍しくありません。しかし、このメトリクスに増加の傾向があるなら、調査が必要です。特に、このディスクキューの増加によってレイテンシが増加しているなら、調査は必要です。(ディスクキュー内で順番を待っている時間は、読み取りや書き込みレイテンシに加算されていきます。)

<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-11-aurora/disk-queue.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-11-aurora/disk-queue.png"></a>

<!--<h3 class="anchor" id="connection-metrics">Connection metrics</h3>-->

### <a class="anchor" id="connection-metrics"></a>Connection metrics

| **Metric description** | **CloudWatch name** | **MySQL name** | [**Metric&nbsp;type**][metric-101] |
|:----------------------:|:-------------------:|:--------------:|:-------------|
| Open database connections | DatabaseConnections | Threads\_connected | Resource: Utilization |
| Currently running connections | - | Threads\_running | Resource: Utilization |
| Failed connection attempts | LoginFailures (per second) | Aborted\_connects (count) | Resource: Error |
| Count of connections refused due to server error | - | Connection\_errors\_<br>internal | Resource: Error |
| Count of connections refused due to `max_connections` limit | - | Connection\_errors\_<br>max_connections | Resource: Error |

> Monitoring how many client connections are in use is critical to understanding your database's activity and capacity. Aurora has a configurable connection limit; the default value depends on the memory of the database's instance class in bytes, according to the formula:

ベータベースの処理状況や処理能力を理解するためには、クライアント接続の数を把握しておくことは重要です。Auroraには、このコネクション数の制限を設定する機能があります。尚、RDSのデフォルト値は、データベースのインスタンスクラスが持っているメモリー容量をベースに、以下の様な計算式になります:


`log(DBInstanceClassMemory/8187281408)*1000`

> The `max_connections` parameter can be checked or modified via the database instance's parameter group using the RDS dashboard in the AWS console. You can also check the current value of `max_connections` by querying the Aurora instance itself (see [part 2][part-2] of this series for more on connecting to RDS instances directly):

MAX_CONNECTIONSパラメータがオンまたはAWSコンソールでRDSのダッシュボードを使用して、データベース・インスタンスのパラメータ群を経由して変更することができます。また、Auroraのインスタンス自体を（直接インスタンスをRDSへの接続の詳細については、このシリーズのパート2を参照）照会することにより、MAX_CONNECTIONSの現在の値を確認することができます。

`max_connections`パラメータは、AWSのコンソールのRDSダッシュボードから、データベース・インスタンスのパラメータグループを編集することで有効化や変更できます。又、`max_connections`の値は、Auroraインスタンスに直接問い合わせることで確認することもできます。(RDSインスタンに直接接続し情報を集取する方法は、このシリーズの[Part 2][part-2]を参照してください。)


<pre class="lang:mysql">
mysql> SELECT @@max_connections;
+-------------------+
| @@max_connections |
+-------------------+
|              1000 |
+-------------------+
1 row in set (0.00 sec)
</pre>

> To monitor how many connections are in use, CloudWatch exposes a `DatabaseConnections` metric tracking open connections, and the database engine exposes a similar `Threads_connected` metric. The `Threads_running` metric provides additional visibility by isolating the threads that are actively processing queries.

使用中のコネクション数を監視するには、次の方法があります。CloudWatchは、`DatabaseConnections`メトリクスという使用中のRDSコネクション数を公開しています。データベースエンジンは、類似のメトリクスとして`Threads_connected`(コネクションスレッドの数)を公開しています。更に、活発にクエリを処理しているスレッドを識別するためには、`Threads_running`メトリクスも公開しています。


> If your server reaches the `max_connections` limit and starts to refuse connections, `Connection_errors_max_connections` will be incremented, as will the `Aborted_connects` metric tracking all failed connection attempts. CloudWatch also tracks failed connections via the `LoginFailures` metric.

もしもサーバーが、`max_connections`の制限値に達し、新しいコネクションを受け入れなくなった場合、`Connection_errors_max_connections`と、接続の試みの全ての失敗を追跡している`Aborted_connects`が加算されていきます。更に、CloudWatchには、コネクションの失敗を計測している`LoginFailures`というメトリクスもあります。


> Aurora's database engine exposes a variety of other metrics on connection errors, which can help you identify client issues as well as serious issues with the database instance itself. The metric `Connection_errors_internal` is a good one to watch, because it is incremented when the error comes from the server itself. Internal errors can reflect an out-of-memory condition or the server's inability to start a new thread.

Auroraのデータベースエンジンは、コネクションエラーに関し、様々なメトリクスを公開しています。これらのメトリクスは、クライアントの問題を識別したり、ベータベースインスタンス自体の深刻な問題を識別するのに役立ちます。`Connection_errors_internal`メトリクスは、コネクションエラーがサーバー側で発生している際に加算されるので、把握しておく必要のあるメトリクスです。このインターナルエラーは、メモリーが不足している状態か、サーバーが新しいスレッドを開始できない状況を反映しています。


#### Metrics to alert on

> * Open database connections: If a client attempts to connect to Aurora when all available connections are in use, Aurora will return a "Too many connections" error and increment `Connection_errors_max_connections`. To prevent this scenario, you should monitor the number of open connections and make sure that it remains safely below the configured limit.

* Open database connections: 利用可能なすべてのコネクションに接続が発生している際に、クライアントがAuroraに接続しようとすると、Auroraは、"Too many connections"エラーを返し、`Connection_errors_max_connections`が、加算されます。このシナリオを回避するためには、使っているコネクションの数を監視し、`max_connections`の制限に掛からないようにコントロールする必要があります。

> * Failed connection attempts: If this metric is increasing, your clients are probably trying and failing to connect to the database. Dig deeper with metrics such as `Connection_errors_max_connections` and `Connection_errors_internal` to diagnose the problem.

* Failed connection attempts: この数が増加している場合、クライアントは、データベースの接続しようとして失敗している状況でしょう。 接続に失敗している原因を診断するために、`Connection_errors_max_connections`や`Connection_errors_internal`のようなメトリクスを使って調査をすすめます。


<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-mysql-rds/threads_connected_2.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-mysql-rds/threads_connected_2.png"></a>

<!--<h3 class="anchor" id="read-replica-metrics">Read replica metrics</h3>-->

<a class="anchor" id="read-replica-metrics"></a>Read replica metrics

| **Name** | **Description** | [**Metric&nbsp;type**][metric-101] | **Availability** |
|:--------:|:---------------:|:---------------:|:------------:|
| AuroraReplicaLag | Number of milliseconds by which replica trails primary instance | Other | CloudWatch |

> Aurora supports the creation of up to 15 read replicas from the master instance. These replicas are assigned a separate endpoint, so you can point client applications to read from a replica rather than from the source instance. You can also monitor the replica's connections, throughput, and query performance, just as you would for an ordinary RDS instance.

Auroraは、マスターインスタンに対し、最大15のリードレプリカの作成をサポートします。これらのレプリカには異なるエンドポイントが割り振られています。従って、マスターになっているインスタンスではなくレプリカから読み取ることができるようにクライアントアプリを設定し直すこともできます。更に、一般的なRDSインスタンスを監視するのと同じように、レプリカのスループットやクエリパフォーマンスも監視することができます。

> The lag time for any read replica is captured by the CloudWatch metric `AuroraReplicaLag`. This metric is usually not actionable, although if the lag is consistently very long, you should investigate your settings and resource usage.

読み込みレプリカの遅延時間は、CloudWatchメトリクスの`ReplicaLag`で収集することができます。一般的は、このメトリクスに対してアクションを起こすことは有りませんが、もしも遅延時間が一貫して非常に長い場合は、設定やリソースの使用状況を再度見直す必要があるでしょう。


> Note that this is a significantly different metric than the generic RDS metric `ReplicaLag`, which applies to other database engines. Because Aurora instances all read from the same virtual storage volume, the `AuroraReplicaLag` tracks the lag in page cache updates from primary to replica rather than the lag in applying all write operations from the primary instance to the replica.

Auroraを使っている場合、RDSメトリクスの`ReplicaLag`は、他のデータベースエンジンで収集しているモノと著しく異なっていることを理解しておくべ気でしょう。Auroraのインスタンスは、皆、同じ仮想ストレージボリュームから読み込むため、`AuroraReplicaLag`は、プライマリ・インスタンスからレプリカ・インスタンスへの書き込み操作の全が完了するまでの遅延ではなく、プライマリからレプリカへのページキャッシュの更新の遅延を計測しています。


<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-11-aurora/replica-lag.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-11-aurora/replica-lag.png"></a>

## Conclusion

> In this post we have explored the most important metrics you should monitor to keep tabs on performance for Amazon Aurora. If you are just getting started with Aurora, monitoring the metrics listed below will give you great insight into your database’s activity and performance. They will also help you to identify when it is necessary to upgrade your instance type or add read replicas to maintain good application performance.

> * [Query throughput](#query-throughput)
> * [Query latency and errors](#query-performance)
> * [Disk queue depth](#disk-i/o-metrics)
> * [Client connections and errors](#connection-metrics)

この記事では、Auroraのパフォーマンスを管理するために監視の必要なメトリクスを検討してきました。もしもあなたが、Auroraを使い始めたばかりなら、以下にリストたメトリクスは、データベースのアクティビティーとパフォーマンスについて優れた洞察を与えてくれるでしょう。又、それらは、アプリの優れたパフォーマンスを維持するために、インスタンスのアップグレードが必要なタイミングや、読み込み用のレプリカの追加のタイミングを判断する指標を与えてくれるでしょう。

* [クエリのスループット](#query-throughput)
* [クエリのパフォーマンス](#query-performance)
* [リソースの活用状況](#resource-utilization)
* [コネクション](#connection-metrics)
* [Read replica metrics](#read-replica-metrics)


> [Part 2][part-2] of this series provides instructions for collecting all the metrics you need from CloudWatch and from the Aurora instance itself.

このシリーズの[Part 2][part-2] では、CloudWatchとAuroraのインスタンスから必要な全てのメトリクスを収集する手順を解説していきます。


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
