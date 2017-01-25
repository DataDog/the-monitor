Monitoring 101: Alerting on what matters
========================================

> *This post is part of a series on effective monitoring. Be sure to check out the rest of the series: [Collecting the right data](/blog/monitoring-101-collecting-data/) and [Investigating performance issues](/blog/monitoring-101-investigation/).*

*このポストは、「効果的な監視: Monitoring 101」シリーズの一部です。このポストの他に、[Collecting the right data](/blog/monitoring-101-collecting-data/) と [Investigating performance issues](/blog/monitoring-101-investigation/) も、合わせて目を通すことをお勧めします。*

> Automated alerts are essential to monitoring. They allow you to spot problems anywhere in your infrastructure, so that you can rapidly identify their causes and minimize service degradation and disruption.

監視システムでは、自動化されたアラート通知は不可欠です。 自動化されたアラートによってインフラに起きている問題に気づき、問題の原因を見つけ出し、 サービスの質の低下や中断を最小に抑えることができます。

> But alerts aren’t always as effective as they could be. In particular, real problems are often lost in a sea of noisy alarms. This article describes a simple approach to effective alerting, regardless of the scale of the systems involved. In short:
>
> 1.	Alert liberally; page judiciously
> 2.	Page on symptoms, rather than causes

しかしアラートは、その本来の意図と反し、有効でない時も有ります。 特に、頻繁にアラームが押し寄せる状態では、本当に対処しなくてはならない問題も無視されることが多々有ります。 この記事では、効果的にアラートを発生させるためのシンプルなアプローチについて解説します。

1. アラートの設定と的確な通知
2. 兆候による通知。

> This series of articles comes out of our experience monitoring large-scale infrastructure for [our customers](https://www.datadoghq.com/customers/). It also draws on the work of [Brendan Gregg](http://dtdg.co/use-method), [Rob Ewaschuk](http://dtdg.co/philosophy-alerting), and [Baron Schwartz](http://dtdg.co/metrics-attention).

このシリーズは、Datadogが[お客様](https://www.datadoghq.com/customers/)の大規模インフラを監視してきた経験を基に、以下に紹介する人たちのブログ記事　[Brendan Gregg](http://dtdg.co/use-method)、 [Rob Ewaschuk](http://dtdg.co/philosophy-alerting)、 [Baron Schwartz](http://dtdg.co/metrics-attention) を参照して構成しています。

When to alert someone (or no one)
---------------------------------

![](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-05-how-to-monitor/alerting101_2_chart.png)

> An alert should communicate something specific about your systems in plain language: “Two Cassandra nodes are down” or “90% of all web requests are taking more than 0.5s to process and respond.”　Automating alerts across as many of your systems as possible allows you to respond quickly to issues and provide better service, and it also saves time by freeing you from continual manual inspection of metrics.

アラートでは、システムで起きている状況を具体的で明確な言葉で伝える必要があります。例えば、"Cassandraのノードが2台停止している"とか"webへのリクエストの90%が、回答に0.5秒以上の時間を要している"というようになります。システムの多くのアラートを可能な限り自動化することで、障害に対し迅速に対応出来るようになり、より良いサービスを提供出来るようになります。更に、継続的にメトリクスを手動で検査する事から解放されるので、多くの時間を節約することが可能になります。

### Levels of alerting urgency

> Not all alerts carry the same degree of urgency. Some require immediate human intervention, some require eventual human intervention, and some point to areas where attention may be needed in the future. All alerts should, at a minimum, be logged to a central location for easy correlation with other metrics and events.

全てのアラートは同じ緊急度合を求めてはいません。一部のものは即時に人間による介入が必要であり、いくつかのものは結果として人間による介入が必要で、そしていくつかは将来的に気を配って対応しなくてはならない問題を指摘しています。全てのアラートは、必要最低限で、どこか一箇所に記録され、他のメトリクスやイベントと連携出来るようになっている必要が有ります。

#### Alerts as records (low severity)

> Many alerts will not be associated with a service problem, so a human may never even need to be aware of them. For instance, when a data store that supports a user-facing service starts serving queries much slower than usual, but not slow enough to make an appreciable difference in the overall service’s response time, that should generate a low-urgency alert that is recorded in your monitoring system for future reference or investigation but does not interrupt anyone’s work. After all, transient issues that could be to blame, such as network congestion, often go away on their own. But should a significant issue develop—say, if the service starts returning a large number of timeouts—that alert-based data will provide invaluable context for your investigation.

例えば、ユーザーと対面しているサービスを支えているデータストレージのクエリー処理が普段より時間を要している場合であっても、全体サービスのレスポンス時間としては顕著な違いが出るほどでは無い場合、アラートは、低い緊急度として処理すれば良く、誰かの仕事を中断させる程のものではありません。これらのアラートは、後の考察や調査の資料として、監視システムに記録しておきます。結局のところ、ネットワークの高負荷のように一過性の問題は、自然に解消されることが多いからです。逆に、システムで膨大な量のタイムアウトが発生するなど、重大な問題が発生した場合は、今まで記録してきたデータが、調査のための貴重なコンテキストを提供することになります。

#### Alerts as notifications (moderate severity)

> The next tier of alerting urgency is for issues that do require intervention, but not right away. Perhaps the data store is running low on disk space and should be scaled out in the next several days. Sending an email and/or posting a notification in the service owner’s chat room is a perfect way to deliver these alerts—both message types are highly visible, but they won’t wake anyone in the middle of the night or disrupt an engineer’s flow.

アラートの次の緊急度レベルは、人間の介入は必要だが、今すぐにその対応が必要ないレベルの障害に対するものです。例えばデータストレージが使っているディスクの残量が不足ぎみで、数日以内には追加しなければならない場合です。メールを送信するか、サービスオーナーのチャットルームに通知をポストするのは、この種のアラートの最善の届け方です。この2つのメッセージタイプは、視認性は高いのですが、深夜に誰かを叩き起こすことはありませんし、エンジニアの思考を妨げることもありません。

#### Alerts as pages (high severity)

> The most urgent alerts should receive special treatment and be escalated to a page (as in “[pager](https://en.wikipedia.org/wiki/Pager)”) to urgently request human attention. Response times for your web application, for instance, should have an internal SLA that is at least as aggressive as your strictest customer-facing SLA. Any instance of response times exceeding your internal SLA would warrant immediate attention, whatever the hour.

最高の緊急性を要するアラートには、特別な扱いが必要で、人間の注目を直ちに引くために[ページャー(電話連絡やポケベル連絡の方法)](https://en.wikipedia.org/wiki/Pager)などにエスカレーションする必要があります。例えば、Webアプリケーションのレスポンス時間には、最低でも最も厳しい顧客を念頭に置いたSLAを設定するべきです。そして、この内部SLAの基準を超えるようなWebアプリケーションのレスポンス時間の増大には、どのような時間であっても、迅速な対応が必要です。

![](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-05-how-to-monitor/alerting101_2_band_1.png)

### When to let a sleeping engineer lie

> Whenever you consider setting an alert, ask yourself three questions to determine the alert’s level of urgency and how it should be handled:

アラートの設定を検討する際には、アラートの緊急性とそれがどのように処理されるべきかを決めるために、次の3つの項目を自分自身に質問して見ましょう。

> 1.	**Is this issue real?** It may seem obvious, but if the issue is not real, it usually should not generate an alert. The examples below can trigger alerts but probably are not symptomatic of real problems. Alerting—or, worse, paging—on occurrences such as these contributes to alert fatigue and can cause more serious issues to be ignored:
> 	-	Metrics in a test environment are out of bounds
> 	-	A single server is doing its work very slowly, but it is part of a cluster with fast-failover to other machines, and it reboots periodically anyway
> 	-	Planned upgrades are causing large numbers of machines to report as offline

> 	If the issue is indeed **real**, it should generate an alert. Even if the alert is not linked to a notification, it should be recorded within your monitoring system for later analysis and correlation.
> 2. **Does this issue require attention?** If you can reasonably automate a response to an issue, you should consider doing so. There is a very real cost to calling someone away from work, sleep, or personal time. If the issue is **real *and* it requires attention**, it should generate an alert that notifies someone who can investigate and fix the problem. At minimum, the notification should be sent via email, chat or a ticketing system so that the recipients can prioritize their response.
> 3. **Is this issue urgent?** Not all issues are emergencies. For example, perhaps a moderately higher than normal percentage of system responses have been very slow, or perhaps a slightly elevated share of queries are returning stale data. Both issues may need to be addressed soon, but not at 4:00 A.M. If, on the other hand, a key system stops doing its work at an acceptable rate, an engineer should take a look immediately. If the symptom is **real *and* it requires attention *and* it is urgent**, it should generate a page.

1.	**この障害は現実? (Is this issue real?)** 明白に聞こえるかもしれませんが、 障害が現実に発生していない場合には、普通はアラートを発生させるべきではありません。 以下の例では、アラートを発生させることはできますが、おそらく実際の障害の兆候ではないでしょう。このようなケースで、アラートを発生したり、ページングしたりすることは、 アラートに慣れてしまう原因になり、より深刻な無視という問題を引き起こします。
	-	テスト環境のメトリクスが規定値を超えた場合。
	-	ある1台のサーバーは非常にゆっくりと処理をしてるが、それ以外は高速に処理ができている。クラスターに含まれている場合。他のサーバーにフェールオーバーしている場合や再起動を繰り返している場合。
	-	計画的な更新により、大量のサーバーが停止の通知をしてきた場合。

	これらの障害が **事実** なら、アラートを発生させる必要はあるでしょう。アラートが通知にリンクされていないとしても、 これらは後の分析と連携のために監視システム内に記録しておくべきです。
2. **この障害には誰かの介入が必要? (Does this issue require attention?)** 合理的に可能であれば、障害に対する対応を自動化することも出来ます。そして、 実際は自動化することを検討するべきでしょう。誰かを仕事や睡眠やプライベート時間から呼び出すことは、現実のコストを要する行為です。起きている障害が **現実の障害で、人間の介入が必要** なら、障害を調査し修正を施せる人材に対し、 アラートを発生させ、通知する必要があるでしょう。その通知は、受信する人が優先順位を決められるように、最低でもメール、チャット、チケットシステムにより送信される必要があるでしょう。
3. **この障害は、緊急性を要するか? (Is this issue urgent?)** 全ての障害は、緊急事態ではありません。例えば、システムレスポンスが通常よりも若干時間を要していたり、古いデータで応答しているクエリが普段よりわずかに増加していたりしている状態が緊急度の低い障害です。このいずれの問題も対処する必要はありますが、午前4:00ではありません。その逆に、全体の要となるシステムが容認範囲の処理ができなくなった場合は、即座にエンジニアが対応する必要があるでしょう。**現実の障害で、人間の介入が必要、緊急性を要する** なら、ページするべきです。

![](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-05-how-to-monitor/alerting101_2_band_2.png)

### Page on symptoms

> Pages deserve special mention: they are extremely effective for delivering information, but they can be quite disruptive if overused, or if they are linked to poorly designed alerts. In general, a page is the most appropriate kind of alert when the system you are responsible for stops doing useful work with acceptable throughput, latency, or error rates. Those are the sort of problems that you want to know about immediately.

ページは、次に示すように特に重要です: ページは、情報を配信するのには非常に効果的です。しかし、使いすぎたり、正しく検討されていないアラートに紐ずいていたりすると、非常に破壊的です。一般的にページは、あなたが担当しているシステムが容認範囲内のスループット、レイテンシ、エラー率の **有益な仕事** をしなくなった時の適切なアラートです。これらは、直ちに知りたい障害の一種です。

> The fact that your system stopped doing useful work is a *symptom*—that is, it is a manifestation of an issue that may have any number of different *causes*. For example: if your website has been responding very slowly for the last three minutes, that is a symptom. Possible causes include high database latency, failed application servers, Memcached being down, high load, and so on. Whenever possible, build your pages around symptoms rather than causes. See our [companion article on data collection](https://www.datadoghq.com/blog/2015/06/monitoring-101-collecting-data/) for a metric framework that helps to separate symptoms from causes.

事実として、システムが **有益な仕事** をしなくなるのは、 **symptom** (徴候)です。それらの徴候は、複数の異なる原因を持っている可能性のある障害が発生する兆しです。例えば、直近3分のwebサイトのレスポンスが非常に遅い場合は、**symptom**(徴候)です。原因の可能性としては、データベースの問い合わせ時間が長くなっていたり、アプリケーションサーバーが停止していたり、Memcachedが停止していたり、高負荷が考えられるでしょう。従って、可能な限り、**casuse**(原因)ではなく、**symptom**(徴候)に基づいてページを設定しましょう。詳しくは、**symptom**(徴候)
と **casuse**(原因)の切り分けをするためのフレームワークに関するポスト [[companion article on data collection]](https://www.datadoghq.com/blog/2015/06/monitoring-101-collecting-data/) を参照してください。

> Paging on symptoms surfaces real, oftentimes user-facing problems, rather than hypothetical or internal problems. Contrast paging on a symptom, such as slow website responses, with paging on potential causes of the symptom, such as high load on your web servers. Your users will not know or care about server load if the website is still responding quickly, and your engineers will resent being bothered for something that is only internally noticeable and that may revert to normal levels without intervention.

徴候に基づいてページすることは、仮説的または内部的な問題よりも、ユーザーに直面している実障害を表面化させます。「Webサイトの応答が遅い」という **symptom**(徴候)に基づいたページと、「Webサーバーが高負荷になった」という **cause**(原因)の可能性に基づいたページという対比では、Webサイトが素早く応答していれば、サーバーが高負荷状態にあることなど、ユーザーは気もつかないし、気にもかけません。そしてエンジニアは、内部的にしか分からない、放置しておけば元に戻ってしまうような *こと* に憤慨することはないでしょう。

#### Durable alert definitions

> Another good reason to page on symptoms is that symptom-triggered alerts tend to be durable. This means that regardless of how underlying system architectures may change, if the system stops doing work as well as it should, you will get an appropriate page even without updating your alert definitions.

徴候に基づいてページするもう一つの良い理由は、徴候に基づいたアラートは、長持ちする傾向があります。基盤システムに変化が有ろうが無かろうが、もしもシステムが **期待している仕事** をしなくなったら、アラート設定を更新していなくても適切なページを受けることができます。

![](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-05-how-to-monitor/alerting101_2_band_3.png)

#### Exception to the rule: Early warning signs

> It is sometimes necessary to call human attention to a small handful of metrics even when the system is performing adequately. Early warning metrics reflect an unacceptably high probability that serious symptoms will soon develop and require immediate intervention.

システムが適切に機能していても、時には、幾つかのメトリクスに対し人間の注意を喚起することが必要な場合があります。早期警戒目的のメトリクスは、容認できない重篤な状態への徴候が、まっもなく発生する前兆で、人間の迅速な介入を必要とするからです。

> Disk space is a classic example. Unlike running out of free memory or CPU, when you run out of disk space, the system will not likely recover, and you probably will have only a few seconds before your system hard stops. Of course, if you can notify someone with plenty of lead time, then there is no need to wake anyone in the middle of the night. Better yet, you can anticipate some situations when disk space will run low and build automated remediation based on the data you can afford to erase, such as logs or data that exists somewhere else.

ディスクの空き容量は、典型的な例です。空きメモリやCPUとは異なり、ディスクの空き容量が無くなると、システムはその状態から自動で復帰することは期待できません。そしてシステムが停止するまでに数秒しかないでしょう。もちろん、長いリードタイムをとって誰かに通知することもできるでしょう。そうすれば、誰も夜中に叩き起こす必要はないでしょう。もっと良い方法は、ディスクの空き容量が少なくなった時のことを予想し、ログや既に退避済みのデータなど失っても良いデータを自動で削除するという回避策を講じておくことです。

## Conclusion: Get serious about symptoms

> -	Send a page only when symptoms of urgent problems in your system’s work are detected, or if a critical and finite resource limit is about to be reached.
> -	Set up your monitoring system to record alerts whenever it detects real issues in your infrastructure, even if those issues have not yet affected overall performance.

- システム内に緊急性の高い問題の徴候が検知された時、又は、重大な危機を発生させる要素を持った有限なリソースの限界が近い場合にページを送信します。
- まだ全体のパフォーマンスに影響を与えていない場合でも、インフラ内で考慮するべき問題をアラートが検知した際は、そのアラートを記録するように監視システムを設定しておきます。

> We would like to hear about your experiences as you apply this framework to your own monitoring practice. If it is working well, please [let us know on Twitter](https://twitter.com/datadoghq)! Questions, corrections, additions, complaints, etc? Please [let us know on GitHub](https://github.com/DataDog/the-monitor).

独自に実践していた監視体制に、このフレームワークで学んだことを取り入れ、新たな監視体制に取り組んだ体験を是非お聞かせください。 フレームワークを取り入れることによって監視が改善された場合は、Twitterで[@datadoghq](https://twitter.com/datadoghq)付きでつぶやいていただけると幸いです。また、質問、修正、追加、苦情、その他がある場合は、[Github](https://github.com/DataDog/the-monitor)のissueにて連絡してください。
