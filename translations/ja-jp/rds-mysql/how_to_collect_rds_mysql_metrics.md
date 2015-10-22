# How to collect RDS MySQL metrics

*This post is part 2 of a 3-part series on monitoring MySQL on Amazon RDS. [Part 1][part-1] explores the key performance metrics of RDS and MySQL, and [Part 3][part-3] describes how you can use Datadog to get a full view of your MySQL instance.*

As covered in [Part 1][part-1] of this series, MySQL on RDS users can access RDS metrics via Amazon CloudWatch and native MySQL metrics from the database instance itself. Each metric type gives you different insights into MySQL performance; ideally both RDS and MySQL metrics should be collected for a comprehensive view. This post will explain how to collect both metric types.

覆われたように[第1部] [パート1]ユーザーがデータベースインスタンス自体からはAmazon CloudWatchの経由RDSメトリックとネイティブMySQLのメトリクスにアクセスすることができますMySQLのRDSにこのシリーズの、。各メトリックタイプは、あなたのMySQLのパフォーマンスに異なる洞察を与えます。理想的には、RDSとMySQLのメトリックの両方を包括的に表示するために収集する必要があります。この投稿は、両方のメトリックのタイプを収集する方法を説明します。

## Collecting RDS metrics

RDS metrics can be accessed from CloudWatch in three different ways:

-   [Using the AWS Management Console and its web interface](#using-the-aws-console)
-   [Using the command line interface](#using-the-command-line-interface)
-   [Using a monitoring tool with a CloudWatch integration](#using-a-monitoring-tool-with-a-cloudwatch-integration)

<h3 class="anchor" id="using-the-aws-console">Using the AWS Console</h3>

Using the online management console is the simplest way to monitor RDS with CloudWatch. The AWS Console allows you to set up simple automated alerts and get a visual picture of recent changes in individual metrics.

オンライン管理コンソールを使用すると、CloudWatchのでRDSを監視するための最も簡単な方法です。 AWSコンソールでは、簡単な自動化されたアラートを設定し、個々のメトリックの最近の変化を視覚的に把握することができます。

#### Graphs

Once you are signed in to your AWS account, you can open the [CloudWatch console][aws-console] where you will see the metrics related to the different AWS services.

あなたのAWSアカウントにサインインしたら、あなたは[CloudWatchのコンソール]を開くことができます[AWS-コンソール]ここで、あなたは別のAWSサービスに関連するメトリックが表示されます。

By selecting RDS from the list of services and clicking on "Per-Database Metrics," you will see your database instances, along with the available metrics for each:

サービスの一覧から、RDSを選択し、をクリックすると、「データベース毎のメトリック、「受信者ごとに使用可能なメトリックと一緒に、あなたのデータベース・インスタンスが表示されます。

<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/metric-list-2.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/metric-list-2.png"></a>

Just select the checkbox next to the metrics you want to visualize, and they will appear in the graph at the bottom of the console.

ちょうどあなたが視覚化するメトリックの横にあるチェックボックスを選択して、彼らは、コンソールの下部にグラフに表示されます。

<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/metric-graph.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/metric-graph.png"></a>

#### Alerts

With the CloudWatch console you can also create alerts that trigger when a metric threshold is crossed.

CloudWatchのコンソールを使用すると、また、メトリックしきい値を超えた場合にトリガし、アラートを作成することができます。

To set up an alert, click on the "Create Alarm" button at the right of your graph and configure the alarm to notify a list of email addresses:

アラートを設定するには、グラフの右側にある「アラームを作成」ボタンをクリックし、電子メールアドレスのリストを通知するようにアラームを設定します。

<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/metric-alarm.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/metric-alarm.png"></a>

<h3 class="anchor" id="using-the-command-line-interface">Using the command line interface</h3>

You can also retrieve metrics related to your database instance using the command line. Command line queries can be useful for spot checks and ad hoc investigations. To do so, you will need to [install and configure the CloudWatch command line interface][aws-cli]. You will then be able to query for any CloudWatch metrics you want, using different filters.

また、コマンドラインを使用して、データベース・インスタンスに関連するメトリックを取得することができます。コマンドラインのクエリは、スポットチェックやアドホック調査のために有用であり得ます。これを行うには、[インストールおよび設定CloudWatchのコマンドラインインターフェイス] [AWS-CLI]にする必要があります。その後、別のフィルタを使用して、あなたが望む任意のCloudWatchのメトリックを照会することができるようになります。

For example, if you want to check the `CPUUtilization` metric across a five-minute window on your MySQL instance, you can run:

あなたのMySQLインスタンス上の5分のウィンドウ全体で`CPUUtilization`メトリックを確認したい場合たとえば、次のコマンドを実行します。

<pre class="lang:sh">
mon-get-stats CPUUtilization
    --namespace="AWS/RDS"
    --dimensions="DBInstanceIdentifier=instance-name"
    --statistics Maximum
    --start-time 2015-09-29T00:00:00
    --end-time 2015-09-29T00:05:00
</pre>

Here is an example of the output returned from a `mon-get-stats` query like the one above:

ここでは上記のような`月-GET-stats`クエリから返される出力の例を次に示します。

<pre class="lang:sh">
2015-09-29 00:00:00  33.09  Percent
2015-09-29 00:01:00  32.17  Percent
2015-09-29 00:02:00  34.67  Percent
2015-09-29 00:03:00  32.33  Percent
2015-09-29 00:04:00  31.45  Percent
</pre>

Full usage details for the `mon-get-stats` command are available [in the AWS documentation][mon-get-stats].

`月-GET-stats`コマンドの完全な使用方法の詳細は、[月-GET-統計] [AWSのマニュアルに]ご利用いただけます。

<h3 class="anchor" id="using-a-monitoring-tool-with-a-cloudwatch-integration">Using a monitoring tool with a CloudWatch integration</h3>

The third way to collect CloudWatch metrics is via your own monitoring tools, which can offer extended monitoring functionality. For instance, if you want to correlate metrics from your database with other parts of your infrastructure (including the applications that depend on that database), or you want to dynamically slice, aggregate, and filter your metrics on any attribute, or you need dynamic alerting mechanisms, you probably need a dedicated monitoring system. Monitoring tools that seamlessly integrate with the CloudWatch API can, with a single setup process, collect metrics from across your AWS infrastructure.

CloudWatchのメトリックを収集するための第三の方法は、拡張された監視機能を提供することができ、独自の監視ツールを介してです。あなたは、（そのデータベースに依存するアプリケーションを含む）、インフラストラクチャの他の部分を使用してデータベースからメトリックを関連付けるしたい場合や、たとえば、動的に、集計をスライスし、任意の属性にあなたのメトリックをフィルタするか、動的に必要メカニズムを警告、あなたはおそらく、専用の監視システムを必要としています。シームレスに、単一のセットアッププロセスで、あなたのAWSインフラストラクチャ全体からメトリックを収集することができますCloudWatchのAPIを使用した統合監視ツール。

In [Part 3][part-3] of this series, we walk through how you can easily collect, visualize, and alert on any RDS metric using Datadog.

で[その3]このシリーズの[-3は一部]、我々はあなたが簡単にDatadogを使用して、メトリックの任意のRDSに視覚化、収集、および警告する方法を歩きます。

## Collecting native MySQL metrics

CloudWatch offers several high-level metrics for any database engine, but to get a deeper look at MySQL performance you will need [metrics from the database instance itself][part-1]. Here we will focus on four methods for metric collection:

CloudWatchのは、任意のデータベースエンジンのいくつかの高レベルのメトリックを提供していますが、[データベースインスタンス自体からメトリック]深く、必要なMySQLのパフォーマンスを見て取得するには、[パート1]。ここでは、メトリック収集のための4つの方法に焦点を当てます。

-   [Querying server status variables](#querying-server-status-variables)
-   [Querying the performance schema and sys schema](#querying-the-performance-schema-and-sys-schema)
-   [Using the MySQL Workbench GUI](#using-the-mysql-workbench-gui)
-   [Using a MySQL monitoring tool](#using-a-mysql-monitoring-tool)

<h3 class="anchor" id="querying-server-status-variables">Querying server status variables</h3>
<h4 class="anchor" id="connecting-to-your-rds-instance">Connecting to your RDS instance</h4>
With RDS you cannot directly access the machines running MySQL. So you cannot run `mysql` commands locally or check CPU utilization from the machine itself, as you could if you installed MySQL yourself on a standalone EC2 instance. That said, you _can_ connect to your MySQL instance remotely using standard tools, provided that the security group for your MySQL instance permits connections from the device or EC2 instance you are using to initiate the connection.

RDSを使用すると、直接MySQLを実行しているマシンにアクセスすることはできません。だから、ローカルコマンドmysql``を実行するか、または可能性としてスタンドアロンEC2インスタンス上でMySQLを自分でインストールした場合、マシン自体からのCPU使用率を確認することはできません。それはあなたがリモートでのMySQLインスタンスのセキュリティグループを使用すると、接続を開始するために使用しているデバイスやEC2インスタンスからの接続を許可することを提供し、標準のツールを使用して、MySQLインスタンスに接続_can_、と述べました。

<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/ssh_to_rds.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/ssh_to_rds.png"></a>

For example, if your RDS MySQL instance accepts traffic only from inside its security group, you can launch an EC2 instance in that security group, and then apply a second security group rule to the EC2 instance to accept inbound SSH traffic (*see diagram above*). Then you can SSH to the EC2 instance, from which you can connect to MySQL using the mysql command line tool:

インバウンドSSHトラフィックを受け入れるように、RDS MySQLインスタンスのみがそのセキュリティグループ内からのトラフィックを受け入れた場合、あなたはそのセキュリティグループにEC2インスタンスを起動することができますし、EC2インスタンスに第2のセキュリティグループルールを適用します（※上記の図を参照してください*）。そして、あなたはmysqlコマンドラインツールを使用してMySQLに接続することができ、そこからEC2インスタンスにSSHすることができます。

<pre class="lang:sh">
mysql -h instance-name.xxxxxx.us-east-1.rds.amazonaws.com -P 3306 -u yourusername -p
</pre>

The instance endpoint (ending in `rds.amazonaws.com`) can be found in the list of instances on the [RDS console][rds-console].

（rds.amazonaws.com``で終わる）インスタンスのエンドポイントは、[RDSコンソール] [RDS-コンソール]にインスタンスのリストに記載されています。

Once you connect to your database instance, you can query any of the hundreds of available MySQL metrics, known as [server status variables][ssv]. To check metrics on connection errors, for instance:

あなたは、データベース・インスタンスに接続したら、[サーバーのステータス変数] [SSV]として知られている利用可能なMySQLのメトリック、数百人のいずれかを照会することができます。例えば、接続エラーにメトリックを確認するには：

<pre class="lang:mysql">
mysql> SHOW GLOBAL STATUS LIKE '%Connection_errors%';
</pre>

<h3 class="anchor" id="querying-the-performance-schema-and-sys-schema">Querying the performance schema and sys schema</h3>
Server status variables by and large capture high-level server activity. To collect metrics at the query level, such as query latency and query errors, you can use the MySQL [performance schema][performance-schema], which captures detailed statistics on server events.

することにより、サーバのステータス変数と大キャプチャハイレベルのサーバーの活動。このようなクエリの待機時間とクエリエラーなどのクエリ・レベルでメトリックを収集するには、サーバーのイベントに関する詳細な統計情報をキャプチャのMySQL[パフォーマンススキーマ] [パフォーマンススキーマ]を、使用することができます。

#### Enabling the performance schema

To enable the performance schema, you must set the `performance_schema` parameter to 1 in the database instance's parameter group using [the AWS console][rds-console]. This change requires an instance reboot.

パフォーマンスのスキーマを有効にするには、[AWSコンソール] [RDS-コンソール]を使用して、データベース・インスタンスのパラメータグループ内の1を `performance_schema`パラメータを設定する必要があります。この変更は、インスタンスの再起動が必要です。

Once it is enabled, the performance schema will collect metrics on all the statements executed by the server. Many of those metrics are summarized in the `events_statements_summary_by_digest` table, available in MySQL 5.6 and later. The digest normalizes all the statements, ignoring data values and standardizing whitespace, so that the following two queries [would be considered the same][digest]:

それを有効にすると、パフォーマンスのスキーマは、サーバーで実行されるすべての文のメトリックを収集します。これらのメトリックの多くは、後のMySQL5.6とで利用でき、`events_statements_summary_by_digest`表にまとめられています。ダイジェストは、[ダイジェスト]次の2つのクエリは、[同じであると考えられる]ように、データ値を無視し、空白文字を標準化し、すべての文を正規化します。

<pre class="lang:mysql">
SELECT * FROM orders WHERE customer_id=10 AND quantity>20
SELECT * FROM orders WHERE customer_id = 25 AND quantity > 100
</pre>

The performance schema captures information about latency, errors, and query volume for each normalized statement. A sample row from the `events_statements_summary_by_digest` table shows an expensive query that takes multiple seconds to execute (all timer measurements are in picoseconds):

パフォーマンスのスキーマは、正規化された各ステートメントの待ち時間、エラー、およびクエリのボリュームについての情報を取得します。 `events_statements_summary_by_digest`テーブルからのサンプル行は、（すべてのタイマー測定がピコ秒である）を実行するために複数秒かかり高価なクエリを示しています。

<pre class="lang:mysql">
*************************** 1. row ***************************
                SCHEMA_NAME: employees
                     DIGEST: 5f56800663c86bf3c24239c1fc1edfcb
                DIGEST_TEXT: SELECT * FROM `employees` . `salaries`
                 COUNT_STAR: 2
             SUM_TIMER_WAIT: 4841460833000
             MIN_TIMER_WAIT: 1972509586000
             AVG_TIMER_WAIT: 2420730416000
             MAX_TIMER_WAIT: 2868951247000
              SUM_LOCK_TIME: 1101000000
                 SUM_ERRORS: 0
               SUM_WARNINGS: 0
          SUM_ROWS_AFFECTED: 0
              SUM_ROWS_SENT: 5688094
          SUM_ROWS_EXAMINED: 5688094
SUM_CREATED_TMP_DISK_TABLES: 0
     SUM_CREATED_TMP_TABLES: 0
       SUM_SELECT_FULL_JOIN: 0
 SUM_SELECT_FULL_RANGE_JOIN: 0
           SUM_SELECT_RANGE: 0
     SUM_SELECT_RANGE_CHECK: 0
            SUM_SELECT_SCAN: 2
      SUM_SORT_MERGE_PASSES: 0
             SUM_SORT_RANGE: 0
              SUM_SORT_ROWS: 0
              SUM_SORT_SCAN: 0
          SUM_NO_INDEX_USED: 2
     SUM_NO_GOOD_INDEX_USED: 0
                 FIRST_SEEN: 2015-09-25 19:57:25
                  LAST_SEEN: 2015-09-25 19:59:39
</pre>

<h4 class="anchor" id="using-the-sys-schema">Using the sys schema</h4>
Though the performance schema can be queried directly, it is usually easier to extract meaningful views of the data using the [sys schema][sys-schema], which provides a number of useful tables, functions, and procedures for parsing your data.

パフォーマンススキーマを直接照会することができますが、それはあなたのデータを解析するための便利なテーブル、関数、およびプロシージャの数を提供[SYSスキーマ] [SYS-スキーマ]を使用して、データの意味のあるビューを抽出する方が簡単です。

To install the sys schema, first clone the [mysql-sys][sys-schema] GitHub repo to the machine that you use to connect to your MySQL instance (e.g., an EC2 instance in the same security group) and position yourself within the newly created directory:

SYSスキーマ、最初のクローン[mysqlの-SYS][SYSスキーマ]あなたのMySQLインスタンスへの接続に使用するマシンにGitHubのレポ（例えば、同じセキュリティグループのEC2インスタンス）をインストールして、内部に自分自身を配置するには新たにディレクトリを作成しました：

<pre class="lang:sh">
git clone https://github.com/MarkLeith/mysql-sys.git
cd mysql-sys
</pre>

Then, run a shell script within the mysql-sys repo that creates an RDS-compatible file for the sys schema. For MySQL version 5.6, the command and output looks like:

次に、SYSスキーマのRDS互換ファイルを作成します。mysqlの-SYSレポ内のシェルスクリプトを実行します。 MySQLバージョン5.6の場合は、コマンドと出力は次のようになります。

<pre class="lang:sh">
$ ./generate_sql_file.sh -v 56 -b -u CURRENT_USER
Wrote file: /home/ec2-user/mysql-sys/gen/sys_1.5.0_56_inline.sql
Object Definer: CURRENT_USER
sql_log_bin: disabled
</pre>

Finally, you must load the newly created file into MySQL, using the filename returned in the step above:

最後に、上記のステップで返されたファイル名を使用して、MySQLの中に新しく作成されたファイルをロードする必要があります。

<pre class="lang:sh">
mysql -h instance-name.xxxxxx.us-east-1.rds.amazonaws.com -P 3306 -u yourusername -p < gen/sys_1.5.0_56_inline.sql
</pre>

Now, when you access your database instance using the mysql command line tool, you will have access to the sys schema and all the views within. The [sys schema documentation][sys-schema] provides information on the various tables and functions, along with a number of useful examples. For instance, to summarize all the statements executed, along with their associated latencies:

あなたはmysqlコマンドラインツールを使用して、データベース・インスタンスにアクセスするときに今、あなたはSYSスキーマと内のすべてのビューにアクセスする必要があります。 [SYSスキーマのドキュメント] [SYS-スキーマ]は有用な例の数とともに、各種テーブルや機能についての情報を提供します。例えば、それらに関連するレイテンシと一緒に、すべての文が実行要約します：

<pre class="lang:mysql">
mysql> select * from sys.user_summary_by_statement_type;
+----------+--------------------+-------+---------------+-------------+--------------+-----------+---------------+---------------+------------+
| user     | statement          | total | total_latency | max_latency | lock_latency | rows_sent | rows_examined | rows_affected | full_scans |
+----------+--------------------+-------+---------------+-------------+--------------+-----------+---------------+---------------+------------+
| gobby    | create_view        |    87 | 490.62 ms     | 6.74 ms     | 9.78 ms      |         0 |             0 |             0 |          0 |
| gobby    | create_procedure   |    26 | 80.58 ms      | 9.16 ms     | 9.06 ms      |         0 |             0 |             0 |          0 |
| gobby    | drop_procedure     |    26 | 51.71 ms      | 2.76 ms     | 1.01 ms      |         0 |             0 |             0 |          0 |
| gobby    | create_function    |    20 | 49.57 ms      | 3.34 ms     | 2.20 ms      |         0 |             0 |             0 |          0 |
| gobby    | drop_function      |    20 | 38.84 ms      | 2.20 ms     | 889.00 us    |         0 |             0 |             0 |          0 |
| gobby    | create_table       |     1 | 20.28 ms      | 20.28 ms    | 0 ps         |         0 |             0 |             0 |          0 |
| gobby    | create_trigger     |     2 | 15.66 ms      | 8.07 ms     | 323.00 us    |         0 |             0 |             0 |          0 |
| gobby    | drop_trigger       |     2 | 4.54 ms       | 2.57 ms     | 0 ps         |         0 |             0 |             0 |          0 |
| gobby    | insert             |     1 | 4.29 ms       | 4.29 ms     | 197.00 us    |         0 |             0 |             5 |          0 |
| gobby    | create_db          |     1 | 3.10 ms       | 3.10 ms     | 0 ps         |         0 |             0 |             1 |          0 |
| gobby    | show_databases     |     3 | 841.59 us     | 351.89 us   | 268.00 us    |        17 |            17 |             0 |          3 |
| gobby    | select             |     5 | 332.27 us     | 92.61 us    | 0 ps         |         5 |             0 |             0 |          0 |
| gobby    | set_option         |     5 | 182.79 us     | 43.50 us    | 0 ps         |         0 |             0 |             0 |          0 |
| gobby    | Init DB            |     1 | 19.82 us      | 19.82 us    | 0 ps         |         0 |             0 |             0 |          0 |
| gobby    | Quit               |     2 | 15.26 us      | 11.95 us    | 0 ps         |         0 |             0 |             0 |          0 |
+----------+--------------------+-------+---------------+-------------+--------------+-----------+---------------+---------------+------------+
</pre>

<h3 class="anchor" id="using-the-mysql-workbench-gui">Using the MySQL Workbench GUI</h3>
[MySQL Workbench][workbench] is a free application with a GUI for managing and monitoring a MySQL instance. MySQL Workbench provides a high-level performance dashboard, as well as an easy-to-use interface for browsing performance metrics (using the views provided by the [sys schema](#using-the-sys-schema)).

【MySQLのワークベンチ] [ワークベンチ]は管理やMySQLインスタンスを監視するためのGUIを使用して無料のアプリケーションです。 MySQLのワークベンチは、高レベルのパフォーマンスダッシュボードと同様に、（使用して--SYS-スキーマ）[SYSスキーマ]が提供するビュー（＃を使用して）、パフォーマンス・メトリックを閲覧するための使いやすいインタフェースを提供します。

<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/workbench-2.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/workbench-2.png"></a>

If you have [configured an EC2](#connecting-to-your-rds-instance) instance to communicate with MySQL running on RDS, you can connect MySQL Workbench to your MySQL on RDS via SSH tunneling:

あなたはMySQLがRDS上で実行されていると通信する（＃接続ツーあなた-RDSインスタンス）インスタンス[EC2を設定して]している場合は、SSHトンネリングを経由して、RDS上のMySQLへのMySQL Workbenchを接続することができます。

<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/ssh_tunneling-2.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/ssh_tunneling-2.png"></a>

You can then view recent metrics on the performance dashboard or click through the statistics available from the sys schema:

あなたは、パフォーマンスのダッシュボードに最近のメトリックを表示したり、SYSスキーマから利用可能な統計を介してクリックすることができます：

<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/95th_percentile-2.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/95th_percentile-2.png"></a>

<h3 class="anchor" id="using-a-mysql-monitoring-tool">Using a MySQL monitoring tool</h3>
The fourth way to access MySQL's native metrics is to use a full-featured monitoring tool that integrates with MySQL. Such tools allow you to not only glimpse a real-time snapshot of your metrics but to visualize and analyze your metrics' evolution over time, and to set alerts to be notified when key metrics go out of bounds. Comprehensive monitoring tools also allow you to correlate your metrics across systems, so you can quickly determine if errors from your application can be traced back to MySQL, or if increased MySQL latency is caused by system-level resource contention. [Part 3][part-3] of this series demonstrates how you can set up comprehensive monitoring of MySQL on RDS with Datadog.

MySQLのネイティブメトリクスにアクセスするための第四の方法は、MySQLと統合フル機能の監視ツールを使用することです。このようなツールを使用するだけでなく、あなたのメトリックのスナップショットを垣間見ることではなく、主要な指標が範囲外に行くときに通知されるように視覚化し、時間をかけてあなたのメトリック」の進化を分析し、アラートを設定することができます。総合的な監視ツールはまた、システム間であなたのメトリックを相関することができますので、あなたのアプリケーションからのエラーが戻ってMySQLへトレースできるかどうか、または増加したMySQLのレイテンシは、システム・レベルのリソースの競合によって引き起こされる場合は、速やかに決定することができます。 [第3部]は、[部分が-3]この一連のあなたがDatadogとRDSでMySQLの総合的な監視を設定する方法を示しています。

## Conclusion

In this post we have walked through how to use CloudWatch to collect and visualize RDS metrics, and how to generate alerts when these metrics go out of bounds. We've also shown you how to collect more detailed metrics from MySQL itself, whether on an ad hoc or continuous basis.

この記事では、RDSのメトリックを収集し、視覚化するCloudWatchの使用方法を歩いていると、これらの指標が範囲外に行くとどのようにアラートを生成します。また、かどうか、広告アドホックまたは継続的に、MySQLの自体からより詳細なメトリックを収集する方法をあなたに示してきました。

In [the next and final part][part-3] of this series, we'll show you how you can set up Datadog to collect, visualize, and set alerts on metrics from both RDS and MySQL.

で[次のと最後の部分] [パート3]このシリーズの、我々はあなたが収集、可視化、およびRDSとMySQLの両方からのメトリックにアラートを設定するDatadogを設定する方法を紹介します。

## Acknowledgments

We are grateful to have had input on this series from Baron Schwartz, whose company [VividCortex][vivid] provides a query-centric view of database performance.

私たちは会社[VividCortex] [ビビッド]データベースのパフォーマンスのクエリ中心のビューを提供バロンシュワルツからこのシリーズの入力があったと感謝しています。

- - -

*Source Markdown for this post is available [on GitHub][markdown]. Questions, corrections, additions, etc.? Please [let us know][issues].*

[markdown]: https://github.com/DataDog/the-monitor/blob/master/rds-mysql/how_to_collect_rds_mysql_metrics.md
[issues]: https://github.com/DataDog/the-monitor/issues
[part-1]: https://www.datadoghq.com/blog/monitoring-rds-mysql-performance-metrics
[part-3]: https://www.datadoghq.com/blog/monitor-rds-mysql-using-datadog
[aws-console]: https://console.aws.amazon.com/cloudwatch/home
[rds-console]: https://console.aws.amazon.com/rds/
[aws-cli]: https://aws.amazon.com/developertools/2534
[mon-get-stats]: http://docs.aws.amazon.com/AmazonCloudWatch/latest/cli/cli-mon-get-stats.html
[ssv]: https://dev.mysql.com/doc/refman/5.6/en/server-status-variables.html
[performance-schema]: http://dev.mysql.com/doc/refman/5.6/en/performance-schema.html
[digest]: https://dev.mysql.com/doc/refman/5.6/en/performance-schema-statement-digests.html
[sys-schema]: https://github.com/MarkLeith/mysql-sys/
[workbench]: http://dev.mysql.com/downloads/workbench/
[vivid]: https://www.vividcortex.com/
