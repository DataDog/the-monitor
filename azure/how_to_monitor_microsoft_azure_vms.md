# How to monitor Microsoft Azure VMs

*This post is part 1 of a 3-part series on monitoring Azure virtual machines. [Part 2](/blog/how-to-collect-azure-metrics) is about collecting Azure VM metrics, and [Part 3](/blog/monitor-azure-vms-using-datadog) details how to monitor Azure VMs with Datadog.*

## What is Azure?

Microsoft Azure is a cloud provider offering a variety of compute, storage, and application services. Azure services include platform-as-a-service (PaaS), akin to Google App Engine or Heroku, and infrastructure-as-a-service (IaaS). In the most recent Gartner “Magic Quadrant” rating of cloud IaaS providers, Azure was one of only two vendors (along with Amazon Web Services) to place in the “Leaders” category.

In this article, we focus on IaaS. In an IaaS deployment, Azure’s basic unit of compute resources is the virtual machine. Azure users can spin up general-purpose Windows or Linux (Ubuntu) VMs, as well as machine images for applications such as SQL Server or Oracle.

## Key metrics to monitor Azure

Whether you run Linux or Windows on Azure, you will want to monitor certain basic VM-level metrics to make sure that your servers and services are healthy. Four of the most generally relevant metric types are **CPU usage**, **disk I/O**, **memory utilization** and **network traffic**. Below we’ll briefly explore each of those metrics and explain how they can be accessed in Azure.

This article references metric terminology [introduced in our Monitoring 101 series](/blog/monitoring-101-collecting-data/), which provides a framework for metric collection and alerting.

Users can monitor Azure with the following metrics via [the Azure web portal](https://portal.azure.com/) or can access the raw data directly via the Azure diagnostics extension. Details on how to collect these metrics are available in [the companion post](/blog/how-to-collect-azure-metrics) on Azure metrics collection.

### CPU metrics

CPU usage is one of the most commonly monitored host-level metrics. Whenever an application’s performance starts to slide, one of the first metrics an operations engineer will usually check is the CPU usage on the machines running that application.

| **Name**            | **Description**                       | **[Metric type](/blog/monitoring-101-collecting-data/)** |
|---------------------|---------------------------------------|----------------------------------------------------------|
| CPU percentage      | Percentage of time CPU utilized       | Resource: Utilization                                    |
| CPU user time       | Percentage of time CPU in user mode   | Resource: Utilization                                    |
| CPU privileged time | Percentage of time CPU in kernel mode | Resource: Utilization                                    |

CPU metrics allow you to determine not only how utilized your processors are (via **CPU percentage**) but also how much of that utilization is accounted for by user applications. The **CPU user time** metric tells you how much time the processor spent in the restricted “user” mode, in which applications run, as opposed to the privileged kernel mode, in which the processor has direct access to the system’s hardware. The **CPU privileged time** metric captures the latter portion of CPU activity.

<div class="anchor" id="cpu-percentage" />

#### Metric to alert on: CPU percentage

Although a system in good health can run with consistently high CPU utilization, you will want to be notified if your hosts’ CPUs are nearing saturation.

[![Azure CPU heat map](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/azure-1-cpu.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/azure-1-cpu.png)

### Disk I/O metrics

Monitoring disk I/O is critical for understanding how your applications are impacting your hardware, and vice versa. For additional visibility beyond the VM-level metrics covered here, you can also collect metrics from your Azure storage accounts to determine if your storage is being throttled or has availability issues that could impact performance.

| **Name**   | **Description**                  | **[Metric type](/blog/monitoring-101-collecting-data/)** |
|------------|----------------------------------|----------------------------------------------------------|
| Disk read  | Data read from disk, per second  | Resource: Utilization                                    |
| Disk write | Data written to disk, per second | Resource: Utilization                                    |

<div class="anchor" id="disk-read" />

#### Metric to alert on: Disk read

Monitoring the amount of data read from disk can help you understand your application’s dependence on disk. If the application is reading from disk more often than expected, you may want to add a caching layer or switch to faster disks to relieve any bottlenecks.

#### Metric to alert on: Disk write

Monitoring the amount of data written to disk can help you identify bottlenecks caused by I/O. If you are running a write-heavy application, you may wish to upgrade[the size of your VM](https://azure.microsoft.com/en-us/documentation/articles/virtual-machines-size-specs/) to increase the maximum number of IOPS (input/output operations per second).
 [![Azure disk write speed](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/1-disk-write-2.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/1-disk-write-2.png)

### Memory metrics

Monitoring memory usage can help identify low-memory conditions and performance bottlenecks.

| **Name**         | **Description**                                               | **[Metric type](/blog/monitoring-101-collecting-data/)** |
|------------------|---------------------------------------------------------------|----------------------------------------------------------|
| Memory available | Free memory, in bytes/MB/GB                                   | Resource: Utilization                                    |
| Memory pages     | Number of pages written to or retrieved from disk, per second | Resource: Saturation                                     |

<div class="anchor" id="memory-pages" />

#### Metric to alert on: Memory pages

Paging events occur when a program requests a [page](https://en.wikipedia.org/wiki/Page_(computer_memory)) that is not available in memory and must be retrieved from disk, or when a page is written to disk to free up working memory. Excessive paging can introduce slowdowns in an application. A low level of paging can occur even when the VM is underutilized—for instance, when the virtual memory manager automatically trims a process’s [working set](https://msdn.microsoft.com/en-us/library/windows/desktop/cc441804(v=vs.85).aspx) to maintain free memory. But a sudden spike in paging can indicate that the VM needs more memory to operate efficiently.
 [![Azure memory paging](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/1-memory-pages.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/1-memory-pages.png)

### Network metrics

Azure’s default metric set provides data on network traffic in and out of a VM. Depending on your OS, the network metrics may be available in bytes per second or via the number of TCP segments sent and received. Because TCP segments are limited in size to 536 bytes each, the number of segments sent and received provides a reasonable proxy for the overall volume of network traffic.

| **Name**              | **Description**                  | **[Metric type](/blog/monitoring-101-collecting-data/)** | **Availability** |
|-----------------------|----------------------------------|----------------------------------------------------------|------------------|
| Bytes transmitted     | Bytes sent, per second           | Resource: Utilization                                    | Linux VMs        |
| Bytes received        | Bytes received, per second       | Resource: Utilization                                    | Linux VMs        |
| TCP segments sent     | Segments sent, per second        | Resource: Utilization                                    | Windows VMs      |
| TCP segments received | Segments received, per second    | Resource: Utilization                                    | Windows VMs      |

<div class="anchor" id="network-sent" />

#### Metric to alert on: Bytes/TCP segments sent

You may wish to generate [a low-urgency alert](/blog/monitoring-101-alerting/#low) when your network traffic nears saturation. Such an alert may not notify anyone directly but will record the event in your monitoring system in case it becomes useful for investigating a performance issue.

#### Metric to alert on: Bytes/TCP segments received

If your network traffic suddenly plummets, your application or network may be overloaded.
 [![Azure network out](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/1-network-out.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/1-network-out.png)

## Conclusion

In this post we’ve explored several general-purpose metrics you should monitor to keep tabs on your Azure virtual machines. Monitoring the metric set listed below will give you a high-level view of your VMs’ health and performance:

-   [CPU percentage](#cpu-percentage)
-   [Disk read/write](#disk-read)
-   [Memory pages](#memory-pages)
-   [Network traffic sent/received](#network-sent)

Over time you will recognize additional, specialized metrics that are relevant to your applications. [Part 2 of this series](/blog/how-to-collect-azure-metrics/) provides step-by-step instructions for collecting any metric you may need to monitor Azure.

## Acknowledgments

Many thanks to reviewers from Microsoft for providing important additions and clarifications prior to publication.

------------------------------------------------------------------------

*Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/azure/how_to_monitor_microsoft_azure_vms.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues).*
