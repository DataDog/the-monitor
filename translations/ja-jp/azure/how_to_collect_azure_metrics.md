# How to collect Azure metrics

> *This post is part 2 of a 3-part series on monitoring Azure virtual machines. [Part 1](/blog/how-to-monitor-microsoft-azure-vms) explores the key metrics available in Azure, and [Part 3](/blog/monitor-azure-vms-using-datadog) details how to monitor Azure with Datadog.*

*このポストは、"Varnishの監視"3回シリーズのPart 2です。 Part 1は、[「Azureの監視方法」](/blog/how-to-monitor-microsoft-azure-vms)で、Part 3は、[「Datadogを使ったAzuzre仮想マシンの監視」](/blog/monitor-azure-vms-using-datadog)になります。*

> How you go about capturing and monitoring Azure metrics depends on your use case and the scale of your infrastructure. There are several ways to access metrics from Azure VMs: you can graph and monitor metrics using the Azure web portal, you can access the raw metric data via Azure storage, or you can use a monitoring service that integrates directly with Azure to gather metrics from your VMs. This post addresses the first two options (using the Azure web portal and accessing raw data); a companion post describes how to monitor your VMs by integrating Azure with Datadog.

Azureのメトリクスをどのように収集して監視するかは、あなたのユースケースとインフラの規模に依存します。Azureの仮想マシンからメトリクスにアクセスする方法には、幾つかの方法があります:

1. Azure web portalを使ったグラフの生成と監視
2. Azureのストーレージに存在するメトリクスデーター自体を使用して監視
3. Azureと直接連携できる外部監視サービスを利用し、仮想マシンからメトリクスを収集して監視

このポストでは、最初に二つのオプション("Azure web portal"と"生データー")を使った監視方法について解説します。更に、このシリーズのPart3では、第三のオプション[「Datadogを使ったAzuzre仮想マシンの監視」](/blog/monitor-azure-vms-using-datadog)について解説していきます。

## Viewing metrics in the Azure web portal

> The [Azure web portal](https://portal.azure.com/) has built-in monitoring functionality for viewing and alerting on performance metrics. You can graph any of the metrics available in Azure and set simple alert rules to send email notifications when metrics exceed minimum or maximum thresholds.

[Azure web portal](https://portal.azure.com/)には、パフォーマンスメトリクス向けに、閲覧とアラート機能を持った監視システムがあらかじめ用意されています。Azureで提供されている全てのメトリクスはグラフとして表示することができ、又、簡単なアラートのルールを設定することで、閾値(最大値や最小値)を超えた際に通知を送信することができます。

### Enabling Azure VM monitoring

> Azure’s Diagnostics extension can be enabled when you create a new virtual machine via the Azure web portal. But even if you disabled Diagnostics when creating a VM, you can turn it on later from the “Settings” menu in the VM view. You can select which metrics you wish to collect (Basic metrics, Network and web metrics, .NET metrics, etc.) in the Diagnostics tile as well. You will have to link the VM to an Azure storage account to store your Diagnostics data.

Azureの"Diagnostics extension"は、Azure web portalより新しい仮想マシンを作成した時に有効にすることができます。更に、仮想マシンを作成する際に、"Diagnostics extension"を有効にしていなくても、後からVMビューの“Settings”メニューより有効にすることができます。Diagnosticsのタイルからは、収集したいメトリクス（基本メトリクス、ネットワークとWebのメトリクス、.NETメトリクスなど）を選択することもできます。Diagnosticsのデーターを保存するには、仮想マシンにAzureストレージのアカウントをリンクする必要があります。

> Note that portal users can create VMs using two different deployment models (“Classic” and “Resource Manager”). At present, some monitoring functionality is only available via the Classic deployment model.

注意: Azure portalのユーザは、2つの異なる"deployment model"(“Classic”と“Resource Manager”)で、仮想マシンを作成することができます。現時点で、いくつかの監視機能は"Classic deployment model"でのみ利用可能です。

[![Enable Azure diagnostics](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/2-enable-diagnostics-2.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/2-enable-diagnostics-2.png)

> Once monitoring is enabled, you will see several default metric graphs when you click on your VM in the Azure portal.

監視が有効になると、Azure portal上で仮想マシンをクリックすることにより、デフォルトメトリクスに関するグラフを閲覧することができるようになります。

![Default graphs](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/2-default-graphs.png)

> Clicking on any monitoring graph opens a larger view, along with two important settings options: “Edit chart,” which allows you to select the metrics and the timeframe displayed on that graph, and “Add alert,” which opens the Azure alerting tile.

監視グラフをクリックすると、拡大されたグラフと共に二つの重要な設定オプションが表示されます:

- **Edit chart**: グラフに表示されるメトリクスの選択と時間軸設定を可能にします。
- **Add alert**: Azure上でアラートを設定をするためのタイルを表示します。

![Metric graphs](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/2-bigger-graph.png)

> In the alerting tile you can set alerts on Azure VM metrics. Azure alerts can be set against any upper or lower threshold and will alert whenever the selected metric exceeds (or falls below) that threshold for a set amount of time. In the example below, we have set an alert that will notify us by email whenever the CPU usage on the given virtual machine exceeds 90 percent over a 10-minute interval.

アラート設定のタイルでは、Azureの仮想マシンのメトリクスに対してアラートを設定することができます。Azureのアラートは、上限または下限の閾値に対して設定することができます。そして、閾値を設定されたメトリクスが、指定した時間以上の間、閾値を超えた場合(又は、下回った場合)に、アラートを発生させることができます。以下の例では、ある仮想マシンのCPU使用率が10分間に渡って90%を超えた場合、メールで通知するアラートを設定しています。

[![Create alert](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/2-alert-rule.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/2-alert-rule.png)

## Accessing raw metric data in Azure storage

> Because Azure metrics are written to storage tables, you can access the raw data from Azure if you want to use external tools to graph or analyze your metrics. This post focuses on accessing metrics via Microsoft’s Visual Studio IDE, but you can also copy metric data tables to local storage using the [AzCopy utility](https://azure.microsoft.com/en-us/documentation/articles/storage-use-azcopy/) for Windows, or you can access metric data programmatically [using the .NET SDK](https://www.nuget.org/packages/Microsoft.Azure.Insights). Note that the [Azure command-line interface](https://azure.microsoft.com/en-us/documentation/articles/virtual-machines-command-line-tools/), which is available for Mac, Linux, and Windows, will allow you to view the list of tables in your storage accounts (via the `azure storage table list` command) but not the actual contents of those tables.

Azureのメトリクスは、ストレージ内のテーブルへ出力されているため、外部のツールでメトリクスをグラフ化したり分析したい場合は、生のデーターにアクセスすることができるようになっています。このポストでは、MicrosoftのVisual Studio IDEを介してメトリクスにアクセスするに方法を紹介します。この方法以外に、Windows用の[AzCopy utility](https://azure.microsoft.com/en-us/documentation/articles/storage-use-azcopy/)を使用し、ローカルストレージにメトリックデータテーブルをコピーすることができるほか、[.NET SDK](https://www.nuget.org/packages/Microsoft.Azure.Insights)を使用し、プログラム的にメトリクスデーターにアクセスすることもできます。

注意: Mac、Linx、Windowsで使用することができる[Azure command-line interface](https://azure.microsoft.com/en-us/documentation/articles/virtual-machines-command-line-tools/)は、Azureストレージアカウントに保存されているテーブルのリストを、`azure storage table list`コマンドを使って表示することはできますが、それらのテーブル内の実際のコンテンツを表示することはできません。

### Connecting to Azure in Visual Studio Cloud Explorer

> Starting with Visual Studio 2015 and Azure SDK 2.7, you can now use Visual Studio’s [Cloud Explorer](https://msdn.microsoft.com/en-us/library/azure/mt185741.aspx) to view and manage your Azure resources. (Similar functionality is available using [Server Explorer](https://msdn.microsoft.com/en-us/library/azure/ff683677.aspx#BK_ViewResources) in older versions of Visual Studio, but not all Azure resources may be accessible.)

Visual Studio 2015とAzure SDK2.7を組み合わせることで、Visual Studioの[Cloud Explorer](https://msdn.microsoft.com/en-us/library/azure/mt185741.aspx)を使いAzureのリソースを閲覧し、管理することができるよになります。(Visual Studioの旧バージョンでは、[Server Explorer](https://msdn.microsoft.com/en-us/library/azure/ff683677.aspx#BK_ViewResources)を使って同様の機能が提供されていますが、Azureのリソースの全てにアクセスできるわけではありません。)
> To view the Cloud Explorer interface in Visual Studio 2015, go to View &gt; Other Windows &gt; Cloud Explorer.


Visual Studio 2015のCloud Explorerインターフェースを表示するには、View &gt; Other Windows &gt; Cloud Explorer とメニューを選択していきます。

[![Cloud Explorer](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/2-cloud-explorer.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/2-cloud-explorer.png)

> Connect to your Azure account with Cloud Explorer by clicking on the gear and entering your account credentials.

歯車のマークをクリックし、Azureアカウント情報を入力することで、Cloud ExplorerにAzureへのアクセス権を付与します。

![Add Azure account to Visual Studio](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/2-add-account.png)

### View stored metrics

> Once you have signed in to your Azure subscription, you will find your metric storage listed under “Storage Accounts” or “Storage Accounts (Classic),” depending on whether the storage account was launched on Azure’s Resource Manager stack or on the Classic Stack.

その後、Azureのアカウントにサイン・インすることができたならば、"Storage Accounts"か"Storage Accounts (Classic)"という項目の配下にメトリクスの保存先を確認することができます。"Storage Accounts"か"Storage Accounts (Classic)"かは、"AzureのResource Manager"スタックか"Classic"スタックでストレージのアカウントが起動されたかにより異なります。

> Metrics are stored in tables, the names of which usually start with “WADMetrics.” Open up a metric table in one of your metric storage accounts, and you will see your VM metrics. Each table contains 10 days worth of data to prevent any one table from growing too large; the date is appended to the end of the table name.

メトリクスは、テーブルに格納され、“WADMetrics.”始まる名前が付与されます。"metric storage account"内のテーブルを表示すると、仮想マシンに関するメトリクスが表示されます。テーブルが巨大化するのを防ぐために、各テーブルには10日分のデーターが保存されるようになっています。そして、新しい日付のデーターは、テーブルの末尾に追加されていきます。

![Azure metrics in storage](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/2-wad-metrics2.png)

### Using stored metrics

> The name of your VM can be found at the end of each row’s partition key, which is helpful for filtering metrics when multiple VMs share the same metric storage account. The metric type can be found in the CounterName column.

仮想マシンの名前は、各行の、`partition key`の欄の末尾の部分で確認することができます。`partition key`の列の末尾に仮想マシン名を持っていることは、複数の仮想マシンで"metric storage account"を共有している場合に、メトリクスを抽出する際に非常に便利です。(尚、メトリクスのタイプは、CounterName欄に記載されています。)

[![Metrics in tables](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/2-metric-table.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/2-metric-table.png)

> To export your data for use in Excel or another analytics tool, click the “Export to CSV File” button on the toolbar just above your table.

Excelや他の解析ツールで使用するために、データーをエクスポートするには、テーブルの上にあるツールバー内にある“Export to CSV File”ボタンをクリックします。

![Export metrics to CSV](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-08-azure/2-export-to-csv.png)

## Conclusion

> In this post we have demonstrated how to use Azure’s built-in monitoring functionality to graph VM metrics and generate alerts when those metrics go out of bounds. We have also walked through the process of exporting raw metric data from Azure for custom analysis.

このポストでは、Azure上に作り込まれている監視機能を使って、仮想マシンのメトリクスをグラフ化し、メトリクスが閾値を超えた際にアラートを通知するようにしました。更に、独自の分析をするために、Azureから生のメトリクスデーターをエクスポートする方法も紹介しました。

> At Datadog, we have integrated directly with Azure so that you can begin collecting and monitoring VM metrics with a minimum of setup. Learn how Datadog can help you to monitor Azure in the [next and final post](/blog/monitor-azure-vms-using-datadog/) of this series.

Datadogでは、仮想マシンのメトリクスを最低限の労力で収集し、監視ができるように、Azureと直で連携できるようにしました。シリーズに含まれる次のポスト、[「Datadogを使ったAzure仮想マシンの監視」](https://www.datadoghq.com/blog/monitor-varnish-using-datadog/)では、Datadogを使ったAzureの監視方法を学ぶことができます。

------------------------------------------------------------------------

> *Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/azure/how_to_collect_azure_metrics.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues).*

*このポストのMarkdownソースは、[GitHub](https://github.com/DataDog/the-monitor/blob/master/azure/how_to_collect_azure_metrics.md)で閲覧することができます。質問、訂正、追加、などがありましたら、[GitHubのissueページ](https://github.com/DataDog/the-monitor/issues)を使って連絡を頂けると幸いです。*
