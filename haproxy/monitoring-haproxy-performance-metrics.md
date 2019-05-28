# Monitoring HAProxy performance metrics


*This post is part 1 of a 3-part series on HAProxy monitoring. [Part 2](http://www.datadoghq.com/blog/how-to-collect-haproxy-metrics) details how to collect metrics from HAProxy, and [Part 3](http://www.datadoghq.com/blog/monitor-haproxy-with-datadog) details how Datadog can help you monitor HAProxy.*

What is HAProxy?

HAProxy is an open source solution for load balancing and reverse proxying both TCP and HTTP requests—and, in keeping with the abbreviation in its name, it is [high availability](https://en.wikipedia.org/wiki/High_availability). HAProxy can continue to operate in the presence of failed backend servers, handling crossover reliably and seamlessly. It also has built-in health checks that will remove a backend if it fails several health checks in a row. With dynamic routing you can transfer incoming traffic to a variety of backend servers, fully configurable with Access Control Lists (ACLs).

HAProxy consistently performs on par or [better](https://github.com/observing/balancerbattle) in benchmarks against other popular reverse proxies like http-proxy or the NGINX webserver. It is a fundamental element in the architecture of many high-profile websites such as GitHub, Instagram, Twitter, Stack Overflow, Reddit, Tumblr, Yelp, and [many more](http://www.haproxy.org/they-use-it.html).

Like other load balancers or proxies, HAProxy is very flexible and largely protocol-agnostic—it can handle anything sent over TCP.

{{< img src="haproxy-1.png" alt="Overview" popup="true" size="1x">}}

Key HAProxy performance metrics

A properly functioning HAProxy setup can [handle](http://loadbalancer.org/blog/load-balancer-performance-benchmarking-haproxy-on-ec2-quick-and-dirty-style) a [significant amount of traffic](http://www.goperf.com/haproxy-experimental-evaluation-of-the-performance/). However, because it is the first point of contact, poor load balancer performance will increase latency across your entire stack.

The best way to ensure proper HAProxy performance and operation is by [monitoring its key metrics](https://www.datadoghq.com/blog/haproxy-monitoring/) in three broad areas:



-   [**Frontend metrics**](#frontend-metrics) such as client connections and requests
-   [**Backend metrics**](#backend-metrics) such as availability and health of backend servers
-   [**Health metrics**](#health-metrics) that reflect the state of your HAProxy setup



Correlating frontend metrics with backend metrics gives you a more comprehensive view of your infrastructure and helps you quickly identify potential hotspots.

{{< img src="default-screen2.png" alt="Frontend and backend metrics" popup="true" size="1x">}}

Read more about collecting HAProxy performance metrics in [part two](http://www.datadoghq.com/blog/how-to-collect-haproxy-metrics) of this series.

This article references metric terminology [introduced in our Monitoring 101 series](https://www.datadoghq.com/blog/monitoring-101-collecting-data/), which provides a framework for metric collection and alerting.

### Frontend metrics

{{< img src="haproxy-2.png" alt="HAProxy frontend metrics" popup="true" size="1x">}}

Frontend metrics provide information about the client’s interaction with the load balancer itself.



<table>
<thead>
<tr class="header">
<th><strong>Name</strong></th>
<th><strong>Description</strong></th>
<th><strong><a href="https://www.datadoghq.com/blog/monitoring-101-collecting-data/">Metric Type</a></strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>req_rate</td>
<td>HTTP requests per second</td>
<td>Work: Throughput</td>
</tr>
<tr class="even">
<td>rate</td>
<td>Number of sessions created per second</td>
<td>Resource: Utilization</td>
</tr>
<tr class="odd">
<td>session utilization (computed)</td>
<td>Percentage of sessions used (<em>scur / slim * 100</em>)</td>
<td>Resource: Utilization</td>
</tr>
<tr class="even">
<td>ereq</td>
<td>Number of request errors</td>
<td>Work: Error</td>
</tr>
<tr class="odd">
<td>dreq</td>
<td>Requests denied due to security concerns (ACL-restricted)</td>
<td>Work: Error</td>
</tr>
<tr class="even">
<td>hrsp_4xx</td>
<td>Number of HTTP client errors</td>
<td>Work: Error</td>
</tr>
<tr class="odd">
<td>hrsp_5xx</td>
<td>Number of HTTP server errors</td>
<td>Work: Error</td>
</tr>
<tr class="even">
<td>bin</td>
<td>Number of bytes received by the frontend</td>
<td>Resource: Utilization</td>
</tr>
<tr class="odd">
<td>bout</td>
<td>Number of bytes sent by the frontend</td>
<td>Resource: Utilization</td>
</tr>
</tbody>
</table>



A note about terminology: HAProxy documentation often uses the terms sessions, connections, and requests together, and it is easy to get lost.

Each client that interacts with HAProxy uses one session. A session is composed of two connections, one from the client to HAProxy, and the other from HAProxy to the appropriate backend server. Once a session has been created (i.e. the client can talk to the backend through HAProxy), the client can begin issuing requests. A client will typically use one session for all of its requests, with sessions terminating after receiving no requests during the timeout window.

#### Frontend metrics to watch:

{{< img src="frontend-req-rate.png" alt="Frontend requests per second" size="1x">}}

**req_rate**: The frontend request rate measures the number of requests received over the last second. Keeping an eye on peaks and drops is essential to ensure continuous service availability. In the event of a traffic spike, clients could see increases in latency or even denied connections. Tracking your request rate over time gives you the data you need to make more informed decisions about HAProxy’s configuration.

{{< img src="f-sessions-second.png" alt="Frontend sessions per second" size="1x">}}

**rate**: HAProxy allows you to configure the maximum number of sessions created per second. If you are not behind a content delivery network (CDN), a significant spike in the number of sessions over a short period could cripple your operations and bring your servers to their knees. Tracking your session creation rate over time can help you discern whether a traffic spike was a unique event or part of a larger trend. You can then set a limit based on historic trends and resource availability so that a sudden and dramatic spike does not result in a denial of service.

{{< img src="response-codes.png" alt="Response codes" caption="Frontends are purple, backends blue" popup="true" size="1x">}}

**hrsp\_4xx and hrsp\_5xx**: HAProxy exposes the number of responses by HTTP status code. Ideally, all responses forwarded by HAProxy would be class **2xx** codes, so an unexpected surge in the number of other code classes could be a sign of trouble.

Correlating the denial metrics with the response code data can shed light on the cause of an increase in error codes. No change in denials coupled with an increase in the number of **404** responses could point to a misconfigured application or unruly client.

Over the course of our internal testing, we graphed the frontend and backend metrics together, one graph per response code, with interesting results.

{{< img src="4xx1.png" alt="4xx codes" size="1x">}}

The difference in the **4xx** responses is explained by the [tendency of some browsers to preconnect](http://www.copernica.com/en/blog/how-chromes-pre-connect-breaks-haproxy-and-http), sometimes resulting in a **408** (request timeout) response. If you are seeing excessive **4xx** responses and suspect them to be **408** codes, you can try [this temporary workaround](http://blog.haproxy.com/2014/05/26/haproxy-and-http-errors-408-in-chrome/) and see if that reduces the number of **4xx** responses.

**bin/bout**: When monitoring high traffic servers, network throughput is a great place to start. Observing traffic volume over time is essential to determine if changes to your network infrastructure are needed. A 10Mb/s pipe might work for a startup getting its feet wet, but is insufficient for larger traffic volumes. Tracking HAProxy’s network usage will empower you to scale your infrastructure with your ever-changing needs.

#### Frontend metrics to alert on:

**session usage (computed)**: For every HAProxy session, two connections are consumed—one for the client to HAProxy, and the other for HAProxy to your backend. Ultimately, the maximum number of connections HAProxy can handle is limited by your configuration and platform (there are [only so many file descriptors](https://docs.oracle.com/cd/E23389_01/doc.11116/e21036/perf002.htm) available).

Alerting on this metric is essential to ensure your server has sufficient capacity to handle all concurrent sessions. Unlike requests, upon reaching the session limit HAProxy will deny additional clients until resource consumption drops. Furthermore, if you find your session usage percentage to be hovering above 80%, it could be time to either [modify HAProxy’s configuration](https://cbonte.github.io/haproxy-dconv/configuration-1.5.html#3.2-maxconn) to allow more sessions, or migrate your HAProxy server to a bigger box.

Remember that sessions and connections are related—consistently high traffic volumes might necessitate an increase in the number of maximum connections HAProxy allows or even require you to add an additional HAProxy instance. Upon reaching its connection limit, HAProxy will continue to accept and queue connections unless or until the backend server handling the requests fails.

This metric is not emitted by HAProxy explicitly and must be calculated by dividing the current number of sessions (`scur`) by the session limit (`slim`) and multiplying the result by 100.

Keep in mind that if HAProxy’s `keep-alive` functionality is enabled (as it is by default), your number of sessions includes sessions not yet closed due to inactivity.

**dreq**: HAProxy provides sophisticated information containment controls out of the box with ACLs. Properly configured ACLs can prevent HAProxy from serving requests that contain sensitive material. Similarly to a web application firewall, you can use ACLs to block database requests from non-local connections, for example, but ACLs are highly configurable—you can even deny requests or responses that [match a regex](https://cbonte.github.io/haproxy-dconv/configuration-1.5.html#7.1.4).

This metric tracks the number of requests denied due to security restrictions. You should be alerted in the event of a significant increase in denials—a malicious attacker or misconfigured application could be to blame. More information on designing ACLs for HAProxy can be found in the [documentation](https://cbonte.github.io/haproxy-dconv/configuration-1.5.html#7).

An increase in denied requests will subsequently cause an increase in **403 Forbidden** codes. Correlating the two can help you discern the root cause of an increase in **4xx** responses.

**ereq**: Similar to `dreq`, this metric exposes the number of request errors. Client-side request errors could have a number of causes:



-   client terminates before sending request
-   read error from client
-   client timeout
-   client terminated connection
-   request was [tarpitted](https://en.wikipedia.org/wiki/Tarpit_(networking))/subject to ACL



Under normal conditions, it is acceptable to (infrequently) receive invalid requests from clients. However, a significant increase in the number of invalid requests received could be a sign of larger, looming issues.

For example, an abnormal number of terminations or timeouts by numerous clients could mean that your application is experiencing excessive latency, causing clients to manually close their connections.

### Backend metrics

{{< img src="haproxy-3-1.png" alt="HAProxy backend metrics" popup="true" size="1x">}}

Backend metrics measure the communication between HAProxy and your backend servers that handle client requests. Monitoring your backend is critical to ensure smooth and responsive performance of your web applications.



<table>
<thead>
<tr class="header">
<th><strong>Name</strong></th>
<th><strong>Description</strong></th>
<th><strong><a href="https://www.datadoghq.com/blog/monitoring-101-collecting-data/">Metric Type</a></strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>rtime</td>
<td>Average backend response time (in ms) for the last 1,024 requests (v1.5+)</td>
<td>Work: Throughput</td>
</tr>
<tr class="even">
<td>econ</td>
<td>Number of requests that encountered an error attempting to connect to a backend server</td>
<td>Work: Error</td>
</tr>
<tr class="odd">
<td>dresp</td>
<td>Responses denied due to security concerns (ACL-restricted)</td>
<td>Work: Error</td>
</tr>
<tr class="even">
<td>eresp</td>
<td>Number of requests whose responses yielded an error</td>
<td>Work: Error</td>
</tr>
<tr class="odd">
<td>qcur</td>
<td>Current number of requests unassigned in queue</td>
<td>Resource: Saturation</td>
</tr>
<tr class="even">
<td>qtime</td>
<td>Average time spent in queue (in ms) for the last 1,024 requests (v1.5+)</td>
<td>Resource: Saturation</td>
</tr>
<tr class="odd">
<td>wredis</td>
<td>Number of times a request was redispatched to a different backend</td>
<td>Resource: Availability</td>
</tr>
<tr class="even">
<td>wretr</td>
<td>Number of times a connection was retried</td>
<td>Resource: Availability</td>
</tr>
</tbody>
</table>



#### Backend metrics to watch:

**econ**: Backend connection failures should be acted upon immediately. Unfortunately, the `econ` metric not only includes failed backend requests but additionally includes general backend errors, like a backend without an active frontend. Thankfully, correlating this metric with `eresp` and response codes from both your frontend and backend servers will give you a better idea of the causes of an increase in backend connection errors.

**dresp**: In most cases your denials will originate in the frontend (e.g., a user is attempting to access an unauthorized URL). However, sometimes a request may be benign, yet the corresponding response contains sensitive information. In that case, you would want to [set up an ACL](https://cbonte.github.io/haproxy-dconv/configuration-1.5.html#7) to deny the offending response. Backend responses that are denied due to ACL restrictions will emit a **502** error code. With properly configured access controls on your frontend, this metric should stay at or near zero.

Denied responses and an increase in **5xx** responses go hand-in-hand. If you are seeing a large number of **5xx** responses, you should check your denied responses to shed some light on the increase in error codes.

{{< img src="retries.png" alt="Retries and Redispatches" size="1x">}}

**wretr**: Some dropped or timed-out connections are to be expected when connecting to a backend server. The retry rate represents the number of times a connection to a backend server was retried. This metric is usually non-zero under normal operating conditions. Should you begin to see more retries than usual, it is likely that other metrics will also change, including `econ` and `eresp`.

Tracking the retry rate in addition to the above two error metrics can shine some light on the true cause of an increase in errors; if you are seeing more errors coupled with low retry rates, the problem most likely resides elsewhere.

**wredis**: The redispatch rate metric tracks the number of times a client connection was unable to reach its original target, and was subsequently sent to a different server. If a client holds a cookie referencing a backend server that is down, the default action is to respond to the client with a **502** status code. However, if you have [enabled](https://cbonte.github.io/haproxy-dconv/configuration-1.5.html#4-option%20redispatch) `option redispatch` in your `haproxy.cfg`, the request will be sent to any available backend server and the cookie will be ignored. It’s a matter of preference whether you want to trade user session persistence for smoother transitions in the face of failed backends.

#### Backend metrics to alert on:

**qcur**: If your backend is bombarded with connections to the point you have reached your global `maxconn` limit, HAProxy will [seamlessly queue new connections](https://stackoverflow.com/questions/8750518/difference-between-global-maxconn-and-server-maxconn-haproxy) in your system kernel’s socket queue until a backend server becomes available.

The `qcur` metric tracks the current number of connections awaiting assignment to a backend server. If you have enabled cookies and the listed server is unavailable, connections will be queued until the queue timeout is reached. However, if you have set the `option redispatch` directive in your global HAProxy configuration, HAProxy can break the session’s persistence and forward the request to any available backend.

Keeping connections out of the queue is ideal, resulting in less latency and a better user experience. You should alert if the size of your queue exceeds a threshold you are comfortable with. If you find that connections are consistently enqueueing, configuration changes may be in order, such as [increasing](https://cbonte.github.io/haproxy-dconv/configuration-1.5.html#3.2-maxconn) your global `maxconn` limit or changing the connection limits on your individual backend servers.

{{< img src="queue.png" alt="Backend queue" caption="An empty queue is a happy queue" size="1x">}}

**qtime (v1.5+)**: In addition to the queue size, HAProxy exposes the average time spent in queue via the `qtime` metric. This metric represents an average of the last 1,024 requests, so an abnormally large queue time for one connection could skew results. It goes without saying that minimizing time spent in the queue results in lower latency and an overall better client experience. Each use case can tolerate a certain amount of queue time but in general, you should aim to keep this value as low as possible.

{{< img src="response-time.png" alt="Backend response time" size="1x">}}

**rtime (v1.5+)**: Tracking average response times is an effective way to measure the latency of your load-balancing setup. Generally speaking, response times in excess of 500 ms will lead to degradation of application performance and customer experience. Monitoring the average response time can give you the upper hand to respond to latency issues before your customers are substantially impacted.

*Keep in mind* that this metric will be [zero if you are not using HTTP](https://cbonte.github.io/haproxy-dconv/configuration-1.5.html#9.1) (see \#60).

**eresp**: The backend error response rate represents the number of response errors generated by your backends. This includes errors caused by data transfers aborted by the servers as well as write errors on the client socket and failures due to ACLs. Combined with other error metrics, the backend error response rate helps diagnose the root cause of response errors. For example, an increase in both the backend error response rate and denied responses could indicate that clients are repeatedly attempting to access ACL-ed resources.

### Health metrics

HAProxy can also expose information about the health of each front and backend server, in addition to the metrics listed above. Health checks are not enabled by default, and require you to set the [`check` directive](https://cbonte.github.io/haproxy-dconv/configuration-1.5.html#5.2-check) in your HAProxy configuration. Once set up, HAProxy will regularly perform health checks on all enabled servers.

If a health check fails three times in a row (configurable with the `rise` directive), it is marked in a **DOWN** state. Monitoring the health of your HAProxy servers gives you the information you need to quickly respond to outages as they occur. Health checks are highly configurable, with specific checks available for MySQL, SMTP, Redis and others. [Refer to the documentation](https://cbonte.github.io/haproxy-dconv/configuration-1.5.html#option%20httpchk) to take full advantage of HAProxy’s powerful health-checking features.

### Conclusion

In this post we’ve covered some of the most important metrics you can monitor to keep tabs on your HAProxy setup. If you are just getting started with HAProxy, monitoring the metrics mentioned below will provide good visibility into the health and performance of your load balancing infrastructure:



-   [Session utilization](#frontend-metrics-to-alert-on)
-   [Latency](#backend-metrics-to-alert-on)
-   [Denials](#backend-metrics-to-watch)
-   [Queue length and queue time](#backend-metrics-to-alert-on)



Eventually you will recognize additional metrics that are particularly relevant to your own infrastructure and use cases.

In the [next post](http://www.datadoghq.com/blog/how-to-collect-haproxy-metrics) of this series, we provide step-by-step instructions on collecting HAProxy performance metrics.


*Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/haproxy/monitoring_haproxy_performance_metrics.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/datadog/the-monitor/issues).*
