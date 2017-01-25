# How Lithium monitors OpenStack

[Lithium] was founded in 2001 as an offshoot from gamers.com (a gaming community) and has since evolved into a leading social software provider whose Total Community platform helps brands connect, engage and understand their customers. With more than [400 communities][communities] and growing, Lithium uses [OpenStack] as a private datacenter, with flexibility to deploy customized, public-facing communities to major brands across industries and regions.

In this article we will pull back the curtain to learn Lithium's best practices and tips for using OpenStack, and how Lithium monitors OpenStack with the help of Datadog.

リチウムは、gamers.com（ゲームコミュニティ）からの分派として2001年に設立されました。以来、Lithiumのコミュニティプラットフォームは、ブランドを展開し、顧客と関わり、彼らを理解するための最先端のソーシャル・ソフトウェア・プロバイダーへと進化してきました。[400以上のコミュニティー][communities]を抱え会社が拡大している状況で、Lithiumは、[OpenStack][OpenStack]を、世界中の各業界の主要ブランドに、カスタマイズ性を有した柔軟なコミュニティー運用環境を提供するするためのプライベートデータセンターとして活用しています。400以上のコミュニティと成長していると、リチウムは業種や地域間の主要なブランドにカスタマイズされた、一般向けのコミュニティを展開する柔軟性を備えた、プライベートデータセンターとしてOpenStackは使用しています。

この記事では、[Lithium][Lithium]のOpenStackのを使用するためのベストプラクティスやヒントを解き明かし、LithiumがどのようにDatadogを使ってOpenStackを監視しているかを紹介していきます。


## Why monitoring OpenStack is critical

[OpenStack] is a central component in Lithium's infrastructure, forming the backbone of their service platform. Lithium leverages OpenStack for both production and development environments, with OpenStack hosting a large number of production communities, as well as demo communities for sales engineers.  
In addition to community hosting, OpenStack also hosts infrastructure services, including [Kubernetes], [Chef] servers and [BIND] slaves. 

With such a far-reaching deployment, failure is not an option. If OpenStack were not properly monitored and managed, numerous and noticeable failures can occur: sales engineers wouldn't be able to create demo environments for prospects, developers wouldn't be able to spawn test environments, and the communities in production could go down or see increased response times as computing resources became unavailable. 

That's why Lithium's engineers monitor OpenStack around the clock. Using [Datadog], they can correlate all the relevant OpenStack metrics with metrics from other parts of their infrastructure, all in one place. Lithium engineers can spot issues at a glance and determine the root cause of the problem, in addition to setting up advanced alerts on mission-critical metrics.

[OpenStack][OpenStack]は、Lithiumのサービスプラットフォームのバックボーンで、Lithiumのインフラの最も重要な構成要素です。Lithiumは、本番環境と開発環境の両方にOpenStackを活用しています。大量のメンバーを抱えた本番コミュニティーや、セールスエンジニアのデモのコミュニティもOpenStackで運用しています。コミュニティー運用の環境のホスティング以外に、[Kubernetes][Kubernetes], [Chef][Chef] server, [BIND][BIND] slavesなどのインフラ構成要素を運用するためにOpenStackを使っています。

このような、大規模で複雑な環境では、障害を起こすことは許されません。OpenStackが、適切に監視され管理されていないと、顕著な障害が多数発生することになるでしょう。例えば、セールスエンジニアは見込み客のためのデモ環境を作成することはできないし、開発者はテスト環境を起動することができないし、本番環境では、コンピューティングリソースが使えなくなるにつれてレスポンス時間が長くなり、停止を経験することもあるでしょう。

従って、LithiumのエンジニアはOpenStackを24時間常に監視しています。[Datadog][Datadog]を使うことにより、OpenStackから収集したメトリクスとインフラの他の部分から収集した情報を一カ所に集め、それらの情報を関連づけて活用することができるようになります。Lithiumのエンジニアは、ミッションクリティカルなメトリクスに対し柔軟にアラートを設定できること加え、障害の発生箇所一目で発見し、問題の原因を特定することができるようになります。


[![Lithium OpenStack dashboard][lithium-dash]][lithium-dash]
_A Datadog dashboard that Lithium uses to monitor OpenStack_

## Key metrics for Lithium

### Number of instances running
Lithium engineers track the total number of instances running across their OpenStack deployment to correlate with changes in other metrics. For example, a large increase in total RAM used makes sense in light of additional instances being spun up. Tracking the number of instances running alongside other metrics helps inform decisions for capacity and [tenant quota][quotas] planning.

Lithiumのエンジニアは、OpenStack環境で起動しているインスタンスの総数を他のメトリクスの変化と連携させるために、動作インスタンス数を収集しています。例えば、RAM使用量の大幅な増加は、追加のインスタンスの起動に照らし合わせれば、説明が付きます。動作インスタンス数を他のメトリクスと併せて把握しておくことは、インフラ規模とtenantに割り当てるquotaの計画をする際の判断材料も与えてくれます。


### Instances per project
Like the total number of instances running, Lithium tracks the number of instances used per project to get a better idea of how their private cloud is being used. A common problem they found was that engineers would often spin up development environments and forget to shut them down, which means resources were provisioned but unused. By tracking the number of instances per project, admins could rein in excessive or unnecessary usage and free up resources without resorting to installing additional hardware.

動作しているインスタンスの総数と同じように、Lithiumでは、プライベートクラウドがどのように活用されているかを把握するために、プロジェクト毎のインスタンス数を把握しています。日常的に発生する問題として彼らは、"エンジニアが、開発環境を起動し、停止することを忘れ、使われていない環境にリソースが提供されている"ことを発見しました。プロジェクトごとのインスタンス数を追跡することにより、管理者は、極端なリーソースの利用や必要でないリソースの利用を抑制し、追加のハードウェアをインストールするに頼ることなく、リソースを確保することができるようになります。


### Available memory
As mentioned in [Part 1][part 1] of our [series][part 2] on [monitoring OpenStack Nova][part 3], visibility into OpenStack's resource consumption is essential to ensuring smooth operation and preventing user frustration. If available resources were insufficient, sales engineers would be breathing down the neck of the techops team, unable to create demo accounts for prospects, and developers would be stuck without a dev environment.

[OpenStack Novaの監視][Part 3]に関する[シリーズ][Part 2]の[Part 1][part 1]で紹介したように、リソースの消費量を把握しておくことは、円滑な運用とユーザーの不満を防止するために不可欠です。もしも、利用可能なリソースが十分確保できていない場合、セールスエンジニアは、見込み客のデモ環境を作ることができなくなり、運用チームの行動を監視するようになるでしょう。開発社は、開発環境を手に入れられず、立ち往生してしまうでしょう。


### VCPU available
Just like available memory, tracking the number of VCPUs available for allocation is critical—a lack of available CPUs prevents provisioning of additional instances. 

空きメモリと同じように、空きVCPU数を把握しておきことも必要不可欠です。利用可能なCPUの不足は、追加のインスタンスの起動の原因につながります。


### Metric deltas
[![Change in instances used][instance-change-graph]][instance-change-graph]

Finally, Lithium tracks the changes in metrics' values over time to give insight into the causes of changes in resource availability and consumption. 

Using Datadog's [Change graph feature][graph-change], engineers have a bird's eye view of week-to-week changes in resource usage. By analyzing resource deltas, engineers and decision makers have the data they need to inform hardware purchasing decisions and perform diligent capacity planning.

最後に、Lithiumは、リソースの利用可能量と消費量の変化の原因を把握するために、メトリクス値の時間変化を把握しています。

Datadogの[Change graph機能][graph-change]を使い、エンジニアは、週単位のリソースの使用量の概要を把握しています。リソースの変化を分析することで、エンジニアや意思決定者は、ハードウェア購入の意思決定の必要性を把握でき、容量計画基づいた積極的な運用が可能になります。


## Alerting the right people
Alerting is an [essential component][alerting-101] of any monitoring strategy—alerts let engineers react to issues as they occur, before users are affected. With Datadog alerts, Lithium is able to send notifications via their usual communication channels (chat, PagerDuty, email, etc.), as well as provide engineers with suggested fixes or troubleshooting techniques—all without human intervention.

Lithium generally uses [PagerDuty] for priority alerts, and [HipChat] or email for lower-priority alerts and for alerting specific engineers to a particular issue. For OpenStack, Lithium alerts on excessive resource consumption. As mentioned in [Part 1][part 1] of our OpenStack series, monitoring resource consumption is a **critical** part of a comprehensive OpenStack monitoring strategy.

[アラートの設計][alerting-101]]は、監視戦略を考える上では非常に重要な要素です。アラートは、ユーザーに影響が及ぶ前に、順次発生する障害に対象するように仕向けます。Datadogのアラート機能を使い、Lithiumは、日常的に使っている情報共有チャネル(チャット, 電子メール, PagerDutyなど)に、受信者に対するトラブルシューティングの方法や修正案を含んだ通知を人間が関与することなく送信できるようになりました。

Lithiumでは、問題に性質によって特定のエンジニアに通知するために、優先度の高いアラートには[PagerDuty][PagerDuty]を、それほど優先度の高くないアラートには[HipChat][HipChat]や電子メールを使っています。OpenStackの場合は、過剰なリソース消費に対してアラートを通知するようにしています。このOpenStackシリーズの[Part 1][part 1]で紹介したように、リソースの消費量の監視は、総合的なOpenStackの監視を考える上では不可欠な部分です。


[![Lithium alerts][lithium-alert]][lithium-alert]

Datadog alerts give Lithium engineers the flexibility to inform the right people that a problem has occurred, at the right time, across an [ever-growing][integration-list] list of platforms. 

Datadogを使ったアラートは、[日々増え続けるプラットフォーム構成部品][integration-list]を前に、Lithiumのエンジニアに、適切なタイミングで適切な人材に対し通知するための柔軟性を提供しています。


## Why Datadog?
Before adopting Datadog, Lithium admins were relying on [Horizon][Horizon] (OpenStack's canonical dashboard) to extract meaningful metrics from their deployment. This approach was severely limited—engineers could only access rudimentary statistics about their deployment and lacked the ability to correlate metrics from OpenStack with metrics from across their infrastructure.

With Datadog [screenboards], they can combine the historical perspective of graphed timeseries data with alert values to put current operations metrics in context.

Datadogを採用する前は、Lithiumの管理者は、本番環境から意味のあるメトリクスを手取り出すために[Horizon][Horizon] （OpenStackの標準的なダッシュボード）に頼っていました。この方法には、多くの制限がありました。エンジニアは、本番環境の初歩的な統計にしかアクセスできず、OpenStackのメトリクスとインフラ全体から収集しているメトリクスを相関させることもできませんでした。

Datadogの[screenboards][screenboards]を使うことにより、Lithiumのエンジニアは、グラフ化したメトリクスデータとアラートで設定している値を過去に遡って検証し、現在必要な運用メトリクスを導き出せるようになりました。


[![Lithium widgets][lithium-widgets]][lithium-widgets]

Datadog also makes it easy to collect and monitor [RabbitMQ] and MySQL metrics, in addition to general OpenStack metrics, for even deeper insight into performance issues. For Lithium, having Datadog in place has allowed engineers to adjust internal workflows, reducing the total number of elements that need monitoring.

又、Datadogは、パフォーマンス問題の更に深い洞察を得るために、OpenStackの一般的なメトリクスに加え、RabbitMQとMySQLのメトリックスを監視することを容易にしました。Lithiumにとって、Datadogを採用することは、内部のワークフローを調整し、監視を必要とする要素を減らすことになりました。


### Saving time, money, and reputation
Adopting Datadog has allowed Lithium to catch problems in OpenStack as well as applications running on their OpenStack cloud. Now, Lithium engineers have the tools and information they need to react quickly to problems and resolve infrastructure issues with minimal customer impact, saving time, money, and reputation.

採用Datadogは、OpenStackの中の問題だけでなく、そのOpenStackのクラウド上で実行中のアプリケーションをキャッチするためにリチウムを可能にしました。さて、リチウムエンジニアは、時間、お金、と評判の保存、問題に迅速に反応し、最小限の顧客への影響とインフラの問題を解決するために必要なツールや情報を持っています。


## Conclusion
[![Nova default dash][nova-dash]][nova-dash]
_Default Datadog OpenStack dashboard_

If you're already using OpenStack and Datadog, we hope these strategies will help you gain improved visibility into what's happening in your deployment. If you don't yet have a Datadog account, you can [start monitoring][part 3] OpenStack performance today with a [free trial].

もしも既にOpenStackとDatadogを使っているなら、ここで紹介している考え方が、本番環境で起きている症状を把握する手助けになるでしょう。もしも、Datadogのアカウントをまだ持っていないなら、[トライアルアカウント][free trial]に登録すれば、[Datadogで、直ちにOpenStackのパフォーマンスの監視][[part 3]]を始められるでしょう。


## Acknowledgments

Thanks to [Lithium] and especially [Mike Tougeron][twit], Lead Cloud Platform Engineer, for generously sharing their OpenStack expertise and monitoring strategies for this article.

この記事においてOpenStackに関するノウハウとその監視の考え方について惜しみなく共有してくださったことを、[Lithium][Lithium]、特にリード・クラウドプラットフォーム・エンジニアの[Mike Tougeron][twit]氏に感謝します。


<iframe width="100%" height="100" style="border: 0;" src="https://go.pardot.com/l/38172/2015-03-02/h6c2r" scrolling="no" type="text/html" frameborder="0" allowtransparency="true"></iframe>

[alerting-101]: https://www.datadoghq.com/blog/monitoring-101-alerting/
[BIND]: https://www.isc.org/downloads/bind/
[Chef]: https://www.chef.io/chef/
[communities]: http://www.lithium.com/why-lithium/customer-success/
[Datadog]: https://datadoghq.com
[graph-change]: http://docs.datadoghq.com/graphing/#select-your-visualization
[HipChat]: https://www.hipchat.com/
[Horizon]: http://docs.openstack.org/developer/horizon/
[instance-change-graph]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-OpenStack/lithium/instances-change-graph.png
[integration-list]: http://docs.datadoghq.com/integrations/
[Kubernetes]: https://www.datadoghq.com/blog/corral-your-docker-containers-with-kubernetes-monitoring/
[Lithium]: http://www.lithium.com
[lithium-alert]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-OpenStack/lithium/lithium-alert.png
[lithium-dash]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-OpenStack/lithium/lithium-dashboard.png
[lithium-widgets]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-OpenStack/lithium/lithium-widgets.png
[OpenStack]: https://www.openstack.org
[PagerDuty]: https://www.pagerduty.com/
[quotas]: http://docs.openstack.org/user-guide-admin/dashboard_set_quotas.html
[nova-dash]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-OpenStack/default-dash.png
[RabbitMQ]: https://www.datadoghq.com/blog/openstack-monitoring-nova/#rabbitmq-metrics
[screenboards]: http://help.datadoghq.com/hc/en-us/articles/204580349-What-is-the-difference-between-a-ScreenBoard-and-a-TimeBoard-
[twit]: https://twitter.com/mtougeron

[free trial]: https://app.datadoghq.com/signup
[part 1]: https://www.datadoghq.com/blog/openstack-monitoring-nova/
[part 2]: https://www.datadoghq.com/blog/collecting-metrics-notifications-openstack-nova/
[part 3]: https://www.datadoghq.com/blog/openstack-monitoring-datadog/