# How to monitor NGINX with Datadog

> *This post is part 3 of a 3-part series on NGINX monitoring. [Part 1](/blog/how-to-monitor-nginx/) explores the key metrics available in NGINX, and [Part 2](/blog/how-to-collect-nginx-metrics/) is about collecting those metrics.*

*このポストは、"NGINXの監視"3回シリーズのPart 1です。 Part 2は、[「NGINXのメトリクスの収集」][3]で、Part 3は、[「Datadogを使ったNGINXの監視」][4]になります。*

> If you’ve already read [our post on monitoring NGINX](/blog/how-to-monitor-nginx/), you know how much information you can gain about your web environment from just a handful of metrics. And you’ve also seen just how easy it is to start collecting metrics from NGINX on ad hoc basis. But to implement comprehensive, ongoing NGINX monitoring, you will need a robust monitoring system to store and visualize your metrics, and to alert you when anomalies happen. In this post, we’ll show you how to set up NGINX monitoring in Datadog so that you can view your metrics on customizable dashboards like this:

すでにnginxのを監視する上で私たちの記事を読んでいれば、あなたはメトリックのちょうど一握りのウェブ環境について得ることができますどのくらいの情報を知っています。そして、あなたはまた、アドホックベースでnginxのからのメトリックの収集を開始することで、どれだけ簡単に見てきました。しかし、総合的、継続的なnginxの監視を実現するためには、強固な監視システム格納し、あなたの評価指標を可視化し、異常が発生したときに警告するために必要になります。この記事では、我々はあなたがこのようなカスタマイズ可能なダッシュボード上のメトリックを表示することができるようにDatadogでnginxの監視を設定する方法を紹介します：

[![NGINX dashboard](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/nginx_board_5.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/nginx_board_5.png)

> Datadog allows you to build graphs and alerts around individual hosts, services, processes, metrics—or virtually any combination thereof. For instance, you can monitor all of your NGINX hosts, or all hosts in a certain availability zone, or you can monitor a single key metric being reported by all hosts with a certain tag. This post will show you how to:

> -   Monitor NGINX metrics on Datadog dashboards, alongside all your other systems
> -   Set up automated alerts to notify you when a key metric changes dramatically

Datadogを使用すると、個々のホスト、サービス、プロセス、メトリック、またはそれらの事実上の任意の組み合わせの周りのグラフとアラートを構築することができます。たとえば、特定のアベイラビリティゾーンであなたのnginxのホスト、またはすべてのホストのすべてを監視することも、一つのキーメトリックが特定のタグを持つすべてのホストによって報告されている監視することができます。この投稿は、どのようにあなたが表示されます：

- すべてのあなたの他のシステムと一緒にDatadogダッシュボード上のモニターnginxのメトリック、
- 劇的に主要な指標の変更を通知する自動警告を設定します

## Configuring NGINX

> To collect metrics from NGINX, you first need to ensure that NGINX has an enabled status module and a URL for reporting its status metrics. Step-by-step instructions [for configuring open-source NGINX](/blog/how-to-collect-nginx-metrics/#open-source) and [NGINX Plus](/blog/how-to-collect-nginx-metrics/#plus) are available in our companion post on metric collection.

nginxのからメトリックを収集するには、最初にnginxのが有効状態モジュールとその状態メトリックを報告するためのURLを持っていることを確認する必要があります。ステップバイステップのオープンソースのnginxとnginxのプラスを構成するための命令がメトリック収集の私達の仲間の記事でご利用いただけます。

## Integrating Datadog and NGINX

### Install the Datadog Agent

> The Datadog Agent is [the open-source software](https://github.com/DataDog/dd-agent) that collects and reports metrics from your hosts so that you can view and monitor them in Datadog. Installing the agent usually takes [just a single command](https://app.datadoghq.com/account/settings#agent).

Datadogエージェントが収集し、表示してDatadogでそれらを監視できるように、あなたのホストからのメトリックを報告し、オープンソースソフトウェアです。通常、エージェントをインストールするだけで、単一のコマンドで実行できます。

> As soon as your Agent is up and running, you should see your host reporting metrics [in your Datadog account](https://app.datadoghq.com/infrastructure).

とすぐにあなたのエージェントが稼働しているとして、あなたは、あなたのホストがDatadogアカウントのメトリックを報告するはずです。

[![Datadog infrastructure list](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/infra_2.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/infra_2.png)

### Configure the Agent

> Next you’ll need to create a simple NGINX configuration file for the Agent. The location of the Agent’s configuration directory for your OS can be found [here](http://docs.datadoghq.com/guides/basic_agent_usage/).

次は、エージェントの簡単なnginxの設定ファイルを作成する必要があります。お使いのOSのためのエージェントの設定ディレクトリの場所はここで見つけることができます。

> Inside that directory, at `conf.d/nginx.yaml.example`, you will find [a sample NGINX config file](https://github.com/DataDog/dd-agent/blob/master/conf.d/nginx.yaml.example) that you can edit to provide the status URL and optional tags for each of your NGINX instances:

そのディレクトリの中に、conf.d/ nginx.yaml.exampleで、あなたがあなたのnginxのinstancのそれぞれのステータスのURLとオプションのタグを提供するために編集できるサンプルnginxの設定ファイルを検索しま

```
init_config:

instances:

    -   nginx_status_url: http://localhost/nginx_status/
        tags:
            -   instance:foo
```

> Once you have supplied the status URLs and any tags, save the config file as `conf.d/nginx.yaml`.

あなたは、ステータスURLと任意のタグを供給したら、conf.d/ nginx.yamlとして設定ファイルを保存します。

### Restart the Agent

> You must restart the Agent to load your new configuration file. The restart command varies somewhat by platform—see the specific commands for your platform [here](http://docs.datadoghq.com/guides/basic_agent_usage/).

あなたは、新しい設定ファイルをロードするために、エージェントを再起動する必要があります。 restartコマンドにより多少異なりますここに使用しているプラットフォームの特定のコマンドを、プラットフォームを参照してください。

### Verify the configuration settings

> To check that Datadog and NGINX are properly integrated, run the Datadog `info` command. The command for each platform is available [here](http://docs.datadoghq.com/guides/basic_agent_usage/).

Datadogとnginxのが適切に統合されていることを確認するには、Datadog infoコマンドを実行します。各プラットフォーム用のコマンドがここにあります。

> If the configuration is correct, you will see a section like this in the output:

設定が正しい場合は、出力のこのようなセクションが表示されます。

```
Checks
======

  [...]

  nginx
  -----
      - instance #0 [OK]
      - Collected 8 metrics & 0 events
```

### Install the integration

> Finally, switch on the NGINX integration inside your Datadog account. It’s as simple as clicking the “Install Integration” button under the Configuration tab in the [NGINX integration settings](https://app.datadoghq.com/account/settings#integrations/nginx).

最後に、あなたのDatadogアカウント内のnginxの統合をオンにします。これは、nginxの連動の設定で[設定]タブの下で、「統合ソフトウェアのインストール」ボタンをクリックするだけで簡単です。

[![Install integration](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/install.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/install.png)

## Metrics!

> Once the Agent begins reporting NGINX metrics, you will see [an NGINX dashboard](https://app.datadoghq.com/dash/integration/nginx) among your list of available dashboards in Datadog.

エージェントはnginxのメトリックを報告し始めると、あなたはDatadogで使用可能なダッシュボードのリストのうち、nginxのダッシュボードが表示されます。

> The basic NGINX dashboard displays a handful of graphs encapsulating most of the key metrics highlighted [in our introduction to NGINX monitoring](/blog/how-to-monitor-nginx/). (Some metrics, notably request processing time, require log analysis and are not available in Datadog.)

基本的なnginxのダッシュボードは、nginxの監視に私たちの紹介で強調表示主要指標の大半をカプセル化グラフの一握りが表示されます。 （一部のメトリックは、特にログ解析必要としDatadogでは利用できない、処理時間を要求します。）

> You can easily create a comprehensive dashboard for monitoring your entire web stack by adding additional graphs with important metrics from outside NGINX. For example, you might want to monitor host-level metrics on your NGINX hosts, such as system load. To start building a custom dashboard, simply clone the default NGINX dashboard by clicking on the gear near the upper right of the dashboard and selecting “Clone Dash”.

あなたは簡単に外nginxのからの重要な測定基準で追加のグラフを追加することで、あなたの全体のウェブ·スタックを監視するための総合的なダッシュボードを作成することができます。たとえば、このようなシステム負荷としてのnginxのホスト上のホストレベルのメトリックを監視することができます。カスタムダッシュボードの構築を開始するには、ダッシュボードの右上付近の歯車をクリックして、「クローンダッシュ」を選択して、デフォルトのnginxのダッシュボードのクローンを作成。

[![Clone dash](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/clone_2.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/clone_2.png)

> You can also monitor your NGINX instances at a higher level using Datadog’s [Host Maps](/blog/introducing-host-maps-know-thy-infrastructure/)—for instance, color-coding all your NGINX hosts by CPU usage to identify potential hotspots.

また、マップ-のインスタンス、色分けCPU使用率により、すべてのnginxのホストが潜在的なホットスポットを特定するためにDatadogのホストを使用して、より高いレベルであなたのnginxのインスタンスを監視することができます。

[![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/nginx-host-map-3.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/nginx-host-map-3.png)

## Alerting on NGINX metrics

> Once Datadog is capturing and visualizing your metrics, you will likely want to set up some monitors to automatically keep tabs on your metrics—and to alert you when there are problems. Below we’ll walk through a representative example: a metric monitor that alerts on sudden drops in NGINX throughput.

Datadogをキャプチャし、あなたの評価指標を可視化されたら、自動的にあなたのメトリックとに問題があると警告を発するように、タブを保つためにいくつかのモニターを設定する可能性が高いでしょう。 nginxのスループットの急激な降下に警告メトリック·モニター：私たちは、代表的な例を歩きます下に。

### Monitor your NGINX throughput

> Datadog metric alerts can be threshold-based (alert when the metric exceeds a set value) or change-based (alert when the metric changes by a certain amount). In this case we’ll take the latter approach, alerting when our incoming requests per second drop precipitously. Such drops are often indicative of problems.

Datadogメトリック·アラートが（メトリックが設定値を超えた場合、警告）しきい値ベースにすることかできます変更ベース（アラート時に一定量測定基準の変更）。このケースでは、ときに、第2のドロップあたりの私たちの着信要求急激に警告する、後者のアプローチを取りますよ。このような液滴は、多くの場合、問題を示すものです。

> 1.  **Create a new metric monitor.** Select “New Monitor” from the “Monitors” dropdown in Datadog. Select “Metric” as the monitor type.
     [![NGINX metric monitor](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/monitor2_step_1.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/monitor2_step_1.png)
> 2.  **Define your metric monitor.** We want to know when our total NGINX requests per second drop by a certain amount. So we define the metric of interest to be the sum of `nginx.net.request_per_s` across our infrastructure.
     [![NGINX metric](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/monitor2_step_2.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/monitor2_step_2.png)
> 3.  **Set metric alert conditions.** Since we want to alert on a change, rather than on a fixed threshold, we select “Change Alert.” We’ll set the monitor to alert us whenever the request volume drops by 30 percent or more. Here we use a one-minute window of data to represent the metric’s value “now” and alert on the average change across that interval, as compared to the metric’s value 10 minutes prior.
     [![NGINX metric change alert](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/monitor2_step_3.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/monitor2_step_3.png)
> 4.  **Customize the notification.** If our NGINX request volume drops, we want to notify our team. In this case we will post a notification in the ops team’s chat room and page the engineer on call. In “Say what’s happening”, we name the monitor and add a short message that will accompany the notification to suggest a first step for investigation. We @mention the Slack channel that we use for ops and use @pagerduty to [route the alert to PagerDuty](/blog/pagerduty/).
     [![NGINX metric notification](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/monitor2_step_4v3.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/monitor2_step_4v3.png)
> 5.  **Save the integration monitor.** Click the “Save” button at the bottom of the page. You’re now monitoring a key NGINX [work metric](/blog/monitoring-101-collecting-data/#metrics), and your on-call engineer will be paged anytime it drops rapidly.

1. 新しいメトリック·モニターを作成します。 Datadogで「モニタ」ドロップダウンから「新規モニター」を選択します。モニターの種類として「メトリック」を選択します。 nginxのメトリック·モニター
2. あなたのメトリック·モニターを定義します。私たちが知りたいときに、特定の量によって、第2のドロップあたりの当社の総nginxの要求。だから我々は我々のインフラストラクチャ全体nginx.net.request_per_sの合計になるように、目的のメトリックを定義します。 nginxのメトリック
3. メトリック·アラート条件を設定します。私たちは変化のではなく、一定の閾値に警告するようにしたいので、私たちは「変更の警告」を選択します。我々は、要求量が30％以上低下するたびに私たちに警告するようにモニターを設定します。ここでは、10分前に、メトリックの値と比較して、その間隔全体の平均変化に、メトリックの "今"の値とアラートを表現するために、データの1分のウィンドウを使用します。 nginxのメトリック変更の警告
4. 通知をカスタマイズします。私たちのnginxの要求量が低下した場合、我々は我々のチームに通知します。このケースでは、OPSチームのチャットルームとページ呼び出しのエンジニアで通知を掲載します。 「何が起こっているかと言う "で、我々はモニターに名前を付け、調査のための最初の一歩を提案する通知を同行するショートメッセージを追加します。私たちは、OPSのために使用して、ルートにPagerDutyにアラートを@pagerduty使用スラックチャネルを@mention。 nginxのメトリック通知
5. 統合モニタを保存します。ページの下部にある「保存」ボタンをクリックします。これで、キーnginxの作業メトリックを監視している、とあなたのオンコールエンジニアは、それが急速に低下いつでもページングされます。


## Conclusion

> In this post we’ve walked you through integrating NGINX with Datadog to visualize your key metrics and notify your team when your web infrastructure shows signs of trouble.

この記事では、あなたの主要な指標を可視化し、Webインフラストラクチャがトラブルの兆候を示しているときにあなたのチームに通知するDatadogとnginxのを統合する手順を歩いてきました。

> If you’ve followed along using your own Datadog account, you should now have greatly improved visibility into what’s happening in your web environment, as well as the ability to create automated monitors tailored to your environment, your usage patterns, and the metrics that are most valuable to your organization.

あなたがあなた自身のDatadogアカウントを使用してに沿って続いてきた場合は、ここで大幅に改善されたウェブ環境で何が起こっているかを可視化、ならびに自動化されたユーザーの環境に合わせたモニター、あなたの使用パターン、およびあるメトリックを作成する能力を持っている必要があります組織にとって最も価値のあります。

> If you don’t yet have a Datadog account, you can sign up for [a free trial](https://app.datadoghq.com/signup) and start monitoring your infrastructure, your applications, and your services today.

あなたはまだDatadogアカウントをお持ちでない場合は、無料試用版にサインアップすると、インフラストラクチャ、アプリケーション、およびサービスの今日の監視を開始することができます。

------------------------------------------------------------------------

> *Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/nginx/how_to_monitor_nginx_with_datadog.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues).*

*この記事のソース·値引きはGitHubの上で利用可能です。ご質問、訂正、追加、など？私たちに知らせてください。*
