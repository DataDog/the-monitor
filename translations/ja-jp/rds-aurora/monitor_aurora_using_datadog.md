> *This post is part 3 of a 3-part series on monitoring Amazon Aurora. [Part 1][part-1] explores the key metrics available for Aurora, and [Part 2][part-2] explains how to collect those metrics.*

*このポストは、Amazon Auroraの監視に関する3回シリーズのポストのPart 3です。[Part 1][part-1]は、”Auroraのキーメトリクス”を解説しています。[Part 2][Part-2]は、”Auroraからどのようにしてデータを収集するか”を解説しています。*


> If you’ve already read [our post][part-2] on collecting metrics from [Amazon Aurora][aurora], you’ve seen that you can easily collect metrics from Amazon's CloudWatch monitoring service and from the database engine itself for ad hoc performance checks. For a more comprehensive view of your database's health and performance, however, you need a monitoring system that can integrate and correlate CloudWatch metrics with database engine metrics, that lets you identify both recent and long-term trends in your metrics, and that can help you identify and investigate performance problems. This post will show you how to connect Aurora to Datadog for comprehensive monitoring in two steps:

Amazon Auroraからメトリクスを集取する方法を解説した[Part 2][part-2]のポストを既に読んでいるのであれば、データベースをチェックするために、Amazon CloudWatchの監視サービスとデータベースエンジン自体からメトリクスが簡単に収集できるのは分かったでしょう。しかし更に、データベースの健全性とパフォーマンスについて総合的に理解をするためには、CloudWatchのメトリックとデータベースエンジンのネイティブメトリックを同時に収集し、互いのデータを相関させることができ、メトリクスの最近のトレンドと長期的なトレンドが把握でき、更に、パフォーマンス問題を識別し、そののの原因の掘り下げがきでる監視システムであることが必要でしょう。このポストでは、2ステップでAuroraにDatadogを接続し、総合的な監視システムを構築する方法を紹介します:


* [Connect Datadog to CloudWatch](#connect-datadog-to-cloudwatch)
* [Integrate Datadog with Aurora's MySQL-compatible database engine](#integrate-datadog-with-mysql)

<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-11-aurora/aurora_diagram_1.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-11-aurora/aurora_diagram_1.png"></a>

<!--<h2 class="anchor" id="connect-datadog-to-cloudwatch">Connect Datadog to CloudWatch</h2>-->

## <a class="anchor" id="connect-datadog-to-cloudwatch"></a>Connect Datadog to CloudWatch

> To start monitoring metrics from Amazon's Relational Database Service (RDS), you just to configure our [CloudWatch integration][aws-integration]. Create a new user via [the IAM console][iam] in AWS and grant that user (or group of users) read-only permissions to these three services, at a minimum:

> 1. EC2
> 1. CloudWatch
> 1. RDS

Amazon's Relational Database Service (RDS)メトリックの監視を開始するには、[AWS CloudWatchのインテグレーション][aws-integration]を設定するだけです。AWSの[IAMのコンソール][iam]から新しいユーザー(又は、ユーザーグループ)を作成し、下記の3つのサービスに対して、最低でもデーターが読み取り可能(例:read-only)なアクセス権を許可します:

1. EC2
1. CloudWatch
1. RDS


> You can attach managed [policies][policy] for each service by clicking on the name of your user in the IAM console and selecting "Permissions," or by using the Amazon API.

IAMコンソールからユーザーにアクセス権を付与たり、AWSのAPIを使ったりして、サービス毎に[管理ポリシー][policy]を設定することもできます。


> Once these settings are configured within AWS, create access keys for your read-only user and enter those credentials in [the AWS integration tile][aws-tile] on Datadog to start pulling RDS data.

データー読み込むためのユーザーのアクセス権限の設定が完了したら、そのユーザーへのアクセスキーを作成し、Datadogのサイトにある[AWSインテグレーションのタイル][aws-tile]に、その認証情報を設定します。アクセスキーの設定が完了し、しばらくするとAmazon CloudWatch経由でのデーター収集が開始されます。


> Note that if you are using ELB, ElastiCache, SNS, or other AWS products in addition to RDS, you may need to grant additional permissions to the user. [See here][aws-integration] for the complete list of permissions required to take full advantage of the Datadog–AWS integration.

RDSに加え、ELB、ElastiCache、SNS、または、他のAWSサービスを使用している場合は、そのユーザーに追加の権限を付与する必要があることに注意してください。Datadog-AWSのインテグレーションを最大限に活用するために[必要なアクセス許可の一覧][aws-tile]についてはこちらをご覧ください。


<!--<h2 class="anchor" id="integrate-datadog-with-mysql">Integrate Datadog with Aurora's database engine</h2>-->

## <a class="anchor" id="integrate-datadog-with-mysql"></a>Integrate Datadog with Aurora's database engine

> As explained in [Part 1][part-1], CloudWatch provides you with several high-level metrics that apply to any of the supported RDS database engines, plus several valuable Aurora-only metrics. To access the hundreds of metrics exposed by the MySQL-compatible database engine, however, you must monitor the database instance itself.

このシリーズの[Part 1][part-1]で解説したように、CloudWatchは、RDSでサポートされているデータベースエンジンや、幾つかのAurora独自のメトリクスについて、複数の貴重なメトリックを提供しています。しかし、MySQL互換データベースに準備されたメトリクスを収集するためには、データベースインスタンス自体にアクセスし監視する必要があります。


### Installing the Datadog Agent on EC2

> [Datadog's Agent][dd-agent] integrates seamlessly with MySQL and compatible technologies (including Aurora) to gather and report key performance metrics, many of which are not available through RDS. Where the same metrics are available through the Agent and through RDS, Agent metrics should be preferred, as they are reported at a higher resolution. Installing the Agent is easy: it usually requires just a single command, and the Agent can collect detailed metrics even if [the performance schema][p_s] is not enabled and the sys schema is not installed. Installation instructions for different operating systems are available [here][agent-install].

Datadog Agnetは、MySQLとそれと互換性を持った技術(Auroraのように)と高度に連携し、RDS経由では入手できないキーパフォーマンスメトリクスを収集し、レポートすることができます。又、Datadog AgentとRDSから同じメトリクスが集取できる場合は、高い解像度でレポートされているDatadog Agentからのメトリクスを選択するべきでしょう。Datadog Agnetのインストールは、非常に簡単です:一般的には、単一のシェルコマンドを実行するのみです。そして、[MySQL performance schema][p_s]が、サーバー内で有効になっていなくも、又、sys schemaがインストールされていなくても、メトリクスを収集することができます。異なるOSのインストール手順は、[このリンク先][agent-install]から入手できます。


> Because RDS does not provide you direct access to the machines running Aurora, you cannot install the Agent on the database instance to collect metrics locally. Instead you must run the Agent on another machine, often an EC2 instance in the same security group. See [Part 2][remote-ec2] of this series for more on accessing Aurora via EC2.

RDSは、MySQLが動作しているOS自体に直接アクセスし操作をすることを許可していないので、MySQLインスタンスにDatadog Agentをインストールし、ローカルからメトリクスを集取することができません。代わりに、Datadog Agentを、同一セキュリティーグループの内にある他のマシン(EC2インスタンスなど)にインストトールして、代理のインスタンス経由でメトリクスを集取することできます。EC2を経由したAuroraへのアクセスの詳細については、このシリーズの[Part 2][part-2]を参照してください。


### Configuring the Agent for RDS

> Collecting Aurora metrics from an EC2 instance is quite similar to running the Agent on a MySQL host to collect metrics locally, with two small exceptions:

> 1. Instead of `localhost` as the server name, provide the Datadog Agent with your Aurora instance endpoint (e.g., `instance_name.xxxxxxx.us-east-1.rds.amazonaws.com`)
> 1. Tag your Aurora metrics with the DB instance identifier (`dbinstanceidentifier:instance_name`) to separate database metrics from the host-level metrics of your EC2 instance

他のEC2インスタンスからAuroraのネイティブメトリクスを集取するための設定は、Datadog AgentとMySQLを同一サーバー内で実行し、ローカルサーバー内でメトリクスを集取している状態と、以下の二つの項目が異なります: (mysql.yamlの記述に関するローカル設定と異なる部分を記します)

1. サーバー名の部分に`localhost`と書かずに、Auroraのエンドポイント情報を記述します。（例えば、`instance_name.xxxxxxx.us-east-1.rds.amazonaws.com`）
2. Datadog Agentが実行されている外部EC2インスタンスのホスト自体のメトリックの発生源と、Auroraから収集したネイティブメトリックの発生源を区別するために、Auroraに関連するメトリクスに識別用のDBインスタンス識別（`dbinstanceidentifier:instance_name`）タグを付与します。


> > The Aurora instance endpoint and DB instance identifier are both available from the AWS console. Complete instructions for configuring the Agent to capture MySQL or Aurora metrics from RDS are available [here][dd-doc].

AuroraインスタンスのエンドポイントとDBインスタンス識別子に関する情報は、AWSコンソールから入手できます。RDSからMySQLやAuroraのメトリックを収集するために必要なDatadog Agentの設定の詳細に関しては、次の[リンク][dd-doc]を参照してください。


### Unifying your metrics

> Once you have set up the Agent, all the metrics from your database instance will be uniformly tagged with  `dbinstanceidentifier:instance_name` for easy retrieval, whether those metrics come from RDS or from the database engine itself.

Datadog Agentの設定が完了したら、効率的にメトリクスを取り扱うために、RDSからかデーターベースエンジン自体にからかに関わらず、データベースのインスタンスクラスから集取された全てのメトリクスには、一律に`dbinstanceidentifier:instance_name`のタグが付与されているはずです。


## View your comprehensive Aurora dashboard

> Once you have integrated Datadog with RDS, a comprehensive dashboard called “Amazon - RDS (Aurora)” will appear in your list of [integration dashboards][dash-list]. The dashboard gathers the metrics highlighted in [Part 1][part-1] of this series: metrics on query throughput and performance, along with key metrics around resource utilization, database connections, and replication lag.

RDSをDatadogと連携する作業が完了すると、“Amazon - RDS (Aurora)”という総合ダッシュボードが、[インテグレーション用のダッシュボード][dash-list]のリストに表示されます。そのダッシュボードは、[Part 1][part-1]で焦点を当てたメトリクスを表示しています。:クエリーのスループットとパフォーマンス、リソース使用率、データベース接続、およびレプリケーションのログが表示されています。


<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-11-aurora/aurora-ootb-dash-2.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-11-aurora/aurora-ootb-dash-2.png"></a>

> Out of the box, the dashboard displays database engine metrics from all instances configured via the MySQL integration, as well as RDS metrics from all instances running Aurora. You can focus on one particular instance by selecting a particular `dbinstanceidentifier` in the upper left.

インストールを済ませると、レポート対象の全のデータベースインスタンスのネイティブメトリクスと、Auroraが動作している全インスタンスのRDSメトリクスが、デフォルトでダッシュボードに表示されます。ダッシュボードの左上にあるテンプレートバリューセレクターを使って`dbinstanceidentifier`を選択することによって、特定のインスタンス情報のみを表示することもできます。


<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-11-aurora/db-id.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-11-aurora/db-id.png"></a>

### Customize your dashboard

> The Datadog Agent can also collect metrics from the rest of your infrastructure so that you can correlate your entire system's performance with metrics from Aurora. The Agent collects metrics from [ELB][elb], [NGINX][nginx], [Redis][redis], and 120+ other infrastructural applications. You can also easily instrument your own application code to [report custom metrics to Datadog using StatsD][statsd].


Datadog Agentは、システム全体のパフォーマンスに関連したメトリクスとMySQL関連したメトリクスを関連付けることができるように、インフラの残りの部分からもメトリックを収集することができます。Datadog Agentは、[ELB][elb], [NGINX][nginx], [Redis][redis], そして、120を越える他のインフラ系アプリからメトリクスを収集することができ、又、アプリケーションの数行のコード調整で、[StatsDを経由してカスタムメトリックをレポートする][statsd]ことができるようになります。


> Once you have multiple systems reporting metrics to Datadog, you will likely want to build custom dashboards or modify your default dashboards to suit your use case:

> * Add new graphs to track application metrics alongside associated database metrics
> * Add counters to track custom key performance indicators (e.g., number of users signed in)
> * Add metric thresholds (e.g., normal/warning/critical) to your graphs to aid visual inspection


複数のシステムがメトリクスをレポートするようになると、ユースケースに合わせて、カスタムダッシュボードを構築したり、デフォルトのダッシュボードを修正したいと思うようになるでしょう:(ダッシュボードのカスタマイオズ例としては。）

* アプリからのメトリクスをデータベースメトリクスの横に並べて追跡するために、新しいグラフを追加します。
* KPI(key performance indicators)を追跡するために、カウンターを追加します。(例: ユーザーのログイン数など)
* 目視点検の補助として、メトリクスの閾値（例: 正常/警告/クリティカル）をグラフに追加します。


<a href="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-11-aurora/max_conn.png"><img src="https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-11-aurora/max_conn.png"></a>
> To start customizing, clone the default Aurora dashboard by clicking on the gear on the upper right of the default dashboard.

カスタマイズを始めるには、デフォルトのダッシュボード(例:Aurora)の右上の歯車をクリックすることで、そのダッシュボードのクローンを作成することができます。


## Conclusion

> In this post we’ve walked you through integrating Aurora with Datadog so you can access all your database metrics in one place.

このポストでは、データベースに関連した全てのメトリクスにワンストップでアクセスできるように、DatadogとAuroroaを統合する手順を解説してきました。


> Monitoring Aurora with Datadog gives you critical visibility into what’s happening with your database and the applications that depend on it. You can easily create automated alerts on any metric, with triggers tailored precisely to your infrastructure and your usage patterns.

DatadogでAuroraを監視すると、データベースとそれに依存するアプリケーションで何が起こっているかを素早く把握することができるようになります。更に、インフラの構造や利用のパターンに合わせたトリガーを持つ、高度にカスタマイズされたアラートを任意のメトリクスに対して作成することができるようになります。


> If you don’t yet have a Datadog account, you can sign up for a [free trial][trial] and start monitoring your cloud infrastructure, your applications, and your services today.

もしも未だDatadogのアカウントを持っていないなら、無料トライアルへ[ユーザー登録][sign up]すれば直ちにクラウドインフラ、アプリケーション、およびサービスの監視を始めることができます。


- - -

*Source Markdown for this post is available [on GitHub][markdown]. Questions, corrections, additions, etc.? Please [let us know][issues].*

[aurora]: https://aws.amazon.com/rds/aurora/
[markdown]: https://github.com/DataDog/the-monitor/blob/master/rds-aurora/monitor_aurora_using_datadog.md
[issues]: https://github.com/DataDog/the-monitor/issues
[part-1]: https://www.datadoghq.com/blog/monitoring-amazon-aurora-performance-metrics
[part-2]: https://www.datadoghq.com/blog/how-to-collect-aurora-metrics
[aws-integration]: http://docs.datadoghq.com/integrations/aws/
[iam]: https://console.aws.amazon.com/iam/home
[policy]: https://console.aws.amazon.com/iam/home?#policies
[aws-tile]: https://app.datadoghq.com/account/settings#integrations/amazon_web_services
[dd-agent]: https://github.com/DataDog/dd-agent
[agent-install]: https://app.datadoghq.com/account/settings#agent
[remote-ec2]: https://www.datadoghq.com/blog/how-to-collect-aurora-metrics#connecting-to-your-rds-instance
[dd-doc]: http://docs.datadoghq.com/integrations/rds/
[statsd]: https://www.datadoghq.com/blog/statsd/
[dash-list]: https://app.datadoghq.com/dash/list
[trial]: https://app.datadoghq.com/signup
[nginx]: https://www.datadoghq.com/blog/how-to-monitor-nginx/
[redis]: https://www.datadoghq.com/blog/how-to-monitor-redis-performance-metrics/
[elb]: https://www.datadoghq.com/blog/top-elb-health-and-performance-metrics/
[p_s]: https://www.datadoghq.com/blog/how-to-collect-rds-mysql-metrics#querying-the-performance-schema-and-sys-schema
