---
blog/category: ["series metrics"]
blog/tag: ["Apache", "http server", "web server", "performance"]
date: 2017-03-16T00:00:05Z
description: "In this post, we'll explore how Apache works, and discuss the key performance metrics that you should monitor."
draft: false
email: emily.chang@datadoghq.com
featured: true
image: apache-hero1.png
meta_title: null
preview_image: apache-hero1.png
scribbler: "Emily Chang"
scribbler_image: img-0791.jpg
slug: monitoring-apache-web-server-performance
sub_featured: false
title: "Monitoring Apache web server performance"
twitter_handle: 
---

*This post is part 1 of a 3-part series about monitoring Apache performance. In this post, we'll cover how Apache works, and explore the key performance metrics that you should monitor. [Part 2][part-2] explains how to collect Apache metrics and logs, and [part 3][part-3] describes how to monitor Apache with Datadog.* 

## What is Apache?
The [Apache HTTP Server][apache-http], also known as Apache HTTPd, is a widely used open source web server that is extremely customizable. Its functionality can be extended through modules that suit a wide range of use cases, from serving [dynamic PHP content][apache-php] to acting as a [forward or reverse proxy][proxy-docs].

The Apache HTTP Server Project is based on Rob McCool's work on the HTTPd web server for the National Center for Supercomputing Applications (NCSA). After McCool left the NCSA, a group of users (who became known as the original Apache Group) picked up where McCool left off by combining their contributions, or "patches," to the project and releasing it for public use. Apache's name refers to its origins as "a patchy web server" but also pays homage to the Native American tribe with the same name. HTTPd was the first project developed by the [Apache Software Foundation][asf-home], which is a volunteer-driven organization that now supports [more than 300 open source projects][asf-projects], including [Cassandra][cassandra-home], [Kafka][kafka-home], and [Hadoop][hadoop-home]. 

Since it was officially released in 1995, Apache has become the most popular web server in use today. Approximately 45 percent of active sites are running on Apache, according to a [survey conducted by Netcraft in December 2016][netcraft-survey]. Many organizations rely on Apache, including PayPal, Cisco, Apple, and, of course, the Apache Software Foundation.

Note that in this series, we will use the term "Apache" to refer to Apache web server, rather than the Apache Software Foundation. Some of the concepts and metrics are specific to Apache version 2.4; however, many of these concepts are applicable to all versions, and any changes in metric names across versions will be pointed out along the way.  

### Apache vs. NGINX vs. IIS
Apache is often compared to other popular web servers like [NGINX][nginx-home] and [IIS][iis-home], each of which has its strong suits. Apache has been widely adopted because it is completely open source, and its modular architecture is customizable to suit many different needs. Because Apache isolates its core functionality (how it handles requests, sockets, etc.) from the rest of its modules, developers have been able to create and contribute their own modules without affecting the web server's core functionality. However, Apache's original model of one process or thread per connection does not scale well for thousands of concurrent requests, which has paved the way for other types of web servers to gain popularity.

One such web server is **[NGINX][nginx-home]**, which was designed to address the [C10k problem][c10k]: How can web servers handle 10,000 clients at the same time? With each new incoming connection, NGINX creates a file descriptor, which consumes less memory than an entire thread or process. Because its architecture is event-driven rather than process-based, NGINX also reduces the need for context switching that occurs in process-per-connection web servers. 

Microsoft's **[Internet Information Services (IIS)][iis-home]** is similar to Apache in that its functionality can be extended through additional modules. However, while IIS was designed specifically for Windows, Apache runs on many Unix-like platforms, as well as some versions of Windows. Because it was developed by Microsoft (and has been included in every version of Windows since NT), IIS is able to optimize the native kernel's networking resources very efficiently. This has made it a natural choice for Windows environments, and particularly for users who need to serve dynamic content like ASP.NET applications.

## Key Apache performance metrics  
If you're using Apache as your web server, you want to be informed of bottlenecks or performance problems before they manifest themselves as user-facing issues. Some of the most important metrics that will help you gauge your servers' health include the rate of requests, request latency, and error rates.  

In general, there are a few types of metrics you will want to monitor:

- [Throughput and latency metrics](#throughput-and-latency-metrics)
- [Resource utilization and activity metrics](#resource-utilization-and-activity-metrics)
- [Host-level resource metrics](#toc-host-level-resource-metrics)
- [Errors](#errors)

{{< img src="apache-final-screen.png" alt="Dashboard of Apache performance metrics" popup="true" >}}

This article references metric terminology from our [Monitoring 101 series][monitor-101], which provides a framework for metric collection and alerting.

Note: The metrics discussed in this post are available from the Apache status module ([mod_status][mod-status]), as well as the [access log][access-log]. We will walk through the process of collecting and aggregating mod_status metrics in [Part 2][part-2] of this series.  

<div id="work-metrics"></div>

### Throughput and latency metrics

<table>
<thead>
<tr>
<th align="left">Name</th>
<th align="left">Description</th>
<th align="left"><a href="http://localhost:1313/blog/monitoring-101-collecting-data/">Metric type</a></th>
<th align="left">Availability</th>
</tr>
</thead>

<tbody>
<tr>
<td align="left">Request processing time</td>
<td align="left">Microseconds required to process a client request</td>
<td align="left">Work: Performance</td>
<td align="left">Apache access log</td>
</tr>

<tr>
<td align="left">Rate of requests</td>
<td align="left">Average number of client requests per second</td>
<td align="left">Work: Throughput</td>
<td align="left">mod_status</td>
</tr>

<tr>
<td align="left">Bytes</td>
<td align="left">Total bytes served*</td>
<td align="left">Other</td>
<td align="left">mod_status</td>
</tr>

<tr>
<td colspan="4">*<em>Note: This metric reflects the bytes that <strong>should</strong> have been served, which is not necessarily equal to the bytes <strong>actually</strong> (successfully) served.</em></td> 
</tr>

</tbody>
</table>


**Metric to alert on: Request processing time**  
If Apache is processing requests slowly, it could be due to other components of your stack, such as long-running queries in MySQL or slow execution of PHP code. Monitoring all your systems in a way that you can correlate performance data across components helps to identify such issues. If your metrics indicate that the latency is due to Apache itself, however, you may want to experiment with [reducing the `KeepAliveTimeout`][keepalive-docs] to prevent worker threads from being blocked longer than necessary. If you are not already using the event MPM, switching to it (if possible) will enable you to process keep-alive connections more efficiently, which can also help improve request latency. We will cover the event MPM in more detail [below](#event-mpm).  

If you are serving a lot of static content, you can improve request latency by using NGINX as a proxy to handle static requests asynchronously. NGINX will filter requests, fulfill requests for static content, and pass dynamic requests off to Apache, thereby helping relieve some of the load on your Apache servers. It may also be worth checking out [Apache's caching guide][caching-docs] or using a cache like [Varnish][varnish-home]. 

By default, `HostnameLookups` should already be turned off in the configuration file, but you should verify that it's disabled. If enabled, the server takes additional time to translate each request's remote IP into a hostname via DNS lookup, which has a performance cost. Similarly, if you are allowing or restricting access by hostname in the main configuration file (e.g. "Require host example.com"), you should modify it to [specify the IP address][dns-lookup-docs] instead of the hostname, for better performance.   

**Metric to alert on: Rate of requests**  
If `ExtendedStatus` is enabled, Apache's mod_status page will list additional information, including the rate of requests, CPU load, and uptime. [Part 2][part-2] of this series will cover more details about collecting this information.

If the rate of requests is dramatically *increasing*, you may want to take measures to make sure that you have enough resources to handle the load, and/or to determine if it is illegitimate traffic (e.g. a denial of service attack). If the rate is rapidly *decreasing*, it could point to problems elsewhere (for example, your servers may be swapping to disk, or your database could be crashing). 

{{< img src="mod-status-metrics-highlighted.png" alt="Apache mod status page with metrics highlighted" popup="true" >}}

As shown in the screenshot above, Apache's mod_status module provides a metric called **requests/sec**, but note that the name is a bit ambiguous—this value represents the average number of requests per second, calculated *over the entire period the server has been running*.

{{< img src="rate-of-apache-requests.png" alt="Apache requests per second graph" popup="true" >}}

Therefore, it will be difficult to detect sudden spikes or dips if your server has been running for a long time. To get a more meaningful metric, you need to use a monitoring tool to calculate the rate at which the number of requests has changed over a shorter time period (such as the last minute). We'll show how you can do this with Datadog in [Part 3][part-3] of this series.  

### Resource utilization and activity metrics
At its most basic level, Apache processes client requests and delivers responses back to clients. Resource utilization and activity metrics can help you determine whether your servers are effectively utilizing system resources, and whether they have enough capacity to complete their work. 

Apache includes several types of [Multi-Processing Modules][mpm-docs] (MPMs) that determine how the server uses resources (threads/processes, ports, etc.) to process requests. Some operating systems are only compatible with an MPM that is specific to that OS (e.g. mpm_winnt for Windows). 

Apache can only run one MPM at a time; if you do not specify an MPM when compiling the server (by using the `--with-mpm=<DESIRED_MPM>` option), Apache will select one for you, based on your system/environment. If you are running Apache on a Unix-like platform that is compatible with multiple MPMs, it's important to understand the differences between each MPM so that you will know when you should stick with the default, and when another MPM might better suit your needs. In the next section, we will highlight the differences among the three types of MPMs available for Unix-like systems.

Before we get into more detail about each MPM, here are a few configuration settings that are common to all MPMs, with some differences, as noted below. These settings will be referenced in later sections, and can be tweaked by updating your MPM settings, either in the main configuration file (`apache2.conf` or `httpd.conf`) or, on Debian platforms, within the module-specific config file located in the `mods-enabled` directory: `<APACHE2_DIRECTORY>/mods-enabled/<MPM_NAME>.conf`. 

- `StartServers` is the number of child processes created upon starting Apache.
- [`MaxRequestWorkers`][maxrequestworkers-docs] (or `MaxClients` in versions prior to 2.4) is the maximum number of connections that can be open at one time. Once this limit has been reached, any additional incoming connections are queued. The maximum size of the queue is determined by the `ListenBacklog` setting (by default 511, though it can be smaller depending on your OS; on Linux, the queue length is limited by `net.core.somaxconn`).
- `MinSpareServers`/`MinSpareThreads` and `MaxSpareServers`/`MaxSpareThreads` refer to the minimum and maximum number of child processes (in the prefork MPM) or worker threads (in the worker and event MPMs) that should be idle at any one time. If the number of idle processes/threads does not fall within these bounds, the parent process will kill or spawn new processes/threads accordingly.
- `MaxConnectionsPerChild` (known as `MaxRequestsPerChild` prior to version 2.4) determines the total number of connections each child process can serve before it is restarted, which can be important for guarding against [memory leaks](#toc-host-level-resource-metrics) when using certain modules like mod_php. 

#### MPMs for Unix-like systems
The three main MPMs for Unix-like systems are [prefork][prefork-mpm], [worker][worker-mpm], and [event][event-mpm]. As of version 2.4, Apache uses information about your operating system in order to [determine which MPM to run][apache-mpm-settings]. On Unix-like systems, the default MPM depends on each system's capability to support threads and thread-safe polling, but most modern platforms will run the event MPM by default.  

##### Prefork MPM
Though the [prefork MPM][prefork-mpm] was once the most widespread, default option, today, it is only recommended for users who need to run a non-thread-safe library ([such as mod_php][php-apache]). In the prefork MPM, the parent process uses `fork()` to pre-fork a pool of child processes at startup time (determined by `StartServers` in the main [configuration file][config-file-docs]).  

Each idle child process joins a queue to listen for incoming requests. This MPM uses a method called [**accept mutex**][mutex-docs] to ensure that only one process listens for and accepts the next TCP request (mutex stands for MUTual EXclusion mechanism). The first idle worker process in the queue acquires the mutex and listens for the next incoming connection. After receiving a connection, it releases the accept mutex by passing it to the next idle process in the queue, and processes the request (during which time it is considered a busy worker). After it finishes processing the request, it joins the queue once again. 

{{< canvas-animation name="apache_prefork" width="" height="" >}}

Because this MPM needs a higher number of processes to handle any given number of requests, it is generally more memory-hungry than multi-threaded MPMs like worker and event. For this reason, if you are using mod_php you should consider switching over to [PHP-FPM][php-fpm-docs] so that you can use the worker or event MPM instead.

##### Worker MPM
In the [worker MPM][worker-mpm], the parent process creates a certain number of child processes (once again, determined by `StartServers` in the main [configuration file][config-file-docs]), and each child process creates a constant number of threads (`ThreadsPerChild`), as well as a listener thread. 

Like the prefork MPM, the worker MPM uses **accept mutex** to designate which thread will process the next incoming request. Each child process's listener thread only joins the idle queue (which indicates that it is eligible to obtain accept mutex) if it detects that at least one worker thread within the child process is currently idle. Therefore, for every process that has at least one idle worker thread, the listener thread will join the queue to apply for accept mutex. 

The listener thread that accepts the mutex will listen for the next incoming request, accept the connection, and release the accept mutex so that another listener thread can shepherd the next incoming request. The listener thread then passes the socket to an idle worker thread within its process. 

{{< canvas-animation name="apache_worker" width="" height="" >}}

Unlike the prefork MPM, the worker MPM enables each child process to serve more than one request at a time, by utilizing multiple threads. Because you only need one thread per connection, instead of forking one process per connection, this MPM tends to be more memory-efficient than the prefork MPM.

##### Event MPM
As of version 2.4 of Apache, the [**event MPM**][event-mpm] is now an official MPM (it was formerly experimental). Like the worker MPM, each child process in the event MPM creates multiple threads (determined by `ThreadsPerChild`), in addition to one listener thread.

In the other types of MPMs, if a worker thread or process handles a request on a keep-alive connection, the connection stays open (and the worker is blocked from processing other requests) for the duration of the `KeepAliveTimeout`, or until the client closes the connection.  

A major benefit of the event MPM is that it handles keep-alive connections more efficiently by utilizing the kernel's I/O methods like [epoll][epoll-docs] (on Linux) and [kqueue][kqueue-docs] (on BSD systems).  

In the event MPM, a worker thread can write a request to the client, and then pass control of the socket to the listener thread, freeing the worker to address another request. The listener thread assumes control of sockets that don't require immediate action from a worker thread, until it detects an "event" on a socket (e.g. if the client sends a new request on a keep-alive connection, the kernel will create an event to notify the listener that the socket is readable). Once the event is detected, the listener thread will pass it on to the next available idle worker thread.  

If the `KeepAliveTimeout` is reached before any activity occurs on the socket, the listener thread will close the connection. Also, if any listener thread detects that all worker threads within its process are busy, it will close keep-alive connections, forcing clients to create new connections that can be processed more quickly by other processes' worker threads (although, for the sake of simplicity, we do not show this in the example below). Because the dedicated listener thread helps monitor the lifetime of each keep-alive connection, worker threads that would otherwise have been blocked (waiting for further activity) are instead free to address other active requests. 

{{< canvas-animation name="apache_events" width="" height="" >}}
<figcaption>For simplicity, this diagram shows only one worker thread per child process. In reality, the default event MPM behavior is for each child process to create 25 worker threads and one listener thread.</figcaption>

Depending on which MPM you're using, you'll have access to different metrics, which we will cover in more detail in the next section. 

#### Worker resource metrics to watch
Now that we understand how connections are processed differently in each Apache MPM, we can use this information to determine whether resources are over- or underutilized.

Name  | Description  | [Metric type][monitor-101] | Availability
:--|:---|:--|:--|
Busy workers  | Total number of busy worker threads/processes |  Resource: Utilization | mod_status |
Idle workers  | Total number of idle worker threads/processes  |  Resource: Utilization | mod_status |
Asynchronous connections: writing   | Number of async connections in writing state (only applicable to event MPM) | Resource: Utilization | mod_status |
Asynchronous connections: keep-alive   | Number of async connections in keep-alive state (only applicable to event MPM) | Resource: Utilization | mod_status |
Asynchronous connections: closing   | Number of async connections in closing state (only applicable to event MPM) | Resource: Utilization | mod_status |

{{< img src="idle-workers-graph.png" alt="idle Apache workers graph" >}}

**Worker utilization**: A worker is considered "busy" if it is in any of the following states: reading, writing, keep-alive, logging, closing, or gracefully finishing. An "idle" worker is not in any of the busy states; the number of idle workers is shown on [Apache's mod_status page][modstatus-page].  

{{< img src="idle-workers-mod-status.png" alt="idle Apache workers on mod status" popup="true" caption="Apache's status module, mod_status, displays a real-time count of idle workers.">}}

If you consistently see a large number of idle workers, you may want to lower your `MinSpareServers` (for the prefork MPM) or `MinSpareThreads` (for the worker and event MPMs) setting so that you are not sustaining a higher number of processes or threads than necessary to process your rate of traffic. Maintaining more processes or threads than you actually need will unncessarily exhaust system resources.

If, on the other hand, you have very few idle workers at all times, you may see slower request processing times because your server continually needs to spawn new processes or threads to handle new requests, rather than making use of the idle threads or processes already on hand. If you see the **total number of workers (busy + idle)**  approaching your `MaxRequestWorkers` limit, any additional requests that come in will end up in the TCP ListenBacklog (which has a maximum size of `ListenBacklog`), until the next worker thread becomes available.  

Increasing `MaxRequestWorkers` can help reduce the number of queued requests, but be careful not to set it unnecessarily high, as each additional worker thread or process requires additional system resources.  

**Keep-alive connections**: If you see a lot of connections in a keep-alive state (indicated by a `K` on the mod_status scoreboard), you may be getting many requests from clients that don't make subsequent requests (and therefore do not help you reap the intended benefits of keep-alive connections). If you are not already using the event MPM, try switching to it if possible, because this MPM was designed to process keep-alive connections more efficiently. 

{{< img src="keep-alive-apache.png" alt="Apache asynchronous connections in keep-alive state event MPM" popup="true" >}}

If you *are* using the event MPM, Apache will expose the count of keep-alive async connections (any connections that are waiting for further events to signal that they are ready to get passed back to worker threads). If you see a high number of keep-alive async connections, combined with high CPU and memory utilization, you may want to lower the maximum number of simultaneous connections to the server (`MaxRequestWorkers`), and/or decrease the `KeepAliveTimeout` to avoid holding connections open longer than necessary.  

### Host-level resource metrics
Monitoring host-level metrics from your Apache hosts can help provide a more comprehensive view of your web servers' performance. As you monitor these resources, you may find that eventually you need to either [scale up][scaling-up-docs] or [scale out][horizontal-scaling-docs] your servers so that your systems can keep up with the load. 

**Metric to alert on: Memory usage**  
Memory is one of the most important resources to monitor when using Apache. If Apache runs out of memory, it will start swapping to disk, which greatly degrades performance. To guard against memory leakage  (which is particularly important if you use mod_php), you could set `MaxConnectionsPerChild` to a high value (e.g. 1,000) rather than leaving it unbounded (by setting it to 0). By default, this directive is unbounded, which means that processes will never be forced to restart. If you do choose to set this directive, make sure not to set it too low, because restarting processes carries some overhead.

As mentioned above, memory use is also impacted by the `MaxRequestWorkers` setting, which controls the maximum number of processes or threads running at any one time. The value of `MaxRequestWorkers` (known as `MaxClients` prior to version 2.4) should be calculated based on the maximum amount of memory you feel comfortable reserving for Apache processes. Using a tool like [htop][htop] should give you a rough idea of the actual, virtual, and cached memory usage of each Apache process. You can use this to calculate an estimate of what your `MaxRequestWorkers` value should be.  

For example, if you observe that each Apache process uses roughly 50MB, and your server has 4GB of RAM, you would calculate `MaxRequestWorkers` with a rough formula of: `( (4000 - <OTHER_MEMORY_NEEDED>) / 50 )` 

The value of `<OTHER_MEMORY_NEEDED>` depends on whatever else you're running, such as an application server or MySQL. You can also use htop to check how much memory your system is using when Apache is *not* running, and use this value as a basis for `<OTHER_MEMORY_NEEDED>`. Make sure to add in a bit of a cushion as an extra precaution—it's better to be conservative about the `MaxRequestWorkers` value because you don't want to run out of memory and start swapping to disk. The [Apache docs][max-request-docs] offer more advice about determining a good value for `MaxRequestWorkers`.  

If Apache is using too much memory, you should try to switch from prefork to the worker or event MPM if your system allows it, and if you do not need to use non-thread-safe libraries. You can also disable any unnecessary Apache modules (to check which ones are currently loaded, run `httpd -D DUMP_MODULES` on [RPM-based systems][rpm-apache-docs] or `apache2ctl -M` on [other Unix-based systems][apachectl-docs]). 

Lowering the number of processes created upon startup ([StartServers][start-servers]), and/or decreasing `MaxSpareThreads` (maximum allowed number of idle worker threads) can also help lower your memory footprint. Alternatively, you can add more memory to your servers, or [scale horizontally][horizontal-scaling-docs] to distribute the load among a higher number of servers.  

**Metric to alert on: CPU utilization**  
If you see CPU usage continually rising on your Apache servers, this can indicate that you don't have enough resources to serve the current rate of requests. If you are running a database and/or application server on the same host as Apache, you should consider moving them onto separate machines. This gives you more flexibility to [scale each layer of your environment][horizontal-scaling-docs] (database, application, and web servers) as needed. The more connections Apache needs to serve, the more threads or processes are created (depending on the MPM in use), each of which requires additional CPU.  

**Metric to watch: Open file descriptors**  
Apache opens a file descriptor for each connection, as well as every log file. If your server has a large number of virtual hosts, you may run into a problem with your system-imposed limit, because Apache generates separate log files for each virtual host. [The documentation][descriptor-docs] has some useful guidelines about how you can either raise the limit on your system, or [reduce the total number of logs created][virtual-host-log-docs], by writing all virtual host logs to the same file, and using a script like [split-logfile][split-logfile-docs] for downstream categorization. 

### Errors
Name  | Description  | [Metric type][monitor-101] | Availability
:--|:---|:--|:--|
Client error rate  | Rate of 4xx client errors (e.g. 403 Forbidden, 404 Not Found) per second |  Work: Errors | Apache access log |
Server error rate  | Rate of 5xx server-side errors (e.g. 500 Internal Server Error, 502 Bad Gateway, 503 Service Unavailable) per second  |  Work: Errors | Apache access log |

Apache error metrics can be useful indicators of underlying problems or misconfigured files. Although you may also be interested in monitoring client errors, they are not necessarily legitimate indicators of problems that you can solve (e.g. clients entering the wrong URL). In some situations, it may be useful to monitor client errors, as they could indicate that someone is testing your site for vulnerabilities. They can also alert you to situations such as clients trying to access an outdated link, which you can [redirect][redirect-docs] to a new endpoint in your configuration file.

**Metric to alert on: Server error rate**  
The server error rate can be calculated by counting the total number of requests with 5xx errors, and dividing that number by the total number of requests. Monitoring this metric per unit of time can help you determine if the error rate is increasing. If you see an increase in the error rate, you may want to check if there is a mistake in your configuration file, or if something else is causing the issue.  

The [Apache access log][access-log-docs] lists details about each request, including the client IP address, the time of the request, the HTTP request method (GET, POST, etc.) and endpoint/resource, and the HTTP response's status code and size (in bytes). You can also access Apache's [error log][error-log-docs] to see if you can glean more useful details. 

Apache will typically generate a 503 Service Unavailable status code when it is overloaded. Check the error log for more details about what caused the error; it may tell you that you didn't have enough workers available to handle the request load, or that a setting in your configuration file was limiting the number of connections that could access a certain resource/page. You may want to parse your access logs for 5xx errors and forward them to a monitoring platform; for more details, read [Part 3][part-3] of this series.

## Next step: GET the metrics 
In this post, we've covered some of the key metrics you should monitor to ensure that your Apache servers are running smoothly. The next step is to start collecting these metrics and parsing logs in order to get them into the form that is most useful for you. Read on for [Part 2][part-2], where we will walk through how to collect the data that will help you monitor your Apache web servers' performance. 

## Acknowledgment
Thanks to [Daniel Gruno][daniel-gruno], member of the Apache HTTP Server Project Management Committee, for reviewing this article prior to publication.

_Source Markdown for this post is available [on GitHub][the-monitor]. Questions, corrections, additions, etc.? Please [let us know][issues]._

[the-monitor]: https://github.com/datadog/the-monitor
[issues]: https://github.com/DataDog/the-monitor/issues
[asf-home]: https://www.apache.org/
[nginx-home]: https://www.nginx.com/
[iis-home]: https://www.iis.net/
[apache-http]: https://httpd.apache.org/
[netcraft-survey]: https://news.netcraft.com/archives/2016/12/21/december-2016-web-server-survey.html
[c10k]: http://www.kegel.com/c10k.html
[mpm-docs]: https://httpd.apache.org/docs/2.4/mpm.html
[mod-mono]: http://www.mono-project.com/docs/web/mod_mono/
[proxy-docs]: https://httpd.apache.org/docs/current/mod/mod_proxy.html
[apache-php]: https://wiki.apache.org/httpd/php
[monitor-101]: /blog/monitoring-101-collecting-data/
[windows-mpm]: http://httpd.apache.org/docs/current/mod/mpm_winnt.html
[prefork-mpm]: https://httpd.apache.org/docs/current/mod/prefork.html
[worker-mpm]: https://httpd.apache.org/docs/current/mod/worker.html
[event-mpm]: https://httpd.apache.org/docs/current/mod/event.html
[apache-mpm-settings]: http://httpd.apache.org/docs/current/mpm.html
[nginx-performance]: https://www.nginx.com/blog/inside-nginx-how-we-designed-for-performance-scale/
[php-apache]: http://php.net/manual/en/faq.installation.php#faq.installation.apache2
[nginx-home]: https://www.nginx.com/
[iis-architecture]: https://www.iis.net/learn/get-started/introduction-to-iis/introduction-to-iis-architecture
[start-servers]: https://httpd.apache.org/docs/2.4/mod/mpm_common.html#startservers
[modstatus-page]: https://httpd.apache.org/docs/2.4/mod/mod_status.html
[redirect-docs]: https://httpd.apache.org/docs/current/rewrite/remapping.html
[mod-status]: https://httpd.apache.org/docs/current/mod/mod_status.html
[access-log]: https://httpd.apache.org/docs/current/logs.html#accesslog
[varnish-blog]: /blog/top-varnish-performance-metrics/
[max-request-docs]: https://httpd.apache.org/docs/trunk/misc/perf-scaling.html#sizing-maxClients
[horizontal-scaling-docs]: https://wiki.apache.org/httpd/PerformanceScalingOut
[scaling-up-docs]: https://wiki.apache.org/httpd/PerformanceScalingUp
[nginx-blog]: /blog/how-to-monitor-nginx/
[php-fpm-docs]: https://wiki.apache.org/httpd/PHP-FPM
[apache-php-blog]: /blog/monitoring-apache-processes-datadog/
[descriptor-docs]: https://httpd.apache.org/docs/2.4/vhosts/fd-limits.html
[access-log-docs]: http://httpd.apache.org/docs/current/logs.html#accesslog
[caching-docs]: http://httpd.apache.org/docs/current/caching.html
[config-file-docs]: https://httpd.apache.org/docs/current/configuring.html
[error-log-docs]: https://httpd.apache.org/docs/current/logs.html#errorlog
[mysql-blog]: /blog/monitoring-mysql-performance-metrics/
[epoll-docs]: http://man7.org/linux/man-pages/man7/epoll.7.html
[kqueue-docs]: https://www.freebsd.org/cgi/man.cgi?kqueue
[virtual-host-log-docs]: http://httpd.apache.org/docs/current/logs.html#virtualhost
[split-logfile-docs]: http://httpd.apache.org/docs/current/programs/split-logfile.html
[mutex-docs]: https://httpd.apache.org/docs/2.4/mod/core.html#mutex
[nginx-apache]: https://www.nginx.com/blog/nginx-vs-apache-our-view/
[dns-lookup-docs]: https://httpd.apache.org/docs/2.4/dns-caveats.html
[maxrequestworkers-docs]: https://httpd.apache.org/docs/2.4/mod/mpm_common.html#maxrequestworkers
[asf-projects]: https://projects.apache.org/
[cassandra-home]: http://cassandra.apache.org/
[hadoop-home]: http://hadoop.apache.org/
[kafka-home]: http://kafka.apache.org/
[varnish-home]: https://varnish-cache.org/
[keepalive-docs]: https://httpd.apache.org/docs/2.4/mod/core.html#keepalivetimeout
[apachectl-docs]: https://httpd.apache.org/docs/2.4/programs/apachectl.html
[htop]: http://hisham.hm/htop/
[rpm-apache-docs]: https://httpd.apache.org/docs/2.4/platform/rpm.html
[part-2]: /blog/collect-apache-performance-metrics
[part-3]: /blog/monitor-apache-web-server-datadog
[daniel-gruno]: https://httpd.apache.org/contributors/

