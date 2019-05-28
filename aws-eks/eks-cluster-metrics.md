# Key metrics for Amazon EKS monitoring

Amazon Elastic Container Service for Kubernetes, or [Amazon EKS][aws-eks], is a hosted [Kubernetes][k8s] platform that is managed by AWS. Put another way, EKS is Kubernetes-as-a-service, with AWS hosting and managing the infrastructure needed to make your cluster highly available across multiple availability zones. EKS is distinct from [Amazon Elastic Container Service (ECS)][aws-ecs], which is Amazon’s proprietary container orchestration service for running and managing Docker containers. For more information on ECS, see [our monitoring guide](/blog/amazon-ecs-metrics/).

Amazon EKS offers combined benefits of working with Kubernetes and AWS. EKS is [certified Kubernetes conformant][k8s-conformant], meaning that any applications that run on native Kubernetes will run on EKS without modifications. And you can manage your cluster and the applications running on it with [`kubectl`][kubectl], the standard Kubernetes command line tool. Plus, EKS integrates with and relies on a variety of AWS services, including [VPC][aws-vpc] for network isolation, [ELB](/blog/top-elb-health-and-performance-metrics/) for load balancing, [EBS](/blog/amazon-ebs-monitoring/) for persistent storage, and of course [EC2](/blog/ec2-monitoring) for provisioning host VMs, or nodes.

Monitoring your EKS cluster is important for ensuring that the applications running on it are performing properly. It will also surface resource bottlenecks and reveal whether your cluster has adequate capacity for launching new applications or scaling up existing ones when necessary. In this post, we’ll dive into key metrics that will help you monitor the health and performance of your EKS cluster. We will look at the following categories of metrics:

- [Cluster state metrics](#cluster-state-metrics)
- [Container and node resource metrics](#resource-metrics)
- [AWS service metrics](#aws-service-metrics)

Finally, we’ll look at how tracking Kubernetes and AWS [events](#events) keeps you informed about changes in your cluster’s health and status.

But first, let’s take a brief look at how a Kubernetes cluster works and then what EKS does differently.

## How Kubernetes works

A Kubernetes cluster is made up of two primary node types:

- One or more control plane nodes
- Worker nodes

**Control plane nodes** host several components that serve many important functions:

- [**API servers**][k8s-api] are the gateway through which developers and administrators query and interact with the cluster
- [**controller managers**][kube-controller-manager] implement and track the lifecycle of the different [controllers](#setting-the-state-of-the-cluster) that are deployed to the cluster
- [**schedulers**][kube-scheduler] query the state of the cluster and schedule and assign workloads to worker nodes
- [**etcd data stores**][etcd] maintain a record of the state of the cluster in a distributed key-value store so that other components can ensure that all worker nodes are healthy and running the desired workloads*

*Note that the etcd data stores may be colocated on the control plane nodes or they may run separately on their own hosts.

Together, the control plane nodes and etcd data stores make up the **control plane**. The control plane monitors, maintains, and stores the desired state of the cluster. It is also the gateway through which new cluster objects are deployed or existing objects are updated.

For clusters with multiple control plane nodes spread across zones for high availability and redundancy, requests are balanced across the control plane nodes. The control plane will schedule workloads across all available worker nodes.

**Worker nodes** are host VMs. Each one has a **kubelet** process that monitors the worker node and acts as the point of contact between that node and the control plane. The kubelet receives requests from the control plane and instructs the worker node's runtime environment to create and manage **[pods][k8s-pods]** to run the workloads. Pods are isolated, self-contained, easily replicated groups of one or more containers that share storage and a network IP. For example, one pod could be a single instance of an application, while another could be an instance of NGINX. Other pods can be self-terminating and be destroyed once they've completed a specific job.

### Setting the state of the cluster

As a container orchestration platform, the power of Kubernetes lies in your ability to use **manifests**—configuration files in YAML or JSON format—to provide the master API with a desired state, or a specified set of objects that you want your cluster to run. Manifests describe things like the number of pods to launch, what type of containers those pods will run, and any necessary settings. The control plane will then do the work of automatically scheduling the workloads to nodes and maintaining that state.

Another important piece of information that a manifest may include is a set of **requests** and **limits** for the containers. These are integral to how Kubernetes schedules and manages workloads and how to measure your cluster’s performance and ability to match workload demand.

#### Requests and limits

You can declare a request and a limit for CPU (measured in cores) and memory (measured in bytes) for each container running on a pod. A request is the _minimum_ amount of CPU or memory that a node will allocate to the container; a limit is the _maximum_ amount that the container will be allowed to use. A pod’s request and limit is the sum of the requests and limits of its constituent containers.

Requests and limits don't set any rules on a pod's _actual_ resource utilization, but they significantly affect how Kubernetes schedules pods on nodes, as new pods will only be placed on a node that can meet their requests. They also play an important role in how the kubelets manage resources on the worker nodes as each kubelet tries to meet the resource requests of all pods. Requests and limits are also integral to how a kubelet decides to terminate pods (stop the processes running on its containers) and evict pods (delete them from a node). Generally speaking, eviction happens when a node's kubelet detects that it is running low on a specific resource.

We will discuss these concerns in more detail when we talk about important [resource metrics](#resource-metrics) to monitor. You can read more in the Kubernetes documentation about [configuring requests and limits][k8s-resources] and how Kubernetes responds to [low available resources][k8s-resource-handling].

## How EKS works

The primary distinction between an EKS cluster and a self-managed Kubernetes cluster is automation. Amazon automates the provisioning of your Kubernetes infrastructure, and it fully manages the control plane, as well as the networking between your control plane and worker nodes and between pods within each node.

You can launch an EKS cluster using [AWS CloudFormation][aws-cf] templates to automatically provision the necessary elements of your cluster. An EKS cluster requires creating a VPC, or virtual private cloud, to provide isolation for your cluster. For networking management, EKS uses a [Container Network Interface (CNI) plugin][aws-cni] to attach elastic network interfaces, or [ENIs][aws-eni], to each node. Nodes use the ENIs to assign internal VPC IPs to individual pods. Pods can then use these IPs to communicate with other pods across nodes.

{{< img src="eks-cluster-metrics-diagram-rev.png" alt="EKS cluster architecture diagram" popup="true" >}}

### Highly available infrastructure

In addition to automation, one of the main benefits of EKS is built-in high availability. When you provision an EKS cluster, AWS will automatically launch a highly available control plane, with control plane nodes deployed across multiple AWS availability zones. (See the documentation for [which regions][aws-regions] EKS currently supports.) EKS monitors these control plane nodes and automatically replaces them if they become unhealthy. It also installs software updates and patches on control plane nodes. This means that EKS administrators only need to monitor the health and status of their worker nodes. We'll cover how to do this [below](#key-metrics-to-monitor-your-eks-cluster).

Worker nodes in your EKS cluster are EC2 instances. They are built using a specific, [EKS-optimized Amazon Machine Image][eks-ami] and are attached to an [Auto Scaling group][aws-autoscaling]. The launch configuration for an Auto Scaling group includes the minimum and maximum number of worker nodes EKS will run at any one time. AWS automatically balances these nodes across the availability zones that your control plane nodes are running in for load balancing and to ensure availability.

{{< img src="eks-cluster-metrics-container-map.png" alt="EKS monitoring container map" caption="EKS automatically launches control plane and worker nodes in multiple availability zones for load balancing and high availability." popup="false" border="true" >}}

## Key metrics to monitor your EKS cluster

We've explored how an EKS cluster schedules and runs workloads. Now, let’s dive into vital metrics for monitoring your EKS cluster. Understanding how your EKS cluster is performing means monitoring metrics and status checks from various layers. As mentioned in the introduction, these include:

- the [state](#cluster-state-metrics) of the various Kubernetes objects, such as pods and nodes and even your cluster's control plane
- [resource metrics](#resource-metrics), including usage and capacity of containers, pods, and their underlying EC2 instances
- [metrics for other AWS services](#aws-service-metrics) that support your EKS infrastructure and the applications running on it

This article refers to metric terminology from our [Monitoring 101 series](/blog/monitoring-101-collecting-data/), which provides a framework for metric collection and alerting.

Though it is possible to access cluster state information without it, **kube-state-metrics** is a Kubernetes add-on service that listens to the API servers for cluster state information and generates metrics from that data. Using kube-state-metrics allows you to more easily ingest and view cluster state information using a monitoring service. We’ll talk more about accessing cluster state metrics with and without kube-state-metrics in [Part 2][part-two] of this series. When applicable, the below tables include the name of the relevant metric that kube-state-metrics produces.

### Cluster state metrics

Cluster state information is emitted by the Kubernetes API servers. They provide data about the count, health, and availability of various Kubernetes [objects][k8s-objects], such as pods. Internal Kubernetes processes and components use this information to track whether pods are being launched and maintained as expected and to properly schedule new pods.

For Kubernetes objects that are deployed to your cluster, there are several similar but distinct metrics depending on what type of **controller** manages them. Two important types of controllers are:

- Deployments, which create a specified number of pods running one or more containers (often combined with a Service that creates a persistent way to access the pods in the Deployment)
- DaemonSets, which ensure that a particular pod is running on every node (or on a specified set of nodes)

You can read about these and other types of controllers in the [Kubernetes documentation][k8s-controllers].

Cluster state metrics provide you with a high-level view of your cluster and its state. They can surface issues with nodes or pods, alerting you to the possibility that you need to investigate a problem or plan to scale your cluster's capacity.

| Metric | Name in kube-state-metrics | Description | [Metric type](/blog/monitoring-101-collecting-data) |
| Node status | `kube_node_status_condition` | Current health status of the node. Returns a set of node conditions and `true`, `false`, or `unknown` for each | Resource: Availability |
| Desired pods | `kube_deployment_spec_replicas` or `kube_daemonset_status_desired_number_scheduled` | Number of pods specified for a Deployment or DaemonSet | Other |
| Current pods | `kube_deployment_status_replicas` or `kube_daemonset_status_current_number_scheduled` | Number of pods currently running in a Deployment or DaemonSet | Other |
| Pod capacity | `kube_node_status_capacity_pods` | Maximum pods allowed on the node | Resource: Utilization |
| Available pods | `kube_deployment_status_replicas_available` or `kube_daemonset_status_number_available` | Number of pods currently available for a Deployment or DaemonSet | Resource: Availability |
| Unavailable pods | `kube_deployment_status_replicas_unavailable` or `kube_daemonset_status_number_unavailable` | Number of pods currently not available for a Deployment or DaemonSet | Resource: Availability |

While AWS manages the [control plane components](#how-kubernetes-works) of your EKS cluster, it is still useful to [track how those components are performing](#metrics-to-watch-control-plane-metrics). Available metrics—like the number of requests to the API servers, or the latency of requests made by the control plane to AWS for infrastructure provisioning—can surface possible high-level problems with your cluster.

#### Metric to alert on: Node status

This cluster state metric provides a high-level overview of node health. It runs checks on the following [node conditions][k8s-status]:

- `OutOfDisk`
- `Ready` (node is ready to accept pods)
- `MemoryPressure` (node memory is too low)
- `PIDPressure` (too many running processes)
- `DiskPressure` (remaining disk capacity is too low)
- `NetworkUnavailable`

Each check returns `true`, `false`, or, if the worker node hasn't communicated with the relevant control plane node for a grace period (which defaults to 40 seconds), `unknown`. In particular, the `Ready` and `NetworkUnavailable` checks can alert you to nodes that are unavailable or otherwise not usable so that you can troubleshoot further. If a node returns true for the `MemoryPressure` or `DiskPressure` check, the kubelet attempts to reclaim resources. This includes [garbage collection][k8s-garbage] and possibly [deleting pods from the node][k8s-pod-eviction].

#### Metrics to alert on: Desired vs. current pods

While it is possible to manually launch individual pods, it's more likely that you will use [controllers][k8s-deployments] to describe the desired state of your cluster and automate the creation of pods. For example, a Deployment manifest includes a statement of how many replicas of each pod should run. This ensures that the control plane will attempt to keep that many replicas running at all times (i.e., it will recreate a pod if one crashes).
Alternatively, a DaemonSet would launch one pod on every node in your cluster (unless you specify only a subset of nodes).

Kubernetes provides metrics that reflect the number of _desired_ pods (e.g., `kube_deployment_spec_replicas`) and the number of _currently running_ pods (e.g., `kube_deployment_status_replicas`). Ideally, these numbers should match, so comparing these metrics can alert you to issues with your cluster. In particular, a large difference between the numbers might point to resource problems where your nodes lack the capacity to launch new pods. Or, it could indicate a problem with your configuration that is causing pods to fail. In either case, [inspecting pod logs][kubectl-logs] can provide insight into the cause.

#### Metric to alert on: Pod capacity

There are a couple of factors that limit the number of pods a worker node can create. For one, when launching a node, the [kubelet is configured][k8s-kubelet] with a maximum number of pods possible (`--max-pods`), with a default setting of 110.

On top of this, EC2 instances can support a finite number of IP addresses. More specifically, instance types support [limited numbers of elastic network interfaces][eni-limits], and these ENIs have limits on how many IP addresses they can have. Since each pod has a unique IP address, this restricts the number of pods that can run on a given node, separate from any resource considerations.

Pod capacity tracks the number of IP addresses a node's ENIs allow (not the kubelet's configured limit). Keeping track of the [maximum number of IP addresses][aws-max-pods]—and therefore the maximum number of pods—allowed on each instance type and comparing it against the number of running or desired pods, as well as your Kubelets' pod limits, will help you determine if you need to scale up the number of nodes in your fleet.

#### Metrics to watch: Available and unavailable pods

A pod may be _running_ but may not necessarily be _available_, or ready and able to accept traffic. This can be normal during certain circumstances, such as when a pod is newly launched or when a change is made and deployed to the specification of that pod. But, if you see spikes in the number of unavailable pods, or pods that are consistently unavailable, it might indicate a problem with their configuration.

In particular, a large number of unavailable pods might point to poorly configured [readiness probes][readiness-probe]. Developers can set readiness probes to give a pod time to perform initial startup tasks (such as loading large files) before accepting requests so that the application or service doesn't experience problems. Checking a pod’s logs can provide clues as to why it might remain unavailable.

#### Metrics to watch: Control plane metrics

Although you can't manually administer your control plane in EKS, monitoring the overall performance and throughput of requests to your control plane can make you aware of potential cluster-wide problems. Metrics related to your cluster's control plane are exposed through the API servers along with other cluster state information.

In particular, monitoring the latency of requests to different control plane components can give you insight into cluster performance. This includes latency of requests to the API servers (`apiserver_request_latencies_sum`) and requests to the AWS [cloud controller manager][cloud-controller], which acts as an interface between Kubernetes and the underlying AWS infrastructure (`cloudprovider_aws_api_request_duration_seconds_sum`). Spikes in latency can indicate connectivity problems in your control plane that need further investigation.

### Resource metrics

Comparing resource utilization with resource requests and limits will provide a more complete picture of whether your cluster has the capacity to run its workloads and accommodate new ones. It’s important to keep track of resource usage at different layers of your cluster, particularly for your nodes and for the pods running on them.

Monitoring memory, CPU, and disk usage within nodes and pods can help you detect and troubleshoot application-level problems. Note that because resource usage metrics are emitted by individual containers, each pod's resource utilization will be the sum of its constituent containers.

{{< img src="eks-cluster-metrics-resource-graphs.png" alt="EKS monitoring resource utilization" popup="true" wide="true" >}}

For EKS, which uses AWS services for its infrastructure, monitoring resource usage can also provide insights into whether you have provisioned EC2 instances or EBS volumes that are an appropriate type and size for your cluster and the applications running on it.

We will discuss methods for collecting resource metrics from your nodes, pods, and containers in [Part 2][part-two] of this series.

| Metric | Name in kube-state-metrics | Description | [Metric type](/blog/monitoring-101-collecting-data) |
| Memory requests | `kube_pod_container_resource_requests_memory_bytes` | Total memory requests (bytes) of a pod | Resource: Utilization |
| Memory limits | `kube_pod_container_resource_limits_memory_bytes` | Total memory limits (bytes) of a pod | Resource: Utilization |
| Allocatable memory | `kube_node_status_allocatable_memory_bytes` | Total allocatable memory (bytes) of the node | Resource: Utilization |
| Memory utilization | N/A | Total memory in use on a node or pod | Resource: Utilization |
| CPU requests | `kube_pod_container_resource_requests_cpu_cores` | Total CPU requests (cores) of a pod | Resource: Utilization |
| CPU limits | `kube_pod_container_resource_limits_cpu_cores` | Total CPU limits (cores) of a pod | Resource: Utilization |
| Allocatable CPU | `kube_node_status_allocatable_cpu_cores` | Total allocatable CPU (cores) of the node | Resource: Utilization |
| CPU utilization | N/A | Total CPU in use on a node or pod | Resource: Utilization |
| Disk utilization | N/A | Total disk space used on a node or provisioned EBS volume | Resource: Utilization |
| Network in and Network out | N/A | Number of bytes received/sent by a node or pod | Resource: Utilization |

#### Metrics to alert on: Memory limits per pod vs. memory utilization per pod

When specified, a memory limit represents the maximum amount of memory a node will allocate to a container. If a limit is not provided in the manifest and there is not an overall configured default, a pod could use the entirety of a node’s available memory. A node can be oversubscribed, meaning that the sum of the limits for all pods running on a node might be greater than that node’s total allocatable memory. This requires that each pod's defined _request_ is less than the limit. The node's kubelet will reduce resource allocation to individual pods if they use more than they request so long as that allocation at least meets their requests.

Tracking pods' actual memory usage in relation to their specified limits is particularly important because memory is a non-compressible resource. This means that if a pod becomes a memory hog and uses more memory than its defined limit, the kubelet can't throttle its memory allocation, so it terminates the processes running on that pod instead (OOM killed).

Comparing your pods' memory usage to their configured limits will alert you to whether they are at risk of OOM termination, as well as whether their limits make sense. If a pod's limit is too close to its standard memory usage, the pod may get terminated due to an unexpected spike. At the same time, you don't necessarily want to set a pod's limit significantly higher than usage because that can lead to poor scheduling decisions. For example, let's say you have a pod with a memory request of 1GiB and a limit of 4GiB. If it's scheduled on a node with 2GiB of allocatable memory and your pod suddenly needs 3GiB of memory, it will be killed even though it's only using half of its memory limit.

{{< img src="eks-cluster-metrics-memory-limits.png" alt="EKS monitoring memory limits" caption="The graph shows the aggregated memory usage (blue) of a pod with a poorly configured memory limit (red). As its memory usage hits the limit, it gets OOM killed. Kubernetes then attempts to relaunch the pod." popup="true" wide="true" >}}

#### Metric to alert on: Memory utilization

Keeping an eye on memory usage at the pod and node level can provide important insight into your cluster's performance and ability to successfully run workloads. As we've [seen](#metrics-to-alert-on-memory-limits-per-pod-vs-memory-utilization-per-pod), pods whose actual memory usage exceeds their limits will be terminated. Additionally, if a node runs low on available memory, the kubelet flags it as under [memory pressure](#metric-to-alert-on-node-status) and begins procedures to reclaim resources. By default, a node in an EKS cluster is classified as being under memory pressure if available memory falls below 100MiB.

In order to reclaim memory, the kubelet can begin to [evict pods][k8s-pod-eviction], meaning it will delete these pods from the node. The control plane will attempt to reschedule evicted pods on another node with sufficient resources. If your pods' memory usage significantly exceeds their defined requests, it can cause the kubelet to prioritize those pods for eviction, so comparing requests with actual usage can help surface which pods might be vulnerable to eviction.

Habitually exceeding requests could also indicate that your pods are not configured appropriately. Scheduling is largely based on a pod's request, so a pod with a bare-minimum memory request could be placed on a node without enough resources to withstand any spikes or increases in memory needs. Correlating and comparing each pod's actual utilization against its requests can give insight into whether the requests and limits specified in your manifests make sense, or if there might be some issue that is causing your pods to use more resources than expected.

Monitoring overall memory utilization on your nodes can also help you determine when you need to scale your cluster. If node-level usage is high, it could mean you don't have enough nodes to share the workload.

#### Metrics to watch: Memory requests per node vs. allocatable memory per node

Memory requests, as discussed [above](#requests-and-limits), are the minimum amounts of memory a node's kubelet will assign to a container. If a request is not provided, it will default to whatever the value is for the container's limit (which, if also not set, could be all memory on the node). Allocatable memory reflects the amount of memory on a node that is available for pods. Specifically, it takes the overall capacity and subtracts memory requirements for OS and Kubernetes system processes to ensure they will not fight user pods for resources. A node's memory capacity and resulting allocatable memory remain the same based on the [instance type][instance-types] of your nodes specified in their launch configuration. You cannot change it unless you [change the launch configuration][asg-launch] of the entire group.

{{< img src="eks-cluster-metrics-memory-requests.png" alt="EKS monitoring memory requests" caption="Total memory requests per node. The red line is the allocatable memory of each node within this group." popup="true" wide="true" border="true" >}}

Although memory capacity is a static value, keeping an eye on the sum of pod memory requests on each node, versus each node's allocatable memory, is important for capacity planning. These metrics will inform you if your nodes have enough capacity to meet the memory requirements of all current pods and whether the control plane is able to schedule new ones. Kubernetes's scheduling process uses several levels of [criteria][k8s-scheduler] to determine if it can place a pod on a specific node. One of the initial tests is whether a node has enough allocatable memory to satisfy the sum of the requests of all the pods running on that node as well as the new pod.

Comparing memory requests to capacity metrics can also help you troubleshoot problems with launching and running the desired number of pods across your cluster. If you notice that your cluster's count of [current pods](#metrics-to-alert-on-desired-vs-current-pods) is significantly less than the number of desired pods, these metrics might show you that your nodes don't have the resource capacity to host new pods, so the control plane is failing to find a node to assign desired pods to. In this case you might spin up new instances or, in extreme cases, you might need to [migrate to a new worker node fleet][migrate-workers] using a more appropriate EC2 instance type.

#### Metric to alert on: Disk utilization

Out of the box, Amazon EKS supports EBS volumes to provide needed storage, such as the root volumes of your nodes, or [PersistentVolumes][persistent-volumes] (PVs) for persistent storage when you are deploying a stateful application. When you launch your EC2 worker nodes, you can define the size of the root volumes. You can also define storage requests in your manifests and attach them to pods. This will provision PVs to match the requested amount of disk space. These volumes will be attached to a node but only accessible to the pods on that node that are configured to use the volume's storage. For example, you can provision a persistent volume that will be available to a pod running an instance of a database. You can read more about configuring and using volumes in [Kubernetes's documentation][k8s-volumes]. Note that in order to collect and use root volume disk utilization metrics, you will need to install a monitoring agent on your nodes.

Like memory, disk space is a non-compressible resource, so if a kubelet detects low disk space on its root volume, it can cause problems with scheduling pods. If a node's remaining disk capacity crosses a certain resource threshold, it will get flagged as under [disk pressure](#metric-to-alert-on-node-status). The following are the default resource thresholds for a node to come under disk pressure:

| Disk pressure signal | Threshold | Description |
| imagefs.available | 15% | Available disk space for the `imagefs` filesystem, used for images and container-writable layers |
| imagefs.inodesFree | 5% | Available index nodes for the `imagefs` filesystem |
| nodefs.available | 10% | Available disk space for the root filesystem |
| nodefs.inodesFree | 5% | Available index nodes for the root filesystem |

Crossing one of these thresholds leads the kubelet to initiate [garbage collection][k8s-garbage] to reclaim disk space by deleting unused images or dead containers. As a next step, if it still needs to reclaim resources, it will start evicting pods.

In addition to node-level disk utilization, you should also track the usage levels of the volumes used by your pods. This helps you stay ahead of problems at the application or service level. Once these volumes have been provisioned and attached to a node, the node's kubelet exposes several volume-level disk utilization metrics, such as the volume's capacity, utilization, and available space. These volume metrics are available from Kubernetes's Metrics API, which we'll cover in more detail in [part two][part-two] of this series.

If you see that a volume has no space remaining, it could mean that the applications using it are experiencing elevated write errors due to lack of remaining space. Setting an alert to trigger when a volume reaches 80 percent usage can give you time to create new volumes or scale up the storage request to avoid problems.

Another important metric to monitor for your EBS volumes is the number of disk reads and writes. We will discuss EBS volume metrics more [later](#elastic-block-storage-ebs).

#### Metrics to watch: CPU requests per node vs. allocatable CPU per node

Like with [memory](#metrics-to-watch-memory-requests-per-node-vs-allocatable-memory-per-node), allocatable CPU reflects the CPU resources on the node that are available for pod scheduling, while requests are the minimum amount of CPU a node will attempt to allocate to a pod.

As mentioned above, Kubernetes measures CPU in cores. For EKS clusters, one CPU core is equivalent to one [AWS vCPU][vcpu] on an EC2 instance. This makes it easy to compare the number of requested cores against the number of vCPUs available on your nodes' instance type.

Like memory requests, tracking overall CPU requests per node and comparing them to each node's allocatable CPU capacity is valuable for capacity planning of a cluster and will provide insight into whether your cluster can support more pods.

{{< img src="eks-cluster-metrics-cpu-requests.png" alt="EKS monitoring CPU requests" caption="Total CPU requests per node. The blue line is the allocatable CPU of each node within this group." popup="true" wide="true" >}}

#### Metrics to watch: CPU limits per pod vs. CPU utilization per pod

These metrics let you track the maximum amount of CPU a node will allocate to a pod compared to how much CPU it's actually using. Unlike memory, CPU is a compressible resource. This means that if a pod's CPU usage exceeds its defined limit, the node will throttle the amount of CPU available to that pod but allow it to continue running. This throttling can lead to performance issues, so even if your pods won't be terminated, keeping an eye on these metrics will help you determine if your limits are configured properly based on the pods' actual CPU needs.

#### Metric to watch: CPU utilization

Tracking the amount of CPU your pods are using compared to their configured requests and limits, as well as CPU utilization at the node level, will give you important insight into cluster performance. Much like a pod exceeding its CPU limits, a lack of available CPU at the node level can lead to the node throttling the amount of CPU allocated to each pod.

You can configure AWS Auto Scaling to launch new instances in an effort to keep the average CPU utilization close to your specified target value. For example, you can emphasize resource availability by having new instances spin up to keep average CPU utilization around 40 percent across your fleet.

{{< img src="eks-cluster-metrics-autoscaling-plan.png" alt="EKS monitoring AWS autoscaling plan" popup="true" border="true" >}}

Measuring actual utilization compared to requests and limits per pod can also help determine if these are configured appropriately and your pods are requesting enough CPU to run properly. Alternatively, consistently higher than expected CPU usage might point to problems with the pod that need to be identified and addressed.

#### Metrics to watch: Network in and network out

Monitoring network throughput in and out of your nodes and your pods can give you insight into traffic load on your cluster. You can monitor your cluster's network traffic through Amazon's CloudWatch monitoring service or directly from your nodes with a monitoring agent.

Comparing network throughput per node with your EC2 instances' network limits can help you detect potential bottlenecks. Because EBS volumes are networked devices, network performance is particularly important if you want to read or write significant volumes of data.

Unexpected spikes or drops in traffic across your cluster can also alert you to network issues with your nodes or pods. You can compare network metrics with [ELB metrics](#elastic-load-balancing-elb) to see, for example, if a drop in network throughput is correlated with an increase in errors from your load balancers.

### AWS service metrics

An EKS cluster will automatically provision resources from other AWS services—for example, your worker nodes are EC2 instances and storage is provided by EBS volumes. It’s important to monitor the AWS services that your cluster uses to get a complete picture of your EKS infrastructure. AWS services that you will likely use in an EKS cluster include:

- [EC2](#elastic-compute-cloud-ec2) for provisioning worker nodes
- [ELB](#elastic-load-balancing-elb) for load balancing
- [Auto Scaling](#auto-scaling) for dynamically scaling worker nodes
- [EBS](#elastic-block-storage-ebs) for providing persistent storage volumes

Several of the [resource metrics](#resource-metrics) we have discussed so far apply to the AWS services that run your EKS infrastructure, such as measuring CPU utilization on the EC2 instances hosting your worker nodes. But there are additional AWS service metrics that are useful in tracking cluster performance and health. We will cover how to monitor these metrics using CloudWatch in [Part 2][part-two] of this series.

#### Elastic Compute Cloud (EC2)

Your worker nodes are EC2 instances, so the most important information to get from EC2 relates to resource usage, like CPU utilization and network throughput, which are covered [above](#resource-metrics).

However, EC2 emits additional metrics that can be valuable in specific use cases. For example, if your cluster uses an instance type with [bursting][ec2-burst], you likely will want to track your [CPU credit balance](/blog/ec2-monitoring/#cpu-credit-balance). Bursting can provide additional processing power to handle spikes in traffic without needing to launch new nodes, so monitoring your overall burst credit balance can help ensure you will continue to have enough CPU capacity without paying for additional EC2 instances.

For more information about EC2 metrics and status checks and how to monitor them, see [our guide](/blog/ec2-monitoring).

#### Elastic Load Balancing (ELB)

If you have an internet-facing service for your application, for example a web server like NGINX, and have configured that service to use a [load balancer][k8s-service], AWS will automatically provision an Elastic Load Balancer (ELB) to route traffic. By default AWS uses a Classic Load Balancer. You can use a Network Load Balancer by adding the following annotation to your service manifest:

```yaml
service.beta.kubernetes.io/aws-load-balancer-type: nlb
```

The load balancers are the gateway between users and the applications running on your EKS cluster, so monitoring them can give you insight into users’ experience and whether there are any problems with connecting to your applications. For example, metrics like **Latency**, **HTTPCode_ELB_5XX**, or **BackendConnectionErrors** will give you information about the performance and throughput of your load balancers and can alert you to a range of network or connectivity issues (e.g., a misconfigured AWS security group that is blocking traffic, or an incorrect port in your Kubernetes service manifest).

See our [guide on monitoring Amazon ELB](/blog/top-elb-health-and-performance-metrics) for more information on these and other metrics.

#### Auto Scaling

Observing [actual CPU load](#metric-to-watch-cpu-utilization) on your worker nodes and tracking how many nodes are generally running will help you adjust the upper and lower limits for your Auto Scaling groups. For example, if the number of running instances is often near or at the maximum size of your Auto Scaling group, and the load on those nodes remains high, you may want to increase `GroupMaxSize`. Likewise, if your group rarely needs more than the minimum number of nodes and CPU usage overall remains low, it might be more cost effective to decrease the lower limit. Auto Scaling can help with capacity planning, but it's still worth monitoring your cluster's actual activity to achieve a balance between having available resources and minimizing your cloud footprint and cost.

#### Elastic Block Storage (EBS)

EKS provisions Amazon EBS root volume storage for your nodes and PersistentVolumeClaims as needed by your applications. In addition to tracking overall [disk utilization](#metric-to-alert-on-disk-utilization), metrics that track throughput to and from your volumes—such as **VolumeReadOps** or **VolumeWriteBytes**—provide insight into the performance of your volumes and whether they are configured properly for your use case. EBS offers several [volume types][ebs-volumes] that are optimized for different types of workloads. Some are better at handling high levels of random I/O transactions and others are more appropriate for significant amounts of streaming throughput.

So, for example, if your cluster is running a large transactional database that performs a lot of small, random reads and writes, and you choose a volume type that has a very low limit on I/O operations per second, it could lead to bottlenecks or high latency when its limit is met.

For more detailed information on different volume types and key metrics, see our [guide on monitoring EBS](/blog/amazon-ebs-monitoring).

## Events

Both Kubernetes’s API servers and certain AWS services emit events related to changes in the status of your infrastructure. Tracking these events is an important part of monitoring a dynamic EKS cluster that is constantly adding, removing, or updating pods and nodes. For example, Kubernetes events help notify you about the creation or termination of replicas, or the failure of a pod to launch. In terms of AWS services, Auto Scaling emits notifications when it launches or destroys instances, and EC2 publishes events regarding terminating or recreating an instance for maintenance.

Tracking these events and correlating them with resource and cluster state metrics can shed light on possible issues, such as insufficient node capacity. For instance, if you are alerted to abnormal behavior in the number of available pods, Kubernetes events can shed light into whether there are scheduling problems with a specific Deployment. If so, you can investigate further.

{{< img src="eks-cluster-metrics-events.png" alt="EKS monitoring events" caption="Kubernetes events can help reveal issues with specific Deployments." popup="true" wide="true" border="true" >}}

AWS events from services like EC2 and Auto Scaling can also provide information on the state of your cluster's underlying infrastructure. These can help identify possible high-level resource availability issues. For example, Auto Scaling events will help confirm whether instances are being launched properly when needed. Other events might relate to instances failing health checks or being scheduled for termination. If you notice problems with your [nodes' status](#metric-to-alert-on-node-status), or that your nodes aren't scaling as expected, AWS service events can provide more information.

## Start monitoring your EKS cluster

In this post we’ve taken a look at key metrics for monitoring Amazon EKS. These include both Kubernetes metrics to track the performance and health of your EKS cluster and metrics for  additional AWS services that provide the infrastructure your cluster runs on. Together, they will give you insight into whether any parts your cluster are not working properly and help you determine if you need to scale up your cluster to support the applications running on it.

In the [next part][part-two] of this series, we will dive into how to collect these metrics, including using common Kubernetes monitoring tools as well as CloudWatch to gather AWS service metrics.

## Acknowledgment

We wish to thank our friends at AWS for their technical review of this series.

_Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/eks/eks-cluster-metrics.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues)._

[aws-eks]: https://aws.amazon.com/eks/
[k8s]: https://kubernetes.io/
[aws-ecs]: https://aws.amazon.com/ecs/
[k8s-conformant]: https://github.com/cncf/k8s-conformance
[kubectl]: https://kubernetes.io/docs/tasks/tools/install-kubectl/
[aws-vpc]: https://aws.amazon.com/vpc/
[k8s-pods]: https://kubernetes.io/docs/concepts/workloads/pods/pod-overview/
[aws-regions]: https://docs.aws.amazon.com/general/latest/gr/rande.html?id=docs_gateway#eks_region
[aws-autoscaling]: https://aws.amazon.com/ec2/autoscaling/
[k8s-controllers]: https://kubernetes.io/docs/concepts/workloads/controllers/
[k8s-objects]: https://kubernetes.io/docs/concepts/#kubernetes-objects
[k8s-deployments]: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
[readiness-probe]: https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-probes/#define-readiness-probes
[vcpu]: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-optimize-cpu.html
[k8s-resources]: https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container
[aws-cni]: https://github.com/aws/amazon-vpc-cni-k8s
[aws-eni]: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-eni.html
[aws-max-pods]: https://github.com/awslabs/amazon-eks-ami/blob/master/files/eni-max-pods.txt
[k8s-metrics-server]: https://github.com/kubernetes-incubator/metrics-server
[ebs-volumes]: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSVolumeTypes.html
[instance-types]: https://aws.amazon.com/ec2/instance-types/
[part-two]: https://www.datadoghq.com/blog/collecting-eks-cluster-metrics
[kubectl-logs]: https://www.datadoghq.com/blog/collecting-eks-cluster-metrics#viewing-pod-logs-with-kubectl-logs
[k8s-api]: https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.13/
[etcd]: https://github.com/etcd-io/etcd
[eks-ami]: https://docs.aws.amazon.com/eks/latest/userguide/eks-optimized-ami.html
[instance-types]: https://aws.amazon.com/ec2/instance-types/
[cloudformation-tags]: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html
[getting-started]: https://docs.aws.amazon.com/eks/latest/userguide/getting-started.html
[k8s-service]: https://kubernetes.io/docs/concepts/services-networking/service/#loadbalancer
[k8s-status]: https://kubernetes.io/docs/concepts/architecture/nodes/#condition
[auto-scaling]: https://docs.aws.amazon.com/autoscaling/index.html#lang/en_us
[k8s-scheduler]: https://github.com/kubernetes/community/blob/master/contributors/devel/sig-scheduling/scheduler.md
[k8s-resource-handling]: https://kubernetes.io/docs/tasks/administer-cluster/out-of-resource/
[migrate-workers]: https://docs.aws.amazon.com/eks/latest/userguide/migrate-stack.html
[k8s-volumes]: https://kubernetes.io/docs/concepts/storage/volumes/
[persistent-volumes]: https://kubernetes.io/docs/concepts/storage/persistent-volumes/
[ec2-burst]: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/burstable-performance-instances.html
[asg-launch]: https://docs.aws.amazon.com/autoscaling/ec2/userguide/change-launch-config.html
[kubelet-options]: https://kubernetes.io/docs/reference/command-line-tools-reference/kubelet/#options
[eks-bootstrap]: https://aws.amazon.com/blogs/opensource/improvements-eks-worker-node-provisioning/
[eks-storageclass]: https://docs.aws.amazon.com/eks/latest/userguide/storage-classes.html
[k8s-garbage]: https://kubernetes.io/docs/concepts/cluster-administration/kubelet-garbage-collection/
[k8s-allocatable]: https://kubernetes.io/docs/tasks/administer-cluster/reserve-compute-resources/#node-allocatable
[ksm-metrics]: https://github.com/kubernetes/kube-state-metrics/tree/master/Documentation
[aws-cf]: https://docs.aws.amazon.com/cloudformation/index.html#lang/en_us
[k8s-pod-eviction]: https://kubernetes.io/docs/tasks/administer-cluster/out-of-resource/#eviction-policy
[kube-scheduler]: https://kubernetes.io/docs/reference/command-line-tools-reference/kube-scheduler/
[kube-controller-manager]: https://kubernetes.io/docs/reference/command-line-tools-reference/kube-controller-manager/
[k8s-kubelet]: https://kubernetes.io/docs/reference/command-line-tools-reference/kubelet/
[eni-limits]: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-eni.html#AvailableIpPerENI
[cloud-controller]: https://kubernetes.io/docs/concepts/overview/components/#cloud-controller-manager
