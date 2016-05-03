# Collecting monitoring data from OpenStack Nova
> _This post is Part 2 of a 3-part series on monitoring OpenStack's computation module, Nova. [Part 1] explores the key OpenStack metrics available, and [Part 3] shows you how to monitor OpenStack metrics with Datadog._

このポストは、3回に渡るOpenStackのコンピュートモジュールであるNovaの監視のシリーズのPart 2です。[Part 1][Part 1]では、OpenStackのキーメトリックにつて解説しています。そして、[Part 3][Part 3]では、Datadogを使ってOpenStackのメトリックを監視する方法を解説しています。


## Digging into Nova  
> OpenStack Nova offers a variety of sources from which you can collect operational data for monitoring. To get the complete picture of your OpenStack deployment, you will need to combine data collected from various channels.  

> In this post, we will show you how to get information from each of the following categories:  

> - [Nova metrics, including hypervisor, server, and tenant metrics](#NovaMetrics)  
> - [RabbitMQ metrics](#RabbitMQ)  
> - [Notifications](#Notifications)  
> - [Service and process checks](#APIChecks)  

OpenStack Novaの監視のために使う運用データは、様々なソースから集めることができます。そして、OpenStack環境の状態を完全に把握するには、様々なチャネルから収集したデータを関連づけて分析する必要があります。

この記事では、次の紹介するカテゴリーの情報ソースから、監視に必要な情報を収集する方法を紹介します:

- [Nova metrics (hypervisor, server, tenantを含む) メトリクス](#NovaMetrics)  
- [RabbitMQ メトリクス](#RabbitMQ)  
- [通知](#Notifications)  
- [Serviceとprocessチェック](#APIChecks) 


 <div class="anchor" id="NovaMetrics" />

### Collecting OpenStack metrics  
> _Metrics collection_ is done at the source, usually by a [monitoring agent](https://github.com/DataDog/dd-agent) running on the node in question. The agent collects chronologically ordered data points in a timeseries. Collection of timeseries metrics over extended periods gives you the historical context needed to identify what changed, how it changed, and potential causes of the change. Historical baselines are crucial: It is hard to know if something is broken if you don't know what a healthy system looks like. 

> Although OpenStack now ships with its own metering module ([Ceilometer]), it was [not built for monitoring][leveraging-ceilometer]. Ceilometer was created with the intent of capturing and storing critical billing messages. While some Ceilometer data may be a useful supplement to your collected metrics, simply querying Ceilometer is not enough to get useful, actionable information about your OpenStack deployment.  

> Nova offers three different means by which you can collect metrics. You can use:  

> - **API** for Nova server metrics and tenant metrics  
> - **MySQL** for some Nova server metrics, tenant metrics  
> - **[CLI](#CLI)** for hypervisor, server, and tenant metrics  

> Arguably the most efficient method to use is the CLI (command line interface)—it is a one-stop solution to getting all the metrics mentioned in [the first part][Part 1] of this series.  

メトリック収集は、一般的に監視対象のノードで動作している[監視エージェント](https://github.com/DataDog/dd-agent)を使って、そのソースの原点で実行されます。エージェントは、時系列のデータポイントをタイムシーリーズへと収集していきます。長期間にわたるタイムシリーズメトリックの集合は、何が変化したのか、どのように変化したのか、何が潜在的な原因かのかの、時系列的な理由を教えてくれます。過去の実績に基づく判断は重要です:健全に動作しているシステムの状態を知らずに、障害が起きていることを判断するのは難しいことです。

今日、[Ceilometer][Ceilometer]という計量モジュールがOpenstackと共に提供されていますが、このモジュールは、[監視のためには作られていません][leveraging-ceilometer]。Ceilometerは、重要な課金メッセージをキャプチャーし、それらを保存しておく目的で作られました。OpenStack環境において、いくつかのCeilometerのデータは、収集しているメトリックの補助として役に立つかもしれませんが、Ceilometerへ単純な問い合わせだけは、アクションを起こすべき情報を見分けるためには不十分です。

Novaは、ユーザーがメトリックを収集すルことができる、次の三つの異なる手段を提供しています:

- **API**: Novaサーバーメトリクスとtenantメトリクスを収集。
- **MySQL**: Novaサーバーメトリクスとtenantメトリクスを収集。
- **[CLI](#CLI)**: ハイパーバイザー、サーバー、そしてtenantメトリクスを収集。

おそらく、最も効率的な方法は、CLI（コマンドラインインターフェイス）を使うことです。この方法を使えば、このシリーズの[Part 1][Part 1]で紹介したメトリクスを一気に集取することができます。


#### Collecting Nova metrics from the API or MySQL  

> Many of Nova's metrics can be extracted using either the Nova API or an SQL query. For example, to find the total number of VCPUs for a given tenant:  

> * you _could_ query the API using **GET** on the `/v2/<tenant-id>/os-hypervisors/statistics` endpoint  
>     **OR**  
> * run the following SQL query in the `nova` database: `select ifnull(sum(vcpus), 0) from compute_nodes where deleted=0`  

> The main advantages of querying SQL versus the API are faster execution times and lower overhead. However, not all metrics are available via SQL, and future changes to the SQL schema could break queries, whereas API calls should be more resilient to changes.

> Some metrics, like the number of running instances per Compute node, are only available via API endpoint. Thankfully, the Nova API is [well-documented][nova-api] with more than 100 endpoints available—everything from SSH keys to virtual machine image metadata is only a request away. In addition to informational endpoints, the API can also be used to manage your OpenStack deployment. You can add hosts, update quotas, and more—all over HTTP.

Novaに関連したメトリックの多くは、Nova APIまたはSQLクエリを使って収集することができます。例えば、特定のtenantに割り振られたVCPUの総数は次のようになります:

* **GET** メソッドを使い、エンドポイントに向かって次のようなAPIコールを実行することができます。`/v2/<tenant-id>/os-hypervisors/statistics`
  **又は**
* `nova`のデータベースに次のSQLクエリを実行します: `select ifnull(sum(vcpus), 0) from compute_nodes where deleted=0`

APIと比較し、SQLクエリを実行することの利点は、低いオーバーヘッドとより高速な実行時間になります。ただし、すべてのメトリックを、SQLを介して収集することはできず、SQLスキーマが将来変更された場合は、クエリが実行できなくなる原因にもなります。それに対し、APIコールは、変更に対して強いという特徴があります。

コンピュートノードで起動しているインスタンスの数などの幾つかのメトリクスは、APIエンドポイント経由でのみ収集することができます。幸いなことに、NovaのAPIには、100以上のエンドポイントが準備され、[十分に文書化され][nova-api]されています。SSHのキーの情報から、仮想マシンイメージのメタデータの情報まで、全てがAPIリクエスト集取することができます。情報を収集するためにエンドポイントをコールするのに加え、APIを使ってOpenStackの環境を管理することもできます。ホストの追加、Quotasの変更のなど、全てHTTP経由で実行できます。

> Before you can use the API, you must [acquire an authentication token][api-auth]. You can use `curl` or a similar client to get one like so (change your_password to your admin user password and localhost to your Horizon host): 

APIを使用するには、[認証トークンを取得する][api-auth]必要があります。`curl`やそれに類似したクライアントを利用し、以下のようにします。("your_password"には、adminのパスワードを指定してください。 "localhost"には、Horizon hostを指定してくさい。)

```
curl -i \
  -H "Content-Type: application/json" \
  -d '
{ "auth": {
    "identity": {
      "methods": ["password"],
      "password": {
        "user": {
          "name": "admin",
          "domain": { "id": "default" },
          "password": "your_password"
        }
      }
    }
  }
}' \
  http://localhost:5000/v3/auth/tokens ; echo
```

> The above command should return a token in the response header:

上記のコマンドを実行すると、ヘッダ内にトークンを含んだレスポンスが返ってきます：

```
HTTP/1.1 201 Created
Date: Tue, 08 Dec 2015 19:45:36 GMT
Server: Apache/2.4.7 (Ubuntu)
X-Subject-Token: 3939c299ba0743eb94b6f4ff6ff97f6d
Vary: X-Auth-Token
x-openstack-request-id: req-6bf29782-f0a7-4970-b819-5a1c36640d4c
Content-Length: 297
Content-Type: application/json

```

> Note the `X-Subject-Token` field in the output above: this is the authentication token.

`X-Subject-Token` フィールドの部分が、認証トークンになります。


> When it comes to retrieving Nova server metrics, you must use the API. The API endpoint for Nova server metrics is: `/v2.1/​<tenant-id>​/servers/​<server-id>/diagnostics`. Using `curl` and the authentication token acquired above, the request would look something like:

Novaサーバーのメトリクスを収集するには、APIを使用する必要があります。NovaサーバーメトリクスのAPIエンドポイントは、`/v2.1/​<tenant-id>​/servers/​<server-id>/diagnostics`になります。先に入手した認証トークンと`curl`を使うと、リクエストを次のようになります。


```
curl -H "X-Subject-Token: 3939c299ba0743eb94b6f4ff6ff97f6d" http://localhost:5000/v2.1/<tenant-id>/servers/<server-id>/diagnostics
```

> which produces output like below:

このリクエストは、以下のような結果を出力します。


```
[...]
{
    "cpu0_time": 17300000000,
    "memory": 524288,
    "vda_errors": -1,
    "vda_read": 262144,
    "vda_read_req": 112,
    "vda_write": 5778432,
    "vda_write_req": 488,
    "vnet1_rx": 2070139,
    "vnet1_rx_drop": 0,
    "vnet1_rx_errors": 0,
    "vnet1_rx_packets": 26701,
    "vnet1_tx": 140208,
    "vnet1_tx_drop": 0,
    "vnet1_tx_errors": 0,
    "vnet1_tx_packets": 662
}
```

<div class="anchor" id="CLI" />

#### Collecting Nova metrics using Nova's CLI 
> If you don't want to get your hands dirty in API calls or SQL, or are worried about compatibility with future versions, OpenStack provides a command line client for Nova, aptly dubbed `nova`. There are a [large number][nova-client-ref] of available commands, ranging from metric-gathering methods to administrative tools.
  
> The information returned is tenant-dependent, so specify your tenant name, either as a command line argument (`--os-tenant-name <your-tenant-name>`) or as an environment variable (`export OS_TENANT_NAME=<your-tenant-name>`). If the command line complains about a missing username or authentication URL, you can also include them either as additional command line arguments or environment variables, [following the pattern above][env-var].

APIコールやSQLに手を染めたくないなら、又将来のバージョンとの互換性を心配しているなら、OpenStackは、`nova`と呼ばれる、Nova向けにコマンドラインクライアントを提供しています。このクライアントには、メトリクスを収集するためのメソッドから管理ツールに至るまで、[多くのなコマンド][nova-client-ref] が準備されています。

収集できる情報はtenantに紐付けられているので、コマンドラインの引数の中(`--os-tenant-name <your-tenant-name>`)か、環境変数の中(`export OS_TENANT_NAME=<your-tenant-name>`)で、tenant名を指定する必要があります。もしも、ユーザー名や認証URLが指定されておらずコマンドラインクライアントがうまく動作しない場合は、それらについても[上記と同じ][env-var]ように、コマンドラインの引数に追加したり、環境変数に設定することができます。


> All but one of the hypervisor metrics from [part 1][Part 1] of this series can be retrieved with a single command (in this example, the tenant name is _testing_): 

一つのハイパーバイザーメトリクスを除いて、このシリーズの[Part 1][Part 1]で紹介している全てのメトリクスが、単一のコマンドを実行することで取得できます。(次の例では、tenant名は、_testing_ になります。)


```
root@compute-0:~# nova --os-tenant-name testing hypervisor-stats
+----------------------+-------+
| Property             | Value |
+----------------------+-------+
| count                | 2     |
| current_workload     | 1     |
| disk_available_least | 341   |
| free_disk_gb         | 342   |
| free_ram_mb          | 2914  |
| local_gb             | 342   |
| local_gb_used        | 0     |
| memory_mb            | 4002  |
| memory_mb_used       | 1088  |
| running_vms          | 1     |
| vcpus                | 2     |
| vcpus_used           | 1     |
+----------------------+-------+
```
> The only hypervisor metric not covered by the previous command is `hypervisor_load`, which you can view by running `uptime` on your compute node.  

上記のコマンドで収集することのできないハイパーバイザーメトリックは、`hypervisor_load`です。このメトリクスは、コンピュートノードで`uptime`を実行することで見ることができます。


> Getting tenant metrics is just as easy and can be had with the following command:  

tenantメトリクスの取得は非常に簡単で、次のコマンドを実行することで可能です:


```
nova quota-show --tenant <tenant-id>
+-----------------------------+-------+
| Quota                       | Limit |
+-----------------------------+-------+
| instances                   | 10    |
| cores                       | 20    |
| ram                         | 51200 |
| floating_ips                | 10    |
| fixed_ips                   | -1    |
| metadata_items              | 128   |
| injected_files              | 5     |
| injected_file_content_bytes | 10240 |
| injected_file_path_bytes    | 255   |
| key_pairs                   | 100   |
| security_groups             | 10    |
| security_group_rules        | 20    |
| server_groups               | 10    |
| server_group_members        | 10    |
+-----------------------------+-------+
```
> _Note that the command `nova quota-show` requires you pass the tenant id and **not** the tenant name_

`nova quota-show`のコマンドには、tenant名ではなく、tenantのIDを指定していることに注意してください。


> As you can see from the examples above, the Nova CLI is a very powerful tool to add to your monitoring arsenal. With just a handful of commands, you can collect all of the metrics mentioned in [part 1] of this series. To make sure you get the most out of this dynamic tool, check out the [documentation][nova-client-ref] for a list of all available commands with explanations.

上記の例から分かるように、NovaのCLIは、あなたの監視を助ける非常に強力なツールです。幾つかのコマンドを実行するだけで、このシリーズの[Part 1][part 1]で紹介した全てのメトリクスを集取することができます。この強力なツールを十分に使いこなすために、利用可能なコマンドのリストとそれらコマンドについて解説した[ドキュメント][nova-client-ref]を、是非読んでみてください。


<div class="anchor" id="RabbitMQ" />

### Collecting metrics from RabbitMQ  

> RabbitMQ provides a convenient command line client `rabbitmqctl` for accessing its metrics. As described in [part 1][Part 1] of this series, there are four RabbitMQ metrics that are of particular interest for OpenStack monitoring:  

> - count: number of active queues  
> - memory: size of queues in bytes  
> - consumer_utilisation: percentage of time consumers can receive new messages from queue  
> - consumers: number of consumers by queue  

RabbitMQは、自身のメトリックスにアクセスするための便利なコマンドラインクライアントの`rabbitmqctl`を提供します。このシリーズの[Part 1][Part 1]で説明したように、OpenStackの監視をする際に特に重要なRabbitMQのメトリックが四つあります:

- count: アクティブなキューの数
- memory: バイト単位のキューのサイズ
- consumer_utilisation: consumerがキューから新たらしいメッセージを受け取ることのできる時間の割合(1.0が100%を示す)
- consumers: キュー毎のconsumersの数


#### count
> To get a count of the current number of queues, you can run a command such as `rabbitmqctl list_queue name | wc -l` which pipes the output of `rabbitmqctl` into the UNIX word count program—the optional `-l` flag forces `wc` to return only the line count. Because `rabbitmqctl`'s output includes two extraneous text lines, to get your total number of active queues, subtract two from the number returned by the previous command.

現在のキューカウントを取得するには、`rabbitmqctl list_queue name | wc -l`というコマンドを実行します。このコマンドは、`rabbitmqctl` の出力結果をパイプでUNIXのワードカウントプログラムの渡し、`wc`の`-l`オプションを使って行数を出力しています。尚、`rabbitmqctl`の出力には、2行のキューには関係の無い行が含まれているため、先のコマンドで得た数値から2を引いて、アクティブキューの総数を取得します。


#### memory
> Extracting the size of queues in memory requires a similar command. Running `rabbitmqctl list_queues name memory | grep compute` will show you the memory size of all Nova-related queues (in bytes), like in the output below:

メモリ内のキューのサイズを収集するにも類似のコマンドを実行します。`rabbitmqctl list_queues name memory | grep compute`を実行することで、以下の出力結果のように、Novaに関連したキューのメモリーサイズがバイト単位で表示されます。


```
[...]
compute	9096
compute.node0	 9096
compute_fanout_ec3d52fdbe194d89954a3935a8090157 21880
```

#### consumer_utilisation
> Are you noticing a pattern with these commands? To get the consumer utilization rates for all queues, run `rabbitmqctl list_queues name consumer_utilisation`, which produces output resembling the following (recall that a utilization rate of 1.0, or 100 percent, means that the queue never has to wait for its consumers): 

これらのコマンドのパターンが分かってきましたか。全てのキューに関しconsumerのutilisation率を集取するには、`rabbitmqctl list_queues name consumer_utilisation`を実行します。このコマンドは以下のような内容を出力します。(utilisation率が1.0で100％の場合、キューはconsumerがメッセージを受け付けるのを待つことはありません。):


```
Listing queues ...
aliveness-test
cert	1.0
cert.devstack	1.0
cert_fanout_c0a7360141564001b0656bf4cd947dab	1.0
cinder-scheduler	1.0
cinder-scheduler.devstack	1.0
[...]
```

#### consumers
> Last but not least, to get a count of the active consumers for a given queue, run: `rabbitmqctl list_queues name consumers | grep compute`. 

最後になりましたが、特定のキューに対してアクティブなconsumerの数を取得するには、`rabbitmqctl list_queues name consumers | grep compute`を実行します。


> You should see something like this:  

以下のような内容が出力されます:


```
[...]
compute	1
compute.node0 	1
compute_fanout_ec3d52fdbe194d89954a3935a8090157   1
```
>Remember, few queues should have zero consumers.

幾つかのキューは、consumerの値がzeroになっていることを思い出してください。


<div class="anchor" id="Notifications" />

### Collecting Notifications  
> [Notifications][notification system] are emitted on [events][monitoring-101-events] such as instance creation, instance deletion, and resizing operations. Built around an [AMQP] pipeline (typically [RabbitMQ]), Nova is configured to emit notifications on [about 80 events][paste-events]. A number of tools have emerged that collect OpenStack events, but OpenStack's own [StackTach] leads the pack in terms of feature-completeness and documentation. StackTach is especially useful because it needs no updates to handle new events, meaning it can continue to track events in the face of module upgrades.

> If you’re just interested in a quick-and-dirty notification listener you can build around, check out this [gist]. Listening in on events requires the `kombu` Python package. [This script][virtualenv] will create a virtual environment and run the event listener. The OpenStack documentation has [additional resources][roll-your-own-listener] on crafting your own notification listener.

[通知][notification system]は、インスタンスの作成、削除、サイズの変更など[イベント][monitoring-101-events]が発生した際に送信されます。 AMQPパイプライン（一般的にはRabbitMQ）を中心に構築され、Novaの場合、およそ[80種類のイベント][paste-events]に関して通知を送信します。OpenStackのイベントを集取するために幾つかのツールが生まれてきてはいます。しかし、OpenStack自身が提供している[StackTach][StackTach]が、機能のカバー範囲とドキュメント存在という点で他のツールからリードしてます。更にStackTachは、新たいイベントに足してもアップデートを必要とせず、モジュールをアップデートすることで引き続きイベントを追跡できるため、特に便利です。

もしもあなたが、通知のリスナーを素早く簡単に用意したいのなら、この[gist][gist]の例を参考にすることができます。イベントを監視続けるにはPythonパッケージの`kombu`必要とします。[このスクリプト][vritualenv]は、仮想の実行環境を作成し、イベントリスナーを起動します。OpenStackのドキュメントには、独自の通知リスナーを作るための[更に詳しい記述][roll-your-own-listener]もあります。


> The truncated snippet below is an example of notification payloads received after initiating termination of an instance:

以下に部分的に切り出したスニペットは、インスタンスの終了を開始した後、受信した通知ペイロードの例です:


```
================================================================================
{ 
[...]

 'event_type': 'compute.instance.delete.start',
 'message_id': '45731b78-ceba-48a4-b80c-3ef971dd632d',
 'payload': {             
'image_meta': {             
'progress': u'',
            'ramdisk_id': 'd768f34d-bb21-4afa-97ed-8d7143a43751',
            'reservation_id': 'r-gz5vu80w',
            'root_gb': 1,
            'state': 'active',
            'state_description': 'deleting',
            'tenant_id': '3fb0de5c53434c54829b7150129dec61',
            'terminated_at': u'',
            'user_id': 'adf56761cda54d4c99de59dc50fd6c06',
            'vcpus': 1},
 'priority': 'INFO',
 'publisher_id': 'compute.devstack',
 'timestamp': '2015-11-24 18:22:51.665797'}

================================================================================
{
[...]

 'event_type': 'compute.instance.delete.end',
 'message_id': '207d6503-2e28-4ec4-97e7-1f3a2a67f6ba',
 'payload': {
             'image_meta': {
             'progress': u'',
             'ramdisk_id': 'd768f34d-bb21-4afa-97ed-8d7143a43751',
             'reservation_id': 'r-gz5vu80w',
             'root_gb': 1,
             'state': 'deleted',
             'state_description': u'',
             'tenant_id': '3fb0de5c53434c54829b7150129dec61',
             'terminated_at': '2015-11-24T18:22:53.479747',
             'user_id': 'adf56761cda54d4c99de59dc50fd6c06',
             'vcpus': 1},
 'priority': 'INFO',
 'publisher_id': 'compute.devstack',
 'timestamp': '2015-11-24 18:22:53.848974'}
```
> By comparing the timestamps from both events, you can see it took approximately 2.2 seconds to destroy the instance.

両方のイベントのタイムスタンプを比較することにより、インスタンスを破棄するのに約2.2秒かかていることがわかります。


> Note that in the snippet above there are _two_ notifications emitted: one when initiating instance termination and one that signals the successful completion of a termination operation. This is a common pattern for events in OpenStack: emit one notification when the operation has begun, and another upon completion.

上記のスニペットでは、 二つの通知が送信されていることに注目してください: 一つ目がインスタンス終了が開始した時で、二つ目がインスタンス終了の操作が完了した時です。この流れは、OpenStackのイベントの流れとして一般的なパターンです: まず、操作が開始する際に通知を送信し、そしてその操作が完了した際に別の通知を送信します。


> When combined with collected metrics, notifications give valuable perspective and insight into the potential causes for changes in system behavior. For example, you can measure hypervisor task execution time with events, and correlate that information with the API response time. (_For the curious:_ [in practice][api-vs-load] excessive load on the hypervisor does not appear to affect API response time much.)

別途収集されているメトリクスと組み合わせた場合、通知は、システムの挙動の変化について、潜在的な原因に関する貴重な視点と洞察を与えます。例えば、イベントを使ってハイパーバイザ・タスクの実行時間を測定することができ、それをAPIのレスポンス時間と相関させることができます。(好奇心として: [実際][api-vs-load]に、ハイパーバイザーの過度な負荷は、APIのレスポンス時間にあまり影響をおよびしません。)


<div class="anchor" id="APIChecks" />

### Service and API checks 
> _Service checks_ and _API checks_ are used to determine if a service is responsive. API checks generally **GET** or **POST** to a specific API endpoint and verify the response.   

> There are a number of tests you can perform to check the health of the Nova API. However, all tests generally boil down to one of two categories: simple or intrusive.  

_Service checks_と_API checks_は、サービスが応答するかどうかを判定するために使われています。API checksは、一般的に、APIエンドポイントに対し**GET**か**POST**のリクエストを送信し、応答を確認します。

NovaのAPIの健全性を確認するには幾つかのテストを実行することができます。しかし、最終的には次の2つのテストに分類することができます: simple又はintrusiveです。


> A simple API check reads (usually static) data from an endpoint and verifies that the information received is as expected. A simple API check would be polling the quota information for a project with a **GET** request to `/v2.1/​<tenant-id>​/limits`.

simple API checkは、エンドポイントからデータ(通常は静的)を読み込み、受信された情報が期待通りで有ることを検証します。
例として、simple API checkは、プロジェクトのquotaの情報を、**GET**リクエストを使って`/v2.1/​<tenant-id>​/limits`から調査します。


> Intrusive checks modify the state of the receiving endpoint. A typical intrusive check might start by setting a value and optionally following with a request to read or verify the newly created value. Some kind of cleanup would then follow to remove the added values.

> An intrusive check for the Nova API would be something like creating and deleting a key pair, with the following set of API calls (checking the status codes returned):  

> * **POST** `/v2.1/<tenant-id>/os-keypairs '{"keypair": {"name": "test"}}'`  
> * **DELETE** `/v2.1/<tenant-id>/os-keypairs/test`  

Intrusive checksは、リクエストを受けているエンドポイントの状態を変更します。一般的なintrusive checkは、まず値を設置し、その後その値を読み込むためのリクエスか、新しく設定した値を確認するためのリクエストを送信します。そして、最後に、その設定した値を削除するためのクリーンアップリクエストを送信します。

Nova APIのintrusive checkは、キーペアーを作成し、それを削除するようなリクエストになります。次のようなAPIコールで、結果として受信したステータスコードを検証します。

* **POST** `/v2.1/<tenant-id>/os-keypairs '{"keypair": {"name": "test"}}'`  
* **DELETE** `/v2.1/<tenant-id>/os-keypairs/test`  


## Conclusion
> In this article we've discussed a number of ways to check the health of your Compute cluster. 
  
> With so much data available from disparate sources, getting the information you want all in one place can be a challenge. Luckily, Datadog can help take the pain out of the process. At Datadog, we have built an integration with Nova so you can begin collecting and monitoring its metrics with a minimum of setup.  

> Follow along to [part 3][Part 3] to learn how Datadog can help you monitor Nova.

この記事では、コンピュートクラスターの健全性をチェックする方法について解説してきました。

様々な情報源に分指したデーターを取り扱うために、必要な全ての情報を一つの場所に集めるのは簡単なことではありません。幸いなことに、Datadogを使うことで、この集約のプロセスの手間をなくすことができるようになります。Datadogでは、ユーザーが最低限のセットアップで、メトリクスの収集と監視ができるように、Novaをターゲットにしたインテグレーションを開発しました。

Novaの監視にDatadogがどのように活用できるかは、[part 3][Part 3]に読み進んで確認してください。


<iframe width="100%" height="100" style="border: 0;" src="https://go.pardot.com/l/38172/2015-03-02/h6c2r" scrolling="no" type="text/html" frameborder="0" allowtransparency="true"></iframe>

[Part 1]: http://datadoghq.com/blog/openstack-monitoring-nova
[Part 2]: http://datadoghq.com/blog/collecting-metrics-notifications-openstack-nova
[Part 3]: http://datadoghq.com/blog/openstack-monitoring-datadog

[AMQP]: http://docs.openstack.org/developer/nova/rpc.html
[api-auth]: http://docs.openstack.org/developer/keystone/api_curl_examples.html
[architecture]: http://docs.openstack.org/developer/nova/architecture.html

[api-vs-load]: https://javacruft.wordpress.com/2014/06/18/168k-instances/
[Ceilometer]: https://wiki.openstack.org/wiki/Telemetry
[Datadog events]: http://docs.datadoghq.com/guides/dogstatsd/#events
[env-var]: https://wiki.openstack.org/wiki/CLIAuth
[gist]: https://gist.github.com/vagelim/64b355b65378ecba15b0

[paste-events]: http://paste.openstack.org/show/54140/

[leveraging-ceilometer]: https://wiki.openstack.org/wiki/MONaaS

[monitoring-101-events]: https://www.datadoghq.com/blog/monitoring-101-collecting-data#events

[notification system]: https://wiki.openstack.org/wiki/NotificationSystem
[nova-api]: http://developer.openstack.org/api-ref-compute-v2.1.html
[nova-client-ref]: http://docs.openstack.org/cli-reference/content/novaclient_commands.html

[RabbitMQ]: https://app.datadoghq.com/account/settings#integrations/rabbitmq

[roll-your-own-listener]: http://docs.openstack.org/developer/taskflow/notifications.html

[StackTach]: http://stacktach.readthedocs.org/

[virtualenv]: https://gist.github.com/vagelim/98c8792ba12dc8f90341

