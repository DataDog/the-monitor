---
authors:
- email: maxim.brown@datadoghq.com
  image: brown-maxim.jpg
  name: Maxim Brown
  twitter: maximybrown
blog/category:
- series metrics
blog/tag:
- monitoring
- AWS
- alerts
- performance
date: 2018-04-06
description: "Identify and monitor key metrics for your Amazon EBS volumes."
draft: false
image: ebs-hero-one.png
meta_title: Key metrics for Amazon EBS monitoring
preview_image: ebs-hero-one.png
header_video:
    mp4: superhero_EBS_prores_24b.mp4
    no_loop: false
    no_autoplay: false
    stop_time: 0
slug: amazon-ebs-monitoring
technology: aws ebs
title: Key metrics for Amazon EBS monitoring
series: amazon-ebs-monitoring
---

## What is Amazon EBS?
Amazon Elastic Block Storage (EBS) is persistent block-level storage as a service that works in conjunction with [EC2 instances](/blog/ec2-monitoring). Unlike EC2 instance store volumes, which are ephemeral and lose any data once the instance is destroyed, EBS volumes maintain their state when stopped or detached from an instance. You can connect multiple EBS volumes to a single instance, though they must all be within the same availability zone.

{{< img src="amazon-ebs-dashboard-rev.png" alt="Amazon EBS monitoring dashboard" wide="true" popup="true" >}}

In addition to their persistent nature, EBS volumes provide redundancy and data backup for your system with the ability to take [snapshots][snapshots] of the volume, which are then saved to [S3 buckets][s3]. Snapshots can be copied and transferred across AWS regions, and they can be used to launch immediately accessible replicas of the volume. This lets you create and maintain duplicate datasets or migrate application infrastructure to multiple locations.

### Staying connected
EBS volumes are virtualized, networked drives; they are not physical disks attached to an instance’s host computer. Disk performance is thus tightly linked to network performance and throughput. Some EC2 instance types do not separate EBS bandwidth from general network activity. In that case, if the instance is devoting significant bandwidth to other IP traffic, such as serving static content to a user on the internet, it may result in a throttling of disk performance as less bandwidth is available for the EBS volumes.

Many EC2 instance types are [EBS-optimized][ebs-optimized], often by default with no additional charge. EBS-optimized instances provide 425 to 14,000 Mbps (depending on the instance type) of dedicated bandwidth to EBS volumes, separate from the instance’s other network activity. AWS guarantees certain levels of baseline and burst performance of EBS-optimized volumes 99 percent of the time over a given year. Other instance types provide [enhanced networking][enhanced-networking] to help prevent network bottlenecks. But, these instances use the same network for all communication, which makes steady network performance even more important.

When planning out your EC2 instances and attached volumes, it’s important to understand their [network configuration][ec2-config] and whether they match up well together. If multiple high-throughput EBS volumes are attached to an instance with limited bandwidth capacity, the drives will never reach their maximum capacity. As an example, an r4.large instance has a maximum bandwidth of 425 Mbps, or around 53 MB/s of throughput. Regardless of the number or size of the EBS volumes you attach to it, the instance isn’t capable of providing higher throughput than that, and you would be paying for unusable capacity.

### Disk types
EBS volumes come in a [few flavors][volume-types], which have different characteristics. Understanding your workload requirements and using the most appropriate volume types can make a great deal of difference both in terms of your application performance and usage charges. The two primary categories are solid-state drives (SSD) and hard disk drives (HDD).

#### SSD
The main attribute of SSD drives is high levels of I/O operations per second, or IOPS. SSD volumes excel at performing small read and write operations very quickly, with no drop in performance when executing random operations. Because they work best with smaller operations, the individual I/O size, or block size, is capped at 256 KiB for SSD volumes. They have a wide range of possible use cases and are especially good for high-transaction databases or applications where data needs to be accessed or changed frequently.

SSD volumes are available as General Purpose (gp2) volumes, which provide the ability to burst IOPS performance for a period of time, and Provisioned IOPS (io1) volumes, which maintain user-specified IOPS requirements.

#### HDD
Where the strength of SSD volumes is their IOPS, HDD volumes provide excellent data throughput. Because HDD disks require the drive head to physically locate the block where data is stored, they perform relatively poorly when it comes to random reads and writes, but can handle large quantities of sequential I/O very quickly and cost effectively. This makes them great, for example, for processing large data sets, or for file storage or backup. Larger I/O operations actually increase performance on HDD volumes, which can manage block sizes of up to 1,024 KiB.

The two types of HDD volumes are Throughput Optimized (st1) volumes, which provide higher throughput performance, and Cold HDD (sc1) volumes, which are an inexpensive solution for less frequently accessed data. Both st1 and sc1 volumes have the ability to burst throughput performance.

#### Finding the right combination
It’s possible to attach different volume types to a single instance, and mixing and matching can open up many different use cases. For example, an instance can have a high-transaction database running on gp2 volumes, and then move database logs to sc1 volumes for long-term storage. Taking the time to choose and configure the right EBS volumes can make an enormous difference both in terms of performance and how much you pay for your AWS usage.

The below example illustrates how running the same type of workload on different volume types can produce very different results. In reading random data with a block size of 16 KiB, the SSD volume (yellow) provided higher reads per second with significantly less latency per read than the HDD volume (purple). Note that there are two additional volumes (blue) attached to this instance that are inactive during the shown period.

{{< img src="amazon-ebs-iops-diff.png" alt="Difference between EBS volume type performance" wide="true" popup="true" caption="Disk reads per second (system.io.r_s) on top. Average time per read operation (system.io.r_await) on bottom." >}}

EBS volumes are virtually provisioned, which means that the stated performance characteristics of each volume type are based not on physical disk limitations but on how AWS manages the drives. Optimizing volume performance against your workload means understanding and balancing three primary factors, discussed further below: IOPS, throughput, and block size. 

AWS’s [stated limits][volume-types] are based on an I/O block size of 16 KiB for SSD volumes and 1,024 KiB for HDD volumes. For example, a General Purpose SSD volume is able to provide up to a maximum of 10,000 IOPS. A 16-KiB block size means that 10,000 IOPS would equal the maximum stated throughput of 160 MiB/s. If the block size is larger, the volume will never reach its maximum IOPS capacity because it would hit its throughput limit first. (As an example, a block size of 64 KiB would hit the 160 MiB/s throughput limit at only 2,500 IOPS.)

## What to look for with Amazon EBS monitoring
Monitoring your EBS volumes is vital to ensure not only that your applications are healthy, but also that your instance and volume configuration are appropriate and even optimal for your workload. There are three main categories of metrics you will want to track when monitoring your volumes:

- [Disk I/O](#disk-io)
- [Latency](#latency)
- [Disk activity](#disk-activity)

In addition to these, you have access to [status checks](#status-checks) that report on the status of your volumes. Similarly, you can track scheduled [events](#events) that might affect your instances’ status or availability. Any failed volume status checks produce an event to indicate the cause, so keeping track of events provides a high-level view of your volumes and the underlying AWS systems.

The easiest way to see most resource metrics for your EBS volumes and other AWS services is to use Amazon’s [CloudWatch monitoring system][cloudwatch]. But there are a few things to keep in mind. 

First, CloudWatch can aggregate data over different time periods and using different calculations. By default, CloudWatch collects EBS volume metrics at five-minute intervals, with the exception of io1 volumes, which publish metrics at a one-minute frequency. Calculations, or aggregation methods, such as average, sum, maximum, etc., will provide different slices of information on these metrics over that aggregation period. 

Second, AWS separates most resources by region, so you can generally only view CloudWatch metrics for volumes within a single region at a time. And finally, CloudWatch does not report metrics related to your volume’s disk space. We will explore some other ways to track disk space metrics in the [second part][part-two] of this series.

This article references metric terminology introduced in our [Monitoring 101 series](/blog/monitoring-101-collecting-data), which provides a framework for metric collection and alerting.

### Disk I/O
Corresponding with the two volume types available, SSD and HDD, there are two primary and interrelated categories of disk I/O metrics that are important to monitor: IOPS and throughput. Comparing actual I/O levels against your anticipated workload helps determine if you need to scale up, or downsize, your EBS volumes or switch to a different type to increase capacity or avoid paying for unused resources.

Correlating volume IOPS with overall throughput and average I/O block size can reveal if your application would benefit from a different volume type. This is because of how EBS logically organizes I/O. EBS attempts to merge contiguous I/O blocks into a single unit as much as possible. So for example, for an SSD volume—keeping in mind that SSD block size is capped at 256 KiB—four sequential 128 KiB writes would count as two operations, while four random 128 KiB writes would count as four operations. This can have a significant effect on performance. Using the same example with an HDD volume, where block size is capped at 1,024 KiB, four sequential 128 KiB writes would only be one operation. So in this case, an SSD volume could hit its throughput limits while being well under its IOPS capacity. Likewise, small random I/O operations would each count individually, meaning that IOPS can add up quickly while throughput levels remain relatively low.

|Name|Description|Metric type|
|--- |--- |--- |
|VolumeReadOps and VolumeWriteOps|Completed read/write operations from and to the volume|Resource: Utilization|
|VolumeReadBytes and VolumeWriteBytes|Bytes read from or written to the volume|Resource: Utilization|
|VolumeThroughputPercentage*|The percentage of IOPS delivered of the volume’s total provisioned IOPS|Resource: Utilization|
|VolumeConsumedReadWriteOps*|Total combined number of read and write operations from and to the volume|Resource: Utilization|
|*  _Only applicable to io1 volumes._|

#### Metrics to watch: VolumeReadOps and VolumeWriteOps
These metrics provide the total number of read and write operations performed during the aggregation period. For io1 volumes, that is one minute by default; for all other volumes, the aggregation period is five minutes. Normalizing these metrics to per-second rates provides the IOPS, which you can then compare with your volumes’ capacity.  

{{< img src="amazon-ebs-write-ops-rev.png" alt="EBS VolumeReadOps graph" wide="true" popup="true" >}}

In addition to indicating whether you are using the most appropriate volume types, monitoring IOPS can also provide insight into possible issues in your application or infrastructure. Because EBS volumes are networked storage and share infrastructure with other users, higher IOPS [may not lead to increases in overall latency](/blog/aws-ebs-latency-and-iops-the-surprising-truth/). Still, monitoring these metrics can reveal trends like elevated disk activity along with long request queues, which could mean your application needs a caching layer to handle the amount of data it is serving. If you see certain volumes experiencing high read or write levels while others sit idle, this might indicate that you have a misconfigured [application load balancer](/blog/monitor-application-load-balancer/) (or, if you don’t use a load balancer, that you might need one).


#### Metrics to watch: VolumeReadBytes and VolumeWriteBytes
These metrics provide information on the amount of data being transferred by your volumes. The information these metrics provide can be quite different depending on what aggregation method you request. The average will return the block size, or the average size of each I/O operation, calculated across all operations that took place during the time period. This is important for determining what sort of workload your EBS volumes are handling and if your volume type is well-matched to your application. For example, you might be running your application on General Purpose (gp2) SSD volumes. If these metrics show your average I/O size is larger than 256 KiB (the largest possible block size for SSD volumes), and if your workload typically involves sequential data access, you might get a performance boost by switching to st1 volumes. This is because st1 volumes are better suited for processing larger, sequential I/O operations, whereas gp2 volumes are best for smaller, random I/O. One caveat is that, for volumes attached to C5 and M5 instances, averaging these metrics will return the average number of bytes read or written over the requested period, not per operation.

If you request the sum instead of the average of either of these metrics, you will get the total amount of data read or written during the specified period. This is a good way to monitor overall throughput levels and see if any volumes are handling more or less data than anticipated. Monitoring overall throughput will also help you see if the bandwidth limits of instances themselves might be restricting the throughput of your volumes. 

{{< img src="amazon-ebs-write-bytes-rev2.png" alt="Amazon EBS VolumeWriteBytes graph" wide="true" popup="true" >}}

#### Metric to watch: VolumeThroughputPercentage
_Only applicable to Provisioned IOPS volumes._ This metric reports the percentage of the volume's total provisioned IOPS being delivered during the period. Keeping an eye on this metric can provide a quick summary of whether the number of IOPS you have provisioned for your volumes is appropriate. Note that I/O performance might appear degraded in certain situations, such as if you create a snapshot of a volume while it is being used, or if the instance the volume is attached to is not [EBS optimized][ebs-optimized]. This metric is only available for io1 volumes, which by default report metrics at a one-minute resolution.

#### Metric to watch: VolumeConsumedReadWriteOps
_Only applicable to Provisioned IOPS volumes._ This metric is a total sum of combined read and write operations performed during the specified period. Each I/O is measured in terms of 256 KiB blocks, with smaller operations rounded up and larger ones divided into 256K units. Like VolumeThroughputPercentage, this metric gives you a way to quickly compare your io1 volumes' I/O activity against the number of IOPS you have provisioned. This metric is only available for io1 volumes, which by default report metrics at a one-minute resolution.

### Latency
EBS latency is a measure of the time taken between sending a read or write operation to an EBS volume and that operation’s completion. Latency is particularly important to monitor for applications that require high IOPS, and correlating latency with metrics related to volume activity can help pinpoint performance issues.

|Name|Description|Metric type|
|--- |--- |--- |
|VolumeTotalReadTime and VolumeTotalWriteTime|Total time taken, in seconds, for all read/write operations completed within the specified period|Work: Performance|

#### Metrics to watch: VolumeTotalReadTime and VolumeTotalWriteTime
The average of these metrics will return the average time, in seconds, of each completed operation, with the exception of volumes connected to C5 and M5 instances, where average won’t return anything. The sum will return the total time of all operations completed within the specified period. If many simultaneous operations complete within the period, the number of seconds returned might be more than the number of seconds in the period.

As mentioned above, due to resource sharing among AWS users, increases in per-operation latency may not necessarily be an indicator of problems with your volumes. But keeping an eye on these metrics, especially in relation to others like [VolumeReadOperations and VolumeWriteOperations](#metrics-to-watch-volumereadops-and-volumewriteops) and [VolumeQueueLength](#metric-to-watch-volume-queue-length), can provide a general overview of how your volumes are performing, particularly because an increase in latency could be a result of your volumes hitting their IOPS limits. If your application is experiencing latency issues, checking these metrics could help diagnose if the issue is with your EBS volumes.

{{< img src="amazon-ebs-time-write-rev.png" alt="Amazon EBS VolumeTotalWriteTime graph" wide="true" popup="true" >}}

### Disk activity
Aside from making sure your applications are running smoothly, measuring disk activity can provide information to help optimize volume usage so that you can avoid paying for unused resources. It’s useful to keep an eye on whether any volumes are sitting idle, or whether their operation queue length is zero, meaning they are spending time waiting for instructions.

|Name|Description|Metric type|
|--- |--- |--- |
|VolumeQueueLength|The number of read/write operations waiting to be completed|Resource: Saturation|
|VolumeIdleTime|Time, in seconds, when a volume received no read/write operations|Resource: Utilization|
|BurstBalance*|The percentage of I/O or throughput credits available in the burst bucket|Resource: Utilization|
|*_Only applicable to gp2, st1, and sc1 volumes._|


#### Metric to watch: Volume queue length
A volume’s queue length, or the number of pending operations waiting for execution, can have a significant effect on sustained IOPS performance. While an empty queue might sound ideal, it means that your volumes are spending time idle and are not able to optimize IOPS for that duration, essentially wasting resources. On the other hand, queuing requests naturally increases overall latency. Correlating your volumes’ queue length with other metrics like IOPS and volume read/write time can help determine the proper balance for your workload.

In general, AWS suggests maintaining [certain volume queue lengths][queue-length] for optimal performance based on your volume type and what kind of workload you have. A rule of thumb for SSD volumes is to aim for a queue length of one for every 500 IOPS available, and then monitoring and increasing the queue length until your application reaches its baseline or provisioned IOPS. For HDD volumes, the recommended starting point to target is a queue length of at least four when processing 1 MiB sequential operations. Tweaking the queue length might be done by adjusting available throughput capacity, striping I/O across volumes, or by adjusting your application’s structure to change how many requests a single disk receives. 

{{< img src="amazon-ebs-queue-length.png" alt="Amazon EBS VolumeQueueLength graph" wide="true" popup="true" >}}

#### Metric to watch: Volume idle time
Ideally your volumes should always be doing _something_. Monitor this metric to identify any volumes that spend time inactive, leaving provisioned resources unused. If I/O levels drop unexpectedly, a sudden increase in volume idle time could also be a result of larger application problems where requests aren’t being sent to the volumes.

#### Metric to alert on: Burst balance
_Only applicable to General Purpose SSD, Throughput Optimized HDD, and Cold HDD volumes._ Bursting allows a volume to operate at a higher baseline level of performance for as long as there are available burst credits. The burst bucket is the balance of credits available to volumes that provide bursting for either IOPS (up to 3,000 IOPS for gp2 volumes) or throughput (up to 500 MiB/s for st1, and 250 MiB/s for sc1 volumes). In both cases, the volume’s burst bucket replenishes credits at a rate equivalent to the [volume's baseline level of performance][volume-types], meaning that larger volumes will refill their burst buckets more quickly. This metric returns the percentage of credits available.

{{< img src="amazon-ebs-burst-balance-rev2.png" alt="Amazon EBS BurstBalance graph" wide="true" popup="true" >}}

If you see that your volumes are draining their burst buckets more often than expected, this could indicate that you should be using higher capacity volumes for more baseline performance, or that you should switch to io1 volumes to ensure consistent IOPS. Note also that the level of burst performance can be reached and exceeded by choosing a large enough volume, making the burst balance primarily useful for boosting performance of smaller volumes.

### Status checks

AWS automatically runs [status checks][status-checks] on your EBS volumes. These provide a high-level indication of your volumes’ I/O status and whether there are any potential issues with your data or, in the case of io1 volumes, volume performance.

|Name|Description|Metric type|
|--- |--- |--- |
|VolumeStatus|Indicates general I/O status for the volume|Resource: Availability|
|IOPerformance*|Measures I/O performance against expected levels|Resource: Availability|
|*_Only applicable to io1 volumes._|

#### Metric to watch: Volume status
AWS runs I/O status checks on your volumes every five minutes. A volume’s status will appear as `ok` if all checks pass, `impaired` if any check fails, or `insufficient-data` if the checks are incomplete. Provisioned IOPS volumes may return an additional value of `warning` if measured performance is below expectations. This may be the case if an io1 volume is being initialized from a snapshot, in which case degraded performance is temporary and expected.

If AWS detects any possible inconsistencies with a volume’s data, it will by default disable any further I/O to and from that volume to avoid potential corruption. The next volume status check will fail and the volume will be marked impaired. AWS will also generate an [event](#events) indicating that the volume is not accepting I/O. You can change this behavior and keep I/O enabled for problematic volumes, which means that the volume status check will pass, but it will still generate an event indicating that an issue was detected and I/O remained enabled.

#### I/O performance status
_Only applicable to Provisioned IOPS volumes._ This check compares actual I/O performance to the volume’s provisioned level. Possible return values for this check are `Normal`, `Degraded`, `Severely Degraded`, `Stalled`, `Not Available` (if I/O is disabled), or `Insufficient Data`.

### Events
As mentioned above, if a volume status check fails, AWS will generate an event that includes a description of the volume’s status and timestamps for when I/O was disabled. Another event will be generated to mark the time when I/O is enabled again. For io1 volumes, event descriptions will also provide the I/O performance status.

In addition to events related to your EBS volumes, you should monitor your [EC2 events](/blog/ec2-monitoring/#events) to stay informed about   possible changes in the availability of your instances and any connected data. EBS volumes will continue to accrue storage charges, even if they are attached to an instance that has been stopped. So monitoring whether any instances are scheduled to be stopped will provide you enough time to shift volumes to new instances or otherwise adjust your infrastructure.

### Disk space metrics
Because CloudWatch collects metrics via a hypervisor, it does not report internal, system-level metrics such as disk usage on your volumes. In addition to the metrics covered in this post, [part two][part-two] of this series will cover how you can collect disk space metrics so that you have full visibility into the resource usage and availability of your EBS infrastructure.

## Getting started
In this post we have looked at several standard metrics that are invaluable for tracking the usage and performance of your EBS volumes. Amazon EBS’s range of volume types lets you create an infrastructure optimized for just about any use case. This means that keeping an eye on resource utilization is particularly important for determining if it is necessary to change, upgrade, scale up, or even downsize your volume and instance fleet so that it meets your needs efficiently and cost-effectively. And, when troubleshooting problems with your application, these metrics can help you determine if the root cause may be in the arrangement and configuration of your volumes. 

Now that we know what metrics to collect, the [next post][part-two] will guide you through the process of collecting them, via the CloudWatch console, the AWS CLI, and a monitoring tool that integrates with the CloudWatch API.

_Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/aws-ebs/amazon-ebs-monitoring.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues)._


[snapshots]: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSSnapshots.html
[s3]: https://aws.amazon.com/s3/
[ebs-optimized]: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSOptimized.html 
[ec2-config]: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-ec2-config.html
[enhanced-networking]: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/enhanced-networking.html
[cloudwatch]: https://aws.amazon.com/cloudwatch/
[volume-types]: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSVolumeTypes.html
[queue-length]: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/benchmark_procedures.html#UnderstandingQueueLength
[status-checks]: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/monitoring-volume-status.html#monitoring-volume-checks
[part-two]: /blog/collecting-amazon-ebs-metrics
