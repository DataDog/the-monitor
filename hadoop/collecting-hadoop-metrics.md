# How to collect Hadoop metrics


*This post is part 3 of a 4-part series on monitoring Hadoop health and performance. [Part 1](/blog/hadoop-architecture-overview/) gives a general overview of Hadoop's architecture and subcomponents, [Part 2](/blog/monitor-hadoop-metrics/) dives into the key metrics to monitor, and [Part 4](/blog/monitor-hadoop-metrics-datadog/) explains how to monitor a Hadoop deployment with Datadog.*

If you’ve already [read our guide](/blog/monitor-hadoop-metrics/) to key Hadoop performance metrics, you’ve seen that Hadoop provides a vast array of metrics on job execution performance, health, and resource utilization.

In this post we'll step through several different ways to access those metrics. We'll show you how to collect metrics from core Hadoop components (HDFS, MapReduce, YARN), as well as from ZooKeeper, using standard development tools as well as specialized tools like Apache Ambari and Cloudera Manager.

Collecting HDFS metrics
-----------------------


HDFS emits metrics from two sources, the [NameNode](/blog/hadoop-architecture-overview/#hdfs-architecture) and the [DataNodes](/blog/hadoop-architecture-overview/#hdfs-architecture), and for the most part each metric type must be collected at the point of origination. Both the NameNode and DataNodes emit metrics over an HTTP interface as well as via JMX.



-   [Collecting NameNode metrics via API](#namenode-http-api)
-   [Collecting DataNode metrics via API](#datanode-http-api)
-   [Collecting HDFS metrics via JMX](#namenode-and-datanode-metrics-via-jmx)





#### NameNode HTTP API


The NameNode offers a summary of health and performance metrics through an easy-to-use web UI. By default, the UI is accessible via port 50070, so point a web browser at: `http://<namenodehost>:50070`

{{< img src="hadoop-yarn-stats-dfshealth.png" alt="HDFS summary image" popup="true" size="1x" >}}

While a summary is good to have, it is likely you will want to drill deeper into the metrics mentioned in [part two of this series](/blog/monitor-hadoop-metrics/); to see all the metrics, point your browser to `http://<namenodehost>:50070/jmx`, which will result in JSON output like this:


    {      
        "beans" : [ {   
          "name" : "java.lang:type=Memory",      
          "modelerType" : "sun.management.MemoryImpl",      
          "ObjectPendingFinalizationCount" : 0,      
          "HeapMemoryUsage" : {
            "committed" : 241172480,
            "init" : 262144000,
            "max" : 241172480,
            "used" : 110505832
          },
          "NonHeapMemoryUsage" : {
            "committed" : 136773632,
            "init" : 136773632,
            "max" : 318767104,
            "used" : 35047040
          },
          "Verbose" : true,
          "ObjectName" : "java.lang:type=Memory"
        }, {
          "name" : "java.lang:type=GarbageCollector,name=ConcurrentMarkSweep",
          "modelerType" : "sun.management.GarbageCollectorImpl",
          "LastGcInfo" : null,
          "CollectionCount" : 0,
          "CollectionTime" : 0,
          "Valid" : true,
          "MemoryPoolNames" : [ "Par Eden Space", "Par Survivor Space", "CMS Old Gen", "CMS Perm Gen" ],
          "Name" : "ConcurrentMarkSweep",
          "ObjectName" : "java.lang:type=GarbageCollector,name=ConcurrentMarkSweep" 
        }, {
          "name" : "java.nio:type=BufferPool,name=mapped",
          "modelerType" : "sun.management.ManagementFactoryHelper$1",
          "TotalCapacity" : 2144,
          "MemoryUsed" : 2144,
          "Name" : "mapped",
          "Count" : 1,
          "ObjectName" : "java.nio:type=BufferPool,name=mapped"
        }, {
          "name" : "java.lang:type=Compilation",
          "modelerType" : "sun.management.CompilationImpl",
          "CompilationTimeMonitoringSupported" : true,
          "TotalCompilationTime" : 9808,
          "Name" : "HotSpot 64-Bit Tiered Compilers",
          "ObjectName" : "java.lang:type=Compilation"
        }, {
          "name" : "java.lang:type=MemoryPool,name=Par Eden Space",
          "modelerType" : "sun.management.MemoryPoolImpl",
          "Valid" : true,
          "Usage" : {
            "committed" : 167772160,
            "init" : 167772160,
            "max" : 167772160,
            "used" : 95843104
          },
          "PeakUsage" : {
            "committed" : 167772160,
            "init" : 167772160,
            "max" : 167772160,
            "used" : 167772160
          },
      [...]




You can also filter by specific MBeans, like so:

    http://<namenodehost>:50070/jmx?qry=java.lang:type=Memory

