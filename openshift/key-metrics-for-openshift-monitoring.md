## What is OpenShift?

[Red Hat OpenShift](https://www.openshift.com/) is a Kubernetes-based platform that helps enterprise users deploy and maintain containerized applications. Users can deploy OpenShift as a self-managed cluster or use a managed service, which are available from major cloud providers including [AWS](https://aws.amazon.com/quickstart/architecture/openshift/), [Azure](https://azure.microsoft.com/en-us/services/openshift/), and [IBM Cloud](https://www.ibm.com/cloud/openshift).

OpenShift provides a range of benefits over a self-hosted Kubernetes installation or a managed Kubernetes service (e.g., Amazon EKS, Google Kubernetes Engine, or Azure Kubernetes Service). These include more robust multi-tenancy features, advanced security and monitoring, integrated networking and storage, CI/CD pipelines, container image management, and other developer tools.

Monitoring your OpenShift clusters is vital for both administrators and developers. It helps ensure that all deployed workloads are running smoothly and that the environment is properly scoped so that developers can continue to deploy and scale apps. In this post, we will cover key metrics that will give you insight into the health, performance, and capacity of your OpenShift cluster. Primarily, this involves monitoring the Kubernetes objects that are the foundation of OpenShift. We will look at three broad categories of metrics:

- [Cluster state metrics](#cluster-state-metrics)
- [Container and node resource and quota metrics](#resource-metrics)
- Work metrics from the [control plane](#control-plane-metrics)

We will also go over [cluster events](#cluster-events), which can provide further insight into how your cluster is performing. Before we dive in, because OpenShift is based on Kubernetes, let's quickly look at how Kubernetes works and what OpenShift adds to it. You can also jump directly to the [metrics](#key-metrics-for-openshift-monitoring).

## A brief guide to Kubernetes
A Kubernetes cluster is comprised of two types of nodes:

- One or more **master nodes** that host components for administering the cluster and scheduling container workloads
- **Worker nodes** that host and run the container workloads

You can—and generally should—run multiple master nodes distributed across availability zones to ensure high availability and redundancy for your cluster. The master nodes in aggregate make up the **control plane**. The control plane runs four key services for cluster administration:

- The **API server** exposes the Kubernetes APIs for interacting with the cluster
- The **controller manager** watches the current state of the cluster and attempts to move it toward the desired state
- The **scheduler** assigns workloads to nodes
- **etcd** stores data about cluster configuration, cluster state, and more*

**These data store instances may be co-located with the other control plane services on dedicated control plane nodes or hosted externally on separate hosts.*

Worker nodes are host machines. Each one has a **kubelet** process that monitors the worker node and acts as the point of contact between that node and the control plane. The kubelet receives requests from the control plane and instructs the worker node’s runtime environment to create and manage **pods** to run the workloads. Pods are isolated, self-contained, easily replicated groups of one or more containers that share storage and a network IP. For example, one pod could be a single instance of an application, while another could be an instance of NGINX. Other pods could self-terminate once they complete a specific job.

### Setting the state of the cluster
**Controllers** are the key to how Kubernetes can effectively orchestrate complex, dynamic workloads. Manifests—configuration files in YAML or JSON format—provide the API server with a desired state, or a specific set of objects that you want your cluster to run. Manifests describe things like the number of pods to launch, what type of containers those pods will run, and any necessary settings. The control plane will then do the work of automatically scheduling, restarting, or terminating containers to run the desired workloads.

## What OpenShift adds to Kubernetes
While OpenShift's core architecture is based on Kubernetes it adds robust functionality for cluster administration and application deployment. Additionally, there are a few key considerations in terms of the underlying technologies that OpenShift uses.

### A specific environment
OpenShift requires that your master and worker nodes run on a specific OS, which is determined by the version of OpenShift you are using. OpenShift 3.x requires that both your master and worker nodes run Red Hat Enterprise Linux (RHEL). As of OpenShift 4.x, your master nodes must use Red Hat Enterprise Linux CoreOS (RHCOS), while worker nodes may run either RHEL or RHCOS. In addition to this move to RHCOS, OpenShift 4 has also shifted to using [CRI-O](https://cri-o.io/) as its default container runtime instead of Docker.

### Extending Kubernetes
Compared to a standard Kubernetes installation, OpenShift adds several features that make it easier to secure clusters and maintain production-grade applications. These include:

- Different default configurations, such as automatically requiring [role-based access control (RBAC)](https://docs.openshift.com/container-platform/4.1/authentication/using-rbac.html) across the entire cluster and restricting pod permissions with [Security Context Constraints (SCC)](https://docs.openshift.com/container-platform/4.2/authentication/managing-security-context-constraints.html).
- First-class API objects that extend the Kubernetes API. For example, the `DeploymentConfig` API object [extends](https://docs.openshift.com/container-platform/4.2/applications/deployments/what-deployments-are.html#delpoymentconfigs-specific-features_what-deployments-are) the Deployment controller and allows developers to integrate lifecycle hooks, event-based triggers, and version control into their applications.
- Extensive support for **Operators**, which are packaged Kubernetes applications that automate or manage sets of tasks, including cluster monitoring, logging, and image registration. OpenShift also uses Operators to provision certain infrastructure components like storage volumes. _Note that OpenShift 3.x uses **service brokers** for similar purposes. These have been deprecated in 4.x in favor of Operators._
- A web console that allows administrators and developers to visualize information about their clusters and deploy applications.

## Key metrics for OpenShift monitoring
Now that we've taken a look at how Kubernetes runs containerized workloads, and what OpenShift does differently, let’s dive into vital metrics for monitoring your OpenShift cluster. To understand how OpenShift is performing, you'll need to monitor metrics and status checks from several layers of architecture. As mentioned in the introduction, these include:

- the [state](#cluster-state-metrics) of the various Kubernetes objects, such as pods and nodes and even your cluster’s control plane
- [resource metrics](#resource-metrics), including usage, capacity, any defined quotas of containers, pods, and their underlying hosts
- [control plane work metrics](#control-plane-metrics) that provide insight into Kubernetes API workload and activity

This article refers to metric terminology from our [Monitoring 101 series](/blog/monitoring-101-collecting-data/), which provides a framework for metric collection and alerting.

### Cluster state metrics
The Kubernetes API servers emit data about the count, health, and availability of various Kubernetes [objects](https://kubernetes.io/docs/concepts/#kubernetes-objects), such as pods. Internal Kubernetes processes and components use this information to schedule new pods and to track whether pods are being launched and maintained as expected. These cluster state metrics can provide you with a high-level view of your cluster and its state. They can also surface issues with nodes or pods, alerting you to the possibility that you need to investigate a bottleneck or scale out your cluster.

For Kubernetes objects that are deployed to your cluster, several similar but distinct metrics are available, depending on what type of controller manages those objects. Two important types of controllers are:

- Deployments, which create a specified number of pods (often combined with a Service that creates a persistent point of access to the pods in the Deployment)
- DaemonSets, which ensure that a particular pod is running on every node (or on a specified set of nodes)

You can learn about these and other types of controllers in the [Kubernetes documentation](https://kubernetes.io/docs/concepts/workloads/controllers/). While OpenShift extends these controllers with, for example, DeploymentConfigs, they still have the same underlying properties, and monitoring the status of the objects they deploy to your cluster works the same way.

By default, OpenShift's [monitoring stack][part-two] includes the **kube-state-metrics** service, which is a Kubernetes add-on that listens to the API servers for cluster state information and generates metrics from that data. The kube-state-metrics service allows you to more easily ingest and view cluster state information using a monitoring platform. When applicable, the below tables include the names of the relevant metrics that kube-state-metrics produces.

| Metric | Name in kube-state-metrics | Description | [Metric type](/blog/monitoring-101-collecting-data) |
|--- |--- |--- |--- |
| Node condition | `kube_node_status_condition` | Current health status of the node. Returns a set of node conditions (listed below) and `true`, `false`, or `unknown` for each | Resource: Availability |
| Desired pods | `kube_deployment_spec_replicas` or `kube_daemonset_status_desired_number_scheduled` | Number of pods specified for a Deployment or DaemonSet | Other |
| Current pods | `kube_deployment_status_replicas` or `kube_daemonset_status_current_number_scheduled` | Number of pods currently running in a Deployment or DaemonSet | Other |
| Available pods | `kube_deployment_status_replicas_available` or `kube_daemonset_status_number_available` | Number of pods currently available for a Deployment or DaemonSet | Resource: Availability |
| Unavailable pods | `kube_deployment_status_replicas_unavailable` or `kube_daemonset_status_number_unavailable` | Number of pods currently not available for a Deployment or DaemonSet | Resource: Availability |

#### Metric to alert on: Node condition
This cluster state metric provides a high-level overview of node health. It runs checks on the following [node conditions](https://kubernetes.io/docs/concepts/architecture/nodes/#condition):

- `OutOfDisk`
- `Ready` (node is ready to accept pods)
- `MemoryPressure` (node memory is too low)
- `PIDPressure` (too many running processes)
- `DiskPressure` (remaining disk capacity is too low)
- `NetworkUnavailable`

Each check returns `true`, `false`, or, if the worker node hasn't communicated with the relevant control plane node for a grace period (which defaults to 40 seconds), `unknown`. In particular, the `Ready` and `NetworkUnavailable` checks can alert you to nodes that are unavailable or otherwise not usable so that you can troubleshoot further. If a node returns `true` for the `MemoryPressure` or `DiskPressure` check, the kubelet attempts to reclaim resources (e.g., by running [garbage collection](https://docs.openshift.com/container-platform/4.1/nodes/nodes/nodes-nodes-garbage-collection.html) or possibly [deleting pods from the node](https://docs.openshift.com/container-platform/3.11/admin_guide/out_of_resource_handling.html#out-of-resource-eviction-of-pods)).

#### Metrics to alert on: Desired vs. current pods
While you can manually launch individual pods for small-scale experiments, in production you will more likely use [controllers](#setting-the-state-of-the-cluster) to describe the desired state of your cluster and automate the creation of pods. For example, a Deployment manifest states how many replicas of each pod should run. This ensures that the control plane will attempt to keep that many replicas running at all times, even if one or more nodes or pods crashes. Alternatively, a DaemonSet launches one pod on every node in your cluster (unless you specify a subset of nodes). This is often useful for installing a monitoring agent or other node-level utility across your cluster.

Kubernetes provides metrics that reflect the number of _desired_ pods (e.g., `kube_deployment_spec_replicas`) and the number of _currently running_ pods (e.g., `kube_deployment_status_replicas`). Typically, these numbers should match unless you are in the midst of a deployment or other transitional phase, so comparing these metrics can alert you to issues with your cluster. In particular, a large disparity between desired and running pods can point to bottlenecks, such as your nodes lacking the resource capacity to schedule new pods. It could also indicate a problem with your configuration that is causing pods to fail. In either case, inspecting pod logs can provide insight into the cause, as we'll detail in [Part 2][part-two] of this series.

#### Metrics to watch: Available and unavailable pods
A pod may be _running_ but not _available_, meaning it is not ready and able to accept traffic. This is normal during certain circumstances, such as when a pod is newly launched or when a change is made and deployed to the specification of that pod. But if you see spikes in the number of unavailable pods, or pods that are consistently unavailable, it might indicate a problem with their configuration.

{{< img src="openshift-monitoring-metrics-available-pods.png" border="true" popup="true" >}}

In particular, a large number of unavailable pods might point to poorly configured [readiness probes](https://docs.openshift.com/container-platform/4.2/applications/application-health.html#application-health-about_application-health). Developers can set readiness probes to give a pod time to perform initial startup tasks (such as loading large files) before accepting requests so that the application or service doesn't experience problems. Checking a pod’s logs can provide clues as to why it is stuck in a state of unavailability.

### Resource metrics
Monitoring memory, CPU, and disk usage within nodes and pods can help you detect and troubleshoot application-level problems. But monitoring the resource usage of Kubernetes objects is not as straightforward as monitoring a traditional application. In a Kubernetes-based environment, you still need to track the actual resource usage of your workloads, but those statistics become more actionable when you monitor them in the context of resource requests and limits, which govern how Kubernetes manages finite resources and schedules workloads across the cluster. In the metric table below, we'll provide details on how you can monitor actual utilization alongside the requests and limits for a particular resource. 

#### Requests and limits
In a Deployment manifest, you can declare a **request** and a **limit** for CPU (measured in cores), memory (measured in bytes), and storage (also in bytes) for each container running on a pod. A request is the _minimum_ amount of CPU or memory that a node will allocate to the container; a limit is the _maximum_ amount that the container will be allowed to use. The requests and limits for an entire pod are calculated from the sum of the requests and limits of its constituent containers.

Requests and limits do not define a pod’s actual resource utilization, but they significantly affect how Kubernetes schedules pods on nodes. Specifically, new pods will only be placed on a node that can meet their requests. Requests and limits are also integral to how a kubelet manages available resources by terminating pods (stopping the processes running on its containers) or evicting pods (deleting them from a node), which we'll cover in more detail [below](#metric-to-alert-on-memory-utilization). 

Comparing resource utilization with resource requests and limits will provide a more complete picture of whether your cluster has the capacity to run its workloads and accommodate new ones. This is particularly true in an OpenShift environment that is likely to be multi-tenant—with multiple developers deploying and managing workloads using the same resource pool—and have resource quotas in place to keep any one project or Deployment from requesting or using too many resources.

{{< img src="openshift-monitoring-metrics-resources.png" border="true" popup="true" >}}

| Metric | Name in kube-state-metrics | Description | [Metric type](/blog/monitoring-101-collecting-data) |
|--- |--- |--- |--- |
| Memory requests | `kube_pod_container_resource_requests_memory_bytes` | Total memory requests (bytes) of a pod | Resource: Utilization |
| Memory limits | `kube_pod_container_resource_limits_memory_bytes` | Total memory limits (bytes) of a pod | Resource: Utilization |
| Allocatable memory | `kube_node_status_allocatable_memory_bytes` | Total allocatable memory (bytes) of the node | Resource: Utilization |
| Memory utilization | N/A | Total memory in use on a node or pod | Resource: Utilization |
| CPU requests | `kube_pod_container_resource_requests_cpu_cores` | Total CPU requests (cores) of a pod | Resource: Utilization |
| CPU limits | `kube_pod_container_resource_limits_cpu_cores` | Total CPU limits (cores) of a pod | Resource: Utilization |
| Allocatable CPU | `kube_node_status_allocatable_cpu_cores` | Total allocatable CPU (cores) of the node | Resource: Utilization |
| CPU utilization | N/A | Total CPU in use on a node or pod | Resource: Utilization |
| Disk utilization | N/A | Total disk space used on a node | Resource: Utilization |
| Resource and object quota limits | _multiple_ | The total amount or number of the specified resource or object allowed per project or per cluster | Resource: Utilization |
| Resource and object quota used | _multiple_ | The total amount or number of the specified resource or object in use per project or per cluster | Resource: Utilization |
| Network throughput | N/A | Total bytes per second sent or received by a node or pod | Resource: Utilization |

#### Metrics to alert on: Memory limits per pod vs. memory utilization per pod
When specified, a memory limit represents the maximum amount of memory a node will allocate to a container. If a limit is not provided in the manifest and there is not an overall configured default, a pod could use the entirety of a node’s available memory. Note that a node can be _oversubscribed_, meaning that the sum of the limits for all pods running on a node might be greater than that node’s total allocatable memory. This requires that the pods' defined _requests_ are below the limit. The node's kubelet will reduce resource allocation to individual pods if they use more than they request so long as that allocation at least meets their requests.

Tracking pods' actual memory usage in relation to their specified limits is particularly important because memory is a non-compressible resource. In other words, if a pod uses more memory than its defined limit, the kubelet can't throttle its memory allocation, so it terminates the processes running on that pod instead. If this happens, the pod will show a status of `OOMKilled`.

Comparing your pods' memory usage to their configured limits will alert you to whether they are at risk of being OOM killed, as well as whether their limits make sense. If a pod's limit is too close to its standard memory usage, the pod may get terminated due to an unexpected spike. On the other hand, you may not want to set a pod's limit significantly higher than its typical usage because that can lead to poor scheduling decisions. For example, the scheduler might place a pod with a memory request of 1GiB and a limit of 4GiB on a node with 2GiB of allocatable memory (more than sufficient to meet its request). If the pod suddenly needs 3GiB of memory, it will be killed even though it's well below its memory limit.

#### Metric to alert on: Memory utilization
Keeping an eye on memory usage at the pod and node level can provide important insight into your cluster's performance and ability to successfully run workloads. As we've [seen](#metrics-to-alert-on-memory-limits-per-pod-vs-memory-utilization-per-pod), pods whose actual memory usage exceeds their limits will be terminated. Additionally, if a node runs low on available memory, the kubelet flags it as under [memory pressure](#metric-to-alert-on-node-condition) and begins to reclaim resources. 

In order to reclaim memory, the kubelet can [evict pods](https://docs.openshift.com/container-platform/3.11/admin_guide/out_of_resource_handling.html#out-of-resource-eviction-of-pods), meaning it will delete these pods from the node. The control plane will attempt to reschedule evicted pods on another node with sufficient resources. If your pods' memory usage significantly exceeds their defined requests, it can cause the kubelet to prioritize those pods for eviction, so comparing requests with actual usage can help surface which pods might be vulnerable to eviction.

Habitually exceeding requests could also indicate that your pods are not configured appropriately. As mentioned above, scheduling is largely based on a pod's request, so a pod with a bare-minimum memory request could be placed on a node without enough resources to withstand any spikes or increases in memory needs. Correlating and comparing each pod's actual utilization against its requests can give insight into whether the requests and limits specified in your manifests make sense, or if there might be some issue that is causing your pods to use more resources than expected.

Monitoring overall memory utilization on your nodes can also help you determine when you need to scale your cluster. If node-level usage is high, you may need to add nodes to the cluster to share the workload.

#### Metrics to watch: Memory requests per node vs. allocatable memory per node
Memory requests, as discussed [above](#requests-and-limits), are the minimum amounts of memory a node's kubelet will assign to a container. If a request is not provided, it will default to whatever the value is for the container's limit (which, if also not set, could be all memory on the node). Allocatable memory reflects the amount of memory on a node that is available for pods. Specifically, it takes the overall capacity and subtracts memory requirements for OS, Kubernetes, and OpenShift system processes to ensure they will not fight user pods for resources. 

Although memory capacity is a static value, maintaining an awareness of the sum of pod memory requests on each node, versus each node's allocatable memory, is important for capacity planning. These metrics will inform you if your nodes have enough capacity to meet the memory requirements of all current pods and whether the control plane is able to schedule new ones. Kubernetes's scheduling process uses several levels of [criteria](https://kubernetes.io/docs/concepts/scheduling/kube-scheduler/#kube-scheduler-implementation) to determine if it can place a pod on a specific node. One of the initial tests is whether a node has enough allocatable memory to satisfy the sum of the requests of all the pods running on that node, plus the new pod.

Comparing memory requests to capacity metrics can also help you troubleshoot problems with launching and running the desired number of pods across your cluster. If you notice that your cluster's count of [current pods](#metrics-to-alert-on-desired-vs-current-pods) is significantly less than the number of desired pods, these metrics might show you that your nodes don't have the resource capacity to host new pods, so the control plane is failing to find a node to assign desired pods to. One straightforward remedy for this issue is to provision more nodes for your cluster. You might also want to track memory requests by project (or Kubernetes namespace) to determine if OpenShift is reserving significantly more memory for certain projects over others.

{{< img src="openshift-monitoring-metrics-requests.png" border="true" popup="true" >}}

#### Metric to alert on: Disk utilization
Like memory, disk space is a non-compressible resource. If a kubelet detects low disk space on its root volume, it can cause problems for the scheduler with assigning pods to that node. If a node's remaining disk capacity crosses a certain resource threshold, it will get flagged as under [disk pressure](#metric-to-alert-on-node-status). A node's kubelet tracks disk usage for two filesystems: `nodefs`, which stores local volumes, daemon logs, etc.; and `imagefs`, which is optional and is used to store container images.

By default, Kubernetes uses hard eviction thresholds, meaning that the Kubelet will immediately begin trying to [reclaim space](https://docs.openshift.com/container-platform/4.1/nodes/nodes/nodes-nodes-garbage-collection.html) by deleting unused images or dead containers if disk usage passes a threshold. As a next step, if it still needs to reclaim resources, it will start evicting pods. The following are the default resource thresholds for a node to come under disk pressure:

| Disk pressure signal | Threshold | Description |
|--- |--- |--- |
| imagefs.available | 15% | Available disk space for the `imagefs` filesystem, used for images and container-writable layers |
| imagefs.inodesFree | 5% | Available index nodes for the `imagefs` filesystem |
| nodefs.available | 10% | Available disk space for the root filesystem |
| nodefs.inodesFree | 5% | Available index nodes for the root filesystem |

Administrators may change these thresholds and also configure soft eviction thresholds. A soft eviction threshold includes the threshold value and a grace period during which the kubelet will not initiate garbage collection. Configuring a soft eviction threshold and setting an alert for when disk usage drops below it gives you time to reclaim disk space without the risk of the kubelet deleting images or evicting pods. 

In addition to node-level disk utilization, you should also track the usage levels of the [volumes](https://docs.openshift.com/container-platform/4.2/nodes/containers/nodes-containers-volumes.html) used by your pods. This helps you stay ahead of problems at the application or service level. Once these volumes have been provisioned and attached to a node, the node's kubelet exposes several volume-level disk utilization metrics, such as the volume's capacity, utilization, and available space. These volume metrics are available from Kubernetes's Metrics API, which we'll cover in more detail in [Part 2][part-two] of this series.

If a volume runs out of remaining space, your applications that depend on that volume will likely experience errors as they try to write new data to the volume. Setting an alert to trigger when a volume reaches 80 percent usage can give you time to create new volumes or scale up the storage request to avoid problems.

#### Metrics to alert on: Resource and object quota used vs. resource and object quota limits
OpenShift administrators must balance cluster capacity against the resource needs of the workloads running on their clusters, while developers need to make sure new services will deploy successfully. Resource and object quotas are a vital component of handling this.

Resource quotas enable administrators to set constraints on the maximum amount of resources—such as memory, CPU, or storage—or number of cluster objects—pods, services, load balancers, etc.—that workloads are allowed to request and use. These restrictions can be set within a single project using a [ResourceQuota](https://docs.openshift.com/container-platform/4.2/applications/quotas/quotas-setting-per-project.html) object. For example, if a project has a `requests.cpu` quota of one core and `limits.cpu` quota of three cores, the scheduler will reject any new workloads whose defined CPU request or limit would bring the sum total of all requests and limits above the quotas for that project.

OpenShift adds support for [ClusterResourceQuotas](https://docs.openshift.com/container-platform/4.2/applications/quotas/quotas-setting-across-multiple-projects.html), which are resource and object quotas across multiple projects using specific annotations or labels. For example, administrators can set quotas for specific users, aggregated across all their projects, or limit allowed resource usage across all projects that share a certain label. This can help ensure, for example, that a single user or project does not consume a disproportionate amount of the cluster's resources.

OpenShift emits metrics both for the limits of your ResourceQuotas and ClusterResourceQuotas as well as for how much of those quotas are being used. This can help cluster administrators see if the scheduler may start to reject new workloads due to hitting any quota constraints. Developers can also view quotas established for the projects they are deploying to in order to track whether they have access to sufficient resources to deploy their applications.

{{< img src="openshift-monitoring-metrics-applied-quotas.png" border="true" popup="true" caption="Developers can visualize applied ClusterResourceQuota limits and usage across projects they are deploying to." >}}

#### Metrics to watch: CPU requests per node vs. allocatable CPU per node
As with [memory](#metrics-to-watch-memory-requests-per-node-vs-allocatable-memory-per-node), requests are the minimum amount of CPU a node will attempt to allocate to a pod, while allocatable CPU reflects the CPU resources on the node that are available for pod scheduling.

Kubernetes measures CPU in cores. Tracking overall CPU requests per node and comparing them to each node's allocatable CPU capacity is valuable for capacity planning of a cluster and will provide insight into whether your cluster can support more pods.

#### Metrics to watch: CPU limits per pod vs. CPU utilization per pod
These metrics let you track the maximum amount of CPU a node will allocate to a pod compared to how much CPU it's actually using. Unlike memory, CPU is a compressible resource. This means that if a pod's CPU usage exceeds its defined limit, the node will throttle the amount of CPU available to that pod but allow it to continue running. This throttling can lead to performance issues, so even if your pods won't be terminated, keeping an eye on these metrics will help you determine if your limits are configured properly based on the pods' actual CPU needs.

#### Metric to watch: CPU utilization
Tracking the amount of CPU your pods are using compared to their configured requests and limits, as well as CPU utilization at the node level, will give you important insight into cluster performance. Much like a pod exceeding its CPU limits, a lack of available CPU at the node level can lead to the node's kubelet throttling the amount of CPU allocated to each pod running on that node.

Measuring actual utilization compared to requests and limits per pod can help determine if these are configured appropriately and your pods are requesting enough CPU to run properly. Alternatively, CPU usage that is consistently higher than expected (based on historical trends) and requested might point to problems with the pod that need to be identified and addressed.

#### Metrics to watch: Network throughput
Regardless of whether you run OpenShift in the cloud, on-premise, or both, your environment consists of objects that must communicate with each other—and with the outside world—over a network. This means that network connectivity issues at different levels can have a significant impact on the health and performance of your cluster. For example, if your etcd servers can't communicate with one another, they'll lose quorum, leading to the possible loss of your cluster. Tracking network throughput in and out of your nodes can help surface if they're having issues communicating with the control plane. Or, monitoring network activity aggregated by your services can help identify possible configuration issues.

Overall network throughput can also give you a sense of how much work your cluster is performing. You might find you need to scale your nodes or pods (either by adding new ones or beefing up the resources of existing ones) to handle spikes or greater than expected network traffic.

### Control plane metrics
Kubernetes exposes metrics for control plane components, including the API server and scheduler, which you can collect and track to ensure that your cluster's central nervous system is healthy. The below table includes some key metrics for the different control plane parts, but note that this is far from an exhaustive list. The metric names in this table are as they appear in [Prometheus format](https://github.com/prometheus/docs/blob/master/content/docs/instrumenting/exposition_formats.md#text-based-format).

| Metric | Description | [Metric type](/blog/monitoring-101-collecting-data) |
|--- |--- |--- |
| `apiserver_request_latencies_count` | Total count of requests to the API server for a specific resource and verb | Work: Throughput |
| `apiserver_request_latencies_sum` | Sum of request duration to the API server for a specific resource and verb, in microseconds | Work: Performance |
| `workqueue_queue_duration_seconds` | Total number of seconds that items spent waiting in a specific work queue | Work: Performance | 
| `workqueue_work_duration_seconds` | Total number of seconds spent processing items in a specific work queue | Work: Performance |
| `scheduler_schedule_attempts_total` | Total count of attempts to schedule a pod, broken out by result | Work: Throughput | 
| `scheduler_e2e_scheduling_latency_microseconds` | Total elapsed latency in scheduling workload pods on worker nodes, in microseconds | Work: Performance |  

#### Metrics to watch: `apiserver_request_latencies_count` and `apiserver_request_latencies_sum`
Kubernetes provides metrics on the number and duration of requests to the API server for each combination of resource (e.g., pods, deployments) and type of action (e.g., GET, LIST, POST, DELETE). By dividing the summed latency for a specific type of request by the number of requests of that type, you can compute a per-request average latency. You can also use a monitoring service to compute a real-time average of these metrics over time. By tracking the number and latency of specific kinds of requests, you can see if the cluster is falling behind in executing any user-initiated commands to create, delete, or query resources, likely due to the API server being overwhelmed with requests.

#### Metrics to watch: `workqueue_queue_duration_seconds` and `workqueue_work_duration_seconds`
These latency metrics provide insight into the performance of the controller manager, which queues up each actionable item (such as the replication of a pod) before it’s carried out. Each metric is tagged with the name of the relevant queue, such as `queue:daemonset` or `queue:node_lifecycle_controller`. The metric `workqueue_queue_duration_seconds` tracks how much time, in aggregate, items in a specific queue have spent awaiting processing, whereas `workqueue_work_duration_seconds` reports how much time it took to actually process those items. If you see a latency increase in the automated actions of your controllers, you can look at the logs for the controller manager pod to gather more details about the cause.
#### Metrics to watch: `scheduler_schedule_attempts_total` and `scheduler_e2e_scheduling_latency_microseconds`

You can track the work of the Kubernetes scheduler by monitoring its overall number of attempts to schedule pods on nodes, as well as the end-to-end latency of carrying out those attempts. The metric `scheduler_schedule_attempts_total` breaks out the scheduler's attempts by result (`error`, `schedulable`, or `unschedulable`), so you can identify problems with matching pods to worker nodes. An increase in `unschedulable` pods indicates that your cluster may lack the resources needed to launch new pods, whereas an attempt that results in an `error` status reflects an internal issue with the scheduler itself.

The end-to-end latency metrics report both how long it takes to select a node for a particular pod, as well as how long it takes to notify the API server of the scheduling decision so it can be applied to the cluster. If you notice a discrepancy between the number of desired and current pods, you can dig into these latency metrics to see if a scheduling issue is behind the lag. 

### Cluster events
Collecting events from your OpenShift cluster, including from the master and worker nodes and from the container engine, is an important part of monitoring a dynamic environment that is constantly adding, removing, or updating pods and nodes. 

Kubernetes events report on *pod* lifecycles and deployments. Tracking pod failures, for example, can point you to misconfigured launch manifests. Correlating events with resource and cluster state metrics can shed light on possible issues, such as insufficient node capacity. For instance, if you are alerted to abnormal behavior in the number of available pods, events can shed light into whether there are scheduling problems with a specific Deployment. If so, you can investigate further.

## Monitor all your layers
As we have seen in this post, tracking the health and performance of an OpenShift cluster requires getting insight into key metrics and events from the different layers of underlying Kubernetes architecture, from the control plane down to the individual pods running your workloads. In [Part 2][part-two] of this series, we will look at how to collect these metrics, whether you're using built-in Kubernetes APIs and utilities or the extended monitoring and logging Operators that OpenShift provides.

[part-two]: /blog/openshift-monitoring-tools