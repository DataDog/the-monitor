# Collecting monitoring data from OpenStack Nova
> _This post is Part 2 of a 3-part series on monitoring OpenStack's computation module, Nova. [Part 1] explores the key OpenStack metrics available, and [Part 3] shows you how to monitor OpenStack metrics with Datadog._

この投稿は、OpenStackのの計算モジュール、ノヴァの監視の3回シリーズの第2です。パート1は、キーOpenStackのメトリックを使用可能に探り、そして第3部は、どのようにDatadogとOpenStackのメトリックを監視する方法を示します。


## Digging into Nova  
> OpenStack Nova offers a variety of sources from which you can collect operational data for monitoring. To get the complete picture of your OpenStack deployment, you will need to combine data collected from various channels.  

OpenStackの新星は、あなたが監視のための運用データを収集することができ、そこから、さまざまなソースを提供しています。あなたのOpenStackの展開の全体像を取得するには、様々なチャネルから収集されたデータを結合する必要があります。


> In this post, we will show you how to get information from each of the following categories:  

> - [Nova metrics, including hypervisor, server, and tenant metrics](#NovaMetrics)  
> - [RabbitMQ metrics](#RabbitMQ)  
> - [Notifications](#Notifications)  
> - [Service and process checks](#APIChecks)  

この記事では、我々はどのように、次の各カテゴリから情報を取得する方法を紹介します：

- ハイパーバイザ、サーバ、およびテナントメトリックなどノヴァメトリックス、
- RabbitMQのメトリック
- お知らせ
- サービスとプロセスをチェックします


 <div class="anchor" id="NovaMetrics" />

### Collecting OpenStack metrics  
> _Metrics collection_ is done at the source, usually by a [monitoring agent](https://github.com/DataDog/dd-agent) running on the node in question. The agent collects chronologically ordered data points in a timeseries. Collection of timeseries metrics over extended periods gives you the historical context needed to identify what changed, how it changed, and potential causes of the change. Historical baselines are crucial: It is hard to know if something is broken if you don't know what a healthy system looks like. 

メトリックの収集は、通常、問題のノードで実行されている監視エージェントによって、ソースで行われます。エージェントは、年代順に時系列のデータポイントを命じ収集します。長期間にわたる時系列メトリックのコレクションはあなたにそれがどのように変化するか、変更するものを識別するために必要な歴史的文脈、および変更の潜在的な原因を提供します。歴史的なベースラインが重要である：あなたが健康システムがどのように見えるかわからない場合は、何かが壊れているかどうかを知ることは困難です。


> Although OpenStack now ships with its own metering module ([Ceilometer]), it was [not built for monitoring][leveraging-ceilometer]. Ceilometer was created with the intent of capturing and storing critical billing messages. While some Ceilometer data may be a useful supplement to your collected metrics, simply querying Ceilometer is not enough to get useful, actionable information about your OpenStack deployment.  

独自の計量モジュール（雲高計）とOpenStackの今船が、監視のために構築されていませんでした。雲高計をキャプチャして、重要な課金メッセージを格納する目的で作成されました。いくつかの雲高計のデータはあなたの収集されたメトリックに役立つサプリメントかもしれないが、単に雲高計を照会すると、OpenStackの展開に関する有用な、実用的な情報を取得するのに十分ではありません。

> Nova offers three different means by which you can collect metrics. You can use:  

> - **API** for Nova server metrics and tenant metrics  
> - **MySQL** for some Nova server metrics, tenant metrics  
> - **[CLI](#CLI)** for hypervisor, server, and tenant metrics  

ノヴァは、あなたがメトリックを収集することができることにより、三つの異なる手段を提供しています。あなたが使用することができます。

- ノヴァサーバーメトリクスとテナントの指標のためのAPI
- MySQLのいくつかのノヴァサーバメトリクス、テナントメトリックの
- ハイパーバイザ、サーバ、およびテナントメトリックのCLI

> Arguably the most efficient method to use is the CLI (command line interface)—it is a one-stop solution to getting all the metrics mentioned in [the first part][Part 1] of this series.  

間違いなく使用するのが最も効率的な方法は、このシリーズの最初の部分で述べたすべてのメトリックを取得するワンストップソリューションです-it CLI（コマンドラインインターフェイス）があります。


#### Collecting Nova metrics from the API or MySQL  

> Many of Nova's metrics can be extracted using either the Nova API or an SQL query. For example, to find the total number of VCPUs for a given tenant:  

> * you _could_ query the API using **GET** on the `/v2/<tenant-id>/os-hypervisors/statistics` endpoint  
>     **OR**  
> * run the following SQL query in the `nova` database: `select ifnull(sum(vcpus), 0) from compute_nodes where deleted=0`  

ノヴァのメトリックの多くは、ノヴァAPIまたはSQLクエリのいずれかを使用して抽出することができます。例えば、与えられたテナントのためのVCPU数の合計を検索します：

- あなたは/ V2/<テナント-ID>/ OS-ハイパーバイザー/統計エンドポイントでGETを使用してAPIを照会することができ
    **OR**
- 新星データベースで次のSQLクエリを実行します。select IFNULL（合計（仮想CPU）を、0）compute_nodesから=0削除場所


> The main advantages of querying SQL versus the API are faster execution times and lower overhead. However, not all metrics are available via SQL, and future changes to the SQL schema could break queries, whereas API calls should be more resilient to changes.

APIに対してSQLを照会することの主な利点は、より高速な実行時間と低いオーバーヘッドがあります。ただし、すべてのメトリックは、SQLを介して利用可能であり、API呼び出しが変化に対してより弾力的でなければならないのに対し、SQLスキーマの将来の変更は、クエリを中断する可能性があります。


> Some metrics, like the number of running instances per Compute node, are only available via API endpoint. Thankfully, the Nova API is [well-documented][nova-api] with more than 100 endpoints available—everything from SSH keys to virtual machine image metadata is only a request away. In addition to informational endpoints, the API can also be used to manage your OpenStack deployment. You can add hosts, update quotas, and more—all over HTTP.

いくつかの指標は、計算ノードあたりのインスタンスを実行している数と同じように、APIエンドポイント経由でのみ使用可能です。ありがたいことに、ノヴァのAPIは、要求だけ離れた仮想マシンイメージのメタデータへのSSHキーから100以上のエンドポイントが利用可能-すべてにある、よく文書化されています。情報のエンドポイントに加えて、APIはまたあなたOpenStackの展開を管理するために使用することができます。あなたは、ホスト、更新クォータを追加し、より多くの、すべてのHTTP上ですることができます。


> Before you can use the API, you must [acquire an authentication token][api-auth]. You can use `curl` or a similar client to get one like so (change your_password to your admin user password and localhost to your Horizon host): 

あなたはAPIを使用する前に、認証トークンを取得する必要があります。あなたは（あなたのホライゾンホストにあなたの管理者ユーザーのパスワードとローカルホストにyour_passwordに変更する）ようなので1を得るために、カールまたは類似のクライアントを使用することができます。


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

上記のコマンドは、レスポンスヘッダ内のトークンを返す必要があります：

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

> When it comes to retrieving Nova server metrics, you must use the API. The API endpoint for Nova server metrics is: `/v2.1/​<tenant-id>​/servers/​<server-id>/diagnostics`. Using `curl` and the authentication token acquired above, the request would look something like:

上記の出力で、 `X-件名-Token`フィールドに注意してください。これは、認証トークンです。

それはノヴァ・サーバーのメトリックを取得することになると、あなたは、APIを使用する必要があります。ノヴァ・サーバー・メトリックのAPIエンドポイントは、次のとおりです。`/v2.1/<テナント-ID>/サーバー/<サーバーID>/ diagnostics`。 `curl`と上記取得した認証トークンを使用して、要求は何かを次のようになります。

```
curl -H "X-Subject-Token: 3939c299ba0743eb94b6f4ff6ff97f6d" http://localhost:5000/v2.1/<tenant-id>/servers/<server-id>/diagnostics
```

> which produces output like below:

これは、以下のような出力を生成します。


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

> All but one of the hypervisor metrics from [part 1][Part 1] of this series can be retrieved with a single command (in this example, the tenant name is _testing_): 

あなたはAPI呼び出しまたはSQLで手が汚れて取得したい、または将来のバージョンとの互換性を心配しているしない場合は、OpenStackのは、適切に新星と呼ばノヴァのためのコマンドラインクライアントを、提供します。管理ツールへのメトリック収集の方法に至るまで使用可能なコマンドの多くは、あります。

返された情報は、テナントに依存しているので、あなたのテナント名を指定して、いずれかのコマンドライン引数として（--osテナント名<あなたのテナント名>）、または環境変数として（輸出OS_TENANT_NAME=<あなたの-テナント）>という名前を付けます。コマンドラインが欠落しているユーザー名または認証URL言っている場合、あなたはまた、上記のパターンを次のように追加のコマンドライン引数や環境変数、どちらかそれらを含めることができます。

このシリーズのパート1からのハイパーバイザーのメトリックの1つが、すべてが（この例では、テナント名がテストしている）単一のコマンドで取得できます。


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

> Getting tenant metrics is just as easy and can be had with the following command:  

前のコマンドで覆われていないだけで、ハイパーバイザのメトリックは、あなたの計算ノード上で稼働時間を実行することで表示することができますhypervisor_load、です。

テナントのメトリックを取得するのも簡単で、次のコマンドであったことができます。:


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

コマンド新星クォータ・ショーでは、テナントIDとないテナント名を渡す必要があることに注意してください


> As you can see from the examples above, the Nova CLI is a very powerful tool to add to your monitoring arsenal. With just a handful of commands, you can collect all of the metrics mentioned in [part 1] of this series. To make sure you get the most out of this dynamic tool, check out the [documentation][nova-client-ref] for a list of all available commands with explanations.

あなたは上記の例からわかるように、ノヴァCLIは、あなたの監視兵器庫に追加する非常に強力なツールです。コマンドのほんの一握りで、あなたはこのシリーズのパート1で述べたすべてのメトリックを収集することができます。あなたは、このダイナミックなツールを最大限に説明付きで使用可能なすべてのコマンドのリストについては、ドキュメントをチェックアウトを確認します。


<div class="anchor" id="RabbitMQ" />

### Collecting metrics from RabbitMQ  

> RabbitMQ provides a convenient command line client `rabbitmqctl` for accessing its metrics. As described in [part 1][Part 1] of this series, there are four RabbitMQ metrics that are of particular interest for OpenStack monitoring:  

- count: number of active queues  
- memory: size of queues in bytes  
- consumer_utilisation: percentage of time consumers can receive new messages from queue  
- consumers: number of consumers by queue  

RabbitMQのは、そのメトリックにアクセスするための便利なコマンドラインクライアントrabbitmqctlを提供します。このシリーズのパート1で説明したように、OpenStackの監視のために特に重要である4 RabbitMQのメトリックがあります。

- カウント：アクティブなキューの数を
- メモリ：バイト単位のキューのサイズ
- consumer_utilisationは：時間の消費者の割合は、キューから新しいメッセージを受け取ることができます
- 消費者：キューによって消費者の数


#### count  
> To get a count of the current number of queues, you can run a command such as `rabbitmqctl list_queue name | wc -l` which pipes the output of `rabbitmqctl` into the UNIX word count program—the optional `-l` flag forces `wc` to return only the line count. Because `rabbitmqctl`'s output includes two extraneous text lines, to get your total number of active queues, subtract two from the number returned by the previous command.

キューの現在の数のカウントを取得するには、あなたがそのような名前list_queue rabbitmqctlとしてコマンドを実行することができます|トイレ-lこれは、UNIXのワードカウントプログラム・オプションの-lフラグを強制的にトイレにrabbitmqctlの出力のみ行数を返すためのパイプ。 rabbitmqctlの出力は、2つの無関係なテキスト行が含まれているため、アクティブキューのあなたの総数を取得する前のコマンドによって返された数から2を減算します。


#### memory  
> Extracting the size of queues in memory requires a similar command. Running `rabbitmqctl list_queues name memory | grep compute` will show you the memory size of all Nova-related queues (in bytes), like in the output below:  

メモリ内のキューのサイズを抽出するようなコマンドを必要とします。 |名前メモリlist_queues rabbitmqctlを実行しますグレップの計算は、以下の出力のように、あなたの（バイト単位）すべての新星関連のキューのメモリサイズが表示されます：


```
[...]
compute	9096
compute.node0	 9096
compute_fanout_ec3d52fdbe194d89954a3935a8090157 21880
```

#### consumer_utilisation
> Are you noticing a pattern with these commands? To get the consumer utilization rates for all queues, run `rabbitmqctl list_queues name consumer_utilisation`, which produces output resembling the following (recall that a utilization rate of 1.0, or 100 percent, means that the queue never has to wait for its consumers): 

あなたはこれらのコマンドのパターンに気付いていますか？すべてのキュー、次の（1.0、または100パーセントの利用率は、キューが消費者を待たなければならないことを意味していることをリコール）を似た出力を生成し、実行rabbitmqctlのlist_queues名consumer_utilisation、のために消費者の利用率を取得するには：


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
 
> You should see something like this:  

実行、最後になりましたが、指定されたキューのためのアクティブなコンシューマの数を取得する：`rabbitmqctlのlist_queues名の消費者| grep compute`。

あなたはこのように表示されます。


```
[...]
compute	1
compute.node0 	1
compute_fanout_ec3d52fdbe194d89954a3935a8090157   1
```
Remember, few queues should have zero consumers.
<div class="anchor" id="Notifications" />

### Collecting Notifications  
> [Notifications][notification system] are emitted on [events][monitoring-101-events] such as instance creation, instance deletion, and resizing operations. Built around an [AMQP] pipeline (typically [RabbitMQ]), Nova is configured to emit notifications on [about 80 events][paste-events]. A number of tools have emerged that collect OpenStack events, but OpenStack's own [StackTach] leads the pack in terms of feature-completeness and documentation. StackTach is especially useful because it needs no updates to handle new events, meaning it can continue to track events in the face of module upgrades.

> If you’re just interested in a quick-and-dirty notification listener you can build around, check out this [gist]. Listening in on events requires the `kombu` Python package. [This script][virtualenv] will create a virtual environment and run the event listener. The OpenStack documentation has [additional resources][roll-your-own-listener] on crafting your own notification listener.

> The truncated snippet below is an example of notification payloads received after initiating termination of an instance:

通知は、このようなインスタンス作成、インスタンスの削除、およびサイズの変更操作などのイベントに放出されます。 AMQPパイプライン（典型的にはRabbitMQの）を中心に構築された、ノヴァは、約80のイベントの通知を発するように構成されています。ツールの数は、OpenStackのイベントを収集、その浮上しているが、OpenStackの自身のStackTachは、機能完全性およびドキュメントの面でパックをリードしています。それはモジュールのアップグレードに直面してイベントを追跡し続けることができることを意味し、新しいイベントを処理するには、noアップデートを必要としないので、StackTachは特に便利です。

クイック・アンド・ダーティ通知リスナーでちょうど興味があるなら、あなたは、周りの構築この主旨をチェックアウトすることができます。イベントにで聴くと昆布のPythonパッケージを必要とします。このスクリプトは、仮想環境を作成し、イベントリスナーを実行します。 OpenStackのドキュメントは独自の通知リスナーを作り上げる上で追加のリソースを持っています。

以下切り捨てスニペットは、インスタンスの終了を開始した後、受信した通知ペイロードの例です。


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

> Note that in the snippet above there are _two_ notifications emitted: one when initiating instance termination and one that signals the successful completion of a termination operation. This is a common pattern for events in OpenStack: emit one notification when the operation has begun, and another upon completion.

> When combined with collected metrics, notifications give valuable perspective and insight into the potential causes for changes in system behavior. For example, you can measure hypervisor task execution time with events, and correlate that information with the API response time. (_For the curious:_ [in practice][api-vs-load] excessive load on the hypervisor does not appear to affect API response time much.)

両方のイベントからタイムスタンプを比較することによって、あなたはそれがインスタンスを破棄するのに約2.2秒かかっ見ることができます。

1インスタンスの終了および終了操作が正常に完了したことを知らせる1の開始：スニペットに上記放出された2つの通知があることに注意してください。これは、OpenStackの中でのイベントのための一般的なパターンです：完了時に一回の操作が開始された通知、および他を発します。

収集されたメトリックと組み合わせた場合、通知は、システムの行動の変化のために潜在的な原因に貴重な視点と洞察力を与えます。たとえば、イベントと、ハイパーバイザ・タスクの実行時間を測定し、APIの応答時間と、その情報を相関させることができます。 （好奇心のために：ハイパーバイザ上で実際過大な負荷がはるかにAPIの応答時間に影響を与えるように表示されません。）

<div class="anchor" id="APIChecks" />

### Service and API checks 
> _Service checks_ and _API checks_ are used to determine if a service is responsive. API checks generally **GET** or **POST** to a specific API endpoint and verify the response.   

> There are a number of tests you can perform to check the health of the Nova API. However, all tests generally boil down to one of two categories: simple or intrusive.  

> A simple API check reads (usually static) data from an endpoint and verifies that the information received is as expected. A simple API check would be polling the quota information for a project with a **GET** request to `/v2.1/​<tenant-id>​/limits`.

> Intrusive checks modify the state of the receiving endpoint. A typical intrusive check might start by setting a value and optionally following with a request to read or verify the newly created value. Some kind of cleanup would then follow to remove the added values.

> An intrusive check for the Nova API would be something like creating and deleting a key pair, with the following set of API calls (checking the status codes returned):  

> * **POST** `/v2.1/<tenant-id>/os-keypairs '{"keypair": {"name": "test"}}'`  
> * **DELETE** `/v2.1/<tenant-id>/os-keypairs/test`  

サービスチェックとAPIのチェックは、サービスが応答するかどうかを決定するために使用されます。 APIのチェックは、一般的にGETまたはPOST特定のAPIエンドポイントに、応答を確認します。

あなたはノヴァのAPIの健全性をチェックするために実行できるテストの数があります。単純または押し付けがましい：しかし、すべてのテストは、一般的に2つのカテゴリのいずれかに煮詰めます。

シンプルなA​​PIのチェックは、エンドポイントから（通常は静的な）データを読み込み、期待通りに受信された情報があることを検証します。シンプルなA​​PIチェックは<テナント-ID> /制限を/v2.1/するGETリクエストを使用したプロジェクトのクォータ情報のポーリングであろう。

侵入型チェックは、受信エンドポイントの状態を変更します。典型的な侵入型チェックが値を設定し、必要に応じて新たに作成された値を読み取るか検証するための要求に従うことによって開始される可能性があります。クリーンアップのいくつかの種類を加えた値を削除するために従うことになります。

ノヴァAPIの貫入チェックが（ステータスコードを返したチェック）API呼び出しの次のセットで、鍵ペアの作成と削除の​​ようになります。

* **POST** `/v2.1/<tenant-id>/os-keypairs '{"keypair": {"name": "test"}}'`  
* **DELETE** `/v2.1/<tenant-id>/os-keypairs/test`  


## Conclusion
> In this article we've discussed a number of ways to check the health of your Compute cluster. 
  
> With so much data available from disparate sources, getting the information you want all in one place can be a challenge. Luckily, Datadog can help take the pain out of the process. At Datadog, we have built an integration with Nova so you can begin collecting and monitoring its metrics with a minimum of setup.  

> Follow along to [part 3][Part 3] to learn how Datadog can help you monitor Nova.

この記事では、あなたの計算クラスタの健全性を確認するために、いくつかの方法を説明しました。

異なるソースから利用可能なので、多くのデータは、情報を取得すると、あなたは一つの場所ですべてが挑戦することができますしたいです。幸いなことに、Datadogは、プロセスのうち、痛みを取ることができます。あなたが収集し、セットアップを最小限に抑えて、そのメトリックの監視を開始できるようDatadogでは、我々は、ノヴァとの統合を構築しています。

Datadogあなたはノヴァの監視に役立つことができます方法については、第3部に沿って従ってください。


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

