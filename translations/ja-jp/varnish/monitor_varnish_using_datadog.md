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

Datadog Agentは、ホストからメトリクスを収集し、Datadog上で閲覧、監視出来るようにそれらのメトリクスを送信するための[オープンソースソフトウェア](https://github.com/DataDog/dd-agent)です。通常、Datadog Agentのインストールは、[一行のコマンド](https://app.datadoghq.com/account/settings#agent)を実行するだけです。

> As soon as the Datadog Agent is up and running, you should see your host reporting metrics [in your Datadog account](https://app.datadoghq.com/infrastructure).

Datadog Agentのインストールが終了し、稼働し始めると、[Datadogアカウントのインフラリスト](https://app.datadoghq.com/infrastructure)にホスト名が表示され、メトリクスを受信していることが確認できます。

![Varnish host reporting to Datadog](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-03bis.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-03bis.png)

### Configure the Agent

> Next you will need to create a Varnish configuration file for the Agent. You can find the location of the Agent configuration directory for your OS [here](http://docs.datadoghq.com/guides/basic_agent_usage/).

次は、Datadog Agentの設定に必要なVarnish設定ファイルを生成する必要があります。Datadog Agentの設定ファイルの、OS毎の設置ディレクトリは、[「Getting Started with the Agent」](http://docs.datadoghq.com/guides/basic_agent_usage/)ページで確認することができます。

In that directory you will find [a sample Varnish config file](https://github.com/DataDog/dd-agent/blob/master/conf.d/varnish.yaml.example) called `varnish.yaml.example`. Copy this file to `varnish.yaml`, then edit it to include the path to the varnishstat binary, and an optional list of tags that will be applied to every collected metric:

Datadog Agentの設定ファイルのあるディレクトリの中には、`conf.d/nginx.yaml.example`という[Varnishのメトリクスを収集するための設定サンプル](https://github.com/DataDog/dd-agent/blob/master/conf.d/varnish.yaml.example)のファイルが保存されています。このファイルを編集し、varnishstatバイナリへのパスを追加し、Datadog上でVarnishホストを検索したり集計するために使うタグを設定していきます:

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

次に、新しい設定ファイルを読み込むために、Datadog Agentを再起動します。Datadog Agentの再起動コマンドは、使っているOSより多少異なります。各OSの再起動コマンドに関しては、[「Getting Started with the Agent」](Getting Started with the Agent)ページを参照してください。

### Verify the configuration settings

> To check that Datadog and Varnish are properly integrated, execute the Datadog `info` command. The command for each platform is available [here](http://docs.datadoghq.com/guides/basic_agent_usage/).

Datadog AgentとVirnishの監視機能が適切に連携できているかを確認するには、Datadog Agentに内包されている`info`を実行します。各OSの`info`コマンドに関しては、[「Getting Started with the Agent」](http://docs.datadoghq.com/guides/basic_agent_usage/)ページを参照して下さい。

> If the configuration is correct, you will see a section like this in the `info` output:

設定が正しく終了している場合は、`info`コマンドの出力内に以下のようなセクションが表示されます:

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

最後に、Datadogにログインし、Virnish Integrationをオンにします。操作は、`Configuration`タブの配下にある[Varnish integration settings](https://app.datadoghq.com/account/settings#integrations/varnish)タイル内にある“Install Integration” ボタンをクリックするだけです。

[![Install Varnish integration with Datadog](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-04.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-04.png)

## Metrics!

> Once the Agent begins reporting Varnish metrics, you will see [a Varnish dashboard](https://app.datadoghq.com/dash/integration/varnish?live=true&page=0&is_auto=false&from_ts=1436268829917&to_ts=1436283229917&tile_size=m) among your list of available dashboards in Datadog.

Datadog AgentがVirnishのメトリクスをレポーティングし始めると、Datadog上のダッシュボード一覧に[Varnish dashboard](https://app.datadoghq.com/dash/integration/varnish?live=true&page=0&is_auto=false&from_ts=1436268829917&to_ts=1436283229917&tile_size=m)が表示されます。

> The basic Varnish dashboard displays the key metrics highlighted in our [introduction to Varnish monitoring](https://www.datadoghq.com/blog/how-to-monitor-varnish/).

Virnishの基本ダッシュボードには、Part 1の[「Virnishの監視方法」](https://www.datadoghq.com/blog/how-to-monitor-varnish/)で取り上げた重要メトリクスを、各種グラフ形式で表示しています。

[![Varnish dashboard on Datadog](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-05.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-05.png)

> You can easily create a more comprehensive dashboard to monitor your entire web stack by adding additional graphs and metrics from outside systems. For example, you might want to graph Varnish metrics alongside metrics from your Apache web servers, or alongside host-level metrics such as network traffic. To start building a custom dashboard, clone the default Varnish dashboard by clicking on the gear on the upper right of the dashboard and selecting “Clone Dash”.


ダッシュボードに、Virnishが依存する重要なシステム外メトリクスを元にしたグラフを追加することで、Web層を監視するための包括的なダッシュボードも簡単に作成することが出来ます。例えば、ネットワークなどのホストレベルのメトリクスやApache webサーバのメトリクスと、Virnishサーバのメトリクスを並べて状況を把握してみたいこともあるでしょう。カスタムダッシュボードを作り始めるには、Virnishの基本ダッシュボードの右上付近の歯車をクリックした後、“Clone Dash”をクリックし、基本ダッシュボードのコピーを作成します。

[![Clone Varnish dashboard](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-06.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-06.png)

## Alerting on Varnish metrics

> Once Datadog is capturing and visualizing your metrics, you will likely want to set up some [alerts](https://www.datadoghq.com/blog/monitoring-101-alerting/) to be automatically notified of potential issues.

Datadogで、Virnishのメトリクスを記録し、可視化できるようになったら、それらのメトリクスに”Monitors”(監視アラート)を設定し、自動で見張り、問題が発生した際には、[アラート](https://www.datadoghq.com/blog/monitoring-101-alerting/) 通知を受けられるようにしたいでしょう。

> Datadog can monitor individual hosts, containers, services, processes—or virtually any combination thereof. For instance, you can monitor all of your Varnish hosts, or all hosts in a certain availability zone, or a single key metric being reported by all hosts corresponding to a specific tag.

Datadogは個々のホスト、コンテナ、サービス、プロセスを、またはモニタその実質的に任意の組み合わせが出来ます。たとえば、特定のアベイラビリティゾーンであなたのVarnishのホスト、またはすべてのホストを監視することが出来、または単一の主要な指標は、特定のタグに対応するすべてのホストによって報告されています。

> Below we’ll walk through a representative example: an alert on Varnish’s dropped connections.

以下に代表的な事例として、Virnishの”dropped connections”値が急激に増加した際に、アラートを発生させる”Monitor”の設定手順を解説することにします。

### **Monitor Varnish’s dropped client connections**

> Datadog alerts can be threshold-based (alert when the metric exceeds a set value) or change-based (alert when the metric changes by a certain amount). In this case, we’ll take the first approach since we want to be alerted whenever the metric’s value is nonzero.

Datadogが提供するメトリクスアラート(メトリクスの数値を元に判定するアラート）には、閾値ベース(メトリクスが閾値を超えた場合に警告)と変化ベース(一定の量でメトリクスが変化した場合に警告)が有ります。今回のケースでは、メトリクスの値がゼロでない場合にアラートを発生させて欲しいので、閾値ベースのアラートを採用します。

> The `sess_dropped` metric counts client connections Varnish had to drop. There are several possible causes for dropped connections detailed in [part 1](https://www.datadoghq.com/blog/how-to-monitor-varnish/), but regardless this metric should always be equal to 0.

`sess_dropped`のメトリクスは、Varnishが処理しなかったクライアントコネクションを数えたものです。「part 1」で説明したように、コネクションの処理をしなかったのには幾つかの原因があります。原因はなんであれ、このメトリクスは、0である必要があります。

> 1.  **Create a new metric monitor**. Select “New Monitor” from the “Monitors” dropdown in Datadog. Select “Metric” as monitor type.[![Create Datadog alert](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-07.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-07.png)
> 2.  **Define your metric monitor**. We want to know when the number of dropped client connections per second exceeds a certain value. So we define the metric of interest to be the sum of `varnish.sess_dropped`.[![Monitor sess\_dropped](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-08.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-08.png)
> 3.  **Set metric alert conditions**. Since we want to alert on a fixed threshold, rather than on a change, we select “Threshold Alert.” We’ll set the monitor to alert us whenever Varnish starts dropping client connections. Here we alert whenever the metric has surpassed the threshold of zero at least once during the past minute. You should decide whether “greater than zero” is the right threshold for your organization, or whether some greater number of dropped connections is preferable to paging an engineer.[![Monitor sess\_dropped](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-09.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-09.png)
> 4.  **Customize the notification** to notify your team. In this case we will post a notification in the ops team’s chat room and page the engineer on call. In the “Say what’s happening” section we name the monitor and add a short message that will accompany the notification to suggest a first step for investigation. We @mention the [Slack](https://www.datadoghq.com/blog/collaborate-share-track-performance-slack-datadog/) channel that we use for ops and use @pagerduty to route the alert to [PagerDuty](https://www.datadoghq.com/blog/pagerduty/).[![Monitor sess\_dropped](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-10.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-07-varnish/3-10.png)
> 5.  **Save the integration monitor**. Click the “Save” button at the bottom of the page. You’re now monitoring a [key Varnish work metric](https://www.datadoghq.com/blog/how-to-monitor-varnish/), and your on-call engineer will be paged anytime Varnish drops client connections.

1. **新しいメトリクスモニタを作成します。** Datadogのダッシュボード上の“Monitors”タブのドロップダウンメニューから“New Monitor”を選択します。次に"Monitor"のタイプとして“Metric”を選択します。

2. **メトリクスモニタを定義します。** 1秒あたりの"dropped client connections"値が一定の数値を超えた場合、アラートを受けるようにします。そのような場合、`varnish.sess_dropped`のメトリクスをインフラ全体に渡り合算(sum)する設定をしておきます。

3. **メトリクスアラートの条件を設定します。** 変化ではなく、一定の閾値に基づいてアラートを発生させたいので、“Threshold  Alert”を選択します。Varnishが、クライアントコネクションを処理しなくなったら、アラートを報告する"Monitor"(アラート)を設定することにします。`varnish.sess_dropped`の値が、直近1分間に一度でもゼロ以外の数値になった場合、アラートすることにします。この閾値を設定する際に、組織として次の項目を是非検討してください。閾値を「ゼロ」のままにしておくか、それともエンジニアに対するページという観点から「ゼロより幾分か大きい値を設定する」かです。

4. **通知をカスタマイズします。** チームに通知する内容を設定していくことにします。このケースでは、運用チームのチャットルームと待機しているエンジニアに通知を送ることにします。 “Say what’s happening”のセクションで、"Monitor"のタイトルを設定し、調査を開始するために手がかりになる情報をメッセージに追記しておきます。ここでは、"@slack-ops"を使い運用チームの[Slack](https://www.datadoghq.com/blog/collaborate-share-track-performance-slack-datadog/)チャネルにメンションを送信し、"@pagerduty"を使って[PagerDuty](/blog/pagerduty/)にページ要請をしています。

5. **統合モニタを保存します。** ページの下部にある"Save"ボタンをクリックし、ここまでの内容を保存します。ここまでの作業で、Virnishの主要[ワークメトリクス]((/blog/monitoring-101-collecting-data/#metrics))の監視設定は完了し、待機中のエンジニアは、Virnishで"dropped client connections"が発生した際には、ページを受けるようになります。

## Conclusion

> In this post we’ve walked you through integrating Varnish with Datadog to visualize your key metrics and notify the right team whenever your web infrastructure shows signs of trouble.

このポストでは、VirnishをDatadogと連携し、重要なメトリクスを可視化し、Webインフラが問題の兆候を示した時にチームに通知する方法を解説してきました。

> If you’ve followed along using your own Datadog account, you should now have improved visibility into what’s happening in your web environment, as well as the ability to create automated alerts tailored to your infrastructure, your usage patterns, and the metrics that are most valuable to your organization.

Datadogのアカウントを使い、ここまで作業を進めてきたあなたは、Web層で何が起きているかを素早く把握できる監視を手に入れることができたでしょう。それと共に、あなたの環境、使用パターン、組織的に最も価値のあるメトリクスに合わせた"Monitors"(アラート)を設定する方法をも手に入れたでしょう。

> If you don’t yet have a Datadog account, you can sign up for a [free trial](http://app.datadoghq.com/signup) and start monitoring your infrastructure, your applications, and your services today.

もしもまだDatadogアカウントを持っていない場合は、[無料トライアル](https://app.datadoghq.com/signup) に登録することで、今日からすぐにインフラ、アプリケーション、サービスの監視を開始することができます。ます。

------------------------------------------------------------------------

> *Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/varnish/monitor_varnish_using_datadog.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues).*

*このポストのMarkdownソースは、[GitHub](https://github.com/DataDog/the-monitor/blob/master/varnish/monitor_varnish_using_datadog.m)で閲覧することができます。質問、訂正、追加、などがありましたら、[GitHubのissueページ](https://github.com/DataDog/the-monitor/issues)を使って連絡を頂けると幸いです。*
