# Monitoring RDS MySQL performance metrics

*This post is part 1 of a 3-part series about monitoring MySQL on Amazon RDS. [Part 2][part-2] is about collecting metrics from both RDS and MySQL, and [Part 3][part-3] details how to monitor MySQL on RDS with Datadog.*

## What is RDS?

Amazon Relational Database Service (RDS) is a hosted database service in the AWS cloud. RDS users can choose from several relational database engines, including MySQL, Oracle, SQL Server, Postgres, MariaDB, and Amazon Aurora, a new MySQL-compatible database built for RDS. This article focuses on the original RDS database engine: MySQL. 

## Key metrics for MySQL on RDS

To keep your applications running smoothly, it is important to understand and track performance metrics in the following areas:

* [Query throughput](#query-throughput)
* [Query performance](#query-performance)
* [Resource utilization](#resource-utilization)
* [Connections](#connection-metrics)
* [Read replica metrics](#read-replica-metrics)

Users of MySQL on RDS have access to hundreds of metrics, but it's not always easy to tell what you should focus on. In this article we'll highlight key metrics in each of the above areas that together give you a detailed view of your database's performance. 

RDS metrics (as opposed to MySQL metrics) are available through Amazon CloudWatch, and are available regardless of which database engine you use. MySQL metrics, on the other hand, must be accessed from the database instance itself. [Part 2 of this series][part-2] explains how to collect both types of metrics. 

Most of the performance metrics outlined here also apply to Aurora and MariaDB on RDS, but there are some key differences between the database engines. For instance, Aurora has auto-scaling storage and therefore does not expose a metric tracking free storage space. And the version of MariaDB (10.0.17) available on RDS at the time of this writing is not fully compatible with the MySQL Workbench tool or the sys schema, both of which are detailed in [Part 2][part-2] of this series.

This article references metric terminology introduced in [our Monitoring 101 series][metric-101], which provides a framework for metric collection and alerting.

<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-mysql-rds/rds-dash-load.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-mysql-rds/rds-dash-load.png"></a> 

<h3 class="anchor" id="query-throughput">Query throughput</h3>

| **Name** | **Description** | [**Metric&nbsp;type**][metric-101] | **Availability** |
|:--------:|:---------------:|:---------------:|:------------:|
| Questions | Count of executed statements (sent by client only) | Work: Throughput | MySQL |
| Queries | Count of executed statements (sent by client or executed within stored programs) | Work: Throughput | MySQL | 
| Reads (calculated) | Selects + Query cache hits | Work: Throughput | MySQL |
| Writes (calculated) | Inserts + Updates + Deletes | Work: Throughput | MySQL |

Your primary concern in monitoring any system is making sure that its [work is being done][collecting-data] effectively. A database's work is running queries, so the first priority in any monitoring strategy should be making sure that queries are being executed.

The MySQL server status variable `Questions` is incremented for all statements sent by client applications. The similar metric `Queries` is a more all-encompassing count that includes statements executed as part of [stored programs][stored], as well as commands such as `PREPARE` and `DEALLOCATE PREPARE`, which are run as part of server-side [prepared statements][prepared]. For most RDS deployments, the client-centric view makes `Questions` the more valuable metric.

You can also monitor the breakdown of read and write commands to better understand your database's read/write balance and identify potential bottlenecks. Those metrics can be computed by summing native MySQL metrics. Reads increment one of two status variables, depending on whether or not the read is served from the query cache:

    Reads = `Com_select` + `Qcache_hits`

Writes increment one of three status variables, depending on the command:

    Writes = `Com_insert` + `Com_update` + `Com_delete`

#### Metric to alert on: Questions

The current rate of queries will naturally rise and fall, and as such is not always an actionable metric based on fixed thresholds alone. But it is worthwhile to alert on sudden changes in query volume—drastic drops in throughput, especially, can indicate a serious problem.

<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-mysql-rds/questions_2.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-mysql-rds/questions_2.png"></a> 
 

<h3 class="anchor" id="query-performance">Query performance</h3>

| **Name** | **Description** | [**Metric&nbsp;type**][metric-101] | **Availability** |
|:--------:|:---------------:|:---------------:|:------------:|
| Slow_queries | Number of queries exceeding configurable `long_query_time` limit | Work: Performance | MySQL |
| Query errors | Number of SQL statements that generated errors | Work: Error | MySQL* |
_*The count of query errors is not exposed directly as a MySQL metric, but can be gathered by a MySQL query._

Amazon's CloudWatch exposes `ReadLatency` and `WriteLatency` metrics for RDS (discussed [below](#resource-utilization)), but those metrics only capture latency at the disk I/O level. For a more holistic view of query performance, you can dive into native MySQL metrics for query latency. MySQL features a `Slow_queries` metric, which increments every time a query's execution time exceeds the number of seconds specified by the `long_query_time` parameter. `long_query_time` is set to 10 seconds by default but can be modified in the AWS Console. To modify  `long_query_time` (or any other MySQL parameter), simply log in to the Console, navigate to the RDS Dashboard, and select the parameter group that your RDS instance belongs to. You can then filter to find the parameter you want to edit.

<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-mysql-rds/long_query_time.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-mysql-rds/long_query_time.png"></a> 

MySQL's performance schema (when enabled) also stores valuable statistics, including query latency, from the database server. Though you can query the performance schema directly, it is easier to use Mark Leith’s [sys schema][sys-schema], which provides convenient views, functions, and procedures to gather metrics from MySQL. For instance, to find the execution time of all the different statement types executed by each user:

<pre class="lang:mysql">
mysql> select * from sys.user_summary_by_statement_type;
</pre>

Or, to find the slowest statements (those in the 95th percentile by runtime):

<pre class="lang:mysql">
mysql> select * from sys.statements_with_runtimes_in_95th_percentile\G
</pre>

Many useful usage examples are detailed in the sys schema [documentation][sys-schema].

To enable the performance schema, you must set the `performance_schema` parameter to 1 in the database instance's parameter group using the AWS console. If not enabled, this change requires an instance reboot. More about enabling the performance schema and installing the sys schema in [Part 2][part-2] of this series.

If your queries are executing more slowly than expected,  evaluate your [resource metrics](#resource-utilization) and MySQL metrics that track how often operations have been blocked on acquiring a lock. In particular, check the `Innodb_row_lock_waits` metric, which counts how often InnoDB (the default storage engine for MySQL on RDS) had to wait to acquire a row lock.

MySQL users also have a number of caching options to expedite transactions, from making more RAM available for the [buffer pool][buffer-pool] used by InnoDB (MySQL's default storage engine), to enabling the [query cache][query-cache] to serve identical queries from memory, to using an application-level cache such as memcached or [Redis][redis].

The performance schema and sys schema also allow you to quickly assess how many queries generated errors or warnings:

<pre class="lang:mysql">
mysql> SELECT SUM(errors) FROM sys.statements_with_errors_or_warnings;
</pre>

#### Metrics to alert on

* `Slow_queries`: How you define a slow query (and therefore how you configure the `long_query_time` parameter) will depend heavily on your use case and performance requirements. If the number of slow queries reaches worrisome levels, you will likely want to identify the actual queries that are executing slowly so you can optimize them. You can do this by querying the sys schema or by configuring MySQL to log all slow queries. More information on enabling and accessing the slow query log is available [in the RDS documentation][slow-log]. <pre class="lang:mysql">mysql> select * from mysql.slow_log\G
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

* Query errors: A sudden increase in query errors can indicate a problem with your client application or your database. You can use the sys schema to quickly explore which queries may be causing problems. For instance, to list the 10 normalized statements that have returned the most errors:<pre class="lang:mysql">mysql> SELECT * FROM sys.statements_with_errors_or_warnings ORDER BY errors DESC LIMIT 10\G</pre>

<h3 class="anchor" id="resource-utilization">Resource utilization</h3>

#### Disk I/O metrics
| **Description** | **CloudWatch name** | **Enhanced monitoring name** | [**Metric&nbsp;type**][metric-101] |
|:--------:|:---------------:|:---------------:|:------------:|
| Read I/O operations per second | ReadIOPS | diskIO.readIOsPS | Resource: Utilization | 
| Write I/O operations per second | WriteIOPS | diskIO.writeIOsPS | Resource: Utilization | 
| I/O operations waiting for disk access | DiskQueueDepth | diskIO.avgQueueLen | Resource: Saturation | 
| Milliseconds per read I/O operation | ReadLatency | - | Resource: Other | 
| Milliseconds per write I/O operation | WriteLatency | - | Resource: Other | 

#### CPU, memory, storage, and network metrics
| **Description** | **CloudWatch name** | **Enhanced monitoring name** | [**Metric&nbsp;type**][metric-101] |
|:--------:|:---------------:|:---------------:|:------------:|
| Percent CPU utilized | CPUUtilization | cpuUtilization.total | Resource: Utilization |
| Available RAM in gigabytes | FreeableMemory | memory.free | Resource: Utilization | 
| Swap usage | SwapUsage | swap.cached | Resource: Saturation |
| Available storage in bytes | FreeStorageSpace | - | Resource: Utilization | 
| Network traffic to the MySQL instance | NetworkReceive<br>Throughput (bytes/s) | network.rx (packets) | Resource: Utilization | 
| Network traffic from the MySQL instance | NetworkTransmit<br>Throughput (bytes/s) | network.tx (packets) | Resource: Utilization | 

As Baron Schwartz, co-author of *[High Performance MySQL][mysql-book],* often notes, a database needs four fundamental resources: CPU, memory, disk, and network. Any of these can become a performance bottleneck—for a look at how difference RDS instance types can be constrained by their available resources, check out [this 2013 talk][bottlenecks] by Amazon's Grant McAlister. 

Whenever your database instance experiences performance problems, you should check metrics pertaining to the four fundamental resources to look for bottlenecks. As of December 2015, RDS users have access to [enhanced monitoring][enhanced] functionality that exposes detailed system-level metrics for RDS instances. These enhanced metrics can be reported at frequencies as high as once per second. Even out of the box, however, CloudWatch does make available basic metrics, detailed below, on all four fundamental resources. For the most part, these metrics are most useful for [investigating (rather than detecting)][investigation] performance issues.

<h4 class="anchor" id="disk-i/o-metrics">Disk I/O metrics</h4>

CloudWatch makes available RDS metrics on read and write IOPS. These metrics are useful for monitoring the performance of your database and to ensure that your IOPS do not exceed the limits of your chosen instance type. If you are running an RDS instance in production, you will likely want to choose Provisioned IOPS storage to ensure consistent performance. 

If your storage volumes cannot keep pace with the volume of read and write requests, you will start to see I/O operations queuing up. The `DiskQueueDepth` metric measures the length of this queue at any given moment.

Note that there will not be a one-to-one correspondence between queries and disk operations—queries that can be served from memory will bypass disk, for instance, and queries that return a large amount of data can involve more than one I/O operation. Specifically, reading or writing more than 16 KB, the [default page size][iops] for MySQL, will require multiple I/O operations.

In addition to I/O throughput metrics, RDS offers `ReadLatency` and `WriteLatency` metrics. These metrics do not capture full query latency—they only measure how long your I/O operations are taking at the disk level. 

For read-heavy applications, one way to overcome I/O limitations is to [create a read replica][read-replica] of the database to serve some of the client read requests. For more, see the [section below](#read-replica-metrics) on metrics for read replicas.

#### CPU metrics

High CPU utilization is not necessarily a bad sign. But if your database is performing poorly while it is within its IOPS and network limits, and while it appears to have sufficient memory, the CPUs of your chosen instance type may be the bottleneck.

#### Memory metrics

MySQL performs best when most of its working set of data can be held in memory. For this reason, you should monitor `FreeableMemory` and `SwapUsage` to ensure that your database instance is not memory-constrained.

AWS advises that you monitor `ReadIOPS` when the database is under load to ensure that your database instance has enough RAM to [keep the working set almost entirely in memory][working-set]:

> The value of ReadIOPS should be small and stable. If scaling up the DB instance class—to a class with more RAM—results in a dramatic drop in ReadIOPS, your working set was not almost completely in memory.

<h4 class="anchor" id="storage-metrics">Storage metrics</h4>

RDS allows you to allocate a fixed amount of storage when you launch your MySQL instance. The CloudWatch metric `FreeStorageSpace` lets you monitor how much of your allocated storage is still available. Note that you can always add more storage by modifying your running database instance in the AWS console, but you may not decrease it. 

#### Network metrics

RDS relies on Amazon Elastic Block Store (Amazon EBS) volumes for storage, and the network connection to EBS can limit your throughput. Monitoring `NetworkReceiveThroughput` and `NetworkTransmitThroughput` will help you identify potential network bottlenecks.

Even with Provisioned IOPS, it is entirely possible that network limitations will keep your realized IOPS below your provisioned maximum. For instance, if you provision 10,000 IOPS on a db.r3.2xlarge database instance, but your use case is extremely read-heavy, you will reach the bandwidth limit of 1 gigabit per second (roughly 8,000 IOPS) to EBS in each direction before hitting the provisioned limits of your storage.

#### Metrics to alert on

* `ReadLatency` or `WriteLatency`: Monitoring the latency of your disk operations is critical to identify potential constraints in your MySQL instance hardware or your database usage patterns. If your latency starts to climb, check your IOPS, disk queue, and network metrics to see if you are pushing the bounds of your instance type. If so, consult the RDS documentation for details about [storage options][storage], including volumes with provisioned IOPS rates. 

* `DiskQueueDepth`: It is not unusual to have some requests in the disk queue, but investigation may be in order if this metric starts to climb, especially if latency increases as a result. (Time spent in the disk queue adds to read and write latency.)

* `FreeStorageSpace`: AWS recommends that RDS users take action to delete unneeded data or add more storage if disk usage consistently reaches levels of 85 percent or more.  

<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-mysql-rds/latency.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-mysql-rds/latency.png"></a> 

<h3 class="anchor" id="connection-metrics">Connection metrics</h3>

| **Name** | **Description** | [**Metric&nbsp;type**][metric-101] | **Availability** |
|:--------:|:---------------:|:---------------:|:------------:|
| DatabaseConnections | Currently open connections | Resource: Utilization | CloudWatch |
| Threads_connected | Currently open connections | Resource: Utilization | MySQL |
| Threads_running | Currently running connections | Resource: Utilization | MySQL |
| Aborted_connects | Count of failed connection attempts to the server | Resource: Error | MySQL |
| Connection_errors_<br>internal | Count of connections refused due to server error | Resource: Error | MySQL |
| Connection_errors_<br>max_connections | Count of connections refused due to `max_connections` limit | Resource: Error | MySQL |

Monitoring how many client connections are in use is critical to understanding your database's activity and capacity. MySQL has a configurable connection limit; on RDS the default value depends on the memory of the database's instance class in bytes, according to the formula: 
    
`max_connections` = `DBInstanceClassMemory` / 12582880

The `max_connections` parameter can be modified by editing the database instance's parameter group using the RDS dashboard in the AWS console. You can also check the current value of `max_connections` by querying the MySQL instance itself (see [part 2][part-2] of this series for more on connecting to RDS instances directly):

<pre class="lang:mysql">
mysql> SELECT @@max_connections;
+-------------------+
| @@max_connections |
+-------------------+
|               100 |
+-------------------+
1 row in set (0.00 sec)
</pre>

To monitor how many connections are in use, CloudWatch exposes a `DatabaseConnections` metric tracking open RDS connections, and MySQL exposes a similar `Threads_connected` metric counting connection threads. (MySQL allocates one thread per connection.) Either metric will help you monitor your connections in use, but the MySQL metric can be collected at higher resolution than the CloudWatch metric, which is reported at one-minute intervals. MySQL also exposes the `Threads_running` metric to isolate the threads that are actively processing queries. 

If your server reaches the `max_connections` limit and starts to refuse connections, `Connection_errors_max_connections` will be incremented, as will the `Aborted_connects` metric tracking all failed connection attempts.

MySQL exposes a variety of other metrics on connection errors, which can help you identify client issues as well as serious issues with the database instance itself. The metric `Connection_errors_internal` is a good one to watch, because it is incremented when the error comes from the server itself. Internal errors can reflect an out-of-memory condition or the server's inability to start a new thread.

#### Metrics to alert on

* `Threads_connected`: If a client attempts to connect to MySQL when all available connections are in use, MySQL will return a "Too many connections" error and increment `Connection_errors_max_connections`. To prevent this scenario, you should monitor the number of open connections and make sure that it remains safely below the configured `max_connections` limit. 

* `Aborted_connects`: If this counter is increasing, your clients are probably trying and failing to connect to the database. Dig deeper with metrics such as `Connection_errors_max_connections` and `Connection_errors_internal` to diagnose the problem.

<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-mysql-rds/threads_connected_2.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-mysql-rds/threads_connected_2.png"></a> 

<h3 class="anchor" id="read-replica-metrics">Read replica metrics</h3>

| **Name** | **Description** | [**Metric&nbsp;type**][metric-101] | **Availability** |
|:--------:|:---------------:|:---------------:|:------------:|
| ReplicaLag | Number of seconds by which replica trails master | Other | CloudWatch |
| BinLogDiskUsage | Binary log disk usage on master, in bytes | Resource: Utilization | CloudWatch |

RDS supports the creation of read replicas from the master MySQL instance. A replica is read-only by default so that its data remains in sync with the master, but that setting can be modified to add an index to the replica—to support a certain type of query, for instance. 

These replicas are assigned a separate endpoint, so you can point client applications to read from a replica rather than from the source instance. You can also monitor the replica's connections, throughput, and query performance, just as you would for an ordinary RDS instance.

The lag time for any read replica is captured by the CloudWatch metric `ReplicaLag`. This metric is usually not actionable, although if the lag is consistently very long, you should investigate your settings and resource usage.

Another relevant metric for replication scenarios is `BinLogDiskUsage`, which measures the disk usage on the master database instance of binary logs. MySQL asynchronously replicates its data using a single thread on the master, so periods of high-volume writes cause pileups in the master's binary logs before the updates can be sent to the master.

<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-mysql-rds/binlog.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-mysql-rds/binlog.png"></a> 


## Conclusion

In this post we have explored the most important metrics you should monitor to keep tabs on performance for MySQL deployed on Amazon RDS. If you are just getting started with MySQL on RDS, monitoring the metrics listed below will give you great insight into your database’s activity and performance. They will also help you to identify when it is necessary to increase your instance storage, IOPS, or memory to maintain good application performance.

* [Query throughput](#query-throughput)
* [Query performance and errors](#query-performance)
* [Disk queue depth](#disk-i/o-metrics)
* [Storage space](#storage-metrics)
* [Client connections and errors](#connection-metrics)

[Part 2][part-2] of this series provides instructions for collecting all the metrics you need from CloudWatch and from MySQL.

## Acknowledgments

Many thanks to Baron Schwartz of [VividCortex][vivid] and to [Ronald Bradford][bradford] for reviewing and commenting on this article prior to publication.

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
[enhanced]: https://aws.amazon.com/blogs/aws/new-enhanced-monitoring-for-amazon-rds-mysql-5-6-mariadb-and-aurora/
