# Monitor Openstack with Datadog
> _This post is the final part of a 3-part series on OpenStack Nova monitoring. [Part 1] explores the key metrics available from Nova, and [part 2][Part 2] is about collecting those metrics on an ad hoc basis._

> _In this last post of the OpenStack series, we show you how to monitor Openstack with Datadog._

このポストは、3回に渡るOpenStackのコンピュートモジュールであるNovaの監視のシリーズの最終回です。[Part 1][Part 1]では、OpenStackのキーメトリックにつて解説しています。そして、[Part 2][Part 2]では、アドホック的にそれらのメトリクスを収集する方法を紹介しました。

このOpenStackシリーズの最後のポストでは、Datadogを使ってOpenStackの監視する方法を紹介していきます。


> To get the most out of your OpenStack monitoring, you need a way to correlate what’s happening in OpenStack with what’s happening in the rest of your infrastructure. OpenStack deployments often rely on additional software packages not included in the OpenStack codebase itself, including [MySQL][mysql], [RabbitMQ], [Memcached], [HAProxy][haproxy], and Pacemaker. A comprehensive monitoring implementation includes all the layers of your deployment, not just the metrics emitted by OpenStack itself.

> With Datadog, you can collect OpenStack metrics for visualization, alerting, full-infrastructure correlation, and more. Datadog will automatically collect the key metrics discussed in parts [one][Part 1] and [two][Part 2] of this series, and make them available in a template dashboard, as seen below.

OpenStackの監視から最大限に価値を引き出すためには、OpenStackで何が起こっているのかを、それ以外のインフラの部分で何が起こっているかを関連づける方法が必要になります。多くの場合、OpenStackの環境は、[MySQL][mysql], [RabbitMQ], [Memcached], [HAProxy][haproxy], Pacemakerなど、OpenStackのコードベース自体に含まれていない追加のソフトウェアパッケージに依存して構築されています。　OpenStackの包括的な監視には、OpenStack自体から収集できるメトリクスに加え、関連する全ての層を含めて実装が必要になります。

Datadogを使えば、収集したOpenStackのメトリクスを基に、データーを可視化し、アラートを設定し、インフラの全ての部分のと相関関係を見ることができるようになります。DatadogのOpenStackインテグレーションは、このシリーズの[Part 1][Part 1]と[Part 2][Part 2]で紹介したキーメトリクスを自動で収集します、以下のようなダッシュボードに表示してくれます。


[![OpenStack default dashboard][default-dash]][default-dash]

> If you're not a Datadog customer but want to follow along, you can get a [free trial][sign up].

あなたが、Datadogの顧客でなくても、[無償トライアル][sign up]に登録して、この手順にそって進めることも可能です。


## Configuring OpenStack
> Getting the Datadog Agent and OpenStack to talk with each other takes about five minutes. To start, the Datadog Agent will need its own role and user. Run the following series of commands, in order, on your Keystone (identity) server:  

> 1.`openstack role create datadog_monitoring`  
> 2.`openstack user create datadog --password my_password --project my_project_name`  
> 3.`openstack role add datadog_monitoring --project my_project_name --user datadog`  

> Be sure to change my\_password and my\_project before running the commands.
    
> Once you've created the user and role, the next step is to apply the privileges needed to collect metrics, which entails modifying three configuration files.

Datadog Agentを設定し、OpenStackからメトリクスを収集できるようにするには、約5分くらいの時間が掛かります。まず最初に、Datadog Agentが利用するロールとユーザーが必要になります。Keystoneの認証用サーバーで、次のコマンドを順次実行していきます:

1.`openstack role create datadog_monitoring`  
2.`openstack user create datadog --password my_password --project my_project_name`  
3.`openstack role add datadog_monitoring --project my_project_name --user datadog`

上記のコマンドを実行する前に、”my_password”と”my_project_name”を実際の環境に合わせて変更しておきます。

ユーザーとロールを作成したら、次のステップは、3つの構成ファイルを変更し、メトリックを収集するために必要な権限を設定していきます。


### Nova
> First, open Nova's policy file, found at `/etc/nova/policy.json`. Edit the following permissions, adding `role:datadog_monitoring`:  

まず、`/etc/nova/policy.json` にあるNovaのポリシー設定ファイルを編集し、`role:datadog_monitoring`を追加していきます:

``` 
    - "compute_extension:aggregates" : "role:datadog_monitoring",
    - "compute_extension:hypervisors" : "role:datadog_monitoring",
    - "compute_extension:server_diagnostics" : "role:datadog_monitoring",
    - "compute_extension:v3:os-hypervisors" : "role:datadog_monitoring",
    - "compute_extension:v3:os-server-diagnostics" : "role:datadog_monitoring",
    - "compute_extension:availability_zone:detail" : "role:datadog_monitoring",
    - "compute_extension:v3:availability_zone:detail" : "role:datadog_monitoring",
    - "compute_extension:used_limits_for_admin" : "role:datadog_monitoring",
    - "os_compute_api:os-aggregates:index" : "role:datadog_monitoring",
    - "os_compute_api:os-aggregates:show" : "role:datadog_monitoring",
    - "os_compute_api:os-hypervisors" : "role:datadog_monitoring",
    - "os_compute_api:os-hypervisors:discoverable" : "role:datadog_monitoring",
    - "os_compute_api:os-server-diagnostics" : "role:datadog_monitoring",
    - "os_compute_api:os-used-limits" : "role:datadog_monitoring"

```  

> If permissions are already set to a particular rule or role, you can add the new role by appending ` or role:datadog_monitoring`, like so:
>
> `"compute_extension:aggregates": "rule:admin_api"` becomes `"compute_extension:aggregates": "rule:admin_api or role:datadog_monitoring"`

>Save and close the file.

上記の項目に既にルールやロールが設定されている場合は、` or role:datadog_monitoring`を末尾に追記することで権限を設定できます:

`"compute_extension:aggregates": "rule:admin_api"` becomes `"compute_extension:aggregates": "rule:admin_api or role:datadog_monitoring"`

権限設定ファイルを保存し、閉じます。


### Neutron
> Neutron is nice and easy, with only one modification needed. Open its `policy.json` (usually found in `/etc/neutron`) and add `role:datadog_monitoring` to `"get_network"`. Then, save and close the file.

Neutronは、一カ所の変更なので簡単です。`policy.json` (通常は、`/etc/neutron` 以下にあります）を表示し、`"get_network"`項目に、role:datadog_monitoring`を追記します。その後、ファイルを保存し、閉じます。


### Keystone
> Last but not least, you need to configure Keystone so the Agent can access the tenant list. Add `role:datadog_monitoring` to the following directives in Keystone's `policy.json` (usually found in `/etc/keystone`):  

最後になりましたが、Datadog Agentがtenantリストにアクセスできるように、Keystoneの設定を変更する必要があります。`policy.json`(通常は、`/etc/keysstone` 以下にあります）の以下の項目にたし`role:datadog_monitoring`を追記していきます。


```
    - "identity:get_project" : "role:datadog_monitoring",
    - "identity:list_projects" : "role:datadog_monitoring"

```
> Save and close the file.

設定ファイルを保存し、閉じます。

> You may need to restart your Keystone, Neutron and Nova API services to ensure the policy changes are applied.

これまで設定してきたポリシー変更が確実に適応されるように、Keystone, Neutron, Nova API サービスを再起動する必要があります。


## Install the Datadog Agent
> The [Datadog Agent](https://github.com/DataDog/dd-agent) is open-source software that collects and reports metrics from all of your hosts and services so you can view, monitor, and correlate them on the Datadog platform. Installing the Agent usually requires just a single command. 

> Installation instructions are platform-dependent and can be found [here](https://app.datadoghq.com/account/settings#agent).  

> As soon as the Datadog Agent is up and running, you should see your host begin to report its system metrics [in your Datadog account](https://app.datadoghq.com/infrastructure).  

Datadogエージェントは、あなたが、表示モニター、およびDatadogプラットフォーム上で、それらを関連付けることができますので、あなたのホストとサービスのすべてから収集し、レポートメトリクスのオープンソースソフトウェアです。エージェントをインストールすると、通常は単一のコマンドが必要です。

インストール手順は、プラットフォームに依存しており、ここで見つけることができます。

すぐDatadogエージェントが稼働中であるとして、あなたはあなたのホストはあなたのDatadogアカウントでそのシステム・メトリックを報告し始めるはずです。


[![Reporting host in Datadog][default-host]][default-host]

### Configuring the Agent
> With the necessary OpenStack policy changes in place, it is time to configure the Agent to connect to your Keystone server.  

> The location of the Agent configuration directory varies by OS, find it for your platform [here][agent-usage]. In the configuration directory you will find a sample OpenStack configuration file named [openstack.yaml.example][open-yaml]. Copy this file to openstack.yaml, and open it for editing.

> Navigate to the `keystone_server_url` line. Update the URL with the URL of your Keystone server, including the port (usually 5000).  

> Next, under `instances`, change `project id` to the project ID that corresponds to the project associated with the datadog user. To get the project ID, navigate to `<yourHorizonserver>/identity`. See below for an example:

代わりに、必要なOpenStackのポリシーの変更と、あなたのキーストーンサーバーに接続するようにエージェントを構成するための時間です。

エージェントの設定ディレクトリの場所は、ここで使用しているプラットフォームのためにそれを見つけ、OSによって異なります。設定ディレクトリでは、openstack.yaml.exampleという名前のサンプルOpenStackのコンフィギュレーションファイルを検索します。 openstack.yamlするには、このファイルをコピーし、編集用に開きます。

keystone_server_url行に移動します。ポート（通常は5000）を含め、キーストーンサーバーのURLとURLを更新します。

次に、インスタンスの下で、datadogユーザーに関連付けられているプロジェクトに対応するプロジェクトIDにプロジェクトIDを変更します。プロジェクトIDを取得するには、<yourHorizonserver>/アイデンティティに移動します。以下の例を参照してください：


```
instances:
    - name: instance_1 # A required unique identifier for this instance

      # The authorization scope that will be used to request a token from Identity API v3
      # The auth scope must resolve to 1 of the following structures:
      # {'project': {'name': 'my_project', 'domain': 'my_domain} OR {'project': {'id': 'my_project_id'}}
      auth_scope:
          project:
              id: b9d363ac9a5b4cceae228e03639357ae
```

> Finally, you need to modify the authentication credentials to match the user and role created earlier. Navigate to the `# User credentials` section and make the following changes:  

最後に、以前に作成したユーザーとロールに一致するように認証資格情報を変更する必要があります。 ＃ユーザーの資格情報にナビゲートセクションと次のように変更します。電子メールを：


```

      # User credentials
      # Password authentication is the only auth method supported right now
      # User expects username, password, and user domain id

      # `user` should resolve to a structure like {'password': 'my_password', 'name': 'my_name', 'domain$
      user:
          password: my_password
          name: datadog
          domain:
              id: default
```

> Save and close openstack.yaml.

`openstack.yaml`を保存し、閉じます。


## Integrating RabbitMQ with Datadog
> Getting metrics from RabbitMQ requires fewer steps than OpenStack.  
> Start by running the following command to install the management plugin for RabbitMQ: `rabbitmq-plugins enable rabbitmq_management`.  
> This will create a web UI for RabbitMQ on port 15672, and it will expose an HTTP API, which the Datadog Agent uses to collect metrics.

> Once the plugin is enabled, restart RabbitMQ for the changes to take effect:
`service rabbitmq-server restart`.

> Next, navigate to the Agent configuration directory again. Find the sample RabbitMQ config file named [rabbitmq.yaml.example][rabbitmq-yaml] and copy it to rabbitmq.yaml. Open it and navigate to the `instances:` section:

RabbitMQのからメトリックを取得するOpenStackのより少ないステップを必要とします。
RabbitMQの-プラグインがrabbitmq_managementを有効にします。RabbitMQのための管理プラグインをインストールするには、次のコマンドを実行して起動します。
これは、ポート15672上のRabbitMQのWeb UIを作成し、それがDatadogエージェントがメトリックを収集するために使用するHTTP APIを公開します。

プラグインを有効にすると、変更を有効にするため、RabbitMQのを再起動します。
サービスのRabbitMQサーバーの再起動。

次に、再びエージェントの設定ディレクトリに移動します。サンプルRabbitMQの設定ファイルの名前rabbitmq.yaml.exampleを見つけて、それがrabbitmq.yamlにコピーします。それを開いて、インスタンスに移動：セクションを：


```
instances:
    -  rabbitmq_api_url: http://localhost:15672/api/
       rabbitmq_user: guest # defaults to 'guest'
       rabbitmq_pass: guest # defaults to 'guest'
```
> Update the `rabbitmq_user`, `rabbitmq_pass`, and `rabbitmq_api_url` fields appropriately, then save and close the file. 

> After making the appropriate changes to both yaml files, restart the Agent. The command [varies by platform][agent-usage]. For Debian/Ubuntu: `sudo /etc/init.d/datadog-agent restart`

rabbitmq_user、rabbitmq_pass、およびrabbitmq_api_urlフィールドは適切に、ファイルを保存して閉じます更新します。

両方のYAMLファイルに適切な変更を行った後、エージェントを再起動します。コマンドは、プラットフォームによって異なります。 Debianの/ Ubuntuの場合：sudoの/etc/init.d/datadog-agent再起動


## Verify the configuration
> With the configuration changes in place, it's time to see if everything is properly integrated. Execute the Datadog `info` command. On Debian/Ubuntu, run `sudo /etc/init.d/datadog-agent info`

> For other platforms, find the specific command [here][agent-usage].

> If the configuration is correct, you will see a section like the one below in the `info` output:  

代わりに、設定の変更と、それはすべてが適切に統合されているかどうかを確認する時間です。 Datadog infoコマンドを実行します。 Debianの/ Ubuntuの上、実行sudoの/etc/init.d/datadog-agent情報

その他のプラットフォームの場合、ここで特定のコマンドを見つけます。

設定が正しい場合は、情報の出力に以下のようなセクションが表示されます。


```
Checks
======
   [...]
   
    openstack
    ---------
      - instance #0 [OK]
      - Collected 74 metrics, 0 events & 6 service checks
```
> The snippet above shows six service checks in addition to the collected metrics. For OpenStack, the service checks report the availability of your Nova, Neutron, and Keystone APIs as well as checks for individual hypervisors and networks.

> You should also see something like the following for RabbitMQ:

スニペットは、上記収集されたメトリックに加えて、6サービスチェックを示しています。 OpenStackのために、サービスチェックは、個々のハイパーバイザーやネットワークのためのあなたの新星、中性子、およびキーストーンのAPIの利用だけでなく、チェックを報告しています。

また、RabbitMQのために、次のように表示されます。


```
    rabbitmq
    --------
      - instance #0 [OK]
      - Collected 609 metrics, 0 events & 1 service check
```

## Enable the integration
> Finally, click the OpenStack **Install Integration** button inside your Datadog account. The button is located under the Configuration tab in the [OpenStack integration settings][integration-settings].

最後に、OpenStackのは、あなたのDatadogアカウント内部に統合[インストール]ボタンをクリックします。ボタンは、OpenStackの統合設定の[設定]タブの下に位置しています。

  
[![Enable the integration][install-integration]][install-integration]  
> Since the Agent automatically queries RabbitMQ via its API endpoint, you don’t need to enable the RabbitMQ integration in your Datadog account.

エージェントが自動的にそのAPIエンドポイントを経由してのRabbitMQを照会しているので、あなたのDatadogアカウントでRabbitMQの統合を有効にする必要はありません。


## Show me the metrics!
> Once the Agent begins reporting OpenStack metrics, you will see an [OpenStack dashboard][integration-dash] among your list of available dashboards in Datadog.  

> The default OpenStack dashboard displays the key metrics to watch highlighted in our [introduction to Nova monitoring][Part 1].

> You can easily create a tailored dashboard to monitor OpenStack as well as your entire stack by adding additional graphs and metrics from your other systems. For example, you might want to graph Nova metrics alongside metrics from your [Redis databases][redis], or alongside host-level metrics such as network traffic. To start building a custom dashboard, clone the default OpenStack dashboard by clicking on the gear in the upper right of the dashboard and selecting **Clone Dash**.

エージェントは、OpenStackのメトリックを報告し始めると、あなたはDatadogで利用可能なダッシュボードのリストのうち、OpenStackのダッシュボードが表示されます。

デフォルトのOpenStackのダッシュボードには、主要指標は、ノヴァの監視に当社の紹介で強調表示時計に表示されます。

あなたは簡単にOpenStackの監視だけでなく、あなたの他のシステムからの追加のグラフや指標を追加することによって、あなたの全体のスタックに合わせたダッシュボードを作成することができます。たとえば、あなたのRedisデータベースから、または、ネットワークトラフィックなどのホストレベルの指標と並んメトリクスと一緒ノヴァメトリックスをグラフ化することができます。カスタムダッシュボードの作成を開始するには、ダッシュボードの右上にある歯車をクリックしてクローンのダッシュを選択することで、デフォルトOpenStackのダッシュボードのクローンを作成。


[![Clone OpenStack default dash][clone-dash]][clone-dash]

## Diagnosing and Alerting
> Systematically collecting monitoring data serves two broad purposes:  alerting operators in real-time to issues as they develop (alerting), and helping to identify the root cause of a problem (diagnosing). A full-featured monitoring solution does both. With Datadog, you get actionable alerts in real-time, so you can respond to issues as they emerge, plus the high-resolution metrics and historical perspective that you need to dive deep into diagnosing the root cause of an issue.

彼らは（警告）、および（診断）問題の根本原因を特定するのに役立つ開発などの問題にリアルタイムでアラート演算子：体系的に監視データを収集することは二つの大きな目的があります。フル機能を備えた監視ソリューションは、両方を行います。 Datadogを使用すると、リアルタイムで実用的なアラートを取得し、それらが出現するように、あなたは、問題に対応することができ、加えてあなたが問題の根本的な原因を診断中に深く潜る必要があり、高解像度の指標と歴史的な視点を。


### Alerting on Nova metrics
> Once Datadog is capturing and visualizing your metrics, you will likely want to set up some [alerts][alert] to be automatically notified of potential issues. You can set up an alert to notify you of API availability issues, for example.

> Datadog can monitor individual hypervisors, instances, containers, services, and processes—or virtually any combination thereof. For instance, you can monitor all of your Nova nodes, or all hosts in a certain availability zone, or a single key metric being reported by all hosts corresponding to a specific tag.

Datadogをキャプチャし、あなたの評価指標を可視化されたら、自動的に潜在的な問題を通知するためにいくつかのアラートを設定する可能性が高いでしょう。次の例のように、APIの可用性の問題を通知するアラートを設定することができます。

Datadogは、個々のハイパーバイザー、インスタンス、コンテナ、サービス、およびプロセス-またはそれらの事実上の任意の組み合わせを監視することができます。たとえば、特定のアベイラビリティゾーンであなたのノヴァ・ノード、またはすべてのホストのすべてを監視することができ、または単一の主要な指標は、特定のタグに対応するすべてのホストによって報告されています。

## Conclusion
> In this post we’ve walked you through integrating OpenStack Nova and RabbitMQ with Datadog to visualize your key metrics and notify the right team whenever your infrastructure shows signs of trouble.  

> If you’ve followed along using your own Datadog account, you should now have [improved visibility][Part 1] into what’s happening in your environment, as well as the ability to create automated alerts tailored to your infrastructure, usage patterns, and the metrics that are most valuable to your organization.  

> If you don’t yet have a Datadog account, you can [sign up] for a free trial and start monitoring OpenStack Nova right away.

この記事では、我々はあなたの主要な指標を可視化し、インフラストラクチャはトラブルの兆候を示したときに右のチームに通知するDatadogとOpenStackの新星とのRabbitMQを統合する手順を歩いてきました。

あなたがあなた自身のDatadogアカウントを使用してに沿って続いてきた場合、あなたは今、自分の環境だけでなく、インフラストラクチャ、使用パターンに合わせた自動化されたアラートを作成する機能で何が起こっているかを可視化を改善し、かついるはずにとって最も価値のあるメトリックあなたの組織。

あなたはまだDatadogアカウントをお持ちでない場合は、無料試用版にサインアップするとすぐにOpenStackのノヴァの監視を開始することができます。

<iframe width="100%" height="100" style="border: 0;" src="https://go.pardot.com/l/38172/2015-03-02/h6c2r" scrolling="no" type="text/html" frameborder="0" allowtransparency="true"></iframe>

[agent-usage]: http://docs.datadoghq.com/guides/basic_agent_usage/

[alert]: https://www.datadoghq.com/blog/monitoring-101-alerting/

[clone-dash]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-OpenStack/clone-dash.png

[default-dash]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-OpenStack/default-dash.png


[default-host]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-OpenStack/default-host.png

[haproxy]: https://www.datadoghq.com/blog/monitoring-haproxy-performance-metrics/

[install-integration]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-OpenStack/install-integration.png

[integration-dash]: https://app.datadoghq.com/dash/integration/openstack

[integration-settings]: https://app.datadoghq.com/account/settings#integrations/openstack

[Memcached]: https://www.datadoghq.com/blog/collecting-elasticache-metrics-its-redis-memcached-metrics/#memcached

[mysql]: https://www.datadoghq.com/blog/monitoring-rds-mysql-performance-metrics/

[open-yaml]: https://github.com/DataDog/dd-agent/blob/master/conf.d/openstack.yaml.example

[polling]: http://docs.openstack.org/developer/ceilometer/_images/2-2-collection-poll.png

[RabbitMQ]: https://www.datadoghq.com/blog/openstack-monitoring-nova/#rabbitmq-metrics


[rabbitmq-yaml]: https://github.com/DataDog/dd-agent/blob/master/conf.d/rabbitmq.yaml.example

[redis]: http://www.datadoghq.com/blog/how-to-monitor-redis-performance-metrics

[sign up]: https://app.datadoghq.com/signup


[Part 1]: https://www.datadoghq.com/blog/openstack-monitoring-nova
[Part 2]: https://www.datadoghq.com/blog/collecting-metrics-notifications-openstack-nova
[Part 3]: https://www.datadoghq.com/blog/openstack-monitoring-datadog
