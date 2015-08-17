# Monitor Varnish using Datadog

> *This post is part 3 of a 3-part series on Varnish monitoring. [Part 1](https://www.datadoghq.com/blog/how-to-monitor-varnish/) explores the key metrics available in Varnish, and [Part 2](https://www.datadoghq.com/blog/how-to-collect-varnish-metrics/) is about collecting those metrics on an ad-hoc basis.*

*このポストは、"Varnishの監視"3回シリーズのPart 2です。 Part 1は、[「Varnishの監視方法」」](https://www.datadoghq.com/blog/how-to-monitor-varnish/)で、Part 2は、Part 2は、[「Varnishのメトリクスの収集」](https://www.datadoghq.com/blog/how-to-collect-varnish-metrics/)になります。*

> In order to implement ongoing, meaningful monitoring, you will need a dedicated system that allows you to store all relevant Varnish metrics, visualize them, and correlate them with the rest of your infrastructure. You also need to be alerted when anomalies occur. In this post, we’ll show you how to start monitoring Varnish with Datadog.

発展的で価値がある監視を実現するためには、Varnishに関連する全てのメトリクスを保持し、可視化し、インフラの他のメトリクスと連携して分析できる専用システムが必要になります。更に、異常が発生した際には、アラートの発生も必要です。このポストでは、Datadogを使ってvarnishの監視を始める方法を紹介します。

![Varnish cache Datadog dashboard](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-01.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-01.png)

## Integrating Datadog and Varnish

### Verify that Varnish and varnishstat are working

> Before you begin, run this command to verify that Varnish is running properly:

作業を始める前に次のコマンドを実行し、
Varnishが正常に動作していることを確認します:

```
varnishstat -1  && echo -e "VarnishStat - OK" || \ || echo -e "VarnishStat - ERROR"
```

> Make sure the output displays “Varnishstat – OK”:

”Varnishstat - OK”が、表示されていることを確認します:

![Varnish running check](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-02.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-02.png)

### Install the Datadog Agent

> The Datadog Agent is [open-source software](https://github.com/DataDog/dd-agent) that collects and reports metrics from your different hosts so you can view, monitor and correlate them on the Datadog platform. Installing the Agent usually requires just a single command. Installation instructions for different systems are available [here](https://app.datadoghq.com/account/settings#agent).

Datadog Agentは、ホストからメトリクスを収集し、Datadog上で閲覧/監視できるようにそれらのメトリクスを送信するための[オープンソースソフトウェア](https://github.com/DataDog/dd-agent)です。通常、Datadog Agentのインストールは、[一行のコマンド](https://app.datadoghq.com/account/settings#agent)を実行するだけです。

> As soon as the Datadog Agent is up and running, you should see your host reporting metrics [in your Datadog account](https://app.datadoghq.com/infrastructure).

Datadog Agentのインストールが終了し、稼働し始めめると、[Datadogアカウントのインフラリスト](https://app.datadoghq.com/infrastructure)にホスト名が表示され、メトリクスを受信していることが確認できるはずです。

![Varnish host reporting to Datadog](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-03bis.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-03bis.png)

### Configure the Agent

> Next you will need to create a Varnish configuration file for the Agent. You can find the location of the Agent configuration directory for your OS [here](http://docs.datadoghq.com/guides/basic_agent_usage/).

次は、Datadog Agentの設定に必要なVarnish設定ファイルを生成する必要があります。Datadog Agentの設定ファイルの、OS毎の設置ディレクトリーは、[「Getting Started with the Agent」](http://docs.datadoghq.com/guides/basic_agent_usage/)ページで確認することができます。

In that directory you will find [a sample Varnish config file](https://github.com/DataDog/dd-agent/blob/master/conf.d/varnish.yaml.example) called `varnish.yaml.example`. Copy this file to `varnish.yaml`, then edit it to include the path to the varnishstat binary, and an optional list of tags that will be applied to every collected metric:

Datadog Agentの設定ファイルのあるディレクトリーの中には、`conf.d/nginx.yaml.example`という[Varnishのメトリクスを収集するための設定サンプル](https://github.com/DataDog/dd-agent/blob/master/conf.d/varnish.yaml.example)のファイルが保存されています。このファイルを編集し、


NGINXのステータスページのURLと、Datadog上でNGINXホストを検索したり集計するのに使うタグを設定していきます。

```
init_config:

instances:

    -   varnishstat: /usr/bin/varnishstat
        tags:
            -   instance:production
```

> Save and close the file.

保存し、ファイルを閉じます。

### Restart the Agent

> Next restart the Agent to load your new configuration. The restart command varies somewhat by platform; see the specific commands for your platform [here](http://docs.datadoghq.com/guides/basic_agent_usage/).

次に新しい設定をロードするようにエージェントを再起動します。 restartコマンドは、プラットフォームによって多少異なります。ここで使用しているプラットフォームの特定のコマンドを参照してください。

### Verify the configuration settings

> To check that Datadog and Varnish are properly integrated, execute the Datadog `info` command. The command for each platform is available [here](http://docs.datadoghq.com/guides/basic_agent_usage/).

Datadogとワニスが適切に統合されていることを確認するには、Datadog infoコマンドを実行します。各プラットフォーム用のコマンドがここにあります。

> If the configuration is correct, you will see a section like this in the `info` output:

設定が正しい場合は、`info`出力のこのようなセクションが表示されます。

```
Checks
======

  [...]

  varnish
  -----
      - instance #0 [OK]
      - Collected 8 metrics & 0 events
```


### Turn on the integration

> Finally, click the Varnish “Install Integration” button inside your Datadog account. The button is located under the Configuration tab in the [Varnish integration settings](https://app.datadoghq.com/account/settings#integrations/varnish).

最後に、ワニスをクリックしDatadogアカウント内側にボタン「統合をインストールしてください」。ボタンは、ワニスの統合設定の[設定]タブの下にあります。

[![Install Varnish integration with Datadog](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-04.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-04.png)

## Metrics!

> Once the Agent begins reporting Varnish metrics, you will see [a Varnish dashboard](https://app.datadoghq.com/dash/integration/varnish?live=true&page=0&is_auto=false&from_ts=1436268829917&to_ts=1436283229917&tile_size=m) among your list of available dashboards in Datadog.

エージェントはワニスのメトリックを報告し始めると、あなたはDatadogで使用可能なダッシュボードのリストのうち、ワニスのダッシュボードが表示されます。

> The basic Varnish dashboard displays the key metrics highlighted in our [introduction to Varnish monitoring](https://www.datadoghq.com/blog/how-to-monitor-varnish/).

基本的なニスのダッシュボードには、ワニスの監視に私たちの紹介でハイライト主要な指標が表示されます。

[![Varnish dashboard on Datadog](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-05.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-05.png)

> You can easily create a more comprehensive dashboard to monitor your entire web stack by adding additional graphs and metrics from outside systems. For example, you might want to graph Varnish metrics alongside metrics from your Apache web servers, or alongside host-level metrics such as network traffic. To start building a custom dashboard, clone the default Varnish dashboard by clicking on the gear on the upper right of the dashboard and selecting “Clone Dash”.

あなたは簡単に外部のシステムから追加のグラフやメトリックを追加することで、あなたの全体のウェブ·スタックを監視するためのより包括的なダッシュボードを作成することができます。たとえば、あなたは、ネットワークトラフィックなどのApacheのWebサーバー、または並んでホストレベルのメトリックからメトリックと一緒にワニスメトリックをグラフ化することができます。カスタムダッシュボードの構築を開始するには、ダッシュボードの右上の歯車をクリックして「クローンダッシュ」を選択すると、デフォルトワニスのダッシュボードのクローンを作成。

[![Clone Varnish dashboard](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-06.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-06.png)

## Alerting on Varnish metrics

> Once Datadog is capturing and visualizing your metrics, you will likely want to set up some [alerts](https://www.datadoghq.com/blog/monitoring-101-alerting/) to be automatically notified of potential issues.

Datadogをキャプチャし、あなたの評価指標を可視化されたら、自動的に潜在的な問題を通知するためにいくつかの警告を設定する可能性が高いでしょう。

> Datadog can monitor individual hosts, containers, services, processes—or virtually any combination thereof. For instance, you can monitor all of your Varnish hosts, or all hosts in a certain availability zone, or a single key metric being reported by all hosts corresponding to a specific tag.

Datadogは個々のホスト、コンテナ、サービス、プロセスを、またはモニターその実質的に任意の組み合わせができます。たとえば、特定のアベイラビリティゾーンであなたのワニスのホスト、またはすべてのホストのすべてを監視することができ、または単一の主要な指標は、特定のタグに対応するすべてのホストによって報告されています。

> Below we’ll walk through a representative example: an alert on Varnish’s dropped connections.

我々は代表的な例を歩くだろう下：ニスの上のアラートは、接続を落としました。

### **Monitor Varnish’s dropped client connections**

> Datadog alerts can be threshold-based (alert when the metric exceeds a set value) or change-based (alert when the metric changes by a certain amount). In this case, we’ll take the first approach since we want to be alerted whenever the metric’s value is nonzero.

Datadogアラートが（メトリックが設定値を超えた場合、警告）しきい値ベースにすることかできます変更ベース（アラート時に一定量測定基準の変更）。メトリックの値がゼロでないときはいつでも、我々は警告したいので、このケースでは、最初のアプローチを取りますよ。

> The `sess_dropped` metric counts client connections Varnish had to drop. There are several possible causes for dropped connections detailed in [part 1](https://www.datadoghq.com/blog/how-to-monitor-varnish/), but regardless this metric should always be equal to 0.

sess_droppedメトリックカウントのクライアント接続ワニスをドロップしなければなりませんでした。そこの部分1に詳述切断された接続のためのいくつかの原因がありますが、関係なく、このメトリックは、常に0に等しくなければなりません。

> 1.  **Create a new metric monitor**. Select “New Monitor” from the “Monitors” dropdown in Datadog. Select “Metric” as monitor type.[![Create Datadog alert](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-07.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-07.png)
> 2.  **Define your metric monitor**. We want to know when the number of dropped client connections per second exceeds a certain value. So we define the metric of interest to be the sum of `varnish.sess_dropped`.[![Monitor sess\_dropped](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-08.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-08.png)
> 3.  **Set metric alert conditions**. Since we want to alert on a fixed threshold, rather than on a change, we select “Threshold Alert.” We’ll set the monitor to alert us whenever Varnish starts dropping client connections. Here we alert whenever the metric has surpassed the threshold of zero at least once during the past minute. You should decide whether “greater than zero” is the right threshold for your organization, or whether some greater number of dropped connections is preferable to paging an engineer.[![Monitor sess\_dropped](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-09.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-09.png)
> 4.  **Customize the notification** to notify your team. In this case we will post a notification in the ops team’s chat room and page the engineer on call. In the “Say what’s happening” section we name the monitor and add a short message that will accompany the notification to suggest a first step for investigation. We @mention the [Slack](https://www.datadoghq.com/blog/collaborate-share-track-performance-slack-datadog/) channel that we use for ops and use @pagerduty to route the alert to [PagerDuty](https://www.datadoghq.com/blog/pagerduty/).[![Monitor sess\_dropped](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-10.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-10.png)
> 5.  **Save the integration monitor**. Click the “Save” button at the bottom of the page. You’re now monitoring a [key Varnish work metric](https://www.datadoghq.com/blog/how-to-monitor-varnish/), and your on-call engineer will be paged anytime Varnish drops client connections.

1. 新しいメトリック·モニターを作成します。 Datadogで「モニタ」ドロップダウンから「新規モニター」を選択します。モニターtype.Create Datadogアラートとして「メトリック」を選択します。

2. メトリック·モニターを定義します。我々は、毎秒ドロップクライアント接続の数が一定値を超えたときを知りたいです。だから我々はvarnish.sess_dropped.Monitor SESの \_droppedの合計になるように、目的のメトリックを定義します
メトリック·アラート条件を設定します。我々は固定閾値ではなく、変化に警告するようにしたいので、私たちは「しきい値アラート」を選択します。私たちはいつでも私たちに警告するようにモニターを設定します

3. ワニスは、クライアントの接続を切断を開始します。メトリックは、過去分の間に少なくとも一度ゼロのしきい値を超えたときはいつでもここに私達は警告します。あなたは「ゼロより大きいが「あなたの組織に最適な閾値である、または切断された接続のいくつかの大きな数は、SESのengineer.Monitor \_droppedをページングすることが好ましいかどうかを決定する必要があります

4. あなたのチームに通知するための通知をカスタマイズします。このケースでは、OPSチームのチャットルームとページ呼び出しのエンジニアで通知を掲載します。 「何が起こっているかを言う」セクションでは、モニターに名前を付け、調査のための最初の一歩を提案する通知を同行するショートメッセージを追加します。私たちは、OPSのために使用し、ルートアラートへの@pagerduty使用スラックチャネルを@mention

5. PagerDuty.Monitor SESの  \_dropped
統合モニタを保存します。ページの下部にある「保存」ボタンをクリックします。いつでもニスがクライアント接続をドロップするようになりましキーワニス作業メトリックを監視している、とあなたのオンコールエンジニアは、ページングされます。

## Conclusion

> In this post we’ve walked you through integrating Varnish with Datadog to visualize your key metrics and notify the right team whenever your web infrastructure shows signs of trouble.

この記事では、あなたの主要な指標を可視化し、Webインフラストラクチャがトラブルの兆候を示しているときはいつでも右のチームに通知するDatadogとニスを統合する手順を歩いてきました。

> If you’ve followed along using your own Datadog account, you should now have improved visibility into what’s happening in your web environment, as well as the ability to create automated alerts tailored to your infrastructure, your usage patterns, and the metrics that are most valuable to your organization.

あなたがあなた自身のDatadogアカウントを使用してに沿って続いてきた場合、あなたは今、あなたのウェブ環境だけでなく、インフラストラクチャに合わせた自動化されたアラートを作成する機能、あなたの使用パターンで何が起こっているかを可視化を向上させ、最もあるメトリクスている必要があります組織に貴重。

> If you don’t yet have a Datadog account, you can sign up for a [free trial](http://app.datadoghq.com/signup) and start monitoring your infrastructure, your applications, and your services today.

あなたはまだDatadogアカウントをお持ちでない場合は、無料試用版にサインアップすると、インフラストラクチャ、アプリケーション、およびサービスの今日の監視を開始することができます。

------------------------------------------------------------------------

> *Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/varnish/monitor_varnish_using_datadog.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues).*

*このポストのMarkdownソースは、[GitHub](https://github.com/DataDog/the-monitor/blob/master/nginx/how_to_collect_nginx_metrics.md)で閲覧することができます。質問、訂正、追加、などがありましたら、[GitHubのissueページ](https://github.com/DataDog/the-monitor/issues)を使って連絡を頂けると幸いです。*
