*This post is part 2 of a 3-part series on monitoring Amazon ELB. [Part 1](https://www.datadoghq.com/blog/top-elb-health-and-performance-metrics) explores its key performance metrics, and [Part 3](https://www.datadoghq.com/blog/monitor-elb-performance-with-datadog) shows you how Datadog can help you monitor ELB.*

This part of the series is about collecting ELB metrics, which are available from AWS via CloudWatch. They can be accessed in three different ways:

-   [Using the AWS Management Console](#console)
-   [Using the command-line interface (CLI)](#cli)
-   [Using a monitoring tool integrating the CloudWatch API](#tools)

We will also explain how [using ELB access logs](#logs) can be useful when investigating on specific request issues.

この投稿は、監視はAmazon ELBに3回シリーズの第2部です。パート1は、その主要なパフォーマンス指標を探り、そして第3部はDatadogあなたがELBの監視に役立つことができる方法を示します。

シリーズのこの部分はCloudWatchの経由AWSから入手可能であるELBメトリックを収集についてです。彼らは、3つの異なる方法でアクセスできます。

AWS管理コンソールを使用しました
コマンドラインインターフェイスを使用して、（CLI）
CloudWatchのAPIを統合監視ツールを使用して、

特定の要求の問題について調査する際に有用であり得るELBアクセスログを使用して、どのように我々はまた、説明します。


## [翻訳作業中]　Using the AWS Management Console

Using the online management console is the simplest way to monitor your load balancers with CloudWatch. It allows you to set up basic automated alerts and to get a visual picture of recent changes in individual metrics.

オンライン管理コンソールを使用すると、CloudWatchのを使用してロードバランサを監視するための最も簡単な方法です。それはあなたが基本的な自動化されたアラートを設定すると、個々のメトリックの最近の変化を視覚的に把握することができます。


### Graphs

Once you are signed in to your AWS account, you can open the [CloudWatch console](https://console.aws.amazon.com/cloudwatch/home#metrics:) and then browse the metrics related to the different AWS services.

あなたのAWSアカウントにサインインしたら、CloudWatchのコンソールを開き、別のAWSサービスに関連するメトリックを閲覧することができます。


[![ELB metrics in AWS Console](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-01.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-01.png)

By clicking on the ELB Metrics category, you will see the list of available metrics per load balancer, per availability zone:

ELBメトリックカテゴリをクリックすると、アベイラビリティゾーンごとに、ロードバランサごとに使用可能なメトリックのリストが表示されます：。


[![List of ELB metrics in AWS Console](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-02.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-02.png)

You can also view the metrics across all your load balancers:

また、すべてのあなたのロードバランサでの統計情報を表示できます。

[![List of ELB metrics across all load balancers](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-03.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-03.png)

Just select the checkbox next to the metrics you want to visualize, and they will appear in the graph at the bottom of the console:

ちょうどあなたが視覚化するメトリックの隣にあるチェックボックスを選択し、それらは、コンソールの下部にあるグラフに表示されます。

[![ELB metrics graphs in AWS Console](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-04.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-04.png)

### Alerts

With the CloudWatch Management Console you can also create simple alerts that trigger when a metric crosses a specified threshold.

Click on the “Create Alarm” button at the right of your graph, and you will be able to set up the alert and configure it to notify a list of email addresses:

CloudWatchの管理コンソールを使用すると、また、メトリックが指定されたしきい値を超えたときにトリガする単純なアラートを作成することができます。

グラフの右側にある「アラームを作成」ボタンをクリックすると、アラートを設定することができますし、電子メールアドレスのリストを通知するように設定します：


[![ELB alerts in AWS Console](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-05.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-05.png)

## Using the AWS Command Line Interface

You can also retrieve metrics related to a load balancer from the command line. To do so, you will need to install the AWS Command Line Interface (CLI) by following [these instructions](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html). You will then be able to query for any CloudWatch metric, using different filters.

Command line queries can be useful for spot checks and ad hoc investigations when you can’t, or don’t want to, use a browser.

For example, if you want to know the health state of all the backend instances registered to a load balancer, you can run:

また、コマンドラインからロードバランサに関連するメトリックを取得することができます。これを行うには、次の手順に従って、AWSコマンドラインインターフェイス（CLI）をインストールする必要があります。その後、別のフィルタを使用して、任意のCloudWatchのメトリックを照会することができるようになります。

コマンドラインクエリは、スポットチェックやアドホック調査はできませんので、または、ブラウザを使用しないために有用であり得ます。

あなたはロードバランサに登録されているすべてのバックエンドインスタンスの健康状態を知りたい場合たとえば、次のコマンドを実行します。


`aws elb describe-instance-health --load-balancer-name my-load-balancer`

That command should return a JSON output of this form:

このコマンドは、この形式のJSON出力を返す必要があります：

<table>
<colgroup>
<col width="50%" />
<col width="50%" />
</colgroup>
<tbody>
<tr class="odd">
<td align="left"><div class="crayon-pre" style="font-size: 14px !important; line-height: 18px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;">
<div id="crayon-5627aa87106f2681009851-1" class="crayon-line">
 
</div>
<div id="crayon-5627aa87106f2681009851-2" class="crayon-line">
{
</div>
<div id="crayon-5627aa87106f2681009851-3" class="crayon-line">
  &quot;InstanceStates&quot;: [
</div>
<div id="crayon-5627aa87106f2681009851-4" class="crayon-line">
      {
</div>
<div id="crayon-5627aa87106f2681009851-5" class="crayon-line">
          &quot;InstanceId&quot;: &quot;i-xxxxxxxx&quot;,
</div>
<div id="crayon-5627aa87106f2681009851-6" class="crayon-line">
          &quot;ReasonCode&quot;: &quot;N/A&quot;,
</div>
<div id="crayon-5627aa87106f2681009851-7" class="crayon-line">
          &quot;State&quot;: &quot;InService&quot;,
</div>
<div id="crayon-5627aa87106f2681009851-8" class="crayon-line">
          &quot;Description&quot;: &quot;N/A&quot;
</div>
<div id="crayon-5627aa87106f2681009851-9" class="crayon-line">
      },
</div>
<div id="crayon-5627aa87106f2681009851-10" class="crayon-line">
      {
</div>
<div id="crayon-5627aa87106f2681009851-11" class="crayon-line">
          &quot;InstanceId&quot;: &quot;i-xxxxxxxx&quot;,
</div>
<div id="crayon-5627aa87106f2681009851-12" class="crayon-line">
          &quot;ReasonCode&quot;: &quot;N/A&quot;,
</div>
<div id="crayon-5627aa87106f2681009851-13" class="crayon-line">
          &quot;State&quot;: &quot;InService&quot;,
</div>
<div id="crayon-5627aa87106f2681009851-14" class="crayon-line">
          &quot;Description&quot;: &quot;N/A&quot;
</div>
<div id="crayon-5627aa87106f2681009851-15" class="crayon-line">
      },
</div>
<div id="crayon-5627aa87106f2681009851-16" class="crayon-line">
  ]
</div>
<div id="crayon-5627aa87106f2681009851-17" class="crayon-line">
}
</div>
<div id="crayon-5627aa87106f2681009851-18" class="crayon-line">
 
</div>
</div></td>
</tr>
</tbody>
</table>

[Here](http://docs.aws.amazon.com/cli/latest/reference/elb/index.html) are all the ELB commands you can run with the CLI.

ここELBを使用すると、CLIで実行できるコマンド全てです。


## Monitoring tool integrated with CloudWatch

The third way to collect CloudWatch metrics is via your own monitoring tools, which can offer extended monitoring functionality.

You probably need a dedicated monitoring system if, for example, you want to:

-   Correlate metrics from one part of your infrastructure with others (including custom infrastructure or applications)
-   Dynamically slice, aggregate, and filter your metrics on any attribute
-   Access historical data
-   Set up sophisticated alerting mechanisms

CloudWatch can be integrated with outside monitoring systems  via API, and in many cases the integration just needs to be enabled to start working.

As explained in [Part 1](https://www.datadoghq.com/blog/top-elb-health-and-performance-metrics), CloudWatch’s ELB-related metrics give you great insight about your load balancers’ health and performance. However, for more precision and granularity on your backend instances’ performance, you should consider monitoring their resources directly. Correlating native metrics from your EC2 instances with ELB metrics will give you a fuller, more precise picture. In [Part 3](https://www.datadoghq.com/blog/monitor-elb-performance-with-datadog), we cover a concrete example of this type of metrics collection and detail how to monitor ELB using Datadog.

CloudWatchのメトリックを収集するための第三の方法は、拡張された監視機能を提供することができ、独自の監視ツールを介してです。

例えば、あなたがしたい場合は、おそらく専用の監視システムが必要になります。

（カスタムインフラストラクチャやアプリケーションを含む）他のユーザーとインフラストラクチャの一部からのメトリックを関連付けます
動的に集約、スライス、および任意の属性にあなたのメトリックをフィルタリング
アクセス履歴データ
洗練された警告メカニズムを設定します
CloudWatchのは、APIを介して外部監視システムと統合され、多くの場合、積分は単に作業を開始することを可能にする必要があることができます。

パート1で説明したように、CloudWatchののELB-関連のメトリックは、あなたのロードバランサの健康とパフォーマンスについての素晴らしい洞察力を与えます。しかし、あなたのバックエンドインスタンスのパフォーマンスの詳細精度と粒度のために、あなたが直接そのリソースの監視を検討する必要があります。 ELBメトリックを使用してEC2インスタンスからネイティブメトリックを相関させること、あなたに充実し、より正確な画像が得られます。第3部では、指標の収集とELBがDatadogを使用して監視する方法を詳細のこのタイプの具体的な例をカバーしています。


## ELB Access Logs

ELB access logs capture all the information about every request received by the load balancer, such as a time stamp, client IP address, path, backend response, latency, and so on. It can be useful to investigate the access logs for particular requests in case of issues.

ELBのアクセスログは、というように、このようなタイムスタンプ、クライアントのIPアドレス、パス、バックエンドの応答、待ち時間としてロードバランサで受信したすべてのリクエストに関するすべての情報をキャプチャし、。問題の場合には、特定の要求のためのアクセスログを調査することが有用であり得ます。


### Configuring the access logs

First you must enable the access logs feature, which is disabled by default. Logs are stored in an Amazon S3 bucket, which incurs additional storage costs.

Elastic Load Balancing creates [log files](http://docs.aws.amazon.com/ElasticLoadBalancing/latest/DeveloperGuide/access-log-collection.html#access-log-file-format) at user-defined intervals, between 5 and 60 minutes. Every single request received by ELB is logged, including those requests that couldn’t be processed by your backend instances (see [Part 1](https://www.datadoghq.com/blog/top-elb-health-and-performance-metrics) for the different root causes of ELB issues). You can see more details [here](http://docs.aws.amazon.com/ElasticLoadBalancing/latest/DeveloperGuide/access-log-collection.html#access-log-entry-format) about the log entry format and the different fields containing information about a request.

まず、デフォルトでは無効になってアクセスログ機能を、有効にする必要があります。ログには、追加のストレージコストがかかるのAmazon S3バケットに格納されます。

弾性負荷分散は、5〜60分の間で、ユーザ定義の間隔でログファイルが作成されます。 ELBで受信したすべての単一の要求は、バックエンドのインスタンス（ELBの問題の別の根本原因のためにパート1を参照）によって処理することができなかったこれらの要求を含め、ログに記録されます。あなたは、ログエントリのフォーマットや要求に関する情報を含む異なるフィールドについてはこちらの詳細を見ることができます。


### Analyzing logs

ELB access logs can be useful when troubleshooting and investigating specific requests. However, if you want to find and analyze patterns in the overall access log files, you might want to use dedicated log analytics tools, especially if you are dealing with large amount of traffic generating heavy log file volume.

トラブルシューティングおよび特定の要求を調査する際ELBアクセスログが役立ちます。あなたが見つけると、全体的なアクセス・ログ・ファイル内のパターンを分析したい場合は、あなたが重いログファイルのボリュームを生成する大量のトラフィックを扱っている場合は特に、専用のログ分析ツールを使用することもできます。


## Conclusion

In this post we have walked through how to use CloudWatch to collect and visualize ELB metrics, how to generate alerts when these metrics go out of bounds, and how to use access logs for troubleshooting.

In the [next and final part on this series](https://www.datadoghq.com/blog/monitor-elb-performance-with-datadog) you will learn how you can monitor ELB metrics using the Datadog integration, along with native metrics from your backend instances for a complete view, with a minimum of setup.

この記事では、我々はELBメトリックを収集し、視覚化するCloudWatchの使用方法を歩いている、これらの指標は、トラブルシューティングのためにアクセスログを使用する方法を境界の外に出て、ときにアラートを生成する方法について説明します。

このシリーズの次のと最後の部分では、セットアップを最小限に抑えて、完全なビューのためのバックエンドインスタンスからネイティブの指標とともに、Datadog統合を使用して、ELBのメトリックを監視する方法を学びます。