# Monitoring 101: Investigating performance issues

*This post is part of a series on effective monitoring. Be sure to check out the rest of the series: [Collecting the right data](/blog/monitoring-101-collecting-data/) and [Alerting on what matters](/blog/monitoring-101-alerting/).*

> The responsibilities of a monitoring system do not end with symptom detection. Once your monitoring system has notified you of a real symptom that requires attention, its next job is to help you diagnose the root cause. Often this is the least structured aspect of monitoring, driven largely by hunches and guess-and-check. This post describes a more directed approach that can help you to find and correct root causes more efficiently.

監視システムの責任は兆候を検出するところで終わりにはなりません。使っている監視システムが、対処を必要とするような具体的な兆候についてあなたに通知したなら、その監視システムで次にしなくてはならないのは、兆候を起こしている原因の診断をサポートすることです。多くの場合、この診断という側面は、ほとんど整理がされておらず、経験や直感に頼ることが多い領域です。この記事では、根本原因にたどり着き、修正するための論理的なアプローチについて解説をします。

> This series of articles comes out of our experience monitoring large-scale infrastructure for [our customers](https://www.datadoghq.com/customers/). It also draws on the work of [Brendan Gregg](http://dtdg.co/use-method), [Rob Ewaschuk](http://dtdg.co/philosophy-alerting), and [Baron Schwartz](http://dtdg.co/metrics-attention).

このシリーズの内容は、Datadogが[お客様](https://www.datadoghq.com/customers/)の大規模インフラを監視してきた経験を基に、次に紹介するよ人たちのブログ記事　[Brendan Gregg](http://dtdg.co/use-method)、 [Rob
Ewaschuk](http://dtdg.co/philosophy-alerting)、 [Baron
Schwartz](http://dtdg.co/metrics-attention) を参照して構成しています。

## A word about data

![metric types](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-05-how-to-monitor/alerting101_chart_1.png)

> There are three main types of monitoring data that can help you investigate the root causes of problems in your infrastructure. Data types and best practices for their collection are discussed in-depth [in a companion post](https://www.datadoghq.com/blog/2015/06/monitoring-101-collecting-data/), but in short:

> -   **Work metrics** indicate the top-level health of your system by measuring its useful output
> -   **Resource metrics** quantify the utilization, saturation, errors, or availability of a resource that your system depends on
> -   **Events** describe discrete, infrequent occurrences in your system such as code changes, internal alerts, and scaling events

インフラ内の問題の根本原因を調査する際に、参考にできる監視データには主に3つの主要タイプがあります。それらのデータタイプとそれらの収集するためのベストプラクティスの詳細については、[関連記事](https://www.datadoghq.com/blog/2015/06/monitoring-101-collecting-data/)を参照して下さい。

簡単なまとめ:

- **Work metrics**　運用しているシステム上で動作しているサービスのパフーマンスを表しています。
- **Resource metrics** 運用しているシステムが依存するリソースの使用率、飽和レベル、エラー、または可用性など。
- **Events** コードの変更、内部アラート、台数変化に関するイベントなど、システム内で発生する非連続的で不定期な出来事

> By and large, work metrics will surface the most serious symptoms and should therefore generate [the most serious alerts](https://www.datadoghq.com/blog/2015/06/monitoring-101-alerting/#page-on-symptoms). But the other metric types are invaluable for investigating the *causes* of those symptoms.

大方の場合、**work metrics** は、重大な問題の兆候を表面化させます。従って、**work metrics** は、[最も重大な障害用のアラート](https://www.datadoghq.com/blog/2015/06/monitoring-101-alerting/#page-on-symptoms)を発生させる必要があります。

## It’s resources all the way down

![metric uses](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-05-how-to-monitor/alerting101_2_chart.png)

> Most of the components of your infrastructure can be thought of as resources. At the highest levels, each of your systems that produces useful work likely relies on other systems. For instance, the Apache server in a LAMP stack relies on a MySQL database as a resource to support its work. One level down, within MySQL are database-specific resources that MySQL uses to do *its* work, such as the finite pool of client connections. At a lower level still are the physical resources of the server running MySQL, such as CPU, memory, and disks.

インフラの構成要素のほとんどは、リソースとして考えることが出来ます。一番上層から見た場合、あなたのシステムの価値のある仕事は、他のシステムに依存していることが多いです。例えば、LAMPスタックの中のApacheサーバーは、その仕事を進めるためにリソースとしてMySQLデータベースに依存しています。その下の層のMySQLの中では、限られたクライアントコネクションというデータベース特有のリソースに依存しMySQLは機能しています。最も底の層では、MySQLが動作しているサーバーの物理リソースであるCPU、メモリー、ディスク容量などに依存しています。

> Thinking about which systems *produce* useful work, and which resources *support* that work, can help you to efficiently get to the root of any issues that surface. When an alert notifies you of a possible problem, the following process will help you to approach your investigation systematically.

まず、どのシステムが価値のある仕事を生み出し、どのリソースがその仕事をサポートしているか考えてみて下さい。この考え方は、表面化している問題の根本原因に効率的にたどり着く手助けをしてくれるでしょう。次に紹介するプロセスは、アラートが問題かもしれない状況を通知した時、あなたが体系的に調査を進める上で、手助けとなるでしょう。

![recursive investigation](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-05-how-to-monitor/investigating_diagram_4.png)

### 1. Start at the top with work metrics

> First ask yourself, “Is there a problem? How can I characterize it?” If you don’t describe the issue clearly at the outset, it’s easy to lose track as you dive deeper into your systems to diagnose the issue.

まず自問してみてください。「これは問題なのか?」、「この問題は、どのような特徴を持っているのか?」このように最初に問題を明確にしておかないと、問題の診断のためにシステムの詳細を調べ始めた際に、どのように調査を進めるべできあったのかの道筋を見失うことになります。

>Next examine the work metrics for the highest-level system that is exhibiting problems. These metrics will often point to the source of the problem, or at least set the direction for your investigation. For example, if the percentage of work that is successfully processed drops below a set threshold, diving into error metrics, and especially the types of errors being returned, will often help narrow the focus of your investigation. Alternatively, if latency is high, and the throughput of work being requested by outside systems is also very high, perhaps the system is simply overburdened.

次に、問題を通知している最もユーザーに近い層のシステムのWorkメトリクスを検討します。これらのメトリクスは、多くの場合に問題の原因を指し示しているか、又は、少なくとも調査のための指針を示してくれています。例えば、正常に処理されたWorkの割合がしきい値を下回る場合、エラーに関するメトリクス(特に、処理の結果として発生しているエラータイプ)を検討することが、調査の焦点を絞り込むのに役立ちます。あるいは、レイテンシの値が高く、外部システムからのリクエストを受けている仕事のスループットの値も高い場合、恐らく、そのシステムは高負荷にあるだけでしょう。

### 2. Dig into resources

> If you haven’t found the cause of the problem by inspecting top-level work metrics, next examine the resources that the system uses—physical resources as well as software or external services that serve as resources to the system. If you’ve already set up dashboards for each system as outlined below, you should be able to quickly find and peruse metrics for the relevant resources. Are those resources unavailable? Are they highly utilized or saturated? If so, recurse into those resources and begin investigating each of them at step 1.

もしも、問題の原因を、最もユーザーに近い層のWorkメトリクスの検討から導き出せなかった場合、次は、そのシステムが使っている物理リソース、ソフトウェア、外部サービスなどのリソースを検討してみてください。下記に示したように各システムのダッシュボードを既に設定している場合は、迅速に関連しているリソースを見つけ出し、メトリクスを精査することができます。これらのリソースに「アクセスできているのだろうか?」、「高負荷で飽和していないだろうか?」を検討してみます。もしもこれらの問いの答えがYESなら、再び、それらのリソースをステップ1のように検討していきます。

### 3. Did something change?

> Next consider alerts and other events that may be correlated with your metrics. If a code release, [internal alert](https://www.datadoghq.com/blog/2015/06/monitoring-101-alerting/#levels-of-urgency), or other event was registered slightly before problems started occurring, investigate whether they may be connected to the problem.

次に、メトリクスに関連している他のイベントやアラートを検討してみます。新しいコードが適応されていないか、[システム内でアラート](https://www.datadoghq.com/blog/2015/06/monitoring-101-alerting/#levels-of-urgency)が記録されてないか、問題発生の少し前にその他のイベントは記録されていないか、などが問題と関係していないかを検討します。

### 4. Fix it (and don’t forget it)

> Once you have determined what caused the issue, correct it. Your investigation is complete when symptoms disappear—you can now think about how to change the system to avoid similar problems in the future.

問題の原因を特定できたら、それを修正します。問題となっている徴候が解消したら、緊急対処は終了です。ここからは、今後同じ問題に遭遇しないように、システムをどのように改善するべきか検討することになります。

## Build dashboards before you need them

[![dashboard](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-05-how-to-monitor/example-dashboard-2.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-05-how-to-monitor/example-dashboard-2.png)

> In an outage, every minute is crucial. To speed your investigation and keep your focus on the task at hand, set up dashboards in advance. You may want to set up one dashboard for your high-level application metrics, and one dashboard for each subsystem. Each system’s dashboard should render the work metrics of that system, along with resource metrics of the system itself and key metrics of the subsystems it depends on. If event data is available, overlay relevant events on the
graphs for correlation analysis.

障害が発生した時は、1秒も無駄にしたくないものです。調査、検討を円滑に進め、今取り組むべきタスクに集中できるように、予めダッシュボードを設定しておくことお勧めします。ダッシュボードは、最もユーザーに近い層のアプリケ−ションのメトリクスをまとめたものと、各サブシステムについて設定しておく良いでしょう。各システムのダッシュボードには、そのシステムのWorkメトリクスと、そのシステムのResourceメトリクスと依存しているサブシステムのキーメトリクスを表示しておくと良いでしょう。イベント情報が収集できている場合、相関分析のためにそれらのイベント情報をグラフに重ね書きしておきましょう。

## Conclusion: Follow the metrics

> Adhering to a standardized monitoring framework allows you to investigate problems more systematically:

> -   For each system in your infrastructure, set up a dashboard ahead of time that displays all its key metrics, with relevant events overlaid.
> -   Investigate causes of problems by starting with the highest-level system that is showing symptoms, reviewing its [work and resource metrics](https://www.datadoghq.com/blog/2015/06/monitoring-101-collecting-data/#metrics) and any associated events.
> -   If problematic resources are detected, apply the same investigation pattern to the resource (and its constituent resources) until your root problem is discovered and corrected.

標準化された監視フレームワークを厳守することで、体系的に問題の検討を進めることが出来ます:

- インフラの各システムに対し、キーメトリクスとシステムに関連したイベントを重ね書きしたダッシュボードを、予め準備しておきましょう。
- 問題の原因の調査、検討は、最もユーザーに近い層のシステムの徴候から始め、[workメトリクスとresourceメトリクス](https://www.datadoghq.com/blog/2015/06/monitoring-101-collecting-data/#metrics)を検討し、それらに関連しているイベントを検証しましょう。
- リソースに問題があることが分かった場合は、リソースに対しこれまでと同じ調査、検討パターンを適応していきます。その下のサブリソースにも同様にこのパターンを適用し、根本原因を発見し、修正が終わるまで続けます。

> We would like to hear about your experiences as you apply this framework to your own monitoring practice. If it is working well, please [let us know on Twitter](https://twitter.com/datadoghq)! Questions, corrections, additions, complaints, etc? Please [let us know on GitHub](https://github.com/DataDog/the-monitor/blob/master/monitoring-101/monitoring_101_investigating_performance_issues.md).

独自に実践していた監視体制にこのフレームワークで学んだことを取り入れ、新たな監視体制に取り組んだ体験を是非お聞かせください。 フレームワークを取り入れることによって監視が改善された場合は、Twitterで[@datadoghq](https://twitter.com/datadoghq)付きでつぶやいていただけると幸いです。また、質問、修正、追加、苦情、その他がある場合は、[Github](https://github.com/DataDog/the-monitor)のissueにて連絡してください。
