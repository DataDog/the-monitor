# Monitoring RDS MySQL performance metrics

> *This post is part 1 of a 3-part series about monitoring MySQL on Amazon RDS. [Part 2][part-2] is about collecting metrics from both RDS and MySQL, and [Part 3][part-3] details how to monitor MySQL on RDS with Datadog.*

*このポストは、Amazon RDSの上にあるMySQの監視に関する3回シリーズのポストのPart 1です。[Part 2][Part 2]は、”RDS とMySQLからどのようにしてデータを収集するか”を解説しています。[Part 3]では、”Datadogを使ってAmazon RDSの上にあるMySQをどのように監視するか”を解説します。*


## What is RDS?

> Amazon Relational Database Service (RDS) is a hosted database service in the AWS cloud. RDS users can choose from several relational database engines, including MySQL, Oracle, SQL Server, Postgres, MariaDB, and Amazon Aurora, a new MySQL-compatible database built for RDS. This article focuses on the original RDS database engine: MySQL. 

Amazon Relational Database Service (Amazon RDS)は、AWSのクラウド上で提供されているデータベースサービスです。RDSのユーザーは、MySQL, Oracle, SQL Server, Postgres, MariaDB, and Amazon Aurora, そして新しくRDSのために開発したMySQL互換のデータベースからデータベースエンジンを選ぶことができます。今回の記事では、RDSのオリジナルデータベースエンジンであるMySQLにフォーカスして話を進めることにします。


## Key metrics for MySQL on RDS

> To keep your applications running smoothly, it is important to understand and track performance metrics in the following areas:

> * [Query throughput](#query-throughput)
> * [Query performance](#query-performance)
> * [Resource utilization](#resource-utilization)
> * [Connections](#connection-metrics)
> * [Read replica metrics](#read-replica-metrics)

スムーズに動作しているアプリケーションを維持するために、以下の各分野を理解し、パフォーマンス・メトリクスを追跡することが重要です。

* [クエリーのスループット](#query-throughput)
* [クエリーのパフォーマンス](#query-performance)
* [リソースの活用状況](#resource-utilization)
* [コネクション](#connection-metrics)
* [Read replica metrics](#read-replica-metrics)

> Users of MySQL on RDS have access to hundreds of metrics, but it's not always easy to tell what you should focus on. In this article we'll highlight key metrics in each of the above areas that together give you a detailed view of your database's performance. 

RDS上のMySQLのユーザーは、数百ものメトリクスにアクセスできるようになっています。しかし、どのメトリクスにフォーカスするべきかを見つけ出すのは簡単なことではありません。この記事では、先に示した分野毎にキーメトリクスを紹介し、全体としてあなたのデーターベースのパフォーマンスの詳細が読み取れるようにしていきます。


> RDS metrics (as opposed to MySQL metrics) are available through Amazon CloudWatch, and are available regardless of which database engine you use. MySQL metrics, on the other hand, must be accessed from the database instance itself. [Part 2 of this series][part-2] explains how to collect both types of metrics. 

RDSのメトリクス(MySQLのメトリクスとは対照的に)は、使用しているデータベースエンジンに関係なく、Amazon CloudWatchを介して集取することができます。その逆に、MySQLのメトリクスは、データベースインスタンス自体に直接アクセスする必要があります。[このシリーズのPart 2][part-2]では、これらの両方のタイプのメトリクスを収集する方法について解説します。


> Most of the performance metrics outlined here also apply to Aurora and MariaDB on RDS, but there are some key differences between the database engines. For instance, Aurora has auto-scaling storage and therefore does not expose a metric tracking free storage space. And the version of MariaDB (10.0.17) available on RDS at the time of this writing is not fully compatible with the MySQL Workbench tool or the sys schema, both of which are detailed in [Part 2][part-2] of this series.

ここで概説するパフォーマンス・メトリックのほとんどは、RDS上のAuroraやMariaDBに適用することができます。しかしデータベースエンジン間で、重要な幾つかの違いあるのも認識しておく必要があります。例えば、Auroraでは、ストレージが自動的にスケールするので、ストレージの空き容量を提供していません。更にこの記事を書いている時点で、RDSで使うことのできるMariaDBのバージョン(10.0.17)は、MySQLのワークベンチツールまたはSYSスキーマと完全互換ではありません。このことについては、このシリーズの[Part 2][part-2]で詳しく解説することにします。


> This article references metric terminology introduced in [our Monitoring 101 series][metric-101], which provides a framework for metric collection and alerting.

この記事では、[Monitoring 101 series][metric-101]で紹介した”メトリクスの収集とアラートのフレームワーク”で解説した用語を採用しています。


<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/rds-dash-load.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/rds-dash-load.png"></a> 

<h3 class="anchor" id="query-throughput">Query throughput</h3>

| **Name** | **Description** | [**Metric&nbsp;type**][metric-101] | **Availability** |
|:--------:|:---------------:|:---------------:|:------------:|
| Questions | Count of executed statements (sent by client only) | Work: Throughput | MySQL |
| Queries | Count of executed statements (sent by client or executed within stored programs) | Work: Throughput | MySQL | 
| Reads (calculated) | Selects + Query cache hits | Work: Throughput | MySQL |
| Writes (calculated) | Inserts + Updates + Deletes | Work: Throughput | MySQL |

> Your primary concern in monitoring any system is making sure that its [work is being done][collecting-data] effectively. A database's work is running queries, so the first priority in any monitoring strategy should be making sure that queries are being executed.

システムを監視する場合最も注目するべきことは、["仕事"が効率的に処理されている][collecting-data]ことを確認することです。データベースの"仕事"は、クエリを実行することです。従って、データベースの監視戦略の上での最優先事項は、クエリーが実行されていることに確認することになります。


> The MySQL server status variable `Questions` is incremented for all statements sent by client applications. The similar metric `Queries` is a more all-encompassing count that includes statements executed as part of [stored programs][stored], as well as commands such as `PREPARE` and `DEALLOCATE PREPARE`, which are run as part of server-side [prepared statements][prepared]. For most RDS deployments, the client-centric view makes `Questions` the more valuable metric.

MySQLサーバーの`Questions` ステータス変数は、クライアントアプリから送信されるステートメント毎に加算されていきます。同様のメトリクスの`Queries`では、[stored programs][stored]の一部として実行されたステートメントや、サーバーサイドの[prepared statements][prepared]として実行された`PREPARE`と`DEALLOCATE PREPARE`のコマンドなど、全てを網羅したカウント。RDSの多くの環境では、クライアントを中心とした視点ということで、`Questions`の方が価値のあるメトリクスといいうことになります。


> You can also monitor the breakdown of read and write commands to better understand your database's read/write balance and identify potential bottlenecks. Those metrics can be computed by summing native MySQL metrics. Reads increment one of two status variables, depending on whether or not the read is served from the query cache:

データベースの読み/書きバランスを理解し、潜在的なボトルネックを特定するために、読み取りおよび書き込みコマンドの内訳を監視することもできます。これらのメトリクスは、ネイティブのMySQLメトリクスを合計することによって求めることができます。

読み込みの実行は、クエリキャッシュから読み込めているか否かに応じて、`Com_select`か`Qcache_hits`のどちらかのステータス変数に加算されいきます:

    Reads = `Com_select` + `Qcache_hits`

> Writes increment one of three status variables, depending on the command:

書き込みは、コマンドの内容に応じ`Com_insert`, `Com_update`, `Com_delete`のステータス変数に加算されていきます:

    Writes = `Com_insert` + `Com_update` + `Com_delete`

#### Metric to alert on: Questions

> The current rate of queries will naturally rise and fall, and as such is not always an actionable metric based on fixed thresholds alone. But it is worthwhile to alert on sudden changes in query volume—drastic drops in throughput, especially, can indicate a serious problem.

クエリーの実効レートは、当然ながら増減します。そして、固定的な閾値のみを基準にした場合、価値のあるメトリクスとは言いがたいでしょう。しかし、スループットの急激な低下のようなクエリーの量の突然の変化には、深刻な問題を提起していることがあるので、アラートを設定しておく価値があるでしょう。


<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/questions_2.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/questions_2.png"></a> 
 

<h3 class="anchor" id="query-performance">Query performance</h3>

| **Name** | **Description** | [**Metric&nbsp;type**][metric-101] | **Availability** |
|:--------:|:---------------:|:---------------:|:------------:|
| Slow_queries | Number of queries exceeding configurable `long_query_time` limit | Work: Performance | MySQL |
| Query errors | Number of SQL statements that generated errors | Work: Error | MySQL* |

> _*The count of query errors is not exposed directly as a MySQL metric, but can be gathered by a MySQL query._

_*クエリーエラーの数は、MySQLメトリクスとして直接的には公開されていませんが、MySQLのクエリーを集計することで収集することができます。_


> Amazon's CloudWatch exposes `ReadLatency` and `WriteLatency` metrics for RDS (discussed [below](#resource-utilization)), but those metrics only latency at the disk I/O level. For a more holistic view of query performance, you can dive into native MySQL metrics for query latency. MySQL features a `Slow_queries` metric, which increments every time a query's execution time exceeds the number of seconds specified by the `long_query_time` parameter. `long_query_time` is set to 10 seconds by default but can be modified in the AWS Console. To modify  `long_query_time` (or any other MySQL parameter), simply log in to the Console, navigate to the RDS Dashboard, and select the parameter group that your RDS instance belongs to. You can then filter to find the parameter you want to edit.

Amazon CloudWatchは、RDSの`ReadLatency`と`WriteLatency`メトリクス（[後述](#resource-utilization)）を公開しています。しかし、これらのメトリクスは、ディスクI/Oレベルのレイテンシーを計測した値です。より包括的にクエリーのパフォーマンスを把握するには、MySQLのネオティブメトリクスのクエリーレイテンシーを使うことができます。MySQLには、`Slow_queries`というメトリクスを公開しています。このクエリーは、`long_query_time`パラメーターで指定した秒数を超える毎に増加していきます。デフォルトで`long_query_time`は、10秒に設定されていますが、AWSコンソール上で変更することができます。`long_query_time`（または他のMySQLパラメータ）を変更するには、AWSコンソールにログインし、RDSの舵手ボードに移動し、RDSインスタンスが属するパラメータグループを選択します。その後、編集したいパラメーターを検索します。


<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/long_query_time.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/long_query_time.png"></a> 

> MySQL's performance schema (when enabled) also stores valuable statistics, including query latency, from the database server. Though you can query the performance schema directly, it is easier to use Mark Leith’s [sys schema][sys-schema], which provides convenient views, functions, and procedures to gather metrics from MySQL. For instance, to find the execution time of all the different statement types executed by each user:

MySQLのパフォーマンススキーマ(有効化されている状態で)は、クエリーのレイテンシーなどのデータベースサーバーからの貴重な統計情報を記憶しています。パフォーマンススキーマーへは直接紹介することはできますが、Mark Leith氏の[sys schema][sys-schema]を使う方が簡単です。このソフトは、MySQLからメトリクスを収集する際に、便利なビュー、関数、および手順を提供してくれます。例えば、ユーザー毎の異なるステートメントタイプの実行時間を知りたい場合:


<pre class="lang:mysql">
mysql> select * from sys.user_summary_by_statement_type;
</pre>

> Or, to find the slowest statements (those in the 95th percentile by runtime):

又は、最も遅いステートメントを見つけることもできます(ランタイムによる95パーセンタイル値):

<pre class="lang:mysql">
mysql> select * from sys.statements_with_runtimes_in_95th_percentile\G
</pre>

> Many useful usage examples are detailed in the sys schema [documentation][sys-schema].

他のsys schemaの便利な使用例に関しては、[ドキュメント][sys-schema]を参照してください。

> To enable the performance schema, you must set the `performance_schema` parameter to 1 in the database instance's parameter group using the AWS console. If not enabled, this change requires an instance reboot. More about enabling the performance schema and installing the sys schema in [Part 2][part-2] of this series.

performance schemaを有効にするには、AWSコンソールから、そのデータベースインスタンスのパラメータグループに対する`performance_schema`パラメーターを1に設定する必要があります。これまで無効になっていた場合に設定を反映するためには、インスタンスの再起動が必要です。performance schemの有効活用とsys schemaのインストールに関しては、このシリーズの[Part 2][part-2]で解説します。


> If your queries are executing more slowly than expected,  evaluate your [resource metrics](#resource-utilization) and MySQL metrics that track how often operations have been blocked on acquiring a lock. In particular, check the `Innodb_row_lock_waits` metric, which counts how often InnoDB (the default storage engine for MySQL on RDS) had to wait to acquire a row lock.

もしも、クエリーの実行が予想以上に遅い場合、[リソースメトリクス](#resource-utilization)とロックの実行によってブロックされたオペレーションの発生頻度をMySQLメトリクスから評価します。具体的には、InnoDB(RDS上のMySQLのディフォルトストレージエンジン)の行ロックに起因し発生した待機の回数として`Innodb_row_lock_waits`メトリクスを確認します。


> MySQL users also have a number of caching options to expedite transactions, from making more RAM available for the [buffer pool][buffer-pool] used by InnoDB (MySQL's default storage engine), to enabling the [query cache][query-cache] to serve identical queries from memory, to using an application-level cache such as memcached or [Redis][redis].

MySQLのユーザーには、トランスアクションをスピードアップするためのキャッシュオプションが幾つかあります。例えば、InnoDBによって使用される[バッファープール][buffer-pool]により多くのRAMを追加する。同一のクエリーをメモリーから提供するための[クエリーキャッシュ][query-cache]を有効にする。memcachedや[Redis][redis]などの、アプリケーションレベルのキャッシュを利用する、があります。


> The performance schema and sys schema also allow you to quickly assess how many queries generated errors or warnings:

又、クエリーがエラーとワーニングをどの程度発生させているかを、performance schemaとsys schemaを使って知ることもできます:


<pre class="lang:mysql">
mysql> SELECT SUM(errors) FROM sys.statements_with_errors_or_warnings;
</pre>

#### Metrics to alert on

> * `Slow_queries`: How you define a slow query (and therefore how you configure the `long_query_time` parameter) will depend heavily on your use case and performance requirements. If the number of slow queries reaches worrisome levels, you will likely want to identify the actual queries that are executing slowly so you can optimize them. You can do this by querying the sys schema or by configuring MySQL to log all slow queries. More information on enabling and accessing the slow query log is available [in the RDS documentation][slow-log]. 

* `Slow_queries`: どのようにスロークエリーを提起するか(そして、`long_query_tim`のパラメーター値)は、ユースケースと性能要求に大きく依存しています。スロークエリーの数が気になるレベルに達した場合、最適化をするために、それらの処理に時間の掛かっている実際のクエリーを特定したくなることでしょう。この特定は、sys schemaにクエリーを送信するか、スロークエリーを記録する設定をMySQLに施すことにより実現することができます。スロークエリーのログを有効にする方法と、それへのアクセスとの方法についての詳しい情報については、[RDSのドキュメント][slow-log]を参照してください。


> <pre class="lang:mysql">mysql> select * from mysql.slow_log\G
*************************** 1. row ***************************
    start_time: 2015-09-15 20:47:18
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

* Query errors: クエリエラーの急激な増加は、クライアント・アプリケーションまたはデータベースに問題があることを示していることがあります。このようなケースでは、sys schemaを使って、どのクエリーが問題を起こしているかを調べることができます。例えば、エラーを返している量の多い正規化ステートメントのtop 10リストが取得できます:


> <pre class="lang:mysql">mysql> SELECT * FROM sys.statements_with_errors_or_warnings ORDER BY errors DESC LIMIT 10\G</pre>


<h3 class="anchor" id="resource-utilization">Resource utilization</h3>

#### Disk I/O metrics
| **Name** | **Description** | [**Metric&nbsp;type**][metric-101] | **Availability** |
|:--------:|:---------------:|:---------------:|:------------:|
| ReadIOPS | Read I/O operations per second | Resource: Utilization | CloudWatch |
| WriteIOPS | Write I/O operations per second | Resource: Utilization | CloudWatch |
| DiskQueueDepth | I/O operations waiting for disk access | Resource: Saturation | CloudWatch |
| ReadLatency | Seconds per read I/O operation | Resource: Other | CloudWatch | 
| WriteLatency | Seconds per write I/O operation | Resource: Other | CloudWatch | 

#### CPU, memory, storage, and network metrics
| **Name** | **Description** | [**Metric&nbsp;type**][metric-101] | **Availability** |
|:--------:|:---------------:|:---------------:|:------------:|
| CPUUtilization | Percent CPU utilized | Resource: Utilization | CloudWatch |
| FreeableMemory | Available RAM in bytes | Resource: Utilization | CloudWatch |
| SwapUsage | Swap usage in bytes | Resource: Saturation | CloudWatch |
| FreeStorageSpace | Available storage in bytes | Resource: Utilization | CloudWatch |
| NetworkReceive<br>Throughput | Network traffic to the MySQL instance, in bytes per second | Resource: Utilization | CloudWatch |
| NetworkTransmit<br>Throughput | Network traffic from the MySQL instance, in bytes per second | Resource: Utilization | CloudWatch |

> As Baron Schwartz, co-author of *[High Performance MySQL][mysql-book],* often notes, a database needs four fundamental resources: CPU, memory, disk, and network. Any of these can become a performance bottleneck—for a look at how difference RDS instance types can be constrained by their available resources, check out [this 2013 talk][bottlenecks] by Amazon's Grant McAlister.

*[High Performance MySQL][mysql-book]*の共著者のBaron Schwartz氏は、しばしば、次のように指摘してます。データーベースには、４つの基本的なリソースが必要です: それらは、CPU、メモリ、ディスク、およびネットワークです。これらのどれもが、ボトルネックになる可能性を持っています。RDSインスタンスタイプのリソースの差異による制約の詳細に関しては、AmazonのGrant McAlister氏による[2013年のプレゼンテーション][bottlenecks]を、是非参照してください。


> Whenever your database instance experiences performance problems, you should check metrics pertaining to the four fundamental resources to look for bottlenecks. Though you cannot access the full suite of system-level metrics that are available for EC2, CloudWatch does make available metrics on all four of these resources. For the most part, these metrics are most useful for [investigating (rather than detecting)][investigation] performance issues.

データベースインスタンスにパフォーマンス問題が発生した場合、ボトルネックの原因を見つけ出すために、先の四つの基本メトリクスに関係があるか確認する必要があります。一般的にEC2で利用可能なシステムレベルのメトリクスの全てにはアクセスすることはできませんが、CloudWatch上には、これらの四つの基本的メトリクスが公開されています。そして大抵の場合、これらのメトリクスは、パフォーマンス問題を検出するというより、もその原因を調査する際に最も有用になります。


<h4 class="anchor" id="disk-i/o-metrics">Disk I/O metrics</h4>

> CloudWatch makes available RDS metrics on read and write IOPS. These metrics are useful for monitoring the performance of your database and to ensure that your IOPS do not exceed the limits of your chosen instance type. If you are running an RDS instance in production, you will likely want to choose Provisioned IOPS storage to ensure consistent performance. 

CloudWatchには、読み取りと書き込みIOPSのRDSメトリクスも公開されています。これらのメトリクスは、データベースのパフォーマンスを監視し、選択したインスタンスタイプに設定されたIOPSの限界を超えないようにするために有用です。もしもあなたが本番環境でRDSインスタンスをつかっているなら、安定したパフォーマンスを確保するために、Provisioned IOPSストレージを選択することになるでしょう。


> If your storage volumes cannot keep pace with the volume of read and write requests, you will start to see I/O operations queuing up. The `DiskQueueDepth` metric measures the length of this queue at any given moment.

ストレージの処理スピードが、読み取りおよび書き込み要求の量に追従できなくなると、I/O操作の順番待ちが溜まっていくのを確認することができるようになります。`DiskQueueDepth`は、その瞬間の、このキューの長さを計測しています。


> Note that there will not be a one-to-one correspondence between queries and disk operations—queries that can be served from memory will bypass disk, for instance, and queries that return a large amount of data can involve more than one I/O operation. Specifically, reading or writing more than 16 KB, the [default page size][iops] for MySQL, will require multiple I/O operations.

クエリーの量とディスクの操作の量には、1対1の相関関係はありません。メモリーから結果を提供することができる場合は、ディスクへのアクセスはバイパスされます。更に、大量のデーターを返すクエリーは、複数のI/O操作に関係しています。具体的には、[MySQLのディフォルトページサイズ][iops]の16KBを越える読み取り又は書き込みは、複数のI/O操作を必要とします。



> In addition to I/O throughput metrics, RDS offers `ReadLatency` and `WriteLatency` metrics. These metrics do not capture full query latency—they only measure how long your I/O operations are taking at the disk level. 

I/Oスループットのメトリクスに加えて、RDSは`ReadLatency`と`ReadLatency`のメトリクスを提供しています。これらのメトリクスは、クエリーの完全なレイテンシーを計測していません。これらのメトリクスは、ディスクレベルでのI/O操作がどれくらい掛かっているかを計測しています。


> For read-heavy applications, one way to overcome I/O limitations is to [create a read replica][read-replica] of the database to serve some of the client read requests. For more, see the [section below](#read-replica-metrics) on metrics for read replicas.

データーベースからの読み取りの多いアプリで、I/Oの制限を克服する一つの方法は、クライアントの読み込みリクエストを処理するための[読み込み用のレプリカ(複製)を作る][read-replica]ことです。読み取りレプリカのメトリクスの詳細については、[以下のセクション](#read-replica-metrics)を参照してください。


#### CPU metrics

> High CPU utilization is not necessarily a bad sign. But if your database is performing poorly while it is within its IOPS and network limits, and while it appears to have sufficient memory, the CPUs of your chosen instance type may be the bottleneck.

高いCPUの利用率は、必ずしも悪いこと兆候ではありません。しかし、IOPSとネットワークが制限値以内にあり、メモリーも十分に確保できている状態では、選択しているインスタンスのCPUがボトルネックになっているかもしれません。


#### Memory metrics

> MySQL performs best when most of its working set of data can be held in memory. For this reason, you should monitor `FreeableMemory` and `SwapUsage` to ensure that your database instance is not memory-constrained.

MySQLは、処理をしているデーター全体がメモリー内に保持されている場合、最高の性能を発揮します。このような理由から、データベースがメモリーから制約を受けていないことを確認するために、`FreeableMemory`と`SwapUsage`を監視する必要があります。


> AWS advises that you monitor `ReadIOPS` when the database is under load to ensure that your database instance has enough RAM to [keep the working set almost entirely in memory][working-set]:

> > The value of ReadIOPS should be small and stable. If scaling up the DB instance class—to a class with more RAM—results in a dramatic drop in ReadIOPS, your working set was not almost completely in memory.

AWSは、データベースに負荷がかかっている時に、そのデータベース・インスタンスが、ほぼ完全なワーキングセットをメモリ内に維持するのに十分なRAMを有していることを確認するために、`ReadIOPS`を監視するようにアドバイスしています：

> `ReadIOPS`の値は、小さくて、安定していなければなりません。データベースインスタンをRAMの大きいクラスへスケールアップし、`ReadIOPS`値が劇的に低下した場合、以前のインスタンスクラスのRAMでは、ワーキングセットをほぼ完全に保持しておくには容量が足りなかったということになります。


<h4 class="anchor" id="storage-metrics">Storage metrics</h4>

> RDS allows you to allocate a fixed amount of storage when you launch your MySQL instance. The CloudWatch metric `FreeStorageSpace` lets you monitor how much of your allocated storage is still available. Note that you can always add more storage by modifying your running database instance in the AWS console, but you may not decrease it. 

RDSは、MySQLのインスタンを起動する際に、ストレージの量を設定することができます。CloudWatchが公開しているメトリクスの`FreeStorageSpace`を使えば、割り当てたストレージの空き容量を監視することができます。ここで注意すべきことは、AWSのコンソールから、動作中のでエータベースインスタンスのストレージ量を増やすことはできますが、それを減らすことができないと言うことです。


#### Network metrics

> RDS relies on Amazon Elastic Block Store (Amazon EBS) volumes for storage, and the network connection to EBS can limit your throughput. Monitoring `NetworkReceiveThroughput` and `NetworkTransmitThroughput` will help you identify potential network bottlenecks.

RDSは、Amazon Elastic Block Store (Amazon EBS)をストレージに使っています。そして、EBSとのネットワーク接続の状況が、スループットの制約になることがあります。`NetworkReceiveThroughput`と`NetworkTransmitThroughput`を監視することで、潜在的なネットワークのボトルネックを見つけ出すことができるようになります。 


> Even with Provisioned IOPS, it is entirely possible that network limitations will keep your realized IOPS below your provisioned maximum. For instance, if you provision 10,000 IOPS on a db.r3.2xlarge database instance, but your use case is extremely read-heavy, you will reach the bandwidth limit of 1 gigabit per second (roughly 8,000 IOPS) to EBS in each direction before hitting the provisioned limits of your storage.

Provisioned IOPSを設定しても、ネットワーク性能の上限が、プロビジョン設定したIOPSの実現を妨げることもあります。例えば、db.r3.2xlargeのデータベースインスタンスで、10,000をIOPSをプロビジョン設定します。しかし、読み取り中心のケースの場合、ストレージのプロビジョン制限に達する前に、毎秒1ギガビット(約8,000 IOPS)のEBSに対するネットワーク帯域の制限に先に到達してしまいます。


#### Metrics to alert on

> * `ReadLatency` or `WriteLatency`: Monitoring the latency of your disk operations is critical to identify potential constraints in your MySQL instance hardware or your database usage patterns. If your latency starts to climb, check your IOPS, disk queue, and network metrics to see if you are pushing the bounds of your instance type. If so, consult the RDS documentation for details about [storage options][storage], including volumes with provisioned IOPS rates. 

> * `DiskQueueDepth`: It is not unusual to have some requests in the disk queue, but investigation may be in order if this metric starts to climb, especially if latency increases as a result. (Time spent in the disk queue adds to read and write latency.)

> * `FreeStorageSpace`: AWS recommends that RDS users take action to delete unneeded data or add more storage if disk usage consistently reaches levels of 85 percent or more.  

- `ReadLatency`または`WriteLatency`： ディスク操作のレイテンシを監視することは、MySQLインスタンが使っているハードウェアやデータベースのユーセージパターンから来る潜在的な制約を見つけ出す際に重要です。レイテンシが増加し始めたら、IOPSやディスク操作のキューやネットワークのメトリクスを確認し、選択しているインスタンスタイプの限界に達していないかを確認します。もしもそうであれば、provisioned IOPS ratesが設定できるストレージを含め、RDSで設定できる[ストレージオプション][storage]に関してRDSのドキュメントを参照してください。

- `DiskQueueDepth`： ディスクキューにリクエストが溜まっていることは珍しくありません。しかし、このメトリクスが増加傾向にあるなら、調査が必要です。特に、このディスクキューの増加によってレイテンシがぞうかしているなら。(ディスクキュー内で順番を待っている時間は、読み取りや書き込みレイテンシーに加算されていきます。)

- `FreeStorageSpace`： ディスク使用率が一貫して85％以上を越えている場合、AWSでは、不要なデータを削除したり、ストレージスペースを追加することを、推奨しています。



<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/latency.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/latency.png"></a> 

<h3 class="anchor" id="connection-metrics">Connection metrics</h3>

| **Name** | **Description** | [**Metric&nbsp;type**][metric-101] | **Availability** |
|:--------:|:---------------:|:---------------:|:------------:|
| DatabaseConnections | Currently open connections | Resource: Utilization | CloudWatch |
| Threads_connected | Currently open connections | Resource: Utilization | MySQL |
| Threads_running | Currently running connections | Resource: Utilization | MySQL |
| Aborted_connects | Count of failed connection attempts to the server | Resource: Error | MySQL |
| Connection_errors_<br>internal | Count of connections refused due to server error | Resource: Error | MySQL |
| Connection_errors_<br>max_connections | Count of connections refused due to `max_connections` limit | Resource: Error | MySQL |

> Monitoring how many client connections are in use is critical to understanding your database's activity and capacity. MySQL has a configurable connection limit; on RDS the default value depends on the memory of the database's instance class in bytes, according to the formula: 

データーベースの処理状況や処理能力を理解するためにクライアント接続の数を把握することは重要です。MySQLには、このコネクション数の制限を設定する機能があります。RDSの場合、デフォルト値は、データベースのインスタンスクラスのメモリー容量をベースに以下の計算式になっています:

`max_connections` = `DBInstanceClassMemory` / 12582880

> The `max_connections` parameter can be modified by editing the database instance's parameter group using the RDS dashboard in the AWS console. You can also check the current value of `max_connections` by querying the MySQL instance itself (see [part 2][part-2] of this series for more on connecting to RDS instances directly):

`max_connections`パラメーターは、AWSのコンソールのRDSダッシュボードから、データベースインスタンスのパラメーターグループを編集することで変更できます。又、`max_connections`の値は、MySQLに直接問い合わせることで確認することもできます。(RDSインスタンに直接接続し情報を集取する方法は、このシリーズの[Part 2][part-2]を参照してください。)


<pre class="lang:mysql">
mysql> SELECT @@max_connections;
+-------------------+
| @@max_connections |
+-------------------+
|               100 |
+-------------------+
1 row in set (0.00 sec)
</pre>

> To monitor how many connections are in use, CloudWatch exposes a `DatabaseConnections` metric tracking open RDS connections, and MySQL exposes a similar `Threads_connected` metric counting connection threads. (MySQL allocates one thread per connection.) Either metric will help you monitor your connections in use, but the MySQL metric can be collected at higher resolution than the CloudWatch metric, which is reported at one-minute intervals. MySQL also exposes the `Threads_running` metric to isolate the threads that are actively processing queries.

使用中のコネクション数を監視するには、次の方法があります。CloudWatchは、`DatabaseConnections`メトリクスという使用中のRDSコネクション数を公開しています。MySQLは、類似のメトリクスとして`Threads_connected`(コネクションスレッドの数)を公開しています。(MySQLは、スレッド毎にコネクションを割り当てています。)どちらのメトリクスも使用中のコネクションの数を監視するのには使えますが、MySQLから収集した方が、1分毎にCloudwatchから収集するより短いインターバルでメトリクスを収集することができます。更に、MySQLは、活発にクエリーを処理しているスレッドを識別するために`Threads_running`メトリクスも公開します。


> If your server reaches the `max_connections` limit and starts to refuse connections, `Connection_errors_max_connections` will be incremented, as will the `Aborted_connects` metric tracking all failed connection attempts.

もしもサーバーが、`max_connections`の制限値に達し、新しいコネクションを受け入れなくなった場合、`Connection_errors_max_connections`と、接続の試みの失敗を追跡している`Aborted_connects`が加算されていきます。


> MySQL exposes a variety of other metrics on connection errors, which can help you identify client issues as well as serious issues with the database instance itself. The metric `Connection_errors_internal` is a good one to watch, because it is incremented when the error comes from the server itself. Internal errors can reflect an out-of-memory condition or the server's inability to start a new thread.

MySQLは、コネクションエラーに関し、様々なメトリクスを公開しています。これらのメトリクスは、クライアントの問題を識別したり、データーベースインスタンス自体の深刻な問題を識別するのに役立ちます。`Connection_errors_internal`メトリクスは、コネクションエラーがサーバー側で発生している際に加算されるので、把握しておく必要のあるメトリクスです。このインターナルエラーは、メモリーが不足している状態か、サーバーが新しいスレッドを開始できない状況を反映しています。


#### Metrics to alert on

> * `Threads_connected`: If a client attempts to connect to MySQL when all available connections are in use, MySQL will return a "Too many connections" error and increment `Connection_errors_max_connections`. To prevent this scenario, you should monitor the number of open connections and make sure that it remains safely below the configured `max_connections` limit. 

> * `Aborted_connects`: If this counter is increasing, your clients are probably trying and failing to connect to the database. Dig deeper with metrics such as `Connection_errors_max_connections` and `Connection_errors_internal` to diagnose the problem.

- `Threads_connected`： MySQLの全てのコネクションが使用中の時にクライアントがMySQLに接続しようとすると、MySQLは、"Too many connections"エラーを返し、`Connection_errors_max_connections`が、加算されます。このシナリオを回避するためには、使っているコネクションの数を監視し、`max_connections`の制限に掛からないようにコントロールする必要があります。

- `Aborted_connects`： この数が増加している場合、クライアントは、データベースの接続しようとして失敗している状況でしょう。 接続に失敗している原因を診断するために、`Connection_errors_max_connections`や`Connection_errors_internal`のようなメトリクスを使って調査をすすめると良いでしょう。


<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/threads_connected_2.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/threads_connected_2.png"></a> 

<h3 class="anchor" id="read-replica-metrics">Read replica metrics</h3>

| **Name** | **Description** | [**Metric&nbsp;type**][metric-101] | **Availability** |
|:--------:|:---------------:|:---------------:|:------------:|
| ReplicaLag | Number of seconds by which replica trails master | Other | CloudWatch |
| BinLogDiskUsage | Binary log disk usage on master, in bytes | Resource: Utilization | CloudWatch |

> RDS supports the creation of read replicas from the master MySQL instance. A replica is read-only by default so that its data remains in sync with the master, but that setting can be modified to add an index to the replica—to support a certain type of query, for instance. 

RDSは、マスターMySQLインスタンスからのリードレプリカの作成をサポートします。このレプリカは、マスターと同期し続けるために、デフォルトでは読み取り専用になっています。しかし、この設定は、インデックスを追加して特定のクエリーをサポートするための変更にも対応できます。


> These replicas are assigned a separate endpoint, so you can point client applications to read from a replica rather than from the source instance. You can also monitor the replica's connections, throughput, and query performance, just as you would for an ordinary RDS instance.

これらのレプリカには、個別のエンドポイントが割り当てられています。従って、マスターになっているインスタンスではなくレプリカから読み取ることができるようにクライアントアプリを設定し直すこともできます。そして、一般的なRDSインスタンスを監視するように、レプリカのスループットやクエリーパフォーマンスも監視することができます。


> The lag time for any read replica is captured by the CloudWatch metric `ReplicaLag`. This metric is usually not actionable, although if the lag is consistently very long, you should investigate your settings and resource usage.

読み込みレプリカの遅延時間は、CloudWatchメトリクスの`ReplicaLag`で収集することができます。一般的は、このメトリクスに対してアクションを起こすことは有りませんが、もしも遅延時間が一貫して非常に長い場合は、設定やリソースの使用状況を再度見直す必要があるでしょう。


> Another relevant metric for replication scenarios is `BinLogDiskUsage`, which measures the disk usage on the master database instance of binary logs. MySQL asynchronously replicates its data using a single thread on the master, so periods of high-volume writes cause pileups in the master's binary logs before the updates can be sent to the master.

レプリケーションを考えた場合、価値のある他のメトリクスは、`BinLogDiskUsage`です。このメトリクスは、マスターデータベースインスタンのバイナリーログのディスクの使用量を計測しています。MySQLは、マスター内の単一スレッドを使って非同期でデーターを複製しています。従って、大量の書き込みが発生している期間は、マスターにupdateを送るためのバイナリーログの山積み状態の原因になります。


<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/binlog.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/binlog.png"></a> 


## Conclusion

> In this post we have explored the most important metrics you should monitor to keep tabs on performance for MySQL deployed on Amazon RDS. If you are just getting started with MySQL on RDS, monitoring the metrics listed below will give you great insight into your database’s activity and performance. They will also help you to identify when it is necessary to increase your instance storage, IOPS, or memory to maintain good application performance.

> * [Query throughput](#query-throughput)
> * [Query performance and errors](#query-performance)
> * [Disk queue depth](#disk-i/o-metrics)
> * [Storage space](#storage-metrics)
> * [Client connections and errors](#connection-metrics)

この記事では、我々はあなたがアマゾンRDS上で展開のMySQLのパフォーマンスのタブを保つために監視する必要があり、最も重要なメトリックを検討しています。あなただけのRDS上のMySQLの使用を開始している場合は、以下に示す評価指標を監視することは、あなたのデータベースのアクティビティとパフォーマンスに優れた洞察力を与えるだろう。彼らはまた、優れたアプリケーションのパフォーマンスを維持するために、ご使用のインスタンス・ストレージ、IOPS、またはメモリを増やす必要があるときに識別するのに役立ちます。

* [Query throughput](#query-throughput)
* [Query performance and errors](#query-performance)
* [Disk queue depth](#disk-i/o-metrics)
* [Storage space](#storage-metrics)
* [Client connections and errors](#connection-metrics)


> [Part 2][part-2] of this series provides instructions for collecting all the metrics you need from CloudWatch and from MySQL.

このシリーズの[Part 2][part-2] では、CloudWatchとMySQLから必要な全てのメトリクスを収集する手順を解説していきます。

## Acknowledgments

> Many thanks to Baron Schwartz of [VividCortex][vivid] and to [Ronald Bradford][bradford] for reviewing and commenting on this article prior to publication.

この記事を公開するにあたり、レビューに協力しコメントをくれた[VividCortex][vivid]のBaron Schwartz氏と[Ronald Bradford][bradford]氏に感謝します。


- - -

*Source Markdown for this post is available [on GitHub][markdown]. Questions, corrections, additions, etc.? Please [let us know][issues].*


[part-2]: https://www.datadoghq.com/blog/how-to-collect-rds-mysql-metrics
[part-3]: https://www.datadoghq.com/blog/monitor-rds-mysql-using-datadog
[metric-101]: https://www.datadoghq.com/blog/monitoring-101-collecting-data/
[stored]: https://dev.mysql.com/doc/refman/5.6/en/stored-programs-views.html
[prepared]: https://dev.mysql.com/doc/refman/5.6/en/sql-syntax-prepared-statements.html
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
[read-replica]: http://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReadRepl.html#USER_ReadRepl.Overview
[mysql-book]: http://shop.oreilly.com/product/0636920022343.do
[markdown]: https://github.com/DataDog/the-monitor/blob/master/rds-mysql/monitoring_rds_mysql_performance_metrics.md
[issues]: https://github.com/DataDog/the-monitor/issues
[collecting-data]: https://www.datadoghq.com/blog/monitoring-101-collecting-data/#work-metrics
[vivid]: https://www.vividcortex.com/
[bradford]: http://ronaldbradford.com/