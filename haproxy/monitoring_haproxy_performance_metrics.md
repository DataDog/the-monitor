#Monitoring HAProxy performance metrics
_This post is part 1 of a 3-part series on HAProxy monitoring. [Part 2](http://www.datadoghq.com/blog/how-to-collect-haproxy-metrics) details how to collect metrics from HAProxy, and [Part 3](http://www.datadoghq.com/blog/monitor-haproxy-with-datadog) details how Datadog can help you monitor HAProxy._

## What is HAProxy?

HAProxy is an open source solution for load balancing and reverse proxying both TCP and HTTP requests—and, in keeping with the abbreviation in its name, it is [high availability](https://en.wikipedia.org/wiki/High_availability). HAProxy can continue to operate in the presence of failed backend servers, handling crossover reliably and seamlessly. It also has built-in health checks that will remove a backend if it fails several health checks in a row. With dynamic routing you can transfer incoming traffic to a variety of backend servers, fully configurable with Access Control Lists (ACLs). 

HAProxy consistently performs on par or [better](https://github.com/observing/balancerbattle) in benchmarks against other popular reverse proxies like http-proxy or the NGINX webserver. It is a fundamental element in the architecture of many high-profile websites such as GitHub, Instagram, Twitter, Stack Overflow, Reddit, Tumblr, Yelp, and [many more](http://www.haproxy.org/they-use-it.html). 

Like other load balancers or proxies, HAProxy is very flexible and largely protocol-agnostic—it can handle anything sent over TCP. 

[![Overview](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-10-haproxy/HAProxy_1.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-10-haproxy/HAProxy_1.png)

## Key HAProxy performance metrics

A properly functioning HAProxy setup can [handle](http://loadbalancer.org/blog/load-balancer-performance-benchmarking-haproxy-on-ec2-quick-and-dirty-style) a [significant amount of traffic](http://www.goperf.com/haproxy-experimental-evaluation-of-the-performance/). However, because it is the first point of contact, poor load balancer performance will increase latency across your entire stack. The best way to ensure proper HAProxy performance and operation is by [monitoring its key metrics](https://www.datadoghq.com/blog/haproxy-monitoring/) in three broad areas:

*   [**Frontend metrics**](#Frontend) such as client connections and requests
*   [**Backend metrics**](#Backend) such as availability and health of backend servers
*   [**Health metrics**](#Health) that reflect the state of your HAProxy setup

Correlating frontend metrics with backend metrics gives you a more comprehensive view of your infrastructure and helps you quickly identify potential hotspots. 

[![Frontend and backend metrics](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-10-haproxy/default-screen2.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-10-haproxy/default-screen2.png) 

Read more about collecting HAProxy performance metrics in [part two](http://www.datadoghq.com/blog/how-to-collect-haproxy-metrics) of this series. This article references metric terminology [introduced in our Monitoring 101 series](https://www.datadoghq.com/blog/monitoring-101-collecting-data/), which provides a framework for metric collection and alerting.

<div class="anchor" id="Frontend" />

### Frontend metrics

[![HAProxy frontend metrics](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-10-haproxy/HAProxy_2.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-10-haproxy/HAProxy_2.png) Frontend metrics provide information about the client’s interaction with the load balancer itself.

|**Name**|**Description**|**[Metric Type](https://www.datadoghq.com/blog/monitoring-101-collecting-data/)**|
|:---:|:---:|:---:|
|req\_rate|HTTP requests per second|Work: Throughput|
|rate|Number of sessions created per second|Resource: Utilization|
|session utilization (computed)|Percentage of sessions used (_scur / slim * 100_)|Resource: Utilization|
|ereq|Number of request errors|Work: Error|
|dreq|Requests denied due to security concerns (ACL-restricted)|Work: Error|
|hrsp\_4xx|Number of HTTP client errors|Work: Error|
|hrsp\_5xx|Number of HTTP server errors|Work: Error|
|bin|Number of bytes received by the frontend|Resource: Utilization|
|bout|Number of bytes sent by the frontend|Resource: Utilization|

A note about terminology: HAProxy documentation often uses the terms sessions, connections, and requests together, and it is easy to get lost. Each client that interacts with HAProxy uses one session. A session is composed of two connections, one from the client to HAProxy, and the other from HAProxy to the appropriate backend server. Once a session has been created (i.e. the client can talk to the backend through HAProxy), the client can begin issuing requests. A client will typically use one session for all of its requests, with sessions terminating after receiving no requests during the timeout window.

#### Metrics to watch:

![Frontend requests per second](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-10-haproxy/frontend-req-rate.png) 

**req_rate**: The frontend request rate measures the number of requests received over the last second. Keeping an eye on peaks and drops is essential to ensure continuous service availability. In the event of a traffic spike, clients could see increases in latency or even denied connections. Tracking your request rate over time gives you the data you need to make more informed decisions about HAProxy’s configuration. 

![Frontend sessions per second](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-10-haproxy/f-sessions-second.png) 

**rate**: HAProxy allows you to configure the maximum number of sessions created per second. If you are not behind a content delivery network (CDN), a significant spike in the number of sessions over a short period could cripple your operations and bring your servers to their knees. 

Tracking your session creation rate over time can help you discern whether a traffic spike was a unique event or part of a larger trend. You can then set a limit based on historic trends and resource availability so that a sudden and dramatic spike does not result in a denial of service. 

[![Response codes](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-10-haproxy/response-codes.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-10-haproxy/response-codes.png)

<center>_Frontends are purple, backends blue_</center>

**hrsp\_4xx and hrsp\_5xx**: HAProxy exposes the number of responses by HTTP status code. Ideally, all responses forwarded by HAProxy would be class **2xx** codes, so an unexpected surge in the number of other code classes could be a sign of trouble. Correlating the denial metrics with the response code data can shed light on the cause of an increase in error codes. No change in denials coupled with an increase in the number of **404** responses could point to a misconfigured application or unruly client. Over the course of our internal testing, we graphed the frontend and backend metrics together, one graph per response code, with interesting results. 

![4xx codes](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-10-haproxy/4xx1.png) 

The difference in the **4xx** responses is explained by the [tendency of some browsers to preconnect](http://www.copernica.com/en/blog/how-chromes-pre-connect-breaks-haproxy-and-http), sometimes resulting in a **408** (request timeout) response. If you are seeing excessive **4xx** responses and suspect them to be **408** codes, you can try [this temporary workaround](http://blog.haproxy.com/2014/05/26/haproxy-and-http-errors-408-in-chrome/) and see if that reduces the number of **4xx** responses. 

**bin/bout**: When monitoring high traffic servers, network throughput is a great place to start. Observing traffic volume over time is essential to determine if changes to your network infrastructure are needed. A 10Mb/s pipe might work for a startup getting its feet wet, but is insufficient for larger traffic volumes. Tracking HAProxy’s network usage will empower you to scale your infrastructure with your ever-changing needs.

#### Metrics to alert on:

<div class="anchor" id="Utilization" />

**session usage (computed)**: For every HAProxy session, two connections are consumed—one for the client to HAProxy, and the other for HAProxy to your backend. Ultimately, the maximum number of connections HAProxy can handle is limited by your configuration and platform (there are [only so many file descriptors](https://docs.oracle.com/cd/E23389_01/doc.11116/e21036/perf002.htm) available). 

Alerting on this metric is essential to ensure your server has sufficient capacity to handle all concurrent sessions. Unlike requests, upon reaching the session limit HAProxy will deny additional clients until resource consumption drops. Furthermore, if you find your session usage percentage to be hovering above 80%, it could be time to either [modify HAProxy’s configuration](https://cbonte.github.io/haproxy-dconv/configuration-1.5.html#3.2-maxconn) to allow more sessions, or migrate your HAProxy server to a bigger box. 

Remember that sessions and connections are related—consistently high traffic volumes might necessitate an increase in the number of maximum connections HAProxy allows or even require you to add an additional HAProxy instance. Upon reaching its connection limit, HAProxy will continue to accept and queue connections unless or until the backend server handling the requests fails. 

This metric is not emitted by HAProxy explicitly and must be calculated by dividing the current number of sessions (`scur`) by the session limit (`slim`) and multiplying the result by 100. Keep in mind that if HAProxy’s `keep-alive` functionality is enabled (as it is by default), your number of sessions includes sessions not yet closed due to inactivity. 

<div class="anchor" id="Denials" />

**dreq**: HAProxy provides sophisticated information containment controls out of the box with ACLs. Properly configured ACLs can prevent HAProxy from serving requests that contain sensitive material. Similarly to a web application firewall, you can use ACLs to block database requests from non-local connections, for example, but ACLs are highly configurable—you can even deny requests or responses that [match a regex](https://cbonte.github.io/haproxy-dconv/configuration-1.5.html#7.1.4). 

This metric tracks the number of requests denied due to security restrictions. You should be alerted in the event of a significant increase in denials—a malicious attacker or misconfigured application could be to blame. More information on designing ACLs for HAProxy can be found in the [documentation](https://cbonte.github.io/haproxy-dconv/configuration-1.5.html#7). An increase in denied requests will subsequently cause an increase in **403 Forbidden** codes. 

Correlating the two can help you discern the root cause of an increase in **4xx** responses. **ereq**: Similar to `dreq`, this metric exposes the number of request errors. Client-side request errors could have a number of causes:

*   client terminates before sending request
*   read error from client
*   client timeout
*   client terminated connection
*   request was [tarpitted](https://en.wikipedia.org/wiki/Tarpit_(networking))/subject to ACL

Under normal conditions, it is acceptable to (infrequently) receive invalid requests from clients. However, a significant increase in the number of invalid requests received could be a sign of larger, looming issues. For example, an abnormal number of terminations or timeouts by numerous clients could mean that your application is experiencing excessive latency, causing clients to manually close their connections.

<div class="anchor" id="Backend" />

### Backend metrics

[![HAProxy backend metrics](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-10-haproxy/HAProxy_3-1.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-10-haproxy/HAProxy_3-1.png) Backend metrics measure the communication between HAProxy and your backend servers that handle client requests. Monitoring your backend is critical to ensure smooth and responsive performance of your web applications.

|**Name**| **Description** |**[Metric Type](https://www.datadoghq.com/blog/monitoring-101-collecting-data/)**|
|:---:|:---:|:---:|
| rtime | Average backend response time (in ms) for the last 1,024 requests | Work: Throughput |
| econ | Number of requests that encountered an error attempting to connect to a backend server|Work: Error|
|dresp|Responses denied due to security concerns (ACL-restricted)|Work: Error|
|eresp|Number of requests whose responses yielded an error|Work: Error|
|qcur|Current number of requests unassigned in queue|Resource: Saturation|
|qtime|Average time spent in queue (in ms) for the last 1,024 requests|Resource: Saturation|
|wredis|Number of times a request was redispatched to a different backend|Resource: Availability|
|wretr|Number of times a connection was retried|Resource: Availability|
#### Metrics to watch:

**econ**: Backend connection failures should be acted upon immediately. Unfortunately, the `econ` metric not only includes failed backend requests but additionally includes general backend errors, like a backend without an active frontend. Thankfully, correlating this metric with `eresp` and response codes from both your frontend and backend servers will give you a better idea of the causes of an increase in backend connection errors. 

**dresp**: In most cases your denials will originate in the frontend (e.g., a user is attempting to access an unauthorized URL). However, sometimes a request may be benign, yet the corresponding response contains sensitive information. In that case, you would want to [set up an ACL](https://cbonte.github.io/haproxy-dconv/configuration-1.5.html#7) to deny the offending response. Backend responses that are denied due to ACL restrictions will emit a **502** error code. With properly configured access controls on your frontend, this metric should stay at or near zero. Denied responses and an increase in **5xx** responses go hand-in-hand. If you are seeing a large number of **5xx** responses, you should check your denied responses to shed some light on the increase in error codes. 

![Retries and Redispatches](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-10-haproxy/retries.png) 

**wretr**: Some dropped or timed-out connections are to be expected when connecting to a backend server. The retry rate represents the number of times a connection to a backend server was retried. This metric is usually non-zero under normal operating conditions. Should you begin to see more retries than usual, it is likely that other metrics will also change, including `econ` and `eresp`. Tracking the retry rate in addition to the above two error metrics can shine some light on the true cause of an increase in errors; if you are seeing more errors coupled with low retry rates, the problem most likely resides elsewhere. **wredis**: The redispatch rate metric tracks the number of times a client connection was unable to reach its original target, and was subsequently sent to a different server. If a client holds a cookie referencing a backend server that is down, the default action is to respond to the client with a **502** status code. However, if you have [enabled](https://cbonte.github.io/haproxy-dconv/configuration-1.5.html#4-option%20redispatch) `option redispatch` in your `haproxy.cfg`, the request will be sent to any available backend server and the cookie will be ignored. It’s a matter of preference whether you want to trade user session persistence for smoother transitions in the face of failed backends.

#### Metrics to alert on:

<div class="anchor" id="Queue" />

**qcur**: If your backend is bombarded with connections to the point you have reached your global `maxconn` limit, HAProxy will [seamlessly queue new connections](https://stackoverflow.com/questions/8750518/difference-between-global-maxconn-and-server-maxconn-haproxy) in your system kernel’s socket queue until a backend server becomes available. The `qcur` metric tracks the current number of connections awaiting assignment to a backend server. If you have enabled cookies and the listed server is unavailable, connections will be queued until the queue timeout is reached. However, if you have set the `option redispatch` directive in your global HAProxy configuration, HAProxy can break the session’s persistence and forward the request to any available backend. 

Keeping connections out of the queue is ideal, resulting in less latency and a better user experience. You should alert if the size of your queue exceeds a threshold you are comfortable with. If you find that connections are consistently enqueueing, configuration changes may be in order, such as [increasing](https://cbonte.github.io/haproxy-dconv/configuration-1.5.html#3.2-maxconn) your global `maxconn` limit or changing the connection limits on your individual backend servers. ![Backend queue](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-10-haproxy/queue.png)

<center>_An empty queue is a happy queue_</center>

**qtime**: In addition to the queue size, HAProxy exposes the average time spent in queue via the `qtime` metric. This metric represents an average of the last 1,024 requests, so an abnormally large queue time for one connection could skew results. It goes without saying that minimizing time spent in the queue results in lower latency and an overall better client experience. Each use case can tolerate a certain amount of queue time but in general, you should aim to keep this value as low as possible. 

[![Backend response time](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-10-haproxy/response-time.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-10-haproxy/response-time.png) 

<div class="anchor" id="Latency" />

**rtime**: Tracking average response times is an effective way to measure the latency of your load-balancing setup. Generally speaking, response times in excess of 500 ms will lead to degradation of application performance and customer experience. Monitoring the average response time can give you the upper hand to respond to latency issues before your customers are substantially impacted. _Keep in mind_ that this metric will be [zero if you are not using HTTP](https://cbonte.github.io/haproxy-dconv/configuration-1.5.html#9.1) (see #60). 

**eresp**: The backend error response rate represents the number of response errors generated by your backends. This includes errors caused by data transfers aborted by the servers as well as write errors on the client socket and failures due to ACLs. Combined with other error metrics, the backend error response rate helps diagnose the root cause of response errors. For example, an increase in both the backend error response rate and denied responses could indicate that clients are repeatedly attempting to access ACL-ed resources.

<div class="anchor" id="Health" />

### Health metrics

HAProxy can also expose information about the health of each front and backend server, in addition to the metrics listed above. Health checks are not enabled by default, and require you to set the [`check` directive](https://cbonte.github.io/haproxy-dconv/configuration-1.5.html#5.2-check) in your HAProxy configuration. Once set up, HAProxy will regularly perform health checks on all enabled servers. If a health check fails three times in a row (configurable with the `rise` directive), it is marked in a **DOWN** state. 

Monitoring the health of your HAProxy servers gives you the information you need to quickly respond to outages as they occur. 

Health checks are highly configurable, with specific checks available for MySQL, SMTP, Redis and others. [Refer to the documentation](https://cbonte.github.io/haproxy-dconv/configuration-1.5.html#option%20httpchk) to take full advantage of HAProxy’s powerful health-checking features.

### Conclusion

In this post we’ve covered some of the most important metrics you can monitor to keep tabs on your HAProxy setup. If you are just getting started with HAProxy, monitoring the metrics mentioned below will provide good visibility into the health and performance of your load balancing infrastructure:

*   [Session utilization](#Utilization)
*   [Latency](#Latency)
*   [Denials](#Denials)
*   [Queue length and queue time](#Queue)

Eventually you will recognize additional metrics that are particularly relevant to your own infrastructure and use cases. In the [next post](http://www.datadoghq.com/blog/how-to-collect-haproxy-metrics) of this series, we provide step-by-step instructions on collecting HAProxy performance metrics.