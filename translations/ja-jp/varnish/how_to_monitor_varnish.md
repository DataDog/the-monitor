# How to monitor Varnish

*This post is part 1 of a 3-part series on Varnish monitoring. [Part 2](https://www.datadoghq.com/blog/how-to-collect-varnish-metrics/) is about collecting Varnish metrics, and [Part 3](https://www.datadoghq.com/blog/monitor-varnish-using-datadog/) is for readers who use both Datadog and Varnish.*

*このポストは、"Varnishの監視"3回シリーズのPart 1です。 Part 2は、[「Varnishのメトリクスの収集」](https://www.datadoghq.com/blog/how-to-collect-varnish-metrics/)で、Part 3は、[「Datadogを使ったVarnishの監視」](https://www.datadoghq.com/blog/monitor-varnish-using-datadog/)になります。*

## What is Varnish?

> Varnish Cache is a web application accelerator designed specifically for content-rich, dynamic websites and heavily-used APIs. The strategy it uses for acceleration is known as a “caching HTTP reverse proxying”. Let’s unpack these terms.

Varnishキャッシュは、コンテンツが豊富で、APIの使用頻度の高い、動的なWebサイトのために特別に設計されたWebアプリケーションアクセラレータです。Varnishがコンテンツを高速配信のために使用する戦略は、“caching HTTP reverse proxying”として広く知られています。では、この戦略の意味を詳しく見ていきましょう。

> As a reverse proxy, Varnish is server-side, as opposed as a client-side forward proxy. It acts as an invisible conduit between a client and a backend, intermediating all communications between the two. As a cache, it stores often-used assets (such as files, images, css) for faster retrieval and response without hitting the backend. Unlike other caching reverse proxies, which may support FTP, SMTP, or other network protocols, Varnish is exclusively focused on HTTP. As a caching HTTP proxy, Varnish also differs from browser-based HTTP proxies in that it can cache reusable assets between different clients, and cached objects can be invalidated everywhere simultaneously.

Varnishは、クライアント側に存在するフォワードプロキシとは対照的に、リバースプロキシとしてサーバー側に存在します。Varnishは、クライアントとバックエンドの間のすべての通信の間に入り、目に見えない仲介者として機能します。Varnishは、キャッシュのように頻繁に使用されるコンテンツ(files、images、cssなど)を保持し、高速な検索やバックエンドにアクセスせずにリクエストに応答をできるようなっています。Varnishは、他のFTP、SMTP、その他のプロトコルに対応しているキャッシュ用リバースプロキーとは異なり、HTTPプロトコルのみにフォーカスしています。キャッシュ用HTTPプロキシーとしても、Varnishは、ブラウザベースのHTTPプロキシと異なります。Varnishは、異なるクライアント間においても再利用できるコンテンツをキャッシュしておくことができ、またキャッシュされたオブジェクトは、どこにでも同時に無効にすることができます。

[![Varnish client backend](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-01.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-01.png)

> Varnish is a mature technology, and is in use at many high-traffic websites such as The New York Times, Wikipedia, Tumblr, Twitter, Vimeo, and Facebook.

Varnishは、成熟した技術であり、New York Times、Wikipedia、Tumblr、Twitter、Vimeo、Facebookのような高いトラフィック量をこなしているWebサイトで多く使われています。

## Key Varnish metrics

> When running well, Varnish Cache can speed up information delivery by a factor of several hundred. However, if Varnish is not tuned and working properly, it can slow down or even halt responses from your website. The best way to ensure the proper operation and performance of Varnish is by monitoring its key performance metrics in the following areas:

> -   **Client metrics:** client connections and requests
> -   **Cache performance:** cache hits, evictions
> -   **Thread metrics**: thread creation, failures, queues
> -   **Backend metrics:** success, failure, and health of backend connections

適切に設定できた場合、Varnishキャッシュは、コンテンツ配信を数百倍に高速化することができます。しかし、Varnishがチューニングされ、適切に動作していないと、コンテンツ配信は遅くなり、Webサイトからのレスポンスを中断してしまうこともあります。varnishの正常な動作とパフォーマスン確保するためには、次のような主要パフォーマスンメトリクスを監視しておくとが重要になります。

- **Client metrics:** クライアントのコネクションとリクエスト
- **Cache performance:** キャッシュヒット、退避
- **Thread metrics**: スレッドの作成、失敗、キュー待ち
- **Backend metrics:** 成功、失敗とバックエンドコネクションの健全性

[![Key Varnish metrics dashboard](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-02.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-02.png)

> This article references metric terminology [introduced in our Monitoring 101 series](https://www.datadoghq.com/blog/monitoring-101-collecting-data/), which provides a framework for metric collection and alerting.

このポストでは、メトリクスの収集方法やアラートの設定方法に関する基礎的な知識のポストである[introduced in our Monitoring 101 series][10]で紹介したメトリック用語を使っています。

> **NOTE:** All the metrics discussed here can be [collected from the varnishstat command line](https://www.datadoghq.com/blog/how-to-collect-varnish-metrics/), and use the metric names from the latest version, Varnish 4.0.

**注意:** ここで解説するすべてのメトリクスは、[varnishstatコマンドで収集する](https://www.datadoghq.com/blog/how-to-collect-varnish-metrics/)ことができます。また、各メトリクスの名前は、最新バージョンのVarnish4.0のものを採用しています。

### Client metrics

[![Varnish client metrics](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-03.png)
](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-03.png)

> Client metrics measure volume and success of client connections and requests. Below we discuss some of the most important.

クライアントメトリックは、クライアントとの間のコネクションとリクエストの全体数と成功数を測定しています。以下に、最も重要な幾つかのメトリクスを紹介していきます。

| **Name**          | **Description**                                                                                                     | [**Metric type**](https://www.datadoghq.com/blog/monitoring-101-collecting-data/) |
|-------------------|---------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| **sess\_conn**    | Cumulative number of accepted client connections by Varnish Cache                                                   | Resource: Utilization                                                             |
| **client\_req**   | Cumulative number of received client requests. Increments after a request is received, but before Varnish responds. | Work: Throughput                                                                  |
| **sess\_dropped** | Number of connections dropped due to a full queue                                                                   | Work: Error (due to resource saturation)                                          |

> Once a connection is established, the client can use that connection to make several requests to access resources such as images, files, CSS, or Javascript. Varnish can service the requests itself if the requested assets are already cached, or can fetch the resources from the backend.

コネクションが確立されると、クライアントは、画像、ファイル、CSS、JavaScriptなどのリソースにアクセスするためにコネクションを使って、複数のリクエストを送信します。Varnishは、リクエストを受けたコンテンツを既にキャッシュに持っている、そのリクエストに自分自身で応答します。持っていない場合は、バックエンドから所得し、応答します。

**Metrics to alert on:**

> - **`client_req`**: Regularly sampling the number of requests per second  allows you to calculate the number of requests you’re receiving per unit of time—typically minutes or seconds. Monitoring this metric can alert you to spikes in incoming web traffic, whether legitimate or nefarious, or sudden drops, which are usually indicative of problems. A drastic change in requests per second can alert you to problems brewing somewhere in your environment, even if it cannot immediately identify the cause of those problems. Note that all requests are counted the same, regardless of their URLs.

- **`client_req`**: 1秒毎のリクエスト数を欠かすことなく計測することにより、一定時間(例:分、秒)に受信しているリクエストの計算を可能にします。このメトリクスを監視することで、システムに入ってくるwebトラフィックの急増(合法、非合法を含め)や、障害の予兆であるトラフィックの急激な低下を検知しアラートを発生させることができます。秒単位のリクエスト数の急激な変化は、それ自体では、問題の原因をすぐに特定できない場合でも、あなたの環境下で発生しつつある問題を警告してくれています。ここで注意すべきは、リクエストされているURLの内容に関わらず、全てのリクエストは、同等にカウントされているということです。

<!-- -->

> - **`sess_dropped`**: Once Varnish is out of worker threads, it will queue up requests. [`sess_queued`](#thread-metrics) counts how many times this has happened. Once the queue is full, Varnish starts dropping connections without answering requests, and increments `sess_dropped`. If this metric is not equal to zero, then either Varnish is overloaded, or the thread pool is too small in which case you should try gradually increasing [`thread_pool_max`](https://www.varnish-software.com/static/book/Tuning.html#threading-parameters) and see if it fixes the issue without causing higher latency or other problems.

- **`sess_dropped`**: Varnishのワーカースレッドの残りが無くなると、リクエストをキューに入れ始めます。[`sess_queued`](#thread-metrics)は、このリクエストのキューへの追加の発生回数をカウントしています。キューが一杯になると、Varnishは、リクエストに応答するのをやめ、コネクションを切断し始め、`sess_dropped`の値を増やしていきます。この`sess_dropped`がゼロでない場合は、Varnishに過負荷になっているか、スレッドプールの設定値が小さすぎます。このようなケースは、[`thread_pool_max`](https://www.varnish-software.com/static/book/Tuning.html#threading-parameters)を徐々に増やしていき、更に長い遅延や他の問題を引き起すことなく、問題が修正されるかを確認してください。

> <span class="s1">Note that, for historical reasons, there is a `sess_drop` metric present in Varnish which is not the same as `sess_dropped`, discussed above. In new versions of Varnish, `sess_drop` is never incremented so it does not need to be monitored.</span>

<span class="s1">
Varnishには、歴史的な理由で`sess_drop`というメトリクスが存在します。このメトリクスは、上記で紹介した`sess_dropped`とは異なります。また、新しいバージョンのVarnishでは、`sess_drop`は、増加ることはありません。従って、監視する必要はありません。
</span>

[![Varnish client requests](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-04.jpg)
](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-04.jpg)

### Cache performance

> Varnish is a cache, so by measuring cache performance you can see instantly how well Varnish is doing its work.

Varnishはキャッシュです。従って、キャッシュのパフォーマンスを計測することでVarnishが適切に機能しているかを把握することができます。

#### Hit rate

> The diagram below illustrates how Varnish routes requests, and when each of its cache hit metrics is incremented.

以下の図は、Varnishがどのようにしてリクエストの経路を定めるかを示しています。又その際に、どのキャッシュヒットメトリクスの値を増やすかを示しています。

 [![Varnish routes requests](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-05.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-05.png)


| **Name**           | **Description**                                                                                                        | [**Metric type**](https://www.datadoghq.com/blog/monitoring-101-collecting-data/) |
|--------------------|------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| **cache\_hit**     | Cumulative number of times a file was served from Varnish’s cache.                                                     | Other                                                                             |
| **cache\_miss**    | Cumulative number of times a file was requested but was not in the cache, and was therefore requested from the backend | Other                                                                             |
| **cache\_hitpass** | Cumulative number of hits for a “pass” file                                                                            | Other                                                                             |

> When Varnish gets a response from the backend that indicates that a response may not be cached, it records that fact. Subsequent requests for the same object go directly to “pass”, increment `cache_hitpass`, and are not counted as cache misses.

Varnishは、レスポンスがキャッシュされない可能性があることを示す応答をバックエンドから受けた場合、その旨を学習しておきます。その後、同じオブジェクトに対するのリクエストは、直ちに`pass`に移行し、`cache_hitpass`の値にカウントされ、`cashe_miss`にはカウントされないようになっています。

**Metric to alert on:**

> The **cache hit rate** is the ratio of cache hits to total cache lookups: `cache_hit / (cache_hit + cache_miss)`. This derived metric provides visibility into the effectiveness of the cache. The higher the ratio, the better. If the hit rate is consistently high, above 0.7 (70 percent) for instance, then the majority of requests are successfully expedited through caching. If the cache is not answering a sufficient percentage of the read requests, consider increasing its memory, which can be a low-overhead tactic for improving read latency.

**キャッシュヒット率** は、キャッシュ内にコンテンツが見つかった数とキャッシュの検索総数の比率です: `cache_hit / (cache_hit + cache_miss)`。この計算によって求められたメトリクスは、キャッシュの有効性に関し、多くお情報を与えてくれます。この比率は、高ければ、高いほど良いです。例えば0.7(70%)のように高いヒット率に安定している場合は、大部分のリクエストが意図したとおりキャッシュを介して迅速に処理されていることになります。もしも、読み込みリクエストの十分な割合に対し、キャッシュが使われていないようなら、キャッシュに割り当てるメモリーの量を増やすことを検討してください。メモリーの追加割り当ては、少ない負担で読み込み遅延を改善する方法です。

> If after increasing the amount of memory available to your cache, your hit rate is still too low, you might also want to look at which objects are not being cached and why. For this you’ll need to use [Varnishlog](https://www.varnish-cache.org/docs/3.0/reference/varnishlog.html) and then optimize your VCL (Varnish Configuration Language) [tuning to improve the hit/miss ratio](https://www.varnish-cache.org/docs/4.0/users-guide/increasing-your-hitrate.html).

キャッシュが使用することができるメモリの量を増やした後でも、キャッシュヒット率が依然低すぎる場合は、キャッシュされていないオブジェクトを見つけ出し、キャッシュされていない理由を検討します。[Varnishlog](https://www.varnish-cache.org/docs/3.0/reference/varnishlog.html)の中身を検討した後、VCL (Varnish Configuration Language)の内容を最適化し、[hit/miss率が改善するようにチューニング](https://www.varnish-cache.org/docs/4.0/users-guide/increasing-your-hitrate.html)します。

[![Varnish cache hit rate](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-06.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-06.png)

#### Cached objects

| **Name**          | **Description**                                                                                                                           | [**Metric type**](https://www.datadoghq.com/blog/monitoring-101-collecting-data/) |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| **n\_expired**    | Cumulative number of expired objects for example due to [TTL](https://en.wikipedia.org/wiki/Time_to_live)                                 | Other                                                                             |
| **n\_lru\_nuked** | Least Recently Used Nuked Objects: Cumulative number of cached objects that Varnish has evicted from the cache because of a lack of space | Resource: Saturation                                                              |

**Metric to alert on:**

> The LRU (Least Recently Used) Nuked Objects counter, `n_lru_nuked`, should be closely watched. If the eviction rate is increasing, that means your cache is evicting objects faster and faster due to a lack of space. In this case you may want to consider increasing the cache size.

LRU (Least Recently Used) Nuked Objects(`n_lru_nuked`)のカウンター値には、注目しておくべきです。オブジェクトの退避率が増加してきている場合、キャッシュを保持しておくスペースが不足しているために、オブジェクトを次々と退避させていることになります。このような場合は、キャッシュサイズを増やすことを検討することをお勧めします。

### Thread-related metrics

[![Varnish thread metrics](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-07.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-07.png)

> Metrics related to worker threads tell you if your thread pools are healthy and functioning well.

ワーカースレッドに関するメトリクスは、スレッドプールが順調に機能しているかを教えてくれます。

| **Name**               | **Description**                                                                                                  | **[Metric type](https://www.datadoghq.com/blog/monitoring-101-collecting-data/)** |
|------------------------|------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| **threads**            | Number of threads currently being used                                                                           | Resource: Utilization                                                             |
| **threads\_created**   | Number of times a thread has been created                                                                        | Resource: Utilization                                                             |
| **threads\_failed**    | Number of times that Varnish unsuccessfully tried to create a thread                                             | Resource: Error                                                                   |
| **threads\_limited**   | Number of times Varnish wanted to create a thread but varnishd maxed out its configured capacity for new threads | Resource: Error                                                                   |
| **thread\_queue\_len** | Current queue length: number of requests waiting on worker thread to become available                            | Resource: Saturation                                                              |
| **sess\_queued**       | Number of times Varnish has been out of threads and had to queue up a request                                    | Resource: Saturation                                                              |

> Keep an eye on the metric `thread_queue_len` which should not be too high. If it’s not equal to zero, that means Varnish is saturated and responses are slowed.

`thread_queue_len`の値が高くなりすぎないように注目しておきます。この値がゼロ以外の場合は、Varnishは、飽和状態に至ってい、レスポンスへの応答が遅くなっていることを意味します。

> **These metrics should always be equal to 0:**
> - **`threads_failed`**: otherwise you have likely exceeded your server limits, or attempted to create threads too rapidly. The latter case usually occurs right after Varnish is started, and can be corrected by increasing the `thread_pool_add_delay` value.
> - **`threads_limited`**: otherwise you should consider increasing the value of `thread_pool_max`.

**これらのメトリクスは常にゼロである必要があります:**

- **`threads_failed`**: ゼロでない場合は、サーバーの限界を超えているか、あまりにも急速にスレッドを作りすぎています。後者のケースは、Varnishの起動直後に発生し、`thread_pool_add_delay`を調整することで調整できます。
- **`threads_limited`**: ゼロでない場合は、`thread_pool_max`の値を増やすことを検討してください。

### Backend metrics

[![Varnish backend metrics](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-08.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-08.png)

> Keeping an eye on the state of your connections with backend web servers is also crucial to understand how well Varnish is able to do its work.

Varnishが適切に機能できる状態になっているかを把握するには、バックエンドにあるWebサーバとのコネクションの状態に注目しておくことも、重要なことです。

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

> If your backend has [keep-alive set](https://www.varnish-software.com/blog/understanding-timeouts-varnish-cache), Varnish will use a pool of connections. You can get some insight into the effectiveness of the connection pool by looking at `backend_recycle` and `backend_reuse`.

バックエンドに対するコネクションに[keep-alive set](https://www.varnish-software.com/blog/understanding-timeouts-varnish-cache)が設定されている場合、Varnishは、プール内のコネクションを再利用しようとします。コネクションのプールの有効性を把握するためには、`backend_recycle`と`backend_reuse`を監視します。

> By default when `backend_busy` is incremented, that means the client receives a 5xx error response. However by using VCL, you can configure Varnish to recover from a busy backend by using a different backend, or by serving an outdated or synthetic response.

デフォルトの設定では、`backend_busy`に処理結果の値が加算された時は、クライアントは、5xx系のエラーを示すレスポンスを受信しています。しかし、VCLを編集することにより、Varnishに、別のバックエンドを使ったり、古いデーターを使ったり、人工的なレスポンスを使ってリカバーするように設定することができます。

> Backend requests, `backend_req`, should be monitored to detect network or cache performance issues.

バックエンドへのリクエスト数である`backend_req`の値は、ネットワーク、又はキャッシュパのフォーマンス障害を検出するために監視する必要があります。

**Metrics to alert on:**

> - **`backend_fail`** (backend connection failures) should be 0 or very close to 0. Backend connection failures can have several root causes:
    - Initial (TCP) connection timeout: usually results from network issues, but could also be due to an overloaded or unresponsive backend
    - Time to first byte: when a request is sent to the backend and it does not start responding within a certain amount of time
    - Time in between bytes: when the backend started streaming a response but stopped sending data without closing the connection
> - **`backend_unhealthy`**: Varnish [periodically pings](https://www.varnish-cache.org/docs/trunk/users-guide/vcl-backends.html#health-checks) the backend to make sure it is still up and responsive. If it doesn’t receive a 200 response quickly enough, the backend is marked as unhealthy and every new request to it increments this counter until the backend recovers and sends a timely 200 response.

- **`backend_fail`** (backend connection failures)は、ゼロ又は、ゼロに限りなく近い値である必要があります。Backend connection failuresは、様々な原因が考えられます:
  - Initial (TCP) connection timeout: 通常は、ネットワークの障害に起因します。過剰な負荷やバックエンドの応答が無いことが原因である場合もあります。
  - Time to first byte: リクエストは、バックエンドに送信されているが、バックエンドが一定の時間内に応答を開始しないとき。
  - Time in between bytes: バックエンドが、応答のための送信を開始したが、コネクションを閉じずにデーターの送信を停止したとき。
- **`backend_unhealthy`**: Varnishは、バックエンドが動作し、応答可能な状態になっているかを確認するために、[定期的にping](https://www.varnish-cache.org/docs/trunk/users-guide/vcl-backends.html#health-checks)を送信します。Varnishは、バックエンドから一定時間内に200系のレスポンスを受信しなかった場合、そのバックエンドは、異常と判断します。そして、そのバックエンドが一定時間内に200系レスポンスで嘔吐できるように回復するまで、新しいリクエストがある度に`backend_unhealthy`の値を増やしていきます。

[![Varnish metrics backend connections](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-09.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/1-09.png)

### Other metrics to monitor

#### ESI Related

> If you are using [Edge Side Includes](http://en.wikipedia.org/wiki/Edge_Side_Includes), `esi_errors` and `esi_warnings` will give you insight into the validity of your ESI syntax. If these metrics are increasing, you should inspect what is being returned by your backend and fix the errors you find.

[Edge Side Includes](http://en.wikipedia.org/wiki/Edge_Side_Includes)を使っている場合は、`esi_errors`と`esi_warnings`の値は、ESI構文の妥当性について教えてくれるでしょう。もしもそれらのメトリクスが増加しているようなら、バックエンドから応答を受けている内容を検査し、その中のエラーを修正する必要があります。

## Conclusion

> In this post we’ve explored the most important metrics you should monitor to keep tabs on your Varnish cache. If you are just getting started with Varnish, monitoring the metrics listed below will give you great insight into your cache’s health and performance. Most importantly it will help you identify areas where tuning could provide significant benefits.

このポストでは、Varnishキャッシュの状況を把握しておくために監視しておくべき最も有用なメトリクスについて紹介してきました。Varnishを使い始めている場合、以下のリストにあるメトリクスを監視することで、Web層の健全性や稼働状態を把握する手助けをしてくれるはずです。更にありがたいことに、Varnishのチューニングが大きなメリットになる領域を探し出す手助けをしてくれるはずです。

- [Requests per second](#client-metrics)
- [Dropped client connections](#client-metrics)
- [Cache hit rate](#hit-rate)
- [LRU Nuked objects](#cached-objects)
- [Some worker thread related metrics](#thread-metrics)
- [Backend connection failures or unhealthy backend](#backend-metrics)

> Eventually you will recognize additional, more specialized metrics that are particularly relevant to your own environment and use cases.

最終的には、あなたのインフラやユースケースに特に関連性のある、より専門的なメトリクスも存在することに気がつくでしょう。

> Of course, what you monitor will depend on the tools you have and the metrics available.

もちろん、何を監視するかは、持っているツールと監視可能なメトリクスの種類に依存しています。

> [Part 2 of this post](https://www.datadoghq.com/blog/how-to-collect-varnish-metrics/) provides step-by-step instructions for collecting these metrics from Varnish.

このシリーズのPart2[「How to collect Varnish metrics」](https://www.datadoghq.com/blog/how-to-collect-varnish-metrics/)では、Varnishから、メトリクスを収集するために必要な手順を解説していくことにます。

## Acknowledgments

> Many thanks to the [Fastly](https://www.fastly.com/) and [Varnish Software](https://www.varnish-software.com/) teams for reviewing this article prior to publication and providing important feedback and clarifications.

このポストを公開するに当たり、記事を事前にレビューし、重要なフィードバックと細部にわたる解説を提供してくれた[Fastly](https://www.fastly.com/) と[Varnish Software](https://www.varnish-software.com/) チームに感謝します。


------------------------------------------------------------------------

*Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/varnish/how_to_monitor_varnish.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues).*

*このポストのMarkdownソースは、[GitHub](https://github.com/DataDog/the-monitor/blob/master/varnish/how_to_monitor_varnish.md).d)で閲覧することができます。質問、訂正、追加、などがありましたら、[GitHubのissueページ](https://github.com/DataDog/the-monitor/issues)を使って連絡を頂けると幸いです。*
