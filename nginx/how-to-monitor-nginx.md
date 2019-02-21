---

What is NGINX?
-----------------------------------------------------


[NGINX](http://nginx.org/en/) (pronounced “engine X”) is a popular HTTP server and reverse proxy server. As an HTTP server, NGINX serves static content very efficiently and reliably, using relatively little memory. As a [reverse proxy](http://nginx.com/resources/glossary/reverse-proxy-server/), it can be used as a single, controlled point of access for multiple back-end servers or for additional applications such as caching and load balancing. NGINX is available as a free, open source product or in a more full-featured, commercially distributed version called NGINX Plus.

NGINX can also be used as a mail proxy and a generic TCP proxy, but this article does not directly address NGINX monitoring for these use cases.

Key NGINX metrics
-----------------


By monitoring NGINX you can catch two categories of issues: resource issues within NGINX itself, and also problems developing elsewhere in your web infrastructure. Some of the metrics most NGINX users will benefit from monitoring include **requests per second**, which provides a high-level view of combined end-user activity; **server error rate**, which indicates how often your servers are failing to process seemingly valid requests; and **request processing time**, which describes how long your servers are taking to process client requests (and which can point to slowdowns or other problems in your environment).

More generally, there are at least three key categories of metrics to watch:



-   [Basic activity metrics](#basic-activity-metrics)
-   [Error metrics](#error-metrics)
-   [Performance metrics](#performance-metrics)



Below we’ll break down a few of the most important NGINX metrics in each category, as well as metrics for a fairly common use case that deserves special mention: using NGINX Plus for reverse proxying. We will also describe how you can monitor all of these metrics with your graphing or monitoring tools of choice.

This article references metric terminology [introduced in our Monitoring 101 series](/blog/monitoring-101-collecting-data/), which provides a framework for metric collection and alerting.



### Basic activity metrics


Whatever your NGINX use case, you will no doubt want to monitor how many client requests your servers are receiving and how those requests are being processed.

NGINX Plus can report basic activity metrics exactly like open source NGINX, but it also provides a secondary module that reports metrics slightly differently. We discuss open source NGINX first, then the additional reporting capabilities provided by NGINX Plus.

#### NGINX


The diagram below shows the lifecycle of a client connection and how the open source version of NGINX [collects metrics](http://nginx.org/en/docs/http/ngx_http_stub_status_module.html) during a connection.

{{< img src="nginx-connection-diagram-2.png" alt="connection, request states" popup="true" size="1x" >}}

Accepts, handled, and requests are ever-increasing counters. Active, waiting, reading, and writing grow and shrink with request volume.

<table>
<td><strong>Name</strong></td>
<td><strong>Description</strong></td>
<td><strong><a href="/blog/monitoring-101-collecting-data/">Metric type</a></strong></td> 
<tbody>
<tr class="odd">
<td>accepts</td>
<td>Count of client connections attempted by NGINX</td>
<td>Resource: Utilization</td>
<tr class="even">
<td>handled</td>
<td>Count of successful client connections</td>
<td>Resource: Utilization</td>
</tr>
<tr class="odd">
<td>active</td>
<td>Currently active client connections</td>
<td>Resource: Utilization</td>
</tr>
<tr class="even">
<td>dropped (calculated)</td>
<td>Count of dropped connections (accepts – handled)</td>
<td>Work: Errors</td>
</tr>
<tr class="odd">
<td>requests</td>
<td>Count of client requests</td>
<td>Work: Throughput</td>
</tr>
<tr>
<td colspan="3"><em>*Strictly speaking, dropped connections is <a href="/blog/monitoring-101-collecting-data/#resource-metrics" target="_blank">a metric of resource saturation</a>, but since saturation causes NGINX to stop servicing some work (rather than queuing it up for later), “dropped” is best thought of as <a href="https://www.datadoghq.com/blog/monitoring-101-collecting-data/#work-metrics" target="_blank">a work metric.</a></em></td>
</tr>
</tbody>
</table>



The **accepts** counter is incremented when an NGINX worker picks up a request for a connection from the OS. If the worker fails to get a connection for the request (by establishing a new connection or reusing an open one), then the connection is dropped and **dropped** is incremented. Ordinarily connections are dropped because a resource limit, such as NGINX's [worker_connections](http://nginx.org/en/docs/ngx_core_module.html#worker_connections) limit has been reached.








-   **Waiting:** An active connection may also be in a Waiting substate if there is no active request at the moment. New connections can bypass this state and move directly to Reading, most commonly when using “accept filter” or “deferred accept”, in which case NGINX does not receive notice of work until it has enough data to begin working on the response. Connections will also be in the Waiting state after sending a response if the connection is set to keep-alive.
-   **Reading:** When a request is received, the connection moves out of the waiting state, and the request itself is counted as Reading. In this state NGINX is reading a client request header. Request headers are lightweight, so this is usually a fast operation.
-   **Writing:** After the request is read, it is counted as Writing, and remains in that state until a response is returned to the client. That means that the request is Writing while NGINX is waiting for results from upstream systems (systems “behind” NGINX), and while NGINX is operating on the response. Requests will often spend the majority of their time in the Writing state.




Often a connection will only support one request at a time. In this case, the number of Active connections == Waiting connections + Reading requests + Writing requests. However, HTTP/2 allows multiple concurrent requests/responses to be multiplexed over a connection, so Active may be less than the sum of Waiting, Reading, and Writing.



<h4>NGINX Plus</h4>



As mentioned above, all of open source NGINX’s metrics are available within NGINX Plus, but Plus can also report additional metrics. The section covers the metrics that are only available from NGINX Plus.

{{< img src="nginx-plus-connection-diagram-2.png" alt="connection, request states" popup="true" size="1x" >}}

Accepted, dropped, and total are ever-increasing counters. Active, idle, and current track the current number of connections or requests in each of those states, so they grow and shrink with request volume.



<table>
<tr class="header">
<th><strong>Name</strong></th>
<th><strong>Description</strong></th>
<th><strong><a href="https://www.datadoghq.com/blog/monitoring-101-collecting-data/">Metric Type</a></strong></th>
</tr>
<tbody>
<tr class="odd">
<td>accepted</td>
<td>Count of client connections attempted by NGINX</td>
<td>Resource: Utilization</td>
<tr class="even">
<td>dropped (calculated)</td>
<td>Count of dropped connections</td>
<td>Work: Errors</td>
</tr>
<tr class="odd">
<td>active</td>
<td>Currently active client connections</td>
<td>Resource: Utilization</td>
</tr>
<tr class="even">
<td>idle</td>
<td>Client connections with zero current requests</td>
<td>Resource: Utilizations</td>
</tr>
<tr class="odd">
<td>Total</td>
<td>Count of client requests</td>
<td>Work: Throughput</td>
</tr>
<tr>
<td colspan="3"><em>*Strictly speaking, dropped connections is <a href="/blog/monitoring-101-collecting-data/#resource-metrics" target="_blank">a metric of resource saturation</a>, but since saturation causes NGINX to stop servicing some work (rather than queuing it up for later), “dropped” is best thought of as <a href="https://www.datadoghq.com/blog/monitoring-101-collecting-data/#work-metrics" target="_blank">a work metric.</a></em></td>
</tr>
</tbody>
</table>



The **accepted** counter is incremented when an NGINX Plus worker picks up a request for a connection from the OS. If the worker fails to get a connection for the request (by establishing a new connection or reusing an open one), then the connection is dropped and dropped is incremented. Ordinarily connections are dropped because a resource limit, such as NGINX Plus’s worker_connections limit, has been reached. 


**Active** and **idle** are the same as “active” and “waiting” states in open source NGINX as described above, with one key exception: in open source NGINX, “waiting” falls under the “active” umbrella, whereas in NGINX Plus “idle” connections are excluded from the “active” count. **Current** is the same as the combined “reading + writing” states in open source NGINX. 


**Total** is a cumulative count of client requests. Note that a single client connection can involve multiple requests, so this number may be significantly larger than the cumulative number of connections. In fact, (total / accepted) yields the average number of requests per connection.





<table>
<thead>
<tr class="header">
<th>NGINX (open source)</th>
<th>NGINX Plus</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>accepts</td>
<td>accepted</td>
</tr>
<tr class="even">
<td>dropped must be calculated</td>
<td>dropped is reported directly</td>
</tr>
<tr class="odd">
<td>reading + writing</td>
<td>current</td>
</tr>
<tr class="even">
<td>waiting</td>
<td>idle</td>
</tr>
<tr class="odd">
<td>active (includes “waiting” states)</td>
<td>active (excludes “idle” states)</td>
</tr>
<tr class="even">
<td>requests</td>
<td>total</td>
</tr>
</tbody>
</table>





#### **Metric to alert on: Dropped connections**


The number of connections that have been dropped is equal to the difference between accepts and handled (NGINX) or is exposed directly as a standard metric (NGINX Plus). Under normal circumstances, dropped connections should be zero. If your rate of dropped connections per unit time starts to rise, look for possible resource saturation.

{{< img src="dropped-connections.png" alt="Dropped connections" popup="true" size="1x" >}}



#### **Metric to alert on: Requests per second**


Sampling your request data (**requests** in open source, or **total** in Plus) with a fixed time interval provides you with the number of requests you’re receiving per unit of time—often minutes or seconds. Monitoring this metric can alert you to spikes in incoming web traffic, whether legitimate or nefarious, or sudden drops, which are usually indicative of problems. A drastic change in requests per second can alert you to problems brewing somewhere in your environment, even if it cannot tell you exactly where those problems lie. Note that all requests are counted the same, regardless of their URLs.

{{< img src="requests-per-sec.png" alt="Requests per second" popup="true" size="1x" >}}

#### Collecting activity metrics


Open source NGINX exposes these basic server metrics on a simple status page. Because the status information is displayed in a standardized form, virtually any graphing or monitoring tool can be configured to parse the relevant data for analysis, visualization, or alerting. NGINX Plus provides a JSON feed with much richer data. Read the companion post on [NGINX metrics collection](/blog/how-to-collect-nginx-metrics/) for instructions on enabling metrics collection.



### Error metrics




<table>
<thead>
<tr class="header">
<th><strong>Name</strong></th>
<th><strong>Description</strong></th>
<th><strong><a href="/blog/monitoring-101-collecting-data/">Metric type</a></strong></th>
<th><strong>Availability</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>4xx codes</td>
<td>Count of client errors such as "403 Forbidden" or "404 Not Found"</td>
<td>Work: Errors</td>
<td>NGINX logs, NGINX Plus</td>
</tr>
<tr class="even">
<td>5xx codes</td>
<td>Count of server errors such as "500 Internal Server Error" or "502 Bad Gateway"</td>
<td>Work: Errors</td>
<td>NGINX logs, NGINX Plus</td>
</tr>
</tbody>
</table>



NGINX error metrics tell you how often your servers are returning errors instead of producing useful work. Client errors are represented by 4xx status codes, server errors with 5xx status codes.



#### **Metric to alert on: Server error rate**


Your server error rate is equal to the number of 5xx errors, such as "502 Bad Gateway", divided by the total number of [status codes](http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html) (1xx, 2xx, 3xx, 4xx, 5xx), per unit of time (often one to five minutes). If your error rate starts to climb over time, investigation may be in order. If it spikes suddenly, urgent action may be required, as clients are likely to report errors to the end user.

{{< img src="5xx-rate.png" alt="Server error rate" popup="true" size="1x" >}}

A note on client errors: while it is tempting to monitor 4xx, there is limited information you can derive from that metric since it measures client behavior without offering any insight into particular URLs. In other words, a change in 4xx could be noise, e.g. web scanners blindly looking for vulnerabilities.

#### Collecting error metrics


Although open source NGINX does not make error rates immediately available for monitoring, there are at least two ways to capture that information:

1. Use the expanded status module available with commercially supported NGINX Plus
2. Configure NGINX’s log module to write response codes in access log

Read the companion post on NGINX metrics collection for detailed instructions on both approaches.



### Performance metrics




<table>
<thead>
<tr class="header">
<th><strong>Name</strong></th>
<th><strong>Description</strong></th>
<th><strong><a href="/blog/monitoring-101-collecting-data/">Metric type</a></strong></th>
<th><strong>Availability</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>request time</td>
<td>Time to process each request, in seconds</td>
<td>Work: Performance</td>
<td>NGINX logs</td>
</tr>
</tbody>
</table>





#### **Metric to alert on: Request processing time**


The request time metric logged by NGINX records the processing time for each request, from the reading of the first client bytes to fulfilling the request. Long response times can point to problems upstream.

#### Collecting processing time metrics


NGINX and NGINX Plus users can capture data on processing time by adding the `$request_time` variable to the access log format. More details on configuring logs for monitoring are available in our companion post on [NGINX metrics collection](/blog/how-to-collect-nginx-metrics/).

### Reverse proxy metrics




<table>
<thead>
<tr class="header">
<th><strong>Name</strong></th>
<th><strong>Description</strong></th>
<th><strong><a href="/blog/monitoring-101-collecting-data/">Metric type</a></strong></th>
<th><strong>Availability</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Active connections by upstream server</td>
<td>Currently active client connections</td>
<td>Resource: Utilization</td>
<td>NGINX Plus</td>
</tr>
<tr class="even">
<td>5xx codes by upstream server</td>
<td>Server errors</td>
<td>Work: Errors</td>
<td>NGINX Plus</td>
</tr>
<tr class="odd">
<td>Available servers per upstream group</td>
<td>Servers passing health checks</td>
<td>Resource: Availability</td>
<td>NGINX Plus</td>
</tr>
</tbody>
</table>



One of the most common ways to use NGINX is as a [reverse proxy](https://en.wikipedia.org/wiki/Reverse_proxy). The commercially supported NGINX Plus exposes a large number of metrics about backend (or “upstream”) servers, which are relevant to a reverse proxy setup. This section highlights a few of the key upstream metrics that are available to users of NGINX Plus.

NGINX Plus segments its upstream metrics first by group, and then by individual server. So if, for example, your reverse proxy is distributing requests to five upstream web servers, you can see at a glance whether any of those individual servers is overburdened, and also whether you have enough healthy servers in the upstream group to ensure good response times.

#### **Activity metrics**


The number of **active connections per upstream server** can help you verify that your reverse proxy is properly distributing work across your server group. If you are using NGINX as a load balancer, significant deviations in the number of connections handled by any one server can indicate that the server is struggling to process requests in a timely manner or that the load-balancing method (e.g., [round-robin or IP hashing](http://nginx.com/blog/load-balancing-with-nginx-plus/)) you have configured is not optimal for your traffic patterns.

#### Error metrics


Recall from the error metric section above that 5xx (server error) codes, such as "502 Bad Gateway" or "503 Service Temporarily Unavailable", are a valuable metric to monitor, particularly as a share of total response codes. NGINX Plus allows you to easily extract the number of **5xx codes per upstream server**, as well as the total number of responses, to determine that particular server’s error rate.

#### **Availability metrics**


For another view of the health of your web servers, NGINX also makes it simple to monitor the health of your upstream groups via the total number of **servers currently available within each group**. In a large reverse proxy setup, you may not care very much about the current state of any one server, just as long as your pool of available servers is capable of handling the load. But monitoring the total number of servers that are up within each upstream group can provide a very high-level view of the aggregate health of your web servers.

#### **Collecting upstream metrics**


NGINX Plus upstream metrics are exposed on the internal NGINX Plus monitoring dashboard, and are also available via a JSON interface that can serve up metrics into virtually any external monitoring platform. See examples in our companion post on [collecting NGINX metrics](/blog/how-to-collect-nginx-metrics/).

Conclusion
----------


In this post we’ve touched on some of the most useful metrics you can monitor to keep tabs on your NGINX servers. If you are just getting started with NGINX, monitoring most or all of the metrics in the list below will provide good visibility into the health and activity levels of your web infrastructure:



-   [Dropped connections](#metric-to-alert-on-dropped-connections)
-   [Requests per second](#metric-to-alert-on-requests-per-second)
-   [Server error rate](#metric-to-alert-on-server-error-rate)
-   [Request processing time](#metric-to-alert-on-request-processing-time)



Eventually you will recognize additional, more specialized metrics that are particularly relevant to your own infrastructure and use cases. Of course, what you monitor will depend on the tools you have and the metrics available to you. See the companion post for [step-by-step instructions on metric collection](/blog/how-to-collect-nginx-metrics/), whether you use NGINX or NGINX Plus.

At Datadog, we have built integrations with both NGINX and NGINX Plus so that you can begin collecting and monitoring metrics from all your web servers with a minimum of setup. Monitor NGINX with Datadog [in this post](/blog/how-to-monitor-nginx-with-datadog/), and get started right away with [a free trial of Datadog](https://app.datadoghq.com/signup).

Acknowledgments
---------------


Many thanks to the NGINX team for reviewing this article prior to publication and providing important feedback and clarifications.

------------------------------------------------------------------------


**Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/nginx/how_to_monitor_nginx.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues).**
