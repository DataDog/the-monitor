# How to collect Azure metrics

> *This post is part 2 of a 3-part series on monitoring Azure virtual machines. [Part 1](/blog/how-to-monitor-microsoft-azure-vms) explores the key metrics available in Azure, and [Part 3](/blog/monitor-azure-vms-using-datadog) details how to monitor Azure with Datadog.*

*このポストは、"Varnishの監視"3回シリーズのPart 1です。 Part 2は、[「Azureのメトリクスの収集」](/blog/how-to-collect-azure-metrics)で、Part 3は、[「Datadogを使ったAzuzreの監視」](/blog/monitor-azure-vms-using-datadog)になります。*

> How you go about capturing and monitoring Azure metrics depends on your use case and the scale of your infrastructure. There are several ways to access metrics from Azure VMs: you can graph and monitor metrics using the Azure web portal, you can access the raw metric data via Azure storage, or you can use a monitoring service that integrates directly with Azure to gather metrics from your VMs. This post addresses the first two options (using the Azure web portal and accessing raw data); a companion post describes how to monitor your VMs by integrating Azure with Datadog.

どのようにキャプチャし、Azureのメトリックを監視するについて行くには、ユースケースと、インフラストラクチャの規模に依存します。 Azureの仮想マシンからメトリックにアクセスするには、いくつかの方法があります：あなたがグラフ化できるとAzureのWebポータルを使用してモニター·メトリックは、あなたがAzureストレージを介して生メトリックデータにアクセスすることができる、またはあなたからメトリックを収集するためにアズールと直接統合監視サービスを使用することができますあなたのVM。この投稿は、最初の2つのオプション（アズールWebポータルを使用して、生データへのアクセスを）アドレス。コンパニオンポストはDatadogでアズールを統合することにより、あなたのVMを監視する方法について説明します。

## Viewing metrics in the Azure web portal

> The [Azure web portal](https://portal.azure.com/) has built-in monitoring functionality for viewing and alerting on performance metrics. You can graph any of the metrics available in Azure and set simple alert rules to send email notifications when metrics exceed minimum or maximum thresholds.

AzureのWebポータルに組み込まれた監視機能の表示およびパフォーマンス·メトリックに警告します。あなたはアズールで使用可能なメトリックのいずれかをグラフ化し、メトリックが最小または最大のしきい値を超えた場合に電子メール通知を送信するために、単純なアラートルールを設定することができま

### Enabling Azure VM monitoring

> Azure’s Diagnostics extension can be enabled when you create a new virtual machine via the Azure web portal. But even if you disabled Diagnostics when creating a VM, you can turn it on later from the “Settings” menu in the VM view. You can select which metrics you wish to collect (Basic metrics, Network and web metrics, .NET metrics, etc.) in the Diagnostics tile as well. You will have to link the VM to an Azure storage account to store your Diagnostics data.

> Note that portal users can create VMs using two different deployment models (“Classic” and “Resource Manager”). At present, some monitoring functionality is only available via the Classic deployment model.

あなたはAzureのWebポータルを介して、新しい仮想マシンを作成するときのAzureの診断拡張が有効にすることができます。 VMを作成するときでさえ、あなた無効診断場合は、VMビューで「設定」メニューから、後でそれをオンにすることができます。あなたは同様に診断タイルに（基本メトリクス、ネットワークとウェブメトリクス、.NETメトリックなど）を収集したいメトリックを選択することができます。あなたは、あなたの診断データを格納するためのAzureストレージアカウントにVMをリンクする必要があります。

ポータルユーザが仮想マシンは、2つの異なる展開モデル（「クラシック」と「リソース·マネージャ」）を使用して作成できることに注意してください。現時点では、いくつかの監視機能は、クラシック展開モデルを介してのみ使用可能です。

[![Enable Azure diagnostics](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/2-enable-diagnostics-2.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/2-enable-diagnostics-2.png)

> Once monitoring is enabled, you will see several default metric graphs when you click on your VM in the Azure portal.

監視を有効にすると、あなたがAzureのポータルにあなたのVMをクリックしたときに、あなたは、いくつかのデフォルトのメトリックのグラフが表示されます。

![Default graphs](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/2-default-graphs.png)

> Clicking on any monitoring graph opens a larger view, along with two important settings options: “Edit chart,” which allows you to select the metrics and the timeframe displayed on that graph, and “Add alert,” which opens the Azure alerting tile.

Azureの警告タイルを開く」警告を追加、「あなたはメトリックとそのグラフ上に表示された時間枠を選択することを可能にする「編集·チャート」、および：任意の監視グラフをクリックすると、二つの重要な設定オプションと一緒に、より大きなビューが開きます。

![Metric graphs](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/2-bigger-graph.png)

> In the alerting tile you can set alerts on Azure VM metrics. Azure alerts can be set against any upper or lower threshold and will alert whenever the selected metric exceeds (or falls below) that threshold for a set amount of time. In the example below, we have set an alert that will notify us by email whenever the CPU usage on the given virtual machine exceeds 90 percent over a 10-minute interval.

警告タイルでは、AzureのVMのメトリクスにアラートを設定することができます。 Azureのアラートは、任意の上限または下限のしきい値に対して設定することができ、選択されたメトリックは、設定した時間のためにそのしきい値を超える（または下回る）たびに警告が表示されます。以下の例では、特定の仮想マシンのCPU使用率が10分間隔で90パーセントを超えた場合、電子メールで私たちに通知するアラートを設定しています。

[![Create alert](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/2-alert-rule.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/2-alert-rule.png)

## Accessing raw metric data in Azure storage

> Because Azure metrics are written to storage tables, you can access the raw data from Azure if you want to use external tools to graph or analyze your metrics. This post focuses on accessing metrics via Microsoft’s Visual Studio IDE, but you can also copy metric data tables to local storage using the [AzCopy utility](https://azure.microsoft.com/en-us/documentation/articles/storage-use-azcopy/) for Windows, or you can access metric data programmatically [using the .NET SDK](https://www.nuget.org/packages/Microsoft.Azure.Insights). Note that the [Azure command-line interface](https://azure.microsoft.com/en-us/documentation/articles/virtual-machines-command-line-tools/), which is available for Mac, Linux, and Windows, will allow you to view the list of tables in your storage accounts (via the `azure storage table list` command) but not the actual contents of those tables.

Azureのメトリックを記憶表に書かれているので、あなたがグラフやあなたのメトリックを分析するために外部ツールを使用したい場合は、Azureのからの生データにアクセスすることができます。この投稿は、MicrosoftのVisual StudioのIDEを介してメトリックにアクセスするに焦点を当てていますが、WindowsのAzCopyユーティリティを使用して、ローカルストレージにメトリックデータテーブルをコピーすることができ、または、プログラムで.NET SDKを使用して、メトリックデータにアクセスすることができます。マック、Linux、およびWindowsで利用可能ですAzureのコマンドラインインターフェイスは、あなたが（Azureストレージテーブルlistコマンドを介して）、ストレージアカウント内のテーブルのリストを表示できるようになりますので注意してくださいが、それらのテーブルのない実際の内容。

### Connecting to Azure in Visual Studio Cloud Explorer

> Starting with Visual Studio 2015 and Azure SDK 2.7, you can now use Visual Studio’s [Cloud Explorer](https://msdn.microsoft.com/en-us/library/azure/mt185741.aspx) to view and manage your Azure resources. (Similar functionality is available using [Server Explorer](https://msdn.microsoft.com/en-us/library/azure/ff683677.aspx#BK_ViewResources) in older versions of Visual Studio, but not all Azure resources may be accessible.)

Visual Studioの2015年のAzure SDK2.7以降では、今、あなたのAzureのリソースを表示および管理するために、Visual StudioのクラウドExplorerを使用することができます。 （同様の機能は、Visual Studioの旧バージョンでサーバーエクスプローラを使用して利用可能ですが、すべてではないのAzureのリソースにアクセスできる可能性はあります。）

> To view the Cloud Explorer interface in Visual Studio 2015, go to View &gt; Other Windows &gt; Cloud Explorer.

Visual Studioの2015年のクラウドエクスプローラインターフェイスを表示するには、>他のWindows>クラウドエクスプローラを表示するために行きます。

[![Cloud Explorer](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/2-cloud-explorer.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/2-cloud-explorer.png)

> Connect to your Azure account with Cloud Explorer by clicking on the gear and entering your account credentials.

ギアをクリックして、アカウントの資格情報を入力することで、クラウドエクスプローラを使用してAzureのアカウントに接続します。

![Add Azure account to Visual Studio](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/2-add-account.png)

### View stored metrics

> Once you have signed in to your Azure subscription, you will find your metric storage listed under “Storage Accounts” or “Storage Accounts (Classic),” depending on whether the storage account was launched on Azure’s Resource Manager stack or on the Classic Stack.

> Metrics are stored in tables, the names of which usually start with “WADMetrics.” Open up a metric table in one of your metric storage accounts, and you will see your VM metrics. Each table contains 10 days worth of data to prevent any one table from growing too large; the date is appended to the end of the table name.

あなたはAzureのサブスクリプションにサインインしたら、ストレージアカウントがアズールのリソースマネージャスタックまたはクラシックスタック上で起動されたかどうかに応じて"、ストレージアカウント（クラシック）「あなたのメトリック記憶は「ストレージアカウント」または下にリストされているでしょう。

メトリックは、テーブルに格納されている、の名前は通常、「。WADMetrics"で始まるあなたのメトリック記憶アカウントのいずれかにメトリック表を開き、あなたのVMのメトリクスが表示されます。各テーブルには大きくなりすぎるからいずれかのテーブルを防ぐために、データの10日間分が含まれています。日付は、テーブル名の最後に追加されます。

![Azure metrics in storage](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/2-wad-metrics2.png)

### Using stored metrics

> The name of your VM can be found at the end of each row’s partition key, which is helpful for filtering metrics when multiple VMs share the same metric storage account. The metric type can be found in the CounterName column.

あなたのVMの名前が複数のVMが同じメトリックストレージアカウントを共有する場合、フィルタリングメトリクスのために有用であるそれぞれの行のパーティションキーの終わりにあります。メトリックタイプは、CounterName欄に記載されています。

[![Metrics in tables](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/2-metric-table.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/2-metric-table.png)

> To export your data for use in Excel or another analytics tool, click the “Export to CSV File” button on the toolbar just above your table.

Excelで使用するか、別の解析ツールのためにデータをエクスポートするには、ちょうどあなたのテーブルの上にあるツールバーのボタンを「CSVファイルにエクスポートファイル」をクリックします。

![Export metrics to CSV](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/2-export-to-csv.png)

## Conclusion

> In this post we have demonstrated how to use Azure’s built-in monitoring functionality to graph VM metrics and generate alerts when those metrics go out of bounds. We have also walked through the process of exporting raw metric data from Azure for custom analysis.

> At Datadog, we have integrated directly with Azure so that you can begin collecting and monitoring VM metrics with a minimum of setup. Learn how Datadog can help you to monitor Azure in the [next and final post](/blog/monitor-azure-vms-using-datadog/) of this series.

この記事では、これらのメトリックが範囲外に行くときにアラートをVMメトリックをグラフ化して生成するために、アズールの組み込みの監視機能を使用する方法を実証しました。また、カスタムの分析のためのAzureからの生メトリックデータをエクスポートするプロセスを歩いてきました。

あなたが収集して、セットアップを最小限に抑えてVMのメトリクスの監視を開始することができるようにDatadogで、我々はアズールと直接統合しています。 Datadogは、あなたがこのシリーズの次と最終後にAzureのを監視するのを助けることができる方法を学びます。

------------------------------------------------------------------------

> *Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/azure/how_to_collect_azure_metrics.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues).*

*このポストのMarkdownソースは、[GitHub](https://github.com/DataDog/the-monitor/blob/master/azure/how_to_collect_azure_metrics.md)で閲覧することができます。質問、訂正、追加、などがありましたら、[GitHubのissueページ](https://github.com/DataDog/the-monitor/issues)を使って連絡を頂けると幸いです。*
