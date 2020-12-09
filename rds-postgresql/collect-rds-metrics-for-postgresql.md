---
authors:
- email: emily.chang@datadoghq.com
  image: img-0791.jpg
  name: Emily Chang
blog/category:
- series collection
blog/tag:
- aws
- postgres
- rds
- performance
- database
date: 2018-04-12 00:00:04
description: How to query RDS metrics from CloudWatch and directly from the PostgreSQL database engine.
draft: false
image: rds-metrics-hero.jpg
preview_image: rds-metrics-hero.jpg
slug: collect-rds-metrics-for-postgresql
technology: rds postgres
title: Collecting RDS metrics from PostgreSQL databases
series: rds-postgresql-monitoring
toc_cta_text: Start monitoring RDS PostgreSQL
---

If you read [Part 1][part-1] of this series, you've gotten an overview of the types of metrics that can help you track the health and performance of PostgreSQL on RDS. In order to gain comprehensive insights into PostgreSQL performance, you will need to collect RDS metrics from Amazon CloudWatch, but you will also need to query PostgreSQL metrics directly from each database instance. In this post, we will show you how to collect metrics from both of these sources, so you can keep a handle on RDS PostgreSQL database health and performance. 

## How to collect RDS metrics from CloudWatch
AWS enables RDS PostgreSQL users to access CloudWatch metrics from their database instances in a few different ways:

- [In the AWS Management Console](#accessing-rds-metrics-from-the-aws-management-console)
- [Through the AWS command line interface](#querying-rds-postgresql-metrics-from-the-aws-cli)
- [Using a CloudWatch-compatible monitoring tool](#setting-up-another-RDS-PostgreSQL-monitoring-tool-that-integrates-with-cloudwatch)

### Accessing RDS metrics from the AWS Management Console
To access metrics from your database instances, visit the [AWS CloudWatch console][cloudwatch-console], click on "Metrics" in the sidebar, and select "RDS" under "AWS Namespaces." 

{{< img src="rds-metrics-postgresql-monitoring-tools-aws-console-step1.png" alt="rds metrics postgresql monitoring tools aws console" popup="true" wide="true" >}}

You can filter RDS metrics by dimensions like the database name, instance class, or engine. You can also search for a metric name or database, to view available metrics that adhere to that search query, broken down by database instance identifier.  

Select the name of the metric you want to visualize, and you'll immediately see it graphed at the top of the console. You can adjust the time window to view how the metric has changed over the past hour, day, week, or any other custom period. You can also graph multiple metrics from the same database instance, or graph the same metric across multiple instances.

In the graph below, we're comparing the CloudWatch metric `DiskQueueDepth` across our primary/source instance and its read replica.

{{< img src="rds-metrics-postgresql-monitoring-tools-cw-step2multi.png" alt="rds metrics postgresql monitoring tools aws console graph multiple metrics" popup="true" wide="true" >}}

You can also create an alert by clicking on the bell icon to the right of the metric name. You'll need to provide a threshold, duration, and aggregator (average, minimum, maximum, sum, or sample count), as well as a list of email addresses to contact if the alert triggers.

{{< img src="rds-metrics-postgresql-monitoring-tools-cw-alarm.png" alt="rds metrics postgresql monitoring tools aws console cloudwatch alarm alert" popup="true" wide="true" >}}

### Querying RDS metrics from the AWS CLI
The [AWS command line interface][aws-rds-cli] (AWS CLI) provides a quick and easy way to query any particular CloudWatch metric from your RDS database instances, scoped to one or more dimensions. Before proceeding, you'll need to install and configure the AWS CLI by following the instructions [here][aws-cli-install].

The AWS CLI's [`get-metric-statistics`][aws-rds-cli] command provides data for the specified metric. You'll need to supply the following parameters:

- `namespace`: For RDS, this will be `AWS/RDS`
- `metric-name`: the CloudWatch metric name (e.g., `FreeStorageSpace`)
- `start-time` and `end-time`: timestamp (in [ISO 8601 UTC][iso-wiki] format) of the first and last data point you want to query
- `period`: the period over which all data points during the designated time window should be aggregated (granularity)

Other optional parameters include:

- `dimensions`: The dimensions used to filter this metric, formatted as `Name:x,Value:y`
- `statistics` (or `extended-statistics`): the type of statistic you want to query (`SampleCount`, `Average`, `Sum`, `Minimum`, or `Maximum`). Use `extended-statistics` if you want to query a percentile value between `p0.0` and `p100`
- `unit`: the units you want the metric to be supplied in; if the metric is only available in one unit, specifying this parameter won't do anything

For example, here's how you would query the minimum value of `FreeStorageSpace` at a 60-second granularity over a period of two minutes (yielding the minimum data point in each one-minute bucket), filtered by the name of our database instance identifier (in this case, `my-db-identifier`):

```no-minimize
aws cloudwatch get-metric-statistics 
--namespace AWS/RDS 
--metric-name FreeStorageSpace 
--start-time 2018-02-27T00:00:00 
--end-time 2018-02-27T00:02:00 
--period 60 
--statistics Minimum 
--dimensions Name=DBInstanceIdentifier,Value=my-db-identifier
```

The output is:

```no-minimize
{
    "Label": "FreeStorageSpace",
    "Datapoints": [
        {
            "Timestamp": "2018-02-27T00:01:00Z",
            "Minimum": 20067475456.0,
            "Unit": "Bytes"
        },
        {
            "Timestamp": "2018-02-27T00:00:00Z",
            "Minimum": 20067475456.0,
            "Unit": "Bytes"
        }
    ]
} 
```
Consult the [AWS documentation][aws-rds-cli] for more specific information about structuring your metric queries.

### Setting up an RDS PostgreSQL monitoring tool that integrates with CloudWatch
You can also use another monitoring tool to regularly query metrics from CloudWatch, and compare and correlate them with metrics from other parts of your infrastructure, including application-specific metrics from the applications that query your database. If you use a monitoring tool that integrates with the CloudWatch API as well as the other technologies in your stack, you will be able to gain a comprehensive overview of health and performance across all of your services and applications, as well as their underlying infrastructure. The [next part][part-3] of this series will explore how you can set up Datadog to automatically collect, visualize, and alert on RDS PostgreSQL data alongside metrics from more than {{< translate key="integration_count" >}} technologies.

## How to collect native PostgreSQL metrics from RDS
Many of the PostgreSQL metrics mentioned in [Part 1][part-1] of this series are not available in CloudWatch and will need to be queried directly from the database instance. You can collect these metrics via the PostgreSQL statistics collector's [statistics views][pg-views-docs], including:

- [`pg_stat_database`](#pg-stat-database) (shows one row per database)
- [`pg_stat_user_tables`](#pg-stat-user-tables) (shows one row per table in the current database)
- [`pg_stat_user_indexes`](#pg-stat-user-indexes) (shows one row per index in the current database)
- [`pg_stat_bgwriter`](#pg-stat-bgwriter) (shows only one row, since there is only one background writer process)

The collector aggregates statistics on a per-table, per-database, or per-index basis, depending on the metric. You can dig deeper into each statistics view's actual query language by looking at the [system views source code][sys-views-code]. For example, the [code for `pg_stat_database`][pg-stat-code] indicates that it queries the number of connections, deadlocks, and tuples/rows fetched, returned, updated, inserted, and deleted.

Some of the metrics mentioned in Part 1 are not accessible through these statistics views, and will need to be collected through other types of queries, as explained in [a later section of this post](#querying-other-postgresql-statistics). 

### Connecting to your RDS PostgreSQL instance
In order to access PostgreSQL's statistics views, you'll need to connect to PostgreSQL on your RDS instance. Although RDS does not enable to you to connect directly to the host of your database instance, you can configure the inbound rules of your RDS instance's security group to accept access to the PostgreSQL database within the same security group. For example, you can launch an EC2 instance in the same security group as your RDS instance, and add a rule to the EC2 instance to allow inbound SSH traffic. Then you can SSH into your EC2 instance and [connect to the RDS instance][rds-connect-pg] by using a tool like `psql`. You would need to specify the endpoint of your database instance as the host, and log in with the credentials for the user you created while setting up your RDS instance:

```
psql --host=<INSTANCE_ENDPOINT> --port=5432 --username=<YOUR_USERNAME> --password --dbname=<YOUR_DB>
```
You can locate your `<INSTANCE_ENDPOINT>` by navigating to your database instance in the AWS console. It will look similar to `instancename.xxxxxx.us-east-1.rds.amazonaws.com`.

You will be prompted to enter the password you created when you first launched your RDS PostgreSQL instance. This user is automatically added to the [`rds_superuser` role][rds-superuser-docs], which is granted the highest level of privileges in RDS. This role is closely related to the `superuser` role in conventional PostgreSQL, with some restrictions. Therefore, it may be a good idea to create another user and assign it the privileges it needs:

```
create user <NEW_USERNAME> with password <PASSWORD>;
grant SELECT ON pg_stat_database to <NEW_USERNAME>;
```

If you wish to switch to the new user before proceeding, you can exit the `psql` session and start another one as your newly created user:
 
 ```
psql --host=<INSTANCE_ENDPOINT> --port=5432 --username=<NEW_USERNAME> --password --dbname=<YOUR_DB>
```

Now we are ready to query metrics from the PostgreSQL database engine's statistics collector.

### PostgreSQL's statistics collector
PostgreSQL's built-in statistics collector automatically tracks internal statistics about the database, including its tables and indexes. The statistics collector groups useful metrics into pre-defined statistics views, which are essentially windows into certain aspects of the database's activity. In order to access these statistics views, we'll need to make sure that the statistics collector is enabled on our RDS PostgreSQL instance. By default, it should already be enabled, but we can confirm this in one of two ways:

1. In the AWS RDS console, navigate to your instance's parameter group and search for `track_activities`. If the value is set to 1, this means that the statistics collector is currently enabled, while a value of `0` indicates that it is disabled in this parameter group. 
2. In a `psql` session, query the `track_activities` parameter directly like so:  

    ```
    SHOW track_activities;
    track_activities
    ------------------
    on
    (1 row)
    ```

If `track_activities` is off/disabled for some reason, you can either modify the parameter group directly in the AWS management console, or use the [AWS CLI's `modify-db-parameter-group`][aws-cli-parameter] command to apply the change:

```
aws rds modify-db-parameter-group 
--db-parameter-group-name <MY_PARAMETER_GROUP> 
--parameters ParameterName=track_activities,ParameterValue=on,ApplyMethod=immediate
```

If it is successful, you should see the following output (with the name of your parameter group replaced below):

```
{
    "DBParameterGroupName": "<MY_PARAMETER_GROUP>"
}
```

Since `track_activities` is a dynamic parameter, we were able to apply this change immediately (as indicated by `ApplyMethod=immediate`). If we had been modifying a static parameter, we would have specified `ApplyMethod=pending-reboot` instead.

Now that `track_activities` is on, the statistics collector will start collecting internal statistics about your database. The statistics collector process continuously aggregates data about the server's activity, but it will only report the data as frequently as specified by the `PGSTAT_STAT_INTERVAL` (500 milliseconds, by default). Note that each time a query is issued to one of the statistics views, it will use the most recently available report to deliver information about the database's activity at that point in time, which will be slightly delayed in comparison to real-time activity. Statistics collector views will not yield data about any queries or transactions that are currently in progress.  

### pg_stat_database
Let's take a look at the `pg_stat_database` statistics view in more detail:  

```no-minimize
 datid |    datname    | numbackends | xact_commit | xact_rollback | blks_read | blks_hit | tup_returned | tup_fetched | tup_inserted | tup_updated | tup_deleted | conflicts | temp_files | temp_bytes | deadlocks | blk_read_time | blk_write_time |          stats_reset
-------+---------------+-------------+-------------+---------------+-----------+----------+--------------+-------------+--------------+-------------+-------------+-----------+------------+------------+-----------+---------------+----------------+-------------------------------
 13289 | template0     |           0 |       62824 |             0 |       157 |  2356814 |     30247713 |      346244 |            4 |           2 |           4 |         0 |          0 |          0 |         0 |             0 |              0 | 2018-02-22 21:10:37.030342+00
 16384 | rdsadmin      |           1 |      586152 |             0 |       396 |  3500601 |     51714268 |      359285 |           30 |        3260 |           4 |         0 |          0 |          0 |         0 |             0 |              0 | 2017-12-07 03:11:43.2653+00
     1 | template1     |           0 |       62854 |             0 |       182 |  2358346 |     30256860 |      346808 |            4 |           3 |           4 |         0 |          0 |          0 |         0 |             0 |              0 | 2018-02-22 21:05:43.846763+00
 13294 | postgres      |           0 |       62882 |             0 |       237 |  2359602 |     30257679 |      347514 |            4 |           3 |           4 |         0 |          0 |          0 |         0 |             0 |              0 | 2017-12-07 03:11:42.88194+00
 16390 | testdb        |           1 |       62925 |            14 |       299 |  2364549 |     30538616 |      350470 |         1140 |           9 |          66 |         0 |          0 |          0 |         0 |             0 |              0 | 2018-02-22 21:10:37.060195+00
(5 rows)
```

We can see from the `datname` column that, like PostgreSQL, RDS creates three databases by default: `template0`, `template1`, and `postgres`. However, RDS also creates an additional `rdsadmin` database that is only accessible to the `rdsadmin` role, which is used internally by AWS to manage RDS (e.g., to manage autovacuuming). The rightmost column, `stats_reset`, shows the last time the statistics (which are reported as cumulative counters) were reset in this database. 

`pg_stat_database` collects statistics about each database in the cluster, including the number of connections (`numbackends`), commits, rollbacks, and rows/tuples fetched and returned. Each row displays statistics for a different database, but you can also limit your query to a specific database as shown below:

```no-minimize
SELECT * FROM pg_stat_database WHERE datname = 'testdb';

 datid |    datname    | numbackends | xact_commit | xact_rollback | blks_read | blks_hit | tup_returned | tup_fetched | tup_inserted | tup_updated | tup_deleted | conflicts  | temp_files  | temp_bytes | deadlocks | blk_read_time | blk_write_time |          stats_reset
-------+---------------+-------------+-------------+---------------+-----------+----------+--------------+-------------+--------------+-------------+-------------+-----------+------------+------------+-----------+---------------+----------------+-------------------------------
 16390 |    testdb     |           1 |       62994 |            16 |       299 |  2367210 |     30571960 |      350902 |         1140 |           9 |          66 |         0 |          0 |          0 |         0 |             0 |              0 | 2018-02-22 21:10:37.060195+00
(1 row)
``` 

### pg_stat_user_tables
Whereas `pg_stat_database` collects and displays statistics for each database, `pg_stat_user_tables` displays statistics for each of the user tables in a particular database. 

```no-minimize
SELECT * FROM pg_stat_user_tables;  

 relid | schemaname |  relname  | seq_scan | seq_tup_read | idx_scan | idx_tup_fetch | n_tup_ins | n_tup_upd | n_tup_del | n_tup_hot_upd | n_live_tup | n_dead_tup | n_mod_since_analyze | last_vacuum | last_autovacuum | last_analyze |       last_autoanalyze        | vacuum_count | autovacuum_count | analyze_count | autoanalyze_count
-------+------------+-----------+----------+--------------+----------+---------------+-----------+-----------+-----------+---------------+------------+------------+---------------------+-------------+-----------------+--------------+-------------------------------+--------------+------------------+---------------+-------------------
 16416 | public     | employees |        7 |           19 |          |               |         3 |         0 |         2 |             0 |          1 |          2 |                   5 |             |                 |              |                               |            0 |                0 |             0 |                 0
 16401 | public     | test      |        5 |         5000 |          |               |      1000 |         0 |         0 |             0 |       1000 |          0 |                   0 |             |                 |              | 2018-02-22 21:40:18.590377+00 |            0 |                0 |             0 |                 1
(2 rows)
 ```
 
This database contains two tables: `employees` and `test`. With `pg_stat_user_tables`, we can see a cumulative count of the sequential scans, index scans, and rows fetched/read/updated within each table.

### pg_stat_user_indexes
`pg_stat_user_indexes` shows you how often each index is actually being used to serve queries. You can analyze this statistics view to determine if any indexes are underutilized, and consider deleting them in order to make better use of resources. 

You can query this view like any other table, like so:

```no-minimize
SELECT * FROM pg_stat_user_indexes;

 relid | indexrelid | schemaname |  relname   |      indexrelname       | idx_scan | idx_tup_read | idx_tup_fetch
-------+------------+------------+------------+-------------------------+----------+--------------+---------------
 16454 |      16491 | public     | categories | categories_pkey         |        0 |            0 |             0
 16463 |      16493 | public     | customers  | customers_pkey          |        1 |            1 |             1
 16470 |      16495 | public     | inventory  | inventory_pkey          |        0 |            0 |             0
 16478 |      16497 | public     | orders     | orders_pkey             |        0 |            0 |             0
 16484 |      16499 | public     | products   | products_pkey           |        0 |            0 |             0
 16458 |      16501 | public     | cust_hist  | ix_cust_hist_customerid |        0 |            0 |             0
 16463 |      16502 | public     | customers  | ix_cust_username        |        0 |            0 |             0
 16478 |      16503 | public     | orders     | ix_order_custid         |        0 |            0 |             0
 16473 |      16504 | public     | orderlines | ix_orderlines_orderid   |        0 |            0 |             0
 16484 |      16505 | public     | products   | ix_prod_category        |        0 |            0 |             0
 16484 |      16506 | public     | products   | ix_prod_special         |        0 |            0 |             0
(11 rows)
```

The `indexrelname` column shows the name of the index, while `idx_scan` tells you how many times that index has been scanned.

### pg_stat_bgwriter
As mentioned in [Part 1][part-1-checkpoints], monitoring the checkpoint process can help you determine how much load is being placed on your databases. The `pg_stat_bgwriter` view will return one row of data that shows the number of total checkpoints completed across all databases in your cluster, broken down by the type of checkpoint (timed or requested), and how shared buffers were flushed to disk: during a checkpoint process (buffers_checkpoint), by the background writer (buffers_clean), or by another backend process (buffers_backend):

```no-minimize
SELECT * FROM pg_stat_bgwriter;

 checkpoints_timed | checkpoints_req | checkpoint_write_time | checkpoint_sync_time | buffers_checkpoint | buffers_clean | maxwritten_clean | buffers_backend | buffers_backend_fsync | buffers_alloc |          stats_reset
-------------------+-----------------+-----------------------+----------------------+--------------------+---------------+------------------+-----------------+-----------------------+---------------+-------------------------------
              3139 |              17 |                 71436 |                 9828 |               3834 |             0 |                0 |              40 |                     0 |          1327 | 2017-12-07 03:11:41.894957+00
(1 row)
```

### Querying other PostgreSQL statistics
Although most of the metrics covered in [Part 1][part-1] are available through PostgreSQL's predefined statistics views, these four categories of metrics need to be accessed from [system administration functions][pg-sys-admin-docs] and other native sources:

- [replication delay](#tracking-replication-delay)
- [connections](#connection-metrics)
- [locks](#locks)
- [disk space used by tables and indexes](#disk-usage)

#### Tracking replication delay
You can connect to any replica database instance through `psql` to query replication delay in two ways: in terms of seconds and bytes. CloudWatch provides a `ReplicaLag` metric that tracks the replication lag in seconds, and is equivalent to the following query:

```
SELECT extract(epoch from now() - pg_last_xact_replay_timestamp()); 
```

However, note that this query will tell you how much time has passed since the last WAL update was applied on the replica—so if you haven't updated the database recently, this metric may be higher than expected. [According to the RDS documentation][rds-replica-docs], "A PostgreSQL Read Replica reports a replication lag of up to five minutes if there are no user transactions occurring on the source DB instance."

To supplement the `ReplicaLag` metric, you can also query the replication lag in bytes on each replica, by using `pg_xlog_location_diff()` to calculate the difference between two recovery information functions: `pg_last_xlog_receive_location()` and `pg_last_xlog_replay_location()`. The first function tracks the location in the WAL file that was most recently synced to disk on the replica, while the second function tracks the location in the WAL file that was most recently applied/replayed on the replica. Note that these functions have been [renamed in PostgreSQL 10][recovery-pg-10] to `pg_wal_lsn_diff()`, `pg_last_wal_receive_lsn()` and  `pg_last_wal_replay_lsn()`. 

Let's initialize a `psql` session on a replica database instance and query the replication delay in bytes, using the [recovery information functions][pg-recovery-query] stated above:

```
# on PostgreSQL versions <10.x:
SELECT abs(pg_xlog_location_diff(pg_last_xlog_receive_location(), pg_last_xlog_replay_location())) AS replication_delay_bytes; 

# on PostgreSQL versions 10.x:
SELECT abs(pg_wal_lsn_diff(pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn())) AS replication_delay_bytes; 
```

This tells us the replication delay in bytes, in terms of the amount of WAL data that still needs to be applied on this replica instance in order to be up to date with the primary/source instance. You can automatically collect the output of this query and set up an alert when it increases significantly. This metric is not available in CloudWatch. 

#### Connection metrics
Although you can access the [number of active connections][part-1-connections] through `pg_stat_database`, you'll need to query `pg_settings` to find the server's current setting for the maximum number of connections:

```no-minimize
SELECT setting::float FROM pg_settings WHERE name = 'max_connections';
 setting
---------
      87
(1 row)
```

If you use a connection pool like PgBouncer to proxy connections between your applications and PostgreSQL database instances, you can also monitor metrics from your connection pool in order to ensure that connections are functioning as expected.

#### Locks
Tracking the most recent status of locks granted across each of your databases can help you keep database operations running smoothly. The [pg_locks][pglocks] view provides a breakdown of the type of lock (in the `mode` column), as well as the relevant database, relation, and process ID. 

```no-minimize
SELECT locktype, database, relation::regclass, mode, pid FROM pg_locks;


   locktype    | database | relation |       mode       | pid
---------------+----------+----------+------------------+-----
 relation      | 12066    | pg_locks | AccessShareLock  | 965
 virtualxid    |          |          | ExclusiveLock    | 965
 relation      | 16611    | 16628    | AccessShareLock  | 820
 relation      | 16611    | 16628    | RowExclusiveLock | 820
 relation      | 16611    | 16623    | AccessShareLock  | 820
 relation      | 16611    | 16623    | RowExclusiveLock | 820
 virtualxid    |          |          | ExclusiveLock    | 820
 relation      | 16611    | 16628    | AccessShareLock  | 835
 relation      | 16611    | 16623    | AccessShareLock  | 835
 virtualxid    |          |          | ExclusiveLock    | 835
 transactionid |          |          | ExclusiveLock    | 820
(11 rows)
```
 
You'll see an [object identifier (OID)][postgres-oid] listed in the database and relation columns. To translate these OIDs into the actual names of each database and relation, you can query the database OID from [pg_database][pg-database], and the relation OID from [pg_class][pg-class].

#### Disk usage
RDS provides the `FreeStorageSpace` CloudWatch metric to help you track the amount of free storage on each database instance. However, you should also investigate *how* that storage is actually being used by the tables and indexes in your database, by using PostgreSQL's [database object size functions][database-management-docs]. In the example below, we are querying the size of `mydb` using the `pg_database_size` function. We also wrap the query in `pg_size_pretty()` to return the result in a human-readable format:

```no-minimize
SELECT pg_size_pretty(pg_database_size('mydb')) AS mydbsize;

 mydbsize
------------
 846 MB
(1 row)
```

You can check the size of your tables by querying the object ID (OID) of each table in your database, and using that OID to query the size of each table from `pg_table_size`. The following query will show you how much disk space the top five tables are using (excluding indexes):

```no-minimize
SELECT 
       relname AS "table_name", 
       pg_size_pretty(pg_table_size(C.oid)) AS "table_size" 
FROM 
       pg_class C 
LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace) 
WHERE nspname NOT IN ('pg_catalog', 'information_schema') AND nspname !~ '^pg_toast' AND relkind IN ('r') 
ORDER BY pg_table_size(C.oid) 
DESC LIMIT 5;

    table_name    | table_size
------------------+------------
 pgbench_accounts | 705 MB
 customers        | 3944 kB
 orderlines       | 3112 kB
 cust_hist        | 2648 kB
 products         | 840 kB
(5 rows)

```

You can customize these queries to gain more granular views into disk usage across tables and indexes in your databases. For example, in the query above, you could replace `pg_table_size` with `pg_total_relation_size`, if you'd like to include indexes in your `table_size` metric. You can also fine-tune your queries by using [regular expressions][pg-docs-regex]. For example, in the query above, we used the `!~` regex operator to exclude [TOAST tables][pg-toast-docs].

## Comprehensive insights into RDS metrics + your PostgreSQL database
In this post, we've shown you how to gain more visibility into RDS PostgreSQL performance by combining RDS metrics from CloudWatch with statistics from the PostgreSQL database engine. Because `pg_stat_*` statistics views provide data in the form of cumulative counters that reset periodically, ad hoc queries are often not as helpful as regularly collecting these metrics and tracking how they change over time. 

In the [next part][part-3] of this series, we'll show you how to use Datadog to automatically query PostgreSQL statistics from your RDS instances, visualize them in a customizable, out-of-the-box dashboard, and analyze RDS PostgreSQL performance alongside more than {{< translate key="integration_count" >}} other technologies. We'll also show you how to deploy Datadog's distributed tracing and APM so you can optimize and troubleshoot applications that query data from your RDS PostgreSQL database instances.


[part-1]: /blog/aws-rds-postgresql-monitoring
[part-1-connections]: /blog/aws-rds-postgresql-monitoring/#connections
[part-1-checkpoints]: /blog/aws-rds-postgresql-monitoring/#checkpoints-and-postgresql-reliability
[pg-stat-code]: https://github.com/postgres/postgres/blob/master/src/backend/catalog/system_views.sql#L800
[cloudwatch-console]: https://console.aws.amazon.com/cloudwatch/home
[aws-cli-install]: https://docs.aws.amazon.com/cli/latest/userguide/installing.html
[aws-rds-cli]: https://docs.aws.amazon.com/cli/latest/reference/cloudwatch/get-metric-statistics.html
[pg-views-docs]: https://www.postgresql.org/docs/current/static/tutorial-views.html
[aws-cli-parameter]: https://docs.aws.amazon.com/cli/latest/reference/rds/modify-db-parameter-group.html
[rds-superuser-docs]: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html#PostgreSQL.Concepts.rds_superuser
[rds-connect-pg]: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ConnectToPostgreSQLInstance.html
[access-rds-postgresql]: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_VPC.Scenarios.html
[pg-recovery-query]: https://www.postgresql.org/docs/9.6/static/functions-admin.html#FUNCTIONS-RECOVERY-INFO-TABLE
[postgres-oid]: https://www.postgresql.org/docs/current/static/datatype-oid.html
[pg-class]: https://www.postgresql.org/docs/current/static/catalog-pg-class.html
[pglocks]: https://www.postgresql.org/docs/current/static/view-pg-locks.html
[database-management-docs]: https://www.postgresql.org/docs/current/static/functions-admin.html#FUNCTIONS-ADMIN-DBSIZE
[pg-docs-regex]: https://www.postgresql.org/docs/current/static/functions-matching.html
[pg-sys-admin-docs]: https://www.postgresql.org/docs/current/static/functions-admin.html
[rds-replica-docs]: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReadRepl.html
[recovery-pg-10]: https://www.postgresql.org/docs/current/static/functions-admin.html#FUNCTIONS-RECOVERY-INFO-TABLE
[pg-database]: https://www.postgresql.org/docs/current/static/catalog-pg-database.html
[sys-views-code]: https://github.com/postgres/postgres/blob/master/src/backend/catalog/system_views.sql#L507
[iso-wiki]: https://en.wikipedia.org/wiki/ISO_8601
[pg-toast-docs]: https://www.postgresql.org/docs/current/static/storage-toast.html
[part-3]: /blog/postgresql-rds-monitoring-datadog
