Monitoring 101: Collecting the right data
====================================================

> *This post is part of a series on effective monitoring. Be sure to check out the rest of the series: [Alerting on what matters](/blog/monitoring-101-alerting/) and [Investigating performance issues](/blog/monitoring-101-investigation/).*

*このポストは、「効果的な監視: Monitoring 101」シリーズの一部です。このポスト内容に続いて、[Alerting on what matters](/blog/monitoring-101-alerting/) と [Investigating performance issues](/blog/monitoring-101-investigation/) も、合わせて目を通すことをお勧めします。*

> Monitoring data comes in a variety of forms — some systems pour out data
continuously and others only produce data when rare events occur. Some
data is most useful for *identifying* problems; some is primarily
valuable for *investigating* problems. This post covers which data to
collect, and how to classify that data so that you can:

> 1.  Receive meaningful, automated alerts for potential problems
> 2.  Quickly investigate and get to the bottom of performance issues

> Whatever form your monitoring data takes, the unifying theme is this:

>> Collecting data is cheap, but not having it when you need it can be
>> expensive, so you should instrument everything, and collect all the
> useful data you reasonably can.

> This series of articles comes out of our experience monitoring
> large-scale infrastructure for [our
> customers](https://www.datadoghq.com/customers/). It also draws on the
> work of [Brendan Gregg](http://dtdg.co/use-method), [Rob
> Ewaschuk](http://dtdg.co/philosophy-alerting), and [Baron
> Schwartz](http://dtdg.co/metrics-attention).

監視データは色々なところから送られていきます。あるシステムは、監視データを連続して送信し続けます。別の監視システムでは、特定のイベントが発生したときデータを送信します。あるデータは、問題を特定するのに非常に役に立ちます。又あるデータは、問題の調査過程で意味を持つものもあります。このポストでは、次の項目を実現するために、どのデータを収集し、分類するかを説明していきます。

1. 自動検知により、潜在的な問題に関し効果的なアラートを受信する。
2. 迅速に調査を進行し、パフォーマンスに関する問題の原因に到達する。

監視データがどのような形態になっていようと、今回のポストのテーマは以下になります:

> データの収集は、ローコストで実現できます。しかし、必要なデータを持っていない状況での損失は非常に大きい(高価)です。従って全てをうまく調整し、合理的と判断できる範囲で、全ての価値のあるデータを収集する。

このシリーズの内容は、Datadogが[お客様](https://www.datadoghq.com/customers/)の大規模インフラを監視してきた経験を基に、次に紹介する人たちのブログ記事　[Brendan Gregg](http://dtdg.co/use-method)、 [Rob
Ewaschuk](http://dtdg.co/philosophy-alerting)、 [Baron
Schwartz](http://dtdg.co/metrics-attention) を参照して構成しています。

![](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-05-how-to-monitor/alerting101_band_1.png)

### Metrics

> Metrics capture a value pertaining to your systems *at a specific point
> in time* — for example, the number of users currently logged in to a web
> application. Therefore, metrics are usually collected once per second,
> one per minute, or at another regular interval to monitor a system over
> time. There are two important categories of metrics in our framework:
> work metrics and resource metrics. For each system that is part of your
> software infrastructure, consider which work metrics and resource
> metrics are reasonably available, and collect them all.

メトリクスは、そのシステムが *ある時点で* 持っている価値を数値化します。(例えば、webのアプリケーションに現在ログインしているユーザー数)　従って、メトリクスは、通常1秒に1回や1分間に1回、又は他の定期的な間隔で収集されます。私たちのメトリクスの捉え方には、2つの重要なカテゴリーがあります。それらは、**work metrics** と **resource metorics** です。あなたのソフトウェアインフラを構成している各システムで、どのような **work metrics** と **resource metorics** が無理をしない範囲で収集出来るかを検討し、全てを収集するようにします。

![](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-05-how-to-monitor/alerting101_chart_1.png)

#### Work metrics

Work metrics indicate the top-level health of your system by measuring
its useful output. When considering your work metrics, it’s often
helpful to break them down into four subtypes:

Work metricsは、運用しているシステム上で動作しているサービスのパフォーマンスを表しています。
Work metoricsを検討する際は、メトリクスを次の4つのサブタイプに分類すると検討が容易になります:

> -   **throughput** is the amount of work the system is doing per
    unit time. Throughput is usually recorded as an absolute number.
> -   **success** metrics represent the percentage of work that was
    executed successfully.
> -   **error** metrics capture the number of erroneous results, usually
    expressed as a rate of errors per unit time or normalized by the
    throughput to yield errors per unit of work. Error metrics are often
    captured separately from success metrics when there are several
    potential sources of error, some of which are more serious or
    actionable than others.
> -   **performance** metrics quantify how efficiently a component is
    doing its work. The most common performance metric is latency, which
    represents the time required to complete a unit of work. Latency can
    be expressed as an average or as a percentile, such as “99% of
    requests returned within 0.1s”.

- **throughput** は、システムが一定時間内に処理している仕事量になります。一般的にthuroughputは、絶対値として記録されています。
- **success** メトリクスは、正しく実行された仕事の割合(パーセンテージ）を表します。
- **error** メトリクスは、誤った結果の数を表します。通常は、単位時間当たりのエラー発生率として表現されるか、throughputを使って正規化しエラー数/仕事量で表現します。エラーの発生源の幾つかは、深刻であったり、アクションが起こしやすかったりします。従って、エラーの発生源が複数有る場合、errorメトリクスはsuccessメトリクスとは別に収集されることが多いです。
- **performance** メトリクスは、コンポーネントがどれくらい効率的に動作しているかを定量化しています。最も一般的なperformaceメトリクスは、一単位の仕事を終了する必要な時間であるレイテンシです。レイテンシは、次の様に平均値やパーセンテージで表現することができます。"99%のリクエストは0.1秒以内に応答した。"

> Below are example work metrics of all four subtypes for two common kinds
> of systems: a web server and a data store.

以下は、webサーバとデータストレージという一般的なシステム部品についてwork metricsの4サブタイプを検討した例です。

> **Example work metrics: Web server (at time 2015-04-24 08:13:01 UTC)**

> | **Subtype** | **Description**                                              | **Value** |
> |-------------|--------------------------------------------------------------|-----------|
> | throughput  |  requests per second                                         | 312       |
> | success     |  percentage of responses that are 2xx since last measurement | 99.1      |
> | error       |  percentage of responses that are 5xx since last measurement | 0.1       |
> | latency     |  90th percentile response time in seconds                    | 0.4       |

**[例] work metrics: Web server (at time 2015-04-24 08:13:01 UTC)**

| **サブタイプ** | **説明**                                             　　　 | **値** |
|-------------|--------------------------------------------------------------|-----------|
| throughput  |  リクエスト数 / 秒                         　　                 | 312       |
| success     |  前回の計測時からの、結果コード2xxのレスポンスのパーセンテージ　　　　　　| 99.1      |
| error       |  前回の計測時からの、結果コード5xxのレスポンスのパーセンテージ　        | 0.1       |
| latency     |  レスポンス時間で90パーセンタイルに位置する時間　                   | 0.4       |

> **Example work metrics: Data store (at time 2015-04-24 08:13:01 UTC)**

> | **Subtype** | **Description**                                                    | **Value** |
> |-------------|--------------------------------------------------------------------|-----------|
> | throughput  | queries per second                                                 | 949       |
> | success     | percentage of queries successfully executed since last measurement | 100       |
> | error       | percentage of queries yielding exceptions since last measurement   | 0         |
> | error       | percentage of queries returning stale data since last measurement  | 4.2       |
> | latency     | 90th percentile query time in seconds                              | 0.02      |

**[例] work metrics: Data store (at time 2015-04-24 08:13:01 UTC)**

| **サブタイプ** | **説明**                                                    | **値** |
|-------------|--------------------------------------------------------------|-----------|
| throughput  | リクエスト数 / 秒                                           　  | 949       |
| success     | 前回の計測時からの、成功したクエリーコールのパーセンテージ　　　　　　　 | 100       |
| error       | 前回の計測時からの、エクセプションを返したクエリーのパーセンテージ　　 | 0         |
| error       | 前回の計測時からの、古いデータを返したクエリーのパーセンテージ　  　　　| 4.2       |
| latency     | クエリー時間で90パーセンタイルに位置する時間                        | 0.02      |

#### Resource metrics

> Most components of your software infrastructure serve as a resource to
> other systems. Some resources are low-level—for instance, a server’s
> resources include such physical components as CPU, memory, disks, and
> network interfaces. But a higher-level component, such as a database or
> a geolocation microservice, can also be considered
> a resource if another system requires that component to produce work.

ソフトウェアインフラの構成部品のほとんどは、他のシステムのリソースとして機能しています。リソースの一部は、低レベルコンポーネントです。インスタンスの基礎の部分にあたる物理コンポーネントのリソースとしてCPU、メモリ、ディスク、ネットワークインターフェイスなどが該当します。その反対に、高レベルコンポーネントがリソースとして考えられることもあります。データベースや、ジオロケーションのマイクロサービスの結果を基に、運用しているシステムが結果を計算しているなら、高レベルのリソースに該当します。

> Resource metrics are especially valuable for investigation and diagnosis
> of problems. For each resource in your system, try to collect metrics
> that cover four key areas:

リソースメトリクスは、問題の調査や診断に特に価値があります。システム内の各リソースについて、次の４つの主要分野をカバーできるようにメトリクスを収集できる様にします:

> 1.  **utilization** is the percentage of time that the resource is busy,
>      or the percentage of the resource’s capacity that is in use.
> 2.  **saturation** is a measure of the amount of requested work that the
>     resource cannot yet service, often queued.
> 3.  **errors** represent internal errors that may not be observable in
>     the work that the resource produces.
> 4.  **availability** represents the percentage of time that the resource
>    responded to requests. This metric is only well-defined for
>    resources that can be actively and regularly checked
>    for availability.

1. **utilization** は、リソースがビジーな時間のパーセンテージ、または、使用中のリソースの容量のパーセンテージです。
2. **saturation** は、キュー待ちの状態など、処理を待っているリクエスト仕事の量を表します。
3. **errors** は、リソースが生成する仕事で観察不能かもしれない内部エラーを表します。
4. **availability** は、リソースがリクエストに応答した時間のパーセンテージを表します。このメトリクスは、リソースのavailabilityについて積極的かつ定期的にチェックを実施していいる場合についてのみ明確に定義できます。

> Here are example metrics for a handful of common resource types:

以下は、一般的なリソース·タイプのメトリクスの例です:

> | **Resource** | **Utilization**                                       | **Saturation**       | **Errors**                                   | **Availability**             |
> |--------------|-------------------------------------------------------|----------------------|----------------------------------------------|------------------------------|
> | Disk IO      | % time that device was busy                           | wait queue length    | \# device errors                             | % time writable              |
> | Memory       | % of total memory capacity in use                     | swap usage           | N/A (not usually observable)                 | N/A                          |
> | Microservice | average % time each request-servicing thread was busy | \# enqueued requests | \# internal errors such as caught exceptions | % time service is reachable  |
> | Database     | average % time each connection was busy               | \# enqueued queries  | \# internal errors, e.g. replication errors  | % time database is reachable |


| **リソース** | **Utilization**                                       | **Saturation**       | **Errors**                                   | **Availability**             |
|--------------|-------------------------------------------------------|----------------------|----------------------------------------------|------------------------------|
| Disk IO      | % time that device was busy                           | キュー待ちリストの長さ    | \# device errors                             | % time writable              |
| Memory       | % of total memory capacity in use                     | swap usage           | N/A (not usually observable)                 | N/A                          |
| Microservice | average % time each request-servicing thread was busy | \# enqueued requests | \# internal errors such as caught exceptions | % time service is reachable  |
| Database     | average % time each connection was busy               | \# enqueued queries  | \# internal errors, e.g. replication errors  | % time database is reachable |


### Other metrics

> There are a few other types of metrics that are neither work nor
> resource metrics, but that nonetheless may come in handy in diagnosing
> causes of problems. Common examples include counts of cache hits or
> database locks. When in doubt, capture the data.

workメトリクスにもリソースメトリクスにも属さない別のタイプのメトリクスがあります。
この別のタイプのメトリクスは、問題の原因を診断する際に非常に重宝することがあります。
キャッシュヒット数またはデータベースロック数などが、代表的な例です。
何か疑問に思うことがあるときは、このタイプのデータを取っておくと良いでしょう。

### Events

> In addition to metrics, which are collected more or less continuously,
> some monitoring systems can also capture events: discrete, infrequent
> occurrences that can provide crucial context for understanding what
> changed in your system’s behavior.

> Some examples:

メトリクスに加え、監視システムはイベント情報を収集していることがあります。
イベント情報は、メトリクスよりは非連続的に収集されています。
イベント情報は、システムの振る舞いの変化の原因を理解するため、個別のめったに起こらない重要なコンテキスト情報です。

以下が例です:

> - Changes: Internal code releases, builds, and build failures
> - Alerts: Internally generated alerts or third-party notifications
> - Scaling events: Adding or subtracting hosts

- **Changes** : 内部で実施したコードリリース、ビルドの実施およびビルドの失敗
- **Alerts** : 内部で派生または生成したアラートや第三者から受け取った通知
- **Scaling events** : ホストの追加や削除

> An event usually carries enough information that it can be interpreted
> on its own, unlike a single metric data point, which is generally only
> meaningful in context. Events capture *what happened*, at a point in
> *time*, with optional *additional information*. For example:

文脈的に把握するメトリクスのデータポイントと異なり、イベント情報は、通常独自に解釈するのに十分な情報を内包しています。イベント情報は、*どの時点* で *何が起きた* のかを、*付随情報*　と共に記録します。

例えば:

> | **What happened**                     | **Time**                | **Additional information** |
> |---------------------------------------|-------------------------|----------------------------|
> | Hotfix f464bfe released to production | 2015–05–15 04:13:25 UTC | Time elapsed: 1.2 seconds  |
> | Pull request 1630 merged              | 2015–05–19 14:22:20 UTC | Commits: ea720d6           |
> | Nightly data rollup failed            | 2015–05–27 00:03:18 UTC | Link to logs of failed job |

| **何が起きたのか**                     | **時間**                | **付随情報** |
|---------------------------------------|-------------------------|----------------------------|
| Hotfix f464bfe released to production | 2015–05–15 04:13:25 UTC | Time elapsed: 1.2 seconds  |
| Pull request 1630 merged              | 2015–05–19 14:22:20 UTC | Commits: ea720d6           |
| Nightly data rollup failed            | 2015–05–27 00:03:18 UTC | Link to logs of failed job |

> Events are sometimes used to generate alerts—someone should be
> notified of events such as the third example in the table above, which
> indicates that critical work has failed. But more often they are used to
> investigate issues and correlate across systems. In general, think of
> events like metrics—they are valuable data to be collected wherever it
> is feasible.

折につけイベント情報は、アラートを発生させるために使われることがあります。上の表の第三の例のように危機的な状況を起こし得ない作業の失敗イベントに関しては、誰かが通知を受けている必要があります。しかし多くのケースでは、障害の原因調査やシステムの他の情報と相互に関連付けシステムの状態を理解するのに利用します。一般的に、イベント情報もメトリクスと同じように、収集可能な範囲で集めておくべき価値のあるデータと考えます。

![](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-05-how-to-monitor/alerting101_band_3.png)

### What good data looks like

> The data you collect should have four characteristics:

収集するデータは、次のような四つ性格を持っている必要があります:

> -   **Well-understood.** You should be able to quickly determine how
>    each metric or event was captured and what it represents. During an
>    outage you won’t want to spend time figuring out what your
>    data means. Keep your metrics and events as simple as possible, use
>    standard concepts described above, and name them clearly.
>-   **Granular.** If you collect metrics too infrequently or average
>    values over long windows of time, you may lose important information
>    about system behavior. For example, periods of 100% resource
>    utilization will be obscured if they are averaged with periods of
>    lower utilization. Collect metrics for each system at a frequency
>    that will not conceal problems, without collecting so often that
>    monitoring becomes perceptibly taxing on the system (the [observer
>    effect](https://en.wikipedia.org/wiki/Observer_effect_(information_technology)))
>    or creates noise in your monitoring data by sampling time intervals
>    that are too short to contain meaningful data.
>-   **Tagged by scope.** Each of your hosts operates simultaneously in
>    multiple scopes, and you may want to check on the aggregate health
>    of any of these scopes, or their combinations. For example: how is
>    production doing in aggregate? How about production in the Northeast
>    U.S.? How about a particular software/hardware combination? It is
>    important to retain the multiple scopes associated with your data so
>    that you can alert on problems from any scope, and quickly
>    investigate outages without being limited by a fixed hierarchy
>    of hosts.
>-   **Long-lived.** If you discard data too soon, or if after a period
>    of time your monitoring system aggregates your metrics to reduce
>    storage costs, then you lose important information about what
>    happened in the past. Retaining your raw data for a year or more
>    makes it much easier to know what “normal” is, especially if your
>    metrics have monthly, seasonal, or annual variations.

- **Well-understood(よく理解されている)**　メトリクスを取集している者が、各イベントやイベントが、何を表現し、どのように記録されているかを瞬時に見極めることができる必要があります。障害が発生している状態では、それぞれのデータがどのような意味を持っているかを考え出すのに費やす時間はありません。上で紹介したコンセプトに基づき、収集しているメトリクスとイベントを、できる限り簡単で分かりやすい名前をつけるようにします。
- **Granular(適切な情報収集間隔)** 開きすぎた間隔でメトリクスを収集したり、または長時間に渡る変化の平均値を収集している場合は、システムの挙動に関する重要な情報を取り損ねているかもしません。例えば、リソース使用率の低い期間と一緒に平均化されてると、リソースが100%利用されている期間は、はっきりわからない状態になってしまいます。メトリクスの収集は、システムが抱えている問題を見逃さない周期で実行する必要があります。しかしこの周期は、監視負荷の影響をシステムに与えない範囲(the [observer
effect](https://en.wikipedia.org/wiki/Observer_effect_(information_technology)))で、かつ周期を短くすることによりノイズが増加し、データの本来の意味を損なってしまうことのないようにする必要があります。
- **Tagged by scope(スコープに基づいたタグ付け)** 各ホストは、異なったスコープを持ちつつ並行して動作しています。そして、どれかのスコープまたは複数のスコープのコンビネーションを基にホストを集約して健康状態を把握したいものです。例えば、ホスト全部で考えた場合、プロダクション環境はどのような状態にあるのか？米国東海岸で考えた場合、どのような状態にあるのか？特定のソフトウェア/ハードウェアの組み合わせはどうなのか？異なる切り口のスコープに基づいた障害でアラートを発生させ、固定階層化されたホスト構造に制限されることなく、供給停止(障害)状態の迅速な対処作業ができる様にするためにも、収集しているデータと複数のスコープの関連性を保つことは重要です。
- **Long-lived(長い保存期間)** あまりにも早期にデータを破棄したり、メトリクスの保存コストを削減するために一定期期間経過後にデータポイントを集約する加工をしたりすると、過去の経過として収集した重要な情報を失うことになります。特に、年やシーズンや月でメトリクスが変動する場合は、1年以上の生データを保存しておくことにより、正常範囲を把握することが容易になります。

### Data for alerts and diagnostics

> The table below maps the different data types described in this article
> to different levels of alerting urgency outlined [in a companion post](https://www.datadoghq.com/blog/2015/06/monitoring-101-alerting/). In
> short, a *record* is a low-urgency alert that does not notify anyone
> automatically but is recorded in a monitoring system in case it becomes
> useful for later analysis or investigation. A *notification* is a
> moderate-urgency alert that notifies someone who can fix the problem in
> a non-interrupting way such as email or chat. A *page* is an urgent
> alert that interrupts a recipient’s work, sleep, or personal time,
> whatever the hour. Note that depending on severity, a notification may
> be more appropriate than a page, or vice versa:

以下の表では、この記事で紹介した各タイプのメトリクスデータとアラートの方法と緊急度合いをマッピングしています。[[関連記事]](https://www.datadoghq.com/blog/2015/06/monitoring-101-alerting/)
*record* は、緊急性の低いアラートです。*record* の場合、誰かに自動的に通知されることはないですが、後の解析や障害調査の時のために監視システムに記録されます。
*notification* は、緊急性が中程度のアラートです。*notification* の場合、メールやチャットのような強制的中断を要求しないような方法を使い、問題を解決することができる人材に通知します。
*page* は、電話やポケベルなどの連絡で、緊急性の高いアラートです。*page* は、通知を受ける人の仕事、睡眠、プイラベートなどの時間に関係なく、どのような時間にも割り込んできます。ここで注意しなくてはならないことは、問題の重要度によっては *page* ではなく *notification* を採用する方が的確な場合があるということです。(あるいは、その逆もあります。)

> | **Data**                      | **Alert**    | **Trigger**                                                                         |
> |-------------------------------|--------------|-------------------------------------------------------------------------------------|
> | Work metric: Throughput       | Page         | value is much higher or lower than usual, or there is an anomalous rate of change   |  
> | Work metric: Success          | Page         | the percentage of work that is successfully processed drops below a threshold       |  
> | Work metric: Errors           | Page         | the error rate exceeds a threshold                                                  |  
> | Work metric: Performance      | Page         | work takes too long to complete (e.g., performance violates internal SLA)           |  
> | Resource metric: Utilization  | Notification | approaching critical resource limit (e.g., free disk space drops below a threshold) |  
> | Resource metric: Saturation   | Record       | number of waiting processes exceeds a threshold                                     |  
> | Resource metric: Errors       | Record       | number of errors during a fixed period exceeds a threshold                          |  
> | Resource metric: Availability | Record       | the resource is unavailable for a percentage of time that exceeds a threshold       |
> | Event: Work-related           | Page         | critical work that should have been completed is reported as incomplete or failed   |  

| **データ**                      | **アラート方法**    | **切っ掛け**                                                                         |
|-------------------------------|--------------|-------------------------------------------------------------------------------------|
| Work metric: Throughput       | Page         | value is much higher or lower than usual, or there is an anomalous rate of change   |  
| Work metric: Success          | Page         | the percentage of work that is successfully processed drops below a threshold       |  
| Work metric: Errors           | Page         | the error rate exceeds a threshold                                                  |  
| Work metric: Performance      | Page         | work takes too long to complete (e.g., performance violates internal SLA)           |  
| Resource metric: Utilization  | Notification | approaching critical resource limit (e.g., free disk space drops below a threshold) |  
| Resource metric: Saturation   | Record       | number of waiting processes exceeds a threshold                                     |  
| Resource metric: Errors       | Record       | number of errors during a fixed period exceeds a threshold                          |  
| Resource metric: Availability | Record       | the resource is unavailable for a percentage of time that exceeds a threshold       |
| Event: Work-related           | Page         | critical work that should have been completed is reported as incomplete or failed   |

## Conclusion: Collect ’em all

> -   Instrument everything and collect as many work metrics, resource
>     metrics, and events as you reasonably can.
> -   Collect metrics with sufficient granularity to make important spikes
>     and dips visible. The specific granularity depends on the system you
>     are measuring, the cost of measuring and a typical duration between
>     changes in metrics—seconds for memory or CPU metrics, minutes for
>     energy consumption, and so on.
> -   To maximize the value of your data, tag metrics and events with
>     several scopes, and retain them at full granularity for at least
>     a year.


- 各種の手段を施して、合理的に収集できる全てのworkingメトリクス、resourceメトリクス、イベントを収集する。
- 気付く必要があるスパイク(急上昇)やディップ(急降下)が可視化できる程度の十分な粒度でメトリクスを収集する。メトリクス収集の粒度は、計測している対象に依存し、計測のコストとメトリクスが変化している時間に関わってきます。例えば、CPUやメモリーなら１秒間隔、エネルキー消費量なら１分間隔というようになります。
- データを最小限に抑えるために、メトリクスとイベントには、複数のスコープに基づいてタグ付けをしておきます。そして、最低でも１年間は、オリジナルの粒度で保存しておきます。

> We would like to hear about your experiences as you apply this framework
> to your own monitoring practice. If it is working well, please [let us
> know on Twitter](https://twitter.com/datadoghq)! Questions, corrections,
> additions, complaints, etc? Please [let us know on
> GitHub](https://github.com/DataDog/the-monitor).

独自に実践していた監視体制にこのフレームワークで学んだことを取り入れ、新たな監視体制に取り組んだ体験を是非お聞かせください。
フレームワークを取り入れることによって監視が改善された場合は、Twitterで[@datadoghq](https://twitter.com/datadoghq)付きでつぶやいていただけると幸いです。また、質問、修正、追加、苦情、その他がある場合は、[Github](https://github.com/DataDog/the-monitor)のissueにて連絡ください。
