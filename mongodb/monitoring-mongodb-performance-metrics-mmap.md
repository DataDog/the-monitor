# Monitoring MongoDB performance metrics (MMAP)


*This post is part 1 of a 3-part series about monitoring MongoDB performance with the MMAPv1 storage engine. [Part 2](/blog/collecting-mongodb-metrics-and-statistics) explains the different ways to collect MongoDB metrics, and [Part 3](/blog/monitor-mongodb-performance-with-datadog) details how to monitor its performance with Datadog.*

If you are using the WiredTiger storage engine, which was introduced with MongoDB 3.0 and is now the default storage engine, visit the companion article “[Monitoring MongoDB performance metrics (WiredTiger)](/blog/monitoring-mongodb-performance-metrics-wiredtiger)”.

What is MongoDB?
----------------


There are different types of NoSQL databases:



-   Key-value stores like [Redis](/blog/how-to-monitor-redis-performance-metrics/) where each item is stored and retrieved with its name (key)
-   Wide column stores such as [Cassandra](/blog/how-to-monitor-cassandra-performance-metrics/) used to quickly aggregate large datasets, and for which columns can vary from one row to another
-   Graph databases, like Neo4j or Titan, which use graph structures to store networks of data
-   Document-oriented databases which store data as documents thus offering a more flexible structure than other databases: fields can store arrays, or two records can have different fields for example. [MongoDB](https://www.mongodb.com/) is a document-oriented database, as are CouchDB and [Amazon DynamoDB](/blog/top-dynamodb-performance-metrics/).



MongoDB is cross-platform and represents its documents in a binary-encoded JSON format called [BSON](https://www.mongodb.com/json-and-bson) (Binary JSON). The lightweight binary format adds speed to the flexibility of the JSON format, along with more data types. Fields inside MongoDB documents can be indexed.

MongoDB ensures high availability thanks to its replication mechanisms, horizontal scalability allowed by sharding, and is currently [the most widely adopted](http://db-engines.com/en/ranking) document store. It is used by companies such as Facebook, eBay, Foursquare, Squarespace, Expedia, and Electronic Arts.

Key MongoDB performance metrics to monitor
------------------------------------------


{{< img src="mongodb-metrics.png" alt="monitoring MongoDB dashboard" popup="true" size="1x" >}}

By properly monitoring MongoDB you can quickly spot slowdowns, hiccups, or pressing resource limitations, and know which actions to take to correct these issues before there are user-facing consequences. Here are the key areas you will want to track and analyze metrics.



-   [Throughput metrics](#throughput-metrics)
-   [Database performance](#database-performance)
-   [Resource utilization](#resource-utilization)
-   [Resource saturation](#resource-saturation)
-   [Errors](#errors-asserts) (asserts)



In this article, we focus on the metrics available in MongoDB when using the [MMAPv1](https://docs.mongodb.com/manual/core/mmapv1/) storage engine. If your storage engine is [WiredTiger](https://docs.mongodb.com/manual/core/wiredtiger/), you should read [the article dedicated to it](/blog/monitoring-mongodb-performance-metrics-wiredtiger).

This article references metric types terminology introduced in [our Monitoring 101 series](/blog/monitoring-101-collecting-data/), which provides a framework for metric collection and alerting.

All these metrics are accessible using a variety of tools, including MongoDB’s utilities, commands (indicated in this article for each metric presented), or dedicated monitoring tools. For details on metrics collection using any of these methods, see [Part 2](/blog/collecting-mongodb-metrics-and-statistics) of this series.

### Throughput metrics


{{< img src="mongodb-throughput-metrics.png" alt="monitoring MongoDB Throughput metrics" size="1x" >}}

Throughput metrics are crucial and most of your alerts should be set on these metrics in order to avoid any [performance](#database-performance) issue, [resource saturation](#resource-saturation), or [errors](#errors-asserts). The majority of the metrics presented in the other sections are typically used to investigate problems.

#### Read and Write operations


To get a high-level view of your cluster’s activity levels, the most important metrics to monitor are the number of clients making read and write requests to MongoDB, and the number of operations they are generating. Understanding how, and how much, your cluster is being used will help you optimize MongoDB’s performance and avoid overloading your database. For instance, your strategy to scale up or out (see [corresponding section](#scaling-mongodb-sharding-vs-replication) at the end of this article) should take into account the type of workload your database is receiving.



<table>
<thead>
<tr class="header">
<th><strong>Metric Description</strong></th>
<th><strong>Name</strong></th>
<th><a href="/blog/monitoring-101-collecting-data/"><strong>Metric Type</strong></a></th>
<th><a href="/blog/collecting-mongodb-metrics-and-statistics"><strong>Availability</strong></a></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Number of read requests received during the selected time period (query, getmore)</td>
<td>opcounters.query, opcounters.getmore</td>
<td>Work: Throughput</td>
<td>serverStatus</td>
</tr>
<tr class="even">
<td>Number of write requests received during the selected time period (insert, delete, update)</td>
<td>opcounters.insert, opcounters.update, opcounters.delete</td>
<td>Work: Throughput</td>
<td>serverStatus</td>
</tr>
<tr class="odd">
<td>Number of clients with read operations in progress or queued</td>
<td>globalLock.activeClients.readers</td>
<td>Work: Throughput</td>
<td>serverStatus</td>
</tr>
<tr class="even">
<td>Number of clients with write operations in progress or queued</td>
<td>globalLock.activeClients.writers</td>
<td>Work: Throughput</td>
<td>serverStatus</td>
</tr>
</tbody>
</table>



NOTE: A *getmore* is the operation the [cursor](#cursors) executes to get additional data from a query.

##### Metrics to alert on:


By properly monitoring the **number of read and write requests** you can prevent resource saturation, spot bottlenecks, quickly find the cause of potential overloads, and know when to scale [up or out](#scaling-mongodb-sharding-vs-replication). The `currentQueue` metrics (presented in the section about [Resource Saturation](#resource-saturation)) will confirm if requests are accumulating faster than they are being processed. Look also at `activeClients.readers` or `activeClients.writers` to check if the number of active clients explains the requests load. These two activeClients metrics are reported under “[globalLock](https://docs.mongodb.com/manual/reference/command/serverStatus/#server-status-global-lock)” even if they are not really related to global lock.

In order to be able to quickly spot the potential causes of abnormal changes in traffic, you should break down your graphs by operation type: *query* and *getmore* for read requests, *insert*, *update*, and *delete* for write requests.

### Database performance


{{< img src="mongodb-database-performance.png" alt="monitoring MongoDB database performance metrics" size="1x" >}}

#### Replication and Oplog


The metrics presented in this paragraph matter only if you use a replica set, which you should do if you run MongoDB in production in order to ensure high data availability.

The oplog (operations log) constitutes the basis of MongoDB’s replication mechanism. It’s a limited-size collection stored on primary and secondary nodes that keeps track of all the write operations. Write operations are applied on the primary node itself and then recorded on its oplog. Right after secondary nodes copy and apply these changes asynchronously. But if the primary node fails before the copy to the secondary is made, data might not be replicated.

Each replica contains its own oplog, corresponding to its view of the data at this point in time based on what it saw the most recently from the primary.



<table>
<thead>
<tr class="header">
<th><strong>Metric Description</strong></th>
<th><strong>Name</strong></th>
<th><a href="/blog/monitoring-101-collecting-data/"><strong>Metric Type</strong></a></th>
<th><a href="/blog/collecting-mongodb-metrics-and-statistics"><strong>Availability</strong></a></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Size of the oplog (MB)</td>
<td>logSizeMB</td>
<td>Other</td>
<td>getReplicationInfo</td>
</tr>
<tr class="even">
<td>Oplog window (seconds)</td>
<td>timeDiff</td>
<td>Other</td>
<td>getReplicationInfo</td>
</tr>
<tr class="odd">
<td>Replication Lag: delay between a write operation on the primary and its copy to a secondary (milliseconds)</td>
<td>members.optimeDate[primary] - members.optimeDate[secondary member] **</td>
<td>Work: Performance</td>
<td>replSetGetStatus</td>
</tr>
<tr class="even">
<td>Replication headroom: difference between the primary’s oplog window and the replication lag of the secondary (milliseconds)</td>
<td>getReplicationInfo.timeDiff x 1000 - (replSetGetStatus.members.optimeDate[primary] - replSetGetStatus.members.optimeDate[secondary member])</td>
<td>Work: Performance</td>
<td>getReplicationInfo and replSetGetStatus</td>
</tr>
<tr class="odd">
<td>Replica set member state</td>
<td>members.state</td>
<td>Resource: Availability</td>
<td>replSetGetStatus</td>
</tr>
</tbody>
</table>



\*\* For the calculation of Replication Lag, **optimeDate** values are provided with the [isoDate](https://docs.mongodb.com/manual/reference/glossary/#term-isodate) format (YYYY-MM-DD HH:MM.SS.ms) so the difference will be in milliseconds.

##### Metrics to alert on:


**Replication lag** represents how far a secondary is behind the primary. Obviously you want to keep a replication lag as small as possible. It's especially true if yours is the rare case where your secondary nodes address reads (usually not advised, see [sections about scaling MongoDB](#scaling-mongodb-sharding-vs-replication)) since you want to avoid serving stale data. Ideally, replication lag is equal to zero, which should be the case if you don’t have load issues. If it gets too high for all secondary nodes, the integrity of your data set might be compromised in case of failover (secondary member taking over as the new primary because the current primary is unavailable). Indeed write operations happening during the delay are not immediately propagated to secondaries and related changes might be lost if the primary fails.

You might want to set up a warning notification for any lag higher than 60 seconds. A high priority alert can be set for lags exceeding 240 seconds. With a healthy replica set, you shouldn’t get false positive with this threshold.

A high replication lag can be due to:



-   Networking issue between the primary and secondary making nodes unreachable: check `members.state` to spot unreachable nodes
-   A secondary node applying data slower than the primary: check the `backgroundFlushing.average_ms` metric (see [section about background flush](#background-flush))
-   Insufficient write capacity in which case you should add more shards: check queued write requests (see [section about resource saturation](#resource-saturation))
-   Slow operations on the primary node blocking replication. You can [spot slow queries](https://docs.mongodb.com/manual/tutorial/manage-the-database-profiler/#profiling-levels) with the [db.getProfilingStatus()](https://docs.mongodb.com/manual/reference/method/db.getProfilingStatus/#db.getProfilingStatus) command or through the *Visual Query Profiler* in [MongoDB Ops Manager](https://www.mongodb.com/products/ops-manager) if you are using it: level 1 corresponds to slow operations (taking longer than the threshold defined by the `operationProfiling.slowOpThresholdMs` parameter set to 100 ms by default). It can be due to heavy write operations on the primary node or an under-provisioned secondary. You can prevent the latter by scaling up the secondary to match the primary capacity. You can use *“majority”* [*write concern*](https://docs.mongodb.com/manual/reference/write-concern/) to make sure writes are not getting ahead of replication.



{{< img src="replication-lag-grouped-by-replica-set.png" alt="monitoring MongoDB replication lag by replica set" popup="true" size="1x" >}}

The **oplog window** represents the interval of time between the oldest and the latest entries in the oplog, which usually corresponds to the approximate amount of time available in the primary's replication oplog. So if a secondary is down longer than this oplog window, it won’t be able to catch up unless it completely resyncs all data from the primary. The amount of time it takes to fill the oplog varies: during heavy traffic times, it will shrink since the oplog will receive more operations per second. If the oplog window for a primary node is getting too short you should consider [increasing the **size of your oplog**](https://docs.mongodb.com/manual/tutorial/change-oplog-size/). MongoDB advises to send a warning notification if the oplog windows is 25% below its usual value during traffic peaks, and a high priority alert under 50%.

If the **replication headroom** is rapidly shrinking and is about to become negative, that means that the replication lag is getting higher than the oplog window. In that case, write operations recorded in the oplog will be overwritten before secondary nodes have time to replicate them. MongoDB will constantly have to resync the entire data set on this secondary which takes much longer than just fetching new changes from the oplog. Properly monitoring and alerting on **Replication Lag** and **oplog window** should allow you to prevent this.

The **replica set member state** is an integer indicating the current status of a node in a replica set. You should alert on error state changes so you can quickly react if a host is having issues. Here are potentially problematic states:



-   ***Recovering*** (state = 3): the members is performing startup self-checks, or just completed a [rollback](https://docs.mongodb.com/manual/core/replica-set-rollbacks/) or a [resync](https://docs.mongodb.com/manual/tutorial/resync-replica-set-member/). A *Recovering* state can be fine if it’s intentional (for example when resyncing a secondary) but if it’s unexpected, you should find the root cause of this issue in order to maintain a healthy replica set.
-   ***Unknown*** (state = 6): the member doesn’t communicate any status information to the replica set.
-   ***Down*** (state = 8): the member lost its connection with the replica set. This is critical if there is no replica to address requests to the node that went down.
-   ***Rollback*** (state = 9): when a secondary member takes over as the new primary before writes were totally replicated to it, the old primary reverts these changes. If you don't use "majority" [write concern](https://docs.mongodb.com/manual/reference/write-concern/), you should trigger a paging alert in case a node shows a *Rollback* state since you might lose data changes from write operations. Rollbacks of acknowledged data [should be avoided](https://docs.mongodb.com/manual/core/replica-set-rollbacks/#avoid-replica-set-rollbacks).
-   ***Removed*** (state = 10): the member has been removed from the replica set.



You can find all the member states [here](https://docs.mongodb.com/manual/reference/replica-states/).

#### Journaling


While oplog stores recent write operations for replication, journaling is a write-ahead process. It is enabled by default since v2.0 and you shouldn’t turn it off, especially when using MongoDB in production.

The purpose and underlying mechanisms of journaling with the MMAPv1 storage engine are different than with [WiredTiger](/blog/monitoring-mongodb-performance-metrics-wiredtiger), and available metrics won’t be the same.

With MMAPv1, unlike with WiredTiger, an unclean shutdown can impact data integrity. So MongoDB applies writes to journal files first before applying them to in-memory data files. Thus if the process stops unexpectedly before editing the data files, when resuming, MongoDB can recover data from the journal files and properly apply the changes to the data files. Consistency is maintained.

For both storage engines, the frequency of committing/syncing the journal to disk is defined by the parameter [storage.journal.commitIntervalMs](https://docs.mongodb.com/manual/reference/configuration-options/#storage.journal.commitIntervalMs) which can be tuned. Decreasing its value reduce the chances of data loss since writes will be recorded more frequently but may increase the latency of write operations.



<table>
<thead>
<tr class="header">
<th><strong>Metric Description</strong></th>
<th><strong>Name</strong></th>
<th><a href="/blog/monitoring-101-collecting-data/"><strong>Metric Type</strong></a></th>
<th><a href="/blog/collecting-mongodb-metrics-and-statistics"><strong>Availability</strong></a></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Count of transactions that have been written to the journal in the last journal group commit interval.</td>
<td>dur.commits</td>
<td>Resource: Utilization</td>
<td>serverStatus</td>
</tr>
<tr class="even">
<td>Volume of data written to the journal as part of the last journal group commit interval (MB)</td>
<td>dur.journaledMB</td>
<td>Resource: Utilization</td>
<td>serverStatus</td>
</tr>
</tbody>
</table>



Tracking the number of transactions and the amount of data written to the journal provides insights on load. This can be useful when troubleshooting.

#### Background flush


With the MMAPv1 storage engine, background flush is the process of applying data modification from data files to disk, in addition to having written them to the journal (see previous section).

Statistics about this mechanism are available and should be monitored if you are using MMAPv1. They are particularly useful if you have concerns about write performance.



<table>
<thead>
<tr class="header">
<th><strong>Metric Description</strong></th>
<th><strong>Name</strong></th>
<th><a href="/blog/monitoring-101-collecting-data/"><strong>Metric Type</strong></a></th>
<th><a href="/blog/collecting-mongodb-metrics-and-statistics"><strong>Availability</strong></a></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Average time taken by flushes to execute in the selected time period (milliseconds)</td>
<td>backgroundFlushing.average_ms *</td>
<td>Resource: Performance</td>
<td>serverStatus</td>
</tr>
<tr class="even">
<td>Time taken by the last flush operation to execute (milliseconds)</td>
<td>backgroundFlushing.last_ms *</td>
<td>Resource: Performance</td>
<td>serverStatus</td>
</tr>
</tbody>
</table>



\*Only for the MMAPv1 storage engine

##### Metric to alert on:


The **average time taken by flushes to execute** should be monitored. Indeed MongoDB “flushes” writes to data files [every 60 seconds by default](https://docs.mongodb.com/manual/reference/configuration-options/#storage.syncPeriodSecs). This parameter can be tuned depending on the workload. So if your background flushes take more than this frequency value to execute, it means that MongoDB is continuously flushing to disk which can have a serious impact on your database performance. Your background flushes should usually take less than 1 second. If you see them taking more than 10 seconds on a regular basis, in order to reduce them, try to increase your disks I/O capacity (upgrading to faster disks) or inspect your write throughput capacity and add more shards if necessary. In some cases, tuning flush frequency can help smooth out peaks of flush times (decrease frequency if writes are applied many times to the same subset of documents, increase it otherwise).

Remember that, since this metric an average, it might be skewed by a past issue. If you see an abnormal value for `backgroundFlushing.averagems`, make sure to double check by looking at `backgroundFlushing.lastms`.

#### Concurrent operations management: Locking performance


In order to support simultaneous queries while avoiding write conflicts and inconsistent reads, MongoDB has an internal locking system. Suboptimal indexes, and poor schema design patterns can lead to locks being held longer than necessary.

The MMAPv1 storage engine, based on memory mapped files, was using database-level lock until v3.0. For these previous versions, locking metrics were really important since the mechanism could impact MongoDB’s capacity to handle concurrent requests. [Lock percentage](http://blog.cloud.mongodb.com/post/78650784046/learn-about-lock-percentage-concurrency-in) was important to track along with queues length.



<table>
<thead>
<tr class="header">
<th><strong>Metric Description</strong></th>
<th><strong>Name</strong></th>
<th><a href="/blog/monitoring-101-collecting-data/"><strong>Metric Type</strong></a></th>
<th><a href="/blog/collecting-mongodb-metrics-and-statistics"><strong>Availability</strong></a></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Average wait time to acquire the locks (Average Lock percentage)</td>
<td>locks.timeAcquiringMicros / locks.acquireWaitCount *</td>
<td>Resource: Saturation</td>
<td>serverStatus</td>
</tr>
<tr class="even">
<td>Time since the database last started and created the globalLock (ms)</td>
<td>globalLock.totalTime *</td>
<td>Resource: Utilization</td>
<td>serverStatus</td>
</tr>
</tbody>
</table>



\*Only for the MMAPv1 storage engine

Locks are responsible for requests being queued, so you should keep an eye on how long operations wait for a lock (**wait time to acquire the locks**), even if you are already monitoring [queued requests](#resource-saturation).





#### Cursors

When a read query is received, MongoDB returns a cursor which represents a pointer to the data set of the answer. To access all the documents resulted by the query, clients can then iterate over the cursor.



<table>
<thead>
<tr class="header">
<th><strong>Metric Description</strong></th>
<th><strong>Name</strong></th>
<th><a href="/blog/monitoring-101-collecting-data/"><strong>Metric Type</strong></a></th>
<th><a href="/blog/collecting-mongodb-metrics-and-statistics"><strong>Availability</strong></a></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Number of cursors currently opened by MongoDB for clients</td>
<td>metrics.cursor.open.total</td>
<td>Work: Throughput</td>
<td>serverStatus</td>
</tr>
<tr class="even">
<td>Number of cursors that have timed out during the selected time period</td>
<td>metrics.cursor.timedOut</td>
<td>Work: Throughput</td>
<td>serverStatus</td>
</tr>
<tr class="odd">
<td>The number of open cursors with timeout disabled</td>
<td>metrics.cursor.open.noTimeout</td>
<td>Other</td>
<td>serverStatus</td>
</tr>
</tbody>
</table>



##### Metrics to alert on:


A gradual increase in the **number of open cursors** without a corresponding growth of traffic is often symptomatic of poorly indexed queries. It can also be the result of long running queries due to large result sets. You should take a look to see how you could optimize them.

`cursor.timedOut` is incremented when a client connection has died without having gracefully closed the cursor. This cursor remains open on the server, consuming memory. By default MongoDB reaps these cursors after 10 minutes of inactivity. You should check if you have a large amount of memory being consumed from non-active cursors. A high number of timed out cursors can be related to application issues.

This also explains why cursors with no timeout should be avoided: they can prevent resources to be freed as it should and slow down internal system processes. Indeed the [DBQuery.Option.noTimeout](https://docs.mongodb.com/v3.0/reference/method/cursor.addOption/#DBQuery.Option.noTimeout) flag (until v3.0) or the [cursor.noCursorTimeout()](https://docs.mongodb.com/manual/reference/method/cursor.noCursorTimeout/#cursor.noCursorTimeout) method can be used to prevent the server to timeout cursors after a period of inactivity (idle cursors). You can make sure that there is no cursors with no timeout by checking if the `cursor.open.noTimeout` metric which count their number is always equal to zero.

### Resource Utilization


{{< img src="mongodb-resource-utilization.png" alt="monitoring MongoDB resource utilization metrics" size="1x" >}}

#### Connections


Abnormal traffic loads can lead to performance issues. That’s why the number of client connections should be closely monitored.



<table>
<thead>
<tr class="header">
<th><strong>Metric Description</strong></th>
<th><strong>Name</strong></th>
<th><a href="/blog/monitoring-101-collecting-data/"><strong>Metric Type</strong></a></th>
<th><a href="/blog/collecting-mongodb-metrics-and-statistics"><strong>Availability</strong></a></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Number of clients currently connected to the database server</td>
<td>connections.current</td>
<td>Resource: Utilization</td>
<td>serverStatus</td>
</tr>
<tr class="even">
<td>Number of unused connections available for new clients</td>
<td>connections.available</td>
<td>Resource: Utilization</td>
<td>serverStatus</td>
</tr>
</tbody>
</table>



##### Metric to alert on:


Unexpected changes in the **current number of client connections** can be due to errors on your application or driver. All the officially supported MongoDB drivers use pools of connections in order to efficiently re-use them. If the number of client connections is getting very high, it should be related to a rise in the number of real client requests in which case you can [scale](#scaling-mongodb-sharding-vs-replication) to support this increasing load. If this growth is not expected, it often indicates a driver or configuration issue. Knowing how many connections you should expect under low, normal, and peak traffics allows you to appropriately set your alerts. You might want to send a warning notification if there the number of connections is 50% higher than the number you usually see at peak, and a high priority alert if it exceeds twice this usual number at peak.

If MongoDB runs low on connections, in may not be able to handle incoming requests in a timely manner. That’s why you should also alert on the **percentage of connections used**: 100 x *current / (current + available)*.

This number of incoming connections is constrained but the limit can be changed except on older versions prior to 2.6. Since MongoDB 2.6, on Unix-based systems, the limit is simply defined by the [maxIncomingConnections](https://docs.mongodb.com/manual/reference/configuration-options/#net.maxIncomingConnections) parameter, set by default to 1 million connections on v2.6 and 65,536 connections since v3.0. This value [is configurable](https://docs.mongodb.com/manual/reference/ulimit/). **connections.current** should never get too close to this limit.

NOTE: the **connections.current** metrics also counts connections from shell and from other hosts like replicas or mongos instances.

#### Storage metrics



##### Understanding MongoDB’s storage structure and statistics


In MongoDB, data is stored in **documents** using the [BSON](https://docs.mongodb.com/manual/reference/glossary/#term-bson) format.

Documents (usually with similar or related purpose) are grouped into **collections**. A collection can be seen as the equivalent of a table in a relational database. For example, the database “users” can contain the two collections “purchase” and “profile”. In that case, you could access those collections with the namespaces *users.purchase* and *user.profile.*

With MMAPv1, collections are stored in areas called **extents**. Each extent contains either one index or one collection of documents (data). If an index or collection of data is too big to fit into a single extent, it can overflow into additional extents.

Extents are stored in larger storage units of 2GB called **data files**, and a set of data files constitutes a database. A MongoDB server has multiple databases.

Here is a diagram to better understand the storage structure with MMAPv1:

{{< img src="mongodb-mmap-storage-structure.png" alt="monitoring MongoDB MMAPv1 storage structure" popup="true" size="1x" >}}

##### Storage size metrics (from dbStats):


With the MMAPv1 storage engine, MongoDB pre-allocates extra space on the disk to documents so efficient in-place updates are possible since documents have room to grow without having to be relocated. This extra space is called **padding**.

Here are the different storage metrics you should know:



-   `dataSize` measures the space taken by all the documents and padding in the database. Because of padding, dataSize decreases if documents are deleted but not when they shrink or get bigger following an update—those operations just add to or borrow from the document’s padding.
-   `indexSize` returns the size of all indexes created on the database.
-   `storageSize` measures the size of all the data extents in the database. With MMAPv1, it’s always greater than or equal to dataSize because extents contain free space not yet used or freed by deleted and moved documents. storageSize is not affected when documents shrink or are moved.
-   `fileSize` corresponds to the size of your data files. It’s obviously always larger than storageSize and can be seen as the storage footprint of you database on disk. It decreases only if you delete a database and is not affected when collections, documents, or indexes are removed.



{{< img src="mongodb-mmap-dbstats-metrics.png" alt="monitoring MongoDB MMAPv1 dbStats metrics" popup="true" size="1x" >}}

##### Metrics to monitor




<table>
<thead>
<tr class="header">
<th><strong>Metric Description</strong></th>
<th><strong>Name</strong></th>
<th><a href="/blog/monitoring-101-collecting-data/"><strong>Metric Type</strong></a></th>
<th><a href="/blog/collecting-mongodb-metrics-and-statistics"><strong>Availability</strong></a></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Number of objects (documents) in the database among all the collections</td>
<td>objects</td>
<td>Resource: Utilization</td>
<td>dbStats</td>
</tr>
<tr class="even">
<td>Size of all documents + padding in the database (bytes)</td>
<td>dataSize</td>
<td>Resource: Utilization</td>
<td>dbStats</td>
</tr>
<tr class="odd">
<td>Size of all indexes in the database (bytes)</td>
<td>indexSize</td>
<td>Resource: Utilization</td>
<td>dbStats</td>
</tr>
<tr class="even">
<td>Size of all extents in the database (bytes)</td>
<td>storageSize</td>
<td>Resource: Utilization</td>
<td>dbStats</td>
</tr>
<tr class="odd">
<td>Size of data extents + index extents + unused space in the data files of the database (bytes)</td>
<td>fileSize *</td>
<td>Resource: Utilization</td>
<td>dbStats</td>
</tr>
</tbody>
</table>



\*Only for the MMAPv1 storage engine

##### Metrics to alert on:


If **memory space metrics** (dataSize, indexSize, storageSize, or fileSize) or the **number of objects** show a significant unexpected change while the database traffic remained within ordinary ranges, it can indicate a problem. A sudden drop of dataSize can be due to a large amount of data deletion, which should be quickly investigated if it was not expected.

With MMAPv1 MongoDB always keep an extra empty data file (2GB). So the value of the `fileSize` metric may be up to 4 GB larger than `storageSize`. However if it gets larger than that, it can indicates that your data is overly fragmented. Indeed, as documents and collections get deleted or moved, MongoDB keeps these empty spaces within the data files in order to reuse them later. However with the MMAPv1 storage, it cannot return it to the OS. [Check this section](https://docs.mongodb.com/manual/faq/storage/#how-do-i-reclaim-disk-space) of the MongoDB documentation to know how to make MongoDB efficiently reuse these empty disk spaces.

#### Memory metrics




<table>
<thead>
<tr class="header">
<th><strong>Metric Description</strong></th>
<th><strong>Name</strong></th>
<th><a href="/blog/monitoring-101-collecting-data/"><strong>Metric Type</strong></a></th>
<th><a href="/blog/collecting-mongodb-metrics-and-statistics"><strong>Availability</strong></a></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Virtual memory usage (MB)</td>
<td>mem.virtual</td>
<td>Resource: Utilization</td>
<td>serverStatus</td>
</tr>
<tr class="even">
<td>Amount of memory used by the database process (MB)</td>
<td>mem.resident</td>
<td>Resource: Utilization</td>
<td>serverStatus</td>
</tr>
<tr class="odd">
<td>Mapped memory: quantity of virtual memory used to map the database into memory (MB)</td>
<td>mem.mapped *</td>
<td>Resource: Utilization</td>
<td>serverStatus</td>
</tr>
<tr class="even">
<td>Non-mapped virtual memory: amount of virtual memory consumed by connections and not for mapping data files</td>
<td><strong>If journaling enabled:</strong> mem.virtual - mem.mappedWithJournal *<strong>If not:</strong> mem.virtual - mem.mapped *</td>
<td>Resource: Utilization</td>
<td>serverStatus</td>
</tr>
<tr class="odd">
<td>Number of times MongoDB had to request from disk (per second)</td>
<td>extra_info.page_faults</td>
<td>Other</td>
<td>serverStatus</td>
</tr>
</tbody>
</table>



\*Only for the MMAPv1 storage engine

The **resident memory** usage usually approaches the amount of physical RAM available to the MongoDB server.

**Memory-mapped** files are crucial for performance with the MMAPv1 storage engine since it allows MongoDB to manipulate data files as if they were in memory. A memory mapped file is a region of the virtual memory which has been assigned a direct byte-for-byte correlation with a portion of a data file (on-disk) of the database. Thus when MongoDB needs to access an on-disk file to address a query, it does it via the memory mapped file (virtual memory region corresponding to the disk file) using the [mmap()](https://en.wikipedia.org/wiki/Mmap) method, which is much faster than accessing the disk directly.

NOTE: mem.mapped gives you a good approximation of the total size of your database(s).

##### Metrics to notify on:


**Non-mapped virtual memory** corresponds to the virtual memory used for tasks other than mapping data files—memory consumed by connections for example. Make sure that your non-mapped virtual memory allocation remains relatively stable. If it is ever-increasing, look for opened connections that were not properly closed or a potential memory leak from the driver or the server.

With MMAPv1, if journaling is turned on, the amount of **virtual memory** is always at least two times larger than the memory mapped. In the unlikely event that it gets to be more than 3 times larger than the mapped memory, it means that the non-mapped virtual memory is getting too high (cf: paragraph above for troubleshooting).

**Page faults** indicate operations which required the MongoDB to fetch data from disk because it wasn’t available in active memory (“hard” page fault), or when the operation required in-memory page relocation (“soft” page fault). Requests which trigger page faults take more time to execute than requests that do not. Frequent page faults may indicate that your data set is too large for the allocated memory. However that’s not a big issue if the throughput remains healthy. Limited and occasional page faults do not necessarily indicate serious problems. In order to reduce the frequency of page faults, you can increase the size of your RAM or consider adding more shards to your deployments in order to better distribute incoming requests. Page faults can also be a sign of inefficient schema design, redundant or unnecessary indexes, or anything using available RAM unnecessarily.

{{< img src="mongodb-page-faults.png" alt="monitoring MongoDB page faults" popup="true" size="1x" >}}

##### Note about the working set’s size:


With the MMAPv1 storage engine, your working set—the data that is most often accessed—[needs to fit in RAM](https://docs.mongodb.com/manual/faq/diagnostics/#must-my-working-set-size-fit-ram) to maintain good performance. If it does not fit in RAM, you’ll see a lot of hard page faults and disk I/O.

#### Other host-level metrics


You’ll also want to monitor system metrics of machines running MongoDB in order to investigate performance issues.

**Disk space** is one of the most important host-level metrics to alert on. You should trigger a high priority alert if it is getting close to full (for example a warning if 80% full, and an alert at 90% full).

If **CPU utilization** is increasing too much, it can lead to bottlenecks and may indirectly indicate inefficient queries, perhaps due to poor indexing.

When **I/O utilization** is getting close to 100% for lengthy periods of time, it means you are hitting the limit of the physical disk’s capacity. If it’s constantly high, you should upgrade your disk or add more shards in order to avoid performance issues such as slow queries or slow replication.

**I/O wait** limits throughput so a high value indicates high throughput. In that case you should consider scaling up by adding more shards (see section about [scaling MongoDB](#scaling-mongodb-sharding-vs-replication)), or increasing your disk I/O capacity (after verifying optimal schema and index design). RAM saturation might also be a cause of low I/O per second, especially if your system is not write-heavy. It can be due to the size of your working set being larger than the available memory for example.

### Resource Saturation


{{< img src="mongodb-resource-saturation-metrics.png" alt="monitoring MongoDB resource saturation metrics" size="1x" >}}



<table>
<thead>
<tr class="header">
<th><strong>Metric Description</strong></th>
<th><strong>Name</strong></th>
<th><a href="/blog/monitoring-101-collecting-data/"><strong>Metric Type</strong></a></th>
<th><a href="/blog/collecting-mongodb-metrics-and-statistics"><strong>Availability</strong></a></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Number of read requests currently queued</td>
<td>globalLock.currentQueue.readers</td>
<td>Resource: Saturation</td>
<td>serverStatus</td>
</tr>
<tr class="even">
<td>Number of write requests currently queued</td>
<td>globalLock.currentQueue.writers</td>
<td>Resource: Saturation</td>
<td>serverStatus</td>
</tr>
<tr class="odd">
<td>Number of times documents had to be moved on-disk because they got larger than their respective allocated record space</td>
<td>metrics.record.moves *</td>
<td>Resource: Saturation</td>
<td>serverStatus</td>
</tr>
</tbody>
</table>



\*Only for the MMAPv1 storage engine

##### Metrics to notify on:


**Queued read and writes requests** are reported under “[globalLock](https://docs.mongodb.com/manual/reference/command/serverStatus/#server-status-global-lock)” even if they are not really related to global lock. If you see that the number of queued requests keeps growing during heavy read/write traffic, that means MongoDB is not addressing requests as fast as they are arriving. In order to avoid performance issues and make sure your database is able to keep up with the demand, you should increase your deployment capacity (see [section about scaling MongoDB](#scaling-mongodb-sharding-vs-replication)).

NOTE: Scaling up vertically by adding more capacity (CPU, memory, faster disks, more disks on each instance) is also an option, but this strategy can become cost-prohibitive, and the size of your instances might be limited by your IT department’s inventory, or by your cloud-infrastructure provider.

### Errors: asserts


{{< img src="mongodb-asserts-errors.png" alt="monitoring MongoDB asserts errors" size="1x" >}}

Asserts typically represent errors. MongoDB generates [a document](https://docs.mongodb.com/manual/reference/command/serverStatus/#asserts) reporting on the number of each type of assertions that have been raised: message, warning, regular, and user. Assertions don’t occur often but should be investigated when they do.



<table>
<thead>
<tr class="header">
<th><strong>Metric Description</strong></th>
<th><strong>Name</strong></th>
<th><a href="/blog/monitoring-101-collecting-data/"><strong>Metric Type</strong></a></th>
<th><a href="/blog/collecting-mongodb-metrics-and-statistics"><strong>Availability</strong></a></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Number of message assertions raised during the selected time period</td>
<td>asserts.msg</td>
<td>Resource: Error</td>
<td>serverStatus</td>
</tr>
<tr class="even">
<td>Number of warning assertions raised during the selected time period</td>
<td>asserts.warning</td>
<td>Resource: Error</td>
<td>serverStatus</td>
</tr>
<tr class="odd">
<td>Number of regular assertions raised during the selected time period</td>
<td>asserts.regular</td>
<td>Resource: Error</td>
<td>serverStatus</td>
</tr>
<tr class="even">
<td>Number of assertions corresponding to errors generated by users during the selected time period</td>
<td>asserts.user</td>
<td>Resource: Error</td>
<td>serverStatus</td>
</tr>
</tbody>
</table>



NOTE: These counters will rollover to zero if the MongoDB’s process is restarted or after 2^30 assertions.

The MongoDB log files will give you more details about assert exception returned, which will help you find possible causes.

##### Metrics to notify on:


**Message asserts** indicate internal server exceptions.

**Warning asserts** are not as serious as errors. They just indicate things that might be worth checking like too low [ulimit](https://docs.mongodb.com/manual/reference/ulimit/) or readahead.

**Regular asserts** are per-operation invariants (e.g. “unexpected failure while reading a BSON document”).

**User asserts** are triggered as the result of user operations or commands generating an error like a full disk space, a duplicate key exception, or write errors (e.g. insert not properly formatted, or no access right). These errors are returned to the client so most of them won’t be logged into the mongod logs. However you should investigate potential problems with your application or deployment.

Both regular and user asserts will result in the corresponding operation failing.

Scaling MongoDB: sharding vs replication
----------------------------------------


A replica set represents multiple servers running MongoDB, each one containing the exact same data. There is one primary node and the rest are secondary nodes. Replica sets provide fault-tolerance and high data availability. If the primary node becomes unavailable, one of the secondary nodes will be elected to take over as the new primary.

{{< img src="mongodb-replication-sharding.png" alt="monitoring MongoDB sharding vs replication" popup="true" size="1x" >}}

In order to increase your throughput capacity, you can scale horizontally by adding more shards to your cluster. Sharding splits data and distributes it among the shards (mongod instances) of a cluster according to a *[shard key](https://docs.mongodb.com/manual/core/sharding-shard-key/)* defined for your collections. Incoming requests will be addressed by the corresponding shard(s) containing the requested data. Thus it allows to support more **read and write** throughputs. You can also upgrade the hardware on the cluster.

NOTE: For rare very specific cases where reads on secondaries can be acceptable (reads querying all the data for example), you can also consider adding more secondaries to your replica set and using them to support more **read** requests. But this is definitely not a general scaling tactic. Replica set members main purpose is to ensure high data availability, not to support read-heavy throughputs. The MongoDB’s documentation [gives more details](https://docs.mongodb.com/manual/core/read-preference/#counter-indications) on why using more secondaries to provide extra read capacity shouldn’t be a scaling tactic most of the time.

Since write operations can only be directed to the primary node (they are then applied to secondaries), additional secondaries will not increase write-throughput capacity. If you need to support higher write throughput, you should use more shards instead.

{{< img src="mongodb-sharding.png" alt="monitoring MongoDB sharding" popup="true" size="1x" >}}

<em>Sharding in MongoDB

</em>


Adding more shards to a cluster increases read and write throughput capacities. In order to ensure high availability of all of your data even when a shard is down, each shard should be a replica set (especially [in production](https://docs.mongodb.com/manual/core/sharded-cluster-architectures-production/)).

Recap
-----


In this post we’ve explored the metrics you should monitor to keep tabs on your MongoDB cluster. If you are just getting started with MongoDB, monitoring the metrics in the list below will provide visibility into your database’s health, performance, resource usage, and may help identify areas where tuning could provide significant benefits:



-   [Throughput metrics](#throughput-metrics)
-   [Database performance](#database-performance)
-   [Resource utilization](#resource-utilization)
-   [Resource saturation](#resource-saturation)
-   [Errors](#errors-asserts) (asserts)



{{< img src="mongodb-metrics-categories.png" alt="monitoring MongoDB metrics categories" popup="true" size="1x" >}}

Closely tracking throughput metrics should give you a great overview of your database activity. Database performance, errors, resource utilization and resource saturation metrics will help you investigate issues and understand what to do to maintain good performance.

Eventually you will recognize additional, more specialized metrics that are particularly relevant to your own usage of MongoDB.

[Part 2](/blog/collecting-mongodb-metrics-and-statistics) will give you a comprehensive guide to collecting any of the metrics described in this article, or any other metric exposed by MongoDB.

Acknowledgments
---------------


Many thanks to the Engineering Team at [MongoDB](https://www.mongodb.com/) for reviewing this publication and suggesting improvements.

 

*Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/mongodb/monitoring-mongodb-performance-metrics-mmap.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues).*

