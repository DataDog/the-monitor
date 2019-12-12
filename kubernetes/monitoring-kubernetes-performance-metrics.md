# Monitoring Kubernetes performance metrics


*This post highlights key Kubernetes metrics, and is Part 2 of a 4-part series about Kubernetes monitoring. [Part 1](https://www.datadoghq.com/blog/monitoring-kubernetes-era/) discusses how Kubernetes changes your monitoring strategies, this post breaks down the key metrics to monitor, [Part 3](https://www.datadoghq.com/blog/how-to-collect-and-graph-kubernetes-metrics) covers the different ways to collect that data, and [Part 4](https://www.datadoghq.com/blog/monitoring-kubernetes-with-datadog/) details how to monitor Kubernetes performance with Datadog.*

As explained in [Part 1](https://www.datadoghq.com/blog/monitoring-kubernetes-era/), using Kubernetes for container orchestration requires a rethinking of your monitoring strategy. But if you use the proper tools, know which metrics to track, and know how to interpret performance data, you will have good visibility into your containerized infrastructure and its orchestration. This part of the series digs into the different Kubernetes metrics you should monitor.

Where Kubernetes metrics come from
-----------------------



### Heapster: Kubernetes’ own metrics collector


We cannot talk about Kubernetes metrics without introducing [Heapster](https://github.com/kubernetes/heapster): it is for now the go-to source for basic resource utilization metrics and events from your Kubernetes clusters. On each node, [cAdvisor](https://github.com/google/cadvisor) collects data about running containers that Heapster then queries through the [kubelet](http://kubernetes.io/docs/admin/kubelet/) of the node. [Part 3](https://www.datadoghq.com/blog/how-to-collect-and-graph-kubernetes-metrics) of this series, which describes the different solutions to collect Kubernetes metrics, will give you more details on how Heapster works and how to configure it for that purpose.

### Heapster vs. native container metrics


It’s important to understand that metrics reported by your container engine (Docker or rkt) can have different values than the equivalent metrics from Kubernetes. As mentioned above, Kubernetes relies on Heapster to report metrics instead of the [cgroup](https://en.wikipedia.org/wiki/Cgroups) file directly. And one of Heapster’s limitations is that it collects Kubernetes metrics at a different frequency (aka “housekeeping interval”) than cAdvisor, which makes the overall metric collection frequency for metrics reported by Heapster tricky to evaluate. This can lead to inaccuracies due to mismatched sampling intervals, especially for metrics where sampling is crucial to the value of the metric, such as counts of CPU time. That’s why you should really consider tracking metrics from your containers instead of from Kubernetes. Throughout this post, we’ll highlight the metrics that you should monitor. Even when you are using Docker metrics, however, you should still aggregate them using the [*labels* from Kubernetes](https://www.datadoghq.com/blog/monitoring-kubernetes-era/#toc-tags-and-labels-were-important-now-they-re-essential5).

Now that we’ve made this clear, let’s dig into the metrics you should monitor.

Key Kubernetes performance metrics to monitor
----------------------------------


Since Kubernetes plays a central role in your infrastructure, it has to be closely monitored. You’ll want to be sure that pods are healthy and correctly deployed, and that resource utilization is optimized.

### Pod deployments


In order to make sure Kubernetes does its job properly, you want to be able to check the health of pod [deployments](http://kubernetes.io/docs/user-guide/deployments/).

During a deployment rollout, Kubernetes first determines the number of desired pods required to run your application(s). Then it deploys the needed pods; the newly created pods are up and counted as ***current***. But ***current*** pods are not necessarily ***available*** immediately for their intended use.



    $ kubectl get deployments

      NAME               DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
      nginx-deployment   3         3         3            3           18s




Indeed for some types of deployments, you might want to enforce a waiting period before making them available. Let's say you have a Jenkins cluster where slaves are pods in Kubernetes. They need some time to start so you want to leave them unavailable during that initiation time and not have them handle any incoming requests. You can specify a delay in your PodSpec using `.spec.minReadySeconds,` which will temporarily prevent your pods from becoming ***available***. Note that [readiness checks](http://kubernetes.io/docs/user-guide/production-pods/#liveness-and-readiness-probes-aka-health-checks) can be a better solution in some cases to make sure your pods are healthy before they receive requests (see [section about health checks](#container-health-checks) below).

During a [rolling update](http://kubernetes.io/docs/user-guide/rolling-updates/), you can also specify in the PodSpec [`.spec.strategy.rollingUpdate.maxUnavailable`](http://kubernetes.io/docs/user-guide/deployments/#max-unavailable) to make sure you always have at least a certain number (or percentage) of pods ***available*** throughout the process. You can also use [`.spec.strategy.rollingUpdate.maxSurge`](http://kubernetes.io/docs/user-guide/deployments/#max-surge) to specify a cap on the number (or percentage) of extra pods that can be created beyond the ***desired*** pods.



<table>
<tbody>
<tr class="odd">
<td><strong>Metric</strong></td>
<td><strong>Metric name in</strong> <a href="https://www.datadoghq.com/blog/how-to-collect-and-graph-kubernetes-metrics/#toc-adding-kube-state-metrics2"><strong>kube-state-metrics</strong></a></td>
<td><strong>Description</strong></td>
<td><a href="https://www.datadoghq.com/blog/monitoring-101-collecting-data/"><strong>Metric type</strong></a></td>
</tr>
<tr class="even">
<td><em>Desired</em> pods</td>
<td>kube_deployment_spec_replicas</td>
<td>Number of pods desired when the deployment started</td>
<td>Other</td>
</tr>
<tr class="odd">
<td><em>Available</em> pods</td>
<td>kube_deployment_status_replicas_available</td>
<td>Number of pods currently available</td>
<td>Other</td>
</tr>
<tr class="even">
<td><em>Unavailable</em> pods</td>
<td>kube_deployment_status_replicas_unavailable</td>
<td>Number of pods currently existing but not available</td>
<td>Other</td>
</tr>
</tbody>
</table>



You should make sure the number of ***available*** pods always matches the ***desired*** number of pods outside of expected deployment transition phases.

### Running pods




<table>
<tbody>
<tr class="odd">
<td><strong>Metric</strong></td>
<td><strong>Description</strong></td>
<td><a href="https://www.datadoghq.com/blog/monitoring-101-collecting-data/"><strong>Metric type</strong></a></td>
</tr>
<tr class="even">
<td><em>Current</em> pods</td>
<td>Number of pods currently running</td>
<td>Resource: Utilization</td>
</tr>
</tbody>
</table>



Keeping an eye on the number of pods currently running (by node or replica set, for example) will give you an overview of the evolution of your dynamic infrastructure.

To understand how the number of running pods impacts resource usage (CPU, memory, etc.) in your cluster, you should correlate this Kubernetes metric with the resource metrics described in the next section.

{{< img src="kubernetes-pods-nodes.png" alt="pods per node" popup="true" size="1x" >}}

### Resource utilization


Monitoring system resources helps ensure that your clusters and applications remain healthy.



<table>
<tbody>
<tr class="odd">
<td><strong>Metric</strong></td>
<td><strong>Metric name in</strong> <a href="https://www.datadoghq.com/blog/how-to-collect-and-graph-kubernetes-metrics/#toc-adding-kube-state-metrics2"><strong>kube-state-metrics</strong></a></td>
<td><strong>Description</strong></td>
<td><a href="https://www.datadoghq.com/blog/monitoring-101-collecting-data/"><strong>Metric type</strong></a></td>
</tr>
<tr class="even">
<td>CPU usage</td>
<td>-</td>
<td>Percentage of allocated CPU currently in use</td>
<td>Resource: Utilization</td>
</tr>
<tr class="odd">
<td>Node CPU capacity</td>
<td>kube_node_status_capacity_cpu_cores</td>
<td>Total CPU capacity of your cluster’s nodes</td>
<td>Resource: Utilization</td>
</tr>
<tr class="even">
<td>Memory usage</td>
<td>-</td>
<td>Percentage of total memory in use</td>
<td>Resource: Utilization</td>
</tr>
<tr class="odd">
<td>Node Memory capacity</td>
<td>kube_node_status_capacity_memory_bytes</td>
<td>Total memory capacity of your cluster’s nodes</td>
<td>Resource: Utilization</td>
</tr>
<tr class="even">
<td>Requests</td>
<td>-</td>
<td>Minimum amount of a given resource required for containers to run (should be summed over a node)</td>
<td>Resource: Utilization</td>
</tr>
<tr class="odd">
<td>Limits</td>
<td>-</td>
<td>Maximum amount of a given resource allowed to containers (should be summed over a node)</td>
<td>Resource: Utilization</td>
</tr>
<tr class="even">
<td>Filesystem usage</td>
<td>-</td>
<td>Volume of disk being used (bytes)</td>
<td>Resource: Utilization</td>
</tr>
<tr class="odd">
<td>Disk I/O</td>
<td>-</td>
<td>Bytes read from or written to disk</td>
<td>Resource: Utilization</td>
</tr>
</tbody>
</table>



#### CPU and memory


It probably goes without saying that when performance issues arise, CPU and memory usage are likely the first resource metrics you will want to review.

However, as explained in the first section of this post, to track memory and CPU usage you should favor the metrics reported by your container technology, such as Docker, rather than the Kubernetes metrics reported by Heapster.

To access your nodes’ CPU and memory capacity, [**kube-state-metrics**](https://www.datadoghq.com/blog/how-to-collect-and-graph-kubernetes-metrics/#toc-adding-kube-state-metrics2) (presented in [Part 3](https://www.datadoghq.com/blog/how-to-collect-and-graph-kubernetes-metrics)) exposes these two metrics: `kube_node_status_capacity_cpu_cores` and `kube_node_status_capacity_memory_bytes` respectively.

**kube-state-metrics** also reports `kube_node_status_allocatable_cpu_cores` and `kube_node_status_allocatable_memory_bytes` tracking respectively the CPU and memory resources of each node that are available for scheduling. Note that these metrics don’t track actual reservation and are not impacted by current scheduling operations. They are equal to the remaining resource available in the node capacity once you remove the amount of resource dedicated to system processes (journald, sshd, kubelet, kube-proxy, etc…).

##### Requests vs. limits


For pod scheduling, Kubernetes allows you to specify how much CPU and memory each container can consume through two types of thresholds:



-   **Request** represents the **minimum** amount of CPU or memory the container needs to run, which needs to be guaranteed by the system.
-   **Limit** is the **maximum** amount of the resource that the container will be allowed to consume. It’s unbounded by default.



##### Beware of the trap


With other technologies, you are probably used to monitoring actual resource consumption and comparing that with your node capacity. With Kubernetes, if the sum of container **limits** on a node is strictly greater than the sum of **requests** (minimum resources required), the node can be *oversubscribed* and containers might use more resources than they actually need, which is fine. Even if they use 100 percent of the available CPU resources on a node, for example, Kubernetes can still make room to schedule another pod on the node. Kubernetes would simply lower the CPU available to existing pods to free up resources for the new one, as long as all containers have enough resources to meet their **request**. That’s why monitoring the sum of requests on the node and making sure it never exceeds your node’s capacity is much more important than monitoring simple CPU or memory usage. If you don’t have enough capacity to meet the minimum resource requirements of all your containers, you should scale up your nodes’ capacity or add more nodes to distribute the workload.

{{< img src="kubernetes-resource-metrics.png" alt="Kubernetes memory and CPU per host" popup="true" >}}

Having some oversubscription on your nodes can be good in many cases since it can help reduce the number of nodes in your Kubernetes cluster. You can tune the request/limit ratio by monitoring it over time and tracking how it impacts your container resource usage.

Note that since version 1.3 Kubernetes offers auto-scaling capabilities for Google Compute Engine and Google Container Engine ([AWS support should come soon](http://blog.kubernetes.io/2016/07/autoscaling-in-kubernetes.html)). So on those platforms Kubernetes can now adjust the number pods in a deployment, replica set, or replication controller based on CPU utilization (support for other auto-scaling triggers is in alpha).

##### Container resource metrics


As explained in the [section about container metrics](#monitoring-containers-using-native-metrics), some statistics reported by Docker should be also monitored as they provide deeper (and more accurate) insights. The CPU throttling metric is a great example, as it represents the number of times a container hit its specified **limit**.

#### Disk usage and I/O


The percentage of disk in use is generally more useful than the *volume* of disk usage, since the thresholds of concern won’t depend on the size of your clusters. You should graph its evolution over time and trigger an alert if it exceeds 80% for example.

Graphing the number of bytes read from or written to disk provides critical context for higher-level metrics. For example, you can quickly check whether a latency spike is due to increased I/O activity.

{{< img src="kubernetes-disk-io.png" alt="Kubernetes disk I/O" popup="true" >}}

#### Network


Just as with ordinary hosts, you should monitor network metrics from Kubernetes pods and containers.



<table>
<tbody>
<tr class="odd">
<td><strong>Metric</strong></td>
<td><strong>Description</strong></td>
<td><a href="https://www.datadoghq.com/blog/monitoring-101-collecting-data/"><strong>Metric type</strong></a></td>
</tr>
<tr class="even">
<td>Network in</td>
<td>Bytes per second received through network</td>
<td>Resource: Utilization</td>
</tr>
<tr class="odd">
<td>Network out</td>
<td>Bytes per second sent through network</td>
<td>Resource: Utilization</td>
</tr>
<tr class="even">
<td>Network errors</td>
<td>Number of network errors per second</td>
<td>Resource: Error</td>
</tr>
</tbody>
</table>



Network metrics can shed light on traffic load. You should investigate if you see an increasing number of network errors per second, which could indicate a low-level issue or a networking misconfiguration.



### Container health checks


In addition to standard resource metrics, Kubernetes also provides configurable health checks. You can configure, via the PodSpec, [checks](http://kubernetes.io/docs/user-guide/production-pods/#liveness-and-readiness-probes-aka-health-checks) to detect:



-   When running applications enter a broken state (liveness probe fails), in which case the kubelet will kill the container.
-   When applications are temporarily unable to properly address requests (readiness probe fails), in which case the Kubernetes endpoint controller will remove the pod’s IP address from the endpoints of all services that match the pod, so that no traffic is sent to the affected containers.



The kubelet can run diagnostic liveness and readiness probes against containers through an HTTP check (the most common choice), an exec check, or a TCP check. The Kubernetes documentation provides [more details about container probes](http://kubernetes.io/docs/user-guide/pod-states/#container-probes) and tips on [when you should use them](http://kubernetes.io/docs/user-guide/pod-states/#when-should-i-use-liveness-or-readiness-probes).



### Monitoring containers using native metrics


As we said, container metrics should be usually preferred to Kubernetes metrics. Containers can rightly be seen as mini-hosts. Just like virtual machines, they run on behalf of resident software, which consumes CPU, memory, I/O, and network resources.

If you are using Docker, check out [our Docker monitoring guide](https://www.datadoghq.com/blog/how-to-monitor-docker-resource-metrics/), which discusses all the resource metrics available from Docker that you should collect and monitor.

Using Docker in the framework provided by Kubernetes labels will give you insights about your containers’ health and performance. Kubernetes labels are already applied to Docker metrics. You could track for example the number of running containers by pod, or the most RAM-intensive pods by graphing the [RSS non-cache memory](https://www.datadoghq.com/blog/how-to-monitor-docker-resource-metrics/#toc-memory3) broken down by *pod name*.

{{< img src="containers-per-pod.png" alt="containers per pod" popup="true" size="1x" >}}

### Application-specific metrics


In order to properly monitor your containerized infrastructure, you should collect Kubernetes metrics along with Docker container resource metrics, and correlate them with the health and performance of the different [applications running on top of them](https://www.datadoghq.com/docker-adoption/#6). Each image comes with its specificities, and the types of metrics you should track and alert on will vary from one to another. However throughput, latency, and errors are usually the most important metrics.

We have published monitoring guides to help you identify key metrics for many popular technologies, including [NGINX](https://www.datadoghq.com/blog/how-to-monitor-nginx/), [Redis](https://www.datadoghq.com/blog/how-to-monitor-redis-performance-metrics/), [MongoDB](https://www.datadoghq.com/blog/monitoring-mongodb-performance-metrics-wiredtiger/), [MySQL](https://www.datadoghq.com/blog/monitoring-mysql-performance-metrics/), [Elasticsearch](https://www.datadoghq.com/blog/monitor-elasticsearch-performance-metrics/), and [Varnish](https://www.datadoghq.com/blog/top-varnish-performance-metrics/).

Heapster is not designed to collect by default metrics from the applications running in your containers. If you want deeper context than just system metrics, you have to instrument your applications in order to collect metrics from them as well.

Since Kubernetes 1.2 a new feature (still in Alpha) allows cAdvisor to [collect custom metrics](https://github.com/google/cadvisor/blob/master/docs/application_metrics.md) from applications running in containers, if these metrics are exposed in the [Prometheus format](https://prometheus.io/docs/instrumenting/exposition_formats/) natively, which is the case for only [a few applications](https://prometheus.io/docs/instrumenting/exporters/#directly-instrumented-software) today. These custom metrics can be [used to trigger horizontal pod auto-scaling](http://kubernetes.io/docs/user-guide/horizontal-pod-autoscaling/#support-for-custom-metrics) (HPA) when a metric exceeds a specified threshold. Note that Heapster re-exposes these custom metrics through its [Model API](https://github.com/kubernetes/heapster/blob/master/docs/model.md) which is not an official Kubernetes API.

Correlate Kubernetes metrics with events
---------------------


Collecting events from Docker and Kubernetes allows you to see how pod creation, destruction, starting, or stopping impacts the performance of your infrastructure (and also the inverse).

While Docker events trace container lifecycles, Kubernetes events report on *pod* lifecycles and deployments. Tracking pods failures for example can indicate a misconfiguration or resource saturation. That’s why you should correlate events with Kubernetes metrics for easier investigations.

### Pod scheduling events


You can make sure pod scheduling works properly by tracking Kubernetes events. If scheduling fails repeatedly, you should investigate. Insufficient resources in your cluster such as CPU or memory can be the root cause of scheduling issues, in which case you should consider [adding more nodes](http://kubernetes.io/docs/admin/cluster-management/#resizing-a-cluster) to the cluster, or [deleting](http://kubernetes.io/docs/user-guide/pods/single-container/#deleting-a-pod) unused pods to make room for [***pending***](http://kubernetes.io/docs/user-guide/pod-states/#pod-phase) ones.

Node ports can also be a cause of scheduling contention. If [*NodePort*](http://kubernetes.io/docs/user-guide/services/#type-nodeport) is used to assign specific port numbers, then Kubernetes won’t be able to schedule a pod to a node where that port is already taken. This can lead to scheduling issues due to:



-   Poor configuration, for example if two conflicting pods try to claim the same port.
-   Resource saturation, for example if the *NodePort* is set but the [replica set](http://kubernetes.io/docs/user-guide/replicasets/) requires more pod replicas than there are nodes. In that case you should scale up the number of nodes or use a Kubernetes [service](http://kubernetes.io/docs/user-guide/services/) so multiple pods behind it can live in one node.



Alerting properly
-----------------


Since your pods are constantly moving, alerts on the metrics they report (CPU, memory, I/O, network…) have to follow. That’s why they should be set up using what remains stable as pods come and go: custom labels, service names, and names of replication controllers or replica sets.

A concrete use case
-------------------


As discussed in Part 1, monitoring orchestrated, containerized infrastructure means collecting metrics from every layer of your stack: from Docker and Kubernetes as well as from your hosts and containerized applications. Let’s see how the different data from all the components of your infrastructure can be used to investigate a performance issue.

Let’s say we are running [NGINX](https://www.datadoghq.com/blog/how-to-monitor-nginx/) for our web app in Docker containers, which are orchestrated by Kubernetes.

#### 1. Application metric showing performance issue


We receive an [alert](https://www.datadoghq.com/blog/monitoring-101-alerting/) triggered after the number of NGINX 5xx errors suddenly skyrocketed over a set threshold.

{{< img src="nginx-errors.png" alt="NGINX 5xx errors" popup="true" >}}

#### 2. Corresponding Kubernetes labels and events


If we look at which pods our web app was running on, we can see that the Kubernetes label attached to them, which defines the replication controller involved, is ***rc-nginx***. And when looking at Kubernetes events, a [rolling update deployment](http://kubernetes.io/docs/user-guide/deployments/#rolling-update-deployment) happened on those pods exactly at the moment that the web app started returning 5xx errors.

Let’s investigate the containers impacted by this rolling update to understand what happened.

#### 3. What happened at the container level


The first place to look is usually resource metrics. Remember that Docker metrics should be preferred to Kubernetes metrics for time-sampled data. So let’s graph the CPU utilization by Docker containers, broken down by pod (or container) and filtered to retain only the pods with the label ***rc-nginx***.

{{< img src="cpu-pods.png" alt="CPU per pod" popup="true" >}}

Interesting! It looks like CPU usage in some pods drastically increased at the moment that the 5xx error peaked. Would it be possible that the underlying hosts running this pod replica saturated their CPU capacity?

#### 4. Host metrics to confirm the hypothesis


By graphing the CPU usage broken down by host, we can see that indeed three hosts maxed out their CPU at that moment.

{{< img src="hosts-full-cpu.png" alt="CPU per host" popup="true" >}}

#### Resolving the issue and postmortem


A short-term solution can be to roll back the update to our web app code if we think that an update led to this issue. Scaling up our hosts’ CPU capacity can also help support higher resource consumption.

If appropriate, we could also make use of [the underlying mechanism in Kubernetes that imposes restrictions](http://kubernetes.io/docs/admin/limitrange/) on the resources (CPU and memory) a single pod can consume. In this case, we should consider lowering the CPU limit for a given pod.

Here we have combined data from across our container infrastructure to find the root cause of a Kubernetes performance issue:



-   Application metrics for alerting
-   Kubernetes labels to identify affected pods
-   Kubernetes events to look for potential causes
-   Docker metrics aggregated by Kubernetes labels to investigate hypothesized cause
-   Host-level metrics to confirm resource constraint



{{< img src="k8s-use-case.png" alt="Kubernetes monitoring use case" popup="true" caption="Using data from across your orchestrated containerized infrastructure to find the root cause of a performance issue">}}


<div class="text-center">


<a class="button-tweet button-royal-blue" href="https://twitter.com/intent/tweet?text=Combine+data+from+%23Kubernetes%2C+%23Docker%2C+and+hosts+to+solve+performance+issues+http%3A%2F%2Fdtdg.co%2Fk8s-monitoring+by+%40datadoghq+https%3A%2F%2Ftwitter.com%2Fdd_docker%2Fstatus%2F796078373718159364%2Fphoto%2F1" target="_blank"><i class="icon icon-twitter"></i> TWEET</a>

</div>


Watching the conductor and the orchestra
----------------------------------------


Kubernetes makes working with containers much easier. However it requires you to completely rethink how you monitor your infrastructure and applications. For example, having a smart labeling strategy is now essential, as is smartly combining data from Kubernetes, your container technology, and your applications for full observability.

The methods and tools used to collect resource metrics from Kubernetes are different from the commands used on a traditional host. Part 3 of this series covers how to collect the Kubernetes metrics you need to properly monitor your containerized apps and infrastructure, as well as their orchestration. [Read on…](https://www.datadoghq.com/blog/how-to-collect-and-graph-kubernetes-metrics)

Acknowledgment
--------------


Many thanks to Lachlan Evenson from [Deis](http://deis.io/), Charles Butler from [Canonical](http://www.canonical.com/), Mike Kaplinsky from [Ladder](https://www.ladderlife.com/), Rudi Chiarito from [Clarifai](https://www.clarifai.com/), and the Kubernetes Slack communities for reviewing this publication and suggesting improvements.

___
*Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/kubernetes/monitoring-kubernetes-performance-metrics.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues).*

