# How to collect RDS MySQL metrics

> *This post is part 2 of a 3-part series on monitoring MySQL on Amazon RDS. [Part 1][part-1] explores the key performance metrics of RDS and MySQL, and [Part 3][part-3] describes how you can use Datadog to get a full view of your MySQL instance.*

*このポストは、Amazon RDSの上にあるMySQの監視に関する3回シリーズのポストのPart 2です。[Part 1][part-1]は、”RDSとMySQLのキーメトリクス”を解説しています。[Part 3][part-3]では、”Datadogを使ってAmazon RDSの上にあるMySQをどのように監視するか”を解説します。*


> As covered in [Part 1][part-1] of this series, MySQL on RDS users can access RDS metrics via Amazon CloudWatch and native MySQL metrics from the database instance itself. Each metric type gives you different insights into MySQL performance; ideally both RDS and MySQL metrics should be collected for a comprehensive view. This post will explain how to collect both metric types.

このシリーズの[Part 1][part-1]で取り上げたように、RDS上のMysqlのユーザーは、Amazon CloudWatch経由でRDSのメトリクスにアクセスでき、更にデータベース自体からネイティブのMySQLメトリクスにもアクセスできます。それぞれのタイプのメトリクスは、MySQLのパフォーマンスについて異なる洞察を与えてくれます。理想的には、包括的に状況を把握できるようにするために、RDSとMySQLの両方のメトリクスを集取している必要があります。この記事では、両方のメトリックタイプを収集する方法を解説していきます。


## Collecting RDS metrics

> RDS metrics can be accessed from CloudWatch in three different ways:

> -   [Using the AWS Management Console and its web interface](#using-the-aws-console)
> -   [Using the command line interface](#using-the-command-line-interface)
> -   [Using a monitoring tool with a CloudWatch integration](#using-a-monitoring-tool-with-a-cloudwatch-integration)

RDSメトリックへは、CloudWatch経由で、次の3つの方法でアクセスできます。

- [AWSの管理コンソールを使用る方法](#using-the-aws-console)
- [コマンドラインインターフェースを使用する方法](#using-the-command-line-interface)
- [CloudWatchインテグレーションを持った監視ツールを使用する方法](#using-a-monitoring-tool-with-a-cloudwatch-integration)


<h3 class="anchor" id="using-the-aws-console">Using the AWS Console</h3>

> Using the online management console is the simplest way to monitor RDS with CloudWatch. The AWS Console allows you to set up simple automated alerts and get a visual picture of recent changes in individual metrics.

AWSの管理コンソールを使用する方法が、CloudWatchのでRDSを監視する最もシンプルな方法です。AWSコンソールのインターフェース上では、個々のメトリックの直近の変化を視覚的に把握したり、簡単な自動アラートを設定することができます。


#### Graphs

> Once you are signed in to your AWS account, you can open the [CloudWatch console][aws-console] where you will see the metrics related to the different AWS services.

> By selecting RDS from the list of services and clicking on "Per-Database Metrics," you will see your database instances, along with the available metrics for each:

AWSアカウントにサインインしたら、AWSサービスに関連するメトリックを閲覧することができる[CloudWatchコンソール][aws-console]を開くことができます。

サービスリストからRDSを選択し、"Per-Database Metrics"をクリックすると、閲覧可能なメトリクスと共に、データベースインスタンスのリストが表示されます。


<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/metric-list-2.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/metric-list-2.png"></a>

> Just select the checkbox next to the metrics you want to visualize, and they will appear in the graph at the bottom of the console.

可視化したいメトリクスの横にあるチェックボックスを選択すると、コンソールの下部にグラフで表示されます。


<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/metric-graph.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/metric-graph.png"></a>

#### Alerts

> With the CloudWatch console you can also create alerts that trigger when a metric threshold is crossed.

> To set up an alert, click on the "Create Alarm" button at the right of your graph and configure the alarm to notify a list of email addresses:

CloudWatchのコンソールには、メトリクスが閾値を超えた場合にアラートを発生させる機能があります。

このアラート機能を設定するには、グラフの右側にある"Create Alarm"ボタンをクリックし、警報を通知するメールアドレスを指定します:

<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/metric-alarm.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/metric-alarm.png"></a>

<!-- <h3 class="anchor" id="using-the-command-line-interface">Using the command line interface</h3> -->
### <a class="anchor" id="using-the-command-line-interface"></a>Using the command line interface

> You can also retrieve metrics related to your database instance using the command line. Command line queries can be useful for spot checks and ad hoc investigations. To do so, you will need to [install and configure the CloudWatch command line interface][aws-cli]. You will then be able to query for any CloudWatch metrics you want, using different filters.
>
> For example, if you want to check the `CPUUtilization` metric across a five-minute window on your MySQL instance, you can run:

コマンドラインを使用して、データベースインスタンスに関するメトリックを取得することもできます。コマンドラインからの問い合わせは、スポット的なチェックやアドホックな原因追及の時に便利です。この方法を使うためには、[CloudWatchのコマンドラインから操作するソフト][aws-cli]を手元の端末にインストールし、設定する必要があります。インストールと設定が完了すると、異なる検索コマンドを使ってCloudWatchメトリクスに問い合わせることができるようになります。

例えば、MySQLインスタンスの5分間の`CPUUtilization`(CPU利用率)メトリクスを確認したい場合、次のようなコマンドを実行します:


<pre class="lang:sh">
mon-get-stats CPUUtilization
    --namespace="AWS/RDS"
    --dimensions="DBInstanceIdentifier=instance-name"
    --statistics Maximum
    --start-time 2015-09-29T00:00:00
    --end-time 2015-09-29T00:05:00
</pre>

> Here is an example of the output returned from a `mon-get-stats` query like the one above:

上記に紹介した`mon-get-stats`コマンドの実行結果の出力は、以下のようになります:


<pre class="lang:sh">
2015-09-29 00:00:00  33.09  Percent
2015-09-29 00:01:00  32.17  Percent
2015-09-29 00:02:00  34.67  Percent
2015-09-29 00:03:00  32.33  Percent
2015-09-29 00:04:00  31.45  Percent
</pre>

> Full usage details for the `mon-get-stats` command are available [in the AWS documentation][mon-get-stats].

`mon-get-stats`コマンドの完全な使い方は、[AWSのマニュアルで該当コマンドの詳細][mon-get-stats]を参照してください。


<!-- <h3 class="anchor" id="using-a-monitoring-tool-with-a-cloudwatch-integration">Using a monitoring tool with a CloudWatch integration</h3> -->
### <a class="anchor" id="using-a-monitoring-tool-with-a-cloudwatch-integration"></a>Using a monitoring tool with a CloudWatch integration

> The third way to collect CloudWatch metrics is via your own monitoring tools, which can offer extended monitoring functionality. For instance, if you want to correlate metrics from your database with other parts of your infrastructure (including the applications that depend on that database), or you want to dynamically slice, aggregate, and filter your metrics on any attribute, or you need dynamic alerting mechanisms, you probably need a dedicated monitoring system. Monitoring tools that seamlessly integrate with the CloudWatch API can, with a single setup process, collect metrics from across your AWS infrastructure.

CloudWatchのメトリックを収集する第三の方法は、高度な監視機能を持った独自の監視ツールを使う方法です。例えば、データベースから収集したメトリクスを、アプリを含むインフラの他の部分から収集したメトリクスと相関したい場合。又、収集したばかりのメトリクスを属性に基づいて、その場で、分類し、集約し、フィルターしたい場合。ダイナミックなアラートシステムが必要な場合。これらの場合は、ダイナミックな監視システムが必要になるでしょう。高度にCloudWatchのAPIと連携できる監視ツールは、AWS上に構築したインフラの全体に渡りメトリクスを収集してくれるはずです。


> In [Part 3][part-3] of this series, we walk through how you can easily collect, visualize, and alert on any RDS metric using Datadog.

このシリーズの[Part 3][part-3]では、Datadogを使用してRDSメトリクスを収集し、可視化し、アラートを設定する手順を解説していきます。


## Collecting native MySQL metrics

> CloudWatch offers several high-level metrics for any database engine, but to get a deeper look at MySQL performance you will need [metrics from the database instance itself][part-1]. Here we will focus on four methods for metric collection:

> - [Querying server status variables](#querying-server-status-variables)
> - [Querying the performance schema and sys schema](#querying-the-performance-schema-and-sys-schema)
> - [Using the MySQL Workbench GUI](#using-the-mysql-workbench-gui)
> - [Using a MySQL monitoring tool](#using-a-mysql-monitoring-tool)

CloudWatchは、任意のデータベースエンジンの概要的なメトリクスを提供してくれています。しかし、より詳細にMySQLのパフォーマンスを把握したい場合は、[データベースインスタンス自体からメトリクスを収集する][part-1]必要があります:

- [サーバーステータスに関する変数への問い合わせ](#querying-server-status-variables)
- [performance schemaとsys schemaへの問い合わせ](#querying-the-performance-schema-and-sys-schema)
- [MySQL Workbench GUI](#using-the-mysql-workbench-gui)
- [MySQL監視ツール](#using-a-mysql-monitoring-tool)


<!--
<h3 class="anchor" id="querying-server-status-variables">Querying server status variables</h3>
<h4 class="anchor" id="connecting-to-your-rds-instance">Connecting to your RDS instance</h4>
-->
### <a class="anchor" id="querying-server-status-variables"></a>Querying server status variables
#### <a class="anchor" id="connecting-to-your-rds-instance"></a>Connecting to your RDS instance

> With RDS you cannot directly access the machines running MySQL. So you cannot run `mysql` commands locally or check CPU utilization from the machine itself, as you could if you installed MySQL yourself on a standalone EC2 instance. That said, you _can_ connect to your MySQL instance remotely using standard tools, provided that the security group for your MySQL instance permits connections from the device or EC2 instance you are using to initiate the connection.

RDSでは、MySQLを実行しているマシンに直接アクセスすることはできません。従って、EC2インスタンス上にMySQLをインストールした場合のように、`mysql`コマンドをローカルから実行したり、CPUの利用率をそのマシン自身から確認したりすることができません。しかしながら、RDS上のMySQLインスタンスのセキュリティグループが、それに接続使用としているバックエンドEC2インスタンスやデバイスからの接続を許可している場合、リモートでスタンダードツールを使ってMySQLインスタンスに接続することはできます。


<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/ssh_to_rds.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/ssh_to_rds.png"></a>

> For example, if your RDS MySQL instance accepts traffic only from inside its security group, you can launch an EC2 instance in that security group, and then apply a second security group rule to the EC2 instance to accept inbound SSH traffic (*see diagram above*). Then you can SSH to the EC2 instance, from which you can connect to MySQL using the mysql command line tool:

例えば、RDSのMySQLインスタンスがセキュリティグループ内部からのトラフィックを受け入れる場合、そのセキュリティーグループ内にEC2インスタンスを起動します。次に、そのEC2インスタンスに、インバウンドSSHトラフィックを許可するように、第2のセキュリティグループルールを適用します（*上記の図を参照してください。*）。そして、SSH経由でそのEC2インスタンスを操作し、mysqlコマンドラインツールを使用してRDS上のMySQLから情報を集取してきます。


<pre class="lang:sh">
mysql -h instance-name.xxxxxx.us-east-1.rds.amazonaws.com -P 3306 -u yourusername -p
</pre>

> The instance endpoint (ending in `rds.amazonaws.com`) can be found in the list of instances on the [RDS console][rds-console].

> Once you connect to your database instance, you can query any of the hundreds of available MySQL metrics, known as [server status variables][ssv]. To check metrics on connection errors, for instance:

インスタンスのエンドポイント(`rds.amazonaws.com`で終わる部分)は、[RDSのコンソール][rds-console]上のインスタンスリストに記載されています。

データベース・インスタンスに接続できたら、[server status variables][ssv]で知られる、数百をもあるMySQLメトリクスを参照することができるようになります。例えば、接続エラーのメトリックを確認するのは次のようになります:


<pre class="lang:mysql">
mysql> SHOW GLOBAL STATUS LIKE '%Connection_errors%';
</pre>

<!--<h3 class="anchor" id="querying-the-performance-schema-and-sys-schema">Querying the performance schema and sys schema</h3>-->

### <a class="anchor" id="querying-the-performance-schema-and-sys-schema"></a>Querying the performance schema and sys schema

> Server status variables by and large capture high-level server activity. To collect metrics at the query level, such as query latency and query errors, you can use the MySQL [performance schema][performance-schema], which captures detailed statistics on server events.

Server status variablesは、概して、サーバーアクティビティの概要的な情報を収集しています。"クエリーレイテンシー"や"クエリーエラー"などの、クエリーレベルのメトリクスを収集するには、サーバーイベントに関し詳細な統計情報を集取しているMySQL [performance schema][performance-schema]を使うことができます。


#### Enabling the performance schema

> To enable the performance schema, you must set the `performance_schema` parameter to 1 in the database instance's parameter group using [the AWS console][rds-console]. This change requires an instance reboot.
>
> Once it is enabled, the performance schema will collect metrics on all the statements executed by the server. Many of those metrics are summarized in the `events_statements_summary_by_digest` table, available in MySQL 5.6 and later. The digest normalizes all the statements, ignoring data values and standardizing whitespace, so that the following two queries [would be considered the same][digest]:

performance schemaを有効にするには、AWSコンソールから該当するデータベース・インスタンスのパラメータグループ内の`performance_schema`項目を1にする必要があります。この変更には、インスタンスの再起動が必要です。

この設定が有効になると、performance schemaは、サーバによって実行されたすべてのステートメントに関するメトリックを収集します。performance schemaのメトリックの多くは、MySQLの5.6以降で利用可能になった`events_statements_summary_by_digest`の表にまとめられています。この`events_statements_summary_by_digest`では、全てのステートメントのデータ値は無視され、空白は取り除かれて正規化の処理が施されます。従って、次の二つのクエリーは、[同じモノとして処理されます][digest]:


<pre class="lang:mysql">
SELECT * FROM orders WHERE customer_id=10 AND quantity>20
SELECT * FROM orders WHERE customer_id = 25 AND quantity > 100
</pre>

> The performance schema captures information about latency, errors, and query volume for each normalized statement. A sample row from the `events_statements_summary_by_digest` table shows an expensive query that takes multiple seconds to execute (all timer measurements are in picoseconds):

performance schemaは、先に示した正規化の規則に基づいて分類したステートメント毎に、レイテンシー, エラー, クエリー数に関する情報を取得しています。以下のサンプル行は、`events_statements_summary_by_digest`の表から抽出した、実行コストの高価(実行に数秒間かかる)なクエリーを表示しています(時間の単位は、ピコ秒):


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

<!--<h4 class="anchor" id="using-the-sys-schema">Using the sys schema</h4>-->

#### <a class="anchor" id="using-the-sys-schema"></a>Using the sys schema

> Though the performance schema can be queried directly, it is usually easier to extract meaningful views of the data using the [sys schema][sys-schema], which provides a number of useful tables, functions, and procedures for parsing your data.

> To install the sys schema, first clone the [mysql-sys][sys-schema] GitHub repo to the machine that you use to connect to your MySQL instance (e.g., an EC2 instance in the same security group) and position yourself within the newly created directory:

performance schemaに直接照会することはできます。しかし、[sys schema][sys-schema]の便利な関数や表、データーパース手順を使用した方が、データーから簡単に価値の高い検分を得ることができます。

sys schemaをインストールするには、まずは、MySQLインスタンスに接続に使用するマシン(例: 同一セキュリティグループに起動したEC2インスタンス)に、GitHubのリポから[mysql-sys][sys-schema]をクローンします。そして、新しく作成したディレクトリ内に移動します:


<pre class="lang:sh">
git clone https://github.com/MarkLeith/mysql-sys.git
cd mysql-sys
</pre>

> Then, run a shell script within the mysql-sys repo that creates an RDS-compatible file for the sys schema. For MySQL version 5.6, the command and output looks like:

そして、mysql-sysリポディレクトの中でシェルスクリプトを実行し、sys schemaのRDS互換ファイルを作成します。ySQLバージョン5.6の場合、コマンドとその出力は、次のようになります。


<pre class="lang:sh">
$ ./generate_sql_file.sh -v 56 -b -u CURRENT_USER
Wrote file: /home/ec2-user/mysql-sys/gen/sys_1.5.0_56_inline.sql
Object Definer: CURRENT_USER
sql_log_bin: disabled
</pre>

> Finally, you must load the newly created file into MySQL, using the filename returned in the step above:

最後に、上記のステップで取得したファイル名を使って、新しく作成されたファイルをMySQLにアップロードする必要があります。


<pre class="lang:sh">
mysql -h instance-name.xxxxxx.us-east-1.rds.amazonaws.com -P 3306 -u yourusername -p < gen/sys_1.5.0_56_inline.sql
</pre>

> Now, when you access your database instance using the mysql command line tool, you will have access to the sys schema and all the views within. The [sys schema documentation][sys-schema] provides information on the various tables and functions, along with a number of useful examples. For instance, to summarize all the statements executed, along with their associated latencies:

ここで、mysqlコマンドラインツールを使用して、データベース・インスタンスにアクセスすると、sys schemaとそれが提供しているビューにアクセスすることができるようになっているはずです。
[sys schemaのドキュメント][sys-schema]には、多くの例と共に、各種の表や関数の情報が掲載されています。例えば、実行された全てのステートメントとそれに関連したレイテンシーは、次のようにサマライズできます:


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

<!--<h3 class="anchor" id="using-the-mysql-workbench-gui">Using the MySQL Workbench GUI</h3>-->

### <a class="anchor" id="using-the-mysql-workbench-gui"></a>Using the MySQL Workbench GUI

> [MySQL Workbench][workbench] is a free application with a GUI for managing and monitoring a MySQL instance. MySQL Workbench provides a high-level performance dashboard, as well as an easy-to-use interface for browsing performance metrics (using the views provided by the [sys schema](#using-the-sys-schema)).

[MySQL Workbench][workbench]は、MySQLインスタンスを管理し、監視するためのGUI付き無料アプリケーションです。MySQL Workbenchは、パフォーマンスの概要についてのダッシュボード、ならびに、performance metricsを閲覧するための使いやすいインターフェース([sys schema](#using-the-sys-schema)のビューを使った)を提供します。


<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/workbench-2.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/workbench-2.png"></a>

> If you have [configured an EC2](#connecting-to-your-rds-instance) instance to communicate with MySQL running on RDS, you can connect MySQL Workbench to your MySQL on RDS via SSH tunneling:

RDS上のMySQLと通信するように[EC2インスタンスを設定](#connecting-to-your-rds-instance)している場合、SSHトンネリングを介してRDS上のMySQLへMySQL Workbenchを接続することができます:


<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/ssh_tunneling-2.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/ssh_tunneling-2.png"></a>

> You can then view recent metrics on the performance dashboard or click through the statistics available from the sys schema:

パフォーマンスダッシュボード上で、最新のメトリックを表示したり、sys schema提供されているから統計を閲覧することができます：


<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/95th_percentile-2.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/95th_percentile-2.png"></a>

<!--<h3 class="anchor" id="using-a-mysql-monitoring-tool">Using a MySQL monitoring tool</h3>-->

### <a class="anchor" id="using-a-mysql-monitoring-tool"></a>Using a MySQL monitoring tool

> The fourth way to access MySQL's native metrics is to use a full-featured monitoring tool that integrates with MySQL. Such tools allow you to not only glimpse a real-time snapshot of your metrics but to visualize and analyze your metrics' evolution over time, and to set alerts to be notified when key metrics go out of bounds. Comprehensive monitoring tools also allow you to correlate your metrics across systems, so you can quickly determine if errors from your application can be traced back to MySQL, or if increased MySQL latency is caused by system-level resource contention. [Part 3][part-3] of this series demonstrates how you can set up comprehensive monitoring of MySQL on RDS with Datadog.

MySQLのネイティブメトリクスにアクセスするための第四の方法は、MySQLと総合的に連携できるフル装備の監視ツールを使用することです。このようなツールは、メトリクスのリアルタイムスナップショットを見ることができるだけでなく、メトリクスの時間をかけた変化を可視化し分析することができ、キーメトリクスが規定値を超えた場合に通知するためのアラートを設定することができます。更に、総合的な監視ツールは、各システムの間でメトリクスを相関することができ、アプリから出ているエラーがMySQLに起因しているかを判断できたり、MySQLのレイテンシーがシステムレベルのリソースの競合によって引き起こされている可能性を判断できたりします。このシリーズの[Part 3][part-3]では、RDS上のMySQLの包括的な監視を、Datadogを使って実現する方法を紹介します。

## Conclusion

> In this post we have walked through how to use CloudWatch to collect and visualize RDS metrics, and how to generate alerts when these metrics go out of bounds. We've also shown you how to collect more detailed metrics from MySQL itself, whether on an ad hoc or continuous basis.
>
> In [the next and final part][part-3] of this series, we'll show you how you can set up Datadog to collect, visualize, and set alerts on metrics from both RDS and MySQL.

この記事では、CloudWatchを使ってRDSのメトリックを収集し、視覚化する方法と、メトリクスが閾値を超えた場合にアラートを発生させる方法を解説してきました。更に、MySQL自体から、必要に応じて単発的や継続的に、より詳細なメトリクスを収集する方法を紹介していきました。

このシリーズの[最後のPart 3][part-3]では、Datadogを使って、RDSとMySQL自体の両方からメトリクスを収集し、可視化し、アラートを設定する方法を紹介します。


## Acknowledgments

> We are grateful to have had input on this series from Baron Schwartz, whose company [VividCortex][vivid] provides a query-centric view of database performance.

クエリーを使ったデータベースパフォーマンスの把握を行っている[VividCortex][vivid]社のBaron Schwartz氏より、このシリーズにアドバイスを頂けたことを感謝しています。


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
