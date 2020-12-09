---
authors:
- email: emily.chang@datadoghq.com
  image: img-0791.jpg
  name: Emily Chang
blog/category:
- series metrics
blog/tag:
- postgres
- performance
- database
date: 2017-12-15 00:00:05
description: Learn how to identify and track key PostgreSQL performance metrics in this monitoring guide.
draft: false
image: postgresql-monitoring-hero1.jpg
preview_image: postgresql-monitoring-hero1.jpg
slug: postgresql-monitoring
technology: postgres
title: Key metrics for PostgreSQL monitoring
series: postgresql-monitoring
toc_cta_text: Start monitoring PostgreSQL
---

PostgreSQL, or simply "Postgres," is an open source, object-relational database system that was developed out of the POSTGRES project at the University of California, Berkeley. PostgreSQL ensures data integrity and reliability with built-in features like Multi-Version Concurrency Control (MVCC) and write-ahead logging. Today, many organizations and companies, including Cisco, Fujitsu, and Datadog, utilize PostgreSQL as a reliable, robust data storage solution. 

## PostgreSQL terminology + overview
Before diving into the key metrics for PostgreSQL monitoring, let's briefly walk through some terminology. Most notably, a PostgreSQL database **cluster** is not a collection of servers, but a collection of **databases** managed by a single server. [PostgreSQL 10][postgres-10-release] was the first release to include built-in support for logical replication. Prior to that release, PostgreSQL has left it largely up to users to implement their own approaches to replication and load balancing across databases, typically involving some form of [logical and/or physical data partitioning][postgres-availability-docs].   

Each database **table** stores rows of data as an array of 8-KB **pages**, or **blocks**. If your data contains field values that exceed this limit, PostgreSQL TOAST (The Oversized-Attribute Storage Technique) is designed to help accommodate this need (consult the [documentation][toast-docs] to see which data types are eligible for TOAST storage).

You may see the terms "block" and "page" used interchangeably—the only difference is that a [page includes a header](https://www.postgresql.org/docs/current/static/storage-page-layout.html#PAGEHEADERDATA-TABLE) that stores metadata about the block, such as information about the most recent write-ahead log entry that affects tuples in its block. We'll also cover write-ahead logs in more detail in a [later section of this post](#replication-and-reliability). The diagram below takes a closer look at how PostgreSQL stores data across rows within each page/block of a table.

{{< img src="postgresql-monitoring-storage-diagram3.png" alt="monitoring postgresql - page and row storage diagram" popup="true" >}}

PostgreSQL's work extends across four main areas:  

- **[planning and optimizing queries](#read-query-throughput-and-performance)**  
- using [**multi-version concurrency control**](#write-query-throughput-and-performance) to manage data updates  
- querying data from the [**shared buffer cache**](#shared-buffer-usage) and on disk  
- continuously [**replicating**](#replication-and-reliability) data from the primary to one or more standbys  

Although these ideas will be explained in further detail throughout this post, let's briefly explore how they all work together to make PostgreSQL an efficient, reliable database. 

PostgreSQL uses a query planner/optimizer to determine the most efficient way to execute each query. In order to do so, it accounts for a number of factors, including whether or not the data in question has been indexed, as well as [internal statistics][internal-statistics-docs] about the database, like the number of rows in each table.

When a query involves updating or deleting data, PostgreSQL uses [multi-version concurrency control](#write-query-throughput-and-performance) (MVCC) to ensure that data remains accessible and consistent, even in high-concurrency environments. Each transaction operates on its own snapshot of the database at that point in time, so that read queries won't block write queries, and vice versa. 

In order to speed up queries, PostgreSQL uses a certain portion of the database server's memory as a [shared buffer cache][shared-buffers] (128MB by default), to store recently accessed blocks in memory. When data is updated or deleted, PostgreSQL will note the change in the write-ahead log (WAL), update the page in memory, and mark it as "dirty." PostgreSQL periodically runs checkpoint processes to flush these dirty pages from memory to disk, to ensure that data is up to date, not only in memory but also on disk. The animation below shows how PostgreSQL adds and updates data in memory before it gets flushed to disk in a checkpoint process.

{{< img src="postgresql-monitoring-animation-compressed.mp4" alt="PostgreSQL updates data in memory through MVCC, and then flushes the changes to disk during a checkpoint process." wide="true" video="true" >}}

PostgreSQL [maintains data reliability](#replication-and-reliability) by logging each transaction in the WAL on the primary, and writing it to disk periodically. In order to ensure high availability, the primary needs to communicate WAL updates to one or more standby servers. 

In this post, we'll cover all of these concepts in more detail, as well as the important metrics for PostgreSQL monitoring that will help you ensure that your database is able to do its work successfully. 

## Key metrics for PostgreSQL monitoring
PostgreSQL automatically collects a substantial number of statistics about its activity, but here we will focus on just a few categories of metrics that can help you gain insights into the health and performance of your database servers:

* [Read query throughput and performance](#read-query-throughput-and-performance)
* [Write query throughput and performance](#write-query-throughput-and-performance)
* [Replication and reliability](#replication-and-reliability)
* [Resource utilization](#resource-utilization)

All of the metrics mentioned in this article are accessible through PostgreSQL's [statistics collector][stats-collector-docs] and other native sources. In the [next part][part-2] of this series, we'll explain how to query and collect these metrics for visualization and alerting.

This article references metric terminology defined in our [Monitoring 101 series][monitoring-101-blog], which provides a framework for metric collection and alerting. 

{{< img src="postgresql-monitoring-dashboard-pt1v3.png" alt="postgresql dashboard" popup="true" wide="true" border="true" >}}

### Read query throughput and performance
PostgreSQL collects internal statistics about its activity in order to provide a window into how effectively the database is performing its work. One major category of its work is read query throughput—monitoring this metric helps you ensure that your applications are able to access data from your database. 

| **Metric description**  | **Name** | [**Metric type**][monitoring-101-blog] | [**Availability**][part-2] |
| :------------ | :----------- | :------------------- | :------------------- |
| Number of index scans on a table    | idx_scan     | Other  |  pg_stat_user_tables | 
| Number of sequential scans on a table    |  seq_scan    | Other  |  pg_stat_user_tables | 
| Rows fetched vs. returned by queries to the database    |  tup_fetched vs. tup_returned    | Work: Throughput  |  pg_stat_database | 
| Amount of data written temporarily to disk to execute queries (available in v. 9.2+)  | temp_bytes      | Resource: Saturation  |  pg_stat_database | 

**Sequential scans vs. index scans:** If you see your database regularly performing more sequential scans over time, its performance could be improved by creating an [**index**](https://www.postgresql.org/docs/current/static/sql-createindex.html) on data that is frequently accessed. Running EXPLAIN on your queries can tell you more details about how the planner decides to access the data. Sequential scans typically take longer than index scans because they have to scan through each row of a table sequentially, rather than relying on an index to point to the location of specific rows. However, note that the planner will prefer a sequential scan over an index scan if it determines that the query would need to return a large portion of the table. 

To track trends in performance, you can use a monitoring tool to continuously collect the number of sequential scans as a metric, and compare the number of sequential scans performed this week and last week, like in the graph below.  

{{< img src="postgresql-monitoring-sequential-scans.png" alt="postgresql sequential scans with timeshift" wide="true" border="true" >}}

If you believe that the query planner is mistakenly preferring sequential scans over index scans, you can try tweaking the `random_page_cost` setting (the estimated cost of randomly accessing a page from disk). [According to the docs][random-page-cost], lowering this value in proportion to `seq_page_cost` (explained in more detail in the [next section](#seqpagecost)) will encourage the planner to prefer index scans over sequential scans. The default setting assumes that [~90 percent of your reads will access data that has already been cached][random-page-cost] in memory. However, if you're running a dedicated database instance, and your entire database can easily fit into memory, you may want to try lowering the random page cost to see if it yields good results. 

**Rows fetched vs. rows returned by queries to the database:** Somewhat confusingly, PostgreSQL tracks `tup_returned` as the number of rows *read/scanned*, rather than indicating anything about whether those rows were actually returned to the client. Rather, `tup_fetched`, or "rows fetched", is the metric that counts how many rows contained data that was actually needed to execute the query. Ideally, the number of rows fetched should be close to the number of rows returned (read/scanned) on the database. This indicates that the database is completing read queries efficiently—it is not scanning through many more rows than it needs to in order to satisfy read queries. 

In the screenshot below, PostgreSQL is scanning (purple) through more rows in this particular database than it is fetching (green), which indicates that the data may not be properly indexed.

{{< img src="postgresql-monitoring-rows-fetched-vs-returned.png" alt="postgresql rows fetched vs rows returned" popup="true" wide="true" border="true" >}}

PostgreSQL can only perform an index scan if the query does not need to access any columns that haven't been indexed. Typically, creating indexes on frequently accessed columns can help improve this ratio. However, maintaining each index doesn’t come free—it requires the database to perform additional work whenever it needs to add, update, or remove data included in any particular index. 

**Amount of data written temporarily to disk to execute queries:** PostgreSQL reserves a certain amount of memory—specified by [`work_mem`](https://www.postgresql.org/docs/9.6/static/runtime-config-resource.html#RUNTIME-CONFIG-RESOURCE-MEMORY) (4 MB by default)—to perform sort operations and hash tables needed to execute queries. EXPLAIN ANALYZE (which is explained in further detail in the [next section](#explain-analyze)) can help you gauge how much memory a query will require. 

When a complex query requires access to more memory than `work_mem` allows, it has to write some data temporarily to disk in order to do its work, which has a negative impact on performance. If you see data frequently being written to temporary files on disk, this indicates that you are running a large number of resource-intensive queries. To improve performance, you may need to increase the size of `work_mem`—however, it's important not to set this too high, because it can encourage the query planner to choose more inefficient queries. 

Another reason you shouldn't set `work_mem` too high is that it's a per-operation setting—so if you're running a complex query that includes several sort operations, each operation will be allowed to use up to `work_mem` amount of memory before writing temporarily to disk. With an overly generous `work_mem` setting, your database will not have enough memory left to serve a high number of concurrent connections, which can negatively impact performance or crash your database.

#### PostgreSQL query planner
To understand more about these throughput metrics, it can be helpful to get more background about how the [query planner/optimizer][planner-docs] works. The query planner/optimizer uses [internal statistics][internal-statistics-docs] (such as the number of fields in a table or index) to estimate the cost of executing different query plans, and then determines which one is optimal. One of the plans it always evaluates is a sequential scan.

Running an EXPLAIN command can help provide more insights into those internal statistics, which the planner actually uses to estimate the cost of a query:

```
EXPLAIN SELECT * FROM blog_article ORDER BY word_count;
                              QUERY PLAN
-----------------------------------------------------------------------
 Sort  (cost=337.48..348.14 rows=4261 width=31)
   Sort Key: word_count
   ->  Seq Scan on blog_article  (cost=0.00..80.61 rows=4261 width=31)
(3 rows)

```

The planner calculates the cost by using a number of factors—in this case, the number of rows that need to be scanned (4,261) and the number of blocks that this table is stored on. You can find out how many blocks are in this particular table/relation (or `relname`), by querying `pg_class`:

```
SELECT relpages, reltuples FROM pg_class WHERE relname='blog_article';

 relpages | reltuples
----------+-----------
       38 |      4261
```

This tells us that our `blog_article` table contains data that is stored across 38 pages, which contain 4,261 tuples/rows. To calculate the cost of the sequential scan in the query plan above, the planner used this formula:

```
cost of sequential scan = (pages read * seq_page_cost) + (rows scanned * cpu_tuple_cost)
```

<div id="seqpagecost"></div>

`seq_page_cost` refers to the planner's estimate of the cost of fetching a page from disk during a sequential scan, while `cpu_tuple_cost` is the planner's estimate of the CPU cost of querying a row/tuple. Actual sequential page cost will vary according to your disk hardware, so if you're using high-performance SSDs, your cost of fetching a page from disk will be lower than if you were storing data on hard disk drives. You can adjust the values of `seq_page_cost` and `cpu_tuple_cost` in your PostgreSQL settings to match the performance of your hardware. For now, we'll use the default values to calculate the cost shown in our query plan above:

```
cost = (38 pages read * 1.0) + (4261 rows scanned * 0.01) = 80.61
```

Note that EXPLAIN shows you the estimated *cost*, rather than the estimated *time* it takes to run a query. However, the two values should be strongly correlated—the higher the cost, the longer the query will take. 

If you run [EXPLAIN ANALYZE][explain-docs] on a query, it will actually execute the query and show you the planner's estimated costs of running the query, compared to the actual timing of that query:

<div id="explain-analyze"></div>
```
EXPLAIN ANALYZE SELECT * FROM blog_article ORDER BY word_count;
                                                     QUERY PLAN
--------------------------------------------------------------------------------------------------------------------
 Sort  (cost=337.48..348.14 rows=4261 width=31) (actual time=9.039..11.101 rows=4261 loops=1)
   Sort Key: word_count
   Sort Method: quicksort  Memory: 525kB
   ->  Seq Scan on blog_article  (cost=0.00..80.61 rows=4261 width=31) (actual time=0.049..1.559 rows=4261 loops=1)
 Total runtime: 11.981 ms
(5 rows)
```

EXPLAIN ANALYZE enables you to assess how closely the planner's estimates stack up against actual execution (in this example, the planner correctly estimated that it would need to scan through 4,261 rows). The output also tells us that it used 525 KB of memory to complete the sort operation (meaning it did not need to write any data temporarily to disk). Another benefit of running ANALYZE is that it helps provide the query planner/optimizer with up-to-date internal statistics that will make its execution plans more accurate as the database gets updated in real time. 

In addition to troubleshooting slow queries with EXPLAIN ANALYZE, you may also find it helpful to log the EXPLAIN output for slow queries that surpass a specific latency threshold, by specifying [`auto_explain.log_min_duration`](https://www.postgresql.org/docs/9.3/static/auto-explain.html) in your configuration file. In the example below, we've set it to automatically log the EXPLAIN execution plan for every SQL statement that exceeds 250 ms:

```
# postgresql.conf

auto_explain.log_min_duration = 250       

```
For help with deciphering EXPLAIN and EXPLAIN ANALYZE queries, you can consult a tool like [explain.depesz.com][explain-depesz]. 

### Write query throughput and performance
In addition to ensuring that your applications can *read* data from your database, you should also monitor how effectively you can *write/update* data to PostgreSQL. Any issues or unusual changes in write throughput usually point to problems in other key aspects of the database, including replication and reliability. Therefore, monitoring write throughput is crucial to ensure that you maintain the overall health and availability of your database.

#### Writing data to PostgreSQL: MVCC 
Before we dive into the metrics, let's explore how PostgreSQL uses [multi-version concurrency control (MVCC)][mvcc-docs] to ensure that concurrent transactions do not block each other. Each transaction operates based on a snapshot of what the database looked like when it started. In order to do this, every INSERT, UPDATE, or DELETE transaction is assigned its own transaction ID (XID), which is used to determine which rows will and will not be visible to that transaction. 

Each row stores metadata in a header, including [`t_xmin` and `t_xmax` values](https://github.com/postgres/postgres/blob/master/src/include/access/htup_details.h#L118) that specify which transactions/XIDs will be able to view that row's data. `t_xmin` is set to the XID of the transaction that last inserted or updated it. If the row is live (hasn't been deleted), its `t_xmax` value will be 0, meaning that it is visible to all transactions. If it was deleted or updated, its `t_xmax` value is set to the XID of the transaction that deleted or updated it, indicating that it will not be visible to future UPDATE or DELETE transactions (which will get assigned an XID > `t_xmax`). Any row with a `t_xmax` value is also known as a "dead row" because it has either been deleted or updated with new data. 

To understand a little more about how MVCC works behind the scenes, let's look at a simplified example of the various stages of a DELETE operation. First, we'll create a table & add some data to it:

```
CREATE TABLE employees ( id SERIAL, name varchar, department varchar);
INSERT INTO employees (name, department) VALUES ('Sue', 'Sales'), ('Dan', 'Operations'), ('Snoop', 'Sales');
```
       
Here's a quick look at the employees table:

```
SELECT * FROM employees;

 id | name  | department
----+-------+------------
  1 | Sue   | Sales
  2 | Dan   | Operations
  3 | Snoop | Sales
(3 rows)

```

Now we can use the [`pageinspect` module](https://www.postgresql.org/docs/current/static/pageinspect.html) to take a closer look at the page:

```
SELECT * FROM heap_page_items(get_raw_page('employees', 0));

 lp | lp_off  | lp_flags  | lp_len | t_xmin | t_xmax | t_field3 | t_ctid  | t_infomask2 | t_infomask | t_hoff  | t_bits | t_oid
----+--------+----------+--------+--------+--------+----------+--------+-------------+------------+--------+--------+-------
  1 |   8152 |        1 |     38 |    730 |      0 |        0 | (0,1)  |           3 |       2306 |     24 |        |
  2 |   8104 |        1 |     43 |    730 |      0 |        0 | (0,2)  |           3 |       2306 |     24 |        |
  3 |   8064 |        1 |     40 |    730 |      0 |        0 | (0,3)  |           3 |       2306 |     24 |        |
(3 rows)
  ```
  
Note that the `t_xmin` column shows us the transaction ID (XID) that was assigned to the INSERT operation we ran in the previous step. 

Let's delete everyone in Sales and then query the table again:

```
DELETE FROM employees WHERE department = 'Sales';
SELECT * FROM employees;

 id | name | department
----+------+------------
  2 | Dan  | Operations
(1 row)
```

But we will still be able to see the deleted rows when we inspect the page:

```
SELECT * FROM heap_page_items(get_raw_page('employees',0));

 lp | lp_off  | lp_flags | lp_len | t_xmin | t_xmax | t_field3 | t_ctid | t_infomask2 | t_infomask | t_hoff  | t_bits | t_oid
----+--------+---------+--------+--------+--------+---------+--------+-------------+------------+--------+--------+-------
  1 |   8152 |      1  |     38 |    730 |    731 |      0 | (0,1)   |      8195   |       1282 |     24 |        |
  2 |   8104 |      1  |     43 |    730 |      0 |      0 | (0,2)   |         3   |       2306 |     24 |        |
  3 |   8064 |      1  |     40 |    730 |    731 |      0 | (0,3)   |      8195   |       1282 |     24 |        |
(3 rows)
```
  
Note that the deleted/dead rows now have a `t_xmax` value equal to the transaction ID (XID) of the DELETE operation (731). Because future transactions will be assigned XIDs that are larger than this `t_xmax` value, they will not be able to view the dead row. However, the database will still have to scan over dead rows during each sequential scan until the next VACUUM process removes the dead rows (see more details about VACUUMs in the [section below](#vacuum-processes)).

#### Write query throughput & performance metrics
| **Metric description**  | **Name** | [**Metric type**][monitoring-101-blog] | [**Availability**][part-2] |
| :------------ | :----------- | :------------------- | :------------------- |
| Rows inserted, updated, deleted by queries (per database)     | tup_inserted, tup_updated, tup_deleted        | Work: Throughput  |  pg_stat_database | 
| Rows inserted, updated, deleted by queries (per table)     | n_tup_ins, n_tup_upd, n_tup_del        | Work: Throughput  |  pg_stat_user_tables | 
| Heap-only tuple (HOT) updates   | n_tup_hot_upd        | Work: Throughput  |  pg_stat_user_tables | 
| Total number of transactions executed (commits + rollbacks)     | xact_commit + xact_rollback           | Work: Throughput |  pg_stat_database | 

**Metrics to watch:**  

**Rows inserted, updated, and deleted:** Monitoring the number of rows inserted, updated, and deleted can help give you an idea of what types of write queries your database is serving. If you see a high rate of updated and deleted rows, you should also keep a close eye on the number of dead rows, since an increase in dead rows indicates a problem with VACUUM processes, which can slow down your queries. 

A sudden drop in throughput is concerning and [could be due to issues like locks](#locks) on tables and/or rows that need to be accessed in order to make updates. Monitoring write activity along with other database metrics like locks can help you pinpoint the potential source of the throughput issue.

{{< img src="postgresql-monitoring-rows-deleted.png" alt="postgresql rows deleted" wide="true" >}}

**Tuples updated vs. heap-only tuples (HOT) updated:** PostgreSQL will try to optimize updates when it is feasible to do so, through what's known as a [Heap-Only Tuple (HOT)](https://github.com/postgres/postgres/blob/master/src/backend/access/heap/README.HOT) update. A HOT update is possible when the transaction does not change any columns that are currently indexed (for example, if you created an index on the column `age`, but the update only affects the `name` column, which is not indexed). 

In comparison with normal updates, a HOT update introduces less I/O load on the database, since it can update the row without having to update its associated index. In the next index scan, PostgreSQL will see a pointer in the old row that directs it to look at the new data instead. In general, you want to see more HOT updates over regular updates because they produce less load on the database. If you see a significantly higher number of updates than HOT updates, it may be due to frequent data updates in indexed columns. This issue will only continue to increase as your indexes grow in size and become more difficult to maintain. 

#### Concurrent operations performance metrics
PostgreSQL's statistics collector tracks several key metrics that pertain to concurrent operations. Tracking these metrics is an important part of PostgreSQL monitoring, helping you ensure that the database can scale sufficiently to be able to fulfill a high rate of queries. The VACUUM process is one of the most important maintenance tasks related to ensuring successful concurrent operations.

<div id="vacuum-processes"></div>
##### Exploring the VACUUM process
MVCC enables operations to occur concurrently by utilizing snapshots of the database (hence the "multi-version" aspect of MVCC), but the tradeoff is that it creates dead rows that eventually need to be cleaned up by running a VACUUM process. 

The VACUUM process removes dead rows from tables and indexes and adds a marker to indicate that the space is available. Usually, the operating system will technically consider that disk space to be "in use," but PostgreSQL will still be able to use it to store updated and/or newly inserted data. In order to actually recover disk space to the OS, you need to run a [VACUUM FULL](https://www.postgresql.org/docs/9.6/static/routine-vacuuming.html) process, which is more resource-intensive, and requires an exclusive lock on each table as it works. If you do determine that you need to run a VACUUM FULL, you should do so during off-peak hours.

Routinely running VACUUM processes is crucial to maintaining efficient queries—not just because sequential scans have to scan through those dead rows, but also because VACUUM processes provide the query planner with updated internal statistics about tables, so that it can plan more efficient queries. To automate this process, you can enable the [autovacuum daemon][autovacuum-docs] to periodically run a VACUUM process whenever the number of dead rows in a table surpasses a specific threshold. This threshold is calculated based on a combination of factors:

- the [`autovacuum_vacuum_threshold`](https://www.postgresql.org/docs/current/static/runtime-config-autovacuum.html#GUC-AUTOVACUUM-VACUUM-THRESHOLD) (50, by default) 
- the [`autovacuum_vacuum_scale_factor`](https://www.postgresql.org/docs/current/static/runtime-config-autovacuum.html#GUC-AUTOVACUUM-VACUUM-SCALE-FACTOR) (0.2 or 20 percent, by default) 
- the estimated number of rows in the table (based on the value of [`pg_class.reltuples`][pgclass-docs])

The autovacuum daemon uses the following formula to calculate when it will trigger a VACUUM process on any particular table:

``` 
autovacuuming threshold = autovacuum_vacuum_threshold + autovacuum_vacuum_scale_factor * estimated number of rows in the table
```

For example, if a table contains an estimated 5,000 rows, the autovacuum daemon (configured using the default settings listed above) would launch a VACUUM on it whenever the number of dead rows in that table surpasses a threshold of `50 + 0.2 * 5000`, or 1,050.

If it detects that a table has recently seen an increase in updates, the autovacuum process will run an `ANALYZE` command to gather statistics to help the query planner make more informed decisions. Each VACUUM process also updates the [visibility map](https://www.postgresql.org/docs/current/static/storage-vm.html), which shows which pages are visible to active transactions. This can improve the performance of index-only scans and will make the next VACUUM more efficient by enabling it to skip those pages. VACUUM processes can normally run concurrently with most operations like SELECT/INSERT/UPDATE/DELETE queries, but they may not be able to operate on a table if there is a lock-related conflict (e.g. due to an ALTER TABLE or LOCK TABLE operation).


| **Metric description**  | **Name** | [**Metric type**][monitoring-101-blog] | [**Availability**][part-2] |
| :------------ | :----------- | :------------------- | :------------------- |
| Locks     | lock         | Other |  pg_locks | 
| Deadlocks (v. 9.2+)     | deadlocks      | Other |  pg_stat_database | 
| Dead rows     | n_dead_tup          | Other |  pg_stat_user_tables | 

<div id="locks"></div>
**Metrics to watch:**  

**Locks:** [PostgreSQL grants locks](https://www.postgresql.org/docs/current/static/explicit-locking.html) to certain transactions in order to ensure that data remains consistent across concurrent queries. You can also query the [`pg_locks` view][pg-locks] to see the active locks on the database, which objects have locks, and which processes are waiting to place locks on objects.

Viewing the number of locks per table, categorized by lock mode, can help ensure that you are able to access data consistently. Some types of lock modes, such as ACCESS SHARE, are less restrictive than others, like ACCESS EXCLUSIVE (which conflicts with every other type of lock), so it can be helpful to focus on monitoring the more restrictive lock modes. A high rate of locks in your database indicates that active connections could be building up from long-running queries, which will result in queries timing out.  

{{< img src="postgresql-monitoring-locks_by_lockmode.png" alt="postgresql locks" popup="true" wide="true" border="true" >}}

**Deadlocks:** A deadlock occurs when one or more transactions holds exclusive lock(s) on the same rows/tables that other transactions need in order to proceed. Let's say that transaction A has a row-level lock on row 1, and transaction B has a row-level lock on row 2. Transaction A then tries to update row 2, while transaction B requests a lock on row 1 to update a column value. Each transaction is forced to wait for the other transaction to release its lock before it can proceed. 

In order for either transaction to complete, one of the transactions must be rolled back in order to release a lock on an object that the other transaction needs. PostgreSQL uses a [`deadlock_timeout`](https://www.postgresql.org/docs/current/static/runtime-config-locks.html) setting to determine how long it should wait for a lock before checking if there is a deadlock. The default is one second, but it's generally not advised to lower this, because checking for deadlocks uses up resources. The documentation advises that you should aim to avoid deadlocks by ensuring that your applications acquire locks in the same order all the time, to avoid conflicts.

**Dead rows:** If you have a vacuuming schedule in place (either through autovacuum or some other means), the number of dead rows should not be steadily increasing over time—this indicates that something is interfering with your VACUUM process. VACUUM processes can get blocked if there is a lock on the table/row that needs to be vacuumed. If you suspect that a VACUUM is stuck, you will need to investigate to see what is causing this slowdown, as it can lead to slower queries and increase the amount of disk space that PostgreSQL uses. Therefore, it's crucial to monitor the number of dead rows to ensure that your tables are being maintained with regular, periodic VACUUM processes.

{{< img src="postgresql-monitoring-dead-rows-sawtooth.png" alt="postgresql dead rows removed by vacuum process" caption="The number of dead rows normally drops after a VACUUM process runs successfully, and then rises again as the database accumulates more dead rows over time, resulting in a sawtooth pattern." wide="true" border="true" >}}

### Replication and reliability
As mentioned earlier, PostgreSQL writes and updates data by noting each transaction in the [write-ahead log (WAL)][wal-docs]. In order to maintain data integrity without sacrificing too much performance, PostgreSQL only needs to record updates in the WAL and then commit the WAL (not the actual updated page/block) to disk to ensure data reliability in case the primary fails. After logging the transaction to the WAL, PostgreSQL will check if the block is in memory, and if so, it will update it in memory, marking it as a "dirty page." 

The [`wal_buffers`](https://www.postgresql.org/docs/9.6/static/runtime-config-wal.html#GUC-WAL-BUFFERS) setting specifies the amount of shared memory that WAL can use to store data not yet written to disk. By default, PostgreSQL will set this value to about 3% of `shared_buffers`. You can adjust this setting, but keep in mind that it cannot be less than 64 KB, or greater than the size of one WAL segment (16 MB). The WAL is flushed to disk every time a transaction is committed. It is also flushed to disk either every [`wal_writer_delay`](https://www.postgresql.org/docs/9.6/static/runtime-config-wal.html#GUC-WAL-WRITER-DELAY) ms (200 ms, by default), or when the WAL reaches a certain size, as specified by `wal_writer_flush_after` (1 MB, by default). [According to the documentation](https://www.postgresql.org/docs/9.6/static/runtime-config-wal.html#GUC-WAL-WRITER-DELAY), the maximum window of potential data loss is actually about 3X the value of `wal_writer_delay`, because the WAL writer tries to optimize performance by writing whole pages to disk at a time when the database is very busy. 

#### WAL replication in PostgreSQL
Many users set up PostgreSQL to replicate WAL changes from each primary server to one or more standby servers, in order to improve performance by directing queries to specific pools of read-only standbys. Replication also makes the database highly available—if the primary server experiences a failure, the database will always be prepared to failover to a standby. Replication is typically achieved in any one of three ways:

**Streaming replication:** The primary server streams WAL updates to the standby as they come in. This method is asynchronous, which means that there is a slight delay between a transaction that has been committed in the primary and the same transaction taking effect in the standby.

{{< img src="postgresql-monitoring-streaming-replication2.png" alt="monitor postgres streaming replication diagram" caption="In this example of streaming replication, the primary server asynchronously replicates its WAL updates to three standby servers." border="true" >}}

**Cascading replication:** A standby server receives updates from the primary, and then communicates those updates to other standby servers. This method helps reduce the number of direct connections to the primary. This method of replication is also asynchronous.

{{< img src="postgresql-monitoring-cascading-replication.png" alt="monitor postgres streaming replication diagram" caption="In this example of cascading replication, the primary server asynchronously replicates its WAL updates to one standby, which then communicates those updates to two other standby servers." border="true" >}}

**Synchronous replication:** Available in PostgreSQL version 9.1+, this is the only method that ensures that every transaction on the primary is written to each standby server's WAL, and written to disk, before the transaction can be considered "committed." This is slower than the asynchronous methods, but it is the only method that ensures that data is always consistent across the primary and all standby servers, even in the event that the primary server crashes.

{{< img src="postgresql-monitoring-synchronous-replication.png" alt="monitor postgres synchronous replication diagram" caption="In this example, a primary server replicates its WAL updates to three standby servers." border="true" >}}

#### Checkpoints and PostgreSQL reliability
Of course, the WAL is not the only file that needs to be committed to disk when data is inserted, updated, or deleted. [PostgreSQL's checkpoints][checkpoint-docs] are designed to periodically flush updated/dirty buffers (stored in memory) to disk. The WAL also notes each time a checkpoint completes, so that, in the event of a failure, the standby server will know where to pick up and start replaying transactions. 

Checkpoints occur every [`checkpoint_timeout`](https://www.postgresql.org/docs/current/static/runtime-config-wal.html#GUC-CHECKPOINT-TIMEOUT) seconds (5 minutes by default), or when the WAL file reaches a certain size specified in your configuration settings. This setting was known as [`checkpoint_segments` prior to version 9.5](https://www.postgresql.org/docs/9.4/static/runtime-config-wal.html#GUC-CHECKPOINT-SEGMENTS) (~48 MB by default) , and renamed to [`max_wal_size`](https://www.postgresql.org/docs/9.6/static/runtime-config-wal.html#GUC-MAX-WAL-SIZE) in versions 9.5+ (1 GB by default). When either one of these settings is reached, it will trigger a checkpoint.

Checkpoint frequency is also influenced by the [`checkpoint_completion_target`](https://www.postgresql.org/docs/current/static/runtime-config-wal.html#GUC-CHECKPOINT-COMPLETION-TARGET) setting, which is specified as the ratio of how quickly a checkpoint should be completed in relation to the time between checkpoints. By default, it is 0.5, which means that it aims to complete the current checkpoint in about half the time between the current checkpoint and when the next checkpoint is estimated to run. This is designed to space out checkpoints to distribute the I/O load of writing data to disk. 

#### Replication & checkpoint metrics
| **Metric description**  | **Name** | [**Metric type**][monitoring-101-blog] | [**Availability**][part-2] |
| :------------ | :----------- | :------------------- | :------------------- |
| Replication delay (seconds)    |  time elapsed since pg_last_xlog_replay_location() timestamp, or pg_last_wal_replay_lsn() in version 10+       | Other |  pg_xlog | 
| Number of checkpoints requested & scheduled    | checkpoints_req & checkpoints_timed      | Other  |  pg_stat_bgwriter | 
| Number of buffers written during checkpoints    | buffers_checkpoint      | Other  |  pg_stat_bgwriter | 
| Number of buffers written by the background writer    | buffers_clean      | Other  |  pg_stat_bgwriter | 
| Number of buffers written by backends    | buffers_backend     | Other  |  pg_stat_bgwriter | 

**Metric to alert on:**  
**Replication delay:** If you are running some form of asynchronous replication, tracking replication delay on each standby/replica server is important, because it helps you estimate how long it would take for your data to become consistent on a standby if your primary were to crash.

Replication delay is typically measured as the time delay between the last WAL update received from a primary, and the last WAL update applied/replayed on disk on that standby/replica. Collecting and graphing this metric over time is particularly insightful, as it tells you how consistently data is being updated across your replica servers. 

For example, if you see that replication lag is increasing by one second, every second, on a standby that accepts read queries, that means that it hasn’t been receiving any new data updates, so it could be serving queries with stale or outdated data. PostgreSQL enables you to track replication lag in seconds (as of version 9.1) and bytes (as of version 9.2). We'll explain how to collect this metric in the [next part][part-2] of this series.

If your data is constantly being updated, you should closely monitor replication lag on any standby/replica servers that are serving read queries, to ensure that they are not serving stale data. However, it's also important to monitor lag on standby servers that are not actively serving any queries, because they need to be prepared to step in quickly if the primary fails.  

{{< img src="postgresql-monitoring-replication-delay-seconds.png" alt="postgresql replication delay on replica" wide="true" border="true" >}}

**Metrics to watch:**  
**Requested checkpoints:** If you see a high percentage of checkpoints being requested as opposed to time-based/scheduled, this tells you that WAL updates are reaching the `max_wal_size` or `checkpoint_segments` size before the `checkout_timeout` is reached. This indicates that your checkpoints can't keep up with the rate of data updates. Generally it's better for your databases' health if checkpoints are scheduled rather than requested, as the latter can indicate that your databases are under heavy load. Increasing `max_wal_size` or `checkpoint_segments` can help checkpoints become a time-driven process rather than a load-driven one, but only to a certain extent. If you are using a version prior to 9.5, the default `checkpoint_segments` setting is quite low, at 48 MB, so you can probably safely increase this up to 32 segments (or ~1 GB). As of version 9.5 and later, the default `max_wal_size` has already been raised to 1 GB.

{{< img src="postgresql-monitoring-checkpoints-graph.png" alt="postgresql scheduled vs requested checkpoints" wide="true" >}}

**Buffers written by checkpoints as percentage of total buffers written:** [`pg_stat_bgwriter`][pt-2-bgwriter] provides metrics for each of the three ways that PostgreSQL flushes dirty buffers to disk: via backends (buffers_backend), via the background writer (buffers_clean), or via the checkpoint process (buffers_checkpoint). PostgreSQL uses the [background writer](https://www.postgresql.org/docs/9.6/static/runtime-config-resource.html#RUNTIME-CONFIG-RESOURCE-BACKGROUND-WRITER) process to help lighten each checkpoint's I/O load by writing dirty shared buffers to disk periodically in between checkpoints. However, there are times when the background writer may increase I/O load unnecessarily—for instance, if you are updating the same page/block of data multiple times between checkpoints. If the background writer stepped in it would write the update to disk multiple times, whereas that update would normally have just been flushed once, during the next checkpoint. 

If you see an increasing number of buffers being written directly by backends, this indicates that you have a write-heavy load that is generating dirty buffers so quickly that it can't keep up with the rate of checkpoints. It's generally better for performance if the majority of buffers are written to disk during checkpoints, as opposed to directly by backends or by the background writer.

### Resource utilization
Like any other database, PostgreSQL relies on many system resources to complete its work, including CPU, disk, memory, and network bandwidth. Monitoring these system-level metrics can help ensure that PostgreSQL has the resources it needs to respond to queries and update data throughout its tables and indexes. PostgreSQL also collects metrics about its own resource usage, including connections, shared buffer usage, and disk utilization, which we'll cover in more detail below. 

#### Connections
| **Metric description**  | **Name** | [**Metric type**][monitoring-101-blog] | [**Availability**][part-2] |
| :------------ | :----------- | :------------------- | :------------------- |
| Number of active connections    | numbackends      | Resource: Utilization  |  pg_stat_database | 
| Percentage of max connections in use    | numbackends as percentage of max_connections in pg_settings      | Resource: Utilization  |  pg_stat_database, pg_settings | 
| Client connections waiting on a server connection (PgBouncer)    | cl_waiting      | Resource: Saturation  |  PgBouncer | 
| Max time a client connection has been waiting to be served (PgBouncer)    | maxwait      | Resource: Saturation  |  PgBouncer | 

The PostgreSQL primary server process forks a new process every time a client requests a connection. PostgreSQL sets a [`connection limit`](https://www.postgresql.org/docs/9.6/static/runtime-config-connection.html#GUC-MAX-CONNECTIONS), which determines the maximum number of connections that can be opened to the backend at any one time. However, note that the maximum number of connections may be lower, depending on the operating system's limits. 

In high-concurrency environments, using a connection pool like [PgBouncer][pgbouncer] can help distribute the number of direct connections to your primary server. The pool serves as a proxy between your applications and PostgreSQL backends. 

If you see the number of active connections consistently approaching the number of maximum connections, this can indicate that applications are issuing long-running queries, and constantly creating new connections to send other requests, instead of reusing existing connections. Using a connection pool can help ensure that connections are consistently reused as they go idle, instead of placing load on the primary server to frequently have to open and close connections. 

You can also set an [idle_in_transaction_session_timeout](https://www.postgresql.org/docs/current/static/runtime-config-client.html#GUC-IDLE-IN-TRANSACTION-SESSION-TIMEOUT) value to instruct PostgreSQL to close any connections that remain idle for the specified period of time. By default, this value is 0, which means that it is disabled. 

#### Shared buffer usage
| **Metric description**  | **Name** | [**Metric type**][monitoring-101-blog] | [**Availability**][part-2] |
| :------------ | :----------- | :------------------- | :------------------- |
| Blocks in this database that were shared buffer hits vs. read from disk    | blks_hit  vs. blks_read    | Other |  pg_stat_database |
| Blocks in this table that were shared buffer hits vs. read from disk   | heap_blks_hit  vs. heap_blks_read    | Other |  pg_statio_user_tables |
| Blocks from indexes in this table that were shared buffer hits vs. read from disk   | idx_blks_hit vs. idx_blks_read      | Other |  pg_statio_user_tables |

When PostgreSQL reads or updates data, it checks for the block in the shared buffer cache first, and also in the OS cache, to see if it can serve the request without having to read from disk. If the block is not cached, it will need to access the data from disk, but it will cache it in the OS cache as well as the database's shared buffer cache so that the next time that data is queried, it won't need to access the disk. Inevitably, this means that some data will be cached in more than one place at any one time, so the [documentation recommends][shared-buffers] limiting `shared_buffers` to 25 percent of the OS memory.

[`pg_statio`][pt-2-pgstatio] only provides statistics that pertain to the PostgreSQL shared buffer cache, not the OS cache. Therefore, if your cache hit rate *looks* low, it's important to remember that it doesn't account for pages that were hits in the OS cache, even they weren't hits in the shared buffer cache. While it is helpful to keep an eye on the cache hit rate, `pg_statio` only paints one side of the picture when it comes to PostgreSQL's actual memory usage. You should supplement PostgreSQL's `pg_statio` statistics with your kernel's I/O and memory utilization metrics to help paint a clearer picture of performance.

#### Disk and index usage
| **Metric description**  | **Name** | [**Metric type**][monitoring-101-blog] | [**Availability**][part-2] |
| :------------ | :----------- | :------------------- | :------------------- |
| Disk space used by each table (excluding indexes)   |  pg_table_size | Resource: Utilization | [Database object management functions](https://www.postgresql.org/docs/current/static/functions-admin.html#FUNCTIONS-ADMIN-DBSIZE) |
| Disk space used by indexes in the table   |  pg_indexes_size | Resource: Utilization | [Database object management functions](https://www.postgresql.org/docs/current/static/functions-admin.html#FUNCTIONS-ADMIN-DBSIZE) |
| Number of index scans initiated on this table or index    |  idx_scan | Resource: Utilization | pg_stat_user_tables or pg_stat_user_indexes |

PostgreSQL collects statistics internally to help you track the size of tables and indexes over time, which is helpful for gauging future changes in query performance. As your tables and indexes grow in size, queries will take longer, and indexes will require more disk space, which means that you either need to scale up the instance's disk space, [partition your data][postgresql-partitioning], or rethink your indexing strategy. If you see any unexpected growth in table or index size, it may also point to problems with VACUUMs not running properly. 

{{< img src="postgresql-monitoring-index-scans-by-index.png" alt="postgresql sequential scans with timeshift" wide="true" >}}

In the [next part][part-2] of this series, we'll show you how to query `pg_stat_user_indexes` to see if there are any underutilized indexes that you could remove in order to free up disk space and decrease unnecessary load on the database. As mentioned in a previous section, indexes can be increasingly difficult to maintain as they grow in size, so it may not be worth applying resources to data that isn't queried very often. 

## Next steps in PostgreSQL monitoring
In this post, we've covered an overview of PostgreSQL monitoring and its key performance metrics. As you continue to scale your PostgreSQL deployment over time, keeping an eye on these metrics will help you effectively detect and troubleshoot potential issues in real time. Read the [next part][part-2] of this series to learn how to collect all of these metrics from PostgreSQL, or check out [Part 3](https://www.datadoghq.com/blog/collect-postgresql-data-with-datadog/) to learn how to monitor these metrics alongside distributed traces from your applications, all in one place.


[postgres-scalable]: https://www.postgresql.org/about/
[stats-collector-docs]: https://www.postgresql.org/docs/current/static/monitoring-stats.html
[monitoring-101-blog]: https://www.datadoghq.com/blog/monitoring-101-collecting-data/
[planner-docs]: https://www.postgresql.org/docs/current/static/planner-optimizer.html
[tuple-header]: https://github.com/postgres/postgres/blob/master/src/include/access/htup_details.h#L142
[explain-docs]: https://www.postgresql.org/docs/current/static/using-explain.html
[mvcc-docs]: https://www.postgresql.org/docs/current/static/mvcc-intro.html
[toast-docs]: https://www.postgresql.org/docs/current/static/storage-toast.html
[pg-locks]: https://www.postgresql.org/docs/current/static/view-pg-locks.html
[wal-docs]: https://www.postgresql.org/docs/current/static/wal-intro.html
[checkpoint-docs]: https://www.postgresql.org/docs/current/static/wal-configuration.html
[pgbouncer]: https://pgbouncer.github.io/
[postgres-availability-docs]: https://www.postgresql.org/docs/current/static/different-replication-solutions.html
[postgres-10-release]: https://www.postgresql.org/docs/current/static/release-10.html
[explain-depesz]: https://explain.depesz.com/
[random-page-cost]: https://www.postgresql.org/docs/current/static/runtime-config-query.html#GUC-RANDOM-PAGE-COST
[shared-buffers]: https://www.postgresql.org/docs/current/static/runtime-config-resource.html#GUC-SHARED-BUFFERS
[postgresql-partitioning]: https://www.postgresql.org/docs/current/static/ddl-partitioning.html
[pt-2-bgwriter]: /blog/postgresql-monitoring-tools/#pg-stat-bgwriter
[pt-2-pgstatio]: /blog/postgresql-monitoring-tools/#pg-statio-user-tables
[internal-statistics-docs]: https://www.postgresql.org/docs/current/static/planner-stats.html
[part-2]: /blog/postgresql-monitoring-tools
[part-3]: /blog/collect-postgresql-data-with-datadog
[autovacuum-docs]: https://www.postgresql.org/docs/current/static/routine-vacuuming.html#AUTOVACUUM
[pgclass-docs]: https://www.postgresql.org/docs/current/static/catalog-pg-class.html