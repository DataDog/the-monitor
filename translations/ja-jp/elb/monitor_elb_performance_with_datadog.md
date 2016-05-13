# [翻訳作業中]

*This post is the last of a 3-part series on monitoring Amazon ELB. [Part 1](https://www.datadoghq.com/blog/top-elb-health-and-performance-metrics) explores its key performance metrics, and [Part 2](https://www.datadoghq.com/blog/how-to-collect-aws-elb-metrics) explains how to collect these metrics.*

*このポストは、Amazon ELBの監視に関する3回シリーズのPart 3です。 [Part 1](https://www.datadoghq.com/blog/top-elb-health-and-performance-metrics)では、ELBのキーメトリクスを解説しています。[Part 2](https://www.datadoghq.com/blog/how-to-collect-aws-elb-metrics)では、Amazon ELBのメトリクスの収集方法に関して解説していきます。*


> If you’ve already read [our post](https://www.datadoghq.com/blog/how-to-collect-aws-elb-metrics) on collecting Elastic Load Balancing metrics, you’ve seen that you can visualize their recent evolution and set up simple alerts using the AWS Management Console’s web interface. For a more dynamic and comprehensive view, you can connect ELB to Datadog.

既にELBメトリックの収集方法に関するポストを読んでいるのなら、AWS管理コンソールのWebインタフェースを使用して、それらのメトリクスの変化を可視化し、簡単なアラートを設定することは理解しているでしょう。更に総合的にかつダイナミックにELBメトリクスを把握するには、DatadogでELBを監視する方法があります。


> Datadog lets you collect and view ELB metrics, access their historical evolution, and slice and dice them using any combination of properties or custom tags. Crucially, you can also correlate ELB metrics with metrics from any other part of your infrastructure for better insight—especially native metrics from your backend instances. And with more than 100 supported integrations, you can create and send advanced alerts to your team using collaboration tools such as [PagerDuty](https://www.datadoghq.com/blog/pagerduty/) and [Slack](https://www.datadoghq.com/blog/collaborate-share-track-performance-slack-datadog/).

Datadogを使うと、ELBメトリクスからを集取し、可視化し、それらの過去の変化にもアクセスすることができるようになります。更に、プロパティーやカスタムタグの組み合わせて、集取したメトリクスを再編成し、表示やアラートに活用することができりようになります。最も重要なこととして、ELBメトリクスをインフラの他の部分から集取したメトリクス(例えば、バックエンドインスタンスから収集したネイティブメトリクス)と相関させて、ELBの状況を更に詳しく把握することができるようになります。そして、100以上もあるインテグレーションを使って、高度に設計されたアラートを作成し、[PagerDuty](https://www.datadoghq.com/blog/pagerduty/)や[Slack](https://www.datadoghq.com/blog/collaborate-share-track-performance-slack-datadog/)などのコラボレーションツールを使用して、チームにメッセージを送信することができるようになります。


> In this post we’ll show you how to get started with the ELB integration, and how to correlate your load balancer performance metrics with your backend instance metrics.

このポストでは、ELBインテグレーションの導入方法を解説し、ロードバランサーメトリクスとバックエンドインスタンスからのメトリクスを相関させる方法を解説していきます。


[![ELB metrics graphs](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/3-01.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/3-01.png)

> *ELB metrics graphs on Datadog*

*Datadog上にELBメトリクスを表示したグラフ*

## Integrate Datadog and ELB

> To start monitoring ELB metrics, you only need to [configure our integration with AWS CloudWatch](http://docs.datadoghq.com/integrations/aws/). Create a new user via the [IAM Console](https://console.aws.amazon.com/iam/home#s=Home) and grant that user (or group of users) the required set of permissions. These can be set via the [Policy management](https://console.aws.amazon.com/iam/home?#policies) in the console or using the Amazon API.

ELBメトリックの監視を開始するには、AWS CloudWatchとDatadogを連携するための[インテグレーションを設定](http://docs.datadoghq.com/integrations/aws/)する必要があります。[IAMのコンソール](https://console.aws.amazon.com/iam/home#s=Home)から、新しいユーザーを作成し、そのユーザー(又は、ユーザーグループ）に、メトリクスへのアクセス権限の組み合わせを付与していきます。これら権限は、管理コンソールか、Amazon APIを使って、[Policy management](https://console.aws.amazon.com/iam/home?#policies)を編集することで設定できます。


> Once these credentials are configured within AWS, follow the simple steps on the [AWS integration tile](https://app.datadoghq.com/account/settings#integrations/amazon_web_services) on Datadog to start pulling ELB data.

AWS側でこれらの権限設定が完了したら、ELBのメトリクスデーターをDdatadogへ取り入れるための、[AWS インテグレーションをタイル](https://app.datadoghq.com/account/settings#integrations/amazon_web_services)内の解説に従って設定していきます。


> Note that if, in addition to ELB, you are using RDS, SES, SNS, or other AWS products, you may need to grant additional permissions to the user. [See here](http://docs.datadoghq.com/integrations/aws/) for the complete list of permissions required to take full advantage of the Datadog–AWS integration.

ELBに加え、RDS, SES, SNMS, 又は他のAWSのサービスを使っている場合で、それらからもメトリクスを集取したい場合は、それらのサービスに付いても、先のユーザーに権限を追加する必要があることに注意してください。Datadogが提供しているAWSのインテグレーションを最大限に活用刷るために必要なアクセス権限に関しては、[リンク先](http://docs.datadoghq.com/integrations/aws/)を参照してください。


## Keep an eye on all key ELB metrics

> Once you have successfully integrated Datadog with ELB, you will see [a default dashboard](https://app.datadoghq.com/screen/integration/aws_elb) called “AWS-Elastic Load Balancers” in your list of [integration dashboards](https://app.datadoghq.com/dash/list). The ELB dashboard displays all of the key metrics highlighted in [Part 1](https://www.datadoghq.com/blog/top-elb-health-and-performance-metrics) of this series: requests per second, latency, surge queue length, spillover count, healthy and unhealthy hosts counts, HTTP code returned, and more.

DatadogとELBの連携が完了すると、インテグレーション用のダッシュボード一覧に、“AWS-Elastic Load Balancers”という名の[ELBのデフォルトダッシュボード](https://app.datadoghq.com/screen/integration/aws_elb) が表示されます。


あなたが成功しELBでDatadogを統合したら、統合ダッシュボードのリストに「AWS-弾性ロードバランサ」と呼ばれるデフォルトのダッシュボードが表示されます。 ELBのダッシュボードが表示主要指標のすべてが、このシリーズのパート1で強調表示：秒、待ち時間、サージキューの長さ、波及カウント、健康と不健康なホスト数、HTTPコードが返され、より多くのあたりの要求を。


[![ELB default dashboard on Datadog](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/3-02.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/3-02.png)

*ELB default dashboard on Datadog*

## Customize your dashboards

> Once you are capturing metrics from Elastic Load Balancing in Datadog, you can build on the default dashboard and edit or add additional graphs of metrics from ELB or even from other parts of your infrastructure. To start building a custom [screenboard](https://www.datadoghq.com/blog/introducing-screenboards-your-data-your-way/), clone the default ELB dashboard by clicking on the gear on the upper right of the default dashboard.





あなたはDatadogに弾性負荷分散からメトリックをキャプチャしたら、デフォルトのダッシュボードや編集の上に構築したり、インフラストラクチャの他の部分からでもELBからのメトリックの追加のグラフを追加したりすることができます。カスタムscreenboardの作成を開始するには、デフォルトのダッシュボードの右上の歯車をクリックしてデフォルトELBのダッシュボードのクローンを作成。


> You can also create [timeboards](http://help.datadoghq.com/hc/en-us/articles/204580349-What-is-the-difference-between-a-ScreenBoard-and-a-TimeBoard-), which are interactive Datadog dashboards displaying the evolution of multiple metrics across any timeframe.





また、任意の時間枠全体で複数のメトリックの進化を表示するインタラクティブDatadogダッシュボードですtimeboardsを、作成することができます。


## Correlate ELB with EC2 metrics

> As explained in [Part 1](https://www.datadoghq.com/blog/top-elb-health-and-performance-metrics), CloudWatch’s ELB-related metrics inform you about your load balancers’ health and performance. ELB also provides backend-related metrics reflecting your backend instances health and performance. However, to fully monitor your backend instances, you should consider collecting these backend metrics directly from EC2 as well for better insight. By correlating ELB with EC2 metrics, you will be able to quickly investigate whether, for example, the high number of requests being queued by your load balancers is due to resource saturation on your backend instances (memory usage, CPU utilization, etc.).





パート1で説明したように、CloudWatchののELB-関連の指標は、あなたのロードバランサの健康とパフォーマンスについてお知らせ。 ELBはまたあなたのバックエンドインスタンスの健全性とパフォーマンスを反映して、バックエンド関連のメトリックを提供します。しかし、完全にあなたのバックエンドのインスタンスを監視するために、あなたはより良い洞察力だけでなく、EC2から直接これらのバックエンド・メトリックの収集を検討する必要があります。 EC2の指標とELBを相関させることによって、あなたはすぐに、たとえば、要求の高い数は、ロード・バランサによってキューイングされ、かどうかを調査することができるようになりますあなたのバックエンドインスタンス（メモリ使用量、CPU使用率など）の飽和を資源によるものです。


> Thanks to our integration with CloudWatch and the permissions you set up, you can already access EC2 metrics on Datadog. Here is [your default dashboard](https://app.datadoghq.com/screen/integration/aws_ec2) for EC2.




CloudWatchのあなたが設定したアクセス権との統合のおかげで、あなたはすでにDatadogにEC2メトリックにアクセスすることができます。ここではEC2用のデフォルトのダッシュボードがあります。


[![Default EC2 dashboard on Datadog](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/3-03.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/3-03.png)

> *Default EC2 dashboard on Datadog*

*Datadog上のデフォルトのEC2ダッシュボード*

> You can add graphs to your custom dashboards and view side by side ELB and EC2 metrics. Correlating peaks in two different metrics to see if they are linked is very easy.





あなたが側ELBとEC2の指標により、カスタムダッシュボードとビュー側にグラフを追加することができます。それらがリンクされているかどうかを確認するために、2つの異なるメトリックのピークを相関させることは非常に簡単です。


> You can also, for example, display a host map to spot at a glance if all your backend instances have a reasonable CPU utilization:




また、例えば、すべてのバックエンドインスタンスが妥当なCPU使用率を持っている場合は、一目でスポットするホストマップを表示することができます。


[![Default EC2 dashboard on Datadog](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/3-04.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/3-04.png)

### Native metrics for more precision

> In addition to pulling in EC2 metrics via CloudWatch, Datadog also allows you to monitor your EC2 instances’ performance with higher resolution by installing the Datadog Agent to pull native metrics directly from the servers. The Agent is [open-source software](https://github.com/DataDog/dd-agent) that collects and reports metrics from your individual hosts so you can view, monitor and correlate them on the Datadog platform. Installing the Agent usually requires just a single command. Installation instructions for different operating systems are available [here](https://app.datadoghq.com/account/settings#agent).





CloudWatchの経由EC2メトリックスを引き込むことに加えて、Datadogはまた、サーバーから直接ネイティブのメトリックを引っ張ってDatadog Agentをインストールすることで、より高い解像度を使用してEC2インスタンスのパフォーマンスを監視することができます。エージェントを使用すると、表示、監視およびDatadogプラットフォーム上で、それらを関連付けることができますので、あなたの個々のホストからのメトリックを収集し、レポートのオープンソースソフトウェアです。エージェントをインストールすると、通常は単一のコマンドが必要です。異なるオペレーティングシステムのインストール手順は、ここから入手できます。


> By using the [Datadog Agent](https://www.datadoghq.com/blog/dont-fear-the-agent/), you can collect backend instance metrics with a higher granularity for a better view of their health and performance. The Agent reports metrics directly, at rapid intervals, and does not rely on polling an intermediary (such as CloudWatch), so you can access metrics more frequently without being limited by the provider’s monitoring API.




Datadogエージェントを使用することにより、あなたは自分の健康とパフォーマンスをより良く見るためのより高い粒度でバックエンドインスタンスのメトリックを収集することができます。エージェントは、急速な間隔で、直接メトリックを報告し、ポーリングの仲介を（例えばCloudWatchのように）依存していないので、あなたは、プロバイダの監視APIによって制限されることなく、より頻繁にメトリックにアクセスすることができます。


> The Agent provides higher-resolution views of all key system metrics, such as CPU utilization or memory consumption by process.




エージェントは、このようなプロセスによるCPU使用率やメモリ消費量など、すべての主要なシステム・メトリックの高解像度のビューを提供します。


> Once you have set up the Agent, correlating native metrics from your EC2 instances with ELB’s CloudWatch metrics is a piece of cake (as explained above), and will give you a full and precise picture of your infrastructure’s performance.




[エージェントの設定が完了したら（上記で説明したように）、ELBのCloudWatchのメトリクスを使用してEC2インスタンスからネイティブメトリックを相関させてケーキで、あなたのインフラストラクチャのパフォーマンスの完全かつ正確な画像が得られます。


> The Agent can also collect application metrics so that you can correlate your application’s performance with the host-level metrics from your compute layer. The Agent integrates seamlessly with applications such as MySQL, [NGINX](https://www.datadoghq.com/blog/how-to-monitor-nginx/), Cassandra, and many more. It can also collect custom application metrics as well.




あなたのコンピューティング層からホストレベルのメトリックを使用してアプリケーションのパフォーマンスを相関させることができるように、エージェントは、アプリケーションのメトリックを収集することができます。エージェントは、MySQLの、nginxの、カサンドラ、および多くのようなアプリケーションとシームレスに統合します。また、同様に、カスタム・アプリケーション・メトリックを収集することができます。


> To install the Datadog Agent, follow the [instructions here](http://docs.datadoghq.com/guides/basic_agent_usage/) depending on the OS your EC2 machines are running.




Datadogエージェントをインストールするには、あなたのEC2のマシンが稼働しているOSに応じて、ここでの指示に従ってください。


## Conclusion

> In this post we’ve walked you through integrating Elastic Load Balancing with Datadog so you can visualize and alert on its key metrics. You can also visualize EC2 metrics to keep tab on your backend instances, to improve performance, and to save costs.




この記事では、我々はあなたが視覚化し、その主要な指標に警告できるようDatadogでバランス弾性荷重を統合する手順を歩いてきました。また、パフォーマンスを向上させるために、コストを節約するために、バックエンドインスタンスのタブを保つためにEC2の指標を可視化することができます。


> Monitoring ELB with Datadog gives you critical visibility into what’s happening with your load balancers and applications. You can easily create automated [alerts](https://www.datadoghq.com/blog/monitoring-101-alerting/) on any metric across any group of instances, with triggers tailored precisely to your infrastructure and usage patterns.





DatadogでELBを監視するあなたのロードバランサやアプリケーションと何が起こっているのかに重要な可視性を提供します。トリガーは、インフラストラクチャと使用パターンに正確に合わせて使えば、簡単に、インスタンスの任意のグループ全体で任意のメトリックに自動化されたアラートを作成することができます。


> If you don’t yet have a Datadog account, you can sign up for a [free trial](https://app.datadoghq.com/signup) and start monitoring your cloud infrastructure, applications, and services.





あなたはまだDatadogアカウントをお持ちでない場合は、無料試用版にサインアップして、クラウドインフラストラクチャ、アプリケーション、およびサービスの監視を開始することができます。
