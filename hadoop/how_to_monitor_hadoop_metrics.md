_This post is part 2 of a 4-part series on monitoring Hadoop health and performance. [Part 1] gives a general overview of Hadoop's architecture and subcomponents, this post covers Hadoop's key metrics, [Part 3] details how to monitor Hadoop performance natively, and [Part 4] explains how to monitor a Hadoop deployment with Datadog._

If you've already [read our guide][Part 1] to Hadoop architecture, you know about the components that make up a typical Hadoop cluster. In this post, we'll dive deep into each of the technologies introduced in that guide and explore the key metrics exposed by Hadoop that you should keep your eye on.

## Service-oriented monitoring

From an operations perspective, Hadoop clusters are incredibly resilient in the face of system failures. Hadoop was designed with failure in mind and can tolerate entire racks going down.

Monitoring Hadoop requires a different mindset than monitoring something like [RabbitMQ]—DataNodes and NodeManagers should be treated [like cattle][pets-v-cattle]. As with Docker containers, you [generally don't care][host-centric monitoring] if a single worker node fails, although failure of a master node such as one of your NameNodes will require fairly rapid remediation. Generally speaking, individual host-level indicators are less important than service-level metrics when it comes to Hadoop.

## Key Hadoop performance metrics to monitor
When working properly, a Hadoop cluster can handle a truly massive amount of data—there are plenty of production clusters managing petabytes of data each. Monitoring each of Hadoop's sub-components is essential to keep jobs running and the cluster humming.

Hadoop metrics can be broken down into four broad categories:

- [HDFS metrics](#toc-hdfs-metrics2)
- [MapReduce counters](#toc-mapreduce-counters4)
- [YARN metrics](#toc-yarn-metrics5)
- [ZooKeeper metrics](#toc-zookeeper-metrics9)

[![Hadoop metrics breakdown diagram][hadoop-metrics-tree]][hadoop-metrics-tree]

To learn more about collecting Hadoop and ZooKeeper metrics, take a look at [part three][Part 3] of this series. 

This article references metric terminology introduced in our [Monitoring 101 series][monitoring-101], which provides a framework for metric collection and alerting.

<div id="HDFS-metrics"></div>

## HDFS metrics
HDFS metrics can be further decomposed into two categories:  

- [NameNode metrics](#NameNode-metrics)
- [DataNode metrics](#DataNode-metrics)

<!-- [![HDFS metrics breakdown][hdfs-metrics-tree]][hdfs-metrics-tree] -->

<canvas id="canvas" width="700" height="300" style="background-color:#FFFFFF"></canvas>
 
**NameNode and DataNodes**  

[DataNodes][dn-part1] communicate with their [NameNode][nn-part1] (and vice versa) via a periodic heartbeat (by default every three seconds, set by `dfs.heartbeat.interval`). The heartbeat contains (amongst other things) health information about the DataNode. It is through this mechanism that the NameNode is able to know the state of all the DataNodes in the cluster.

<div id="NameNode-metrics"></div>

Failure of the [NameNode][nn-part1] without any replica standing by will cause data stored in the cluster to become unavailable. Therefore monitoring the primary NameNode and its Secondary/Standby NameNode is critical to ensure high cluster availability. In addition to reporting metrics about themselves, NameNodes can also report metrics about all DataNodes, providing a good birds-eye view of the rest of your HDFS deploy.

NameNode metrics can be divided into two groups:

- NameNode-emitted metrics  
- [NameNode JVM metrics](#NameNode-JVM)

<!-- instead of words, zoom in diagram -->

### NameNode-emitted metrics
  
|Name|Description|[Metric Type][monitoring-101]|
|:--:|:--:|:--:|:--:|
|CapacityRemaining|Available capacity|Resource: Utilization|
|CorruptBlocks/MissingBlocks| Number of corrupt/missing blocks|Resource: Error/Resource: Availability|
|VolumeFailuresTotal|Number of failed volumes| Resource: Error|
|NumLiveDataNodes/NumDeadDataNodes|Count of alive DataNodes/Count of dead DataNodes| Resource: Availability|
|FilesTotal|Total count of files tracked by the NameNode| Resource: Utilization|
|TotalLoad|Measure of file access across all DataNodes|Resource: Utilization|
|BlockCapacity/BlocksTotal|Maximum number of blocks allocable/Count of blocks tracked by NameNode| Resource: Utilization
|UnderReplicatedBlocks| Count of under-replicated blocks| Resource: Availability|
|NumStaleDataNodes|Count of stale DataNodes| Resource: Availability|

<div id="Capacity"> </div>

![HDFS Capacity remaining graph][hdfs-capacity-remaining]

**Metric to alert on: CapacityRemaining** 
CapacityRemaining represents the total available capacity remaining across the entire HDFS cluster. It is an understatement to say that running out of disk space in HDFS will cause BadThingsToHappen&trade;. DataNodes that are out of space are likely to fail on boot, and of course, running DataNodes will not be able to be written to. In addition, any running jobs which write out temporary data may fail due to lack of capacity. It is good practice to ensure that disk use never exceeds 80 percent capacity.

Thankfully, HDFS [makes it easy][hdfs-add-datanode] to spin up new DataNodes to add capacity (or you can add extra disks to existing DataNodes, of course).

**Metric to alert on: MissingBlocks**  
Corrupt or missing blocks can point to an unhealthy cluster. Typically, upon receiving a read request a DataNode will locate the requested block and serve it back to the client, along with a checksum for the data (which was calculated and stored on the DataNode when the block was written). If the checksum for the received data doesn’t match the stored checksum, the client reports the corruption to the NameNode and reads the data from one of the other replicas. The NameNode, meanwhile, schedules a rereplication of the block from one of the healthy copies, and then tells the original DataNode to delete its corrupted copy. So, although you may see corrupt blocks reported on your cluster from time to time, that doesn’t necessarily mean that you have lost any data. 

A _missing_ block is far worse than a corrupt block, because a missing block cannot be recovered by [copying a replica][hadoop-recovery]. A missing block represents a block for which no known copy exists in the cluster. That's not to say that the block no longer exists—if a series of DataNodes were taken offline for maintenance, missing blocks could be reported until they are brought back up.

You may not care if you have a corrupt block or two in the entire cluster, but if blocks start going missing without any scheduled maintenance it is cause for concern.

**Metric to alert on: VolumeFailuresTotal**  
In [old versions of Hadoop][datanode-fail], failure of a single disk would cause an entire DataNode to be taken offline. Thankfully, that is no longer the case—HDFS now allows for disks to fail in place, without affecting DataNode operations, until a threshold value is reached. (This is set on each DataNode via the `dfs.datanode.failed.volumes.tolerated` property; it defaults to 0, meaning that any volume failure will shut down the DataNode; on a production cluster where DataNodes typically have 6, 8, or 12 disks, setting this parameter to 1 or 2 is typically the best practice.)

Though a failed volume will not bring your cluster to grinding halt, you most likely want to know when hardware failures occur, if only so that you can replace the failed hardware. Since HDFS was designed with hardware failure in mind, with a default replication of three, a failed volume should never signal data loss.

**Metric to alert on: NumDeadDataNodes**  
NumLiveDataNodes and NumDeadDataNodes together track the number of DataNodes in the cluster, by state. Ideally, your number of live DataNodes will be equal to the number of DataNodes you've provisioned for the cluster. If this number unexpectedly drops, it may warrant investigation.

NumDeadDataNodes, on the other hand, should be alerted on. When the NameNode does not hear from a DataNode for 30 seconds, that DataNode is marked as "stale." Should the DataNode fail to communicate with the NameNode for 10 minutes following the transition to the "stale" state, the DataNode is marked "dead." The death of a DataNode causes a flurry of network activity, as the NameNode initiates replication of blocks lost on the dead nodes.

Though the loss of a single DataNode may not impact performance much, losing multiple DataNodes will start to be very taxing on cluster resources, and could result in data loss.

**FilesTotal** is a running count of the number of files being tracked by the NameNode. Because the NameNode stores all metadata in memory, the greater the number of files (or blocks, or directories) tracked, [the more memory][small-files-problem] required by NameNode. The rule of thumb for NameNode memory requirements is that each object (file, directory, block) tracked by the NameNode consumes roughly [150 bytes][namenode-limit] of memory. If each file is mapped to one block (files often span multiple blocks), that is approximately 300 bytes per file. That doesn't sound like much until you factor in the replication of data: the default replication factor is 3 (so 900 bytes per file), _and_ each replica adds an additional 16 bytes, for a total of ~1 KB of metadata per file. That still may not sound like much, but as your cluster expands to include millions of files, you should keep this number in mind and plan to add additional memory to your NameNode.

![TotalLoad diagram][hdfs-totalload]

**TotalLoad** is the current number of concurrent file accesses (read/write) across all DataNodes. This metric is not usually indicative of a problem, though it can illuminate issues related to job execution. Because worker nodes running the DataNode daemon also perform MapReduce tasks, extended periods of high I/O (indicated by high TotalLoad) generally translate to degraded job execution performance. Tracking TotalLoad over time can help get to the bottom of job performance issues.

**BlockCapacity/BlocksTotal**: Like FilesTotal, keeping an eye on the total number of blocks across the cluster is essential to continued operation. Block capacity and file capacity are very closely related but not the same (files can span multiple blocks); monitoring both block and file capacity is necessary to ensure uninterrupted operation. If your cluster is approaching the limits of block capacity, you can easily add more by bringing up a new DataNode and adding it to the pool, or adding more disks to existing nodes. Once added, you can use the [Hadoop balancer][balancer] to balance the distribution of blocks across DataNodes.

**UnderReplicatedBlocks** are the number of blocks with insufficient replication. Hadoop's replication factor is configurable on a [per-client][global-replication] or [per-file][file-replication] basis. The default replication factor is three, meaning that each block will be stored on three DataNodes. If you see a large, sudden spike in the number of under-replicated blocks, it is likely that a DataNode has died—this can be verified by correlating under-replicated block metrics with the status of DataNodes (via NumLiveDataNodes and related metrics). 


[![Live, dead, and decommissioned DataNodes image][live-dead-decom]][live-dead-decom]

**NumStaleDataNodes**: Every three seconds (by default), DataNodes send a heartbeat message to the NameNode. This heartbeat acts as a health-check mechanism but can also be used by the NameNode to delegate new work. As explained above, DataNodes that do not send a heartbeat within 30 seconds are marked as "stale." A DataNode might not emit a heartbeat for a number of reasons—network issues or high load are among the more common causes. Unless you've disabled reads or writes to stale DataNodes, you should definitely keep an eye on this metric. A DataNode that did not emit a heartbeat due to high system load (or a slow network) will likely cause any reads or writes to that DataNode to be delayed as well. However, in practice, a stale DataNode is likely dead.

Even if reading and writing on stale DataNodes is disabled, you should still monitor for sudden increases in the number of stale DataNodes, because in a short time stale nodes can easily become dead nodes. And stale DataNodes will be written to regardless of your settings if the ratio of stale DataNodes to total DataNodes exceeds the value of `dfs.namenode.write.stale.datanode.ratio`.

<div id="NameNode-JVM"></div>

### NameNode JVM metrics
Because the NameNode runs in the Java Virtual Machine (JVM), it relies on Java garbage collection processes to free up memory. The more activity in your HDFS cluster, the more often the garbage collection will run.

Anyone familiar with Java applications knows that garbage collection can come with a high performance cost. See [the Oracle documentation][jvm-gc] for a good primer on Java garbage collection. 

If you are seeing excessive pauses during garbage collection, you can consider upgrading your JDK version or garbage collector. Additionally, you can tune your Java runtime to minimize garbage collection. 

Because a NameNode is typically hosted on a machine with ample computational resources, using the CMS (ConcurrentMarkSweep) garbage collector is recommended, _especially_ because bottlenecks on the NameNode will result in degraded performance cluster-wide. From the Oracle documentation:
> The CMS collector should be used for applications that require low pause times and can share resources with the garbage collector. Examples include desktop UI application that respond to events, a webserver responding to a request or a database responding to queries.

ConcurrentMarkSweep collections free up unused memory in the old generation of the heap. CMS is a low-pause garbage collection, meaning that although it does temporarily stop application threads, it does so only intermittently. 

For more information on optimizing NameNode garbage collection, see this [excellent guide][hadoop-jvm-tuning] from Hortonworks.


|Name|Description|[Metric Type][monitoring-101]|
|:--:|:--:|:--:|:--:|
|ConcurrentMarkSweep count|Number of old-generation collections|Other |
|ConcurrentMarkSweep time| Elapsed time of old-generation collections, in milliseconds| Other| 

[![NameNode CMS][nn-cms-graph]][nn-cms-graph]

If CMS is taking more than a few seconds to complete, or is occurring with increased frequency, your NameNode may not have enough memory allocated to the JVM to function efficiently.

<div id="DataNode-metrics"></div>

### DataNode metrics

DataNode metrics are host-level metrics specific to a particular DataNode.

|Name|Description|[Metric Type][monitoring-101]|
|:--:|:--:|:--:|:--:|
|Remaining| Remaining disk space | Resource: Utilization|
|NumFailedVolumes| Number of failed storage volumes | Resource: Error|

[![Disk remaining on DataNodes][dn-disk-graph]][dn-disk-graph]

**Remaining**: As mentioned in the [section on NameNode metrics](#Capacity), running out of disk space can cause a number of problems in a cluster. If left unrectified, a single DataNode running out of space could quickly cascade into failures across the entire cluster as data is written to an increasingly-shrinking pool of available DataNodes. Tracking this metric over time is essential to maintain a healthy cluster; you may want to alert on this metric when the remaining space falls dangerously low (less than 10 percent).

**NumFailedVolumes**: By default, a single volume failing on a DataNode will cause the entire node to go offline. Depending on your environment, that may not be desired, especially since most DataNodes operate with multiple disks. If you haven't set `dfs.datanode.failed.volumes.tolerated` in your HDFS configuration, you should definitely track this metric. Remember, when a DataNode is taken offline, the NameNode must copy any under-replicated blocks that were lost on that node, causing a burst in network traffic and potential performance degradation. To prevent a slew of network activity from the failure of a single disk (if your use case permits), you should set the tolerated level of volume failure in your config like so:

```
<property>
    <name>dfs.datanode.failed.volumes.tolerated</name>
    <value>N</value>
</property>
```
where N is the number of failures a DataNode should tolerate before shutting down. 
_Don't forget to restart your DataNode process following a configuration change._

The downside to enabling this feature is that, with fewer disks to write to, a DataNode's performance may suffer. Setting a reasonable value for tolerated failures will vary depending on your use case.

<div id="MapReduce-counters"></div>

## MapReduce counters

The MapReduce framework exposes a number of counters to track statistics on MapReduce job execution. Counters are an invaluable mechanism that let you see what is actually happening during a MapReduce job run. They provide a count of the number of times an event occurred. MapReduce counters can be broken down into four categories:

- [job counters](#Job-counters)
- [task counters](#Task-counters)
- [custom counters](#Custom-counters)
- file system counters

[![MapReduce counters breakdown][mapreduce-metrics-tree]][mapreduce-metrics-tree]

MapReduce application developers may want to track the following counters to to find bottlenecks and potential optimizations in their applications.

<div id="Job-counters"></div>

### Job counters
Group name:`org.apache.hadoop.mapreduce.JobCounter`  

|Counter Name|Description|[Metric Type][monitoring-101]|
|:---:|:---:|:---:|
|MILLIS\_MAPS/MILLIS\_REDUCES| Processing time for maps/reduces|Work: Performance|
|NUM\_FAILED\_MAPS/NUM\_FAILED\_REDUCES| Number of failed maps/reduces|Work: Error|
|RACK\_LOCAL\_MAPS/DATA\_LOCAL\_MAPS/OTHER\_LOCAL\_MAPS| Counters tracking where map tasks were executed| Resource: Other|

<div id="MILLIS-MAPS"></div>

**MILLIS\_MAPS/MILLIS\_REDUCES**: These metrics track the wall time spent across all of your map and reduce tasks. Their full utility is realized when tracked alongside the task counter GC\_TIME\_MILLIS (see [below](#toc-task-counters8)); when taken altogether, it is possible to determine the percentage of time spent performing garbage collection.

Using all three counters, we can calculate the percentage of time spent in garbage collection with the following formula: GC\_TIME\_PERCENTAGE = GC\_TIME\_MILLIS / (MILLIS\_MAPS + MILLIS\_REDUCES)

Jobs where garbage collection is consuming a significant percentage of computation time (e.g. more than 20 percent) may benefit from increasing the amount of heap available to them.

**NUM\_FAILED\_MAPS/NUM\_FAILED\_REDUCES**: This pair of metrics tracks the number of failed map/reduce tasks for a job. Tasks can fail for many reasons—abrupt exit by the JVM, runtime errors, and hanging tasks are among the most common. Failed tasks are tolerated, up to the value set by the `mapreduce.map.maxattempts` and `mapreduce.reduce.maxattempts` properties (set to four, by default). If a task fails `maxattempts` times, it is marked as failed. A job will fail as a whole if more than `mapreduce.map.failures.maxpercent` percent of map tasks in the job fail or more than `mapreduce.reduce.failures.maxpercent` percent of the reduce tasks fail.

Because failures are expected, you should not alert on this metric, though if you are seeing the same task fail on several DataNodes, it may be worth diving into the job logs or even the application code for bugs. If many tasks fail on a particular DataNode, the issue could be hardware-related.

**DATA\_LOCAL\_MAPS/RACK\_LOCAL\_MAPS/OTHER\_LOCAL\_MAPS**: These counters track the number of map tasks that were performed, aggregated by location. Data can be located either: on the node executing the map task, on a node in the same rack as the node performing the map task, or on a node located on a different rack somewhere else in the cluster. Recall from [part 1 of this series][Part-1-HDFS] that one of Hadoop's greatest strengths lies in its preference for moving computation as close to the data as possible. The benefits from operating on local data include reduced network overhead and faster execution. These benefits are lost when the computation must be performed on a node that is not physically close to the data being processed.

Because sending data over the network takes time, correlating poor job performance with these counters can help determine _why_ performance suffered. If many maps had to be executed on nodes where the data was not locally hosted, it would be reasonable to expect degraded performance.

<div id="Task-counters"></div>

### Task counters
Task counters track the results of task operations in aggregate. Each counter below represents the total across all tasks associated with a particular job.

Group name: `org.apache.hadoop.mapreduce.JobCounter`  

|Counter Name|Description|[Metric Type][monitoring-101]|
|:---:|:---:|:---:|
|REDUCE\_INPUT\_RECORDS| Number of input records for reduce tasks|Other| <!-- the closest thing would be like a queue --> 
|SPILLED\_RECORDS|Number of records spilled to disk|Resource: Saturation|
|GC\_TIME\_MILLIS|Processing time spent in garbage collection|Other|

**REDUCE\_INPUT\_RECORDS**: Keeping an eye on the number of input records for each reduce task in a job is one of the best ways to identify performance issues related to a _skewed dataset_. Skewed data is characterized by a disproportionate distribution of input records across all reducers for a job. To give a concrete example, consider the canonical wordcount run on a text composed of 40,000 "the"s and one "a". If this text were run through two reducers, and each got the values associated with one of the two keys, the reducer working on the larger dataset (the set of "the" keys) would take much longer to complete than the reducer with a much smaller dataset.

Skewed datasets can make jobs take much longer to complete than expected. Unfortunately, cluster administrators can't simply add more reducers to speed up execution—in cases like this, the MapReduce job would probably benefit from the addition of a [combine step][combiner].

**SPILLED\_RECORDS**: Map output data is stored in memory, but when the buffer fills up data is dumped to disk. A separate thread is spawned to merge all of the spilled data into a single larger sorted file for reducers. Spills to disk should be minimized, as more than one spill will result in an increase in disk activity as the merging thread has to read and write data to disk. Tracking this metric can help determine if configuration changes need to be made (like increasing the memory available for map tasks) or if additional processing (compression) of the input data is necessary.
 
**GC\_TIME\_MILLIS**: Useful for determining the percentage of time tasks spent performing garbage collection. See the section on [MILLIS\_MAPS/MILLIS\_REDUCES](#MILLIS-MAPS) for more information.

<div id="Custom-counters"></div>

### Custom counters
MapReduce allows users to implement [custom counters][counter-api] that are specific to their application. Custom counters can be used to track more fine-grained counts, such as [counting the number of malformed or missing records][custom-counter-tut].

Keep in mind, however, that since all counters reside in the JobTracker JVM's memory, there is a practical limit to the number of counters you should use, limited by the amount of physical memory available.  (Hadoop has a configuration value, `mapreduce.job.counters.max`, which limits the number of custom counters that can be created; by default this is 120.)

<div id="YARN-metrics"></div>

## YARN metrics
YARN metrics can be grouped into three distinct categories:

- [Cluster metrics](#toc-cluster-metrics6)
- [Application metrics](#toc-application-metrics7)
- [NodeManager metrics](#toc-nodemanager-metrics8)

[![YARN metrics breakdown][yarn-metrics-tree]][yarn-metrics-tree]

<div id="YARN-Cluster"></div>

### Cluster metrics
Cluster metrics provide a high-level view of YARN application execution. The metrics listed here are aggregated cluster-wide.  

|Name|Description|[Metric Type][monitoring-101]|
|:--:|:--:|:--:|
|unhealthyNodes|Number of unhealthy nodes|Resource: Error|
|activeNodes|Number of currently active nodes|Resource: Availability|
|lostNodes|Number of lost nodes|Resource: Error|
|appsFailed|Number of failed applications|Work: Error|
|totalMB/allocatedMB|Total amount of memory/amount of memory allocated|Resource: Utilization|

**Metric to alert on: unhealthyNodes**
YARN considers any node with disk utilization exceeding the value specified under the property `yarn.nodemanager.disk-health-checker.max-disk-utilization-per-disk-percentage` (in yarn-site.xml) to be unhealthy. Ample disk space is critical to ensure uninterrupted operation of a Hadoop cluster, and large numbers of unhealthyNodes (the number to alert on depends on the size of your cluster) should be quickly investigated and resolved. Once a node is marked unhealthy, other nodes have to fill the void, which can cause a cascade of alerts as node after node nears full disk utilization.

It is worth mentioning that you can add your own health checks to YARN with a [simple configuration change][external-health-script]. But be warned—if the script should fail for any reason, including wrong permissions, incorrect path, and so on—it will cause the node to be marked as unhealthy.

**activeNodes/lostNodes**: The activeNodes metric tracks the current count of active, or normally operating, nodes. This metric should remain static in the absence of anticipated maintenance. If a NodeManager fails to maintain contact with the ResourceManager, it will eventually be marked as "lost" and its resources will become unavailable for allocation. The timeout threshold is configurable via the `yarn.resourcemanager.nm.liveness-monitor.expire-interval-ms` property in yarn-site.xml, with a default value of 10 minutes (600000 ms). Nodes can lose contact with the ResourceManager for a number of reasons, including network issues, hardware failure, or a hung process. It is good to be aware of lost nodes, so you can take action if the node never returns.

**appsFailed**: Assuming you are running MapReduce on YARN, if the percentage of failed map or reduce tasks exceeds a specific threshold (configured with `mapreduce.map.failures.maxpercent` and `mapreduce.reduce.failures.maxpercent`, respectively) the application as a whole will fail. It is important to note that YARN cannot distinguish between a failed NodeManager and a hanging task—in either case, the NodeManager will fail to report to the ResourceManager within the heartbeat timeout period and the task will be rerun. After four unsuccessful attempts to run the task (configured with `mapreduce.map.maxattempts` and `mapreduce.reduce.maxattempts`, respectively), it will be marked as failed.

In the case of ResourceManager failure, application state is largely unaffected, though no new work will be able to be submitted and currently running jobs will start to fail. Because the ApplicationMasters (on each NodeManager) store the application state (including the list of run/failed/killed tasks), once a new ResourceManager is brought online (and assuming the old saved state is recoverable), NodeManagers can pick up where they left off.

**totalMB/allocatedMB**: When taken together, the totalMB and allocatedMB metrics give a high-level view of your cluster's memory usage. Memory is currency in Hadoop, and if you are nearing the ceiling of your memory usage you have a couple of options. To increase the memory available to your cluster, you can add new NodeManager nodes, tweak the amount of memory reserved for YARN applications (set by the `yarn.nodemanager.resource.memory-mb` in `yarn-site.xml`, or change the minimum amount of RAM allocated to containers (set by the `yarn.scheduler.minimum-allocation-mb` property in `yarn-site.xml`). 

Keep in mind that YARN may over-commit resources, which can occasionally translate to reported values of allocatedMB which are higher than totalMB.

<div id="YARN-Application"></div>

### Application metrics
Application metrics provide detailed information on the execution of individual YARN applications.

|Name|Description|[Metric Type][monitoring-101]|
|:--:|:--:|:--:|
|progress|Application execution progress meter|Work: Performance|

**progress**: Progress gives you a real-time window into the execution of a YARN application. Its reported value will always be in the range of zero to one (inclusive), with a value of one indicating completed execution. Because application execution can often times be opaque when running hundreds of applications on thousands of nodes, tracking progress alongside other metrics can better help you to determine the cause of any performance degradation. Applications that go extended periods without making progress should be investigated. 

<div id="YARN-Node"></div>

### NodeManager metrics
NodeManager metrics provide resource information at the individual node level. 

|Name|Description|[Metric Type][monitoring-101]|
|:--:|:--:|:--:|
|containersFailed| Number of containers that failed to launch | Resource: Error|

**containersFailed** tracks the number of containers that failed to launch on that particular NodeManager. [Recall from the first article][resource-containers] in the series that NodeManager containers are _not_ Docker containers.
[Configuration issues aside][container-launch-fail], the most common cause of container launch failure is hardware-related. If the NodeManager's disk is full, [any container it launches will fail][container-fail-on-disk]. Similarly, if the NodeManager's [heap is set too low][container-heap], containers won't launch. You don't need to be alerted for every container that failed to launch, but if a single node has many failed containers, it may be time to investigate.

<div id="ZooKeeper-metrics"></div>

## ZooKeeper metrics
ZooKeeper plays an important role in a Hadoop deployment. It is responsible for ensuring the availability of the [HDFS NameNode][hdfs-zookeeper] and YARN's ResourceManager. If your cluster is operating in high-availability mode, you should be sure to monitor ZooKeeper alongside the rest of your Hadoop components to avoid service interruptions.

ZooKeeper exposes metrics via MBeans as well as through a command line interface, using the so-called [4-letter words][part3-4-letters].  For more details on collecting ZooKeeper metrics, be sure to check out [part three][Part 3] of this series.

|Name|Description|[Metric Type][monitoring-101]|
|:--:|:--:|:--:|
|`zk_followers`|Number of active followers| Resource: Availability|
|`zk_avg_latency`|Amount of time it takes to respond to a client request (in ms)| Work: Performance|
|`zk_num_alive_connections`| Number of clients connected to ZooKeeper | Resource: Availability|

**Metric to alert on: zk\_followers (leader only)**
The number of followers should equal the total size of your ZooKeeper ensemble, minus 1 (the leader is not included in the follower count). If the ensemble fails to maintain quorum, all automatic failover features are suspended. Changes to this value should be alerted on, as the size of your ensemble should only change due to user intervention (e.g., an administrator decommissioned or commissioned a node).

**zk\_avg\_latency**: The average request latency is the average time it takes (in milliseconds) for ZooKeeper to respond to a request. ZooKeeper will not respond to a request until it has written the transaction to its transaction log. Any latency spikes could delay the transition between servers in the event of a ResourceManager or NameNode failure. Of course, such events are rare, but by tracking the average latency over time you can better correlate errors that may have been caused by stale data.

[![ZooKeeper average request latency][avg-req-latency-zk]][avg-req-latency-zk]

**zk\_num\_alive\_connections**: ZooKeeper reports the number of connected clients via this metric. This represents all connections, including connections from non-ZooKeeper nodes. In most environments, this number should remain fairly static—generally, your number of NameNodes, ResourceManagers, and their respective standbys should remain relatively stable. You should be aware of unanticipated drops in this value; since Hadoop uses ZooKeeper to provide high availability, a loss of connection to ZooKeeper could make the cluster less resilient to node loss.

## Go forth, and collect!
In this post we’ve explored many of the key metrics you should monitor to keep tabs on the health and performance of your Hadoop cluster. 

The metrics covered in this post pertain to the core Hadoop components and their typical use. Given Hadoop's vast ecosystem, over time you will likely identify additional metrics that are particularly relevant to your specific Hadoop infrastructure, and its users. 

[Read on][Part 3] for a comprehensive guide to collecting all of the metrics described in this article, and any other metric exposed by Hadoop.

## Acknowledgments 

Special thanks to [Ian Wrigley][ian-twit], Director of Education Services at [Confluent][confluent], for graciously sharing both his Hadoop expertise and monitoring strategies for this article.

[ian-twit]: https://twitter.com/iwrigley
[confluent]: http://www.confluent.io/


_Source Markdown for this post is available [on GitHub][markdown]. Questions, corrections, additions, etc.? Please [let us know][issues]._ 

[]: Links

[]: Preamble

[host-centric monitoring]: https://www.datadoghq.com/blog/the-docker-monitoring-problem/#toc-host-centric-monitoring14
[monitoring-101]: https://www.datadoghq.com/blog/monitoring-101-collecting-data/
[pets-v-cattle]: http://cloudscaling.com/blog/cloud-computing/pets-vs-cattle-the-elastic-cloud-story/
[RabbitMQ]: https://www.datadoghq.com/blog/openstack-monitoring-nova/#rabbitmq-metrics
[zookeeper-ha]: REPLACE_LINK_TO_ZOOKEEPER_IN_PART0

[]: HDFS

[balancer]: https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HDFSCommands.html#balancer
[datanode-fail]: https://issues.apache.org/jira/browse/HDFS-2137
[decommission-datanode]: https://docs.hortonworks.com/HDPDocuments/HDP2/HDP-2.4.2/bk_Sys_Admin_Guides/content/ref-a179736c-eb7c-4dda-b3b4-6f3a778bd8c8.1.html
[file-replication]: https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-common/FileSystemShell.html#setrep
[global-replication]: https://hadoop.apache.org/docs/r2.4.1/hadoop-project-dist/hadoop-hdfs/hdfs-default.xml#dfs.replication
[hadoop-jvm-tuning]: https://community.hortonworks.com/articles/14170/namenode-garbage-collection-configuration-best-pra.html
[hadoop-recovery]: https://twiki.opensciencegrid.org/bin/view/Storage/HadoopRecovery
[hdfs-add-datanode]: https://wiki.apache.org/hadoop/FAQ#I_have_a_new_node_I_want_to_add_to_a_running_Hadoop_cluster.3B_how_do_I_start_services_on_just_one_node.3F
[namenode-limit]: https://www.mail-archive.com/core-user@hadoop.apache.org/msg02835.html
[small-files-problem]: http://blog.cloudera.com/blog/2009/02/the-small-files-problem/
[jvm-gc]: http://www.oracle.com/webfolder/technetwork/tutorials/obe/java/gc01/index.html

[]: MapReduce

[combiner]: http://www.tutorialspoint.com/map_reduce/map_reduce_combiners.htm
[counter-api]: https://hadoop.apache.org/docs/r2.7.2/api/org/apache/hadoop/mapred/Counters.html
[custom-counter-tut]: http://www.ashishpaliwal.com/blog/2012/05/hadoop-recipe-using-custom-java-counters/

[]: YARN

[container-launch-fail]: https://stackoverflow.com/questions/22579943/yarn-mapreduce-job-issue-am-container-launch-error-in-hadoop-2-3-0
[container-fail-on-disk]: https://issues.apache.org/jira/browse/YARN-257
[container-heap]: https://stackoverflow.com/questions/23374693/hadoop-yarn-failed-to-launch-container
[external-health-script]: https://hadoop.apache.org/docs/current/hadoop-yarn/hadoop-yarn-site/NodeManager.html#External_Health_Script


[]: ZooKeeper

[avg-req-latency-zk]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-07-hadoop/graphs/zk-lat.png

[hdfs-zookeeper]: https://www.datadoghq.com/blog/hadoop-architecture-overview/#toc-hdfs-and-zookeeper16
[yarn-zookeeper]: https://www.datadoghq.com/blog/hadoop-architecture-overview/#toc-hdfs-and-zookeeper16

[]: Images

[hdfs-capacity-remaining]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-07-hadoop/graphs/hdfs-disk-usage-2.png
[hdfs-totalload]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-07-hadoop/graphs/hdfs-totalload.png
[dn-disk-graph]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-07-hadoop/graphs/dn-disk0.png
[live-dead-decom]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-07-hadoop/graphs/live-dead-decom.png
[nn-cms-graph]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-07-hadoop/graphs/nn-cms-1.png

[hadoop-metrics-tree]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-07-hadoop/metrics-diagrams/hadoop_diagram10-5.png
[hdfs-metrics-tree]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-07-hadoop/metrics-diagrams/hadoop_diagram11-1.png
[mapreduce-metrics-tree]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-07-hadoop/metrics-diagrams/hadoop_diagram12-2.png
[yarn-metrics-tree]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-07-hadoop/metrics-diagrams/hadoop_diagram13-3.png


[Part 1]: https://www.datadoghq.com/blog/hadoop-architecture-overview/
[Part 2]: https://www.datadoghq.com/blog/monitor-hadoop-metrics/
[Part 3]: https://www.datadoghq.com/blog/collecting-hadoop-metrics/ 
[Part 4]: https://www.datadoghq.com/blog/monitor-hadoop-metrics-datadog/
[Part-1-HDFS]: https://www.datadoghq.com/blog/hadoop-architecture-overview/#HDFS-architecture
[resource-containers]: https://www.datadoghq.com/blog/hadoop-architecture-overview/#Glossary
[part3-4-letters]: https://www.datadoghq.com/blog/collecting-hadoop-metrics/#4-letter-words

[dn-part1]: https://www.datadoghq.com/blog/hadoop-architecture-overview/#HDFS-architecture
[nn-part1]: https://www.datadoghq.com/blog/hadoop-architecture-overview/#NameNode

[markdown]: https://github.com/DataDog/the-monitor/blob/master/hadoop/how_to_monitor_hadoop_metrics.md
[issues]: https://github.com/DataDog/the-monitor/issues