*This post is part 1 of a 3-part series on monitoring Amazon ELB. [Part 2](https://www.datadoghq.com/blog/how-to-collect-aws-elb-metrics) explains how to collect its metrics, and [Part 3](https://www.datadoghq.com/blog/monitor-elb-performance-with-datadog) shows you how Datadog can help you monitor ELB.*

## [翻訳作業中] What is Amazon Elastic Load Balancing?

Elastic Load Balancing (ELB) is an AWS service used to dispatch incoming web traffic from your applications across your Amazon EC2 backend instances, which may be in different availability zones.

ELB is widely used by web and mobile applications to help ensure a smooth user experience and provide increased fault tolerance, handling traffic peaks and failed EC2 instances without interruption.

ELB continuously checks for unhealthy EC2 instances. If any are detected, ELB immediately reroutes their traffic until they recover. If an entire availability zone goes offline, Elastic Load Balancing can even route traffic to instances in other availability zones. With [Auto Scaling](https://aws.amazon.com/autoscaling/), AWS can ensure your infrastructure includes the right number of EC2 hosts to support your changing application load patterns.

弾性負荷分散（ELB）は、異なるアベイラビリティゾーンであってもよいあなたのAmazon EC2のバックエンドインスタンス間で、アプリケーションからの着信Webトラフィックをディスパッチするために使用AWSサービスです。

ELBは広く、トラフィックのピークを処理し、スムーズなユーザーエクスペリエンスを確保し、増加したフォールトトレランスを提供するために、Webおよびモバイルアプリケーションで使用されると、中断することなく、EC2インスタンスを失敗しました。

ELBは、継続的に不健康なEC2インスタンスをチェックします。いずれかが検出された場合、それらが回復するまで、ELBはすぐにトラフィックを再ルーティングします。全体のアベイラビリティゾーンは、他の利用可能ゾーンでインスタンスにオフライン、弾性負荷分散することができてもルートトラフィックを進みます。オートスケーリングにより、AWSは、インフラストラクチャは、あなたの変更、アプリケーションの負荷パターンをサポートするためのEC2ホストの右の数を含んで確保することができます。



[![ELB dashboard - Datadog](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/1-01.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/1-01.png)

## Key ELB metrics

As the first gateway between your users and your application, load balancers are a critical piece of any scalable infrastructure. If it is not working properly, your users can experience much slower application response times or even outright errors, which can lead to lost transactions for example. That’s why ELB needs to be continuously monitored and its key metrics well understood to ensure that the load balancer itself and the EC2 instances behind it remain healthy. There are two broad categories of ELB metrics to monitor:

-   [Load balancer metrics](#elb-metrics)
-   [Backend-related metrics](#backend-metrics)

This article references metric terminology introduced in [our Monitoring 101 series](https://www.datadoghq.com/blog/monitoring-101-collecting-data/), which provides a framework for metric collection and alerting.

ユーザーとアプリケーションの間の最初のゲートウェイとして、ロードバランサは、任意のスケーラブルなインフラストラクチャの重要な部分です。それが正常に動作しない場合、ユーザーは、例えば、失われたトランザクションにつながる可能性が非常に遅く、アプリケーションの応答時間、あるいはあからさまなエラーを、体験することができます。 ELBを継続的に監視する必要があり、その主要な指標はよくその背後にあるロードバランサ自体とEC2インスタンスが正常な状態であることを確実にするために理解している理由です。監視するELBメトリックの2つのカテゴリがあります。

ロードバランサのメトリック
バックエンド関連のメトリック
この記事の参照メトリック用語は、メトリック収集と警告するためのフレームワークを提供し、当社のモニタリング101シリーズで導入されました。


### Load balancer metrics

![Load balancer metrics](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/1-02.png)

The first category of metrics to consider comes from the load balancer itself, as opposed to the backend instances registered with the load balancer. For each metric we noted the most relevant and useful statistic to monitor (sum, avg, min, or max) since they are usually all available.

ロードバランサに登録され、バックエンドのインスタンスとは対照的に考慮すべきメトリクスの第一のカテゴリーは、ロードバランサ自体から来ています。各メトリックのために我々は監視するために最も関連性の高い、有用な統計を指摘（合計、平均、最小、または最大）彼らは通常、すべての利用可能であるからです。


| **Name**                 | **Description**                                                                                                                    | [**Metric Type**](https://www.datadoghq.com/blog/monitoring-101-collecting-data/) |
|--------------------------|------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| **RequestCount**         | Number of requests ELB received and sent to the registered EC2 instances during the selected time period (sum).                    | Work: Throughput                                                                  |
| **SurgeQueueLength**     | Number of inbound requests currently queued by the load balancer waiting to be accepted and processed by a backend instance (max). | Resource: Saturation                                                              |
| **SpilloverCount**       | Number of requests that have been rejected due to a full surge queue during the selected time period (sum).                        | Work: Error (due to resource saturation)                                          |
| **HTTPCode\_ELB\_4XX\*** | Number of HTTP 4xx errors (client error) returned by the load balancer during the selected time period (sum).                      | Work: Error                                                                       |
| **HTTPCode\_ELB\_5XX\*** | Number of HTTP 5xx errors (server error) returned by the load balancer during the selected time period (sum).                      | Work: Error                                                                       |

\* *Elastic Load Balancing configuration requires one or more* *[listeners](http://docs.aws.amazon.com/ElasticLoadBalancing/latest/DeveloperGuide/elb-listener-config.html), which are ELB processes that check for connection requests. The HTTPCode\_ELB\_\* metrics named above will be available only if the listener is configured with HTTP or HTTPS protocol for both front- and back-end connections.*

*弾性負荷分散構成は、接続要求を確認ELBプロセスである1つ以上のリスナーが必要です。上記の名前メトリック\ HTTPCode_ELB_は、バックエンド接続をリスナーが両方のフロント用のHTTPまたはHTTPSプロトコルで構成されている場合にのみ利用できるようにとなります。*


#### Metrics to alert on:

-   **RequestCount:** This metric measures the amount of traffic your load balancer is handling. Keeping an eye on peaks and drops allows you to alert on drastic changes which might indicate a problem with AWS or upstream issues like DNS. If you are **not** using [Auto Scaling](https://aws.amazon.com/autoscaling/), then knowing when your request count changes significantly can also help you know when to adjust the number of instances backing your load balancer.
-   **SurgeQueueLength**: When your backend instances are fully loaded and can’t process any more requests, incoming requests are queued, which can increase latency ([see below](#backend-metrics)) leading to slow user navigation or timeout errors. That’s why this metric should remain as low as possible, ideally at zero. Backend instances may refuse new requests for many reasons, but it’s often due to too many open connections. In that case you should consider tuning your backend or adding more backend capacity. The “max” statistic is the most relevant view of this metric so that peaks of queued requests are visible. Crucially, make sure the queue length always remains substantially smaller than the maximum queue capacity, currently capped to 1,024 requests, so you can avoid dropped requests.
-   **SpilloverCount**: When the **SurgeQueueLength** reaches the maximum of 1,024 queued requests, new requests are dropped, the user receives a 503 error, and the spillover count metric is incremented. In a healthy system, this metric is always equal to zero.
-   **HTTPCode\_ELB\_5XX**: This metric counts the number of requests that could not be properly handled. It can have different root causes:
    -   If the error code is [502 (Bad Gateway)](http://docs.aws.amazon.com/ElasticLoadBalancing/latest/DeveloperGuide/ts-elb-error-message.html#ts-elb-errorcodes-http502), the backend instance returned a response, but the load balancer couldn’t parse it because the load balancer was not working properly or the response was malformed.
    -   If it’s [503 (Service Unavailable)](http://docs.aws.amazon.com/ElasticLoadBalancing/latest/DeveloperGuide/ts-elb-error-message.html#ts-elb-errorcodes-http503), the error comes from your backend instances or the load balancer, which may not have had enough capacity to handle the request. Make sure your instances are healthy and registered with your load balancer.
    -   If a [504 error (Gateway Timeout)](http://docs.aws.amazon.com/ElasticLoadBalancing/latest/DeveloperGuide/ts-elb-error-message.html#ts-elb-errorcodes-http504) is returned, the response time exceeded ELB’s idle timeout. You can confirm it by checking if latency (see table below) is high and 5xx errors are returned by ELB. In that case, consider scaling up your backend, tuning it, or increasing the idle timeout to support slow operations such as file uploads. If your instances are closing connections with ELB, you should enable keep-alive with a timeout higher than the ELB idle timeout.

RequestCount：このメトリックは、ロードバランサが処理しているトラフィックの量。ピークと滴に目を保つことはあなたがAWSやDNSなどの上流の問題に問題がある可能性があり急激な変化に警告することができます。あなたの要求カウントの変化が著しく、また、あなたのロードバランサをバックアップするインスタンスの数を調整するときにあなたが知っている助けることができるときに知って、自動スケーリングを使用していない場合。
SurgeQueueLength：あなたのバックエンドインスタンスが完全にロードされ、それ以上の要求を処理できない場合、着信要求は、ユーザーのナビゲーションやタイムアウトエラーを遅くするリーディング（下記参照）の待ち時間を増やすことができ、キューイングされます。このメトリックは、理想的にはゼロで、できるだけ低いままでなければならない理由です。バックエンドのインスタンスは、多くの理由のための新しい要求を拒否することができるが、それは多くの場合、あまりにも多くのオープン接続が原因です。その場合は、あなたのバックエンドを調整する以上のバックエンドの容量を追加することを検討すべきです。キューに入れられた要求のピークが表示されるように「最大」統計は、このメトリックの最も関連性の図です。決定的に、あなたがドロップされたリクエストを避けることができるようにキュー長は常に、現在1024の要求にキャップされたキューの最大容量、より実質的に小さいままであることを確認してください。
SpilloverCount：SurgeQueueLengthは1024キューに入れられた要求の最大に達すると、新しい要求は廃棄され、ユーザーは503エラーを受け取り、スピルオーバーカウントメトリックをインクリメントします。健全なシステムでは、このメトリックは常にゼロに等しいです。
HTTPCode_ELB_5XX：このメトリックは、適切に処理することができなかった要求の数をカウントします。それは別の根本原因を持つことができます。
エラーコードは502（不正なゲートウェイ）である場合は、バックエンドのインスタンスが応答を返しますが、ロードバランサが正常に動作していなかったか、応答が不正であったため、ロードバランサは、それを解析できませんでした。
それは503（サービス利用不可）の場合は、エラーが要求を処理するのに十分な容量を持っていない可能性があり、あなたのバックエンドインスタンスまたはロードバランサ、から来ています。あなたのインスタンスが健康であなたのロードバランサに登録されていることを確認します。
504エラー（ゲートウェイタイムアウト）が返された場合、応答時間はELBのアイドルタイムアウトを超えました。あなたが高く、5xxのエラーがELBによって返されるレイテンシが（下の表を参照）か否かをチェックすることによって、それを確認することができます。その場合は、それをチューニングし、バックエンドのスケールアップ、またはそのようなファイルのアップロードなどの低速の操作をサポートするために、アイドルタイムアウトを増やすことを検討してください。あなたのインスタンスがELBとの接続をクローズしている場合は、キープアライブELBアイドルタイムアウトよりもタイムアウトで有効にする必要があります。


[![Load balancer metrics graphs](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/1-03.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/1-03.png)

#### Note about HTTPCode\_ELB\_4XX:

There is usually not much you can do about 4xx errors, since this metric basically measures the number of erroneous requests sent to ELB (which returns a 4xx code). If you want to investigate, you can check in the ELB access logs (see [Part 2](https://www.datadoghq.com/blog/how-to-collect-aws-elb-metrics)) to determine [which code has been returned](http://docs.aws.amazon.com/ElasticLoadBalancing/latest/DeveloperGuide/ts-elb-error-message.html#ts-elb-errorcodes-http400).

このメトリックは、基本的に（の4xxコードを返します）ELBに送信された誤った要求の数を測定するので、ずっとあなたが4xxのエラーについて行うことができない通常あります。あなたが調査したい場合は、ELBのアクセスログで確認することができます返されたコードを決定する（第2部を参照してください）。


### Backend-related metrics

![Backend metrics](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/1-04.png)

CloudWatch also provides metrics about the status and performance of your backend instances, for example response latency or the results of ELB health checks. Health checks are the mechanism ELB uses to identify unhealthy instances so it can send requests elsewhere. You can use the default health checks or [configure them](http://docs.aws.amazon.com/ElasticLoadBalancing/latest/DeveloperGuide/elb-healthchecks.html) to use different protocols, ports, or healthy/unhealthy thresholds. The frequency of health checks is 30 seconds by default but you can set this interval to anywhere between 5–300 seconds.

CloudWatchのは、ステータスとパフォーマンスのバックエンドインスタンスの、例応答待ち時間またはELBヘルスチェックの結果に関するメトリックを提供します。ヘルスチェックは、それが他の場所で要求を送信できるようにELBが不健全なインスタンスを識別するために使用するメカニズムです。デフォルトのヘルスチェックを使用するか、別のプロトコル、ポート、または健康/不健康なしきい値を使用するように設定することができます。ヘルスチェックの頻度は、デフォルトでは30秒ですが、あなたはどこでも5から300の間の秒にこの間隔を設定することができます。

<table>
<colgroup>
<col width="33%" />
<col width="33%" />
<col width="33%" />
</colgroup>
<tbody>
<tr class="odd">
<td align="left"><strong>Name</strong></td>
<td align="left"><strong>Description</strong></td>
<td align="left"><a href="https://www.datadoghq.com/blog/monitoring-101-collecting-data/"><strong>Metric Type</strong></a></td>
</tr>
<tr class="even">
<td align="left"><strong>HealthyHostCount *</strong></td>
<td align="left">Current number of healthy instances in each availability zone.</td>
<td align="left">Resource: Availability</td>
</tr>
<tr class="odd">
<td align="left"><strong>UnHealthyHostCount *</strong></td>
<td align="left">Current number of unhealthy instances in each availability zone.</td>
<td align="left">Resource: Availability</td>
</tr>
<tr class="even">
<td align="left"><strong>Latency</strong></td>
<td align="left">Round-trip request-processing time between load balancer and backend</td>
<td align="left">Work: Performance</td>
</tr>
<tr class="odd">
<td align="left"><strong>HTTPCode_Backend_2XX</strong>
<strong>HTTPCode_Backend_3XX</strong></td>
<td align="left">Number of HTTP 2xx (success) / 3xx (redirection) codes returned by the registered backend instances during the selected time period.</td>
<td align="left">Work: Success</td>
</tr>
<tr class="even">
<td align="left"><strong>HTTPCode_Backend_4XX</strong>
<strong>HTTPCode_Backend_5XX</strong></td>
<td align="left">Number of HTTP 4xx (client error) / 5xx (server error) codes returned by the registered backend instances during the selected time period.</td>
<td align="left">Work: Error</td>
</tr>
<tr class="odd">
<td align="left"><strong>BackendConnectionErrors</strong></td>
<td align="left">Number of attempted but failed connections between the load balancer and a seemingly-healthy backend instance.</td>
<td align="left">Resource: Error</td>
</tr>
</tbody>
</table>

\* These counts can be tricky to interpret in CloudWatch in some cases. Indeed, when [Cross-Zone Balancing](http://docs.aws.amazon.com/ElasticLoadBalancing/latest/DeveloperGuide/enable-disable-crosszone-lb.html) is enabled on an ELB (to make sure traffic is evenly spread across the different availability zones), all the instances attached to this load balancer are considered part of **all** AZs by CloudWatch (see [Part 2](https://www.datadoghq.com/blog/how-to-collect-aws-elb-metrics) for more about metrics collection). So if you have for example two healthy instances in one zone and three in the other, ELB will display five healthy hosts **per AZ**, which can be counter-intuitive.

*これらのカウントは、いくつかのケースではCloudWatchの中で解釈するのが難しいことができます。クロスゾーンバランシングがELBで有効になっているとき実際、CloudWatchの（についての情報パート2を参照することによって、このロードバランサに接続されたすべてのインスタンスがすべてAZSの一部とみなされる（必ずトラフィックが均等に異なるアベイラビリティゾーンにまたがっているために）指標の収集）。あなたが他の、例えば1ゾーンと3人に2人の健康のインスタンスを持っているのであれば、ELBは直感に反することができAZあたり5健康のホストを、表示されます。

#### Metrics to alert on:

-   **HealthyHostCount** and **UnHealthyHostCount**: If an instance exceeds the unhealthy threshold defined for the health checks, ELB flags it and stops sending requests to that instance. The most common cause is the health check exceeding the load balancer’s timeout ([see note below](#timeouts) about timeouts). Make sure to always have enough healthy backend instances in each availability zone to ensure good performance. You should also correlate this metric with **Latency** and **SurgeQueueLength** to make sure you have enough instances to support the volume of incoming requests without substantially slowing down the response time.
-   **Latency**: This metric measures your application latency due to request processing by your backend instances, not latency from the load balancer itself. Tracking backend latency gives you good insight on your application performance. If it’s high, requests might be dropped due to timeouts, which can lead to frustrated users. High latency can be caused by network issues, overloaded backend hosts, or non-optimized configuration (enabling keep-alive can help reduce latency for example). [Here are a few tips](https://aws.amazon.com/premiumsupport/knowledge-center/elb-latency-troubleshooting/) provided by AWS to troubleshoot high latency.

HealthyHostCountとUnHealthyHostCount：インスタンスは、ヘルスチェック用に定義された不健康なしきい値を超えたELBフラグは、そのインスタンスへの要求の送信を停止した場合。最も一般的な原因は、ロードバランサのタイムアウト（タイムアウトについては下記の注を参照）を超えるヘルスチェックです。常に良好なパフォーマンスを確保するために、各アベイラビリティゾーンに十分な健全なバックエンドのインスタンスを持っていることを確認してください。また、あなたは、実質的に応答時間を遅くすることなく、着信要求のボリュームをサポートするのに十分なインスタンスを持っていることを確認するためにレイテンシとSurgeQueueLengthでこのメトリックを関連付ける必要があります。

レイテンシ：あなたのバックエンドのインスタンスによるによる要求処理にこのメトリックは、あなたのアプリケーションの遅延は、ロードバランサ自体からレイテンシません。バックエンドの待ち時間を追跡することは、あなたのアプリケーションのパフォーマンスに優れた洞察力を与えます。それが高いなら、要求が原因でイライラユーザーにつながる可能性がタイムアウトに廃棄される可能性があります。高レイテンシは（キープアライブ有効にすると、例えば、待ち時間を減らすことができます）ネットワークの問題、オーバーロードされたバックエンドホスト、または非最適化された構成によって発生することができます。ここで、高遅延のトラブルシューティングを行うには、AWSが提供するいくつかのヒントがあります。


#### Metric to watch:

**BackendConnectionErrors**: Connection errors between ELB and your servers occur when ELB attempts to connect to a backend, but cannot successfully do so. This type of error is usually due to network issues or backend instances that are not running properly. If you are already alerting on ELB errors and latency, you may not want to be alerted about connection errors that are not directly impacting users.

NOTE: If a connection with the backend fails, ELB will retry it, so this count can be higher than the request rate.

BackendConnectionErrors：ELBとサーバー間の接続エラーがELBは、バックエンドに接続しようとするときに発生するが、正常にそうすることはできません。このタイプのエラーは、ネットワークの問題や正常に実行されていないバックエンドインスタンスに通常起因しています。すでにELBエラーや待ち時間に警告している場合は、直接ユーザーに影響を与えていない接続エラーについて警告されたくないかもしれません。

注：バックエンドとの接続に失敗した場合は、ELBはそれを再試行しますので、このカウントが要求率よりも高くすることができます。


[![Backend metrics graphs](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/1-05.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/1-05.png)

#### About backend response codes

You might want to monitor the HTTP codes returned by your backend for a high-level view of your servers. But for more granularity and better insight about your servers, you should monitor them directly or by collecting native metrics from your instances (see [Part 3](https://www.datadoghq.com/blog/monitor-elb-performance-with-datadog)), or also analyze their logs (see [Part 2](https://www.datadoghq.com/blog/how-to-collect-aws-elb-metrics)).

あなたは、あなたのサーバーの高レベルのビューのためにバックエンドから返されたHTTPコードを監視することができます。しかし、より多くの細かさやサーバーに関するより深い洞察のために、あなたが直接、またはあなたのインスタンスからネイティブのメトリックを収集することにより、それらを監視する必要があります（第3部を参照してください）、あるいはまた、それらのログを（パート2を参照）を分析。


#### About timeouts

For each request, there is one connection between the client and load balancer, and one connection between the load balancer and backend. And for each request, ELB has an overall idle timeout which is by default 60 seconds. If a request is not completed within these 60 seconds, the connection is closed. If necessary you can increase this idle timeout to make sure long operations like file transfers can be completed.

You might want to consider enabling keep-alive in your EC2 backend instances settings so your load balancer can reuse connections with your backend hosts, which decreases their resource utilization. Make sure the keep-alive time is set to more than the ELB’s idle timeout so the backend instances won’t close a connection before the load balancer does—otherwise ELB might incorrectly flag your backend host as unhealthy.

各要求について、クライアントとロードバランサの間に1つの接続、およびロードバランサとバックエンドの間に1つの接続があります。そして、要求ごとに、ELBは、デフォルトは60秒です全体のアイドルタイムアウトを持っています。要求がこれらの60秒以内に完了しない場合、接続が閉じられます。あなたは、ファイル転送が完了することができるようにしてください長い操作を行うために、このアイドルタイムアウトを増やすことができ、必要な場合。

あなたはキープアライブあなたのEC2のバックエンドインスタンスの設定であなたのロードバランサは、それらのリソース使用率を減少させ、バックエンドホストとの接続を再利用することができますので、有効にすることを検討することをお勧めします。ロードバランサは、前にバックエンドインスタンスが接続を閉じないように、キープアライブ時間がELBのアイドルタイムアウト以上に設定されていることを確認してい-そうでない場合はELBは間違って不健康としてバックエンドホストにフラグを立てるかもしれません。


### Hosts metrics for a full picture

Backend instances’ health and load balancers’ performance are directly related. For example, high CPU utilization on your backend instances can lead to queued requests. These queues can eventually exceed their maximum length and start dropping requests. So keeping an eye on your backend hosts’ resources is a very good idea. For these reasons, a complete picture of ELB’s performance and health includes EC2 metrics. We will detail in [Part 3](https://www.datadoghq.com/blog/monitor-elb-performance-with-datadog) how correlating ELB metrics with EC2 metrics will help you gain better insights.

バックエンドインスタンスの健康とロードバランサのパフォーマンスは直接関連しています。たとえば、バックエンドのインスタンス上の高いCPU使用率は、キューに登録された要求につながることができます。これらのキューは、最終的にそれらの最大長を超えて、要求をドロップし始めることができます。だからあなたのバックエンドホストのリソースに目を保つことは非常に良いアイデアです。これらの理由から、ELBのパフォーマンスと健康の全体像は、EC2のメトリックが含まれます。私たちは、詳細パート3にEC2の指標とELBメトリックを相関することで、より良い洞察を得るのに役立ちますでしょうか。


## Conclusion

In this post we have explored the most important Amazon ELB performance metrics. If you are just getting started with Elastic Load Balancing, monitoring the metrics listed below will give you great insight into your load balancers, as well as your backend servers’ health and performance:

-   **[**Request count**](#RequestCount)**
-   **[**Surge queue length** and **spillover count**](#SurgeQueueLength)**
-   [**ELB 5xx errors**](#HTTPCode_ELB_5XX)
-   [**Backend instances health status**](#backend-metrics)
-   **[Backend latency](#backend-metrics)**

[Part 2 of this series](https://www.datadoghq.com/blog/how-to-collect-aws-elb-metrics) provides instructions for collecting all the metrics you need from ELB.


この記事では、最も重要なアマゾンELBパフォーマンス・メトリックを検討しています。あなただけの弾性負荷分散の使用を開始している場合は、以下に示す評価指標を監視することはあなたに偉大なあなたのロードバランサへの洞察だけでなく、バックエンドサーバーの状態とパフォーマンスを提供します：

[リクエスト数]（＃RequestCount）
（＃のSurgeQueueLength）[キューの長さと波及カウントサージ]
ELBの5xxのエラー
バックエンドインスタンス健康状態
バックエンドの待ち時間

このシリーズの第2回では、あなたがELBから必要なすべてのメトリックを収集するための手順を説明します。