# [翻訳作業中]

> *This post is part 3 of a 3-part series on monitoring Amazon Aurora. [Part 1][part-1] explores the key metrics available for Aurora, and [Part 2][part-2] explains how to collect those metrics.*

*この投稿は、監視アマゾンオーロラに3回シリーズの第3部です。 [第1部] [パート1]はオーロラに利用できる主要な指標を検討し、[パート2]は、[パート2]は、これらのメトリックを収集する方法について説明します。*

> If you’ve already read [our post][part-2] on collecting metrics from [Amazon Aurora][aurora], you’ve seen that you can easily collect metrics from Amazon's CloudWatch monitoring service and from the database engine itself for ad hoc performance checks. For a more comprehensive view of your database's health and performance, however, you need a monitoring system that can integrate and correlate CloudWatch metrics with database engine metrics, that lets you identify both recent and long-term trends in your metrics, and that can help you identify and investigate performance problems. This post will show you how to connect Aurora to Datadog for comprehensive monitoring in two steps:

あなたは既にアマゾンオーロラからメトリックを収集することに私たちの記事を読んでいれば、あなたが簡単にAmazonのCloudWatchの監視サービスからとアドホック検査用のデータベースエンジン自体からメトリックを収集できることを見てきました。お使いのデータベースの状態とパフォーマンスのより包括的なビューについては、しかし、あなたはあなたの評価指標の両方で最近、長期的な傾向を把握することができます統合し、データベースエンジンの指標とCloudWatchのメトリックを相関させることができる監視システムを、必要とし、それは助けることができますあなたが識別し、パフォーマンスの問題を調査します。この投稿は、二段階で包括的に監視するためのDatadogにオーロラを接続する方法を紹介します：


* [Connect Datadog to CloudWatch](#connect-datadog-to-cloudwatch)
* [Integrate Datadog with Aurora's MySQL-compatible database engine](#integrate-datadog-with-mysql)

<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-11-aurora/aurora_diagram_1.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-11-aurora/aurora_diagram_1.png"></a>

<!--<h2 class="anchor" id="connect-datadog-to-cloudwatch">Connect Datadog to CloudWatch</h2>-->

## <a class="anchor" id="connect-datadog-to-cloudwatch"></a>Connect Datadog to CloudWatch

> To start monitoring metrics from Amazon's Relational Database Service (RDS), you just to configure our [CloudWatch integration][aws-integration]. Create a new user via [the IAM console][iam] in AWS and grant that user (or group of users) read-only permissions to these three services, at a minimum:

> 1. EC2
> 1. CloudWatch
> 1. RDS

> You can attach managed [policies][policy] for each service by clicking on the name of your user in the IAM console and selecting "Permissions," or by using the Amazon API.

> Once these settings are configured within AWS, create access keys for your read-only user and enter those credentials in [the AWS integration tile][aws-tile] on Datadog to start pulling RDS data.

> Note that if you are using ELB, ElastiCache, SNS, or other AWS products in addition to RDS, you may need to grant additional permissions to the user. [See here][aws-integration] for the complete list of permissions required to take full advantage of the Datadog–AWS integration.

（RDS）Amazonのリレーショナルデータベースサービスからのメトリックの監視を開始するには、ちょうど私たちのCloudWatchの統合を設定します。読み取り専用これらの3つのサービスへのアクセス許可を、最低でもAWSにおけるIAMコンソールを介して、新しいユーザーを作成し、そのユーザーに付与（またはユーザのグループ）：

EC2
CloudWatchの
RDS
あなたは、「アクセス許可」IAMコンソールでユーザーの名前をクリックして選択することにより、各サービスの管理するポリシーを付加やAmazonのAPIを使用してすることができます。

これらの設定はAWS内で構成されていたら、読み取り専用ユーザーのためのアクセスキーを作成し、RDSデータを引っ張って開始するDatadogにAWSの統合タイルでこれらの資格情報を入力します。

あなたはRDSに加えてELB、ElastiCache、SNS、または他のAWS製品を使用している場合は、ユーザーに追加の権限を付与する必要があるかもしれないことに注意してください。 Datadog-AWSの統合を最大限に活用するために必要なアクセス許可の一覧についてはこちらをご覧ください。

<!--<h2 class="anchor" id="integrate-datadog-with-mysql">Integrate Datadog with Aurora's database engine</h2>-->

## <a class="anchor" id="integrate-datadog-with-mysql"></a>Integrate Datadog with Aurora's database engine

> As explained in [Part 1][part-1], CloudWatch provides you with several high-level metrics that apply to any of the supported RDS database engines, plus several valuable Aurora-only metrics. To access the hundreds of metrics exposed by the MySQL-compatible database engine, however, you must monitor the database instance itself.

パート1で説明したように、CloudWatchのは、サポートされているRDSデータベースエンジンのいずれにも適用されるいくつかの高レベルの指標に加え、いくつかの貴重なオーロラのみのメトリックを提供します。 MySQLの互換性データベースエンジンによって公開されたメトリックの数百にアクセスするには、しかし、あなたは、データベース・インスタンス自体を監視する必要があります。


### Installing the Datadog Agent on EC2

> [Datadog's Agent][dd-agent] integrates seamlessly with MySQL and compatible technologies (including Aurora) to gather and report key performance metrics, many of which are not available through RDS. Where the same metrics are available through the Agent and through RDS, Agent metrics should be preferred, as they are reported at a higher resolution. Installing the Agent is easy: it usually requires just a single command, and the Agent can collect detailed metrics even if [the performance schema][p_s] is not enabled and the sys schema is not installed. Installation instructions for different operating systems are available [here][agent-install].

> Because RDS does not provide you direct access to the machines running Aurora, you cannot install the Agent on the database instance to collect metrics locally. Instead you must run the Agent on another machine, often an EC2 instance in the same security group. See [Part 2][remote-ec2] of this series for more on accessing Aurora via EC2.

Datadogのエージェントが収集し、RDSを介して利用可能ではありませんその多くが主要なパフォーマンス指標を、報告するためにMySQLと（オーロラ含む）互換性のある技術とシームレスに統合します。同指標はエージェントを通って、RDSを介して利用可能である場合、それらはより高い解像度で報告されるように、エージェントのメトリックは、好まれるべきです。エージェントのインストールは簡単です：それは、通常は単一のコマンドを必要とし、パフォーマンスのスキーマが有効になっておらず、SYSスキーマがインストールされていない場合でも、エージェントは詳細なメトリックを収集することができます。異なるオペレーティングシステムのインストール手順は、ここから入手できます。

RDSはあなたにオーロラを実行しているマシンへの直接アクセスを提供していないので、あなたは、ローカルメトリックを収集するために、データベース・インスタンスにエージェントをインストールすることはできません。代わりに、同じセキュリティグループで、多くの場合、EC2インスタンス、別のマシンにエージェントを実行する必要があります。 EC2経由オーロラへのアクセスの詳細については、この連載の第2回を参照してください。


### Configuring the Agent for RDS

> Collecting Aurora metrics from an EC2 instance is quite similar to running the Agent on a MySQL host to collect metrics locally, with two small exceptions:

> 1. Instead of `localhost` as the server name, provide the Datadog Agent with your Aurora instance endpoint (e.g., `instance_name.xxxxxxx.us-east-1.rds.amazonaws.com`)
> 1. Tag your Aurora metrics with the DB instance identifier (`dbinstanceidentifier:instance_name`) to separate database metrics from the host-level metrics of your EC2 instance

> The Aurora instance endpoint and DB instance identifier are both available from the AWS console. Complete instructions for configuring the Agent to capture MySQL or Aurora metrics from RDS are available [here][dd-doc].

EC2インスタンスからオーロラ・メトリックを収集することは二つの小さな例外を除いて、局所的メトリックを収集するためにMySQLのホスト上でエージェントを実行していると非常によく似ています：

代わりに、サーバー名としてlocalhostとの、あなたのオーロラインスタンスエンドポイントとDatadogエージェントを提供する（例えば、instance_name.xxxxxxx.us-east-1.rds.amazonaws.com）
あなたのEC2インスタンスのホストレベルのメトリックからデータベースメトリックを分離するために：DBインスタンス識別子を使用してオーロラの指標（INSTANCE_NAME dbinstanceidentifier）のタグ
オーロラインスタンスのエンドポイントとDBインスタンス識別子は、AWSコンソールからの両方がご利用いただけます。 RDSからMySQLやオーロラのメトリックをキャプチャするようにエージェントを構成するための詳細な手順は、ここから入手できます。



### Unifying your metrics

> Once you have set up the Agent, all the metrics from your database instance will be uniformly tagged with  `dbinstanceidentifier:instance_name` for easy retrieval, whether those metrics come from RDS or from the database engine itself.

[エージェントの設定が完了したら、データベース・インスタンスからすべてのメトリックを均一dbinstanceidentifierでタグ付けされます。INSTANCE_NAMEを簡単に検索するために、これらの指標は、RDSから、またはデータベース・エンジン自体から来ているかどうか。


## View your comprehensive Aurora dashboard

> Once you have integrated Datadog with RDS, a comprehensive dashboard called “Amazon - RDS (Aurora)” will appear in your list of [integration dashboards][dash-list]. The dashboard gathers the metrics highlighted in [Part 1][part-1] of this series: metrics on query throughput and performance, along with key metrics around resource utilization, database connections, and replication lag.

あなたはRDS、と呼ばれる総合的なダッシュボードとDatadogが統合されていたら、「アマゾン - RDS（オーロラ）」の統合・ダッシュボードのリストに表示されます。リソース使用率、データベース接続、およびレプリケーションラグの周りに主要なメトリックとともに、クエリのスループットとパフォーマンス上のメトリック：ダッシュボードには、このシリーズのパート1で強調表示メトリックを収集します。


<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-11-aurora/aurora-ootb-dash-2.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-11-aurora/aurora-ootb-dash-2.png"></a>

> Out of the box, the dashboard displays database engine metrics from all instances configured via the MySQL integration, as well as RDS metrics from all instances running Aurora. You can focus on one particular instance by selecting a particular `dbinstanceidentifier` in the upper left.

箱から出して、ダッシュボードには、オーロラを実行しているすべてのインスタンスからすべてのMySQLの統合を介して構成されたインスタンスだけでなく、RDSメトリクスからデータベース・エンジン・メトリックが表示されます。あなたは、左上の特定dbinstanceidentifierを選択して、1つの特定のインスタンスに集中することができます。


<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-11-aurora/db-id.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-11-aurora/db-id.png"></a>

### Customize your dashboard

> The Datadog Agent can also collect metrics from the rest of your infrastructure so that you can correlate your entire system's performance with metrics from Aurora. The Agent collects metrics from [ELB][elb], [NGINX][nginx], [Redis][redis], and 120+ other infrastructural applications. You can also easily instrument your own application code to [report custom metrics to Datadog using StatsD][statsd].

あなたはオーロラからのメトリックを使用して、システム全体のパフォーマンスを相互に関連付けることができるようにDatadog Agentは、インフラストラクチャの残りの部分からメトリックを収集することができます。エージェントは、ELB、nginxの、Redisの、および120以上の他のインフラのアプリケーションからメトリックを収集します。また、簡単に楽器独自のアプリケーション・コードはStatsDを使用してDatadogにカスタムメトリックを報告することができます。


> Once you have multiple systems reporting metrics to Datadog, you will likely want to build custom dashboards or modify your default dashboards to suit your use case:
> 
> * Add new graphs to track application metrics alongside associated database metrics
> * Add counters to track custom key performance indicators (e.g., number of users signed in)
> * Add metric thresholds (e.g., normal/warning/critical) to your graphs to aid visual inspection

あなたはDatadogに指標を報告する複数のシステムを持っていたら、おそらくあなたのユースケースに合わせてカスタムダッシュボードを構築したり、デフォルトのダッシュボードを変更したいと思うでしょう。

- 関連するデータベースメトリックと並んで、アプリケーションの指標を追跡するための新しいグラフを追加します。
- カスタム重要業績評価指標を追跡するためにカウンタを追加します（例えば、ユーザーの数がログイン）
- 目視検査を助けるためにあなたのグラフにメトリックのしきい値を（例えば、正常/警告/クリティカル）を追加します


<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-11-aurora/max_conn.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-11-aurora/max_conn.png"></a>
> To start customizing, clone the default Aurora dashboard by clicking on the gear on the upper right of the default dashboard.

カスタマイズを開始するには、デフォルトのダッシュボードの右上の歯車をクリックしてデフォルトオーロラのダッシュボードのクローンを作成。


## Conclusion

> In this post we’ve walked you through integrating Aurora with Datadog so you can access all your database metrics in one place.

> Monitoring Aurora with Datadog gives you critical visibility into what’s happening with your database and the applications that depend on it. You can easily create automated alerts on any metric, with triggers tailored precisely to your infrastructure and your usage patterns.

> If you don’t yet have a Datadog account, you can sign up for a [free trial][trial] and start monitoring your cloud infrastructure, your applications, and your services today.

この記事では私たちは、あなたが一箇所ですべてのデータベースメトリックにアクセスできるようにDatadogでオーロラを統合する手順を歩いてきました。

Datadogでオーロラを監視すると、あなたのデータベースとそれに依存するアプリケーションで何が起こっているのかに重要な可視性を提供します。トリガーは、インフラストラクチャとあなたの使用パターンに正確に合わせて使えば、簡単に、任意のメトリックに自動化されたアラートを作成することができます。

あなたはまだDatadogアカウントをお持ちでない場合は、無料試用版にサインアップして、クラウドインフラストラクチャ、アプリケーション、およびサービスの今日の監視を開始することができます。


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
