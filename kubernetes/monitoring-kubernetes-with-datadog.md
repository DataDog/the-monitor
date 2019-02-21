---

*This is the last post in a 4-part series about Kubernetes monitoring. [Part 1](https://www.datadoghq.com/blog/monitoring-kubernetes-era/) discusses how Kubernetes changes your monitoring strategies, [Part 2](https://www.datadoghq.com/blog/monitoring-kubernetes-performance-metrics) explores Kubernetes metrics and events you should monitor, [Part 3](https://www.datadoghq.com/blog/how-to-collect-and-graph-kubernetes-metrics) covers the different ways to collect that data, and this post details how to monitor Kubernetes performance with Datadog.*

If you’ve read [Part 3](https://www.datadoghq.com/blog/how-to-collect-and-graph-kubernetes-metrics) on collecting metrics, you already know that properly monitoring your Dockerized infrastructure orchestrated with Kubernetes requires a tool capable of:



-   Ingesting metrics from all the different layers of your infrastructure, even if your clusters are distributed across multiple data centers or cloud providers
-   Aggregating metrics around Kubernetes labels for better context
-   Tracking your running applications via Autodiscovery as they move across hosts
-   All the advanced graphing and alerting features you need for production-ready infrastructure



Datadog is built to monitor modern infrastructure and offers all these essential functionalities. Our Kubernetes and Docker integrations have been designed to tackle the considerable challenges of monitoring orchestrated containers, as explained in [Part 1](https://www.datadoghq.com/blog/monitoring-kubernetes-era/).

This post will show you how to set up Datadog to automatically collect the key metrics discussed in [Part 2](https://www.datadoghq.com/blog/monitoring-kubernetes-performance-metrics) of this series.

{{< img src="kubernetes-dashboard-small.png" alt="kubernetes dashboard" popup="true" >}}

Full observability for your containerized infrastructure
--------------------------------------------------------

### Easily monitor each layer

After reading the previous parts of this series, you know that it’s essential to monitor the different components of your Kubernetes-orchestrated infrastructure. Datadog integrates with all of them to provide you with a complete picture of cluster health and performance:



-   Datadog’s [**Kubernetes** integration](http://docs.datadoghq.com/integrations/kubernetes/) aggregates metrics, events and labels from Kubernetes
-   The [Docker integration](https://www.datadoghq.com/blog/monitor-docker-datadog/) natively collects all the **container** metrics you need for better accuracy in your monitoring
-   No matter where your Kubernetes clusters are running–AWS, [Google Cloud Platform](https://www.datadoghq.com/blog/monitor-google-compute-engine-performance-with-datadog/), or [Azure](https://www.datadoghq.com/blog/monitor-azure-vms-using-datadog/)– you can monitor the **underlying hosts** of your Kubernetes clusters with Datadog
-   With [{{< translate key="integration_count" >}}+ integrations](https://www.datadoghq.com/product/integrations/) and full support for [custom metrics](http://docs.datadoghq.com/guides/metrics/), Datadog allows you to monitor all the **applications** running on your Kubernetes clusters



### Autodiscovery: check

Thanks to Datadog’s Autodiscovery feature, you can continuously monitor your Dockerized applications without interruption even as they expand, contract, and shift across containers and hosts.

{{< canvas-animation name="service_discovery" width="" height="" >}}

Autodiscovery continuously listens to Docker events. Whenever a container is created or started, the Agent identifies which application is running in the new container, loads your custom monitoring configuration for that application, and starts collecting and reporting metrics. Whenever a container is stopped or destroyed, the Agent understands that too.

Datadog’s Autodiscovery applies Kubernetes labels to application metrics so you can keep monitoring them based on labels, as you do for Kubernetes and Docker data.

To learn more about how Autodiscovery works and how to set it up, check out our [blog post](https://www.datadoghq.com/blog/autodiscovery-docker-monitoring/) and [documentation](http://docs.datadoghq.com/guides/autodiscovery/).

Unleash Datadog
---------------

First, you need to get the Datadog Agent running on your Kubernetes nodes.

### Install the Datadog Agent

The [Datadog Agent](https://docs.datadoghq.com/guides/basic_agent_usage/) is open source software that collects and reports metrics from each of your nodes, so you can view and monitor your entire infrastructure in one place. Installing the Agent usually only takes a few commands.

For Kubernetes, it’s recommended to run the Agent in a container. We have created a Docker image with both the Docker and the Kubernetes integrations enabled.

Thanks to Kubernetes, you can take advantage of [DaemonSets](http://kubernetes.io/docs/admin/daemons/) to automatically deploy the Datadog Agent on all your nodes (or on specific nodes by using [nodeSelectors](http://kubernetes.io/docs/user-guide/node-selection/#nodeselector)). You just need to create a manifest `.yaml` file, pasting in the text you'll find within the Datadog Agent [installation page](https://app.datadoghq.com/account/settings#agent/kubernetes).

Then simply deploy the DaemonSet with the command 

```
kubectl create -f /path/to/the/manifest/.yaml
```

Now that the Agent is running on nodes across your Kubernetes cluster, the next step is to configure it.

### Configure the Agent

The Datadog Agent can be configured by editing the [conf.yaml file](https://github.com/DataDog/integrations-core/blob/master/kubernetes/datadog_checks/kubernetes/data/conf.yaml.example) in the **conf.d** directory. It is necessary so our Kubernetes check can collect metrics from cAdvisor which is running in the Kubelet.

First, override the instances. In the case of a standalone cAdvisor instance, use:

```
instances:
    host: localhost
    port: 4194
    method: http
```

Also add the kubelet port number, such as:

`kubelet_port: 10255`

Then if you want the Agent to collect events from the Kubernetes API, you have to set the `collect_events: True` on **only one Agent** across the entire Kubernetes cluster. Other Agents should have this parameter set to False in order to avoid duplicate events. You also have to specify the namespace from which events will be collected (if not specified, the default namespace will be used):

`namespace: default`

Then you can control if the metrics should be aggregated per container image (`use_histogram: True`) or per container (`use_histogram: False`).

Finally you can add custom tags using:

```
init_config:
    tags:
      - optional_tag1
      - optional_tag2
```

You can also define a whitelist of patterns to collect raw metrics. For example:

```
enabled_rates:
    - cpu.*
    - network.*

enabled_gauges:
    - filesystem.*
```

For additional information, you can refer to the [Datadog Agent Docker container documentation](https://github.com/DataDog/docker-dd-agent).

### Check that the Agent is running

You can make sure the Datadog Agent is running by executing

    kubectl get daemonset

If the agent is correctly deployed, the output should have this form:


```
NAME       DESIRED   CURRENT   NODE-SELECTOR   AGE
dd-agent   3         3         <none>          11h
```

The number of ***desired*** and ***current*** pods should be equal to the number of running nodes in your Kubernetes cluster (you can check this number by running `kubectl get nodes`).

Dive into the metrics!
----------------------

Once the Agent is configured on your Kubernetes nodes, you will have access to our [default Kubernetes screenboard](https://app.datadoghq.com/screen/integration/kubernetes) among your [list of available dashboards](https://app.datadoghq.com/dash/list). It displays the most important metrics presented in [Part 2](https://www.datadoghq.com/blog/monitoring-kubernetes-performance-metrics) and should be a great starting point for monitoring your Kubernetes clusters.

{{< img src="kubernetes-dashboard.png" alt="kubernetes default dashboard in Datadog" caption="Kubernetes default dashboard in Datadog." popup="true" >}}

You can also clone the template dashboard and customize it depending on your needs. You can for example add metrics from your containerized applications to be able to easily correlate them with Kubernetes and Docker metrics.

As you build out your dashboards, don’t forget to [orient your monitoring around Kubernetes labels](https://www.datadoghq.com/blog/monitoring-kubernetes-era/#toc-tags-and-labels-were-important-now-they-re-essential5) even when working with Docker or application metrics.

### Use all the power of Datadog

Datadog offers all the advanced functionalities you need to properly monitor your containerized infrastructure including flexible [alerting](https://www.datadoghq.com/blog/monitoring-101-alerting/), [outlier](https://www.datadoghq.com/blog/introducing-outlier-detection-in-datadog/) and [anomaly](https://www.datadoghq.com/blog/introducing-anomaly-detection-datadog/) detection, dynamic [aggregation using labels and tags](https://www.datadoghq.com/blog/the-power-of-tagged-metrics/), and correlation of metrics and events between systems.

Start monitoring your Kubernetes clusters
-----------------------------------------

In this post, we’ve walked through how to use Datadog to collect, visualize, and alert on metrics from your infrastructure orchestrated by Kubernetes. If you’ve followed along with your Datadog account, you should now have greater visibility into the health and performance of your clusters and be better prepared to address potential issues.

If you don’t yet have a Datadog account, you can start monitoring your Kubernetes clusters with a <a href="#" class="sign-up-trigger">free trial</a>.
___
*Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/kubernetes/monitoring-kubernetes-with-datadog.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues).*
