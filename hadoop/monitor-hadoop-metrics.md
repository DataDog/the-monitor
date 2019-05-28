# How to monitor Hadoop metrics


*This post is part 2 of a 4-part series on monitoring Hadoop health and performance. [Part 1](/blog/hadoop-architecture-overview/) gives a general overview of Hadoop's architecture and subcomponents, this post covers Hadoop's key metrics, [Part 3](/blog/collecting-hadoop-metrics/) details how to monitor Hadoop performance natively, and [Part 4](/blog/monitor-hadoop-metrics-datadog/) explains how to monitor a Hadoop deployment with Datadog.*

If you've already [read our guide](/blog/hadoop-architecture-overview/) to Hadoop architecture, you know about the components that make up a typical Hadoop cluster. In this post, we'll dive deep into each of the technologies introduced in that guide and explore the key metrics exposed by Hadoop that you should keep your eye on.

Service-oriented monitoring


From an operations perspective, Hadoop clusters are incredibly resilient in the face of system failures. Hadoop was designed with failure in mind and can tolerate entire racks going down.

Monitoring Hadoop requires a different mindset than monitoring something like [RabbitMQ](/blog/openstack-monitoring-nova/#rabbitmq-metrics)—DataNodes and NodeManagers should be treated [like cattle](http://cloudscaling.com/blog/cloud-computing/pets-vs-cattle-the-elastic-cloud-story/). As with Docker containers, you [generally don't care](/blog/the-docker-monitoring-problem/#hostcentric-monitoring) if a single worker node fails, although failure of a master node such as one of your NameNodes will require fairly rapid remediation. Generally speaking, individual host-level indicators are less important than service-level metrics when it comes to Hadoop.

Key Hadoop performance metrics to monitor


When working properly, a Hadoop cluster can handle a truly massive amount of data—there are plenty of production clusters managing petabytes of data each. Monitoring each of Hadoop's sub-components is essential to keep jobs running and the cluster humming.

Hadoop metrics can be broken down into four broad categories:



-   [HDFS metrics](#hdfs-metrics)
-   [MapReduce counters](#mapreduce-counters)
-   [YARN metrics](#yarn-metrics)
-   [ZooKeeper metrics](#zookeeper-metrics)



{{< img src="hadoop-diagram10-6.png" alt="Hadoop metrics breakdown diagram" popup="true" size="1x" >}}

To learn more about collecting Hadoop and ZooKeeper metrics, take a look at [part three](/blog/collecting-hadoop-metrics/) of this series.

This article references metric terminology introduced in our [Monitoring 101 series](/blog/monitoring-101-collecting-data/), which provides a framework for metric collection and alerting.



HDFS metrics


HDFS metrics can be further decomposed into two categories:



-   [NameNode metrics](#namenodeemitted-metrics)
-   [DataNode metrics](#datanode-metrics)



 

**NameNode and DataNodes**

[DataNodes](/blog/hadoop-architecture-overview/#hdfs-architecture) communicate with their [NameNode](/blog/hadoop-architecture-overview/#hdfs-architecture) (and vice versa) via a periodic heartbeat (by default every three seconds, set by `dfs.heartbeat.interval`). The heartbeat contains (amongst other things) health information about the DataNode. It is through this mechanism that the NameNode is able to know the state of all the DataNodes in the cluster.


Failure of the [NameNode](/blog/hadoop-architecture-overview/#hdfs-architecture) without any replica standing by will cause data stored in the cluster to become unavailable. Therefore monitoring the primary NameNode and its Secondary/Standby NameNode is critical to ensure high cluster availability. In addition to reporting metrics about themselves, NameNodes can also report metrics about all DataNodes, providing a good birds-eye view of the rest of your HDFS deploy.

NameNode metrics can be divided into two groups:



-   NameNode-emitted metrics
-   [NameNode JVM metrics](#namenode-jvm-metrics)





### NameNode-emitted metrics




<table>
<thead>
<tr class="header">
<th>Name</th>
<th>Description</th>
<th><a href="/blog/monitoring-101-collecting-data/">Metric Type</a></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>CapacityRemaining</td>
<td>Available capacity</td>
<td>Resource: Utilization</td>
</tr>
<tr class="even">
<td>CorruptBlocks/MissingBlocks</td>
<td>Number of corrupt/missing blocks</td>
<td>Resource: Error/Resource: Availability</td>
</tr>
<tr class="odd">
<td>VolumeFailuresTotal</td>
<td>Number of failed volumes</td>
<td>Resource: Error</td>
</tr>
<tr class="even">
<td>NumLiveDataNodes/NumDeadDataNodes</td>
<td>Count of alive DataNodes/Count of dead DataNodes</td>
<td>Resource: Availability</td>
</tr>
<tr class="odd">
<td>FilesTotal</td>
<td>Total count of files tracked by the NameNode</td>
<td>Resource: Utilization</td>
</tr>
<tr class="even">
<td>TotalLoad</td>
<td>Measure of file access across all DataNodes</td>
<td>Resource: Utilization</td>
</tr>
<tr class="odd">
<td>BlockCapacity/BlocksTotal</td>
<td>Maximum number of blocks allocable/Count of blocks tracked by NameNode</td>
<td>Resource: Utilization</td>
</tr>
<tr class="even">
<td>UnderReplicatedBlocks</td>
<td>Count of under-replicated blocks</td>
<td>Resource: Availability</td>
</tr>
<tr class="odd">
<td>NumStaleDataNodes</td>
<td>Count of stale DataNodes</td>
<td>Resource: Availability</td>
</tr>
</tbody>
</table>




{{< img src="hdfs-disk-usage-2.png" alt="HDFS Capacity remaining graph" >}}

#### Metric to alert on: CapacityRemaining

CapacityRemaining represents the total available capacity remaining across the entire HDFS cluster. It is an understatement to say that running out of disk space in HDFS will cause BadThingsToHappen™. DataNodes that are out of space are likely to fail on boot, and of course, running DataNodes will not be able to be written to. In addition, any running jobs which write out temporary data may fail due to lack of capacity. It is good practice to ensure that disk use never exceeds 80 percent capacity.

Thankfully, HDFS [makes it easy](https://wiki.apache.org/hadoop/FAQ#I_have_a_new_node_I_want_to_add_to_a_running_Hadoop_cluster.3B_how_do_I_start_services_on_just_one_node.3F) to spin up new DataNodes to add capacity (or you can add extra disks to existing DataNodes, of course).

#### Metric to alert on: MissingBlocks

Corrupt or missing blocks can point to an unhealthy cluster. Typically, upon receiving a read request a DataNode will locate the requested block and serve it back to the client, along with a checksum for the data (which was calculated and stored on the DataNode when the block was written). If the checksum for the received data doesn’t match the stored checksum, the client reports the corruption to the NameNode and reads the data from one of the other replicas. The NameNode, meanwhile, schedules a rereplication of the block from one of the healthy copies, and then tells the original DataNode to delete its corrupted copy. So, although you may see corrupt blocks reported on your cluster from time to time, that doesn’t necessarily mean that you have lost any data.

A *missing* block is far worse than a corrupt block, because a missing block cannot be recovered by [copying a replica](https://twiki.opensciencegrid.org/bin/view/Storage/HadoopRecovery). A missing block represents a block for which no known copy exists in the cluster. That's not to say that the block no longer exists—if a series of DataNodes were taken offline for maintenance, missing blocks could be reported until they are brought back up.

You may not care if you have a corrupt block or two in the entire cluster, but if blocks start going missing without any scheduled maintenance it is cause for concern.

#### Metric to alert on: VolumeFailuresTotal

In [old versions of Hadoop](https://issues.apache.org/jira/browse/HDFS-2137), failure of a single disk would cause an entire DataNode to be taken offline. Thankfully, that is no longer the case—HDFS now allows for disks to fail in place, without affecting DataNode operations, until a threshold value is reached. (This is set on each DataNode via the `dfs.datanode.failed.volumes.tolerated` property; it defaults to 0, meaning that any volume failure will shut down the DataNode; on a production cluster where DataNodes typically have 6, 8, or 12 disks, setting this parameter to 1 or 2 is typically the best practice.)

Though a failed volume will not bring your cluster to grinding halt, you most likely want to know when hardware failures occur, if only so that you can replace the failed hardware. Since HDFS was designed with hardware failure in mind, with a default replication of three, a failed volume should never signal data loss.

#### Metric to alert on: NumDeadDataNodes

NumLiveDataNodes and NumDeadDataNodes together track the number of DataNodes in the cluster, by state. Ideally, your number of live DataNodes will be equal to the number of DataNodes you've provisioned for the cluster. If this number unexpectedly drops, it may warrant investigation.

NumDeadDataNodes, on the other hand, should be alerted on. When the NameNode does not hear from a DataNode for 30 seconds, that DataNode is marked as "stale." Should the DataNode fail to communicate with the NameNode for 10 minutes following the transition to the "stale" state, the DataNode is marked "dead." The death of a DataNode causes a flurry of network activity, as the NameNode initiates replication of blocks lost on the dead nodes.

Though the loss of a single DataNode may not impact performance much, losing multiple DataNodes will start to be very taxing on cluster resources, and could result in data loss.

**FilesTotal** is a running count of the number of files being tracked by the NameNode. Because the NameNode stores all metadata in memory, the greater the number of files (or blocks, or directories) tracked, [the more memory](http://blog.cloudera.com/blog/2009/02/the-small-files-problem/) required by NameNode. The rule of thumb for NameNode memory requirements is that each object (file, directory, block) tracked by the NameNode consumes roughly [150 bytes](https://www.mail-archive.com/core-user@hadoop.apache.org/msg02835.html) of memory. If each file is mapped to one block (files often span multiple blocks), that is approximately 300 bytes per file. That doesn't sound like much until you factor in the replication of data: the default replication factor is 3 (so 900 bytes per file), *and* each replica adds an additional 16 bytes, for a total of ~1 KB of metadata per file. That still may not sound like much, but as your cluster expands to include millions of files, you should keep this number in mind and plan to add additional memory to your NameNode.

{{< img src="hdfs-totalload.png" alt="TotalLoad diagram" size="1x" >}}

**TotalLoad** is the current number of concurrent file accesses (read/write) across all DataNodes. This metric is not usually indicative of a problem, though it can illuminate issues related to job execution. Because worker nodes running the DataNode daemon also perform MapReduce tasks, extended periods of high I/O (indicated by high TotalLoad) generally translate to degraded job execution performance. Tracking TotalLoad over time can help get to the bottom of job performance issues.

**BlockCapacity/BlocksTotal**: Like FilesTotal, keeping an eye on the total number of blocks across the cluster is essential to continued operation. Block capacity and file capacity are very closely related but not the same (files can span multiple blocks); monitoring both block and file capacity is necessary to ensure uninterrupted operation. If your cluster is approaching the limits of block capacity, you can easily add more by bringing up a new DataNode and adding it to the pool, or adding more disks to existing nodes. Once added, you can use the [Hadoop balancer](https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HDFSCommands.html#balancer) to balance the distribution of blocks across DataNodes.

**UnderReplicatedBlocks** are the number of blocks with insufficient replication. Hadoop's replication factor is configurable on a [per-client](https://hadoop.apache.org/docs/r2.4.1/hadoop-project-dist/hadoop-hdfs/hdfs-default.xml#dfs.replication) or [per-file](https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-common/FileSystemShell.html#setrep) basis. The default replication factor is three, meaning that each block will be stored on three DataNodes. If you see a large, sudden spike in the number of under-replicated blocks, it is likely that a DataNode has died—this can be verified by correlating under-replicated block metrics with the status of DataNodes (via NumLiveDataNodes and related metrics).

{{< img src="live-dead-decom.png" alt="Live, dead, and decommissioned DataNodes image" popup="true" size="1x" >}}

**NumStaleDataNodes**: Every three seconds (by default), DataNodes send a heartbeat message to the NameNode. This heartbeat acts as a health-check mechanism but can also be used by the NameNode to delegate new work. As explained above, DataNodes that do not send a heartbeat within 30 seconds are marked as "stale." A DataNode might not emit a heartbeat for a number of reasons—network issues or high load are among the more common causes. Unless you've disabled reads or writes to stale DataNodes, you should definitely keep an eye on this metric. A DataNode that did not emit a heartbeat due to high system load (or a slow network) will likely cause any reads or writes to that DataNode to be delayed as well. However, in practice, a stale DataNode is likely dead.

Even if reading and writing on stale DataNodes is disabled, you should still monitor for sudden increases in the number of stale DataNodes, because in a short time stale nodes can easily become dead nodes. And stale DataNodes will be written to regardless of your settings if the ratio of stale DataNodes to total DataNodes exceeds the value of `dfs.namenode.write.stale.datanode.ratio`.



### NameNode JVM metrics


Because the NameNode runs in the Java Virtual Machine (JVM), it relies on Java garbage collection processes to free up memory. The more activity in your HDFS cluster, the more often the garbage collection will run.

Anyone familiar with Java applications knows that garbage collection can come with a high performance cost. See [the Oracle documentation](http://www.oracle.com/webfolder/technetwork/tutorials/obe/java/gc01/index.html) for a good primer on Java garbage collection.

If you are seeing excessive pauses during garbage collection, you can consider upgrading your JDK version or garbage collector. Additionally, you can tune your Java runtime to minimize garbage collection.

Because a NameNode is typically hosted on a machine with ample computational resources, using the CMS (ConcurrentMarkSweep) garbage collector is recommended, *especially* because bottlenecks on the NameNode will result in degraded performance cluster-wide. From the Oracle documentation:

> The CMS collector should be used for applications that require low pause times and can share resources with the garbage collector. Examples include desktop UI application that respond to events, a webserver responding to a request or a database responding to queries.


ConcurrentMarkSweep collections free up unused memory in the old generation of the heap. CMS is a low-pause garbage collection, meaning that although it does temporarily stop application threads, it does so only intermittently.

For more information on optimizing NameNode garbage collection, see this [excellent guide](https://community.hortonworks.com/articles/14170/namenode-garbage-collection-configuration-best-pra.html) from Hortonworks.



<table>
<thead>
<tr class="header">
<th>Name</th>
<th>Description</th>
<th><a href="/blog/monitoring-101-collecting-data/">Metric Type</a></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>ConcurrentMarkSweep count</td>
<td>Number of old-generation collections</td>
<td>Other</td>
</tr>
<tr class="even">
<td>ConcurrentMarkSweep time</td>
<td>Elapsed time of old-generation collections, in milliseconds</td>
<td>Other</td>
</tr>
</tbody>
</table>



{{< img src="nn-cms-1.png" alt="NameNode CMS" popup="true" size="1x" >}}

If CMS is taking more than a few seconds to complete, or is occurring with increased frequency, your NameNode may not have enough memory allocated to the JVM to function efficiently.



### DataNode metrics


DataNode metrics are host-level metrics specific to a particular DataNode.



<table>
<thead>
<tr class="header">
<th>Name</th>
<th>Description</th>
<th><a href="/blog/monitoring-101-collecting-data/">Metric Type</a></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Remaining</td>
<td>Remaining disk space</td>
<td>Resource: Utilization</td>
</tr>
<tr class="even">
<td>NumFailedVolumes</td>
<td>Number of failed storage volumes</td>
<td>Resource: Error</td>
</tr>
</tbody>
</table>



{{< img src="dn-disk0.png" alt="Disk remaining on DataNodes" popup="true" size="1x" >}}

**Remaining**: As mentioned in the [section on NameNode metrics](#metric-to-alert-on-capacityremaining), running out of disk space can cause a number of problems in a cluster. If left unrectified, a single DataNode running out of space could quickly cascade into failures across the entire cluster as data is written to an increasingly-shrinking pool of available DataNodes. Tracking this metric over time is essential to maintain a healthy cluster; you may want to alert on this metric when the remaining space falls dangerously low (less than 10 percent).

**NumFailedVolumes**: By default, a single volume failing on a DataNode will cause the entire node to go offline. Depending on your environment, that may not be desired, especially since most DataNodes operate with multiple disks. If you haven't set `dfs.datanode.failed.volumes.tolerated` in your HDFS configuration, you should definitely track this metric. Remember, when a DataNode is taken offline, the NameNode must copy any under-replicated blocks that were lost on that node, causing a burst in network traffic and potential performance degradation. To prevent a slew of network activity from the failure of a single disk (if your use case permits), you should set the tolerated level of volume failure in your config like so:



{{< code >}}
    <property>
      
          <name>dfs.datanode.failed.volumes.tolerated</name>
      
          <value>N</value>
      
      </property>
{{< /code >}}




where N is the number of failures a DataNode should tolerate before shutting down.

*Don't forget to restart your DataNode process following a configuration change.*

The downside to enabling this feature is that, with fewer disks to write to, a DataNode's performance may suffer. Setting a reasonable value for tolerated failures will vary depending on your use case.



MapReduce counters


The MapReduce framework exposes a number of counters to track statistics on MapReduce job execution. Counters are an invaluable mechanism that let you see what is actually happening during a MapReduce job run. They provide a count of the number of times an event occurred. MapReduce counters can be broken down into four categories:



-   [job counters](#job-counters)
-   [task counters](#task-counters)
-   [custom counters](#custom-counters)
-   file system counters



{{< img src="hadoop-diagram12-2.png" alt="MapReduce counters breakdown" popup="true" size="1x" >}}

MapReduce application developers may want to track the following counters to to find bottlenecks and potential optimizations in their applications.



### Job counters


Group name:`org.apache.hadoop.mapreduce.JobCounter`



<table>
<thead>
<tr class="header">
<th>Counter Name</th>
<th>Description</th>
<th><a href="/blog/monitoring-101-collecting-data/">Metric Type</a></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>MILLIS_MAPS/MILLIS_REDUCES</td>
<td>Processing time for maps/reduces</td>
<td>Work: Performance</td>
</tr>
<tr class="even">
<td>NUM_FAILED_MAPS/NUM_FAILED_REDUCES</td>
<td>Number of failed maps/reduces</td>
<td>Work: Error</td>
</tr>
<tr class="odd">
<td>RACK_LOCAL_MAPS/DATA_LOCAL_MAPS/OTHER_LOCAL_MAPS</td>
<td>Counters tracking where map tasks were executed</td>
<td>Resource: Other</td>
</tr>
</tbody>
</table>




**MILLIS_MAPS/MILLIS_REDUCES**: These metrics track the wall time spent across all of your map and reduce tasks. Their full utility is realized when tracked alongside the task counter GC_TIME_MILLIS (see [below](#task-counters)); when taken altogether, it is possible to determine the percentage of time spent performing garbage collection.

Using all three counters, we can calculate the percentage of time spent in garbage collection with the following formula: GC_TIME_PERCENTAGE = GC_TIME_MILLIS / (MILLIS_MAPS + MILLIS_REDUCES)

Jobs where garbage collection is consuming a significant percentage of computation time (e.g. more than 20 percent) may benefit from increasing the amount of heap available to them.

**NUM_FAILED_MAPS/NUM_FAILED_REDUCES**: This pair of metrics tracks the number of failed map/reduce tasks for a job. Tasks can fail for many reasons—abrupt exit by the JVM, runtime errors, and hanging tasks are among the most common. Failed tasks are tolerated, up to the value set by the `mapreduce.map.maxattempts` and `mapreduce.reduce.maxattempts` properties (set to four, by default). If a task fails `maxattempts` times, it is marked as failed. A job will fail as a whole if more than `mapreduce.map.failures.maxpercent` percent of map tasks in the job fail or more than `mapreduce.reduce.failures.maxpercent` percent of the reduce tasks fail.

Because failures are expected, you should not alert on this metric, though if you are seeing the same task fail on several DataNodes, it may be worth diving into the job logs or even the application code for bugs. If many tasks fail on a particular DataNode, the issue could be hardware-related.

**DATA_LOCAL_MAPS/RACK_LOCAL_MAPS/OTHER_LOCAL_MAPS**: These counters track the number of map tasks that were performed, aggregated by location. Data can be located either: on the node executing the map task, on a node in the same rack as the node performing the map task, or on a node located on a different rack somewhere else in the cluster. Recall from [part 1 of this series](/blog/hadoop-architecture-overview/#hdfs-architecture) that one of Hadoop's greatest strengths lies in its preference for moving computation as close to the data as possible. The benefits from operating on local data include reduced network overhead and faster execution. These benefits are lost when the computation must be performed on a node that is not physically close to the data being processed.

Because sending data over the network takes time, correlating poor job performance with these counters can help determine *why* performance suffered. If many maps had to be executed on nodes where the data was not locally hosted, it would be reasonable to expect degraded performance.



### Task counters


Task counters track the results of task operations in aggregate. Each counter below represents the total across all tasks associated with a particular job.

Group name: `org.apache.hadoop.mapreduce.JobCounter`



<table>
<thead>
<tr class="header">
<th>Counter Name</th>
<th>Description</th>
<th><a href="/blog/monitoring-101-collecting-data/">Metric Type</a></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>REDUCE_INPUT_RECORDS</td>
<td>Number of input records for reduce tasks</td>
<td>Other</td>
</tr>
<tr class="even">
<td>SPILLED_RECORDS</td>
<td>Number of records spilled to disk</td>
<td>Resource: Saturation</td>
</tr>
<tr class="odd">
<td>GC_TIME_MILLIS</td>
<td>Processing time spent in garbage collection</td>
<td>Other</td>
</tr>
</tbody>
</table>



**REDUCE_INPUT_RECORDS**: Keeping an eye on the number of input records for each reduce task in a job is one of the best ways to identify performance issues related to a *skewed dataset*. Skewed data is characterized by a disproportionate distribution of input records across all reducers for a job. To give a concrete example, consider the canonical wordcount run on a text composed of 40,000 "the"s and one "a". If this text were run through two reducers, and each got the values associated with one of the two keys, the reducer working on the larger dataset (the set of "the" keys) would take much longer to complete than the reducer with a much smaller dataset.

Skewed datasets can make jobs take much longer to complete than expected. Unfortunately, cluster administrators can't simply add more reducers to speed up execution—in cases like this, the MapReduce job would probably benefit from the addition of a [combine step](http://www.tutorialspoint.com/map_reduce/map_reduce_combiners.htm).

**SPILLED_RECORDS**: Map output data is stored in memory, but when the buffer fills up data is dumped to disk. A separate thread is spawned to merge all of the spilled data into a single larger sorted file for reducers. Spills to disk should be minimized, as more than one spill will result in an increase in disk activity as the merging thread has to read and write data to disk. Tracking this metric can help determine if configuration changes need to be made (like increasing the memory available for map tasks) or if additional processing (compression) of the input data is necessary.

**GC_TIME_MILLIS**: Useful for determining the percentage of time tasks spent performing garbage collection. See the section on [MILLIS_MAPS/MILLIS_REDUCES](#job-counters) for more information.



### Custom counters


MapReduce allows users to implement [custom counters](https://hadoop.apache.org/docs/r2.7.2/api/org/apache/hadoop/mapred/Counters.html) that are specific to their application. Custom counters can be used to track more fine-grained counts, such as [counting the number of malformed or missing records](http://www.ashishpaliwal.com/blog/2012/05/hadoop-recipe-using-custom-java-counters/).

Keep in mind, however, that since all counters reside in the JobTracker JVM's memory, there is a practical limit to the number of counters you should use, limited by the amount of physical memory available. (Hadoop has a configuration value, `mapreduce.job.counters.max`, which limits the number of custom counters that can be created; by default this is 120.)



YARN metrics


YARN metrics can be grouped into three distinct categories:



-   [Cluster metrics](#cluster-metrics)
-   [Application metrics](#application-metrics)
-   [NodeManager metrics](#nodemanager-metrics)



{{< img src="hadoop-diagram13-3.png" alt="YARN metrics breakdown" popup="true" size="1x" >}}



### Cluster metrics


Cluster metrics provide a high-level view of YARN application execution. The metrics listed here are aggregated cluster-wide.



<table>
<thead>
<tr class="header">
<th>Name</th>
<th>Description</th>
<th><a href="/blog/monitoring-101-collecting-data/">Metric Type</a></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>unhealthyNodes</td>
<td>Number of unhealthy nodes</td>
<td>Resource: Error</td>
</tr>
<tr class="even">
<td>activeNodes</td>
<td>Number of currently active nodes</td>
<td>Resource: Availability</td>
</tr>
<tr class="odd">
<td>lostNodes</td>
<td>Number of lost nodes</td>
<td>Resource: Error</td>
</tr>
<tr class="even">
<td>appsFailed</td>
<td>Number of failed applications</td>
<td>Work: Error</td>
</tr>
<tr class="odd">
<td>totalMB/allocatedMB</td>
<td>Total amount of memory/amount of memory allocated</td>
<td>Resource: Utilization</td>
</tr>
</tbody>
</table>



#### Metric to alert on: unhealthyNodes

YARN considers any node with disk utilization exceeding the value specified under the property `yarn.nodemanager.disk-health-checker.max-disk-utilization-per-disk-percentage` (in yarn-site.xml) to be unhealthy. Ample disk space is critical to ensure uninterrupted operation of a Hadoop cluster, and large numbers of unhealthyNodes (the number to alert on depends on the size of your cluster) should be quickly investigated and resolved. Once a node is marked unhealthy, other nodes have to fill the void, which can cause a cascade of alerts as node after node nears full disk utilization.

It is worth mentioning that you can add your own health checks to YARN with a [simple configuration change](https://hadoop.apache.org/docs/current/hadoop-yarn/hadoop-yarn-site/NodeManager.html#External_Health_Script). But be warned—if the script should fail for any reason, including wrong permissions, incorrect path, and so on—it will cause the node to be marked as unhealthy.

**activeNodes/lostNodes**: The activeNodes metric tracks the current count of active, or normally operating, nodes. This metric should remain static in the absence of anticipated maintenance. If a NodeManager fails to maintain contact with the ResourceManager, it will eventually be marked as "lost" and its resources will become unavailable for allocation. The timeout threshold is configurable via the `yarn.resourcemanager.nm.liveness-monitor.expire-interval-ms` property in yarn-site.xml, with a default value of 10 minutes (600000 ms). Nodes can lose contact with the ResourceManager for a number of reasons, including network issues, hardware failure, or a hung process. It is good to be aware of lost nodes, so you can take action if the node never returns.

**appsFailed**: Assuming you are running MapReduce on YARN, if the percentage of failed map or reduce tasks exceeds a specific threshold (configured with `mapreduce.map.failures.maxpercent` and `mapreduce.reduce.failures.maxpercent`, respectively) the application as a whole will fail. It is important to note that YARN cannot distinguish between a failed NodeManager and a hanging task—in either case, the NodeManager will fail to report to the ResourceManager within the heartbeat timeout period and the task will be rerun. After four unsuccessful attempts to run the task (configured with `mapreduce.map.maxattempts` and `mapreduce.reduce.maxattempts`, respectively), it will be marked as failed.

In the case of ResourceManager failure, application state is largely unaffected, though no new work will be able to be submitted and currently running jobs will start to fail. Because the ApplicationMasters (on each NodeManager) store the application state (including the list of run/failed/killed tasks), once a new ResourceManager is brought online (and assuming the old saved state is recoverable), NodeManagers can pick up where they left off.

**totalMB/allocatedMB**: When taken together, the totalMB and allocatedMB metrics give a high-level view of your cluster's memory usage. Memory is currency in Hadoop, and if you are nearing the ceiling of your memory usage you have a couple of options. To increase the memory available to your cluster, you can add new NodeManager nodes, tweak the amount of memory reserved for YARN applications (set by the `yarn.nodemanager.resource.memory-mb` in `yarn-site.xml`, or change the minimum amount of RAM allocated to containers (set by the `yarn.scheduler.minimum-allocation-mb` property in `yarn-site.xml`).

Keep in mind that YARN may over-commit resources, which can occasionally translate to reported values of allocatedMB which are higher than totalMB.



### Application metrics


Application metrics provide detailed information on the execution of individual YARN applications.



<table>
<thead>
<tr class="header">
<th>Name</th>
<th>Description</th>
<th><a href="/blog/monitoring-101-collecting-data/">Metric Type</a></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>progress</td>
<td>Application execution progress meter</td>
<td>Work: Performance</td>
</tr>
</tbody>
</table>



**progress**: Progress gives you a real-time window into the execution of a YARN application. Its reported value will always be in the range of zero to one (inclusive), with a value of one indicating completed execution. Because application execution can often times be opaque when running hundreds of applications on thousands of nodes, tracking progress alongside other metrics can better help you to determine the cause of any performance degradation. Applications that go extended periods without making progress should be investigated.



### NodeManager metrics


NodeManager metrics provide resource information at the individual node level.



<table>
<thead>
<tr class="header">
<th>Name</th>
<th>Description</th>
<th><a href="/blog/monitoring-101-collecting-data/">Metric Type</a></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>containersFailed</td>
<td>Number of containers that failed to launch</td>
<td>Resource: Error</td>
</tr>
</tbody>
</table>



**containersFailed** tracks the number of containers that failed to launch on that particular NodeManager. [Recall from the first article](/blog/hadoop-architecture-overview/#caution-overloaded-terms-ahead) in the series that NodeManager containers are *not* Docker containers.

[Configuration issues aside](https://stackoverflow.com/questions/22579943/yarn-mapreduce-job-issue-am-container-launch-error-in-hadoop-2-3-0), the most common cause of container launch failure is hardware-related. If the NodeManager's disk is full, [any container it launches will fail](https://issues.apache.org/jira/browse/YARN-257). Similarly, if the NodeManager's [heap is set too low](https://stackoverflow.com/questions/23374693/hadoop-yarn-failed-to-launch-container), containers won't launch. You don't need to be alerted for every container that failed to launch, but if a single node has many failed containers, it may be time to investigate.



ZooKeeper metrics


ZooKeeper plays an important role in a Hadoop deployment. It is responsible for ensuring the availability of the [HDFS NameNode](/blog/hadoop-architecture-overview/#hdfs-and-zookeeper) and YARN's ResourceManager. If your cluster is operating in high-availability mode, you should be sure to monitor ZooKeeper alongside the rest of your Hadoop components to avoid service interruptions.

ZooKeeper exposes metrics via MBeans as well as through a command line interface, using the so-called [4-letter words](/blog/collecting-hadoop-metrics/#the-4letter-word). For more details on collecting ZooKeeper metrics, be sure to check out [part three](/blog/collecting-hadoop-metrics/) of this series.



<table>
<thead>
<tr class="header">
<th>Name</th>
<th>Description</th>
<th><a href="/blog/monitoring-101-collecting-data/">Metric Type</a></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><code>zk_followers</code></td>
<td>Number of active followers</td>
<td>Resource: Availability</td>
</tr>
<tr class="even">
<td><code>zk_avg_latency</code></td>
<td>Amount of time it takes to respond to a client request (in ms)</td>
<td>Work: Performance</td>
</tr>
<tr class="odd">
<td><code>zk_num_alive_connections</code></td>
<td>Number of clients connected to ZooKeeper</td>
<td>Resource: Availability</td>
</tr>
</tbody>
</table>



#### Metric to alert on: zk_followers (leader only)

The number of followers should equal the total size of your ZooKeeper ensemble, minus 1 (the leader is not included in the follower count). If the ensemble fails to maintain quorum, all automatic failover features are suspended. Changes to this value should be alerted on, as the size of your ensemble should only change due to user intervention (e.g., an administrator decommissioned or commissioned a node).

**zk_avg_latency**: The average request latency is the average time it takes (in milliseconds) for ZooKeeper to respond to a request. ZooKeeper will not respond to a request until it has written the transaction to its transaction log. Any latency spikes could delay the transition between servers in the event of a ResourceManager or NameNode failure. Of course, such events are rare, but by tracking the average latency over time you can better correlate errors that may have been caused by stale data.

{{< img src="zk-lat.png" alt="ZooKeeper average request latency" popup="true" >}}

**zk_num_alive_connections**: ZooKeeper reports the number of connected clients via this metric. This represents all connections, including connections from non-ZooKeeper nodes. In most environments, this number should remain fairly static—generally, your number of NameNodes, ResourceManagers, and their respective standbys should remain relatively stable. You should be aware of unanticipated drops in this value; since Hadoop uses ZooKeeper to provide high availability, a loss of connection to ZooKeeper could make the cluster less resilient to node loss.

Go forth, and collect!


In this post we’ve explored many of the key metrics you should monitor to keep tabs on the health and performance of your Hadoop cluster.

The metrics covered in this post pertain to the core Hadoop components and their typical use. Given Hadoop's vast ecosystem, over time you will likely identify additional metrics that are particularly relevant to your specific Hadoop infrastructure, and its users.

[Read on](/blog/collecting-hadoop-metrics/) for a comprehensive guide to collecting all of the metrics described in this article, and any other metric exposed by Hadoop.

Acknowledgments


Special thanks to [Ian Wrigley](https://twitter.com/iwrigley), Director of Education Services at [Confluent](http://www.confluent.io/), for graciously sharing both his Hadoop expertise and monitoring strategies for this article.

*Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/hadoop/how_to_monitor_hadoop_metrics.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues).*
