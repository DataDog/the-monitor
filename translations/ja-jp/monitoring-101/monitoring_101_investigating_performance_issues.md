# Monitoring 101: Investigating performance issues

*This post is part of a series on effective monitoring. Be sure to check out the rest of the series: [Collecting the right data](/blog/monitoring-101-collecting-data/) and [Alerting on what matters](/blog/monitoring-101-alerting/).*

> The responsibilities of a monitoring system do not end with symptom detection. Once your monitoring system has notified you of a real symptom that requires attention, its next job is to help you diagnose the root cause. Often this is the least structured aspect of monitoring, driven largely by hunches and guess-and-check. This post describes a more directed approach that can help you to find and correct root causes more efficiently.

監視システムの責任は兆候の検出するところでは終わりにはなりません。使っている監視システムが、対処を必要とするような具体的な兆候についてあなたに通知したなら、その監視システムの次にしなくてはならないのは、兆候を起こしている原因の診断をするあなたを助けることです。多くの場合、この診断という側面は、ほとんど整理がされておらず、経験や直感に頼ることが多い領域です。この記事では、根本原因にたどり着き、修正するための論理的なアプローチについて解説をします。

> This series of articles comes out of our experience monitoring large-scale infrastructure for [our customers](https://www.datadoghq.com/customers/). It also draws on the work of [Brendan Gregg](http://dtdg.co/use-method), [Rob Ewaschuk](http://dtdg.co/philosophy-alerting), and [Baron Schwartz](http://dtdg.co/metrics-attention).

このシリーズの内容は、Datadogが[お客様](https://www.datadoghq.com/customers/)の大規模インフラを監視してきた経験を基にし、次に紹介するような人たちのブログ記事　[Brendan Gregg](http://dtdg.co/use-method)、 [Rob
Ewaschuk](http://dtdg.co/philosophy-alerting)、 [Baron
Schwartz](http://dtdg.co/metrics-attention) を参照して構成しています。

## A word about data

![metric types](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-05-how-to-monitor/alerting101_chart_1.png)

> There are three main types of monitoring data that can help you investigate the root causes of problems in your infrastructure. Data types and best practices for their collection are discussed in-depth [in a companion post](https://www.datadoghq.com/blog/2015/06/monitoring-101-collecting-data/), but in short:

> -   **Work metrics** indicate the top-level health of your system by measuring its useful output
> -   **Resource metrics** quantify the utilization, saturation, errors, or availability of a resource that your system depends on
> -   **Events** describe discrete, infrequent occurrences in your system such as code changes, internal alerts, and scaling events

インフラ内の問題の根本原因を調査する際に、参考のできる監視データには主に3つの主要タイプがあります。それらのデータタイプとそれらの収集するためのベストプラクティスの詳細については、[関連記事](https://www.datadoghq.com/blog/2015/06/monitoring-101-collecting-data/)を参照してください。

簡単なまとめ:

- **Work metrics**　運用しているシステム上で動作しているサービスのパフーマンスを表しています。
- **Resource metrics** 運用しているシステムが依存するリソースの使用率、飽和レベル、エラー、または可用性など。
- **Events** コードの変更、内部アラート、台数変化に関するイベントなど、システム内で発生する非連続的で不定期な出来事

> By and large, work metrics will surface the most serious symptoms and should therefore generate [the most serious alerts](https://www.datadoghq.com/blog/2015/06/monitoring-101-alerting/#page-on-symptoms). But the other metric types are invaluable for investigating the *causes* of those symptoms.

大方の場合、**work metrics** は、重大な問題の兆候を表面化させます。従って、**work metrics** は、[最も重大な障害用のアラート](https://www.datadoghq.com/blog/2015/06/monitoring-101-alerting/#page-on-symptoms)を発生させる必要があります。

## It’s resources all the way down

![metric uses](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-05-how-to-monitor/alerting101_2_chart.png)

> Most of the components of your infrastructure can be thought of as resources. At the highest levels, each of your systems that produces useful work likely relies on other systems. For instance, the Apache server in a LAMP stack relies on a MySQL database as a resource to support its work. One level down, within MySQL are database-specific resources that MySQL uses to do *its* work, such as the finite pool of client connections. At a lower level still are the physical resources of the server running MySQL, such as CPU, memory, and disks.

インフラストラクチャのコンポーネントのほとんどは、リソースと考えることができます。最高レベルでは、可能性の高い有用な仕事を生成するあなたのシステムのそれぞれは、他のシステムに依存しています。例えば、LAMPスタックのApacheサーバがその作業をサポートするためのリソースとしてMySQLデータベースに依存しています。 MySQLの内の1つ上のレベルダウンは、MySQLは、このようなクライアント接続の有限プールとしてその作業を、行うために使用するデータベース固有のリソースです。低いレベルではまだこのようなCPU、メモリ、ディスクなどのMySQLを実行しているサーバーの物理的なリソースが、あります。

> Thinking about which systems *produce* useful work, and which resources *support* that work, can help you to efficiently get to the root of any issues that surface. When an alert notifies you of a possible problem, the following process will help you to approach your investigation systematically.

これについて考えるシステムは有用な仕事を生成し、そのリソースが仕事、あなたが効率的に表面の任意の問題の根本を取得するのを助けることができることを支持しています。アラートは問題がある可能性を通知すると、次のプロセスでは、体系的にあなたの調査をアプローチするのに役立ちます。

![recursive investigation](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-05-how-to-monitor/investigating_diagram_4.png)

### 1. Start at the top with work metrics

> First ask yourself, “Is there a problem? How can I characterize it?” If you don’t describe the issue clearly at the outset, it’s easy to lose track as you dive deeper into your systems to diagnose the issue.

まず自問してみて、「問題はありませんか？どのように私はそれを特徴付けることができますか？"あなたが最初に明らかに問題を記述しない場合、それはあなたが問題を診断するために、あなたのシステムに深く潜るように、トラックを失うのは簡単です。

>Next examine the work metrics for the highest-level system that is exhibiting problems. These metrics will often point to the source of the problem, or at least set the direction for your investigation. For example, if the percentage of work that is successfully processed drops below a set threshold, diving into error metrics, and especially the types of errors being returned, will often help narrow the focus of your investigation. Alternatively, if latency is high, and the throughput of work being requested by outside systems is also very high, perhaps the system is simply overburdened.

次の問題点を展示している最高レベルのシステムの作業メトリックを調べます。これらのメトリックは、多くの場合、問題の原因を指し、または少なくともあなたの調査のための方向を設定します。たとえば、正常にエラーメトリックに設定された閾値、ダイビングを下回ったが処理され、エラーの種類、特にされている作業の割合が返された場合、多くの場合、あなたの調査の焦点を絞り込むのに役立ちます。レイテンシが高く、外部のシステムによって要求される作業のスループットも非常に高い場合あるいは、恐らくシステムは単に過負荷です。

### 2. Dig into resources

> If you haven’t found the cause of the problem by inspecting top-level work metrics, next examine the resources that the system uses—physical resources as well as software or external services that serve as resources to the system. If you’ve already set up dashboards for each system as outlined below, you should be able to quickly find and peruse metrics for the relevant resources. Are those resources unavailable? Are they highly utilized or saturated? If so, recurse into those resources and begin investigating each of them at step 1.

あなたはトップレベルの作業メトリックを調べて問題の原因を発見していない場合は、次のシステムは、システムへのリソースとして機能するリソースだけでなく、ソフトウェアや外部サービス·物理を使用するリソースを調べます。下記のようにすでに各システムのダッシュボードを設定している場合は、すぐに見つけて、関連するリソースのメトリックを閲覧することができるはずです。これらのリソースは使用できませんか？彼らは非常に利用または飽和されていますか？もしそうであれば、それらのリソースに再帰し、ステップ1でそれらのそれぞれを調査し始めます。

### 3. Did something change?

> Next consider alerts and other events that may be correlated with your metrics. If a code release, [internal alert](https://www.datadoghq.com/blog/2015/06/monitoring-101-alerting/#levels-of-urgency), or other event was registered slightly before problems started occurring, investigate whether they may be connected to the problem.

次へアラートとあなたの測定基準と相関することができる他のイベントを検討してください。問題が発生して開始する前に、コードのリリース、内部警告、または他のイベントが若干登録されている場合、彼らは問題に接続することができるかどうかを調べます。

### 4. Fix it (and don’t forget it)

> Once you have determined what caused the issue, correct it. Your investigation is complete when symptoms disappear—you can now think about how to change the system to avoid similar problems in the future.

あなたが問題の原因を決定したら、それを修正します。症状は、あなたが消え、今、将来的に同様の問題を回避するためにシステムを変更する方法を考えることができるときあなたの調査は完了です。

## Build dashboards before you need them

[![dashboard](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-05-how-to-monitor/example-dashboard-2.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-05-how-to-monitor/example-dashboard-2.png)

> In an outage, every minute is crucial. To speed your investigation and keep your focus on the task at hand, set up dashboards in advance. You may want to set up one dashboard for your high-level application metrics, and one dashboard for each subsystem. Each system’s dashboard should render the work metrics of that system, along with resource metrics of the system itself and key metrics of the subsystems it depends on. If event data is available, overlay relevant events on the graphs for correlation analysis.

停電では、毎分は非常に重要です。あなたの調査を高速化し、手元の作業にあなたの焦点を維持し、事前にダッシュボードを設定します。あなたは、高レベルのアプリケーション·メトリックのための1つのダッシュボード、および各サブシステムごとに1つのダッシュボードを設定することもできます。各システムのダッシュボードは、システム自体とそれが依存するサブシステムの主要指標のリソース測定基準と一緒に、そのシステムの作業メトリックをレンダリングする必要があります。イベントデータが利用可能である場合、相関分析のためのグラフに関連するイベントをオーバーレイ。

## Conclusion: Follow the metrics

> Adhering to a standardized monitoring framework allows you to investigate problems more systematically:

> -   For each system in your infrastructure, set up a dashboard ahead of time that displays all its key metrics, with relevant events overlaid.
> -   Investigate causes of problems by starting with the highest-level system that is showing symptoms, reviewing its [work and resource metrics](https://www.datadoghq.com/blog/2015/06/monitoring-101-collecting-data/#metrics) and any associated events.
> -   If problematic resources are detected, apply the same investigation pattern to the resource (and its constituent resources) until your root problem is discovered and corrected.

標準化された監視フレームワークに付着すると、より体系の問題を調査することができます：

- インフラストラクチャ内の各システムは、関連するイベントが重ねで、すべての主要な統計が表示され、事前にダッシュボードを設定します。
- その[ワークとリソースのメトリック]（https://www.datadoghq.com/blog/2015/06/monitoring-101-collecting-dataを見直し、症状を示している最高レベルのシステムで起動することによって問題の原因を調査/＃メトリクス）および関連するイベント。
- 問題のリソースが検出された場合は、あなたの根本的な問題が発見され、修正されるまで、リソース（およびその構成リソース）に同じ調査パターンを適用します。

> We would like to hear about your experiences as you apply this framework to your own monitoring practice. If it is working well, please [let us know on Twitter](https://twitter.com/datadoghq)! Questions, corrections, additions, complaints, etc? Please [let us know on GitHub](https://github.com/DataDog/the-monitor/blob/master/monitoring-101/monitoring_101_investigating_performance_issues.md).

独自に実践していた監視体制にこのフレームワークで学んだことを取り入れ、新たな監視体制に取り組んだ体験を是非お聞かせください。 フレームワークを取り入れることによって監視が改善された場合は、Twitterで[@datadoghq](https://twitter.com/datadoghq)付きでつぶやいていただけると幸いです。また、質問、修正、追加、苦情、その他がある場合は、[Github](https://github.com/DataDog/the-monitor)のissueにて連絡してみてください。
