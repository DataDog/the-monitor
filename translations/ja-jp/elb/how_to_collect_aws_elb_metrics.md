> *This post is part 2 of a 3-part series on monitoring Amazon ELB. [Part 1](https://www.datadoghq.com/blog/top-elb-health-and-performance-metrics) explores its key performance metrics, and [Part 3](https://www.datadoghq.com/blog/monitor-elb-performance-with-datadog) shows you how Datadog can help you monitor ELB.*

*このポストは、Amazon ELBの監視に関する3回シリーズのPart 2です。 [Part 1](https://www.datadoghq.com/blog/top-elb-health-and-performance-metrics)では、ELBのキーメトリクスを解説しています。[Part 3](https://www.datadoghq.com/blog/monitor-elb-performance-with-datadog)では、Amazon ELBの監視にDatadogを役立てる方法を解説していきます。*


> This part of the series is about collecting ELB metrics, which are available from AWS via CloudWatch. They can be accessed in three different ways:
> 
> -   [Using the AWS Management Console](#console)
> -   [Using the command-line interface (CLI)](#cli)
> -   [Using a monitoring tool integrating the CloudWatch API](#tools)
> 
> We will also explain how [using ELB access logs](#logs) can be useful when investigating on specific request issues.

シリーズのこの部分では、AWSのCloudWatch経由で集取できるELBメトリクスの集取方法に関し解説していきます。それらのメトリクスには、次の3つの方法でアクセスすることができます:

- [AWS管理コンソールを使用して](#console)
- [コマンドラインインターフェイスを使用して（CLI）](#cli)
- [CloudWatchのAPIをつかった監視ツールを使用して](#tools)

ELBのアクセスログの使用が、特定リクエストの問題の調査に有用なことも解説していきます。


## Using the AWS Management Console

> Using the online management console is the simplest way to monitor your load balancers with CloudWatch. It allows you to set up basic automated alerts and to get a visual picture of recent changes in individual metrics.

オンライン管理コンソールの使用は、CloudWatchを使ったロードバランサーの監視としては最も簡単な方法です。この管理コンソールを使うことで、基本的な自動化されたアラートを設定すると、個々のメトリックの最近の変化を可視化することができまし。


### Graphs

> Once you are signed in to your AWS account, you can open the [CloudWatch console](https://console.aws.amazon.com/cloudwatch/home#metrics:) and then browse the metrics related to the different AWS services.

AWSアカウントにサインインしたら、[CloudWatchコンソール](https://console.aws.amazon.com/cloudwatch/home#metrics:)を表示すると、各サービスに関連するメトリクスを閲覧することができます。


[![ELB metrics in AWS Console](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-01.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-01.png)

> By clicking on the ELB Metrics category, you will see the list of available metrics per load balancer, per availability zone:

ELBメトリクスのカテゴリをクリックすると、アベイラビリティゾーン毎にリスト化されたロードバランサー毎に監視しているメトリクスのリストが表示されます:


[![List of ELB metrics in AWS Console](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-02.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-02.png)

> You can also view the metrics across all your load balancers:

又、特定メトリクスという切り口で、全てのロードバランサーを横断的に表示することもできます。

[![List of ELB metrics across all load balancers](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-03.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-03.png)

> Just select the checkbox next to the metrics you want to visualize, and they will appear in the graph at the bottom of the console:

可視化したいメトリクスの横のチェックボックスを選択すると、そのメトリクスは、コンソールの下部にあるグラフに表示されます。


[![ELB metrics graphs in AWS Console](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-04.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-04.png)

### Alerts

> With the CloudWatch Management Console, you can also create simple alerts that trigger when a metric crosses a specified threshold.

CloudWatchの管理コンソールを使用すると、ELBメトリクスが予め設定している閾値を超えた時に発報するシンプルなアラートを作ることができます。


> Click on the “Create Alarm” button at the right of your graph, and you will be able to set up the alert and configure it to notify a list of email addresses:

グラフの右側にある“Create Alarm”ボタンをクリックすると、閾値を指定し、リストで指定した電子メールアドレスに通知を送信するアラートが設定できます:


[![ELB alerts in AWS Console](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-05.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-05.png)

## Using the AWS Command Line Interface

> You can also retrieve metrics related to a load balancer from the command line. To do so, you will need to install the AWS Command Line Interface (CLI) by following [these instructions](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html). You will then be able to query for any CloudWatch metric, using different filters.

コマンドラインからロードバランサーに関連するメトリックを取得することもできます。これを行うには、[次の手順に従って](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html)、AWS Command Line Interface (CLI) をインストール必要があります。インストールが完了すれば、異なるコマンドオプションを使って、CloudWatchのメトリックを参照することができるようになります。


> Command line queries can be useful for spot checks and ad hoc investigations when you can’t, or don’t want to, use a browser.

コマンドラインからの問い合わせは、スポットチェックや臨時の調査が発生した場合で、ブラウザーが使えない又は使いたくない場合に、非常に便利です。


> > For example, if you want to know the health state of all the backend instances registered to a load balancer, you can run:

例えば、ロードバランサに登録されているすべてのバックエンドインスタンスの状態を知りたい場合、次のコマンドを実行します。


`aws elb describe-instance-health --load-balancer-name my-load-balancer`

> That command should return a JSON output of this form:

上記のコマンドは、JSON形式の結果を出力します：


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

> [Here](http://docs.aws.amazon.com/cli/latest/reference/elb/index.html) are all the ELB commands you can run with the CLI.

ELBで使用するとができる[CLIコマンドの一覧](http://docs.aws.amazon.com/cli/latest/reference/elb/index.html)です。


## Monitoring tool integrated with CloudWatch

> The third way to collect CloudWatch metrics is via your own monitoring tools, which can offer extended monitoring functionality.

CloudWatchメトリックを収集する第三の方法は、総合的な監視機能を教授することができる、独自の監視ツールを使用する方法です。


> You probably need a dedicated monitoring system if, for example, you want to:
> - Correlate metrics from one part of your infrastructure with others (including custom infrastructure or applications)
> - Dynamically slice, aggregate, and filter your metrics on any attribute
> - Access historical data
> - Set up sophisticated alerting mechanisms

例えば、以下のような目的を達成したい場合は、専用の監視システムが必要になるでしょう:
- インフラ一部のメトリクスとそれ以外の部分のメトリクスを相関して状況を把握したい。(専用インフラ部品やアプリを含む)
- 動的にアトリビュートの基づいて、分類、集約、フィルタリングしたい。
- 種修したメトリクスを過去に遡って参照したい。
- 洗練された警告メカニズムを設定したい。


> CloudWatch can be integrated with outside monitoring systems via API, and in many cases the integration just needs to be enabled to start working.

CloudWatchは、APIを介して外部監視システムと連携すうことができます。多くの場合、連携に使う仕組みは、外部監視システムでその機能を有効にし、動作させるだけです。


> > As explained in [Part 1](https://www.datadoghq.com/blog/top-elb-health-and-performance-metrics), CloudWatch’s ELB-related metrics give you great insight about your load balancers’ health and performance. However, for more precision and granularity on your backend instances’ performance, you should consider monitoring their resources directly. Correlating native metrics from your EC2 instances with ELB metrics will give you a fuller, more precise picture. In [Part 3](https://www.datadoghq.com/blog/monitor-elb-performance-with-datadog), we cover a concrete example of this type of metrics collection and detail how to monitor ELB using Datadog.

[Part 1](https://www.datadoghq.com/blog/top-elb-health-and-performance-metrics)で紹介したように、CloudWatchから集取できるELB関連メトリクスを使えば、ロードバランサの状態とパフォーマンスについての深い洞察力を与ることができます。しかしながら、バックエンドインスタンスの、より高精細で高精度なパフォーマンス情報のためには、それらのリソースを直接監視することを検討刷る必要があります。EC2インスタンスから収集したネーティブのメトリクスをELBのメトリクスと相関することによって、より完結し、より精度の高い内容を把握出るようになります。[Part 3](https://www.datadoghq.com/blog/monitor-elb-performance-with-datadog)では、このタイプのメトリクス収集方法の例として、Datadogを使ったELBの監視について解説していきます。


## ELB Access Logs

> ELB access logs capture all the information about every request received by the load balancer, such as a time stamp, client IP address, path, backend response, latency, and so on. It can be useful to investigate the access logs for particular requests in case of issues.

ELBのアクセスログには、タイムスタンプ、クライアントのIPアドレス、リクエストパス、バックエンドの応答内容、レイテンシーなどのロードバランサーで受信した全リクエストの情報がキャプチャされています。特定のリクエストに関してアクセスログを調査することが、問題が発生した場合の有効に解決手段になることもあります。


### Configuring the access logs

> First you must enable the access logs feature, which is disabled by default. Logs are stored in an Amazon S3 bucket, which incurs additional storage costs.

まず最初に、デフォルトでは無効になっているアクセスログ機能を有効にします。ログは、Amazon S3のバケツに収納されます。そして、このログに保存には、Amazon S3のストレージ料金が発生します。


> Elastic Load Balancing creates [log files](http://docs.aws.amazon.com/ElasticLoadBalancing/latest/DeveloperGuide/access-log-collection.html#access-log-file-format) at user-defined intervals, between 5 and 60 minutes. Every single request received by ELB is logged, including those requests that couldn’t be processed by your backend instances (see [Part 1](https://www.datadoghq.com/blog/top-elb-health-and-performance-metrics) for the different root causes of ELB issues). You can see more details [here](http://docs.aws.amazon.com/ElasticLoadBalancing/latest/DeveloperGuide/access-log-collection.html#access-log-entry-format) about the log entry format and the different fields containing information about a request.

ELBは、ユーザーが定義した間隔(5〜60分の間)で、[ログファイル](http://docs.aws.amazon.com/ElasticLoadBalancing/latest/DeveloperGuide/access-log-collection.html#access-log-file-format)を生成していきます。ELBで受信した全てのリクエストは、ログに保存されます。このリクエストには、バックエンドインスタンスで、処理ができなかったものも含まれます(ELB障害の異なる根本原因に関しては、[Part 1](https://www.datadoghq.com/blog/top-elb-health-and-performance-metrics)を参照してください)。アクセスログのフォーマットとリクエストに含まれる情報とそのフィールドに関しては、この[リンク先](http://docs.aws.amazon.com/ElasticLoadBalancing/latest/DeveloperGuide/access-log-collection.html#access-log-entry-format)を参照してください。


### Analyzing logs

> ELB access logs can be useful when troubleshooting and investigating specific requests. However, if you want to find and analyze patterns in the overall access log files, you might want to use dedicated log analytics tools, especially if you are dealing with large amount of traffic generating heavy log file volume.

ELBアクセスログはトラブルシューティングや特定にリクエストに関する調査を実施している時のは非常に便利です。しかし、全てのアクセスログファイルを解析し、パターンを発見たいようなケースでは、専用のログ解析ツールを使った方た方が良いかもしれません。特に、膨大なトラフィックを扱い、大量のログファイルを生成している場合には、専用のログ解析ツールが必要です。


## Conclusion

> In this post we have walked through how to use CloudWatch to collect and visualize ELB metrics, how to generate alerts when these metrics go out of bounds, and how to use access logs for troubleshooting.

このポストでは、CloudWatchを使ってELBメトリックを収集し、視覚化する方法を解説しました。次に、メトリクスが閾値を超えた場合にアラートを発生させる方法について解説しました。最後に、アクセスログを使ったトラブルシューティングの方法も解説してきました。


> In the [next and final part on this series](https://www.datadoghq.com/blog/monitor-elb-performance-with-datadog) you will learn how you can monitor ELB metrics using the Datadog integration, along with native metrics from your backend instances for a complete view, with a minimum of setup.

この[シリーズの次で最後の部分](https://www.datadoghq.com/blog/monitor-elb-performance-with-datadog)では、監視のセットアップを最小限に抑えつつ、更にバックエンドインスタンスもネイティブなメトリクスして完全な状況把握を実現するための、Datadogのインテグレーションを使った、ELBメトリクスの方法を解説していきます。