Monitoring 101: Alerting on what matters
===================================================

> *This post is part of a series on effective monitoring. Be
sure to check out the rest of the series: [Collecting the right data](/blog/monitoring-101-collecting-data/) and [Investigating performance issues](/blog/monitoring-101-investigation/).*

*このポストは、「効果的な監視: Monitoring 101」シリーズの一部です。このポスト内容他に、[Collecting the right data](/blog/monitoring-101-collecting-data/) と [Investigating performance issues](/blog/monitoring-101-investigation/) も、合わせて目を通すことをお勧めします。*

> Automated alerts are essential to monitoring. They allow you to spot
problems anywhere in your infrastructure, so that you can rapidly
identify their causes and minimize service degradation and disruption.

監視システムには、自動化されたアラート通知は不可欠です。
自動化されたアラートによってインフラに起きている問題に気づき、大至急で問題の原因を見つけ出し、
サービスの質の低下や中断を最小に抑えることができます。

> But alerts aren’t always as effective as they could be. In particular,
real problems are often lost in a sea of noisy alarms. This article
describes a simple approach to effective alerting, regardless of the
scale of the systems involved. In short:

> 1.  Alert liberally; page judiciously
> 2.  Page on symptoms, rather than causes

しかしアラートは、それらの本来の意図と反し、有効でない時もあります。
特に、頻繁にアラームが押し寄せる状態では、本当に対処しなくてはならない問題も無視されることが多々有ります。
この記事では、効果的にアラートを発生させるためのシンプルなアプローチについて解説します。

要するに：
1. 自由にアラートを設定するも、**page** に関しては正当性を十分に検討する!
2. 原因ではなく、症状を基に **page** をする。

> This series of articles comes out of our experience monitoring
large-scale infrastructure for [our
customers](https://www.datadoghq.com/customers/). It also draws on the
work of [Brendan Gregg](http://dtdg.co/use-method), [Rob
Ewaschuk](http://dtdg.co/philosophy-alerting), and [Baron
Schwartz](http://dtdg.co/metrics-attention).

このシリーズの内容は、Datadogが[お客様](https://www.datadoghq.com/customers/)の大規模インフラを監視してきた経験を基にし、次に紹介するような人たちのブログ記事　[Brendan Gregg](http://dtdg.co/use-method)、 [Rob
Ewaschuk](http://dtdg.co/philosophy-alerting)、 [Baron
Schwartz](http://dtdg.co/metrics-attention) を参照して構成しています。

When to alert someone (or no one)
-------------------------------------------

![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-05-how-to-monitor/alerting101_2_chart.png)

> An alert should communicate something specific about your systems in
plain language: “Two Cassandra nodes are down” or “90% of all web
requests are taking more than 0.5s to process and respond.”　Automating
alerts across as many of your systems as possible allows you to respond
quickly to issues and provide better service, and it also saves time by
freeing you from continual manual inspection of metrics.

アラートでは、システムで起きている内容を具体的で明確な言葉で伝える必要があります。例えば、"Cassandraのノードが2台停止ている"とか"webへのリクエストの90%が、プロセスと回答に0.5秒以上の時間を要している"というようになります。可能な限り多くのシステムでアラートを自動化することで、障害に対し迅速に対応できるようになり、より良いサービスを提供できるようになり、更に、継続的なメトリクスの手動による検査から解放されることにより、時間を節約することもできるようになります。

### Levels of alerting urgency

> Not all alerts carry the same degree of urgency. Some require immediate
human intervention, some require eventual human intervention, and some
point to areas where attention may be needed in the future. All alerts
should, at a minimum, be logged to a central location for easy
correlation with other metrics and events.

全てのアラートが同じ緊急度合を求めてはいません。一部のものは即時の人間による介入を必要し、いくつかもものは結果として人間による介入を必要とし、そしていくつかは将来的に気を気張って対応しなくてはならない領域を指摘しています。全てのアラートは、必要最低限で、どこか一箇所の所に記録され、他のメトリクスやイベントと連携できるようになっているべきです。

#### Alerts as records (low severity)

> Many alerts will not be associated with a service problem, so a human
may never even need to be aware of them. For instance, when a data store
that supports a user-facing service starts serving queries much slower
than usual, but not slow enough to make an appreciable difference in the
overall service’s response time, that should generate a low-urgency
alert that is recorded in your monitoring system for future reference or
investigation but does not interrupt anyone’s work. After all, transient
issues that could be to blame, such as network congestion, often go away
on their own. But should a significant issue develop—say, if the service
starts returning a large number of timeouts—that alert-based data will
provide invaluable context for your investigation.


Many alerts will not be associated with a service problem,
so a human　may never even need to be aware of them.

For instance, when a data store that supports a user-facing service starts serving queries much slower than usual,

but not slow enough to make an appreciable difference in the
overall service’s response time,

that should generate a low-urgency alert that is recorded in your monitoring system for future reference or investigation but does not interrupt anyone’s work.

After all, transient issues that could be to blame, such as network congestion, often go away
on their own.

But should a significant issue develop—say, if the service starts returning a large number of timeouts—that alert-based data will provide invaluable context for your investigation.

多くのアラートは、サービスに障害に紐付いています。


例えば、データストーレジが

多くのアラートは、サービスの問題に関連するので、人間がされることはありません
でもそれらを意識する必要がないかもしれません。たとえば、ときに、データストア
それは、ユーザ側のサービスが提供するクエリはるかに遅いを開始サポート
通常よりますが、中にかなりの違いを確認するのに十分遅くありません
全体的なサービスの応答時間は、それが低緊急度を生成する必要があります
それが今後の参考のためにお使いの監視システムに記録されている警告や
調査が、誰の仕事が中断されることはありません。結局のところ、過渡
このようなネットワークの輻輳などのせいにすることができた問題は、多くの場合、離れて行きます
自分で。しかし、重要な問題は、サービスがあれば開発、言う必要があります
そのタイムアウト·アラート·ベースのデータが多数をします返す開始
あなたの調査のための非常に貴重なコンテキストを提供します。


#### Alerts as notifications (moderate severity)

> The next tier of alerting urgency is for issues that do require
intervention, but not right away. Perhaps the data store is running low
on disk space and should be scaled out in the next several days. Sending
an email and/or posting a notification in the service owner’s chat room
is a perfect way to deliver these alerts—both message types are highly
visible, but they won’t wake anyone in the middle of the night or
disrupt an engineer’s flow.

The next tier of alerting urgency is for issues that do require
intervention, but not right away. Perhaps the data store is running low
on disk space and should be scaled out in the next several days. Sending
an email and/or posting a notification in the service owner’s chat room
is a perfect way to deliver these alerts—both message types are highly
visible, but they won’t wake anyone in the middle of the night or
disrupt an engineer’s flow.

緊急性を警告する次の層は必要ない問題のためであります
介入ではなく、すぐに。おそらく、データ·ストアは、不足しています
ディスク容量にし、次の数日間にスケールアウトする必要があります。送信
電子メールおよび/またはサービス所有者のチャットルームでの通知を掲示
これらの配信に最適な方法であるアラートは、両方のメッセージタイプは非常にあります
目に見える、彼らは夜中に誰も目を覚ますしませんが、または
エンジニアの流れを破壊します。

#### Alerts as pages (high severity)

> The most urgent alerts should receive special treatment and be escalated
to a page (as in “[pager](https://en.wikipedia.org/wiki/Pager)”) to
urgently request human attention. Response times for your web
application, for instance, should have an internal SLA that is at least
as aggressive as your strictest customer-facing SLA. Any instance of
response times exceeding your internal SLA would warrant immediate
attention, whatever the hour.

The most urgent alerts should receive special treatment and be escalated
to a page (as in “[pager](https://en.wikipedia.org/wiki/Pager)”) to
urgently request human attention. Response times for your web
application, for instance, should have an internal SLA that is at least
as aggressive as your strictest customer-facing SLA. Any instance of
response times exceeding your internal SLA would warrant immediate
attention, whatever the hour.

最も緊急アラートは、特別な治療を受けるべきであり、エスカレートします
（のように"[ページャ]（https://en.wikipedia.org/wiki/Pager）」）のページへへ
早急に人間の注意を要求します。あなたのWebのための応答時間
アプリケーション、例えば、少なくともある内部SLAを持つ必要があります
あなたの最も厳しい顧客向けSLAのように積極的。の任意のインスタンス
応答時間内部SLAが即時保証だろう超えます
注意、どんな時間。


![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-05-how-to-monitor/alerting101_2_band_1.png)

### When to let a sleeping engineer lie

Whenever you consider setting an alert, ask yourself three questions to
determine the alert’s level of urgency and how it should be handled:

1.  **Is this issue real?** It may seem obvious, but if the issue is not
    real, it usually should not generate an alert. The examples below
    can trigger alerts but probably are not symptomatic of real
    problems. Alerting—or, worse, paging—on occurrences such as these
    contributes to alert fatigue and can cause more serious issues to be
    ignored:
    -   Metrics in a test environment are out of bounds
    -   A single server is doing its work very slowly, but it is part of
        a cluster with fast-failover to other machines, and it reboots
        periodically anyway
    -   Planned upgrades are causing large numbers of machines to report
        as offline

    If the issue is indeed **real**, it should generate an alert. Even
    if the alert is not linked to a notification, it should be recorded
    within your monitoring system for later analysis and correlation.
2.  **Does this issue require attention?** If you can reasonably
    automate a response to an issue, you should consider doing so. There
    is a very real cost to calling someone away from work, sleep, or
    personal time. If the issue is **real *and* it requires attention**,
    it should generate an alert that notifies someone who can
    investigate and fix the problem. At minimum, the notification should
    be sent via email, chat or a ticketing system so that the recipients
    can prioritize their response.
3.  **Is this issue urgent?** Not all issues are emergencies. For
    example, perhaps a moderately higher than normal percentage of
    system responses have been very slow, or perhaps a slightly elevated
    share of queries are returning stale data. Both issues may need to
    be addressed soon, but not at 4:00 A.M. If, on the other hand, a key
    system stops doing its work at an acceptable rate, an engineer
    should take a look immediately. If the symptom is **real *and* it
    requires attention *and* it is urgent**, it should generate a page.

![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-05-how-to-monitor/alerting101_2_band_2.png)

### Page on symptoms

Pages deserve special mention: they are extremely effective for
delivering information, but they can be quite disruptive if overused, or
if they are linked to poorly designed alerts. In general, a page is the
most appropriate kind of alert when the system you are responsible for
stops doing useful work with acceptable throughput, latency, or error
rates. Those are the sort of problems that you want to know about
immediately.

The fact that your system stopped doing useful work is a *symptom*—that
is, it is a manifestation of an issue that may have any number of
different *causes*. For example: if your website has been responding
very slowly for the last three minutes, that is a symptom. Possible
causes include high database latency, failed application servers,
Memcached being down, high load, and so on. Whenever possible, build
your pages around symptoms rather than causes. See our [companion article
on data collection](https://www.datadoghq.com/blog/2015/06/monitoring-101-collecting-data/) for a metric framework that helps to separate
symptoms from causes.

Paging on symptoms surfaces real, oftentimes user-facing problems,
rather than hypothetical or internal problems. Contrast paging on a
symptom, such as slow website responses, with paging on potential causes
of the symptom, such as high load on your web servers. Your users will
not know or care about server load if the website is still responding
quickly, and your engineers will resent being bothered for something
that is only internally noticeable and that may revert to normal levels
without intervention.

#### Durable alert definitions

Another good reason to page on symptoms is that symptom-triggered alerts
tend to be durable. This means that regardless of how underlying system
architectures may change, if the system stops doing work as well as it
should, you will get an appropriate page even without updating your
alert definitions.

![](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-05-how-to-monitor/alerting101_2_band_3.png)

#### Exception to the rule: Early warning signs

It is sometimes necessary to call human attention to a small handful of
metrics even when the system is performing adequately. Early warning
metrics reflect an unacceptably high probability that serious symptoms
will soon develop and require immediate intervention.

Disk space is a classic example. Unlike running out of free memory or
CPU, when you run out of disk space, the system will not likely recover,
and you probably will have only a few seconds before your system hard
stops. Of course, if you can notify someone with plenty of lead time,
then there is no need to wake anyone in the middle of the night. Better
yet, you can anticipate some situations when disk space will run low and
build automated remediation based on the data you can afford to erase,
such as logs or data that exists somewhere else.

## Conclusion: Get serious about symptoms

-   Send a page only when symptoms of urgent problems in your system’s
    work are detected, or if a critical and finite resource limit is
    about to be reached.
-   Set up your monitoring system to record alerts whenever it detects
    real issues in your infrastructure, even if those issues have not
    yet affected overall performance.

We would like to hear about your experiences as you apply this framework
to your own monitoring practice. If it is working well, please [let us
know on Twitter](https://twitter.com/datadoghq)! Questions, corrections,
additions, complaints, etc? Please [let us know on
GitHub](https://github.com/DataDog/the-monitor).
