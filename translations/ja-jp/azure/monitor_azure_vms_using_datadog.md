# Monitor Azure VMs using Datadog

> *This post is part 3 of a 3-part series on monitoring Azure virtual machines. [Part 1](/blog/how-to-monitor-microsoft-azure-vms) explores the key metrics available in Azure, and [Part 2](/blog/how-to-collect-azure-metrics) is about collecting Azure VM metrics.*

*このポストは、"Azureの監視"3回シリーズのPart 3です。 Part 1は、[「Azureの監視方法」](/blog/how-to-monitor-microsoft-azure-vms)で、Part 2は、[「Azureのメトリクスの収集」](/blog/how-to-collect-azure-metrics)になります。*

> If you’ve already read [our post](/blog/how-to-collect-azure-metrics) on collecting Azure VM metrics, you’ve seen that you can view and alert on metrics from individual VMs using the Azure web portal. For a more dynamic, comprehensive view of your infrastructure, you can connect Azure to Datadog.

今回のシリーズのPart2 [「Azureの仮想マシンメトリクスの収集」](/blog/how-to-collect-azure-metrics)を読んでいれば、Azure web portalを使って各仮想マシンのメトリクスを、閲覧し、アラートを発生させることがきることを知っているはずです。今回のポストでは、あなたのインフラを、更に多面的、且つ広範囲にわたって把握をするためのAzureとDatadogの連携について解説することにします。

## Why Datadog?

> By integrating Datadog and Azure, you can collect and view metrics from across your infrastructure, correlate VM metrics with application-level metrics, and slice and dice your metrics using any combination of properties and custom tags. You can use the Datadog Agent to collect more metrics—and at higher resolution—than are available in the Azure portal. And with more than 100 supported integrations, you can route automated alerts to your team using third-party collaboration tools such as PagerDuty and Slack.

DatadogとAzureを連携することで、インフラ全体のメトリクスを収集し閲覧することができるようになります。更に、アプリケーションレベルのメトリクスを仮想マシンのメトリクスと関連付け、タグやプロパティーに基づいてメトリクスを分類して状況を把握することが出来るようになります。Datadog Agentを使うことによりAzure portalが提供している細かい粒度のメトリクスも収集出来るようになります。Datadogが公式に提供するIntegration(100種を超えている)を使うことで、サードパーティのコラボレーションツールを使用して自動的に検知したアラートをチームに届けることが出来るようになります。

> In this post we’ll show you how to get started.

このポストでは、これらの機能を実現していくために、Datadogをどのように設定していけばよいかを解説していきます。

## How to integrate Datadog and Azure

[![](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-08-azure/3-azure-dash-2.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-08-azure/3-azure-dash-2.png)

*Host map of Azure VMs by region*

> As with all hosts, you can install the Datadog Agent on an Azure VM (whether [Windows](https://app.datadoghq.com/account/settings#agent/windows) or [Linux](https://app.datadoghq.com/account/settings#agent/ubuntu)) using the command line or as part of your automated deployments. But Azure users can also integrate with Datadog using the Azure and Datadog web interfaces. There are two ways to set up the integration from your browser:

> 1.  Enable Datadog to collect metrics via the Azure API
> 2.  Install the Datadog Agent using the Azure web portal

他の一般的なホストと同じように、Azureの仮想マシン( [Windows](https://app.datadoghq.com/account/settings#agent/windows) 又は [Linux](https://app.datadoghq.com/account/settings#agent/ubuntu)のどちらでも)にも、コマンドラインを使うか、Chefなどの自動デプロイツールを使ってDatadog Agentをインストールすることができます。それ以外にもAzureのユーザーは、AzureとDatadogの両方のwebインターフェースを使って、Datadogとの連携をすることも出来ます。ブラウザからIntegrationを設定するには、以下の2つの方法があります:

1. AzureのAPIを使用してメトリクスを収集するようにDatadogを設定する方法
2. Azure Web Portalを使用してDatadog Agentをインストールるする方法

> Both options provide basic metrics about your Azure VMs with a minimum of overhead, but the two approaches each provide somewhat different metric sets, and hence can be complementary. In this post we’ll walk you through both options and explain the benefits of each.

どちらの方法でも、最小限のオーバーヘッドでAzure仮想マシンの基本的なメトリクスを提供してくれます。しかし、これら異なる二つのアプローチは、多少異なった組み合わせのメトリクスが提供されます。それ故に、これら二つのアプローチは、相補的に使われることが多いです。このポストでは、両方のアプローチの手順について紹介し、各々の利点を解説することにします。

## Enable Datadog to collect Azure metrics

> The easiest way to start gathering metrics from Azure is to connect Datadog to Azure’s read-only monitoring API. You won’t need to install anything, and you’ll start seeing basic metrics from all your VMs right away.

最も簡単にAzureからメトリクスを収集する方法は、Azureが提供する読み込み専用の監視APIにDatadogを接続することです。このアプローチでは、何もインストールする必要はなく、仮想マシンの基本的なメトリクスを直ちに閲覧できるようになります。

> To authorize Datadog to collect metrics from your Azure VMs, simply click [this link](https://app.datadoghq.com/azure/landing) and follow the directions on the configuration pane under the heading “To start monitoring all your Azure Virtual Machines”.

Azure 仮想マシンからのメトリクスの収集をDatadogに許可するためには、DatadogのIntegrationページ内の[Azureのタイル](https://app.datadoghq.com/azure/landing)をクリックし、“To start monitoring all your Azure Virtual Machines”と書かれている部分の設定ペインの手順に従って作業を進めていきます。

[![](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-08-azure/3-config-2.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-08-azure/3-config-2.png)

### View your Azure metrics

> Once you have successfully integrated Datadog with Azure, you will see [an Azure default screenboard](https://app.datadoghq.com/screen/integration/azure) on your list of [Integration Dashboards](https://app.datadoghq.com/dash/list). The basic Azure dashboard displays all of the key CPU, disk I/O, and network metrics highlighted in Part 1 of this series, “How to monitor Microsoft Azure VMs”.

AzureとDatadogの連携が完了すると、インストールが完了している各種IngtegrationのデフォルトScreenBoardが一覧表示される部分に、Azureのデフォルトダッシュボードが表示されるようになります。この基礎的なAzureのダッシュボードには、CPU、disk I/O, ネットワークに関する主要なメトリクスが表示されています。(シリーズ Part 1の[「Azureの監視方法」](/blog/how-to-monitor-microsoft-azure-vms)で紹介したメトリクス)

[![](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-08-azure/azure-screenboard.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-08-azure/azure-screenboard.png)

### Customize your Azure dashboards

> Once you are capturing Azure metrics in Datadog, you can build on the default screenboard by adding additional Azure VM metrics or even graphs and metrics from outside systems. To start building a custom screenboard, clone the default Azure dashboard by clicking on the gear on the upper right of the dashboard and selecting “Clone Dash”. You can also add VM metrics to any custom timeboard, which is an interactive Datadog dashboard displaying the evolution of multiple metrics across any timeframe.

AzureのメトリクスをDatadog上で表示できるようなったら、そのデフォルトのScreenBoardに、Azure上の他の仮想マシンのメトリクスや、外部のシステムで発生しているイベントやメトリクスを追加し、カスタムダッシュボードをつくることが出来ます。カスタムScreenBoardを作り始めるには、ダッシュボードの右上の歯車をクリックし、“Clone Dash”を選択してAzureのデフォルトダッシュボードのクローンを作成します。又、Azureの仮想マシンメトリクスをTimeBoardに追加してカスタムダッシュボードを作成することもできます。(TimeBoard: Datadogが提供する対話的ダッシュボード。任意の時間軸が選択でき、複数のメトリクスが自動的に更新され、指定したイベントの発生状態がグラフに合成常時されるダッシュボード。)

[![](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-08-azure/3-clone-3.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-08-azure/3-clone-3.png)

## Install the Datadog Agent on an Azure VM

> Installing the Datadog Agent lets you monitor additional server-level metrics from the host, as well as real-time metrics from the applications running on the VM. Agent metrics are collected at higher resolution than per-minute Azure portal metrics.

Datadog Agentをインストールすると、サーバレベルメトリクスが追加で監視できるようになるだけでなく、仮想マシン上で動作しているアプリケーションのメトリクスをリアルタイムで監視できるようになります。更に、Datatadog Agentが収集するメトリクスは、Azure portalが提供している1分毎のメトリクスよりも高い解像度で収集されます。

> Azure users can install the Datadog Agent as an Azure extension in seconds. (Note: At present, Azure extensions are only available for VMs launched running on the “Classic” service management stack.)

Azureのユーザは、Datadog AgentをAzure extentionとして短時間でインストールすることができます。(注: 現時点では、Azure extentionは、“Classic” service managementスタックで起動した仮想マシンについてのみ利用可能です。)

### Install the Agent from the Azure portal

> In the [Azure web portal](https://portal.azure.com/), click on the name of your VM to bring up the details of that VM. From the details pane, click the “Settings” gear and select “Extensions.”

[Azure web portal](https://portal.azure.com/)上で仮想マシンの名前をクリックし、詳細情報を表示させます。詳細情報のペインで、歯車マークの“Settings”をクリックし、“Extensions”を選択します。

[![](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-08-azure/3-extensions.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-08-azure/3-extensions.png)

> On the Extensions tile, click “Add” to select a new extension. From the list of extensions, select the Datadog Agent for your operating system.

新しいExtentionを追加するには、Extentionタイルが表示部分で、"+Add"をクリックします。次にExtentionのリストから、使っているOS用のDatadog Agentを選択します。

 [![](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-08-azure/3-dd-agent.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-08-azure/3-dd-agent.png)

> Click “Create” to add the extension.

“Create”をクリックし、Extentionを追加します。

### Configure the Agent with your Datadog API key

> At this point you will need to provide your Datadog API key to connect the Agent to your Datadog account. You can find your API key via [this link](https://app.datadoghq.com/azure/landing/).

この時点で、Datadog AgentがあなたのDatadogアカウントのメトリクスを送信できるように、Datadog API キーの情報を設定します。Datadog API キーの情報は、ダッシュボードの`Integration`タブをクリックし、[`APIs`](https://app.datadoghq.com/azure/landing/)を選択すると表示されます。

### Viewing your Azure VMs and metrics

> Once the Agent starts reporting metrics, you will see your Azure VMs appear as part of your monitored infrastructure in Datadog.

Datadog Agnetがメトリクスを送信し始めると、Datadogの`Infrastructure`タブ以下の各表示項目で、Azure上の仮想マシンを確認することができるようになります。(以下は、`Host Map`の事例です)

[![](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-08-azure/3-hostmap.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-08-azure/3-hostmap.png)

> Clicking on any VM allows you to view the integrations and metrics from that VM.

どれかの仮想マシンマークをクリックすると、その仮想マシンに関連するメトリクスとIntegrationが閲覧できるようになります。

### Agent metrics

> Installing the Agent provides you with system metrics (such as `system.disk.in_use`) for each VM, as opposed to the Azure metrics (such as `azure.vm.memory_pages_per_sec`) collected via the Azure monitoring API as described above.

Datadog Agentをインストールることで、上記で紹介したAzureの監視APIを介して収集したAzureメトリクス(例: `azure.vm.memory_pages_per_sec`) とは対照的に、各仮想マシンのシステムメトリクス(例: `system.disk.in_use`)を収集できるようになります。

> The Agent can also collect application metrics so that you can correlate your application’s performance with the host-level metrics from your compute layer. The Agent monitors services running in an Azure VM, such as IIS and SQL Server, as well as non-Windows integrations such as MySQL, NGINX, and Cassandra.

Datadog Agentは、アプリケーションのメトリクスを収集できるようになっています。そうすることで、計算用インスタンス達のホストレベルでのメトリクスと実行されているアプリケーションにパフォーマンスに関するメトリクスを関連付けて分析できるようになるからです。Datadog Agentは、Azureの仮想マシンで動作しているIIS、SQLサーバーなどのサービスに加え、MySQL、 NGINX、CassandraなどのWindowsではないサービスも監視することができます。

[![](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-08-azure/3-wmi.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-08-azure/3-wmi.png)

## Conclusion

> In this post we’ve walked you through integrating Azure with Datadog so you can visualize and alert on your key metrics. You can also see which VMs are overutilized or underutilized and should be resized to improve performance or save costs.

このポストでは、AzureからのメトリクスをDatadog側で可視化し、主要メトリクスに基づいてアラートを発生させるための連携の手順について解説してきました。又この連携で得たメトリクスを使って、コストの節約とパフォーマンスを向上するためのインスタンスサイズ変更をするための情報として、どの仮想マシンが過剰に使用され、どの仮想マシンが活用されていないかを判断できるようになったでしょう。

> Monitoring Azure with Datadog gives you critical visibility into what’s happening with your VMs and your Azure applications. You can easily create automated alerts on any metric across any group of VMs, with triggers tailored precisely to your infrastructure and your usage patterns.

Datadogを使ってAzureを監視することで、仮想マシンやアプリケーションで
発生している変化について貴重な情報を得られるようになります。又、グループに属する複数の仮想マシンを対照にしたメトリクスの集計を基に、インフラ構成と使用パターンにより適合した、自動アラートを簡単に設置することができるようになります。

> If you don’t yet have a Datadog account, you can sign up for a [free trial](https://app.datadoghq.com/signup) and start monitoring your cloud infrastructure, your applications, and your services today.

まだDatadogのアカウントを持っていないなら、無料トライアルに登録すれば、**今日から直ぐに**、クラウドインフラ、アプリケーション、およびサービスの監視を開始することができます。

------------------------------------------------------------------------

> *Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/azure/monitor_azure_vms_using_datadog.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues).*

*このポストのMarkdownソースは、[GitHub](https://github.com/DataDog/the-monitor/blob/master/azure/monitor_azure_vms_using_datadog.md)で閲覧することができます。質問、訂正、追加、などがありましたら、[GitHubのissueページ](https://github.com/DataDog/the-monitor/issues)を使って連絡を頂けると幸いです。*
