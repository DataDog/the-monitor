_This post is part 1 of a 4-part series on monitoring Hadoop health and performance. [Part 2] dives into the key metrics to monitor, [Part 3] details how to monitor Hadoop performance natively, and [Part 4] explains how to monitor a Hadoop deployment with Datadog._

In this post, we'll explore each of the technologies that make up a typical Hadoop deployment, and see how they all fit together. If you're already familiar with HDFS, MapReduce, and YARN, feel free to continue on to [Part 2] to dive right into Hadoop's key performance metrics.

## What is Hadoop?

Apache Hadoop is an open source framework for distributed storage and processing of very large data sets on computer clusters. Hadoop began as a project to implement Google's [MapReduce][mapreduce-paper] programming model, and has become synonymous with a [rich ecosystem][hadoop-ecosystem] of related technologies, not limited to: Apache Pig, Apache Hive, Apache Spark, Apache HBase, and others.

Hadoop has seen [widespread adoption][powered-by] by many companies including Facebook, Yahoo!, Adobe, Cisco, eBay, Netflix, and Datadog.

## Architecture overview
Hadoop has three core components, plus ZooKeeper if you want to enable high availability:

- [Hadoop Distributed File System (HDFS)](#toc-hdfs-architecture2)  
- [MapReduce](#toc-mapreduce-overview6)  
- [Yet Another Resource Negotiator (YARN)](#toc-untangling-yarn9)  
- [ZooKeeper](#toc-zookeeper15)  

<div id="HDFS-architecture"></div>

## HDFS architecture

The Hadoop Distributed File System (HDFS) is the underlying file system of a Hadoop cluster. It provides scalable, fault-tolerant, rack-aware data storage designed to be deployed on commodity hardware. Several attributes set HDFS apart from other distributed file systems. Among them, some of the key differentiators are that HDFS is:

- designed with hardware failure in mind  
- built for large datasets, with a default block size of 128 MB  
- optimized for sequential operations  
- rack-aware  
- cross-platform and supports heterogeneous clusters  

Data in a Hadoop cluster is broken down into smaller units (called blocks) and distributed throughout the cluster. Each block is duplicated twice (for a total of three copies), with the two replicas stored on two nodes in a rack somewhere else in the cluster. Since the data has a default replication factor of three, it is highly available and fault-tolerant. If a copy is lost (because of machine failure, for example), HDFS will automatically re-replicate it elsewhere in the cluster, ensuring that the threefold replication factor is maintained.

HDFS architecture can vary, depending on the Hadoop version and features needed:  

- Vanilla HDFS  
- [High-availability HDFS](#toc-ha-namenode-service4)  

HDFS is based on a leader/follower architecture. Each cluster is typically composed of a single NameNode, an optional SecondaryNameNode (for data recovery in the event of failure), and an arbitrary number of DataNodes.

[![Vanilla Hadoop deployment diagram][vanilla]][vanilla]  
_A vanilla Hadoop deployment_

<div id="NameNode"></div>

In addition to managing the file system namespace and associated metadata (file-to-block maps), the NameNode acts as the master and brokers access to files by clients (though once brokered, clients communicate directly with DataNodes). The NameNode operates entirely in memory, persisting its state to disk. It represents a single point of failure for a Hadoop cluster that is not running in high-availability mode. To mitigate against this, production clusters typically persist state to two local disks (in case of a single disk failure) and also to an NFS-mounted volume (in case of total machine failure). In [high-availability mode](#toc-ha-namenode-service4), Hadoop maintains a standby NameNode to guard against failures. Earlier versions of Hadoop offered an alternative with the introduction of the SecondaryNameNode concept, and many clusters today still operate with a SecondaryNameNode.

To understand the function of the SecondaryNameNode requires an explanation of the mechanism by which the NameNode stores its state. 

### fsimage and the edit log

The NameNode stores file system metadata in [two different files][checkpointing]: the fsimage and the edit log. The fsimage stores a complete snapshot of the file system’s metadata at a specific moment in time. Incremental changes (like renaming or appending a few bytes to a file) are then stored in the edit log for durability, rather than creating a new fsimage snapshot each time the namespace is modified. With this separation of concerns in places, the NameNode can restore its state by loading the fsimage and performing all the transforms from the edit log, restoring the file system to its most recent state.
![Secondary NameNode architecture diagram][secondary-nn-arch]

[checkpointing]: http://blog.cloudera.com/blog/2014/03/a-guide-to-checkpointing-in-hadoop/

Through RPC calls, the SecondaryNameNode is able to independently update its copy of the fsimage each time changes are made to the edit log. Thus, if the NameNode goes down in the presence of a SecondaryNameNode, the NameNode doesn't need to replay the edit log on top of the fsimage; cluster administrators can retrieve an updated copy of the fsimage from the SecondaryNameNode. 

SecondaryNameNodes provide a means for _much_ faster recovery in the event of NameNode failure. Despite its name, though, it is not a drop-in replacement for the NameNode and does not provide a means for automated failover.

<div id="HA-NameNode"></div>

### HA NameNode service

Early versions of Hadoop introduced several concepts (like SecondaryNameNodes, among others) to make the NameNode more resilient. With Hadoop 2.0 and Standby NameNodes, a mechanism for true high availability was realized. 

Standby NameNodes, which are incompatible with SecondaryNameNodes, provide automatic failover in the event of primary NameNode failure. Achieving high availability with Standby NameNodes requires shared storage between the primary and standbys (for the edit log).

Though there are two options for the necessary shared storage—[NFS][ha-with-nfs] and [Quorum Journal Manager(QJM)][ha-with-qjm]—only QJM is considered production-ready.

#### NameNode and QJM
Using the Quorum Journal Manager (QJM) is the preferred method for achieving high availability for HDFS.

Using QJM to maintain consistency of Active and Standby state requires that both nodes be able to communicate with a group of JournalNodes (JNs). When the Active node modifies the namespace, it logs a record of the change to a majority of JournalNodes. The StandbyNode watches the JNs for changes to the edit log and applies them to its own namespace. 

[![QJM interaction diagram][qjm-diagram]][qjm-diagram]

JournalNode daemons have relatively low overhead, so provisioning additional machines for them is unnecessary—the daemons can be run on the same machines as existing Hadoop nodes. Typically, a daemon is run on the [ResourceManager](#toc-resourcemanager11) as well as on each of the two NameNodes. Because edit log changes require a quorum of JNs, you must maintain an odd number of at least three daemons running at any one time. JournalNodes can tolerate failures of at most (N - 1) / 2 nodes (where N is the number of JNs).

### Alternative file systems

HDFS is the canonical file system for Hadoop, but Hadoop's file system abstraction supports a [number of alternative file systems][HCFS], including the local file system, FTP, AWS S3, Azure's file system, and OpenStack's Swift. The file system used is determined by the access URI, e.g. `file:` for the local file system, `s3:` for data stored on Amazon S3, etc. Most of these have limitations, though, and in production HDFS is almost always the file system used for the cluster.

<div id="MapReduce"></div>

## MapReduce overview
MapReduce is a framework tailor-made for processing large datasets in a distributed fashion across multiple machines. The core of a MapReduce job can be, err, reduced to three operations: _map_ an input data set into a collection of <key,value> pairs, _shuffle_ the resulting data (transfer data to the reducers), then _reduce_ over all pairs with the same key.

The top-level unit of work in MapReduce is a job. Each job is composed of one or more _map_ or _reduce_ tasks.
 
The canonical example of a MapReduce job is counting word frequencies in a body of text. The image below illustrates such an example:

[![MapReduce word frequency flow diagram][mapreduce-wordcount]][mapreduce-wordcount]

### Key differences between versions

In earlier versions of Hadoop (pre-2.0), MapReduce took care of its own resource allocation and job scheduling as well as the actual computation. 

Newer versions of Hadoop (2.0+) decouple the scheduling from the computation with [YARN](#toc-untangling-yarn9), which handles the allocation of computational resources for MapReduce jobs. This allows other processing frameworks (see below) to share the cluster without resource contention.

### Other frameworks
Though Hadoop comes with MapReduce out of the box, a number of computing frameworks have been developed for or adapted to the Hadoop ecosystem. Among the more popular are [Apache Spark][Spark] and [Apache Tez][Tez]. This article series will focus on MapReduce as the compute framework.

<div id="YARN"></div>

## Untangling YARN
YARN (Yet Another Resource Negotiator) is the framework responsible for assigning computational resources for application execution. 


[![YARN architecture diagram][yarn-arch-alt]][yarn-arch-alt]

YARN consists of three core components:

- [ResourceManager](#toc-resourcemanager11) (one per cluster)
- [ApplicationMaster](#toc-applicationmaster12) (one per application)   
- [NodeManagers](#toc-nodemanagers13) (one per node)  

<div id="Glossary"></div>

### Caution, overloaded terms ahead

YARN uses some very common terms in uncommon ways. For example, when most people hear "container", they think [Docker]. In the Hadoop ecosystem, it takes on a new meaning: a _Resource Container (RC)_ represents a collection of physical resources. It is an abstraction used to bundle resources into distinct, allocatable units.

"Application" is another overloaded term—in YARN, an _application_ represents a set of tasks that are to be executed together. Application in YARN is synonymous with MapReduce's _job_ concept.

<div id="ResourceManager"></div>

### ResourceManager
The ResourceManager is the rack-aware master node in YARN. It is responsible for taking inventory of available resources and runs several critical services, the most important of which is the Scheduler.

#### Scheduler
The Scheduler component of the YARN ResourceManager allocates resources to running applications. It is a pure scheduler in that it does not monitor or track application status or progress. As it performs no monitoring, it cannot guarantee that tasks will restart should they fail.

As of Hadoop 2.7.2, YARN supports several scheduler policies: the [CapacityScheduler], the [FairScheduler], and the FIFO (first in first out) Scheduler. The default scheduler varies by Hadoop distribution, but no matter the policy used, the Scheduler allocates resources by assigning containers (bundles of physical resources) to the requesting ApplicationMaster.

<!-- ![Yarn container](http://simplejoys.typepad.com/my_weblog/images/yarn_holder_homemade_version.jpg)  
_A YARN container_ -->


<div id="ApplicationMaster"></div>

### ApplicationMaster
Each application running on Hadoop has its own dedicated ApplicationMaster instance. This instance lives in its own, separate container on one of the nodes in the cluster. Each application's ApplicationMaster periodically sends heartbeat messages to the ResourceManager, as well as requests for additional resources, if needed. Additional resources are granted by the ResourceManager through the assignment of Container Resource leases, which serve as reservations for containers on NodeManagers.

The ApplicationMaster oversees the execution of an application over its full lifespan, from requesting additional containers from the ResourceManger, to submitting container release requests to the NodeManager.

<div id="NodeManagers"></div>

### NodeManagers
The NodeManager is a per-node agent tasked with overseeing containers throughout their lifecycles, monitoring container resource usage, and periodically communicating with the ResourceManager. 


Conceptually, NodeManagers are much like TaskTrackers in earlier versions of Hadoop. Whereas TaskTrackers used a fixed number of map and reduce _slots_ for scheduling, NodeManagers have a number of dynamically created, arbitrarily-sized Resource Containers (RCs). Unlike slots in MR1, RCs can be used for map tasks, reduce tasks, or tasks from other frameworks. 

### Executing applications with YARN

[![YARN application execution diagram][yarn-exec-flow]][yarn-exec-flow]

Typical application execution with YARN follows this flow:

1. Client program submits the MapReduce application to the ResourceManager, along with information to launch the application-specific ApplicationMaster.
2. ResourceManager negotiates a container for the ApplicationMaster and launches the ApplicationMaster.
3. ApplicationMaster boots and registers with the ResourceManager, allowing the original calling client to interface directly with the ApplicationMaster.
4. ApplicationMaster negotiates resources (resource containers) for client application.
5. ApplicationMaster gives the container launch specification to the NodeManager, which launches a container for the application.
6. During execution, client polls ApplicationMaster for application status and progress.
7. Upon completion, ApplicationMaster deregisters with the ResourceManager and shuts down, returning its containers to the resource pool.

## ZooKeeper
Apache ZooKeeper is a popular tool used for coordination and synchronization of distributed systems. Since Hadoop 2.0, ZooKeeper has become an essential service for Hadoop clusters, providing a mechanism for enabling high-availability of former single points of failure, specifically the [HDFS NameNode](#toc-ha-namenode-service4) and [YARN ResourceManager](#toc-resourcemanager11).

<div id="HDFS-ZooKeeper"></div>

### HDFS and ZooKeeper

[![NameNode HA with ZooKeeper diagram][namenode-ha]][namenode-ha]

In previous versions of Hadoop, the NameNode represented a single point of failure—should the NameNode fail, the entire HDFS cluster would become unavailable as the metadata containing the file-to-block mappings would be lost.

Hadoop 2.0 brought many improvements, among them a [high-availability NameNode service](#toc-ha-namenode-service4). When ZooKeeper is used in conjunction with QJM or NFS, it [enables automatic failover][zookeeper-failover].

Automatic NameNode failover requires two components: a ZooKeeper quorum, and a ZKFailoverController (ZKFC) process running on each NameNode. The NameNode and Standby NameNodes maintain persistent sessions in ZooKeeper, with the NameNode holding a special, ephemeral "lock" [znode][znode] (the equivalent of a file or directory, in a regular file system); if the NameNode does not maintain contact with the ZooKeeper ensemble, its session is expired, triggering a failover (handled by ZKFC).

ZKFailoverController is a process that runs alongside the NameNode and Standby NameNodes, periodically checking the health of the node it is running on. On healthy nodes, ZKFC will try to acquire the lock znode, succeeding if no other node holds the lock (which means the primary NameNode has failed). Once the lock is acquired, the new NameNode transitions to the active NameNode.

[znode]: https://zookeeper.apache.org/doc/r3.1.2/zookeeperProgrammers.html#sc_zkDataModel_znodes

<div id="YARN-ZooKeeper"></div>

### YARN and ZooKeeper

[![ResourceManager HA with ZooKeeper diagram][resource-manager-ha]][resource-manager-ha]

When YARN was initially created, its ResourceManager represented a single point of failure—if NodeManagers lost contact with the ResourceManager, all jobs in progress would be halted, and no new jobs could be assigned.

Hadoop 2.4 improved YARN's resilience with the release of the ResourceManager high-availability feature. The new feature incorporates ZooKeeper to allow for automatic failover to a standby ResourceManager in the event of the primary's failure.

Like HDFS, YARN uses a similar, ZooKeeper-managed lock to ensure only one ResourceManager is active at once. Unlike HDFS, YARN's automatic failover mechanism does not run as a separate process—instead, its [ActiveStandbyElector] service is part of the ResourceManager process itself. Like ZKFailoverController, the ActiveStandbyElector service on each ResourceManager continuously vies for control of an ephemeral znode, _ActiveStandbyElectorLock_. Because the node is ephemeral, if the currently active RM allows the session to expire, the RM that successfully acquires a lock on the ActiveStandbyElectorLock will automatically be promoted to the active state. 

## From theory, to practice
In this post, we’ve explored all the core components found in a standard Hadoop cluster. 

[Read on][Part 2] to the next article in this series for an examination of Hadoop's key performance metrics and health indicators.

## Acknowledgments 

Thanks to [Ian Wrigley][ian-twit], Director of Education Services at [Confluent][confluent], for generously sharing their Hadoop expertise for this article.

[ian-twit]: https://twitter.com/iwrigley
[confluent]: http://www.confluent.io/

_Source Markdown for this post is available [on GitHub][markdown]. Questions, corrections, additions, etc.? Please [let us know][issues]._

[]: Links

[ActiveStandbyElector]: https://johnjianfang.blogspot.com/2015/03/hadoop-two-ha-activestandbyelector.html
[CapacityScheduler]: http://hadoop.apache.org/docs/current/hadoop-yarn/hadoop-yarn-site/CapacityScheduler.html
[Docker]: https://www.datadoghq.com/blog/the-docker-monitoring-problem/

[FairScheduler]: http://hadoop.apache.org/docs/current/hadoop-yarn/hadoop-yarn-site/FairScheduler.html
[federation-jira]: https://issues.apache.org/jira/browse/HDFS-1052
[ha-with-nfs]: https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HDFSHighAvailabilityWithNFS.html
[ha-with-qjm]:https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HDFSHighAvailabilityWithQJM.html
[hadoop-ecosystem]: https://hadoopecosystemtable.github.io/
[HCFS]: https://wiki.apache.org/hadoop/HCFS
[mapreduce-paper]: https://static.googleusercontent.com/media/research.google.com/en//archive/mapreduce-osdi04.pdf
[NameNode-fencing]: https://hadoop.apache.org/docs/r2.7.2/hadoop-project-dist/hadoop-hdfs/HDFSHighAvailabilityWithNFS.html
[powered-by]: https://wiki.apache.org/hadoop/PoweredBy
[Spark]: https://spark.apache.org/
[Tez]: https://tez.apache.org/
[zookeeper-failover]: https://hadoop.apache.org/docs/r2.7.2/hadoop-project-dist/hadoop-hdfs/HDFSHighAvailabilityWithQJM.html#Automatic_Failover

[]: Images

[hdfs-arch]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-07-hadoop/hdfs_architecture.jpg

[mapreduce-wordcount]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-07-hadoop/hadoop_diagram1-3.png

[namenode-federation-diagram]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-07-hadoop/namenode-federation-diagram.png
[namenode-ha]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-07-hadoop/hadoop_diagram7.png

[qjm-diagram]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-07-hadoop/hadoop_diagram2.png

[resource-manager-ha]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-07-hadoop/hadoop_diagram6-1.png

[secondary-nn-arch]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-07-hadoop/hadoop_diagram4.png

[vanilla]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-07-hadoop/hadoop_diagram3.png

[yarn-arch-alt]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-07-hadoop/hadoop_diagram8.png

[yarn-exec-flow]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-07-hadoop/hadoop_diagram9-1.png

[yarn-ha]: http://blog.cloudera.com/wp-content/uploads/2014/05/Client_Failover.png


[Part 1]: https://www.datadoghq.com/blog/hadoop-architecture-overview/
[Part 2]: https://www.datadoghq.com/blog/monitor-hadoop-metrics/
[Part 3]: https://www.datadoghq.com/blog/collecting-hadoop-metrics/
[Part 4]: https://www.datadoghq.com/blog/monitor-hadoop-metrics-datadog/

[markdown]: https://github.com/DataDog/the-monitor/blob/master/hadoop/hadoop_architecture_overview.md
[issues]: https://github.com/DataDog/the-monitor/issues
