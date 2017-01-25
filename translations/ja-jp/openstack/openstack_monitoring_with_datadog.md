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

[Datadog Agent](https://github.com/DataDog/dd-agent)は、監視対象の全てのホストやサービスから、メトリクスを収集し、Datadogのプラットフォームに転送するオープンソースのソフトウェアです。Datadogのプラットフォーム上では、収集したメトリクスを基に、それらのデータを可視化したり、アラートを設定しり、相関性を見ることができます。通常、Agentのインストールは、単一のコマンドの実行で完了します。


> Installation instructions are platform-dependent and can be found [here](https://app.datadoghq.com/account/settings#agent).  

インストール手順は、プラットフォームに依存しています。詳細に関しては、次の[リンク](https://app.datadoghq.com/account/settings#agent)を参照してくさい。


> As soon as the Datadog Agent is up and running, you should see your host begin to report its system metrics [in your Datadog account](https://app.datadoghq.com/infrastructure).  

Datadog Agentが起動しメトリクスの送信が始まると、[Datadogアカウント](https://app.datadoghq.com/infrastructure)内に、そのホストから受信しているシステムメトリクスを確認することができるようになります。


[![Reporting host in Datadog][default-host]][default-host]

### Configuring the Agent
> With the necessary OpenStack policy changes in place, it is time to configure the Agent to connect to your Keystone server.  

既に、OpenStack関連のポリシー変更が完了しテイル場合は、Datadog AgentをKeystoneサーバーと接続するための設定をします。


> The location of the Agent configuration directory varies by OS, find it for your platform [here][agent-usage]. In the configuration directory you will find a sample OpenStack configuration file named [openstack.yaml.example][open-yaml]. Copy this file to openstack.yaml, and open it for editing.

Datadog Agentの設定ファイルの保存先は、OSによって異なります。次の[リンク先][agent-usage]から使用中のOSの保存先を確認してください。設定ファイルの保存先から、[openstack.yaml.example][open-yaml]を見つけ出します。このファイルを、`openstack.yaml`というファイル名でコピーし、編集を開始します。


> Navigate to the `keystone_server_url` line. Update the URL with the URL of your Keystone server, including the port (usually 5000).  

設定ファイルを、`keystone_server_url`と書かれた行まで移動します。その行のURLの部分をKeystoneサーバーのポート番号付きのURLで書き換えます。(通常、Keystroneは5000番ポートでリッスンしています)


> Next, under `instances`, change `project id` to the project ID that corresponds to the project associated with the datadog user. To get the project ID, navigate to `<yourHorizonserver>/identity`. See below for an example:

次に、`instances`の部分で、Datadogユーザーに対応したプロジェクトのプロジェクトIDを、`project`項目の`id`の部分に追記していきます。プロジェクトIDを確認するには、`<yourHorizonserver>/identity`を実行してください。記載内容に関しては、以下の例を参照してください:


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

次に、上記で作成したユーザーとロールに一致するように認証資格情報を書き換えていきます。`# User credentials`のセクションまで移動し、次のような変更を加えていきます:


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

RabbitMQからメトリックを取得する設定は、OpenStackのそれより少ないステップで完了します。


> Start by running the following command to install the management plugin for RabbitMQ: `rabbitmq-plugins enable rabbitmq_management`.  
> This will create a web UI for RabbitMQ on port 15672, and it will expose an HTTP API, which the Datadog Agent uses to collect metrics.

`rabbitmq-plugins enable rabbitmq_management`のコマンドを実行して、RabbitMQにプラグインをインストールするところから始めます。このコマンドは、RabbitMQサーバーの15672ポートにWeb UIを作成し、Datadog Agentがメトリクスを収集するためのHTTP APIを公開してくれます。


> Once the plugin is enabled, restart RabbitMQ for the changes to take effect:
`service rabbitmq-server restart`.

このプラグインを有効にした後、変更を有効にするためにRabbitMQを再起動します。
`service rabbitmq-server restart`


> Next, navigate to the Agent configuration directory again. Find the sample RabbitMQ config file named [rabbitmq.yaml.example][rabbitmq-yaml] and copy it to rabbitmq.yaml. Open it and navigate to the `instances:` section:

次に、再びDatadog Agentの設定ディレクトリに移動します。[rabbitmq.yaml.example][rabbitmq-yaml]を、`rabbitmq.yaml`にコピーし、編集を開始します。編集画面で、`instances:`セクションまで移動します:


```
instances:
    -  rabbitmq_api_url: http://localhost:15672/api/
       rabbitmq_user: guest # defaults to 'guest'
       rabbitmq_pass: guest # defaults to 'guest'
```
> Update the `rabbitmq_user`, `rabbitmq_pass`, and `rabbitmq_api_url` fields appropriately, then save and close the file. 

`rabbitmq_user`, `rabbitmq_pass`, `rabbitmq_api_url`のフィールドは適切に更新し、ファイルを保存して閉じます。


> After making the appropriate changes to both yaml files, restart the Agent. The command [varies by platform][agent-usage]. For Debian/Ubuntu: `sudo /etc/init.d/datadog-agent restart`

以上2つのyamlファイルが適切に変更できたら、Datadog Agentを再起動します。[再起動のコマンド][agent-usage]は、OSによって異なります。Debian/Ubuntuの場合は、`sudo /etc/init.d/datadog-agent restart`になります。


## Verify the configuration
> With the configuration changes in place, it's time to see if everything is properly integrated. Execute the Datadog `info` command. On Debian/Ubuntu, run `sudo /etc/init.d/datadog-agent info`

設定を変更し、Datadog Agentを再起動した後は、設定が正しく反映され、インテグレーションが正しく動作しているか確認します。Datadog Agentの動作確認をするには、`info` オプションをつけて`datadog-agent`コマンドを実行します。Debian/Ubuntuの場合は、`sudo /etc/init.d/datadog-agent info`になります。


> For other platforms, find the specific command [here][agent-usage].

他のOSに関しては必要なコマンドの書式を、次の[リンク][agent-usage]より参照してください。


> If the configuration is correct, you will see a section like the one below in the `info` output:  

全てが正しく設定されている場合は、`info`コマンドの出力結果に、以下のようなセクションの内容が表示されます。


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

上記の出力結果からは、74個のメトリクスと6個のサービスチェックが動作していることが確認できます。OpenStackの場合、サービスチェックは、Nova, Neutron, KeystoneのAPIとハイパーバイザーとネットワークをチェックし、動作状況を報告しています。


> You should also see something like the following for RabbitMQ:

RabbitMQのためには、以下のような内容が表示されます:


```
    rabbitmq
    --------
      - instance #0 [OK]
      - Collected 609 metrics, 0 events & 1 service check
```

## Enable the integration
> Finally, click the OpenStack **Install Integration** button inside your Datadog account. The button is located under the Configuration tab in the [OpenStack integration settings][integration-settings].

最後に、OpenStackインテグレーションの**Install Integration**ボタンをクリックします。このボタンは、Datadogのダッシュボードの`Configuration`タブ内の、[OpenStack integration][integration-settings]タイルをクリックすると表示されます。


[![Enable the integration][install-integration]][install-integration]  
> Since the Agent automatically queries RabbitMQ via its API endpoint, you don’t need to enable the RabbitMQ integration in your Datadog account.

OpenStackのケースでは、Datadog Agentは、自動的にRabbitMQのエンドポイントAPIを経由してメトリクスを収集しているため、ダッシュボード上でRabbitMQのインテグレーションを有効にする必要はありません。


## Show me the metrics!
> Once the Agent begins reporting OpenStack metrics, you will see an [OpenStack dashboard][integration-dash] among your list of available dashboards in Datadog.

Datadog AgentがOpenStackのメトリクスを送信し始めると、インテグレーション用のダッシュボード一覧の中に[OpenStack dashboard][integration-dash]が表示されます。


> The default OpenStack dashboard displays the key metrics to watch highlighted in our [introduction to Nova monitoring][Part 1].

OpenStackのインテグレーション用のダッシュボードには、このシリーズの["Part 1: introduction to Nova monitoring"][Part 1]で取り上げたキーメトリクスが表示されています。


> You can easily create a tailored dashboard to monitor OpenStack as well as your entire stack by adding additional graphs and metrics from your other systems. For example, you might want to graph Nova metrics alongside metrics from your [Redis databases][redis], or alongside host-level metrics such as network traffic. To start building a custom dashboard, clone the default OpenStack dashboard by clicking on the gear in the upper right of the dashboard and selecting **Clone Dash**.

様々なOpenStackの環境の監視に併せ、追加要素のメトリクスを表示するためのグラフを追加し専用のダッシュボードを簡単に作ることができます。例えば、[Redis databases][redis]から集取したメトリクスやネットワークトラフィックなどのホストレベルのメトリクスを、Novaのメトリクスと一緒にグラフ化したいとします。カスタムダッシュボードを構成してく場合は、既存のOpenStackのダッシュボードをクローンするところから始めます。既存のOpenStackのダッシュボードの右上にある歯車のマークをクリックし、**Clone Dash**を選択することで、カスタム用のダッシュボードのベースを新しく生成することができます。


[![Clone OpenStack default dash][clone-dash]][clone-dash]

## Diagnosing and Alerting
> Systematically collecting monitoring data serves two broad purposes:  alerting operators in real-time to issues as they develop (alerting), and helping to identify the root cause of a problem (diagnosing). A full-featured monitoring solution does both. With Datadog, you get actionable alerts in real-time, so you can respond to issues as they emerge, plus the high-resolution metrics and historical perspective that you need to dive deep into diagnosing the root cause of an issue.

体系的に監視データを収集することは二つの大きな目的があります: まず第一にアラートです、問題が発生すると同時にリアルタイムでオペレーターの警告します。次に分析です、問題の根本原因を特定するのを助けます。フル機能を備えた監視ソリューションでは、両方を行っています。Datadogを使用すると、リアルタイムで実行価値のあるアラートを受けることができます。そして、問題が表面化すると同時に対応できるようになります。更に、高解像度のメトリクスと過去に渡って保存されているデータは、問題の根本原因を深く探っていく際の基本データを提供してくれます。


### Alerting on Nova metrics
> Once Datadog is capturing and visualizing your metrics, you will likely want to set up some [alerts][alert] to be automatically notified of potential issues. You can set up an alert to notify you of API availability issues, for example.

Datadogを使ってメトリクスを収集し可視化できるようになると、問題の可能性がある場合に自動で通知されるように[アラート][alert]を設定したくなるでしょう。例えば、APIの応答状障害に関してアラートを設定することができます。


> Datadog can monitor individual hypervisors, instances, containers, services, and processes—or virtually any combination thereof. For instance, you can monitor all of your Nova nodes, or all hosts in a certain availability zone, or a single key metric being reported by all hosts corresponding to a specific tag.

Datadogは、個々のハイパーバイザー, インスタンス, コンテナ, サービス, プロセスと、それらの組み合わせを監視することができます。そして、タグを指定することで、Novaの全てのノードや、特定のアベイラビリティゾーンの全てのホストや、全てのホストから収集した単一キーメトリクスを特定することができます。


## Conclusion
> In this post we’ve walked you through integrating OpenStack Nova and RabbitMQ with Datadog to visualize your key metrics and notify the right team whenever your infrastructure shows signs of trouble.  

今回のポストでは、Datadogでキーメトリクスを可視化し、インフラがトラブルの兆候を示したときに適切なチームに通知するためのOpenStack NovaとRabbitMQの連携の手順を解説してきました。


> If you’ve followed along using your own Datadog account, you should now have [improved visibility][Part 1] into what’s happening in your environment, as well as the ability to create automated alerts tailored to your infrastructure, usage patterns, and the metrics that are most valuable to your organization.  

Datadogアカウントを使って、この手順をここまで進めていたなら、あなたのOpenStackの環境で何が起きているかを[具体的に理解するための視界][Part 1]を手に入れることができたでしょう。それと同時に、あなたのインフラに合わせた自動化されたアラートや、インフラの使用パターンや、組織にとって最も重要なメトリクスも手に入れることができたでしょう。


> If you don’t yet have a Datadog account, you can [sign up] for a free trial and start monitoring OpenStack Nova right away.

もしも未だDatadogのアカウントを持っていないなら、無料トライアルへ[ユーザー登録][sign up]すれば直ちにOpenStack Novaの監視を始めることができます。


<iframe width="100%" height="100" style="border: 0;" src="https://go.pardot.com/l/38172/2015-03-02/h6c2r" scrolling="no" type="text/html" frameborder="0" allowtransparency="true"></iframe>

[agent-usage]: http://docs.datadoghq.com/guides/basic_agent_usage/

[alert]: https://www.datadoghq.com/blog/monitoring-101-alerting/

[clone-dash]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-OpenStack/clone-dash.png

[default-dash]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-OpenStack/default-dash.png


[default-host]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-OpenStack/default-host.png

[haproxy]: https://www.datadoghq.com/blog/monitoring-haproxy-performance-metrics/

[install-integration]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-12-OpenStack/install-integration.png

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
