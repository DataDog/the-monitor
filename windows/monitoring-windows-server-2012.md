# Monitoring Windows Server 2012


*This post is part 1 of a 3-part series on monitoring the health and performance of the Windows operating system. [Part 2](https://datadoghq.com/blog/collect-windows-server-2012-metrics) details how to monitor Windows Server 2012 natively with a variety of tools, and [Part 3](https://datadoghq.com/blog/monitoring-windows-server-2012-datadog) explains how to monitor Windows with Datadog. For an in-depth webinar and Q&A session based on this series, check out this [slide deck][slides] and [video][webinar-video].*

[slides]: http://www.slideshare.net/DatadogSlides/lifting-the-blinds-monitoring-windows-server-2012
[webinar-video]: https://vimeo.com/199077503/ce3175a2f5

A window into Windows performance
---------------------------------


Operating systems monitor resources continuously in order to effectively schedule processes. However, surfacing that data for your own monitoring or analytics is not always easy. Fortunately, the Windows Server family of operating systems offer a wealth of operational data that you can access through a number of channels. To help make your Windows infrastructure observable, you need to track several types of data from Windows Server 2012:



-   [Performance counters](#performance-countersmetrics)
-   [Events](#events)
-   [Services](#services)



A few notes about terminology: In this series, we use the term "Windows" to reference Windows Server 2012 R2 specifically, though many of the performance counters and events discussed in this series are available in other Windows Server versions. And we'll characterize metrics as "work" or "resource" metrics—for background on this distinction, refer to our [Monitoring 101 posts](/blog/monitoring-101-collecting-data/) on metric collection and alerting.



### Performance counters/metrics


Windows exposes a huge number of metrics (more than 15,000 on a fresh install) as so-called [performance counters](https://msdn.microsoft.com/en-us/library/windows/desktop/aa371643(v=vs.85).aspx). Key performance counters can be divided into four groups:



-   [CPU](#cpu-metrics)
-   [Memory](#memory-metrics)
-   [Disk](#disk-metrics)
-   [Network](#network-metrics)



The lists provided below provide a good foundation to get started monitoring Windows Server, no matter if your box is a file server, DNS server, Active Directory Domain Controller, or otherwise. Though many of these metrics are not *immediately* actionable, taken in aggregate, they provide a clear view of the state of the system at a point in time, which is invaluable when performing root cause analysis or troubleshooting. Of course, depending on your use case, there may be additional performance counters to monitor.



#### CPU metrics




<table>
<thead>
<tr class="header">
<th>WMI Class</th>
<th>Property name</th>
<th>Description</th>
<th><a href="/blog/monitoring-101-collecting-data/">Metric Type</a></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Win32_PerfFormattedData_PerfOS_Processor</td>
<td>PercentProcessorTime</td>
<td>Percentage of time CPU is performing work</td>
<td>Resource: Utilization</td>
</tr>
<tr class="even">
<td>Win32_PerfFormattedData_PerfProc_Thread</td>
<td>ContextSwitchesPersec</td>
<td>Number of times the processor switched to a new thread</td>
<td>Other</td>
</tr>
<tr class="odd">
<td>Win32_PerfFormattedData_PerfOS_System</td>
<td>ProcessorQueueLength</td>
<td>Number of threads waiting on a processor</td>
<td>Resource: Saturation</td>
</tr>
<tr class="even">
<td>Win32_PerfFormattedData_PerfOS_Processor</td>
<td>DPCsQueuedPersec</td>
<td>Number of lower-priority tasks deferred due to interrupts</td>
<td>Resource: Saturation</td>
</tr>
<tr class="odd">
<td>Win32_PerfFormattedData_PerfOS_Processor</td>
<td>PercentPrivilegedTime PercentDPCTime PercentInterruptTime</td>
<td>Percentage of time CPU spent in privileged mode/deferred procedure calls/interrupts</td>
<td>Resource: Utilization</td>
</tr>
</tbody>
</table>



##### PercentProcessorTime

Prolonged periods of 100 percent CPU usage indicates a resource bottleneck. Correlating CPU usage with the length of the processor queue can help you determine if your workload is too much for the machine. High CPU usage alongside spikes in processor queue length imply a lack of adequate compute resources for the operating system to complete the work it's tasked with.


##### ContextSwitchesPersec

A [context switch](https://msdn.microsoft.com/en-us/library/windows/desktop/ms682105(v=vs.85).aspx) occurs when a processor has completed the execution of a task (or is interrupted before completion) and switches to a new one. A context switch is an expensive operation that involves the following steps, as outlined in [Microsoft's reference guide](https://msdn.microsoft.com/en-us/library/windows/desktop/ms682105(v=vs.85).aspx):

1. Save the context of the just-completed thread
2. Push the completed thread down to the end of the queue associated with its priority level
3. Find the highest-priority queue containing executable threads
4. Pop the thread at the head of that queue, load its context, and execute it

A high rate of context switching typically indicates resource contention and points to a CPU bottleneck. Though if the context switches are occurring due to some demanding hardware device (with a corresponding increase in the rate of interrupts), the problem could lie in its driver.

Microsoft offers [a few tips here](https://technet.microsoft.com/en-us/library/cc938642.aspx) on optimizing workloads to minimize context switching, among other useful tidbits.

##### ProcessorQueueLength

Threads in the processor queue are ready to run but can't, due to another thread running on the processor. Queues with sustained element counts greater than 2 are indicative of a bottleneck.

Keep in mind that queues are likely to increase in size during periods of high processor activity, but queues can also develop when utilization is [well below 90 percent](https://technet.microsoft.com/en-us/library/cc940375.aspx).

##### DPCsQueuedPersec

{{< img src="windows-server-2012-monitoring-dpcqueue.png" alt="Windows Server 2012 monitoring - DPC queue" popup="true" >}}

[Deferred procedure calls](https://en.wikipedia.org/wiki/Deferred_Procedure_Call) (DPCs) provide a low-priority interrupt mechanism on Windows systems. Understanding deferred procedure calls requires a brief explanation of system [interrupts](https://en.wikipedia.org/wiki/Interrupt) in an operating system context.

Hardware requirements demand real-time, unfettered access to the CPU in order to ensure that high-priority work (like accepting keyboard input) is performed when it is needed. Interrupts provide a means by which devices can *interrupt* the processor and force it to perform the requested operation (triggering the processor to perform a [context switch](#contextswitchespersec)). Some work from devices may be put off until later, but still must be accomplished in a timely manner. Enter DPCs.

Through DPCs, real-time processes like device drivers can schedule lower-priority tasks to be completed after higher-priority interrupts are handled. DPCs are created by the kernel, and can only be called by [kernel mode programs](https://msdn.microsoft.com/en-us/library/windows/hardware/ff554836(v=vs.85).aspx).

A high or near-constant number of DPCs could point to issues with low-level system software. An unused but buggy sound driver could be the culprit, for example. For more information on finding the offending service or program, check out [part two](https://datadoghq.com/blog/collect-windows-server-2012-metrics) of this series.

##### PercentPrivilegedTime, PercentDPCTime, and PercentInterruptTime

This trio of percentages offers insight into high CPU usage. PrivilegedTime is the time the CPU spends processing instructions from kernel-mode programs, DPCTime is the time the CPU spends processing deferred procedure calls, and InterruptTime is the time the CPU spends handling interrupts. It should be noted that the processor regularly issues interrupts to switch context to a new thread, so you should expect some level of background noise for this metric.

Systems that are spending [30 percent or more](https://blogs.technet.microsoft.com/perfguide/2010/09/28/user-mode-versus-privileged-mode-processor-usage/) of their time processing privileged instructions should be inspected. First, examine DPCTime and InterruptTime; if either value exceeds 20 percent, a hardware issue is likely to be the culprit. You can use a tool like [xperf](https://msdn.microsoft.com/en-us/library/windows/hardware/hh162920.aspx) (bundled with Windows) to dig deeper into the offending process.



#### Memory metrics




<table>
<thead>
<tr class="header">
<th>WMI Class</th>
<th>Property name</th>
<th>Description</th>
<th><a href="/blog/monitoring-101-collecting-data/">Metric Type</a></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Win32_PerfFormattedData_PerfOS_Memory</td>
<td>AvailableMBytes</td>
<td>Amount of physical memory available (MB)</td>
<td>Resource: Utilization</td>
</tr>
<tr class="even">
<td>Win32_PerfFormattedData_PerfOS_Memory</td>
<td>CommittedBytes</td>
<td>Amount of virtual memory (in bytes) committed</td>
<td>Resource: Utilization</td>
</tr>
<tr class="odd">
<td>Win32_PerfFormattedData_PerfOS_Memory</td>
<td>PoolNonpagedBytes</td>
<td>Amount of memory (in bytes) excluded from the paging pool</td>
<td>Resource: Utilization</td>
</tr>
<tr class="even">
<td>Win32_PerfFormattedData_PerfOS_Memory</td>
<td>PageFaultsPersec</td>
<td>Page faults per second</td>
<td>Resource: Saturation</td>
</tr>
<tr class="odd">
<td>Win32_PerfFormattedData_PerfOS_Memory</td>
<td>PagesInputPersec</td>
<td>Number of pages retrieved from disk (per second)</td>
<td>Other</td>
</tr>
<tr class="even">
<td>Win32_PerfFormattedData_PerfOS_PagingFile</td>
<td>PercentUsage</td>
<td>Percent of paging file used</td>
<td>Resource: Utilization</td>
</tr>
</tbody>
</table>



##### AvailableMBytes

It is important to keep an eye on the amount of available memory, as contention for RAM will inevitably lead to paging and performance degradation. To keep your machine humming along, make sure it has an ample amount of RAM for your workloads. Consistently low memory availability can lead to segmentation faults and other serious issues. Possible remedies include increasing the amount of physical memory in the system and, if appropriate, enabling [memory page combining](https://blogs.technet.microsoft.com/clinth/2012/11/29/memory-combining-in-windows-8-and-windows-server-2012/).

##### CommittedBytes

CommittedBytes represents the actual demand for virtual memory. Memory that has been allocated, whether in physical RAM or the page file, counts towards the CommittedBytes total. When the number of CommittedBytes approaches or exceeds the physical memory of the system, paging to disk (and its associated performance impacts) is unavoidable.

If the value of CommittedBytes converges on the maximum memory of the system, then you are running out of available memory and must either increase the size of the page file or increase the amount of physical memory available.

In general, if this metric is trending upward increasing without leveling off, you should investigate.

##### PageFaultsPersec

Page faults occur when a process requests a [page](https://en.wikipedia.org/wiki/Paging) in memory that can't be found. There are two types of page faults: *soft* and *hard*. A *soft page fault* indicates that the page was found elsewhere in memory. A *hard page fault* indicates that the page had to be retrieved from disk. Systems can tolerate a fairly high number of soft page faults, though hard page faults often result in delays.

{{< img src="windows-server-2012-monitoring-pagefaults.png" alt="Windows Server 2012 monitoring - page fault spike!" popup="true" >}}

The PageFaultsPersec metric tracks the number of page faults, both soft and hard. To focus on hard page faults, look for high values of *pages input per second* (outlined below). If you identify a surge in hard page faults, you should either increase system memory, or else [decrease the system cache size](https://serverfault.com/questions/325277/windows-server-2008-r2-metafile-ram-usage/527466#527466) to free up memory for paging.

Monitoring the working set of process memory allows you to correlate a specific process's memory usage with page faulting. Under heavy load, the operating system will continuously trim processes' working memory, resulting in frequent page faults. To narrow down the offending process, you can also correlate with page fault frequency by process (check the Win32_PerfFormattedData_PerfProc_Process object).

##### PoolNonpagedBytes

As mentioned above, the Windows kernel and hardware devices require the ability to preempt other threads to execute their time-sensitive work. Because of these strict requirements, devices and the kernel access physical memory directly, and not through virtual memory, as do user-mode processes.

This special pool of memory is not subject to paging to disk, due to the time requirements of its users. Normally, this is not an issue. But the special treatment of this pool means that problems with the components using this memory could be fatal for the system. Memory leaks in drivers that use the non-paged pool, for instance, could lock up the system entirely, as memory for user-mode processes is dumped to disk. Keeping an eye on this metric is useful for debugging memory leaks and other showstopping issues.

[Windows Event 2019](https://support.microsoft.com/en-us/kb/133384) ("Nonpaged Memory Pool Empty") will occur in the event of insufficient allocable memory. (Though the Microsoft reference page lists the cause as a TCP/IP sockets program continuously attempting to open a nonexistent socket, this event will also occur if the non-paged pool address space is exhausted.)

{{< img src="windows-server-2012-monitoring-pages-input.png" alt="Windows Server 2012 monitoring - Page reads and pages input" popup="true" >}}

##### PagesInputPersec

This metric reports the number of *pages* read from disk (as opposed to the number of *read operations*) to resolve hard page faults.

Recall that there are two types of page faults, and only hard page faults require fetching the page from disk. Tracking PagesInputPersec alongside PageFaultsPersec gives a clear view into the type of fault occurring. High values of the PagesInputPersec counter indicate hard page faults.

It is worth mentioning that when a hard page fault *does* occur, Windows attempts to retrieve multiple, contiguous pages into memory, to maximize the work performed by each read. This, in turn, can potentially increase a page fault's performance impact, as more disk bandwidth is consumed reading in potentially unneeded pages. All of this can potentially be avoided by putting your page file (see next section) on a separate physical (not logical) disk, or increasing the amount of RAM available to your system.

##### PercentUsage

The paging file is a "hidden" file in the Windows system folder, used to store infrequently accessed memory pages on disk to free up RAM for other things. If you are familiar with Linux, the page file is similar to the swap partition.

Because the paging file is located on disk, not only will reads/writes to it impact overall system performance, but it is also subject to fragmentation, which degrades system performance even further.

By default, Windows manages the page file, which means the size of the file can increase or decrease without any user input. However, some cases may warrant manual tweaking of the file size. For more information on tuning your page file size (and other potential optimizations), check out [Microsoft's documentation on page file tuning](https://support.microsoft.com/en-us/kb/2860880).



#### Disk metrics




<table>
<thead>
<tr class="header">
<th>WMI Class</th>
<th>Property name</th>
<th>Description</th>
<th><a href="/blog/monitoring-101-collecting-data/">Metric Type</a></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Win32_PerfFormattedData_PerfDisk_LogicalDisk</td>
<td>PercentFreeSpace</td>
<td>Percentage of disk space remaining</td>
<td>Resource: Utilization</td>
</tr>
<tr class="even">
<td>Win32_PerfFormattedData_PerfDisk_LogicalDisk</td>
<td>PercentIdleTime</td>
<td>Percentage of time disk was idle</td>
<td>Resource: Availability</td>
</tr>
<tr class="odd">
<td>Win32_PerfFormattedData_PerfDisk_LogicalDisk</td>
<td>AvgDisksecPerRead AvgDisksecPerWrite</td>
<td>Average time of a read/write operation (in seconds)</td>
<td>Work: Performance</td>
</tr>
<tr class="even">
<td>Win32_PerfFormattedData_PerfDisk_LogicalDisk</td>
<td>AvgDiskQueueLength</td>
<td>Average number of read/write requests (per disk) in queue</td>
<td>Resource: Saturation</td>
</tr>
<tr class="odd">
<td>Win32_PerfFormattedData_PerfDisk_LogicalDisk</td>
<td>DiskTransfersPersec</td>
<td>Rate of read/write operations on disk</td>
<td>Work: Throughput</td>
</tr>
<tr class="even">
<td>Win32_PerfFormattedData_PerfOS_Memory</td>
<td>CacheBytes</td>
<td>Size of file system cache in memory</td>
<td>Resource: Utilization</td>
</tr>
</tbody>
</table>



##### PercentFreeSpace

Maintaining ample free disk space is a necessity for any operating system. Beyond regular processes requiring disk, core system processes store logs and other kinds of data on disk. Windows will issue a warning if your available disk space drops below 15 percent, but you should alert on this metric to catch the smoke before the fire.

##### PercentIdleTime

This metric reports the percentage of time the disk was idle. If you are hosting your page file on a drive separate from the OS drive, you should *definitely* track and potentially alert on this metric, on both your primary drive and the page file's drive. Low values for idle time should be investigated; high I/O on the page file disk will translate to increased memory access times, which will be felt by any application whose memory is mapped to the paging file. Possible solutions include moving the paging file to an unused drive or a faster drive.

Beyond the paging file, performance of applications that make heavy use of the disk (like SQL Server, for example) will certainly suffer during prolonged periods of high I/O.

##### AvgDisksecPerRead and AvgDisksecPerWrite

This pair of metrics tracks the average amount of time taken for disk read/write operations. In general, values larger than about 30 milliseconds indicate relatively high latency, which can often be reduced by moving to faster disks. Depending on the role of your server, the acceptable threshold could be much lower—as low as 10 milliseconds if you are running Exchange Server or SQL Server.

##### AvgDiskQueueLength

The average disk queue length gives a running average of the number of read/write requests in the queue. This value is not a direct measurement of the disk queue at any given point in time; it is an estimate derived from (Disk Transfers/sec) \* (Disk secs/Transfer).



{{< img src="windows-server-2012-monitoring-disk-queue.png" alt="Windows Server 2012 monitoring - Disk queue" popup="true" caption="Look ma, no pending I/O">}}


Generally speaking, if the average disk queue length exceeds [2 \* (number of drives)](https://technet.microsoft.com/en-us/library/cc938625.aspx?f=255&MSPPError=-2147217396) for prolonged periods, a bottleneck is forming.


##### DiskTransfersPersec

If your server is hosting a demanding application, like SQL Server or Exchange, you will want to monitor your disk I/O rates. The DiskTransfersPersec metric is an aggregate of read (DiskReadsPersec) and write (DiskWritesPersec) activity, tagged by disk (and a total across all disks tagged with _Total). Sustained periods of high disk activity could lead to service degradation and system instability, especially when coupled with high RAM and page file use. Possible remedies include increasing the number of disks in use (*especially* if you're seeing a large number of ops in queue), using faster disks, increasing RAM reserved for file system cache (see below), and distributing the offending workload across more machines, if possible.

##### CacheBytes

The CacheBytes counter tracks the size, in bytes, of the portion of memory reserved as a file system cache. Whereas the paging file is used to store memory contents on disk, the file cache stores disk contents in RAM, for faster access.

{{< img src="windows-server-2012-monitoring-fs-cache.png" alt="Windows Server 2012 monitoring - File system cache" popup="true" >}}

Tuning the file cache size for optimal performance is a balancing act—if the cache is too small, access to files is slower; if the cache is too large, programs may end up with their memory paged to disk, slowing them down. By default, Windows takes care of this for you, allocating free RAM to be used for the file cache. However, your requirements may require manual tweaking of the file cache, for which you can use a tool like [CacheSet](http://technet.microsoft.com/en-us/sysinternals/bb897561.aspx).

It is worth mentioning that if you are opening many "large" files (larger than about one gigabyte), your issue may be caused by an issue in the accessing process, specifically, calling [CreateFile()](https://msdn.microsoft.com/en-us/library/windows/desktop/aa363858%28v=vs.85%29.aspx?f=255&MSPPError=-2147217396) with the FILE_FLAG_RANDOM_ACCESS flag set. Passing this flag to CreateFile causes the Cache Manager to keep previously viewed memory pages in the cache. When accessing files whose cumulative size exceeds the amount of physical memory, performance will suffer. See [KB 2549369](https://support.microsoft.com/en-us/kb/2549369) for more information.



#### Network metrics




<table>
<thead>
<tr class="header">
<th>WMI Class</th>
<th>Property name</th>
<th>Description</th>
<th><a href="/blog/monitoring-101-collecting-data/">Metric Type</a></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Win32_PerfFormattedData_Tcpip_NetworkInterface</td>
<td>BytesSentPersec BytesReceivedPersec</td>
<td>Network send/receive rate</td>
<td>Resource: Utilization</td>
</tr>
<tr class="even">
<td>Win32_PerfFormattedData_Tcpip_TCPv4</td>
<td>SegmentsRetransmittedPersec</td>
<td>IPv4 TCP retransmissions</td>
<td>Other</td>
</tr>
</tbody>
</table>



##### BytesSentPersec and BytesReceivedPersec

Taken together, these two metrics measure the total network throughput of a given network interface. With most consumer hardware shipping with NICs capable of 1 gigabit per second or more, it is unlikely that the network would be a bottleneck in all but the most extreme cases. [Microsoft documentation](https://technet.microsoft.com/en-us/library/cc302601.aspx) suggests that network saturation occurs when consuming more than 80 percent of the interface's bandwidth, amounting to 100 megabytes per second for a 1-Gbps link.

{{< img src="windows-server-2012-monitoring-net-throughput.png" alt="Windows Server 2012 monitoring - Network throughput" popup="true" >}}

Though unlikely to be the cause of performance issues, correlating network throughput with metrics from applications running on top of Windows (like IIS) could shed light on issues arising in those applications. In the event that you *are* saturating your network link, you may consider using a web cache for outbound traffic; otherwise you may need to increase your bandwidth (via your provider or through hardware upgrades).

##### SegmentsRetransmittedPersec

[TCP retransmissions](https://tools.ietf.org/html/rfc793) occur when a transmitted segment has not been acknowledged within the TCP timeout window, so the segment is re-sent.

TCP retransmissions occur frequently and are not errors, though their presence can be a sign of issues. Retransmissions are usually the result of network congestion, and most often are correlated with high bandwidth consumption. You should monitor this metric because excessive retransmissions could cause extensive delays in your applications. If the sender of the retransmits does not receive an acknowledgment of packets sent, it holds off on sending more packets (usually for about 1 second), adding delays that can compound congestion-related slowdowns.

If not caused by network congestion, the source of retransmits could be faulty network hardware. A low number of discarded packets in conjunction with a high rate of retransmissions could point to [excessive buffering](http://www.netcraftsmen.com/application-analysis-using-tcp-retransmissions-part-2/) as the culprit. Whatever the cause, you should track this metric to shed light on seemingly-random fluctuations in network application response times.



### Events


While performance counters provide a high-level overview of resource usage and performance, troubleshooting complex issues requires additional information on the sequence of events that occurred before or during the observed issue. By correlating performance counters with events from the Windows Event Log, metrics can be put in context with events across a network of hosts.

Windows Server 2012 has many event sources and, subsequently, many different event logs. (Our test environment, a fresh Windows Server 2012 installation on Microsoft Azure, had 245 separate event logs.) You can see the full list available on your system by navigating to the `%SystemRoot%\System32\Winevt\Logs` directory. The event logs that are pertinent to you will depend on what you are using your server for (Active Directory Domain Controller, DNS server, etc.).

{{< img src="windows-server-2012-monitoring-eventlog.png" alt="Windows Server 2012 monitoring - Event log snip" popup="true" caption="A sample of Application events streaming in real-time." >}}


In addition to monitoring those event logs important to your use case, the Application (Application.evtx), System (System.evtx) and Security (Security.evtx) logs will provide useful information to most Windows administrators. Below we will break down several important events, categorized by event log, and classified by log level. See [this reference](https://technet.microsoft.com/en-us/library/cc765981(v=ws.11).aspx) for a list of all event properties.




-   [System Events](#system-events)
-   [Application Events](#application-events)
-   [Security Events](#security-related-events)



#### System events




<table>
<thead>
<tr class="header">
<th>Event Log</th>
<th>Level</th>
<th>ID</th>
<th>Event Description</th>
<th>Source</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>System</td>
<td>Critical</td>
<td>41</td>
<td>Unexpected reboot</td>
<td>Kernel-Power</td>
</tr>
<tr class="even">
<td>System</td>
<td>Error</td>
<td>1001</td>
<td>Server rebooting from BugCheck</td>
<td><a href="https://msdn.microsoft.com/en-us/library/windows/hardware/hh994433(v=vs.85).aspx">BugCheck</a></td>
</tr>
</tbody>
</table>



##### System EventID: 41

This system event is logged when a system fails to cleanly shut down before rebooting. Power loss, a crash, or hung operating system are all common causes. Unless otherwise configured, Windows will reboot when it blue screens, so you probably want to alert on this event. If you see this event occur along with System event 1001 (see below), you can be sure the reboot was caused by a blue screen.

##### System EventID: 1001

When a system blue screens, an event is written to the System log with more information on the cause of failure ([returned as a hex value](https://msdn.microsoft.com/en-us/library/windows/hardware/hh994433(v=vs.85).aspx)), as well as the location of the memory dump generated at the time of the failure. By default, Windows will reboot when it blue screens, which means you may not notice an error occurred without peering into the event logs.

{{< img src="windows-server-2012-monitoring-bugcheck-irql-bsod.png" alt="Windows Server 2012 monitoring - IRQL Less or not equal" caption="Cause of this blue screen: a driver attempted to access a memory page that was not in memory (0x000000d1)" popup="true" >}}

Pinpointing the root cause of blue screens is very important—once one occurs, it is generally a sign of things to come. You definitely want to be aware of these events and should set an alert on their occurrence.



#### Application events


Application events give additional details on application failures and started services.



<table>
<thead>
<tr class="header">
<th>Event Log</th>
<th>Level</th>
<th>ID</th>
<th>Event Description</th>
<th>Source</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Application</td>
<td>Error</td>
<td>1000</td>
<td>App Error</td>
<td>Application Error</td>
</tr>
<tr class="even">
<td>Application</td>
<td>Error</td>
<td>1002</td>
<td>App Hang</td>
<td>Application Hang</td>
</tr>
</tbody>
</table>



##### Application EventID: 1000

Events in the Application event log with EventID 1000 indicate that an application error has occurred, which resulted in a crash. From time to time, core Windows applications and services may encounter errors and crash. This is not usually an issue; in most cases, Windows can restart the service and resume operation.

{{< img src="windows-server-2012-monitoring-application-event1000.png" alt="Windows Server 2012 monitoring - Application EventID 1000" popup="true" >}}

Because automatic restart is not always possible, however, you may want to alert on this event, depending on the application that crashed. If an application is continuously crashing, further investigation may be warranted.

##### Application EventID:1002

Hung applications occur when a user attempts to give input to a GUI, and the GUI does not update with the new input. Applications that repeatedly hang should be investigated; there could be an underlying issue causing the hang. An application suddenly and repeatedly hanging when it was previously working correctly can oftentimes be attributed to system changes, like a driver or firmware update. Correlating system changes with this event can shed light on the underlying causes of hung applications. Note that applications can only enter the hung state upon attempts at user interaction; Windows only becomes aware of a hung application when a user attempts to interact with it.



#### Security-related events


Important changes to users, groups, and other important features are logged to the Security Audit event log. Some of the more important events can be found below; for an exhaustive list of security audit events, see Microsoft's [documentation](https://www.microsoft.com/en-us/download/details.aspx?id=50034).

{{< img src="windows-server-2012-monitoring-failed-logon.png" alt="Windows Server 2012 monitoring - Failed logon EventID 4625" popup="true" caption="A failed logon attempt">}}


Should any of these events unexpectedly arise in the event log, swift action should be taken to verify the source of the changes and their legitimacy.



<table>
<thead>
<tr class="header">
<th>Event Log</th>
<th>Level</th>
<th>ID</th>
<th>Event Description</th>
<th>Source</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>System</td>
<td>Information</td>
<td><a href="https://serverfault.com/questions/743575/how-to-find-out-who-deleted-event-viewer-logs">104</a></td>
<td>Event log cleared</td>
<td>Microsoft-Windows-EventLog</td>
</tr>
<tr class="even">
<td>Security</td>
<td>Information</td>
<td><a href="https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventID=1102">1102</a></td>
<td>Audit log cleared</td>
<td>Microsoft-Windows-EventLog</td>
</tr>
<tr class="odd">
<td>System</td>
<td>Information</td>
<td><a href="https://technet.microsoft.com/en-us/itpro/windows/keep-secure/event-4719">4719</a></td>
<td>System audit policy modified</td>
<td>Microsoft-Windows-EventLog</td>
</tr>
<tr class="even">
<td>Security</td>
<td>Information</td>
<td><a href="https://technet.microsoft.com/en-us/itpro/windows/keep-secure/event-4740">4740</a></td>
<td>User account locked</td>
<td>Microsoft-Windows-Security-Auditing</td>
</tr>
<tr class="odd">
<td>Security</td>
<td>Information</td>
<td><a href="http://social.technet.microsoft.com/wiki/contents/articles/17049.event-id-when-a-user-is-added-or-removed-from-security-enabled-global-group-such-as-domain-admins-or-group-policy-creator-owners.aspx">4728</a>, <a href="https://technet.microsoft.com/en-us/itpro/windows/keep-secure/event-4732">4732</a>, <a href="http://social.technet.microsoft.com/wiki/contents/articles/17049.event-id-when-a-user-is-added-or-removed-from-security-enabled-global-group-such-as-domain-admins-or-group-policy-creator-owners.aspx">4756</a></td>
<td>User added to a security-enabled group</td>
<td>Microsoft-Windows-Security-Auditing</td>
</tr>
<tr class="even">
<td>Security</td>
<td>Information</td>
<td><a href="https://technet.microsoft.com/en-us/itpro/windows/keep-secure/event-4735">4735</a></td>
<td>Security-enabled group was modified</td>
<td>Microsoft-Windows-Security-Auditing</td>
</tr>
<tr class="odd">
<td>Security</td>
<td>Information</td>
<td><a href="https://technet.microsoft.com/en-us/itpro/windows/keep-secure/event-4724?f=255&amp;MSPPError=-2147217396">4724</a></td>
<td>Password reset attempt</td>
<td>Microsoft-Windows-Security-Auditing</td>
</tr>
<tr class="even">
<td>Security</td>
<td>Information</td>
<td><a href="https://answers.microsoft.com/en-us/windows/forum/windows_vista-security/where-can-i-find-the-full-list-of-failure-reasons/d0269426-2183-4d99-8af0-cc009dee6658">4625</a></td>
<td>An account failed to logon</td>
<td>Microsoft-Windows-Security-Auditing</td>
</tr>
<tr class="odd">
<td>Security</td>
<td>Information</td>
<td><a href="https://technet.microsoft.com/en-us/itpro/windows/keep-secure/event-4648?f=255&amp;MSPPError=-2147217396">4648</a></td>
<td>A logon was attempted using explicit credentials</td>
<td>Microsoft-Windows-Security-Auditing</td>
</tr>
</tbody>
</table>





### Services


Monitoring Windows services serves two purposes: ensuring that essential services remain up, and enabling the discovery and disabling of non-essential services.

{{< img src="windows-server-2012-monitoring-services-snap-in.png" alt="Windows Server 2012 monitoring -Services Snap-in" caption="Service Management via the Services.msc snap-in" popup="true" >}}

 

[Windows services](https://msdn.microsoft.com/en-us/library/d56de412(v=vs.100).aspx) are long-running, (typically) [background processes](https://en.wikipedia.org/wiki/Daemon_(computing)#Implementation_in_MS-DOS_and_Microsoft_Windows), similar to Unix-like [daemons](https://en.wikipedia.org/wiki/Daemon_(computing)). The services you monitor depend on your use case and the specific [role of the server](https://technet.microsoft.com/en-us/library/hh831669(v=ws.11).aspx) in question. The list below provides a good starting point, containing a mix of essential and common services that are relatively role-neutral.

Most of the following services are essential to core Windows functionality. In [part 2](https://datadoghq.com/blog/collect-windows-server-2012-metrics) of this series, we will explain how to use Windows-native tools to ensure that key services are up and running,



<table>
<thead>
<tr class="header">
<th>Display Name</th>
<th>Service Name</th>
<th>Description (<a href="https://technet.microsoft.com/en-us/library/dd349799(v=ws.10).aspx">source</a>)</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Base Filtering Engine</td>
<td>BFE</td>
<td>Manages firewall and <a href="https://en.wikipedia.org/wiki/IPsec">Internet Protocol security</a> policies</td>
</tr>
<tr class="even">
<td>Background Tasks Infrastructure Service</td>
<td>BrokerInfrastructure</td>
<td>Provides access control for background task execution</td>
</tr>
<tr class="odd">
<td>Cryptographic Services</td>
<td>CryptSvc</td>
<td>Provides three management services: Catalog Database Service, which verifies signatures of system files and new software; Protected Root Service, which controls <a href="https://msdn.microsoft.com/en-us/windows/hardware/drivers/install/trusted-root-certification-authorities-certificate-store?f=255&amp;MSPPError=-2147217396">Trusted Root Certification Authority</a> certificates; and Automatic Root Certificate Update Service, which retrieves root certificates from Windows Update</td>
</tr>
<tr class="even">
<td>DCOM Server Process Launcher</td>
<td>DcomLaunch</td>
<td>Launches Component Object Model (COM) and Distrbuted Component Object Model (DCOM) servers</td>
</tr>
<tr class="odd">
<td>Diagnostic Policy Service</td>
<td>DPS</td>
<td>Enables system diagnostics and issue resolution for Windows components</td>
</tr>
<tr class="even">
<td>Windows Event Log</td>
<td>EventLog</td>
<td>Manages events and event logging. Supports logging, querying, subscribing to, and archiving of events</td>
</tr>
<tr class="odd">
<td>COM+ Event System</td>
<td>EventSystem</td>
<td>Supports System Event Notification Service (SENS), which provides automatic distribution of events to subscribing COM components</td>
</tr>
<tr class="even">
<td>Group Policy Client</td>
<td>gpsvc</td>
<td>Applies settings configured by Group Policy</td>
</tr>
<tr class="odd">
<td>Windows Firewall</td>
<td>MpsSvc</td>
<td>Native firewall to prevent unauthorized network access</td>
</tr>
<tr class="even">
<td>Performance Logs &amp; Alerts</td>
<td>pla</td>
<td>Collects, logs, and alerts on performance data from local or remote computers</td>
</tr>
<tr class="odd">
<td>Task Scheduler</td>
<td>Schedule</td>
<td>Hosts system-critical scheduled tasks and enables user-configurable scheduled tasks</td>
</tr>
<tr class="even">
<td>System Events Broker</td>
<td>SystemEventsBroker</td>
<td>Coordinates background work execution for <a href="https://en.wikipedia.org/wiki/Windows_Runtime">WinRT</a> applications</td>
</tr>
<tr class="odd">
<td>Remote Desktop Services</td>
<td>TermService</td>
<td>Allows remote users to connect interactively to the local machine</td>
</tr>
<tr class="even">
<td>Windows Management Instrumentation</td>
<td>Winmgmt</td>
<td>Provides a standard interface for accessing management information from the operating system, devices, applications and services</td>
</tr>
<tr class="odd">
<td>Windows Remote Management (WS-Management)</td>
<td>WinRM</td>
<td>Provides remote access to Windows Management Instrumentation (WMI) data and enables event collection</td>
</tr>
<tr class="even">
<td>WMI Performance Adapter</td>
<td>wmiApSrv</td>
<td>Provides performance library information from WMI providers</td>
</tr>
</tbody>
</table>



Time to collect
---------------


In this post we’ve explored many of the key metrics and events you should monitor to keep tabs on the health and performance of your Windows 2012 servers.

Most of the metrics and events covered in this post should be relevant to general use. Given the number of roles a Windows server can perform, however, over time you will likely identify additional metrics that are particularly relevant to your workloads and users.

[Read on](https://datadoghq.com/blog/collect-windows-server-2012-metrics) for a comprehensive guide to collecting all of the metrics described in this article, using standard tools bundled with Windows Server 2012.

