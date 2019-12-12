# Monitoring RDS MySQL performance metrics


*This post is part 1 of a 3-part series about monitoring MySQL on Amazon RDS. [Part 2](https://www.datadoghq.com/blog/how-to-collect-rds-mysql-metrics) is about collecting metrics from both RDS and MySQL, and [Part 3](https://www.datadoghq.com/blog/monitor-rds-mysql-using-datadog) details how to monitor MySQL on RDS with Datadog.*

What is RDS?
------------


Amazon Relational Database Service (RDS) is a hosted database service in the AWS cloud. RDS users can choose from several relational database engines, including MySQL, Oracle, SQL Server, Postgres, MariaDB, and Amazon Aurora, a new MySQL-compatible database built for RDS. This article focuses on the original RDS database engine: MySQL.

Key RDS MySQL performance metrics
---------------------------------


To keep your applications running smoothly, it is important to understand and track performance metrics in the following areas:



-   [Query throughput](#query-throughput)
-   [Query performance](#query-performance)
-   [Resource utilization](#resource-utilization)
-   [Connections](#connection-metrics)
-   [Read replica metrics](#read-replica-metrics)



Users of MySQL on RDS have access to hundreds of metrics, but it's not always easy to tell what you should focus on. In this article we'll highlight key metrics in each of the above areas that together give you a detailed view of your database's performance.

RDS metrics (as opposed to MySQL metrics) are available through Amazon CloudWatch, and are available regardless of which database engine you use. MySQL metrics, on the other hand, must be accessed from the database instance itself. [Part 2 of this series](https://www.datadoghq.com/blog/how-to-collect-rds-mysql-metrics) explains how to collect both types of metrics.

Most of the performance metrics outlined here also apply to Aurora and MariaDB on RDS, but there are some key differences between the database engines. For instance, Aurora has auto-scaling storage and therefore does not expose a metric tracking free storage space. And the version of MariaDB (10.0.17) available on RDS at the time of this writing is not fully compatible with the MySQL Workbench tool or the sys schema, both of which are detailed in [Part 2](https://www.datadoghq.com/blog/how-to-collect-rds-mysql-metrics) of this series.

This article references metric terminology introduced in [our Monitoring 101 series](https://www.datadoghq.com/blog/monitoring-101-collecting-data/), which provides a framework for metric collection and alerting.

{{< img src="rds-dash-load.png" alt="" popup="true" size="1x" >}}

### Query throughput




<table>
<thead>
<tr class="header">
<th><strong>Name</strong></th>
<th><strong>Description</strong></th>
<th><a href="https://www.datadoghq.com/blog/monitoring-101-collecting-data/"><strong>Metric type</strong></a></th>
<th><strong>Availability</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Questions</td>
<td>Count of executed statements (sent by client only)</td>
<td>Work: Throughput</td>
<td>MySQL</td>
</tr>
<tr class="even">
<td>Queries</td>
<td>Count of executed statements (sent by client or executed within stored programs)</td>
<td>Work: Throughput</td>
<td>MySQL</td>
</tr>
<tr class="odd">
<td>Reads (calculated)</td>
<td>Selects + Query cache hits</td>
<td>Work: Throughput</td>
<td>MySQL</td>
</tr>
<tr class="even">
<td>Writes (calculated)</td>
<td>Inserts + Updates + Deletes</td>
<td>Work: Throughput</td>
<td>MySQL</td>
</tr>
</tbody>
</table>



Your primary concern in monitoring any system is making sure that its [work is being done](https://www.datadoghq.com/blog/monitoring-101-collecting-data/#work-metrics) effectively. A database's work is running queries, so the first priority in any monitoring strategy should be making sure that queries are being executed.

The MySQL server status variable `Questions` is incremented for all statements sent by client applications. The similar metric `Queries` is a more all-encompassing count that includes statements executed as part of [stored programs](https://dev.mysql.com/doc/refman/5.6/en/stored-programs-views.html), as well as commands such as `PREPARE` and `DEALLOCATE PREPARE`, which are run as part of server-side [prepared statements](https://dev.mysql.com/doc/refman/5.6/en/sql-syntax-prepared-statements.html). For most RDS deployments, the client-centric view makes `Questions` the more valuable metric.

You can also monitor the breakdown of read and write commands to better understand your database's read/write balance and identify potential bottlenecks. Those metrics can be computed by summing native MySQL metrics. Reads increment one of two status variables, depending on whether or not the read is served from the query cache:

Reads = `Com_select` + `Qcache_hits`

Writes increment one of three status variables, depending on the command:

Writes = `Com_insert` + `Com_update` + `Com_delete`

#### Metric to alert on: Questions


The current rate of queries will naturally rise and fall, and as such is not always an actionable metric based on fixed thresholds alone. But it is worthwhile to alert on sudden changes in query volume—drastic drops in throughput, especially, can indicate a serious problem.

{{< img src="questions-2.png" alt="" popup="true" size="1x" >}}

### Query performance




<table>
<thead>
<tr class="header">
<th><strong>Name</strong></th>
<th><strong>Description</strong></th>
<th><a href="https://www.datadoghq.com/blog/monitoring-101-collecting-data/"><strong>Metric type</strong></a></th>
<th><strong>Availability</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Slow_queries</td>
<td>Number of queries exceeding configurable <code>long_query_time</code> limit</td>
<td>Work: Performance</td>
<td>MySQL</td>
</tr>
<tr class="even">
<td>Query errors</td>
<td>Number of SQL statements that generated errors</td>
<td>Work: Error</td>
<td>MySQL*</td>
</tr>
</tbody>
</table>



*\*The count of query errors is not exposed directly as a MySQL metric, but can be gathered by a MySQL query.*

Amazon's CloudWatch exposes `ReadLatency` and `WriteLatency` metrics for RDS (discussed [below](#resource-utilization)), but those metrics only capture latency at the disk I/O level. For a more holistic view of query performance, you can dive into native MySQL performance metrics for query latency. MySQL features a `Slow_queries` metric, which increments every time a query's execution time exceeds the number of seconds specified by the `long_query_time` parameter. `long_query_time` is set to 10 seconds by default but can be modified in the AWS Console. To modify `long_query_time` (or any other MySQL parameter), simply log in to the Console, navigate to the RDS Dashboard, and select the parameter group that your RDS instance belongs to. You can then filter to find the parameter you want to edit.

{{< img src="long-query-time.png" alt="" popup="true" size="1x" >}}

MySQL's performance schema (when enabled) also stores valuable statistics, including query latency, from the database server. Though you can query the performance schema directly, it is easier to use Mark Leith’s [sys schema](https://github.com/MarkLeith/mysql-sys/), which provides convenient views, functions, and procedures to gather metrics from MySQL. For instance, to find the execution time of all the different statement types executed by each user:




    mysql> select * from sys.user_summary_by_statement_type;
      
      



Or, to find the slowest statements (those in the 95th percentile by runtime):




    mysql> select * from sys.statements_with_runtimes_in_95th_percentile\G
      
      



Many useful usage examples are detailed in the sys schema [documentation](https://github.com/MarkLeith/mysql-sys/).

To enable the performance schema, you must set the `performance_schema` parameter to 1 in the database instance's parameter group using the AWS console. If not enabled, this change requires an instance reboot. More about enabling the performance schema and installing the sys schema in [Part 2](https://www.datadoghq.com/blog/how-to-collect-rds-mysql-metrics) of this series.

If your queries are executing more slowly than expected, evaluate your [resource metrics](#resource-utilization) and MySQL performance metrics that track how often operations have been blocked on acquiring a lock. In particular, check the `Innodb_row_lock_waits` metric, which counts how often InnoDB (the default storage engine for MySQL on RDS) had to wait to acquire a row lock.

MySQL users also have a number of caching options to expedite transactions, from making more RAM available for the [buffer pool](https://dev.mysql.com/doc/refman/5.6/en/innodb-buffer-pool.html) used by InnoDB (MySQL's default storage engine), to enabling the [query cache](https://dev.mysql.com/doc/refman/5.6/en/query-cache.html) to serve identical queries from memory, to using an application-level cache such as memcached or [Redis](https://www.datadoghq.com/blog/how-to-monitor-redis-performance-metrics/).

The performance schema and sys schema also allow you to quickly assess how many queries generated errors or warnings:




    mysql> SELECT SUM(errors) FROM sys.statements_with_errors_or_warnings;
      
      


#### Metrics to alert on




-   `Slow_queries`: How you define a slow query (and therefore how you configure the `long_query_time` parameter) will depend heavily on your use case and performance requirements. If the number of slow queries reaches worrisome levels, you will likely want to identify the actual queries that are executing slowly so you can optimize them. You can do this by querying the sys schema or by configuring MySQL to log all slow queries. More information on enabling and accessing the slow query log is available [in the RDS documentation](http://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_LogAccess.Concepts.MySQL.html#USER_LogAccess.MySQL.Generallog). 


        mysql> select * from mysql.slow_log\G          
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
          

    

-   Query errors: A sudden increase in query errors can indicate a problem with your client application or your database. You can use the sys schema to quickly explore which queries may be causing problems. For instance, to list the 10 normalized statements that have returned the most errors: 


        mysql> SELECT * FROM sys.statements_with_errors_or_warnings ORDER BY errors DESC LIMIT 10\G

    



### Resource utilization



#### Disk I/O metrics




<table>
<thead>
<tr class="header">
<th><strong>Description</strong></th>
<th><strong>CloudWatch name</strong></th>
<th><strong>Enhanced monitoring name</strong></th>
<th><a href="https://www.datadoghq.com/blog/monitoring-101-collecting-data/"><strong>Metric type</strong></a></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Read I/O operations per second</td>
<td>ReadIOPS</td>
<td>diskIO.readIOsPS</td>
<td>Resource: Utilization</td>
</tr>
<tr class="even">
<td>Write I/O operations per second</td>
<td>WriteIOPS</td>
<td>diskIO.writeIOsPS</td>
<td>Resource: Utilization</td>
</tr>
<tr class="odd">
<td>I/O operations waiting for disk access</td>
<td>DiskQueueDepth</td>
<td>diskIO.avgQueueLen</td>
<td>Resource: Saturation</td>
</tr>
<tr class="even">
<td>Milliseconds per read I/O operation</td>
<td>ReadLatency</td>
<td>-</td>
<td>Resource: Other</td>
</tr>
<tr class="odd">
<td>Milliseconds per write I/O operation</td>
<td>WriteLatency</td>
<td>-</td>
<td>Resource: Other</td>
</tr>
</tbody>
</table>



#### CPU, memory, storage, and network metrics




<table>
<thead>
<tr class="header">
<th><strong>Description</strong></th>
<th><strong>CloudWatch name</strong></th>
<th><strong>Enhanced monitoring name</strong></th>
<th><a href="https://www.datadoghq.com/blog/monitoring-101-collecting-data/"><strong>Metric type</strong></a></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Percent CPU utilized</td>
<td>CPUUtilization</td>
<td>cpuUtilization.total</td>
<td>Resource: Utilization</td>
</tr>
<tr class="even">
<td>Available RAM in gigabytes</td>
<td>FreeableMemory</td>
<td>memory.free</td>
<td>Resource: Utilization</td>
</tr>
<tr class="odd">
<td>Swap usage</td>
<td>SwapUsage</td>
<td>swap.cached</td>
<td>Resource: Saturation</td>
</tr>
<tr class="even">
<td>Available storage in bytes</td>
<td>FreeStorageSpace</td>
<td>-</td>
<td>Resource: Utilization</td>
</tr>
<tr class="odd">
<td>Network traffic to the MySQL instance</td>
<td>NetworkReceive Throughput (bytes/s)</td>
<td>network.rx (packets)</td>
<td>Resource: Utilization</td>
</tr>
<tr class="even">
<td>Network traffic from the MySQL instance</td>
<td>NetworkTransmit Throughput (bytes/s)</td>
<td>network.tx (packets)</td>
<td>Resource: Utilization</td>
</tr>
</tbody>
</table>



As Baron Schwartz, co-author of *[High Performance MySQL](http://shop.oreilly.com/product/0636920022343.do),* often notes, a database needs four fundamental resources: CPU, memory, disk, and network. Any of these can become a performance bottleneck—for a look at how difference RDS instance types can be constrained by their available resources, check out [this 2013 talk](https://www.youtube.com/watch?v=t6Os_bBNJE0&t=16m12s) by Amazon's Grant McAlister.

Whenever your database instance experiences performance problems, you should check metrics pertaining to the four fundamental resources to look for bottlenecks. As of December 2015, RDS users have access to [<span class="pl-e">enhanced monitoring</span> functionality](https://aws.amazon.com/blogs/aws/new-enhanced-monitoring-for-amazon-rds-mysql-5-6-mariadb-and-aurora/) that exposes detailed system-level metrics for RDS instances. These enhanced metrics can be reported at frequencies as high as once per second. Even out of the box, however, CloudWatch does make available basic metrics, detailed below, on all four fundamental resources. For the most part, these metrics are most useful for [investigating (rather than detecting)](https://www.datadoghq.com/blog/monitoring-101-investigation/) performance issues.

#### Disk I/O metrics


CloudWatch makes available RDS metrics on read and write IOPS. These metrics are useful for monitoring the performance of your database and to ensure that your IOPS do not exceed the limits of your chosen instance type. If you are running an RDS instance in production, you will likely want to choose Provisioned IOPS storage to ensure consistent performance.

If your storage volumes cannot keep pace with the volume of read and write requests, you will start to see I/O operations queuing up. The `DiskQueueDepth` metric measures the length of this queue at any given moment.

Note that there will not be a one-to-one correspondence between queries and disk operations—queries that can be served from memory will bypass disk, for instance, and queries that return a large amount of data can involve more than one I/O operation. Specifically, reading or writing more than 16 KB, the [default page size](http://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html#USER_PIOPS.Realized) for MySQL, will require multiple I/O operations.

In addition to I/O throughput metrics, RDS offers `ReadLatency` and `WriteLatency` metrics. These metrics do not capture full query latency—they only measure how long your I/O operations are taking at the disk level.

For read-heavy applications, one way to overcome I/O limitations is to [create a read replica](http://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReadRepl.html#USER_ReadRepl.Overview) of the database to serve some of the client read requests. For more, see the [section below](#read-replica-metrics) on metrics for read replicas.

#### CPU metrics


High CPU utilization is not necessarily a bad sign. But if your database is performing poorly while it is within its IOPS and network limits, and while it appears to have sufficient memory, the CPUs of your chosen instance type may be the bottleneck.

#### Memory metrics


MySQL performs best when most of its working set of data can be held in memory. For this reason, you should monitor `FreeableMemory` and `SwapUsage` to ensure that your database instance is not memory-constrained.

AWS advises that you monitor `ReadIOPS` when the database is under load to ensure that your database instance has enough RAM to [keep the working set almost entirely in memory](http://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html#CHAP_BestPractices.Performance.RAM):

> The value of ReadIOPS should be small and stable. If scaling up the DB instance class—to a class with more RAM—results in a dramatic drop in ReadIOPS, your working set was not almost completely in memory.



#### Storage metrics


RDS allows you to allocate a fixed amount of storage when you launch your MySQL instance. The CloudWatch metric `FreeStorageSpace` lets you monitor how much of your allocated storage is still available. Note that you can always add more storage by modifying your running database instance in the AWS console, but you may not decrease it.

#### Network metrics


RDS relies on Amazon Elastic Block Store (Amazon EBS) volumes for storage, and the network connection to EBS can limit your throughput. Monitoring `NetworkReceiveThroughput` and `NetworkTransmitThroughput` will help you identify potential network bottlenecks.

Even with Provisioned IOPS, it is entirely possible that network limitations will keep your realized IOPS below your provisioned maximum. For instance, if you provision 10,000 IOPS on a db.r3.2xlarge database instance, but your use case is extremely read-heavy, you will reach the bandwidth limit of 1 gigabit per second (roughly 8,000 IOPS) to EBS in each direction before hitting the provisioned limits of your storage.

#### Metrics to alert on




-   `ReadLatency` or `WriteLatency`: Monitoring the latency of your disk operations is critical to identify potential constraints in your MySQL instance hardware or your database usage patterns. If your latency starts to climb, check your IOPS, disk queue, and network metrics to see if you are pushing the bounds of your instance type. If so, consult the RDS documentation for details about [storage options](http://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html#d0e9920), including volumes with provisioned IOPS rates.
-   `DiskQueueDepth`: It is not unusual to have some requests in the disk queue, but investigation may be in order if this metric starts to climb, especially if latency increases as a result. (Time spent in the disk queue adds to read and write latency.)
-   `FreeStorageSpace`: AWS recommends that RDS users take action to delete unneeded data or add more storage if disk usage consistently reaches levels of 85 percent or more.



{{< img src="latency.png" alt="" popup="true" size="1x" >}}

### Connection metrics




<table>
<thead>
<tr class="header">
<th><strong>Name</strong></th>
<th><strong>Description</strong></th>
<th><a href="https://www.datadoghq.com/blog/monitoring-101-collecting-data/"><strong>Metric type</strong></a></th>
<th><strong>Availability</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>DatabaseConnections</td>
<td>Currently open connections</td>
<td>Resource: Utilization</td>
<td>CloudWatch</td>
</tr>
<tr class="even">
<td>Threads_connected</td>
<td>Currently open connections</td>
<td>Resource: Utilization</td>
<td>MySQL</td>
</tr>
<tr class="odd">
<td>Threads_running</td>
<td>Currently running connections</td>
<td>Resource: Utilization</td>
<td>MySQL</td>
</tr>
<tr class="even">
<td>Aborted_connects</td>
<td>Count of failed connection attempts to the server</td>
<td>Resource: Error</td>
<td>MySQL</td>
</tr>
<tr class="odd">
<td>Connection_errors_ internal</td>
<td>Count of connections refused due to server error</td>
<td>Resource: Error</td>
<td>MySQL</td>
</tr>
<tr class="even">
<td>Connection_errors_ max_connections</td>
<td>Count of connections refused due to <code>max_connections</code> limit</td>
<td>Resource: Error</td>
<td>MySQL</td>
</tr>
</tbody>
</table>



Monitoring how many client connections are in use is critical to understanding your database's activity and capacity. MySQL has a configurable connection limit; on RDS the default value depends on the memory of the database's instance class in bytes, according to the formula:

`max_connections` = `DBInstanceClassMemory` / 12582880

The `max_connections` parameter can be modified by editing the database instance's parameter group using the RDS dashboard in the AWS console. You can also check the current value of `max_connections` by querying the MySQL instance itself (see [part 2](https://www.datadoghq.com/blog/how-to-collect-rds-mysql-metrics) of this series for more on connecting to RDS instances directly):




    mysql> SELECT @@max_connections;      
      +-------------------+      
      | @@max_connections |      
      +-------------------+      
      |               100 |      
      +-------------------+      
      1 row in set (0.00 sec)
      
      



To monitor how many connections are in use, CloudWatch exposes a `DatabaseConnections` metric tracking open RDS connections, and MySQL exposes a similar `Threads_connected` metric counting connection threads. (MySQL allocates one thread per connection.) Either metric will help you monitor your connections in use, but the MySQL metric can be collected at higher resolution than the CloudWatch metric, which is reported at one-minute intervals. MySQL also exposes the `Threads_running` metric to isolate the threads that are actively processing queries.

If your server reaches the `max_connections` limit and starts to refuse connections, `Connection_errors_max_connections` will be incremented, as will the `Aborted_connects` metric tracking all failed connection attempts.

MySQL exposes a variety of other metrics on connection errors, which can help you identify client issues as well as serious issues with the database instance itself. The metric `Connection_errors_internal` is a good one to watch, because it is incremented when the error comes from the server itself. Internal errors can reflect an out-of-memory condition or the server's inability to start a new thread.

#### Metrics to alert on




-   `Threads_connected`: If a client attempts to connect to MySQL when all available connections are in use, MySQL will return a "Too many connections" error and increment `Connection_errors_max_connections`. To prevent this scenario, you should monitor the number of open connections and make sure that it remains safely below the configured `max_connections` limit.
-   `Aborted_connects`: If this counter is increasing, your clients are probably trying and failing to connect to the database. Dig deeper with metrics such as `Connection_errors_max_connections` and `Connection_errors_internal` to diagnose the problem.



{{< img src="threads-connected-2.png" alt="" popup="true" size="1x" >}}

### Read replica metrics




<table>
<thead>
<tr class="header">
<th><strong>Name</strong></th>
<th><strong>Description</strong></th>
<th><a href="https://www.datadoghq.com/blog/monitoring-101-collecting-data/"><strong>Metric type</strong></a></th>
<th><strong>Availability</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>ReplicaLag</td>
<td>Number of seconds by which replica trails master</td>
<td>Other</td>
<td>CloudWatch</td>
</tr>
<tr class="even">
<td>BinLogDiskUsage</td>
<td>Binary log disk usage on master, in bytes</td>
<td>Resource: Utilization</td>
<td>CloudWatch</td>
</tr>
</tbody>
</table>



RDS supports the creation of read replicas from the master MySQL instance. A replica is read-only by default so that its data remains in sync with the master, but that setting can be modified to add an index to the replica—to support a certain type of query, for instance.

These replicas are assigned a separate endpoint, so you can point client applications to read from a replica rather than from the source instance. You can also monitor the replica's connections, throughput, and query performance, just as you would for an ordinary RDS instance.

The lag time for any read replica is captured by the CloudWatch metric `ReplicaLag`. This metric is usually not actionable, although if the lag is consistently very long, you should investigate your settings and resource usage.

Another relevant metric for replication scenarios is `BinLogDiskUsage`, which measures the disk usage on the master database instance of binary logs. MySQL asynchronously replicates its data using a single thread on the master, so periods of high-volume writes cause pileups in the master's binary logs before the updates can be sent to the master.

{{< img src="binlog.png" alt="" popup="true" size="1x" >}}

Conclusion
----------


In this post we have explored the most important metrics you should monitor to keep tabs on performance for MySQL deployed on Amazon RDS. If you are just getting started with MySQL on RDS, monitoring the metrics listed below will give you great insight into your database’s activity and performance. They will also help you to identify when it is necessary to increase your instance storage, IOPS, or memory to maintain good application performance.



-   [Query throughput](#query-throughput)
-   [Query performance and errors](#query-performance)
-   [Disk queue depth](#disk-i/o-metrics)
-   [Storage space](#storage-metrics)
-   [Client connections and errors](#connection-metrics)



[Part 2](https://www.datadoghq.com/blog/how-to-collect-rds-mysql-metrics) of this series provides instructions for collecting all the metrics you need from CloudWatch and from MySQL.

Acknowledgments
---------------


Many thanks to Baron Schwartz of [VividCortex](https://www.vividcortex.com/) and to [Ronald Bradford](http://ronaldbradford.com/) for reviewing and commenting on this article prior to publication.

------------------------------------------------------------------------


*Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/rds-mysql/monitoring_rds_mysql_performance_metrics.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues).*

