# Monitor Azure VMs using Datadog

> *This post is part 3 of a 3-part series on monitoring Azure virtual machines. [Part 1](/blog/how-to-monitor-microsoft-azure-vms) explores the key metrics available in Azure, and [Part 2](/blog/how-to-collect-azure-metrics) is about collecting Azure VM metrics.*

*このポストは、"Varnishの監視"3回シリーズのPart 1です。 Part 2は、[「Azureのメトリクスの収集」](/blog/how-to-collect-azure-metrics)で、Part 3は、[「Datadogを使ったAzuzreの監視」](/blog/monitor-azure-vms-using-datadog)になります。*

> If you’ve already read [our post](/blog/how-to-collect-azure-metrics) on collecting Azure VM metrics, you’ve seen that you can view and alert on metrics from individual VMs using the Azure web portal. For a more dynamic, comprehensive view of your infrastructure, you can connect Azure to Datadog.

すでにAzureのVMのメトリクスを収集する上で私たちの記事を読んでいれば、あなたはAzureのWebポータルを使用して、個々のVMからの測定基準に表示して警告することができることを見てきました。インフラストラクチャをより動的に、包括的なビューでは、DatadogにAzureのを接続することができます。

## Why Datadog?

By integrating Datadog and Azure, you can collect and view metrics from across your infrastructure, correlate VM metrics with application-level metrics, and slice and dice your metrics using any combination of properties and custom tags. You can use the Datadog Agent to collect more metrics—and at higher resolution—than are available in the Azure portal. And with more than 100 supported integrations, you can route automated alerts to your team using third-party collaboration tools such as PagerDuty and Slack.

Datadogとアズールを統合することで、あなたが収集することができ、あなたのインフラストラクチャ全体から見るメトリック、アプリケーションレベルのメトリック、およびスライスを使用して、VMのメトリクスを関連付け、プロパティとカスタムタグの任意の組み合わせを使用してメトリックをサイコロ。あなたは、複数のメトリック·アンドでのより高い解像度よりもAzureのポータルで利用可能なを収集するためにDatadogエージェントを使用することができます。 100以上のサポートの統合で、あなたはPagerDutyとスラックなどのサードパーティのコラボレーションツールを使用して、あなたのチームにアラートをルート自動化することができます。

In this post we’ll show you how to get started.

開始する方法この記事で私たちはあなたを紹介します。

## How to integrate Datadog and Azure

[![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/3-azure-dash-2.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/3-azure-dash-2.png)

*Host map of Azure VMs by region*

> As with all hosts, you can install the Datadog Agent on an Azure VM (whether [Windows](https://app.datadoghq.com/account/settings#agent/windows) or [Linux](https://app.datadoghq.com/account/settings#agent/ubuntu)) using the command line or as part of your automated deployments. But Azure users can also integrate with Datadog using the Azure and Datadog web interfaces. There are two ways to set up the integration from your browser:

すべてのホストと同様に、コマンドラインまたはあなたの自動展開の一部としてを使用して、（WindowsまたはLinuxのいずれか）AzureのVM上Datadogエージェントをインストールすることができます。しかし、Azureのユーザーは、DatadogはアズールとDatadogウェブインタフェースを使用して統合することができます。ブラウザから統合を設定する方法は2つあります。

> 1.  Enable Datadog to collect metrics via the Azure API
> 2.  Install the Datadog Agent using the Azure web portal

1. AzureのAPIを使用してメトリックを収集するためにDatadogを有効にします
2. AzureのWebポータルを使用してDatadogエージェントをインストールします。

> Both options provide basic metrics about your Azure VMs with a minimum of overhead, but the two approaches each provide somewhat different metric sets, and hence can be complementary. In this post we’ll walk you through both options and explain the benefits of each.

両方のオプションは、オーバーヘッドを最小限に抑え、あなたのAzureの仮想マシンについての基本的なメトリックを提供していますが、それ故に多少異なるメトリックのセットを提供し、それぞれ2つのアプローチが相補的であり得ます。この記事では、両方のオプションを順を追ってし、各々の利点を説明します。

## Enable Datadog to collect Azure metrics

> The easiest way to start gathering metrics from Azure is to connect Datadog to Azure’s read-only monitoring API. You won’t need to install anything, and you’ll start seeing basic metrics from all your VMs right away.

アズールから収集メトリックを開始する最も簡単な方法は、アズールの読み取り専用モニタリングAPIにDatadogを接続することです。あなたは何もインストールする必要はありません、あなたはすぐにすべてのあなたのVMからの基本的な測定基準を見てから始めましょう。

> To authorize Datadog to collect metrics from your Azure VMs, simply click [this link](https://app.datadoghq.com/azure/landing) and follow the directions on the configuration pane under the heading “To start monitoring all your Azure Virtual Machines”.

DatadogがあなたAzureの仮想マシンからのメトリックを収集することを許可するには、このリンクをクリックし、「すべてのAzureの仮想マシンの監視を開始するには」の見出しの下に設定ペイン上の指示に従ってください。

[![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/3-config-2.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/3-config-2.png)

### View your Azure metrics

> Once you have successfully integrated Datadog with Azure, you will see [an Azure default screenboard](https://app.datadoghq.com/screen/integration/azure) on your list of [Integration Dashboards](https://app.datadoghq.com/dash/list). The basic Azure dashboard displays all of the key CPU, disk I/O, and network metrics highlighted in Part 1 of this series, “How to monitor Microsoft Azure VMs”.

あなたが正常にアズールでDatadogを統合したら、統合ダッシュボードのリストにAzureのデフォルトscreenboardが表示されます。基本Azureのダッシュボードが表示され、キーCPUの全てが、ディスクのI / O、およびネットワークのメトリックは、このシリーズ、「どのようにMicrosoftのAzureの仮想マシンを監視する」の第1部で強調しました。

[![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/azure-screenboard.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/azure-screenboard.png)

### Customize your Azure dashboards

> Once you are capturing Azure metrics in Datadog, you can build on the default screenboard by adding additional Azure VM metrics or even graphs and metrics from outside systems. To start building a custom screenboard, clone the default Azure dashboard by clicking on the gear on the upper right of the dashboard and selecting “Clone Dash”. You can also add VM metrics to any custom timeboard, which is an interactive Datadog dashboard displaying the evolution of multiple metrics across any timeframe.

あなたがDatadogにAzureのメトリックをキャプチャしたら、外部のシステムから追加AzureのVMのメトリクス、あるいはグラフやメトリックを追加することで、デフォルトのscreenboardに構築することができます。カスタムscreenboardの構築を開始するには、ダッシュボードの右上の歯車をクリックして「クローンダッシュ」を選択して、デフォルトのAzureのダッシュボードのクローンを作成。また、任意の時間枠全体で複数のメトリックの進化を表示するインタラクティブDatadogのダッシュボードで任意のカスタムtimeboardにVMメトリックを追加することができます。

[![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/3-clone-3.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/3-clone-3.png)

## Install the Datadog Agent on an Azure VM

> Installing the Datadog Agent lets you monitor additional server-level metrics from the host, as well as real-time metrics from the applications running on the VM. Agent metrics are collected at higher resolution than per-minute Azure portal metrics.

Datadogエージェントをインストールすると、仮想マシンで実行中のアプリケーションからの追加のホストからサーバ·レベルのメトリックだけでなく、リアルタイム·メトリックを監視できます。エージェントのメトリックは、毎分Azureのポータルメトリックよりも高い解像度で収集されています。

> Azure users can install the Datadog Agent as an Azure extension in seconds. (Note: At present, Azure extensions are only available for VMs launched running on the “Classic” service management stack.)

Azureのユーザーは、秒単位でAzureの拡張としてDatadogエージェントをインストールすることができます。 （注：現時点では、Azureの拡張は、仮想マシンに対してのみ利用可能である「クラシック」サービス管理スタック上で実行して開始しました。）

### Install the Agent from the Azure portal

> In the [Azure web portal](https://portal.azure.com/), click on the name of your VM to bring up the details of that VM. From the details pane, click the “Settings” gear and select “Extensions.”

AzureのWebポータルでは、そのVMの詳細を表示するためにあなたのVMの名前をクリックします。詳細ペインから、「設定」の歯車をクリックして選択し、「拡張機能」。

[![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/3-extensions.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/3-extensions.png)

> On the Extensions tile, click “Add” to select a new extension. From the list of extensions, select the Datadog Agent for your operating system.

拡張タイルで、新しい拡張機能を選択するには、「追加」をクリックします。拡張機能のリストから、ご使用のオペレーティング·システム用のDatadog Agent]を選択します。

 [![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/3-dd-agent.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/3-dd-agent.png)

> Click “Create” to add the extension.

拡張子を追加するには、「作成」をクリックしてください。

### Configure the Agent with your Datadog API key

> At this point you will need to provide your Datadog API key to connect the Agent to your Datadog account. You can find your API key via [this link](https://app.datadoghq.com/azure/landing/).

この時点で、あなたのDatadogアカウントにエージェントを接続するためにあなたのDatadog APIキーを提供する必要があります。あなたは、このリンクを介して、あなたのAPIキーを見つけることができます。

### Viewing your Azure VMs and metrics

> Once the Agent starts reporting metrics, you will see your Azure VMs appear as part of your monitored infrastructure in Datadog.

エージェントがメトリックを報告し始めると、あなたはAzureのVMはDatadogで監視対象のインフラストラクチャの一部として表示されるのを参照します。

[![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/3-hostmap.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/3-hostmap.png)

> Clicking on any VM allows you to view the integrations and metrics from that VM.

任意のVMをクリックすると、そのVMから統合およびメトリックを表示することができます。

### Agent metrics

Installing the Agent provides you with system metrics (such as `system.disk.in_use`) for each VM, as opposed to the Azure metrics (such as `azure.vm.memory_pages_per_sec`) collected via the Azure monitoring API as described above.

前述したようにAzureの監視APIを介して収集された（例えば、`azure.vm.memory_pages_per_sec`など）アズールメトリクスとは対照的に、エージェントをインストールすると、各VMの（例えば、system.disk.in_use``など）システム·メトリックを提供します。

The Agent can also collect application metrics so that you can correlate your application’s performance with the host-level metrics from your compute layer. The Agent monitors services running in an Azure VM, such as IIS and SQL Server, as well as non-Windows integrations such as MySQL, NGINX, and Cassandra.

あなたのコンピューティング層からホストレベルのメトリックを使用してアプリケーションのパフォーマンスを関連付けることができるように、エージェントは、アプリケーションのメトリックを収集することができます。例えば、IISとSQL Server、ならびにMySQLの、nginxの、およびカサンドラなど、Windows以外の統合などのAzureのVMで実行中のエージェントを監視サービス、。

 [![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/3-wmi.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/3-wmi.png)

## Conclusion

> In this post we’ve walked you through integrating Azure with Datadog so you can visualize and alert on your key metrics. You can also see which VMs are overutilized or underutilized and should be resized to improve performance or save costs.

この記事では、我々はあなたが視覚化し、あなたの主要なメトリックの警告できるようDatadogでアズールを統合する手順を歩いてきました。また、VMが過剰使用または活用されていないと、パフォーマンスを改善したり、コストを節約するようにサイズ変更されますされているかを確認することができます。

> Monitoring Azure with Datadog gives you critical visibility into what’s happening with your VMs and your Azure applications. You can easily create automated alerts on any metric across any group of VMs, with triggers tailored precisely to your infrastructure and your usage patterns.

Datadogでアズールを監視するあなたのVMとあなたAzureのアプリケーションで何が起こっているのかに重要な可視性を提供します。トリガーは、インフラストラクチャとあなたの使用パターンに正確に合わせを使えば、簡単に、仮想マシンの任意のグループ全体の任意のメトリックに自動化されたアラートを作成することができます。

> If you don’t yet have a Datadog account, you can sign up for a [free trial](https://app.datadoghq.com/signup) and start monitoring your cloud infrastructure, your applications, and your services today.

あなたはまだDatadogアカウントをお持ちでない場合は、無料試用版にサインアップして、クラウドインフラストラクチャ、アプリケーション、およびサービスの今日の監視を開始することができます。

------------------------------------------------------------------------

> *Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/azure/monitor_azure_vms_using_datadog.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues).*

*このポストのMarkdownソースは、[GitHub](https://github.com/DataDog/the-monitor/blob/master/azure/monitor_azure_vms_using_datadog.md)で閲覧することができます。質問、訂正、追加、などがありましたら、[GitHubのissueページ](https://github.com/DataDog/the-monitor/issues)を使って連絡を頂けると幸いです。*
