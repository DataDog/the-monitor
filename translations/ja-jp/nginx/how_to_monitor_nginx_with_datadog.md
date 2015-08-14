# How to monitor NGINX with Datadog

> *This post is part 3 of a 3-part series on NGINX monitoring. [Part 1](/blog/how-to-monitor-nginx/) explores the key metrics available in NGINX, and [Part 2](/blog/how-to-collect-nginx-metrics/) is about collecting those metrics.*

*このポストは、"NGINXの監視"3回シリーズのPart 3です。 Part 1は、[「NGINXの監視方法」](/blog/how-to-monitor-nginx/)で、Part 2は、[「NGINXのメトリクスの収集」](/blog/how-to-collect-nginx-metrics/)なります。*

> If you’ve already read [our post on monitoring NGINX](/blog/how-to-monitor-nginx/), you know how much information you can gain about your web environment from just a handful of metrics. And you’ve also seen just how easy it is to start collecting metrics from NGINX on ad hoc basis. But to implement comprehensive, ongoing NGINX monitoring, you will need a robust monitoring system to store and visualize your metrics, and to alert you when anomalies happen. In this post, we’ll show you how to set up NGINX monitoring in Datadog so that you can view your metrics on customizable dashboards like this:

このシリースのPart 1でポストした[「NGINXの監視方法」](/blog/how-to-monitor-nginx/)を既に読んでいれば、一握りのメトリクスからあなたのWEB環境についてどれくらいの情報が獲得できるか理解できていることでしょう。そして、場当たり的な閲覧のために、NGINXのメトリクスを収集することがどれほど簡単にできるのも理解できているでしょう。しかし、総合的かつ継続的な監視を実現するためには、収集したメトリクスを保持し、可視化し、異常が発生した際にアラートを通知してくれる強固な監視システムが必要になります。このポストでは、Datadogの下記のようなカスタマイズ可能なダッシュボード上でメトリクスが閲覧できるように、NGINXの監視に必要な設定手順を解説します:

[![NGINX dashboard](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/nginx_board_5.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/nginx_board_5.png)

> Datadog allows you to build graphs and alerts around individual hosts, services, processes, metrics—or virtually any combination thereof. For instance, you can monitor all of your NGINX hosts, or all hosts in a certain availability zone, or you can monitor a single key metric being reported by all hosts with a certain tag. This post will show you how to:

> -   Monitor NGINX metrics on Datadog dashboards, alongside all your other systems
> -   Set up automated alerts to notify you when a key metric changes dramatically

Datadogを使用すると、個々のホスト、個々のサービス、個々のプロセス、個々のメトリクス、または、それら全ての組み合わせに対しグラフとアラートを設定することが出来ます。例えば、全てのNGINXのホストを監視したり、特定のアベーラビリティーゾーンに属すホストを監視したり、また、特定のタグが付与されている全てのNIGINXホストの特定のメトリクスを監視することもできます。

このポストでは、以下を実現する方法を紹介します:

- Datadogのダッシュボード上で、システム内の他のメトリクスと並んでNGINXのメトリクスを表示し、監視する設定
- 重要なメトリクスが劇的に変化した際に、自動でアラートを発生させるめの設定

## Configuring NGINX

> To collect metrics from NGINX, you first need to ensure that NGINX has an enabled status module and a URL for reporting its status metrics. Step-by-step instructions [for configuring open-source NGINX](/blog/how-to-collect-nginx-metrics/#open-source) and [NGINX Plus](/blog/how-to-collect-nginx-metrics/#plus) are available in our companion post on metric collection.

NGINXからメトリクスを収集するには、まず最初にNIGINXのステータスモジュールを有効にし、ステータスメトリクスを開示するためのURLが有効になっているのか確認する必要があります。[オープンソース版NGINX](/blog/how-to-collect-nginx-metrics/#open-source)と[NIGINX Plus](/blog/how-to-collect-nginx-metrics/#plus) 向けのモジュール有効化手順書は、このシリーズのPart 2 [「NGINXのメトリクスの収集」](/blog/how-to-collect-nginx-metrics/)で、詳しく解説しています。

## Integrating Datadog and NGINX

### Install the Datadog Agent

> The Datadog Agent is [the open-source software](https://github.com/DataDog/dd-agent) that collects and reports metrics from your hosts so that you can view and monitor them in Datadog. Installing the agent usually takes [just a single command](https://app.datadoghq.com/account/settings#agent).

Datadog Agentは、ホストからメトリクスを収集し、Datadog上で閲覧、監視できるようにそれらのメトリクスを送信するための[オープンソースソフトウェア](https://github.com/DataDog/dd-agent)です。通常、Datadog Agentのインストールは、[一行のコマンド](https://app.datadoghq.com/account/settings#agent)を実行するだけです。

> As soon as your Agent is up and running, you should see your host reporting metrics [in your Datadog account](https://app.datadoghq.com/infrastructure).

Datadog Agentのインストールが稼働し始めると、Datadogのあなたのアカウント上にホスト名が表示され、メトリクスのレポーティングを受けていることが確認できます。

[![Datadog infrastructure list](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/infra_2.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/infra_2.png)

### Configure the Agent

> Next you’ll need to create a simple NGINX configuration file for the Agent. The location of the Agent’s configuration directory for your OS can be found [here](http://docs.datadoghq.com/guides/basic_agent_usage/).

次は、Datadog Agentの設定に必要なNGINX設定ファイルを生成する必要があります。Datadog Agentの設定ファイルの、OS毎の設置ディレクトリーは、[「Getting Started with the Agent」](Getting Started with the Agent)ページで確認することができます。

> Inside that directory, at `conf.d/nginx.yaml.example`, you will find [a sample NGINX config file](https://github.com/DataDog/dd-agent/blob/master/conf.d/nginx.yaml.example) that you can edit to provide the status URL and optional tags for each of your NGINX instances:

Datadog Agentの設定ファイルのあるディレクトリーの中には、`conf.d/nginx.yaml.example`という[NGINXのメトリクスを収集するための設定サンプル](https://github.com/DataDog/dd-agent/blob/master/conf.d/nginx.yaml.example)のファイルが保存されています。このファイルを編集し、　NGINXのステータスページのURLと、Datadog上でNGINXホストを検索したり集計するのに使うタグを設定していきます。

```
init_config:

instances:

    -   nginx_status_url: http://localhost/nginx_status/
        tags:
            -   instance:foo
```

> Once you have supplied the status URLs and any tags, save the config file as `conf.d/nginx.yaml`.

NGINXのステータスページのURLとタグの編集が終わったら、`conf.d/ nginx.yaml`として設定ファイルを保存します。

### Restart the Agent

> You must restart the Agent to load your new configuration file. The restart command varies somewhat by platform—see the specific commands for your platform [here](http://docs.datadoghq.com/guides/basic_agent_usage/).

新しい設定ファイルを読み込むために、Datadog Agentを再起動します。Datadog Agentの再起動コマンドは、使っているOSにより多少異なります。各OSの再起動コマンドに関しては、[「Getting Started with the Agent」](Getting Started with the Agent)ページを参照してください。

### Verify the configuration settings

> To check that Datadog and NGINX are properly integrated, run the Datadog `info` command. The command for each platform is available [here](http://docs.datadoghq.com/guides/basic_agent_usage/).

Datadog AgentとNGINXの監視機能が適切に連携できているかを確認するには、Datadog Agentに内包されている`info`を実行します。各OSの`info`コマンドに関しては、[「Getting Started with the Agent」](Getting Started with the Agent)ページを参照してください。

> If the configuration is correct, you will see a section like this in the output:

設定が正しく終了している場合は、`info`コマンドの出力内に以下のようなセクションが表示されます。

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

最後に、Datadogにログインし、NGINX Integrationをオンにします。操作は、`Configuration`タブの配下にある[NGINX Integration ](https://app.datadoghq.com/account/settings#integrations/nginx)タイル内にある“Install Integration” ボタンをクリックするだけです。

[![Install integration](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/install.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/install.png)

## Metrics!

> Once the Agent begins reporting NGINX metrics, you will see [an NGINX dashboard](https://app.datadoghq.com/dash/integration/nginx) among your list of available dashboards in Datadog.

Datadog AgentがNGINXのメトリクスをレポーティングし始めると、Datadog上のダッシュボード一覧に[NGINX dashboard](https://app.datadoghq.com/dash/integration/nginx)が表示されます。

> The basic NGINX dashboard displays a handful of graphs encapsulating most of the key metrics highlighted [in our introduction to NGINX monitoring](/blog/how-to-monitor-nginx/). (Some metrics, notably request processing time, require log analysis and are not available in Datadog.)

NGINXの基本ダッシュボードには、Part 1の[「NGINXの監視方法」](/blog/how-to-monitor-nginx/)で取り上げた重要メトリクスの大半を、各種のグラフ形式で表示しています。(`request processing time`のようなログ解析が必要なメトリクスは、Datadog単体では取り扱うことができません。ログ解析エンジンにplug-inをインストールし、Datadogの連携が必要になります。)

> You can easily create a comprehensive dashboard for monitoring your entire web stack by adding additional graphs with important metrics from outside NGINX. For example, you might want to monitor host-level metrics on your NGINX hosts, such as system load. To start building a custom dashboard, simply clone the default NGINX dashboard by clicking on the gear near the upper right of the dashboard and selecting “Clone Dash”.

NGINXが依存する外部の重要なメトリクスを元にしたグラフをダッシュボードに追加することで、Web層を監視するために包括的なダッシュボードも簡単に作成することができます。例えば、CPU負荷などのNGINXホストのホストレベルでのメトリクスも同時に監視したいと思うこともあるでしょう。カスタムダッシュボードを作り始めるには、NGINXの基本ダッシュボードの右上付近の歯車をクリックした後、“Clone Dash”をクリックし、基本ダッシュボードのコピーを作成します。

[![Clone dash](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/clone_2.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/clone_2.png)

> You can also monitor your NGINX instances at a higher level using Datadog’s [Host Maps](/blog/introducing-host-maps-know-thy-infrastructure/)—for instance, color-coding all your NGINX hosts by CPU usage to identify potential hotspots.

また、Datadogの[Host Maps](/blog/introducing-host-maps-know-thy-infrastructure/)を使うことで、NGINXホスト群の全体状況を監視することもできます。例えば、NGINXの各ホストをCPUの使用率により色分けすることで、高負荷になっている可能性があるホストを見つけ出すことができるようになります。

[![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/nginx-host-map-3.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/nginx-host-map-3.png)

## Alerting on NGINX metrics

> Once Datadog is capturing and visualizing your metrics, you will likely want to set up some monitors to automatically keep tabs on your metrics—and to alert you when there are problems. Below we’ll walk through a representative example: a metric monitor that alerts on sudden drops in NGINX throughput.

Datadogで、NGINXのメトリクスを記録し、可視化できるようになったら、それらのメトリクスに”Monitors”(監視アラート)を設定し、自動で見張り、問題が発生した際には、アラート通知受けられるようにしたいでしょう。以下に代表的な事例として、NGINXのスループットの急激な降下が発生した際にアラートを発生させる”Monitor”の設定手順を解説します。

### Monitor your NGINX throughput

> Datadog metric alerts can be threshold-based (alert when the metric exceeds a set value) or change-based (alert when the metric changes by a certain amount). In this case we’ll take the latter approach, alerting when our incoming requests per second drop precipitously. Such drops are often indicative of problems.

Datadogが提供するメトリクスアラート(メトリクスの数値を元に判定するアラート）には、閾値ベース(メトリクスが閾値を超えた場合に警告)と変化ベース(一定の量でメトリクスが変化した場合に警告)が有ります。今回のケースでは変化ベースのアプローチを取り、1秒あたりの着信リクエストが突然落ち込んだ際にアラートを発生するようにします。このようなリクエスト数の落ち込みは、多くの場合において障害の予兆を示すものです。

> 1.  **Create a new metric monitor.** Select “New Monitor” from the “Monitors” dropdown in Datadog. Select “Metric” as the monitor type.
     [![NGINX metric monitor](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/monitor2_step_1.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/monitor2_step_1.png)
> 2.  **Define your metric monitor.** We want to know when our total NGINX requests per second drop by a certain amount. So we define the metric of interest to be the sum of `nginx.net.request_per_s` across our infrastructure.
     [![NGINX metric](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/monitor2_step_2.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/monitor2_step_2.png)
> 3.  **Set metric alert conditions.** Since we want to alert on a change, rather than on a fixed threshold, we select “Change Alert.” We’ll set the monitor to alert us whenever the request volume drops by 30 percent or more. Here we use a one-minute window of data to represent the metric’s value “now” and alert on the average change across that interval, as compared to the metric’s value 10 minutes prior.
     [![NGINX metric change alert](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/monitor2_step_3.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/monitor2_step_3.png)
> 4.  **Customize the notification.** If our NGINX request volume drops, we want to notify our team. In this case we will post a notification in the ops team’s chat room and page the engineer on call. In “Say what’s happening”, we name the monitor and add a short message that will accompany the notification to suggest a first step for investigation. We @mention the Slack channel that we use for ops and use @pagerduty to [route the alert to PagerDuty](/blog/pagerduty/).
     [![NGINX metric notification](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/monitor2_step_4v3.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/monitor2_step_4v3.png)
> 5.  **Save the integration monitor.** Click the “Save” button at the bottom of the page. You’re now monitoring a key NGINX [work metric](/blog/monitoring-101-collecting-data/#metrics), and your on-call engineer will be paged anytime it drops rapidly.

1. **新しいメトリックスモニタを作成します。** Datadogのダッシュボード上の“Monitors”タブのドロップダウンメニューから“New Monitor”を選択します。次に"Monitor"のタイプとして“Metric”を選択します。
2. **メトリックスモニタを定義します。** NGINXが処理する1秒あたりのリクエスト総数が一定量落ち込んだ際に、通知を受けたいとします。まず`nginx.net.request_per_s`のメトリクスをインフラ全体に渡り合算(sum)する設定をしておきます。
3. **メトリックスアラートの条件を設定します。** 一定の閾値ではなく、変化に基づいてアラートを発生させたいので、“Change Alert”を選択します。次に、リクエスト量が30%以上の変化で落ち込んだ時にアラートを発生させるように設定します。ここでは、１分間のデータの平均値を現在のメトリクスの値とし、10分前に計測したメトリクスの値と比較し、その期間内のメトリクスの落ち込みが30％以上ある場合にアラートを発生させます。
4. **通知をカスタマイズします。** NGINXのリクエスト数が落ち込んだ際には、チームに通知することにします。このケースでは、運用チームのチャットルームと待機しているエンジニアに通知を送ることにします。 “Say what’s happening”のセクションで、"Monitor"のタイトルを設定し、調査を開始するための手がかりになる情報をメッセージに追記します。ここでは、"@slack-ops"を使い運用チームのSlackチャネルにメンションを送信し、"@pagerduty"を使って[PagerDuty](/blog/pagerduty/)にページ要請をしています。
5. **統合モニタを保存します。** ページの下部にある"Save"ボタンをクリックし、ここまでの内容を保存します。ここまでの作業で、NGINXの主要[ワークメトリクス]((/blog/monitoring-101-collecting-data/#metrics))の監視設定は完了し、待機中のエンジニアは、リクエスト数が急激に落ち込んだ際にはページを受けるようになります。

## Conclusion

> In this post we’ve walked you through integrating NGINX with Datadog to visualize your key metrics and notify your team when your web infrastructure shows signs of trouble.

このポストでは、NGINXをDatadogと連携し、重要なメトリクスを可視化し、Webインフラが問題の兆候を示した時にチームに通知する方法を解説してきました。

> If you’ve followed along using your own Datadog account, you should now have greatly improved visibility into what’s happening in your web environment, as well as the ability to create automated monitors tailored to your environment, your usage patterns, and the metrics that are most valuable to your organization.

Datadogのアカウントを使い、ここまで作業を進めてきたあなたは、大幅に改善された視認性をもつWeb環境を手に入れることができたでしょう。それと共に、あなたの環境、使用パターン、組織的に最も価値のあるメトリクスに合わせた"Monitors"(アラート)を設定する方法をも手に入れたでしょう。。

> If you don’t yet have a Datadog account, you can sign up for [a free trial](https://app.datadoghq.com/signup) and start monitoring your infrastructure, your applications, and your services today.

もしもまだDatadogアカウントを持っていない場合は、無料トライアルに登録することで、今日からすぐにインフラ、アプリケーション、サービスの監視を開始することができます。

------------------------------------------------------------------------

> *Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/nginx/how_to_monitor_nginx_with_datadog.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues).*

*このポストのMarkdownソースは、[GitHub](https://github.com/DataDog/the-monitor/blob/master/nginx/how_to_collect_nginx_metrics.md)で閲覧することができます。質問、訂正、追加、などがありましたら、[GitHubのissueページ](https://github.com/DataDog/the-monitor/issues)を使って連絡を頂けると幸いです。*
