# How to monitor Varnish

*This post is part 1 of a 3-part series on Varnish monitoring. [Part 2](https://www.datadoghq.com/blog/how-to-collect-varnish-metrics/) is about collecting Varnish metrics, and [Part 3](https://www.datadoghq.com/blog/monitor-varnish-using-datadog/) is for readers who use both Datadog and Varnish.*

## What is Varnish?

Varnish Cache is a web application accelerator designed specifically for content-rich, dynamic websites and heavily-used APIs. The strategy it uses for acceleration is known as a “caching HTTP reverse proxying”. Let’s unpack these terms.

As a reverse proxy, Varnish is server-side, as opposed as a client-side forward proxy. It acts as an invisible conduit between a client and a backend, intermediating all communications between the two. As a cache, it stores often-used assets (such as files, images, css) for faster retrieval and response without hitting the backend. Unlike other caching reverse proxies, which may support FTP, SMTP, or other network protocols, Varnish is exclusively focused on HTTP. As a caching HTTP proxy, Varnish also differs from browser-based HTTP proxies in that it can cache reusable assets between different clients, and cached objects can be invalidated everywhere simultaneously.

[![Varnish client backend](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-01.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-01.png)

Varnish is a mature technology, and is in use at many high-traffic websites such as The New York Times, Wikipedia, Tumblr, Twitter, Vimeo, and Facebook.

## Key Varnish metrics

When running well, Varnish Cache can speed up information delivery by a factor of several hundred. However, if Varnish is not tuned and working properly, it can slow down or even halt responses from your website. The best way to ensure the proper operation and performance of Varnish is by monitoring its key performance metrics in the following areas:

-   **Client metrics:** client connections and requests
-   **Cache performance:** cache hits, evictions
-   **Thread metrics**: thread creation, failures, queues
-   **Backend metrics:** success, failure, and health of backend connections

[![Key Varnish metrics dashboard](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-02.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-02.png)

This article references metric terminology [introduced in our Monitoring 101 series](https://www.datadoghq.com/blog/monitoring-101-collecting-data/), which provides a framework for metric collection and alerting.

 

**NOTE:** All the metrics discussed here can be [collected from the varnishstat command line](https://www.datadoghq.com/blog/how-to-collect-varnish-metrics/), and use the metric names from the latest version, Varnish 4.0.

### Client metrics

[![Varnish client metrics](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-03.png)
](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-03.png)
 Client metrics measure volume and success of client connections and requests. Below we discuss some of the most important.



| **Name**          | **Description**                                                                                                     | [**Metric type**](https://www.datadoghq.com/blog/monitoring-101-collecting-data/) |
|-------------------|---------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| **sess\_conn**    | Cumulative number of accepted client connections by Varnish Cache                                                   | Resource: Utilization                                                             |
| **client\_req**   | Cumulative number of received client requests. Increments after a request is received, but before Varnish responds. | Work: Throughput                                                                  |
| **sess\_dropped** | Number of connections dropped due to a full queue                                                                   | Work: Error (due to resource saturation)                                          |

Once a connection is established, the client can use that connection to make several requests to access resources such as images, files, CSS, or Javascript. Varnish can service the requests itself if the requested assets are already cached, or can fetch the resources from the backend.

**Metrics to alert on:**

-   **`client_req`**: Regularly sampling the number of requests per second  allows you to calculate the number of requests you’re receiving per unit of time—typically minutes or seconds. Monitoring this metric can alert you to spikes in incoming web traffic, whether legitimate or nefarious, or sudden drops, which are usually indicative of problems. A drastic change in requests per second can alert you to problems brewing somewhere in your environment, even if it cannot immediately identify the cause of those problems. Note that all requests are counted the same, regardless of their URLs.

<!-- -->

-   **`sess_dropped`**: Once Varnish is out of worker threads, it will queue up requests. [`sess_queued`](#thread-metrics) counts how many times this has happened. Once the queue is full, Varnish starts dropping connections without answering requests, and increments `sess_dropped`. If this metric is not equal to zero, then either Varnish is overloaded, or the thread pool is too small in which case you should try gradually increasing [`thread_pool_max`](https://www.varnish-software.com/static/book/Tuning.html#threading-parameters) and see if it fixes the issue without causing higher latency or other problems.

<span class="s1">Note that, for historical reasons, there is a `sess_drop` metric present in Varnish which is not the same as `sess_dropped`, discussed above. In new versions of Varnish, `sess_drop` is never incremented so it does not need to be monitored.</span>

[![Varnish client requests](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-04.jpg)
](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-04.jpg)

### Cache performance

Varnish is a cache, so by measuring cache performance you can see instantly how well Varnish is doing its work.

#### Hit rate

The diagram below illustrates how Varnish routes requests, and when each of its cache hit metrics is incremented.
 [![Varnish routes requests](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-05.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-05.png)


| **Name**           | **Description**                                                                                                        | [**Metric type**](https://www.datadoghq.com/blog/monitoring-101-collecting-data/) |
|--------------------|------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| **cache\_hit**     | Cumulative number of times a file was served from Varnish’s cache.                                                     | Other                                                                             |
| **cache\_miss**    | Cumulative number of times a file was requested but was not in the cache, and was therefore requested from the backend | Other                                                                             |
| **cache\_hitpass** | Cumulative number of hits for a “pass” file                                                                            | Other                                                                             |

When Varnish gets a response from the backend that indicates that a response may not be cached, it records that fact. Subsequent requests for the same object go directly to “pass”, increment `cache_hitpass`, and are not counted as cache misses.

**Metric to alert on:**

The **cache hit rate** is the ratio of cache hits to total cache lookups: `cache_hit / (cache_hit + cache_miss)`. This derived metric provides visibility into the effectiveness of the cache. The higher the ratio, the better. If the hit rate is consistently high, above 0.7 (70 percent) for instance, then the majority of requests are successfully expedited through caching. If the cache is not answering a sufficient percentage of the read requests, consider increasing its memory, which can be a low-overhead tactic for improving read latency.

If after increasing the amount of memory available to your cache, your hit rate is still too low, you might also want to look at which objects are not being cached and why. For this you’ll need to use [Varnishlog](https://www.varnish-cache.org/docs/3.0/reference/varnishlog.html) and then optimize your VCL (Varnish Configuration Language) [tuning to improve the hit/miss ratio](https://www.varnish-cache.org/docs/4.0/users-guide/increasing-your-hitrate.html).

[![Varnish cache hit rate](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-06.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-06.png)

#### Cached objects

| **Name**          | **Description**                                                                                                                           | [**Metric type**](https://www.datadoghq.com/blog/monitoring-101-collecting-data/) |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| **n\_expired**    | Cumulative number of expired objects for example due to [TTL](https://en.wikipedia.org/wiki/Time_to_live)                                 | Other                                                                             |
| **n\_lru\_nuked** | Least Recently Used Nuked Objects: Cumulative number of cached objects that Varnish has evicted from the cache because of a lack of space | Resource: Saturation                                                              |

**Metric to alert on:**

The LRU (Least Recently Used) Nuked Objects counter, `n_lru_nuked`, should be closely watched. If the eviction rate is increasing, that means your cache is evicting objects faster and faster due to a lack of space. In this case you may want to consider increasing the cache size.

### Thread-related metrics

[![Varnish thread metrics](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-07.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-07.png)

Metrics related to worker threads tell you if your thread pools are healthy and functioning well.

| **Name**               | **Description**                                                                                                  | **[Metric type](https://www.datadoghq.com/blog/monitoring-101-collecting-data/)** |
|------------------------|------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| **threads**            | Number of threads currently being used                                                                           | Resource: Utilization                                                             |
| **threads\_created**   | Number of times a thread has been created                                                                        | Resource: Utilization                                                             |
| **threads\_failed**    | Number of times that Varnish unsuccessfully tried to create a thread                                             | Resource: Error                                                                   |
| **threads\_limited**   | Number of times Varnish wanted to create a thread but varnishd maxed out its configured capacity for new threads | Resource: Error                                                                   |
| **thread\_queue\_len** | Current queue length: number of requests waiting on worker thread to become available                            | Resource: Saturation                                                              |
| **sess\_queued**       | Number of times Varnish has been out of threads and had to queue up a request                                    | Resource: Saturation                                                              |

Keep an eye on the metric `thread_queue_len` which should not be too high. If it’s not equal to zero, that means Varnish is saturated and responses are slowed.

**These metrics should always be equal to 0:**

-   **`threads_failed`**: otherwise you have likely exceeded your server limits, or attempted to create threads too rapidly. The latter case usually occurs right after Varnish is started, and can be corrected by increasing the `thread_pool_add_delay` value.
-   **`threads_limited`**: otherwise you should consider increasing the value of `thread_pool_max`.

### Backend metrics

[![Varnish backend metrics](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-08.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-08.png)

Keeping an eye on the state of your connections with backend web servers is also crucial to understand how well Varnish is able to do its work.

| **Name**               | **Description**                                                                                                                     | [**Metric type**](https://www.datadoghq.com/blog/monitoring-101-collecting-data/) |
|------------------------|-------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| **backend\_conn**      | Cumulative number of successful TCP connections to the backend                                                                      | Resource: Utilization                                                             |
| **backend\_recycle**   | Cumulative number of current backend connections which were put back to a pool of keep-alive connections and have not yet been used | Resource: Utilization                                                             |
| **backend\_reuse**     | Cumulative number of connections that were reused from the keep-alive pool                                                          | Resource: Utilization                                                             |
| **backend\_toolate**   | Cumulative number of backend connections that have been closed because they were idle for too long                                  | Other                                                                             |
| **backend\_fail**      | Cumulative number of failed connections to the backend                                                                              | Work: Error (due to resource error)                                               |
| **backend\_unhealthy** | Cumulative number of backend connections which were not attempted because the backend has been marked as unhealthy                  | Resource: Error                                                                   |
| **backend\_busy**      | Cumulative number of times the maximum amount of connections to the backend has been reached                                        | Resource: Saturation                                                              |
| **backend\_req**       | Number of requests to the backend                                                                                                   | Resource: Utilization                                                             |

If your backend has [keep-alive set](https://www.varnish-software.com/blog/understanding-timeouts-varnish-cache), Varnish will use a pool of connections. You can get some insight into the effectiveness of the connection pool by looking at `backend_recycle` and `backend_reuse`.

By default when `backend_busy` is incremented, that means the client receives a 5xx error response. However by using VCL, you can configure Varnish to recover from a busy backend by using a different backend, or by serving an outdated or synthetic response.

Backend requests, `backend_req`, should be monitored to detect network or cache performance issues.

**Metrics to alert on:**

-   **`backend_fail`** (backend connection failures) should be 0 or very close to 0. Backend connection failures can have several root causes:
    -   Initial (TCP) connection timeout: usually results from network issues, but could also be due to an overloaded or unresponsive backend
    -   Time to first byte: when a request is sent to the backend and it does not start responding within a certain amount of time
    -   Time in between bytes: when the backend started streaming a response but stopped sending data without closing the connection

-   **`backend_unhealthy`**: Varnish [periodically pings](https://www.varnish-cache.org/docs/trunk/users-guide/vcl-backends.html#health-checks) the backend to make sure it is still up and responsive. If it doesn’t receive a 200 response quickly enough, the backend is marked as unhealthy and every new request to it increments this counter until the backend recovers and sends a timely 200 response.

[![Varnish metrics backend connections](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-09.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-09.png)

### Other metrics to monitor

#### ESI Related

If you are using [Edge Side Includes](http://en.wikipedia.org/wiki/Edge_Side_Includes), `esi_errors` and `esi_warnings` will give you insight into the validity of your ESI syntax. If these metrics are increasing, you should inspect what is being returned by your backend and fix the errors you find.

## Conclusion

In this post we’ve explored the most important metrics you should monitor to keep tabs on your Varnish cache. If you are just getting started with Varnish, monitoring the metrics listed below will give you great insight into your cache’s health and performance. Most importantly it will help you identify areas where tuning could provide significant benefits.

-   [Requests per second](#client-metrics)
-   [Dropped client connections](#client-metrics)
-   [Cache hit rate](#hit-rate)
-   [LRU Nuked objects](#cached-objects)
-   [Some worker thread related metrics](#thread-metrics)
-   [Backend connection failures or unhealthy backend](#backend-metrics)

Eventually you will recognize additional, more specialized metrics that are particularly relevant to your own environment and use cases.

Of course, what you monitor will depend on the tools you have and the metrics available.

[Part 2 of this post](https://www.datadoghq.com/blog/how-to-collect-varnish-metrics/) provides step-by-step instructions for collecting these metrics from Varnish.

## Acknowledgments

Many thanks to the [Fastly](https://www.fastly.com/) and [Varnish Software](https://www.varnish-software.com/) teams for reviewing this article prior to publication and providing important feedback and clarifications.

------------------------------------------------------------------------

*Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/varnish/how_to_monitor_varnish.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues).*