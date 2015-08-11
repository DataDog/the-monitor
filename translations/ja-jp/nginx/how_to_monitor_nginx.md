# How to monitor NGINX
> *This post is part 1 of a 3-part series on NGINX monitoring. [Part 2][1] is about collecting NGINX metrics, and [Part 3][2] details how to monitor NGINX with Datadog.*

*このポストは、"NGINXの監視"3回シリーズのPart1です。 Part 2は、[「NGINXのメトリクスの収集」][3]で、Part 3は、[「Datadogを使ったNGINXの監視」][4]になります。*

## What is NGINX?
> [NGINX][5] (pronounced "engine X") is a popular HTTP server and reverse proxy server. As an HTTP server, NGINX serves static content very efficiently and reliably, using relatively little memory. As a [reverse proxy][6], it can be used as a single, controlled point of access for multiple back-end servers or for additional applications such as caching and load balancing. NGINX is available as a free, open-source product or in a more full-featured, commercially distributed version called NGINX Plus.

> NGINX can also be used as a mail proxy and a generic TCP proxy, but this article does not directly address NGINX monitoring for these use cases.

[NGINX][7](発音は「エンジンエックス」)は、人気のHTTPサーバーとリバースプロキシサーバーです。NGINXは、HTTPサーバーとして活用した場合、比較的少ないメモリー消費量で、高効率かつ確実に静的なコンテンツを配信してくれます。[リバースプロキシサーバー][8]としては、
複数のバックエンドサーバーへの単一アクセスポイントして使用したり、キャッシュや負荷分散などの他の用途に使用することもあります。NIGNXには、無償で提供されているオープンソースの製品と"NIGNX Plus"と呼ばれる、より完全な機能を備えた商用製品があります。

NGINXは、メールプロキシーや汎用TCPプロキシーとして使用することもできます。これらのユースケースに向けたNGINXの監視は、この記事では取り扱い範囲外になります。

## Key NGINX metrics
> By monitoring NGINX you can catch two categories of issues: resource issues within NGINX itself, and also problems developing elsewhere in your web infrastructure. Some of the metrics most NGINX users will benefit from monitoring include **requests per second**, which provides a high-level view of combined end-user activity; **server error rate**, which indicates how often your servers are failing to process seemingly valid requests; and **request processing time**, which describes how long your servers are taking to process client requests (and which can point to slowdowns or other problems in your environment).

NGINXを監視することで、2つのカテゴリーの障害を検出することができます。第一のカテゴリーは、NGINX自体で起きている障害です。第二のカテゴリーは、Webインフラの他の場所で発生している障害です。監視をすることにより、大部分のNGINXユーザーが恩恵を受けられるトリクスは、以下のようなものです。
- **requests per second** : ユーザーの利用状況の概要を示している。
- **server error rate** : 適切なリクエストの処理に失敗する頻度を示している。
- **request processing time** : サーバーがユーザーリクエストを処理するのに必要な時間を示している。(リクエスト応答に時間が掛かるようになってきていることや、環境内で問題が発生している可能性があることがわかります。)

> More generally, there are at least three key categories of metrics to watch:
> - Basic activity metrics
> - Error metrics
> - Performance metrics

より一般的に表現すると、注目するべきメトリクスには、少なくとも3つの主要なカテゴリーがあります。
- 利用状況の基礎的なメトリクス
- エラーに関するメトリクス
- パフォーマンスに関するメトリクス

> Below we'll break down a few of the most important NGINX metrics in each category, as well as metrics for a fairly common use case that deserves special mention: using NGINX Plus for reverse proxying. We will also describe how you can monitor all of these metrics with your graphing or monitoring tools of choice.

以下では、「NGINX Plusのリーバースプロキシー」というかなり一般的なユースケースを題材とすると同時に、NGINXの特に重要なメトリクスの幾つかを、先に紹介した各カテゴリーに分類していきます。その上で、それらのメトリクスを、あなたが選択したグラフツールや監視ツールで、どのように監視できるかを説明してきます。

> This article references metric terminology [introduced in our Monitoring 101 series][9], which provides a framework for metric collection and alerting.

このポストでは、メトリクスの収集方法やアラートの設定方法に関する基礎的な知識のポストである[introduced in our Monitoring 101 series][10]で紹介したメトリック用語を使っています。

### Basic activity metrics
> Whatever your NGINX use case, you will no doubt want to monitor how many client requests your servers are receiving and how those requests are being processed.

> NGINX Plus can report basic activity metrics exactly like open-source NGINX, but it also provides a secondary module that reports metrics slightly differently. We discuss open-source NGINX first, then the additional reporting capabilities provided by NGINX Plus.

どのような利用目的でNGINXを使っていても、どれくらいのクライアントリクエストをサーバーが受信し、またそれらのリクエストがどのように処理されているかを監視したいものです。

NGINX Plusでも、オープンソース版のNGINXと全く同じように基本的なメトリクスをレポートすることができますが、更に追加モジュールを使い幾分か異なるメトリクスも収集することができます。このポストでは、まずオープンソース版のNGINXについて解説し、次にNGINX Plusの追加レポーティング機能について解説します。

#### NGINX
> The diagram below shows the lifecycle of a client connection and how the open-source version of NGINX collects metrics during a connection.

下の図は、クライアントからの接続のライフサイクルとオープンセース版のNGINXがどのようにしてメトリクスを収集しているかを示しています。

![connection, request states][image-1]

> Accepts, handled, and requests are ever-increasing counters. Active, waiting, reading, and writing grow and shrink with request volume.

Accepts、handled、requestsの数値は、積算された値として増え続けていきます。 Active、waiting、reading、writingは、リクエストの状況により増えたり減ったりします。

<table><colgroup> <col style="text-align: left;" /> <col style="text-align: left;" /> <col style="text-align: left;" /> </colgroup>
<thead>
<tr>
<th style="text-align: left;"><strong>Name</strong></th>
<th style="text-align: left;"><strong>Description</strong></th>
<th style="text-align: left;"><strong><a href="/blog/monitoring-101-collecting-data/" target="_blank">Metric type</a></strong></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;">accepts</td>
<td style="text-align: left;">Count of client connections attempted by NGINX</td>
<td style="text-align: left;">Resource: Utilization</td>
</tr>
<tr>
<td style="text-align: left;">handled</td>
<td style="text-align: left;">Count of successful client connections</td>
<td style="text-align: left;">Resource: Utilization</td>
</tr>
<tr>
<td style="text-align: left;">active</td>
<td style="text-align: left;">Currently active client connections</td>
<td style="text-align: left;">Resource: Utilization</td>
</tr>
<tr>
<td style="text-align: left;">dropped (calculated)</td>
<td style="text-align: left;">Count of dropped connections (accepts – handled)</td>
<td style="text-align: left;">Work: Errors*</td>
</tr>
<tr>
<td style="text-align: left;">requests</td>
<td style="text-align: left;">Count of client requests</td>
<td style="text-align: left;">Work: Throughput</td>
</tr>
<tr>
<td style="text-align: left;" colspan="3">*<em>Strictly speaking, dropped connections is <a href="/blog/monitoring-101-collecting-data/#resource-metrics" target="_blank">a metric of resource saturation</a>, but since saturation causes NGINX to stop servicing some work (rather than queuing it up for later), “dropped” is best thought of as <a href="/blog/monitoring-101-collecting-data/#work-metrics" target="_blank">a work metric</a>.</em></td>
</tr>
</tbody>
</table>

> The **accepts** counter is incremented when an NGINX worker picks up a request for a connection from the OS, whereas **handled** is incremented when the worker actually gets a connection for the request (by establishing a new connection or reusing an open one). These two counts are usually the same--any divergence indicates that connections are being **dropped**, often because a resource limit, such as NGINX's [worker\_connections][11] limit, has been reached.

**accepts** カンターは、NGINXワーカーがOSからのコネクションリクエストを受ける度に増加していきます。**handled**は、ワーカーがリクエストの新しいコネクションを生成するか既に存在しているコネクションをリースし、実際にコネクションを成立させた場合に増加していきます。**accepts**と**handled**の数値は、一般的には同じになります。もしも、これらの数値に差が出ているなら、それは**dropped**が発生していることを意味しています。この**dropped**は、例えば、NGINXの[worker\_connections][11]リミットの上限値に達している場合など、リソースの利用が限界に達している時に起こります。

> Once NGINX successfully handles a connection, the connection moves to an **active** state, where it remains as client requests are processed:

NGINXがコネクションを正常に処理すると、コネクションは、クライアントリクエストが処理されるように、**active**ステートに移行します。

##### Active state
> - **Waiting:** An active connection may also be in a Waiting substate if there is no active request at the moment. New connections can bypass this state and move directly to Reading, most commonly when using "accept filter" or "deferred accept", in which case NGINX does not receive notice of work until it has enough data to begin working on the response. Connections will also be in the Waiting state after sending a response if the connection is set to keep-alive.
> - **Reading:** When a request is received, the connection moves out of the waiting state, and the request itself is counted as Reading. In this state NGINX is reading a client request header. Request headers are lightweight, so this is usually a fast operation.
> - **Writing:** After the request is read, it is counted as Writing, and remains in that state until a response is returned to the client. That means that the request is Writing while NGINX is waiting for results from upstream systems (systems "behind" NGINX), and while NGINX is operating on the response. Requests will often spend the majority of their time in the Writing state.

- **Waiting:** 現時点で処理中のリクエストがない場合は、**Active**状態のコネクションは、Waitingというサブステートに成っていることがあります。新しいコネクションをは、**Waiting**状態をバイパスし直接**Reading**状態になります。この直接移行の最も一般的なケースは、"accept filter"や"deferred accept"を使用している時です。このような場合、十分なデータが揃ってレスポンスの処理を始めるまで、処理をしていることの通知をNGINXは受け取っていません。コネクションは、keep-aliveの設定がされている場合も、レスポンスを返信した後に**Waiting**状態になります。 
- **Reading:** リクエストを受信した時、コネクションは**Waiting**状態から抜け出します。そして、そのリクエストは、**Reading**にカウントされます。この状態では、NGINXは、クライアントからのリクエストヘッダーを解析しています。リクエストヘッダーは、非常の情報量はそれほど多くないので、一般的にこの処理にかかる時間は非常に短いです。
- **Writing:** リクエストが**Reading**状態か抜け出すと、**Writing**としてカウントされます。そして、クライアントにレスポンスが返信されるまで、このステートに止まります。つまり、NGINXがバックエンドシステムからの結果を待っている間と実際にレスポンスを返信している間は、**Writing**状態になっています。リクエストは、その大半の時間を**Writing**状態で過ごすことになります。

> Often a connection will only support one request at a time. In this case, the number of Active connections == Waiting connections + Reading requests + Writing requests. However, the newer SPDY and HTTP/2 protocols allow multiple concurrent requests/responses to be multiplexed over a connection, so Active may be less than the sum of Waiting, Reading, and Writing. (As of this writing, NGINX does not support HTTP/2, but expects to add support during 2015.)

多くの場合、コネクションは、一度に1つのリクエストしかサポートしません。このような場合、Activeコネクションは、 WatingコネクションとReadingコネクションとWritingコネクションの合計になります。しかし、新しいSPDYやHTTP/2のプロトコルでは、複数の同時に発生するリクエスト/レスポンスを多重的に一つのコネクション上で通信することを可能にしています。従って、Activeの値は、WaitingとReadingとWritingの合計値より少なくなります。(このポストを執筆している時点は、NGINXは、HTTP/2はサポートしていませんが、2015年内にはサポート予定になっています。)

#### NGINX Plus
> As mentioned above, all of open-source NGINX's metrics are available within NGINX Plus, but Plus can also report additional metrics. The section covers the metrics that are only available from NGINX Plus.

既に記したように、オープンソース版のNGINXで収集可能なメトリクスは、NGINX Plusでも収集できます。更にPlusには、追加のメトリクスも準備されています。このセクションは、NGINX Plusでのみ有効なメトリクスについて解説していきます。

![connection, request states][image-2]

> Accepted, dropped, and total are ever-increasing counters. Active, idle, and current track the current number of connections or requests in each of those states, so they grow and shrink with request volume.

図の中の、Accepted、Dropped、Totalの数値は、積算値として増え続けます。Active、Idle、Currentは、現在のコネクション数やそのステートのリクエスト数を示し、増えたり減ったりします。

<table><colgroup> <col style="text-align: left;" /> <col style="text-align: left;" /> <col style="text-align: left;" /> </colgroup>
<thead>
<tr>
<th style="text-align: left;"><strong>Name</strong></th>
<th style="text-align: left;"><strong>Description</strong></th>
<th style="text-align: left;"><strong><a href="/blog/monitoring-101-collecting-data/" target="_blank">Metric type</a></strong></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;">accepted</td>
<td style="text-align: left;">Count of client connections attempted by NGINX</td>
<td style="text-align: left;">Resource: Utilization</td>
</tr>
<tr>
<td style="text-align: left;">dropped</td>
<td style="text-align: left;">Count of dropped connections</td>
<td style="text-align: left;">Work: Errors*</td>
</tr>
<tr>
<td style="text-align: left;">active</td>
<td style="text-align: left;">Currently active client connections</td>
<td style="text-align: left;">Resource: Utilization</td>
</tr>
<tr>
<td style="text-align: left;">idle</td>
<td style="text-align: left;">Client connections with zero current requests</td>
<td style="text-align: left;">Resource: Utilization</td>
</tr>
<tr>
<td style="text-align: left;">total</td>
<td style="text-align: left;">Count of client requests</td>
<td style="text-align: left;">Work: Throughput</td>
</tr>
<tr>
<td style="text-align: left;" colspan="3">*<em>Strictly speaking, dropped connections is a metric of resource saturation, but since saturation causes NGINX to stop servicing some work (rather than queuing it up for later), “dropped” is best thought of as a work metric.</em></td>
</tr>
</tbody>
</table>

> The **accepted** counter is incremented when an NGINX Plus worker picks up a request for a connection from the OS. If the worker fails to get a connection for the request (by establishing a new connection or reusing an open one), then the connection is dropped and **dropped** is incremented. Ordinarily connections are dropped because a resource limit, such as NGINX Plus's [worker\_connections][12] limit, has been reached.

**accepted**カウンターは、NGINX PlusワーカーがOSからのコネクションリクエストを受ける度に増加していきます。もしも、NGINX Plusワーカーが、リクエストのあったコネクションを、新しく生成するか既存のものを再利用するかし、確保することに失敗すると、ワーカーはコネクションの確保を断念し、**dropped**の値を増加させます。通常、NGINX Plusワーカーは、[worker\_connections][12]制限などのリソースの制限に達した場合に、コネクションを断念します。

> **Active** and **idle** are the same as "active" and "waiting" states in open-source NGINX as described [above][13], with one key exception: in open-source NGINX, "waiting" falls under the "active" umbrella, whereas in NGINX Plus "idle" connections are excluded from the "active" count. **Current** is the same as the combined "reading + writing" states in open-source NGINX.

**Active**と**Idle**は、[オープンソース版のNIGINXで解説した][13]"active"と"waiting"のステートと重要な一つの例外を除いて同じです。オープンソース版のNGINXの場合、"waiting" は、"Active"の配下にありました。NGINX Plusの場合、"idle"は、"Active"の積算から除外されています。そして、**Current**は、"reading"ステータスと"writing"ステータスを合算した値となります。

> **Total** is a cumulative count of client requests. Note that a single client connection can involve multiple requests, so this number may be significantly larger than the cumulative number of connections. In fact, (total / accepted) yields the average number of requests per connection.

**Total** は、クライアントリクエストの累積値です。注意するべきことは、単一のクライアントコネクションが、複数のリクエストを関連しているということです。従って、この数値は、コネクションの累積値よりも著しく大きいということです。実際には、totalをacceptedで除算した値は、コネクションあたりのリクエストの平均値になります。

#### Metric differences between Open-Source and Plus

NGINX (open-source)                | NGINX Plus
|---------------------------------- | -------------------------------
accepts                            | accepted
dropped must be calculated         | dropped is reported directly
reading + writing                  | current
waiting                            | idle
active (includes “waiting” states) | active (excludes “idle” states)
requests                           | total

#### **Metric to alert on: Dropped connections**
> The number of connections that have been dropped is equal to the difference between accepts and handled (NGINX) or is exposed directly as a standard metric (NGINX Plus). Under normal circumstances, dropped connections should be zero. If your rate of dropped connections per unit time starts to rise, look for possible resource saturation.

コネクションとして処理ぜずに落としている数は、オプーンソース版NIGINXでは、**accept**から**handled**を引き算した数値で、NGINX Plusでは**dropped**という基本メトリクスで直接提供されています。通常の状況下では、これらの"dropped connection"の数値はゼロのはずです。単位時間あたりの"dropped connection"のレートが増加している場合は、リソースの飽和を疑う必要があります。

[![Dropped connections][image-3]][14]

#### **Metric to alert on: Requests per second**
> Sampling your request data (**requests** in open-source, or **total** in Plus) with a fixed time interval provides you with the number of requests you're receiving per unit of time--often minutes or seconds. Monitoring this metric can alert you to spikes in incoming web traffic, whether legitimate or nefarious, or sudden drops, which are usually indicative of problems. A drastic change in requests per second can alert you to problems brewing somewhere in your environment, even if it cannot tell you exactly where those problems lie. Note that all requests are counted the same, regardless of their URLs.

秒や分という一定時間でのリクエスト(オープンソース版では、**requests**。NGINX Plusでは、**total**。)の値の収集は、システムが単位時間当たりに受信しているリクエスト数を提供してくれます。このメトリクスを監視することで、Webトラフィックの急上昇を検知しアラートを受けることができます。(合理的なトラフィックの増加か、悪意によるものかにかかわらず。)　また、単位時間当たりリクエストの突然の減少は、障害派生の暗示でもあるでしょう。秒間リクエストの急激な変化は、たとえそれ自身で問題箇所を明確に特定できないとしても、あなたの環境のどこかで問題が発生し始めていることを警告してくれるでしょう。(ここで、注意が必要なのは、URLの内容にかかわらず、全てのリクエストが同等にカウントされていることです。)

[![Requests per second][image-4]][15]

#### Collecting activity metrics
> Open-source NGINX exposes these basic server metrics on a simple status page. Because the status information is displayed in a standardized form, virtually any graphing or monitoring tool can be configured to parse the relevant data for analysis, visualization, or alerting. NGINX Plus provides a JSON feed with much richer data. Read the companion post on [NGINX metrics collection][16] for instructions on enabling metrics collection.

オープンソース版のNGINXは、基本的メトリクスをシンプルなステータスページに公開しています。ステータスページは、標準化されたフォームに基づいて公開されているので、実質的に全ての監視ツールやグラフ化ツールは、状況の解析や可視化やアラートのためのにこのページをパースすることができるようになっています。NGINX Plusでは、より豊富なデータを含んだJSON形式のfeedを提供しています。メトリクスの収集を有効にする方法に関しては、このシリーズに含まれている[「NGINX metrics collection」][16]を参考にしてください。

### Error metrics

**Name**  | **Description**        | **[Metric type][17]** | **Availability**
|--------- | ---------------------- | -------------------------------------------------------- | ----------------------
4xx codes | Count of client errors | Work: Errors                                             | NGINX logs, NGINX Plus
5xx codes | Count of server errors | Work: Errors                                             | NGINX logs, NGINX Plus

> NGINX error metrics tell you how often your servers are returning errors instead of producing useful work. Client errors are represented by 4xx status codes, server errors with 5xx status codes.

NGINXのエラーに関するメトリクスは、サーバーが、有用な仕事の結果を送信せずに、エラーコードをどれ位の頻度で送信しているかを教えてくれます。クライアントサイドのエラーは4xx系のステータスコードで、サーバーサイドのエラーは5xx系のステータスコードで表されます。

#### **Metric to alert on: Server error rate**
> Your server error rate is equal to the number of 5xx errors divided by the total number of [status codes][18] (1xx, 2xx, 3xx, 4xx, 5xx), per unit of time (often one to five minutes). If your error rate starts to climb over time, investigation may be in order. If it spikes suddenly, urgent action may be required, as clients are likely to report errors to the end user.

あなたのサーバーのエラー率は、単位時間(多くの場合、1分~5分)当たりの5xx系のエラーの数を[status codes][18](1xx, 2xx, 3xx, 4xx, 5xx)の合計で割った数値になります。もしも、このエラー率が時間とともに上昇しているようなら、調査が必要かもしれません。もしも突然上昇するようなら、エンドユーザーのwebクライアントは、エラーを表示しているので、緊急対応が必要です。

[![Server error rate][image-5]][19]

> A note on client errors: while it is tempting to monitor 4xx, there is limited information you can derive from that metric since it measures client behavior without offering any insight into particular URLs. In other words, a change in 4xx could be noise, e.g. web scanners blindly looking for vulnerabilities.


クライアントエラーに関する注意: クライアントエラーを把握するために4xx系を監視したくなりますが、このメトリクスからは、限られた情報しか収集することができません。なぜならば、特定のURLに対してどんなリクエストをしているのかの洞察を把握せずに、クライアントの動作具合を測定する状態だからです。つまり、4xx系で起きた変化は、ノイズである可能性もあるということです。例えば、webスキャナーによる総当たり的な脆弱性検査を実施しているケースです。

#### Collecting error metrics
> Although open-source NGINX does not make error rates immediately available for monitoring, there are at least two ways to capture that information:
> 
> 1. Use the expanded status module available with commercially supported NGINX Plus
> 2. Configure NGINX's log module to write response codes in access logs

オープンソース版NGINXは、監視に直ちに使えるようなエラー率を公開していません。以下に紹介した方法でその方法をキャプチャすることができます。

1. エラー率を収集するための拡張状態モジュールを持っている、商用版のNGINX Plusを利用する。
2. NGINXのログモジュールを設定し、アクセスログにレスポンスコードも書き出すようにする。

> Read the companion post on NGINX metrics collection for detailed instructions on both approaches.

両方のアプローチの詳しい手順については、このシリーズに含まれる[「NGINX metrics collection」][21]の記事を参照してください。

### Performance metrics

**Name**     | **Description**                          | **[Metric type][20]** | **Availability**
|------------ | ---------------------------------------- | -------------------------------------------------------- | ----------------
request time | Time to process each request, in seconds | Work: Performance                                        | NGINX logs

#### **Metric to alert on: Request processing time**
> The request time metric logged by NGINX records the processing time for each request, from the reading of the first client bytes to fulfilling the request. Long response times can point to problems upstream.

NGINXによってログ出力された"request time"メトリクスは、クライアントからの最初のバイトの読み取りから、リクエストの対応が終わるまでの応答時間を記録しています。このメトリクス("request time"==応答時間)が、長くなっている場合は、バクエンドで処理をしているサーバーに問題が発生している可能性を示唆しています。

#### Collecting processing time metrics
> NGINX and NGINX Plus users can capture data on processing time by adding the `$request_time` variable to the access log format. More details on configuring logs for monitoring are available in our companion post on [NGINX metrics collection][21].

NGINXとNGINX Plusの両ユーザーは、`$request_time`の値をログ出力フォーマットに追加することで、処理時間を収集することができます。 ログの設定の詳しい手順については、このシリーズに含まれる[「NGINX metrics collection」][21]の記事を参照してください。

### Reverse proxy metrics

**Name**                              | **Description**                     | **[Metric type][22]** | **Availability** |
|------------------------------------- | ----------------------------------- | -------------------------------------------------------- | ----------------
Active connections by upstream server | Currently active client connections | Resource: Utilization                                    | NGINX Plus
5xx codes by upstream server          | Server errors                       | Work: Errors                                             | NGINX PlusAvailable servers per upstream group  | Servers passing health checks       | Resource: Availability                                   | NGINX Plus

> One of the most common ways to use NGINX is as a [reverse proxy][23]. The commercially supported NGINX Plus exposes a large number of metrics about backend (or "upstream") servers, which are relevant to a reverse proxy setup. This section highlights a few of the key upstream metrics that are available to users of NGINX Plus.

NGINXの最も代表的な使い道は、[リバースプロキシ][23]です。そして、商用版のNGINX Plusは、リバースプロキシとして使った場合に非常に価値のある、バックエンドサーバーに関するメトリクスが提供しています。このセクションでは、NGINX plusのユーザーに提供されているバックエンドサーバーに関する主要メトリクスの幾つかを取り上げていきます。(以降、バックエンドサーバーに関するメトリクスすは、"upstreamメトリクス"と呼びます。)

> NGINX Plus segments its upstream metrics first by group, and then by individual server. So if, for example, your reverse proxy is distributing requests to five upstream web servers, you can see at a glance whether any of those individual servers is overburdened, and also whether you have enough healthy servers in the upstream group to ensure good response times.

NGINX Plusは、"upstreamメトリクス"を、まずグループによって分類し、その後個々のサーバーに分類していきます。従って例えば、リバースプロキシーが5台のwebサーバーにリクエストを配分している場合、どれかのwebサーバーに過剰な負荷がかかっていないかを一目で確認することができます。(配分比が意図していない状況になっていないかを確認できます。)更に、満足できるレスポンス時間を確保できているかを確認するために、"upstream"グループ内に正しく動作しているサーバーが十分確保できているかを確認することができます。

#### **Activity metrics**
> The number of **active connections per upstream server** can help you verify that your reverse proxy is properly distributing work across your server group. If you are using NGINX as a load balancer, significant deviations in the number of connections handled by any one server can indicate that the server is struggling to process requests in a timely manner or that the load-balancing method (e.g., [round-robin or IP hashing][24]) you have configured is not optimal for your traffic patterns.

**upsteamサーバー単位でのactive connection**数は、リバースプロキシーがグループに所属する各サーバーに意図した通りに負荷を分散できているかの証明になります。もしも、NGINXをロードバランサーとして使用している場合で、各upstreamサーバーで処理されている"connection"数に大きな差がある場合は、"connection"数の少ないサーバーは適切な時間内にリクエストを処理することが難しい状態になっているか、現在採用している負荷分散方式(例:[round-robin or IP hashing][24])は処理しようとしているトラフィックのパターンに適合していなことが分かります。

#### Error metrics
> Recall from the error metric section above that 5xx (server error) codes are a valuable metric to monitor, particularly as a share of total response codes. NGINX Plus allows you to easily extract the number of **5xx codes per upstream server**, as well as the total number of responses, to determine that particular server's error rate.


既にエラーセクションでも紹介したように、5xx系(サーバー側エラー)コードは、監視対象としては非常に重要なメトリクスです。特に、レスポンスコード全体に占める5xx系コードの割合は、重要なメトリクスです。NGINX Plusでは、特定のサーバーのエラー発生率を判定するために、**upstream server毎の5xx系コード**の数やレスポンスの総数を簡単に収集することもできます。

#### **Availability metrics**
> For another view of the health of your web servers, NGINX also makes it simple to monitor the health of your upstream groups via the total number of **servers currently available within each group**. In a large reverse proxy setup, you may not care very much about the current state of any one server, just as long as your pool of available servers is capable of handling the load. But monitoring the total number of servers that are up within each upstream group can provide a very high-level view of the aggregate health of your web servers.

Webサーバーの状態を判断する別の方法として、NGINXには、各Upstreamグループの動作状態を**各グループ内で、現在リクエストの配給が可能なサーバー**の総数を使って監視できようにしています。リーバスプロキシーを使った大規模な環境では、リクエスト処理をする個々のサーバーの集合体が全体負荷を処理状態にあれば、単体サーバーの現状にはあまり関心がないはずです。しかし、各Upstreamのグループ内で稼働しているサーバーの合計数を監視することは、単体webサーバーを集合体としての集約し、全体的な視点でweb層の状態を提供していくれます。

#### **Collecting upstream metrics**
> NGINX Plus upstream metrics are exposed on the internal NGINX Plus monitoring dashboard, and are also available via a JSON interface that can serve up metrics into virtually any external monitoring platform. See examples in our companion post on [collecting NGINX metrics][25].

NGINX PlusのUpstreamメトリクスは、NGINX Plus内の監視ダッシュボードで提供されています。また、このメトリクスは、JSONインターフェースを介して外部の監視プラットフォームからも利用できるようになっています。詳細に関しては、[collecting NGINX metrics][25]の記事を参照してください。

## Conclusion
> In this post we've touched on some of the most useful metrics you can monitor to keep tabs on your NGINX servers. If you are just getting started with NGINX, monitoring most or all of the metrics in the list below will provide good visibility into the health and activity levels of your web infrastructure:

> - [Dropped connections][26]
> - [Requests per second][27]
> - [Server error rate][28]
> - [Request processing time][29]

このポストでは、NIGINXサーバーの状況を把握しておくために監視しておくべき有用なメトリクスの一部について紹介してきました。NGINXを使い始めている場合、以下のリストにあるメトリクスの大部分または全部を監視することで、Web層の健全性や稼働状態を把握する手助けをしてくれるはずです。

- [Dropped connections][26]
- [Requests per second][27]
- [Server error rate][28]
- [Request processing time][29]

> Eventually you will recognize additional, more specialized metrics that are particularly relevant to your own infrastructure and use cases. Of course, what you monitor will depend on the tools you have and the metrics available to you. See the companion post for [step-by-step instructions on metric collection][30], whether you use NGINX or NGINX Plus.

最終的には、あなたのインフラやユースケースに特に関連性のある、より専門的なメトリクスも存在することに気がつくでしょう。もちろん、何を監視するかは、持っているツールと監視可能なメトリクスの種類に依存しています。監視可能なメトリクスの違いを把握し、NGINXを採用するか、NGINX Plusを採用するかを検討するには、このシリーズに含まれる[step-by-step instructions on metric collection][30]を参考にしてください。

> At Datadog, we have built integrations with both NGINX and NGINX Plus so that you can begin collecting and monitoring metrics from all your web servers with a minimum of setup. Learn how to monitor NGINX with Datadog [in this post][31], and get started right away with [a free trial of Datadog][32].

Datadogでは、NGINXとNGINX Plus用の両方に向けてIntegrationを提供しています。これらのIntegrationを採用することで、最小限の設定で全てのwebのメトリクスを収集し監視できるようになります。このシリーズに含まれる[「How to monitor NGINX with Datadog」][31]では、Datadogを使ったNGINXの監視方法を解説しています。このポストを参考に、Datadogの[無料トライアルアカウント][32]に登録し、NGINXの監視を是非始めてみてください。

## Acknowledgments
> Many thanks to the NGINX team for reviewing this article prior to publication and providing important feedback and clarifications.

このポストを公開するに当たり、記事を事前にレビューし、重要なフィードバックと細部にわたる解説を提供してくれたNGINXチームに感謝します。

---- 

_Source Markdown for this post is available [on GitHub][33]. Questions, corrections, additions, etc.? Please [let us know][34]._

[1]:	/blog/how-to-collect-nginx-metrics/
[2]:	/blog/how-to-monitor-nginx-with-datadog/
[3]:	/blog/how-to-collect-nginx-metrics/
[4]:	/blog/how-to-monitor-nginx-with-datadog/
[5]:	http://nginx.org/en/
[6]:	http://nginx.com/resources/glossary/reverse-proxy-server/
[7]:	http://nginx.org/en/
[8]:	http://nginx.com/resources/glossary/reverse-proxy-server/
[9]:	/blog/monitoring-101-collecting-data/
[10]:	/blog/monitoring-101-collecting-data/
[11]:	http://nginx.org/en/docs/ngx_core_module.html#worker_connections
[12]:	http://nginx.org/en/docs/ngx_core_module.html#worker_connections
[13]:	#active-state
[14]:	https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/dropped_connections.png
[15]:	https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/requests_per_sec.png
[16]:	/blog/how-to-collect-nginx-metrics/
[17]:	/blog/monitoring-101-collecting-data/
[18]:	http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
[19]:	https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/5xx_rate.png
[20]:	/blog/monitoring-101-collecting-data/
[21]:	/blog/how-to-collect-nginx-metrics/
[22]:	/blog/monitoring-101-collecting-data/
[23]:	https://en.wikipedia.org/wiki/Reverse_proxy
[24]:	http://nginx.com/blog/load-balancing-with-nginx-plus/
[25]:	/blog/how-to-collect-nginx-metrics/
[26]:	#dropped-connections
[27]:	#requests-per-second
[28]:	#server-error-rate
[29]:	#request-processing-time
[30]:	/blog/how-to-collect-nginx-metrics/
[31]:	/blog/how-to-monitor-nginx-with-datadog/
[32]:	https://app.datadoghq.com/signup
[33]:	https://github.com/DataDog/the-monitor/blob/master/nginx/how_to_monitor_nginx.md
[34]:	https://github.com/DataDog/the-monitor/issues

[image-1]:	https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/nginx_connection_diagram-2.png
[image-2]:	https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/nginx_plus_connection_diagram-2.png
[image-3]:	https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/dropped_connections.png
[image-4]:	https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/requests_per_sec.png
[image-5]:	https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/5xx_rate.png