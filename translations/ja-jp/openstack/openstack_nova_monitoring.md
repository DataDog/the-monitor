# Monitoring OpenStack Nova
_This post is Part 1 of a 3-part series about monitoring OpenStack Nova. [Part 2] is about collecting operational data from Nova, and [Part 3] details how to monitor Nova with Datadog._

## The 30,000-foot view
> [OpenStack] is an open-source cloud-computing software platform. It is primarily deployed as [infrastructure-as-a-service] and can be likened to a version of [Amazon Web Services][aws] that can be hosted anywhere. Originally developed as a joint project between Rackspace and NASA, OpenStack is about five years old and has a large number of high-profile corporate supporters, including Google, Hewlett-Packard, Comcast, IBM, and Intel.

[Openstack]は、クラウドコンピューティング環境を構築するためのオープンソースのツールです。このツールは、主として[infrastructure-as-a-service]として展開することができ、様々な場所でホスティングすることができ、[Amazon Web Services][aws]各部品と接続することができます。[Openstack]は、もともとRackspaceのとNASAとの共同プロジェクトとして開発されました。OpenStackは開発が始まって5年のプロジェクトで、Google、ヒューレット・パッカード、コムキャスト、IBM、インテルなど、知名度の高い企業に支援されています。


> OpenStack is an ambitious project with the goal of providing an open, self-hostable alternative to cloud providers like AWS, Azure, DigitalOcean, and Joyent. It features a modular architecture with a current list of [16 services][openstack-services], including meta-services like _Ceilometer_, OpenStack's billing/telemetry module.

Openstackは、AWS、Azure、DigitalOcean、およびJoyentのうようなクラウドプロバイダーを自前の構築するための選択肢としてオープンで公開することを目的にした野心的なプロジェクトです。OpenStackは、モジュラー型アーキテクチャーをとり、_Ceilometer_ のような課金/テレメトリモジュールなどのメタサービスを含め、[16のサービス][openstack-services]を抱えています。


> In this series of posts, we will dive into Nova, the OpenStack Compute module, and explain its key metrics and other useful data points:

このシリーズのポストでは、OpnestackのコンピュートモジュールのNovaを題材に、キーメトリクスとその他の重要なデータポイントに付いて介せすしていきます。


> - [Hypervisor metrics](#hypervisor-metrics) report work performed by hypervisors, for example the number of running VMs, or load on the hypervisor itself.
> - [Nova server metrics](#nova-server-metrics) report some information about servers, such as disk read requests per second.
> - [Tenant metrics](#tenant-metrics) report resources used or available to a group of users, for example total number of cores.
> - [Message queue metrics](#rabbitmq-metrics) reflect the state of the internal message-passing queue, for example its size.
> - [Notifications](#notifications) report discrete events such as when a new compute instance begins to be created.

- [ハイパーバイザー メトリクス](#hypervisor-metrics) ハイパーバイザーの動作状況のレポート。例えば、仮想マシンの実行個数、またはハイパーバイザーの負荷など。
- [Nova Servers メトリクス](#nova-server-metrics) サーバーの動作状況のリポート。例えば、1秒間のディスクの読み込みリクエスト数
- [Tenant メトリクス](#tenant-metrics) ユーザーグループに割り当てたリソースの量やその使用量のレポート。例えば、割り当てCPUコア数。
- [メッセージキュー メトリクス](#rabbitmq-metrics) 内部メッセージキューの状態のレポート。例えば、メッセージキューの量。
- [通知](#notifications) 新しいコンピュートインスタンスの作成開始イベントなどの、個々のイベントのリポート。


[![Openstack Architecture overview][arch-over]][arch-over]

> _A typical OpenStack deployment, utilizing 7 of the 16 available services_

_一般的なOpenStackの実行環境みでは、16個のサービスの内、7つのサービスを使います。_


> A note on terminology: The OpenStack project uses the terms **project** and **tenant** [interchangeably](http://docs.openstack.org/openstack-ops/content/projects_users.html) to refer to a group of users. In this post, we will use the term **tenant** for clarity.

用語の解説: OpenStackでは、ユーザーの集合体を **project** か **tenant** かの、[どちらかを使って解説をしています](http://docs.openstack.org/openstack-ops/content/projects_users.html)。このブログの記事では、混乱を防ぐために **tenant** を使うことにします。


## What Nova does
[![Nova diagram][nova]][nova]

<center>Somewhat confusingly, the Compute module (Nova) contains a component, also called Compute.</center>

<center>ややこしことに、コンピュートモジュールのNovaは、それ自体にコンピュートという名前コンポーネントを持っています。</center>

> The core of the OpenStack project lies in the Compute module, known as Nova. Nova is responsible for the provisioning and management of virtual machines. It features full support for KVM and QEMU out of the box, with partial support for other hypervisors including [VMWare, Xen, and Hyper-V](https://wiki.openstack.org/wiki/HypervisorSupportMatrix).

OpenStackのプロジェクトのコアは、Novaとして知られているコンピュートモジュールです。Novaは、仮想マシンのプロビジョニングと管理を担当しています。Novaは、KVMとQEMUをデフォルトでフルサポートし、[VMWare, Xen, Hyper-V](https://wiki.openstack.org/wiki/HypervisorSupportMatrix)のその他のハイパーバイザーの主要機能をサポートしてます。


> If you're already familiar with Amazon Web Services, Nova is compatible with [EC2 and S3][api-compat] APIs, easing the migration of applications and decreasing development times for those already using AWS.

もしもAmazon Web Servicesについて知識があるなら、Novaは、既にAWSを使っている人たちが開発時間を削減し、アプリケーションの移動が簡単になるように、[EC2とS3][api-compat]とのAPIの互換性があります。


## Key Nova metrics and events
> Nova metrics can be logically grouped into three categories: **hypervisor** metrics, **tenant** metrics and **nova server** metrics. Hypervisor metrics give a clear view of the work performed by your hypervisors, nova server metrics give you a window into your virtual machine instances, and tenant metrics provide detailed information about user resource usage.

Novaメトリックは、論理的に3つのカテゴリに分けられます: **Hypervisor** メトリックス, **Tenant** メトリクス, **Nova server** メトリクス。Hypervisorメトリックはハイパーバイザーによって実行される作業量の明確化し、Nova serverメトリックは仮想マシンインスタンスの窓を空け中をのぞけるようにし、Tenantメトリックはユーザーのリソース使用状況に関する詳細情報を提供します。


> Though OpenStack's modules expose many metrics, correlation of these built-in metrics with other information sources is essential to really understand what’s happening inside OpenStack. For example, because OpenStack uses RabbitMQ under the hood, no monitoring solution would be complete without integrating RabbitMQ metrics as well.

OpenStackのモジュールは、多くのメトリクスを公開していますが、他の情報源を持つこれらの組み込みの指標の相関は本当にOpenStackの内部で何が起こっているかを理解することが不可欠です。 OpenStackのは、ボンネットの下のRabbitMQを使用しているため、例えば、何の監視ソリューションは、同様のRabbitMQの指標を統合することなく完全ではないでしょう。


> Combining metrics from various systems in addition to log file data and [OpenStack notifications][notifs] will really help pull back the curtain so you can observe what's actually going on in your deployment.

ログファイルのデータやOpenStackからの通知に各システムから集取したメトリクスを連携することにより、今まで閉じていたカーテンを開いた時のように、運用しているシステムで実際に起きている事象をクリアに把握できるようになるでしょう。


<div class="anchor" id="hypervisor-metrics" />

### Hypervisor metrics

[![Nova hypervisor metrics collection][hypervisor-metrics]][hypervisor-metrics]

> The hypervisor initiates and oversees the operation of virtual machines. Failure of this critical piece of software will cause tenants to experience issues provisioning and performing other operations on their virtual machines, so monitoring the hypervisor is crucial.

ハイパーバイザーが仮想マシンを起動し、動作を管理しています。この重要なソフトウェアの障害は、テナントによるプロビジョニングとその他の仮想マシンへの操作に影響を与えます。従って、ハイパーバイザーの監視は非常に重要です。


> Though a number of hypervisor metrics are available, the following subset gives a good idea of what your hypervisors are doing under the hood:

ハイパーバイザ・メトリクスには多くの項目がありますが、以下に抜き出した項目は、ハイパーバイザーがどうのように状況にあるのかを把握するのに有効です:


|**Name**| **Description**|**[Metric Type][monitoring]**|
|:---:|:---:|:---:|
| hypervisor\_load | System load | Resource: Utilization |
| current_workload | Count of all currently active hypervisor tasks | Resource: Utilization |
| hypervisor\_up | Count of all active hypervisors | Resource: Availability |
| running\_vms | Total number of running virtual machines | Resource: Utilization |
| vcpus_available | Total number of available CPUs | Resource: Utilization |
| free\_disk\_gb | Free hard drive space in GB | Resource: Utilization |
| free\_ram\_mb | Amount of memory (in MB) available| Resource: Utilization|

<div class="anchor" id="hypervisor_load" />

> **hypervisor\_load**: Hypervisor load represents the [system load][load] over the last minute for a given hypervisor. Extended periods of high hypervisor load could degrade performance and slow down hypervisor operations. If you have busy VMs, expect this metric to rise.

**hypervisor\_load**（ハイパーバイザーの負荷）:ハイパーバイザーの負荷は、特定のハイパーバイザーの過去1分間の[システムの負荷][load]を表しています。長期に渡るハイパーバイザーの負荷は、ハイパーバイザーの動作のパフォーマンス低下と遅延の原因になります。もしも、負荷の高い仮想マシンがある場合も、このメトリクスは上昇します。


![Hypervisor workload][hv-work]

> **current_workload**: The current workload metric is a count of all the currently active hypervisor operations: [Build, Snapshot, Migrate, and Resize][hypervisor-operations]. Unless you are using [OpenStack’s Shared File Systems service][shared-fs], the VMs and hypervisor all share the same I/O resources, so an extended period of high hypervisor workload could lead to I/O bottlenecks, with your instances [competing for disk access][IO]. This metric, coupled with hypervisor load, gives you a direct view of the work your hypervisor is performing.

**current_workload**（現在の作業負荷）:current workloadメトリクスは、ハイパーバイザー上でアクティブなオペレーションの数です:例として、[Build, Snapshot, Migrate, Resize][hypervisor-operations]になります。[”OpenStack’s Shared File Systems service”][shared-fs]を採用していない場合は、仮想マシンとハイパーバイザーは同じI/O資源を利用することになります。従って、長期に渡るハイパーバイザーの高負荷は、インスタンスが[ディスクへのアクセスのための計算をする][IO]ことを妨害し、I/Oパフォーマンスの低下の原因にもなります。このメトリクスと”hypervisor load”を組み合わせて監視することで、ハイパーバイザーの稼働状況の全体を直接的に把握できるようになります。


<div class="anchor" id="running_vms" />

> **running_vms**:  OpenStack exposes the number of virtual machines currently running, which can be aggregated by host. The maximum number of VMs running at any point in time is bound by available CPU and memory resources. This metric, along with the current workload and hypervisor load, should give you all the information you need to ensure a fair distribution of load across your cluster of compute nodes.

> How you monitor the `running_vms` metric largely depends on your use case—if you are using OpenStack to run critical infrastructure on a constant number of nodes, changes in running VMs are similar to physical hosts going down; you would want to be aware of either event so you can react accordingly. If on the other hand your infrastructure is more dynamic, you may not care about the comings and goings of individual hosts as long as you have enough capacity to keep all your services running smoothly.

**running_vms**（動作しているVMの数）：

OpenStackは、実行中の仮想マシンの数を公開しています。そして、その数値はホスト毎に集計することができます。特定のタイミングでの仮想マシンの最大実行数は、使用可能なCPUとメモリーに深く関係しています。このメトリクスと"current workload", "hypervisor load"を関連づけることで、クラスター内の計算ノード間での均等な負荷の配置が実現されているかを把握することができます。

`running_vms`メトリクスをどのように監視するかは、ユーザーのOpenStackの使い方に関わっています。もしもあなたが、重要なインフラをノード数が固定されている状態で運用しているなら、仮想マシンの数の変化は物理マシンの障害と同等の意味をもつでしょう。そして、素早く対応できるように、どちらのイベントに関しても把握しておきたいでしょう。一方でインフラが常に変化している場合は、全てのサービスをスムーズに運用維持できるキャパシティーが確保されていれば、個別のホストの追加や削除はあまり気にならないでしょう。


![Available vCPUs][avail-vcpu]

> **vcpus_available**: Each hypervisor reports the current number of CPUs allocated and the maximum number available. Using these two metrics, you can compute the number of CPUs currently available.

> In a production environment with fairly predictable workloads, adding and removing resources from the computation pool should be an anticipated event. In that case, you would want to monitor and possibly alert on any changes to your number of available VCPUs. In other cases, such as using OpenStack as a development environment, tracking this metric is less important.

> Setups with a diminishing number of available CPU resources could benefit from the provisioning of additional Compute hosts. A general awareness of available resources can let you scale your deployment before an increase in demand makes it a necessity. If you are constantly bumping into the resource ceiling, it's time for more machines.

**vcpus_available**（利用可能な仮想CPUの数）：各ハイパーバイザーは、割り当てているCPUの数と、割り当てることのできる最大数をレポートします。この二つのメトリクスを使って、今後割り当てることのできるCPUの数を計算することができます。

運用負荷の予測ができている本番環境では、リソースプールへの追加や削除は予想されるイベントであるべきです。このような場合、割り当て可能なVCPU数を監視し、変化が発生した場合は警告をしたいとこともあるでしょう。しかし、OpenStackを開発環境で使っているようなケースでは、このメトリクスはそれほど重要ではないでしょう。

使用可能なCPUリソースが減少してきている場合には、コンピュートホストの追加は有効な方策でしょう。日常的な使用可能なリソースの把握は、需要の増加によるインフラ拡張の必要性が顕在化する前に、それを可能にしてくれるでしょう。もしも、あなたがリソースの上限値に日常的に達しているなら、それはマシンを追加する時期にきているということになります。


<div class="anchor" id="free_disk_gb" />

> **free\_disk\_gb**: This metric reports the amount of disk space (in gigabytes) currently available for allocation, aggregated by physical host. Maintaining ample disk space is critical, because the hypervisor will be unable to spawn new virtual machines if there isn’t enough available space.

> By tracking your free\_disk\_gb, you can migrate overly large instances to other physical hosts, should space become scarce. You will definitely want to be alerted to diminishing disk space so you can take action and prevent hypervisor errors due to insufficient resources.

**free\_disk\_gb**（空きディスク容量 GB）：このメトリクスは、物理ホスト毎に集計した利用可能なディスクの空き容量（ギガバイト）をレポートします。ハイパーバイザは、ディスクに十分な空き容量がない場合、新しい仮想マシンを起動することができなくなります。ディスクに十分な空き容量を維持することは、非常に重要です。

”free_disk_gb”を把握しておくことにより、大量のディスクを消費しているインスタンスを、他の物理ホストに移行する場合でも安心して作業を進めることができるようになります。リソース不足に起因するハイパーバイザーのエラーを防ぐためにも、空きディスク容量の減少に関しては、アラートは絶対に必要でしょう。


<div class="anchor" id="free_ram_mb" />

> **free\_ram\_mb**: Memory, like disk space, is an important resource. Without sufficient memory, the hypervisor will be unable to spawn new instances or resize instances to larger flavors. Ensuring adequate memory is essential—insufficient memory will result in hypervisor errors and confused users.

> Like free\_disk\_gb, you will want to be alerted to diminishing memory so you can take appropriate action, whether that means migrating instances or provisioning additional compute nodes.

**free\_ram\_mb**（空きメモリー量　MB）：空きディスク容量のようにメモリーも、重要なリソース監視項目です。十分なメモリがないと、ハイパーバイザは、新しいインスタンスを起動できなかったり、既存のインスタンスのサイズアップができなかったりします。十分なメモリを確保することは、必要不可欠です。メモリ不足は、ハイパーバイザーのエラーを引き起こし、更にユーザーにも迷惑を与えます。

”free_disk_gb”と同様に、インスタンの移動の際や追加の計算ノードを起動する際の目安として、メモリーの減少に関してもアラートは必要になるでしょう。


<div class="anchor" id="nova-server-metrics" />

### Nova server metrics
> Computing nodes generally constitute the majority of nodes in an OpenStack deployment. The Nova server metrics group provides information on individual instances operating on computation nodes. Monitoring individual Nova servers helps you to ensure that load is being distributed evenly and to avoid the [noisy neighbor problem][neighbor]. However, to gain the most visibility into your instances, including the full suite of OS and system metrics, installing a [monitoring agent][agent] is essential.

一般的に、OpenStack環境内の対部分のノードは、計算ノードで占められています。Nova server メトリックスのグループは、計算ノード上で動作する個々のインスタンスに関する情報を提供します。個々のNova serverを監視することにより、負荷が均等に分散されていることを確認することができ、[特定ユーザーによる高負荷から生ずる問題][neighbor]を回避することができます。しかしながら、OSおよびシステムメトリックスの全部を手に入れインスタンスの状況を詳しく把握するためにも、[監視のためのエージェント][agent]のインストールは不可欠です。


|**Name**| **Description**|**[Metric Type][monitoring]**|
|:---:|:---:|:---:|
| hdd\_read\_req | Number of read requests per second | Work: Throughput |

> **hdd\_read\_req**: In a virtual environment, RAM size is often a limiting constraint on running processes. Monitoring the number of hard drive requests per second can give you an idea of work being performed within virtual machines on your Nova node. Spikes in this metric indicate that a virtual machine may have low RAM, causing it to [thrash the disk][thrashing] with constant memory paging. At the very least, awareness of high read rates can inform troubleshooting when diagnosing performance issues within your Nova cluster.

**hdd\_read\_req**（HDD読み込みリクエスト数/分）：仮想環境では、割り当てられたRAMサイズは、実行プロセスの制約であることが多いです。1秒あたりのハードドライブへのリクエスト数を監視することで、Noveノード上の仮想マシン内の生産性を把握することができます。このメトリクスの急激な上昇は、仮想マシンの空きRAM容量が低下し、メモリページングを使用してディスクをスラッシュさせていることを表しています。”HDDの読み取り発生率が高い”という状況を把握していくことは、Novaクラスター内のパフォーマンスの問題を診断する際に、トラブルシューティングの重要な手がかりになるはずです。


<div class="anchor" id="tenant-metrics" />

### Tenant metrics

> Tenant metrics are primarily focused on resource usage. _Remember, tenants are just groups of users_. In OpenStack, each tenant is allotted a specific amount of resources, subject to a quota. Monitoring these metrics allows you to fully exploit the available resources and can help inform requests for quota increases should the need arise.

Tenantメトリクスは、主にリソースの使用状況に焦点を当てています。（テナントは、ユーザーの集合体です。）OpenStack上で各テナントには、クオータに基づいて一定量のリソースが割り当てらてれます。これらのメトリクスを監視することは、利用可能なリソースのフルに活用を助けると同時に、quota増加の要請のタイミングをも教えてくれるでしょう。


|**Name**| **Description**|**[Metric Type][monitoring]**|
|:---:|:---:|:---:|
| total\_cores\_used | Total cores currently in use by tenant | Resource: Utilization |
| max\_total\_cores | Maximum number of cores allocated to tenant | Resource: Utilization |
| total\_instances\_used | Total number of instances owned by tenant | Resource: Utilization |
| max\_total\_instances | Maximum number of instances allocated to tenant | Resource: Utilization |

> **total\_cores\_used** and **max\_total\_cores**:  Each tenant has a maximum number of resources allocated, set by a quota. Tracking your per-tenant core usage means you won't unwittingly bump against that quota-imposed ceiling. Graphing this metric alongside the `max_total_cores` metric will give you an immediate view into your resource consumption over time and help you determine if additional resources are required by your tenant.

**total\_cores\_used** と **max\_total\_cores**（テナントによるCPUコアの総使用数と総割り当て数）:各テナントには、クォータによって割り当てられるリソースの最大数が設定されています。テナントに適応されたCPUコアの利用状況を把握しておくことは、知らず知らずのうちに上限を迎えてしまうのを防止してくれます。"total_cores_used"と"max_total_cores"を同一グラフ内で表示することで、時間の経過と共に変化するリソースの消費量を把握することができ、テナントに必要な追加のリソースの判断の手助けになってくれます。


> **total\_instances\_used** and **max\_total\_instances**: Similar to physical resources, the number of instances per tenant is also capped by a quota. Each VM you spin up consumes another instance, and each instance size uses a different number of resources. When setting quotas for internal use, you should keep in mind the projected number of instances you plan to run, as well as the anticipated sizes of those instances.

**total\_instances\_used** and **max\_total\_instances**（テナントによるインスタンスの総所有数と総割り当て数）:物理リソースと同様に、テナントごとのインスタンスの数もクォータによって制限されています。起動する各VMは、それぞれインスタンスを消費します。そして異なるサイズのインスタンスは、異なるリソース数を消費します。内部使用のためのクォータを設定する場合には、将来起動する予定のインスタンス数やそれらに必要なリソースのサイズを知っておく必要があります。


<div class="anchor" id="rabbitmq-metrics" />

### RabbitMQ metrics

[![Message pipeline][amqp-diag]][amqp-diag]

> What's RabbitMQ got to do with OpenStack Nova? RabbitMQ is one of [several options][several options] for OpenStack's message-passing pipeline and is used by default. Nova components use RabbitMQ for both [remote procedure calls][RPC] (RPCs) and for internal communication.

RabbitMQは、OpenStack Nova内でどのような役割をはたしているでしょうか。RabbitMQは、OpenStack上で使用するメッセージ・パッシング・パイプラインの[オプション][several options]の一つで、デフォルトの構成部品として採用されています。Nova componentは、[リモートプロシージャコール][RPC]（RPCs）と内部通信の両方のためにRabbitMQを使用します。


> RabbitMQ serves both as a synchronous and asynchronous communications channel, and failure of this component will disrupt operations across your deployment. Monitoring RabbitMQ is essential if you want the full picture of your OpenStack environment.

RabbitMQは、同期および非同期の通信チャネルを提供しており、RabbitMQのコンポーネントの障害は、デプロイメント全体に影響を与えます。もしも、OpenStack環境の全状況を把握しておきたいと考えるなら、RabbitMQを監視することは不可欠です。


> At the very least, you will want to keep an eye on the following RabbitMQ metrics:

少なくとも、次のRabbitMQのメトリクスに注目しておくべきでしょう：


|**Name**| **Description**|**[Metric Type][monitoring]**|
|:---:|:---:|:---:|
|consumer_utilisation | The proportion of time a queue’s consumers can take new messages | Resource: Utilization |
|memory | Current size of queue in bytes | Resource: Utilization |
|count | Number of active queues (computed)| Resource: Utilization |
|consumers | Number of consumers per queue| Resource: Utilization |

![Queue consumer utilization][utilization]

<div class="anchor" id="consumer_utilisation" />

> **consumer_utilisation**: Introduced in RabbitMQ 3.3, this metric (the spelling of which follows the rules of British English) reports on the utilization of each queue, represented as a percentage. Ideally, this metric will be 100 percent for each queue, meaning consumers get messages as quickly as they are published.

> A couple of factors can contribute to degraded consumer utilization: network congestion and [prefetching]. A slow network translates to an inhibited ability for consumers to get new messages from publishers. Prefetching is the number of messages a consumer can receive while processing the current message. A low prefetch setting could keep consumers from taking in new messages while processing older ones. If you are seeing low consumer utilization for extended periods of time, and your prefetch settings are reasonably high, the problem most likely lies in the network.

**consumer_utilisation**（コンシューマの活用率）:RabbitMQの3.3で導入されたこのメトリックスは、各キューの活用上を％値でリポートします。このメトリックスは、メッセージが生成されると同時にコンシューマが割り当てられると言う意味で、各キュー毎に100%をレポートしているのが理想です。

いくつかの要因が”consumer utilization”の低下の原因になります: ネットワークの輻輳やプリフェッチです。遅いネットワークは、コンシューマーがパブリッシャーからメッセージを受け取る際の抑制要素として機能してします。プリフェッチは、コンシューマーが既存のメッセージを処理している間に受信できる新しいメッセージの数です。プリフェッチの設定値が低い場合、コンシューマーが、古いメッセージを処理している間は、新しいメッセージを取り込むことが抑制されてしまいます。プリフェッチの値を高く設定しているにもかかわらず、長期間に渡り”consumer utilization”の値が低い場合は、ネットワークに問題がある可能性が高いです。


![Memory by queue][queue-mem]

<div class="anchor" id="queue_memory" />

> **memory**:  Like most in-memory message queues, RabbitMQ will begin swapping to disk under memory pressure. In addition to increased latency caused by disk paging, RabbitMQ will preemptively throttle message producers when memory consumption reaches a predefined threshold (40 percent of system RAM by default). Although not often an issue, a significant spike in queue memory could point to a large backlog of unreceived ("ready") messages, or worse. A protracted period of excessive memory consumption could cause performance issues as well.

**memory**（キューが使っているメモリサイズ）：一般的なインメモリーメッセージキューと同様に、RabbitMQも、空きメモリーの残量によりディスクへのスワップを開始します。ディスクページングによって引き起こされるレイテンシーの増加に加え、RabbitMQは、メモリの消費量が事前に設定した閾値（デフォルトでは、システムRAMの40パーセント）を越えると、先行的にメッセージプロデューサーの処理に制限をかけ始めます。問題になることは希ながら、キューメモリーの急激なスパイクは、 大量の準備済み未受信のメッセージかそれより悪い状態の可能性を示しています。又、長期化した過度のメモリ消費状態は、パフォーマンス問題を引き起こす原因にもなります。


> **count**:  Queue count represents the current number of RabbitMQ queues. You can compute this metric by counting the number of queues listed by RabbitMQ. A count of zero queues means there is a serious error in your RabbitMQ deployment, necessitating further investigation. Setting up an alert on this metric is a great idea—zero queues means zero messages being passed.

**count**（アクティブなキュー数）：キューカウントは、現状のRabbitMQのキューの数を表しています。RabbitMQから提供されているキューの数をカウントすることにより、このメトリックスを計算することができます。カウントした値が0の場合、RabbitMQのデプロイに重大な問題があることを意味し、更なる調査が必要なります。このメトリクスに対しアラートを設定しておくことは素晴らしアイディアです。”ゼロキューカウントは、ゼロメッセージが処理されていることを意味しています”。


![Consumers by queue][queue-consume]

<div class="anchor" id="queue_consumers" />

> **consumers**: Similar to the queue count metric, your number of consumers should usually be non-zero for a given queue. Zero consumers means that producers are sending out messages into the void. Depending on your RabbitMQ configuration, those messages could be lost forever.

**consumers**（キュー毎のコンシューマ数）：キュー・カウント・メトリックと同様に、消費者のあなたの数は、通常、指定されたキューのために非ゼロでなければなりません。ゼロの消費者は生産者がvoidにメッセージを送信していることを意味します。あなたのRabbitMQ構成に応じて、これらのメッセージは永遠に失われる可能性があります。


> Generally speaking, there are only a handful of queues that may have zero consumers under normal circumstances: _aliveness-test_, _notifications.info_, and _notifications.error_.

稼働状態テスト、notifications.info、およびnotifications.errorを：一般的に言えば、通常の状況下でゼロの消費者を有することができるキューのほんの一握りがあります。


>  [_Aliveness-test_ ][aliveness]is a queue for monitoring tools to use. A producer typically creates and consumes a message in this queue to ensure RabbitMQ is operating correctly. _Notifications.error_ and _notifications.info_ are notifications with an associated [log level] priority. _Notifications.error_ is the error notification message queue, and _notifications.info_ is the queue for informational messages.

稼働状態-testが使用するツールを監視するためのキューです。プロデューサーは、一般的に作成し、RabbitMQのが正常に動作していることを確認するために、このキューにメッセージを消費します。 Notifications.errorはと関連するログレベルの優先順位の通知notifications.infoです。 Notifications.errorはエラー通知メッセージキューで、notifications.infoは、情報メッセージのキューです。


> Additionally, if you have an OpenStack monitoring tool such as [Stacktach][stacktach] in place, you may see a number of consumer-less queues beginning with _monitor_ if your monitoring tool is not actively consuming messages from those queues.

あなたが代わりにStacktachなどOpenStackの監視ツールを持っている場合はさらに、あなたの監視ツールが積極的にそれらのキューからメッセージを消費していない場合は、モニターで始まる消費者レスキューの数を表示することがあります。


> Read more about collecting emitted notifications in [part two of this series][Part 2]. Beyond the above queues listed, if your consumer count drops to zero for an extended period of time, you probably want to be alerted.  

このシリーズのパート2で発行した通知を収集については、こちらをご覧ください。あなたの消費者の数が長期間にわたってゼロに低下した場合に記載されている上記のキューを超えて、あなたはおそらく警告することにしたいです。


<div class="anchor" id="notifications" />

### Notifications

> Nova reports certain discrete events via _notifications_. Because the majority of work performed by Nova is through asynchronous calls, wherein a user initiates an operation and does not receive a response until the operation is complete, listening in on emitted events is necessary to see the full picture at a given point in time.
Furthermore, handling notifications is the only way to get information on the throughput of work done by the hypervisor.

ノヴァは、通知を経由して、特定の個別のイベントをレポートします。ノヴァによって実行される作業の大半は、ユーザーが操作を開始し、操作が完了するまでの応答を受信しないことを特徴と非同期呼び出しを介してであるため、放出されたイベントにでリスニングして任意の時点で全体像を見ることが必要です。
また、通知を処理する時間のhypervisor.extended期間が行った作業のスループットに関する情報を取得する唯一の方法である、あなたはおそらく警告することにしたいです。


> Though Nova emits notifications on about [80 events][paste-events], the following table lists a number of useful notifications to listen for. The name in the table corresponds to the `event_type` field included in the notification payload.

ノヴァは、約80のイベントの通知を発したが、次の表には、をリッスンするために有用な通知の数を示しています。表中の名前は、通知ペイロードに含まれたevent_typeフィールドに対応しています。


|**Name**| **Description**|**[Metric Type][monitoring]**|
|:---:|:---:|:---:|
| compute.instance.create.[start/end] | Signals the beginning or end of an instance creation event | Event: Scaling |
| compute.instance.delete.[start/end] | Signals the beginning or end of an instance deletion operation | Event: Scaling  |
| compute.instance.resize.prep.start | Signals the beginning of a resize operation | Event: Scaling |
| compute.instance.resize.confirm.end | Signals the end of a successful resize operation | Event: Scaling  |

> For most events, correlating the `start` and `end` notifications and their associated timestamps will give you the execution time for hypervisor operations. Some operations, like resizing an instance, perform preparation and sanity checks before and after the action, so you will need to take these events into account as well to get an accurate sense of performance.

開始と終了の通知を関連付けるほとんどのイベント、およびそれらに関連するタイムスタンプのためにあなたのハイパーバイザーの操作の実行時間を与えるだろう。あなたは、パフォーマンスの正確な感覚を得るためだけでなく、アカウントにこれらのイベントをする必要があるので、一部の操作は、インスタンスのサイズを変更するように、前とアクションの後準備と正気チェックを実行します。


## Conclusion
> In this post we’ve outlined some of the most useful metrics and notifications you can monitor to keep tabs on your Nova computing cluster. If you’re just getting started with OpenStack, monitoring the metrics and events listed below will provide good visibility into the health and performance of your deployment:  

この記事では、我々はあなたのノヴァ・コンピューティング・クラスタ上のタブを保つために監視することができる最も有用な指標と通知のいくつかを概説しました。あなただけのOpenStackの使用を開始している場合は、メトリックと、以下のイベントを監視することは、健康や配備のパフォーマンスに良好な視認性を提供します：


- [hypervisor\_load](#hypervisor_load)  
- [running\_vms](#running_vms)  
- [free\_disk\_gb](#free_disk_gb)  
- [free\_ram\_mb](#free_ram_mb)  
- [queue memory](#queue_memory)  
- [queue consumers](#queue_consumers)  
- [consumer_utilisation](#consumer_utilisation)  

> In the future, you may recognize additional OpenStack metrics that are particularly relevant to your own infrastructure and use cases. Of course, what you monitor will depend on both the tools you have and the OpenStack components you are using. See the [companion post][Part 2] for step-by-step instructions on collecting Nova and RabbitMQ metrics.

将来的には、独自のインフラストラクチャと使用例に特に関連する追加のOpenStackの指標を認識することができます。もちろん、あなたは両方のあなたが持っているツールと、使用しているOpenStackのコンポーネントに依存します監視するもの。ノヴァとRabbitMQのメトリックを収集することにステップバイステップの手順については、コンパニオンの記事を参照してください。


<iframe width="100%" height="100" style="border: 0;" src="https://go.pardot.com/l/38172/2015-03-02/h6c2r" scrolling="no" type="text/html" frameborder="0" allowtransparency="true"></iframe>

[agent]: https://github.com/DataDog/dd-agent

[aliveness]: http://hg.rabbitmq.com/rabbitmq-management/raw-file/default/priv/www/api/index.html

[amqp-diag]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-OpenStack/rabbitmq-3.png

[api-compat]: https://wiki.openstack.org/wiki/Swift/APIFeatureComparison#Amazon_S3_REST_API_Compatability

[arch-over]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-OpenStack/arch_over-4.png

[avail-vcpu]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-OpenStack/vCPU.png

[aws]: https://aws.amazon.com/

[default-dash]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-OpenStack/default-dash.png

[diag]: https://wiki.openstack.org/wiki/Nova_VM_Diagnostics

[hypervisor-metrics]: http://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-OpenStack/hypervisor-3.png

[hv-work]: http://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-OpenStack/hv-work.png

[hypervisor-operations]: http://docs.openstack.org/developer/nova/support-matrix.html

[infrastructure-as-a-service]: https://en.wikipedia.org/wiki/Cloud_computing#Infrastructure_as_a_service_.28IaaS.29

[IO]: https://www.mirantis.com/blog/making-most-of-openstack-compute-performance

[load]: https://en.wikipedia.org/wiki/Load_(computing)

[log level]: http://docs.openstack.org/openstack-ops/content/logging_monitoring.html

[monitoring]: https://www.datadoghq.com/blog/monitoring-101-collecting-data/

[neighbor]: https://www.datadoghq.com/blog/understanding-aws-stolen-cpu-and-how-it-affects-your-apps/

[notifs]: https://wiki.openstack.org/wiki/SystemUsageData

[nova]: http://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-OpenStack/nova-high-level-3.png

[nova-arch]: http://docs.openstack.org/developer/nova/_images/architecture.svg

[OpenStack]: http://openstack.org

[openstack-services]: https://en.wikipedia.org/wiki/OpenStack#Components

[outlier-detection]: https://www.datadoghq.com/blog/introducing-outlier-detection-in-datadog/

[paste-events]: http://paste.openstack.org/show/54140/

[prefetching]: https://www.rabbitmq.com/consumer-prefetch.html

[queue-consume]: http://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-OpenStack/queue-consume.png

[queue-mem]: http://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-OpenStack/queue-mem.png

[RPC]: http://docs.openstack.org/developer/nova/rpc.html

[shared-fs]: http://docs.openstack.org/openstack-ops/content/storage_decision.html#shared_file_system_service

[smart]: https://en.wikipedia.org/wiki/S.M.A.R.T.

[several options]: https://wiki.openstack.org/wiki/Oslo/Messaging

[stacktach]: https://github.com/openstack/stacktach

[thrashing]: https://en.wikipedia.org/wiki/Thrashing_(computer_science)
[utilization]: http://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-OpenStack/utilization.png


[Part 1]: http://datadoghq.com/blog/openstack-monitoring-nova
[Part 2]: http://datadoghq.com/blog/collecting-metrics-notifications-openstack-nova
[Part 3]: http://datadoghq.com/blog/openstack-monitoring-datadog
