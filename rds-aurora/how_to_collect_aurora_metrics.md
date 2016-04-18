*This post is part 2 of a 3-part series on monitoring Amazon Aurora. [Part 1][part-1] explores key Aurora performance metrics, and [Part 3][part-3] describes how you can use Datadog to get a full view of your Aurora cluster.*

As covered in [Part 1][part-1] of this series, [Aurora][aurora] users can access metrics from the Relational Database Service (RDS) via Amazon CloudWatch and many additional metrics from the MySQL-compatible database engine itself. Each metric type gives you different insights into Aurora performance; ideally both RDS and engine metrics should be collected for a comprehensive view. This post will explain how to collect both metric types.

## Collecting RDS metrics

RDS metrics can be accessed from CloudWatch in three different ways:

-   [Using the AWS Management Console and its web interface](#using-the-aws-console)
-   [Using the command line interface](#using-the-command-line-interface)
-   [Using a monitoring tool with a CloudWatch integration](#using-a-monitoring-tool-with-a-cloudwatch-integration)

<h3 class="anchor" id="using-the-aws-console">Using the AWS Console</h3>

Using the online management console is the simplest way to monitor RDS with CloudWatch. The AWS Console allows you to set up simple automated alerts and get a visual picture of recent changes in individual metrics.

#### Graphs

Once you are signed in to your AWS account, you can open the [CloudWatch console][aws-console] where you will see the metrics related to the different AWS services.

By selecting RDS from the list of services and clicking on "Per-Database Metrics," you will see your database instances, along with the available metrics for each:

<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-11-aurora/aurora-metrics-cloudwatch.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-11-aurora/aurora-metrics-cloudwatch.png"></a>
Just select the checkbox next to the metrics you want to visualize, and they will appear in the graph at the bottom of the console.

<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-11-aurora/dml-latency.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-11-aurora/dml-latency.png"></a>
#### Alerts

With the CloudWatch console you can also create alerts that trigger when a metric threshold is crossed.

To set up an alert, click on the "Create Alarm" button at the right of your graph and configure the alarm to notify a list of email addresses:

<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-11-aurora/cloudwatch-alarm.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-11-aurora/cloudwatch-alarm.png"></a>

<h3 class="anchor" id="using-the-command-line-interface">Using the command line interface</h3>

You can also retrieve metrics related to your database instance using the command line. Command line queries can be useful for spot checks and ad hoc investigations. To do so, you will need to [install and configure the CloudWatch command line interface][aws-cli]. You will then be able to query for any CloudWatch metrics you want, using different parameters.

For example, if you want to check the `SelectLatency` metric across a one-hour window on your Aurora instance, you can run:

<pre class="lang:sh">
mon-get-stats SelectLatency
    --namespace="AWS/RDS"
    --dimensions="DBInstanceIdentifier=instance-name"
    --statistics Maximum
    --start-time 2015-11-18T17:00:00
    --end-time 2015-11-18T18:00:00
</pre>

The `mon-get-stats` query will return output like this—one data point per line:

<pre class="lang:sh">
2015-11-18 17:00:00  0.41718811881188117  Milliseconds
2015-11-18 17:01:00  0.42630927835051546  Milliseconds
2015-11-18 17:02:00  0.4364315789473684   Milliseconds
2015-11-18 17:03:00  0.42962886597938144  Milliseconds
2015-11-18 17:04:00  0.44160000000000005  Milliseconds
2015-11-18 17:05:00  0.4355894736842105   Milliseconds
...
</pre>

Full usage details for the `mon-get-stats` command are available [in the AWS documentation][mon-get-stats].

<h3 class="anchor" id="using-a-monitoring-tool-with-a-cloudwatch-integration">Using a monitoring tool with a CloudWatch integration</h3>

The third way to collect CloudWatch metrics is via your own monitoring tools, which can offer extended monitoring functionality. For instance, if you want to correlate metrics from your database with other parts of your infrastructure (including the applications that depend on that database), or you want to dynamically slice, aggregate, and filter your metrics on any attribute, or you need dynamic alerting mechanisms, you probably need a dedicated monitoring system. Monitoring tools that seamlessly integrate with the CloudWatch API can, with a single setup process, collect metrics from across your AWS infrastructure.

In [Part 3][part-3] of this series, we walk through how you can easily collect, visualize, and alert on any Aurora RDS metric using Datadog.

## Collecting database engine metrics

CloudWatch offers several high-level metrics for any database engine, but to get a deeper look at Aurora performance you will often need [metrics from the database instance itself][part-1]. Here we will focus on four methods for metric collection:

-   [Querying server status variables](#querying-server-status-variables)
-   [Querying the performance schema and sys schema](#querying-the-performance-schema-and-sys-schema)
-   [Using the MySQL Workbench GUI](#using-the-mysql-workbench-gui)
-   [Using a MySQL-compatible monitoring tool](#using-a-mysql-monitoring-tool)

<h3 class="anchor" id="querying-server-status-variables">Querying server status variables</h3>
<h4 class="anchor" id="connecting-to-your-rds-instance">Connecting to your RDS instance</h4>
As with all RDS instances, you cannot directly access the machines running Aurora. So you cannot run `mysql` commands locally or check CPU utilization from the machine itself, as you could if you manually installed MySQL or MariaDB on a standalone EC2 instance. That said, you _can_ connect to Aurora remotely using standard tools, provided that the security group for your Aurora instance permits connections from the device or EC2 instance you are using to initiate the connection.

<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-11-aurora/aurora_diagram_2.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-11-aurora/aurora_diagram_2.png"></a>

For example, if Aurora accepts traffic only from inside its security group, you can launch an EC2 instance in that security group, and then apply a second security group rule to the EC2 instance to accept inbound SSH traffic (*see diagram above*). Then you can SSH to the EC2 instance, from which you can connect to Aurora using the standard mysql command line tool:

<pre class="lang:sh">
mysql -h instance-name.xxxxxx.us-east-1.rds.amazonaws.com -P 3306 -u yourusername -p
</pre>

The instance endpoint (ending in `rds.amazonaws.com`) can be found in the list of instances on the [RDS console][rds-console].

Once you connect to your database instance, you can query any of the hundreds of metrics available from the MySQL-compatible database engine, known as [server status variables][ssv]. To check metrics on connection errors, for instance:

<pre class="lang:mysql">
mysql> SHOW GLOBAL STATUS LIKE '%Connection_errors%';
</pre>

<h3 class="anchor" id="querying-the-performance-schema-and-sys-schema">Querying the performance schema and sys schema</h3>
Server status variables by and large capture high-level server activity. To collect metrics at the query level—for instance, to link latency or error metrics to individual queries—you can use the [performance schema][performance-schema], which captures detailed statistics on server events.

#### Enabling the performance schema

To enable the performance schema, you must set the `performance_schema` parameter to 1 in the database instance's parameter group using [the AWS console][rds-console]. This change requires an instance reboot.

Once it is enabled, the performance schema will collect metrics on all the statements executed by the server. Many of those metrics are summarized in the `events_statements_summary_by_digest` table. The digest normalizes all the statements, ignoring data values and standardizing whitespace, so that the following two queries [would be considered the same][digest]:

<pre class="lang:mysql">
SELECT * FROM orders WHERE customer_id=10 AND quantity>20
SELECT * FROM orders WHERE customer_id = 25 AND quantity > 100
</pre>

The performance schema captures information about latency, errors, and query volume for each normalized statement. A sample row from the `events_statements_summary_by_digest` table shows an expensive query that takes multiple seconds to execute (all timer measurements are in picoseconds):

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

To install the sys schema, first clone the [mysql-sys][sys-schema] GitHub repo to the machine that you use to connect to your Aurora instance (e.g., an EC2 instance in the same security group) and position yourself within the newly created directory:

<pre class="lang:sh">
git clone https://github.com/MarkLeith/mysql-sys.git
cd mysql-sys
</pre>

Then, run a shell script within the mysql-sys repo that creates an Aurora-compatible file for the sys schema. As of this writing Aurora is only compatible with MySQL version 5.6, so you must use the version parameter `-v 56`. The command and output looks like:

<pre class="lang:sh">
$ ./generate_sql_file.sh -v 56 -b -u CURRENT_USER
Wrote file: /home/ec2-user/mysql-sys/gen/sys_1.5.0_56_inline.sql
Object Definer: CURRENT_USER
sql_log_bin: disabled
</pre>

Finally, you must load the newly created file into Aurora with the mysql command line tool, using the filename returned in the step above:

<pre class="lang:sh">
mysql -h instance-name.xxxxxx.us-east-1.rds.amazonaws.com -P 3306 -u yourusername -p < gen/sys_1.5.0_56_inline.sql
</pre>

Now, when you access your database instance using the mysql command line tool, you will have access to the sys schema and all the views within. The [sys schema documentation][sys-schema] provides information on the various tables and functions, along with a number of useful examples. For instance, to summarize all the statements executed, along with their associated latencies:

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
[MySQL Workbench][workbench] is a free application with a GUI for managing and monitoring MySQL or a compatible database such as Aurora. MySQL Workbench provides a high-level performance dashboard, as well as an easy-to-use interface for browsing performance metrics (using the views provided by the [sys schema](#using-the-sys-schema)).

<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/workbench-2.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/workbench-2.png"></a>

If you have [configured an EC2](#connecting-to-your-rds-instance) instance to communicate with Aurora, you can connect MySQL Workbench to your Aurora instance via SSH tunneling:

<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-11-aurora/ssh-tunnel.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-11-aurora/ssh-tunnel.png"></a>
You can then view recent metrics on the performance dashboard or click through the statistics available from the sys schema:

<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/95th_percentile-2.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/95th_percentile-2.png"></a>

<h3 class="anchor" id="using-a-mysql-monitoring-tool">Using a MySQL-compatible monitoring tool</h3>
The fourth way to access Aurora's database engine metrics is to use a full-featured monitoring tool that integrates with MySQL. Such tools allow you to not only glimpse a real-time snapshot of your metrics but to visualize and analyze your metrics' evolution over time, and to set alerts to be notified when key metrics go out of bounds. Comprehensive monitoring tools also allow you to correlate your metrics across systems, so you can quickly determine if errors from your application can be traced back to Aurora, or if increased query latency is caused by system-level resource contention. [Part 3][part-3] of this series demonstrates how you can set up comprehensive Aurora monitoring with Datadog.

## Conclusion

In this post we have walked through how to use CloudWatch to collect and visualize Aurora metrics, and how to generate alerts when these metrics go out of bounds. We've also shown you how to collect more detailed metrics from the database engine itself using MySQL-compatible tools, whether on an ad hoc or continuous basis.

In [the next and final part][part-3] of this series, we'll show you how you can set up Datadog to collect, visualize, and set alerts on metrics from both RDS and Aurora's database engine.

- - -

*Source Markdown for this post is available [on GitHub][markdown]. Questions, corrections, additions, etc.? Please [let us know][issues].*

[aurora]: https://aws.amazon.com/rds/aurora/
[markdown]: https://github.com/DataDog/the-monitor/blob/master/rds-aurora/how_to_collect_aurora_metrics.md
[issues]: https://github.com/DataDog/the-monitor/issues
[part-1]: https://www.datadoghq.com/blog/monitoring-amazon-aurora-performance-metrics
[part-3]: https://www.datadoghq.com/blog/monitor-aurora-using-datadog
[aws-console]: https://console.aws.amazon.com/cloudwatch/home
[rds-console]: https://console.aws.amazon.com/rds/
[aws-cli]: https://aws.amazon.com/developertools/2534
[mon-get-stats]: http://docs.aws.amazon.com/AmazonCloudWatch/latest/cli/cli-mon-get-stats.html
[ssv]: https://dev.mysql.com/doc/refman/5.6/en/server-status-variables.html
[performance-schema]: http://dev.mysql.com/doc/refman/5.6/en/performance-schema.html
[digest]: https://dev.mysql.com/doc/refman/5.6/en/performance-schema-statement-digests.html
[sys-schema]: https://github.com/MarkLeith/mysql-sys/
[workbench]: http://dev.mysql.com/downloads/workbench/
