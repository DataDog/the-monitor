# Monitoring in the Kubernetes era
*This post is Part 1 of a 4-part series about Kubernetes monitoring. [Part 2](https://www.datadoghq.com/blog/monitoring-kubernetes-performance-metrics) explores Kubernetes metrics and events you should monitor, [Part 3](https://www.datadoghq.com/blog/how-to-collect-and-graph-kubernetes-metrics) covers the different ways to collect that data, and [Part 4](https://www.datadoghq.com/blog/monitoring-kubernetes-with-datadog/) details how to monitor Kubernetes performance with Datadog.*

## What is Kubernetes?

Docker and other container technologies are currently taking the infrastructure world by storm. Ideal for microservice architectures and environments that scale rapidly or have frequent releases, [Docker has seen a rapid increase in usage](https://www.datadoghq.com/docker-adoption/#1) over the past two years. But containers introduce significant, unprecedented complexity in terms of orchestration. That’s where Kubernetes enters the scene.

### The conductor

[Kubernetes](http://kubernetes.io/) is an open source system, launched by Google, that automates the deployment, management, and scaling of containers running service-oriented applications. Many well-known partners such as Red Hat, CoreOS, VMWare, and Meteor are supporting Kubernetes development, and it is now part of the [Cloud Native Computing Foundation](https://www.cncf.io/).

Just like a conductor directs an orchestra, telling the musicians when to start playing, when to stop, and when to play faster, slower, quieter, or louder, Kubernetes manages your containers—starting, stopping, creating, and destroying them automatically to run your applications at optimal performance. Kubernetes distributes containerized applications across clusters of nodes, and automates their orchestration via:

-   Container scheduling
-   Health checking and recovery
-   Replication to ensure uptime
-   Internal network management for service naming, discovery, and load balancing
-   Resource allocation and management

Kubernetes can deploy your containers wherever they run, whether in AWS, Google Cloud Platform, [Azure](https://www.datadoghq.com/blog/how-to-monitor-microsoft-azure-vms/), or in on-premise or hybrid infrastructure.

Kubernetes has traditionally been used to manage Docker containers, but support for the [rkt](https://github.com/coreos/rkt) container runtime was added with Kubernetes [version 1.3](http://blog.kubernetes.io/2016/07/kubernetes-1.3-bridging-cloud-native-and-enterprise-workloads.html). That release also dramatically improved Kubernetes’s auto-scaling functionality.

Kubernetes has already been adopted by large companies such as eBay, Lithium, Samsung, Jive, and SoundCloud.

### How Kubernetes works behind the scenes

#### Pods

Kubernetes adds a higher level of abstraction to containerized components thanks to [**pods**](http://kubernetes.io/docs/user-guide/pods/), which facilitate resource sharing, communication, application deployment and management, and discovery. Pods are the smallest deployable units that can be created, scheduled, and managed with Kubernetes.

Each pod contains one or several containers on which your applications are running. Containers inside the same pod are always scheduled together, but each container can run a different application. The containers in a given pod run on the same host; share the same IP address, port space, context, and *namespace* (see below); and can also share resources like storage.

#### Nodes, clusters, and namespaces

Pods run on **nodes** (formerly called *minions*), which are virtual or physical machines, grouped into **clusters**. A cluster of nodes has at least one master. It is actually recommended to have more than one master for production environments in order to [ensure high availability](http://kubernetes.io/docs/admin/high-availability/).

And on each node is one [**kubelet**](http://kubernetes.io/docs/admin/kubelet/), which makes sure that all containers described in the [**PodSpec**](http://kubernetes.io/docs/api-reference/v1/definitions/#_v1_podspec) are properly running.

In Kubernetes you can have multiple virtual clusters, called [**namespaces**](http://kubernetes.io/docs/user-guide/namespaces/), backed by the same physical cluster. That way you can spin up only one cluster and use its resources for multiple environments (*staging* and *dev-test,* for example). This can help save time, resources, and cost.

[![kubernetes cluster pods and nodes](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-11-kubernetes/1/kubernetes-pods.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-11-kubernetes/1/kubernetes-pods.png)

#### Replica sets and deployments

Pods are created and destroyed dynamically by [**replica sets**](http://kubernetes.io/docs/user-guide/replicasets/), which are the new generation of [replication controllers](http://kubernetes.io/docs/user-guide/replication-controller/). A replica set preserves service continuity by making sure that the defined number of pods (replicas) are running at all times. If some pods happen to fail or are terminated, the replica set will automatically replace them.

More recently, Kubernetes introduced declarative [**deployments**](http://kubernetes.io/docs/user-guide/deployments/) to manage your replica sets. You simply describe a desired state in a “deployment object”, and the deployment will handle replica sets for you in order to orchestrate pods.

Of course you can also [manually manage pods](http://kubernetes.io/docs/user-guide/pods/multi-container/) without using a replica set or deployments, which can be useful for one-time jobs. But if a pod happens to fail there won’t be anything to detect it and start another one.

#### Services

Since pods are constantly being created and destroyed, their individual IP addresses are unstable and unreliable, and can’t be used for communication between pods. So Kubernetes relies on [**services**](http://kubernetes.io/docs/user-guide/services/), which are simple REST objects that provide a stable level of abstraction across pods and between the different components of your applications. A service (aka microservice) acts as an endpoint for a set of pods by exposing a stable IP address to the external world, which hides the complexity of the dynamic pod scheduling across a cluster. Thanks to this additional abstraction, services can continuously communicate with each other even as the pods that constitute them come and go. It also makes [service discovery](http://kubernetes.io/docs/user-guide/services/#discovering-services) and [load balancing](http://kubernetes.io/docs/user-guide/services/#type-loadbalancer) possible.

Services achieve this by leveraging [labels](http://kubernetes.io/docs/user-guide/labels/#label-selectors), which are arbitrary strings defined on objects in Kubernetes, to dynamically identify where to send incoming requests (see [section about labels](#labels) below).

> Kubernetes is all about abstraction

 

[![kubernetes abstraction](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-11-kubernetes/1/kubernetes-services.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-11-kubernetes/1/kubernetes-services.png)

With the new cross-cluster federated services feature released with Kubernetes 1.3, services can now span multiple clusters that can be located in different (availability) zones, which ensures higher availability.

### Auto-scaling

Kubernetes can automatically scale the number of pods running in a replication controller, deployment, or replica set thanks to the [Horizontal Pod Autoscaler](http://kubernetes.io/docs/user-guide/horizontal-pod-autoscaling/). This process periodically checks the CPU utilization of the pods, then optimizes the number of pods in a deployment, replica set, or replication controller if the average CPU utilization doesn’t match the target you defined. Support for other metrics exists in alpha. Note that the autoscaler requires Heapster (see [Part 3](https://www.datadoghq.com/blog/how-to-collect-and-graph-kubernetes-metrics)) to be deployed in order for auto-scaling to work with these metrics.

## What does Kubernetes mean for your monitoring?

At any scale, monitoring Kubernetes itself as well as the health of your deployed applications and the containers running them is essential to ensure good performance.

Monitoring Kubernetes effectively requires you to rethink and reorient your monitoring strategies, especially if you are used to monitoring traditional hosts such as VMs or physical machines. Just as containers have [completely transformed](https://www.datadoghq.com/blog/the-docker-monitoring-problem/) how we think about running services on virtual machines, Kubernetes has changed the way we interact with containers.

The good news is that with proper monitoring, the abstraction levels inherent to Kubernetes offer you a comprehensive view of your infrastructure, even if your containers are constantly moving. Monitoring Kubernetes is different than traditional monitoring in several ways:

-   Tags and labels become essential
-   You have more components to monitor
-   Your monitoring needs to track applications that are constantly moving
-   Applications may be distributed across multiple cloud providers

### Tags and labels were important; now they’re essential

Using Kubernetes, you have no way to know where your applications are actually running at a given moment. Fortunately labels are here to “tag” your pods and offer a stable view to the external world.

In the pre-container world, [labels and tags were important](https://www.datadoghq.com/blog/the-power-of-tagged-metrics/) when it came to monitoring your infrastructure. They allowed you to group hosts and aggregate their metrics at any level of abstraction. This was extremely useful for tracking performance of dynamic infrastructure and to efficiently investigate issues.

Now with containers—and especially with orchestration frameworks like Kubernetes—labels have become absolutely crucial since they are the only way to identify your pods and their containers.

To make your metrics as useful as possible, you should label your pods so that you can look at any aspect of your containerized infrastructure, such as:

-   Frontend/Backend
-   Application (website, mobile app, database, cache…)
-   Environment (prod, staging, dev…)
-   Team
-   Version

These user-generated Kubernetes labels are essential for monitoring since they are the only way you have to slice and dice your metrics and events across the different layers of your infrastructure.

[![kubernetes labels](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-11-kubernetes/1/kubernetes-labels-monitoring.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-11-kubernetes/1/hkubernetes-labels-monitoring.png)

*Custom labels attached to pods*

 [** TWEET](https://twitter.com/intent/tweet?text=%23Monitoring+in+the+%23Kubernetes+era%3A+%22Labels+and+tags+were+important%3B+now+they+are+essential%22+dtdg.co%2Fk8s-era+by+%40datadoghq)

 

By default, Kubernetes also exposes basic information about pods (**pod\_id**, **pod\_name**, **pod\_namespace**), containers (**container\_base\_image**, **container\_name**), and nodes (**host\_id**, **hostname**), as well as **namespace**, **service name**, and **replication controller name**. Some monitoring tools can ingest these attributes and turn them into tags so you can use them just like other custom Kubernetes labels.

Since v1.2, [Kubernetes also exposes some labels](https://github.com/kubernetes/kubernetes/blob/master/pkg/kubelet/dockertools/labels.go#L37) from Docker. But note that you cannot apply *custom* [Docker labels](https://docs.docker.com/engine/userguide/labels-custom-metadata/) to your images, containers, or daemon when using Kubernetes. You can only apply Kubernetes labels to your pods.

Thanks to these Kubernetes labels at the pod level and Docker labels at the container level, you can get not only a physical picture of your containerized infrastructure but also a logical view. Thus you can examine every layer in your stack (namespace, replication controller, pod, or container) to aggregate your metrics and drill down for investigation.

Being the only way to generate an accessible view of your pods and applications with Kubernetes, labels and tags are now the basis of all your monitoring and alerting strategies. The performance metrics you track won’t be attached to hosts as they were before, but aggregated around labels that you will use to group or filter the pods you are interested in. So make sure to define a logical and easy-to-understand schema for your labels, and create clear labels within your namespaces.

### More components to monitor

In traditional, host-centric infrastructure, you have only two layers to monitor: your applications (caches, databases, load balancers…) and the hosts running them.

Then containers added a [new layer to monitor](https://www.datadoghq.com/blog/how-to-monitor-docker-resource-metrics/) between the host and your applications.

Now Kubernetes, which orchestrates your containers, also needs to be monitored in order to track your infrastructure at a high level. That makes 4 different components that now need to be monitored, each with their specificities and challenges:

-   Your hosts, even if you don’t know which containers and applications they are actually running
-   [Your containers](https://www.datadoghq.com/blog/the-docker-monitoring-problem/)
-   Your containerized applications
-   Kubernetes itself

[![kubernetes monitoring](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-11-kubernetes/1/kubernetes-monitoring.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-11-kubernetes/1/hkubernetes-monitoring.png)

*Evolution of components to monitor
 from traditional to orchestrated containerized infrastructures*

 [** TWEET](https://twitter.com/intent/tweet?text=%23Kubernetes+%2B+%23containers+%3D+more+components+to+monitor+%26+more+complexity+dtdg.co%2Fk8s-era+by+%40datadoghq+https%3A%2F%2Ftwitter.com%2Fdd_docker%2Fstatus%2F793873202720243712%2Fphoto%2F1)

 

Furthermore, Kubernetes introduces a new wrinkle when it comes to monitoring the applications running on your containers…

### Your applications are moving!

Metrics from your containers and pods are an essential part of your monitoring strategy. But you also want to monitor the applications (images) actually running in these containers. With Kubernetes, which automatically schedules your containers, you have very limited control over where they are running. (Delegating such control is the point of Kubernetes!)

*With Kubernetes, your monitoring has to
 follow your moving applications*

Of course you could manually configure the checks collecting the metrics from these applications every time a container is started or restarted, but good luck keeping up with that rate of change.

So what else can you do?

Use a monitoring tool offering [service discovery](https://en.wikipedia.org/wiki/Service_discovery). It will detect any change in the pod and container configuration and automatically adapt the metric collection so you can continuously monitor your containerized infrastructure with no interruption even as it expands, contracts, or shifts across hosts.

> With orchestration tools like Kubernetes, **service discovery** mechanisms become a must-have for monitoring.

 [** TWEET](https://twitter.com/intent/tweet?text=With+%23container+orchestration+tools+like+%23Kubernetes+service+discovery+is+a+must-have+for+%23monitoring.+dtdg.co%2Fkubernetes-era+by+%40datadoghq)

### 

### Adapting to distributed clusters

Since Kubernetes 1.3, [Kubernetes Cluster Federation](https://github.com/kubernetes/kubernetes/blob/8813c955182e3c9daae68a8257365e02cd871c65/release-0.19.0/docs/proposals/federation.md), also called Ubernetes, gives Kubernetes users the ability to distribute their containerized application across several data centers and potentially multiple cloud providers. This allows you to deploy your applications where they will provide the best performance and availability for your users, without having a unique point of failure on a single provider. However, in terms of monitoring, this may complicate things unless you are able to easily aggregate metrics across multiple clouds and/or on-premise infrastructure.

## So where do I begin?

Kubernetes requires you to rethink your approach when it comes to monitoring. But if you know what to observe, how to track it and how to interpret the data, you will be able to keep your containerized infrastructure healthy, performant, and well-orchestrated.

[Part 2](https://www.datadoghq.com/blog/monitoring-kubernetes-performance-metrics) of this series breaks down the data you should collect and monitor when using Kubernetes.
