In [Part 1][part-one], we explored three primary types of metrics for monitoring your Red Hat OpenShift environment:

- [Cluster state metrics](/blog/key-metrics-for-openshift-monitoring/#cluster-state-metrics)
- [Container and node resource and quota metrics](/blog/key-metrics-for-openshift-monitoring/#resource-metrics)
- Work metrics from the [control plane](/blog/key-metrics-for-openshift-monitoring/#control-plane-metrics)

We also looked at how logs and events from both the control plane and your pods provide valuable insights into how your cluster is performing.

In this post, we'll look at how you can use Datadog to get end-to-end visibility into your entire OpenShift environment. Datadog enables you to collect and analyze metrics, logs, performance data from your applications, and more, using one unified platform. We will cover how to:

- [Deploy](#the-datadog-agent) the Datadog Cluster Agent and node-based Agents to collect all of the metrics we covered in [Part 1][part-one]
- Leverage [Autodiscovery](#autodiscover-your-services) to monitor dynamic, containerized workloads even as they move across your cluster
- [Set up log collection and APM](#go-deeper-with-logs-traces-and-more) to get deeper insights into your OpenShift cluster and applications

Before getting started, it's important to understand what level of access the Datadog Agent needs to collect information from your cluster, as that affects how you deploy Datadog.

## Choose the right security level

OpenShift uses two primary mechanisms for restricting cluster access: role-based access control (RBAC) and security context constraints (SCC). The former controls permissions for users and services based on defined roles. The latter restricts what privileges pods have.

The Datadog Agent can collect information from several different sources in your OpenShift cluster, including the Kubernetes API server, each node's kubelet process, and the hosts themselves. Datadog provides three general levels of data collection based on what permissions are required:

- [Restricted](#restricted) for basic metric collection
- [Host network](#host-network) for APM, container logs, and custom metrics
- [Custom](#custom) for full Datadog monitoring

### Restricted
Restricted access is essentially allowing Datadog to access only the API server and kubelet processes. With this level of access you can collect most of the key metrics and cluster events we covered in [Part 1][part-one]. Deploying Datadog with restricted access requires providing the Agent with the needed [role-based access control (RBAC) permissions](https://docs.datadoghq.com/agent/kubernetes/?tab=daemonset#installation). Creating these permissions will be part of [configuring the Datadog Agent](#create-the-datadog-values-chart) below.

### Host network
OpenShift's default SCC configuration does not allow pods to directly access their host nodes' ports. The Datadog Agent needs access to host ports in order to collect custom metrics (via the [DogStatsD protocol](https://docs.datadoghq.com/developers/dogstatsd/?tab=kubernetes)), APM traces, and logs.

In order to allow the Agent pods to access their hosts' ports, you can modify the `hostnetwork` or `hostaccess` option in their SCC configuration to grant the proper permissions. We will do this when we [configure the Datadog Agent](#create-the-datadog-values-chart).

### Custom
You can collect even more information about your OpenShift environment by applying custom SCC to the Datadog Agent. This means, in addition to providing the Datadog Agent pods access to host ports as we did [above](#host-network), also granting them [super privileged](https://developers.redhat.com/blog/2014/11/06/introducing-a-super-privileged-container-concept/) status (`spc_t`). This allows them to collect system information at the container and process levels. 

In order to use the Datadog Agent's full feature set, first create a service account for the node-based Agents. This is part of our [deployment steps below](#create-the-datadog-values-chart). Then, include the service account in the `users` section of the SCC manifest [here](https://github.com/DataDog/datadog-agent/blob/master/Dockerfiles/manifests/openshift/scc.yaml). Finally, apply the manifest:

{{< code-snippet lang="bash" wrap="false"  >}}
oc apply -f path/to/scc.yaml
{{< /code-snippet >}}

## The Datadog Agent
The [Datadog Agent](https://docs.datadoghq.com/agent/) is open source software that collects and reports metrics, distributed traces, and logs from each of your nodes, so you can view and monitor your entire infrastructure in one place. In addition to collecting telemetry data from Kubernetes, Docker, CRI-O, and other infrastructure technologies, the Agent automatically collects and reports resource metrics (such as CPU, memory, and network traffic) from your nodes, regardless of whether they're running in the cloud or on-prem infrastructure. 

Datadog's [Agent deployment instructions](https://docs.datadoghq.com/agent/kubernetes/?tab=daemonset) provide a full manifest for deploying the containerized node-based Agent as a DaemonSet. If you wish to get started quickly for experimentation purposes, you can follow those directions to roll out the Agent across your cluster. In this guide, however, we'll go one step further to show you how to not only install the Agent on all your nodes but also deploy the specialized [Datadog Cluster Agent](https://docs.datadoghq.com/agent/cluster_agent/).

### The Datadog Cluster Agent
The Datadog Cluster Agent provides several additional benefits to using the node-based DaemonSet alone for large-scale, production use cases. For instance, the Cluster Agent:

- reduces the load on the Kubernetes API server for gathering cluster-level data by serving as a proxy between the API server and the node-based Agents 
- provides additional security by reducing the permissions needed for the node-based Agents
- enables [auto-scaling of Kubernetes workloads](https://docs.datadoghq.com/agent/cluster_agent/external_metrics/) using any metric collected by Datadog

{{< img src="openshift-monitoring-datadog-cluster-agent.png" popup="true" >}}

Regardless of whether you choose to use the Cluster Agent or just the node-based DaemonSet, there are several methods for installing the Datadog Agent. In this article, we will go over how to use the [Helm package manager](https://helm.sh/) to install the node-based Datadog Agent along with the [Datadog Cluster Agent](#the-datadog-cluster-agent) to provide comprehensive, resource-efficient Kubernetes monitoring.

### Using Helm
Helm is a package manager for Kubernetes applications. It uses **charts** to define, configure, and install applications. Charts consist of different types of files. The two types that we'll focus most on here are:

- **templates**, which provide the skeleton of a Kubernetes manifest with keys and default values or template variables that will be dynamically populated
- **values**, which provide the data to be applied to the template files

If you do not have Helm, you can [get started](https://helm.sh/docs/intro/quickstart/) by installing it and gaining access to the Helm Chart Repository, where the Datadog Agent and Cluster Agent charts are available. Note that the steps below assume that you are running Helm 3.x. If you are using an older version, see our [documentation](https://docs.datadoghq.com/agent/kubernetes/helm/) for instructions.

We'll need to create a Helm values chart to configure the Cluster Agent and node-based Agents for an OpenShift environment. But first, the Cluster Agent and node-based Agents need to be able to communicate securely with each other.

### Secure Agent communication
In order to enable secure communication between the Cluster Agent and node-based Agents, you can provide a security token to both. Generate a token by running the following command:

{{< code-snippet lang="bash" wrap="false"  >}}
echo -n '<32_CHARACTER_LONG_STRING>' | base64
{{< /code-snippet >}}

Save the resulting token to insert into the values chart.

### Create the Datadog values chart
In order to provide both the Cluster Agent and node-based Agent with the necessary configuration, create a file, **datadog-values.yaml**. You can read more about required parameters and configuration options [here](https://github.com/helm/charts/tree/master/stable/datadog#all-configuration-options). But below, we'll point out several things to include in the values file to make sure that we can properly monitor key data from an OpenShift cluster:

{{< code-snippet lang="yaml" filename="datadog-values.yaml" wrap="false"  >}}
datadog:
  apiKey: <API_KEY>
  criSocketPath: /var/run/crio/crio.sock
  collectEvents: true
  clusterChecks:
    enabled: true
  confd:
    crio.yaml: |-
      init_config:
      instances:
      - prometheus_url: http://localhost:9537/metrics
{{< /code-snippet >}}

The `datadog` section of the values file includes general configuration options for Datadog. This includes, for example, your [API key](https://app.datadoghq.com/account/settings#api). In this example we have also instructed Datadog to look for the CRI socket by passing the `criSocketPath` parameter and [enabling the integration](https://docs.datadoghq.com/agent/kubernetes/helm/?tab=helmv3#enabling-integrations-with-helm). This is necessary for the Agent to collect container metrics for OpenShift clusters using versions 4.x or 3.11 with the CRI-O container runtime instead of Docker, which is the default. If you are using Docker, you can leave these parameters out.

The `collectEvents: true` parameter enables Datadog to collect cluster-level events from the Kubernetes API server. They will appear both in your Datadog [event stream](https://app.datadoghq.com/event/stream) and as logs in the [Log Explorer](https://app.datadoghq.com/logs).

{{< code-snippet lang="yaml" filename="datadog-values.yaml" wrap="false"  >}}
clusterAgent:
  enabled: true
  token: "<32_CHAR_TOKEN>"
  rbac:
    create: true
{{< /code-snippet >}}

The `clusterAgent` section of the values file configures the Datadog Cluster Agent. Aside from enabling it, we have provided the token we generated in the [previous step](#secure-agent-communication) to secure communication between the Cluster Agent and the node-based Agents.

When set to `create:true`, the `rbac` parameter will automatically create a [ClusterRole and ClusterRoleBinding](https://docs.openshift.com/container-platform/4.2/authentication/using-rbac.html#creating-cluster-role_using-rbac) and [service account](https://docs.openshift.com/container-platform/4.2/authentication/understanding-and-creating-service-accounts.html) to grant the Cluster Agent the proper RBAC permissions to query the API server. You can see what permissions are needed [here](https://raw.githubusercontent.com/DataDog/datadog-agent/master/Dockerfiles/manifests/cluster-agent/rbac/rbac-cluster-agent.yaml).

{{< code-snippet lang="yaml" filename="datadog-values.yaml" wrap="false"  >}}
agents:
  enabled: true
  rbac:
    create: true
  containers:
    agent:
      env:
      - name: "DD_KUBELET_TLS_VERIFY"
        value: "false"  
  useHostNetwork: true
{{< /code-snippet >}}

The `agents` section configures the node-based Agents. Like the Cluster Agent, we are creating the necessary [RBAC permissions](https://raw.githubusercontent.com/DataDog/datadog-agent/master/Dockerfiles/manifests/cluster-agent/rbac/rbac-agent.yaml) for the Agent to poll the kubelet for data. We are also passing in an environment variable: `DD_KUBELET_TLS_VERIFY`. Setting it to false lets the Agent discover the kubelet's URL.

If your OpenShift cluster is hosted on a cloud provider, the `useHostNetwork: true` parameter is necessary for the Agent to collect host-level metadata. Note that this also provides the Agent with [access to host-level ports](#host-network), letting you collect traces, logs, and custom metrics via DogStatsD from your containerized workloads. Alternatively, you can enable the [`hostaccess` SCC](https://docs.openshift.com/container-platform/4.2/authentication/managing-security-context-constraints.html). If you deployed the [custom SCC](#custom), you have already taken care of this.

{{< code-snippet lang="yaml" filename="datadog-values.yaml" wrap="false"  >}}
kubeStateMetrics:
  enabled: true
kube-state-metrics:
  rbac:
    create: true
  serviceAccount:
    create: true
{{< /code-snippet >}}

Note that we are including a parameter `kubeStateMetrics` and setting it to `enabled: true`. This will deploy the kube-state-metrics service. Even if you have the OpenShift Monitoring Stack deployed, which by default includes kube-state-metrics, you should still set this parameter to `true`. This is because the OpenShift kube-state-metrics container uses a different image than the [standard service](https://quay.io/repository/coreos/kube-state-metrics?tag=latest&tab=tags), so the Agent will not [automatically find](https://docs.datadoghq.com/agent/autodiscovery/auto_conf/) containers running it.

The `kube-state-metrics` section of the values file creates the necessary RBAC permissions for the service. You can see more information about these and the other required parameters [here](https://github.com/helm/charts/blob/master/stable/datadog/values.yaml) before deploying Datadog.

### Install the Datadog chart
Once you have your **datadog-values.yaml** file ready, you can use Helm to install Datadog to your OpenShift cluster by running:

{{< code-snippet lang="bash" wrap="false"  >}}
helm install -f path/to/datadog-values.yaml <AGENT_SERVICE_NAME> stable/datadog
{{< /code-snippet >}}

Replace `<AGENT_SERVICE_NAME>` with an appropriate name for the Datadog resources (e.g., `datadog-agent`). You should see output like the following:

{{< code-snippet lang="bash" wrap="false"  >}}
NAME: datadog-agent
LAST DEPLOYED: Wed Mar 11 11:51:44 2020
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
DataDog agents are spinning up on each node in your cluster. After a few
minutes, you should see your agents starting in your event stream:
    https://app.datadoghq.com/event/stream
{{< /code-snippet >}}

#### Verify installation
Verify that the Agent deployed successfully by running the following:

{{< code-snippet lang="bash" wrap="false"  >}}
oc get pods | grep datadog

datadog-agent-cluster-agent-68b5ff9d5d-mddgt        1/1     Running   0          123m
datadog-agent-kube-state-metrics-588b774bdd-j5ftg   1/1     Running   0          123m
datadog-agent-l6dj2                                 1/1     Running   0          123m
datadog-agent-kfvpc                                 1/1     Running   0          123m
datadog-agent-xvss5                                 1/1     Running   0          123m
{{< /code-snippet >}}

The output shows that the Cluster Agent pod and three node-based Agent pods are running. The number of node-based Agent pods should be the same as the number of nodes in your cluster. We can also see the kube-state-metrics pod.

In order to check that the node-based Agents are successfully communicating with the Cluster Agent, select the name of one of your node-based Agent pods and run:

{{< code-snippet lang="bash" wrap="false"  >}}
oc exec datadog-agent-l6dj2 agent status
{{< /code-snippet >}}

At the bottom of the output, you should see something like:

{{< code-snippet lang="bash" wrap="false"  >}}
=====================
Datadog Cluster Agent
=====================

  - Datadog Cluster Agent endpoint detected: https://172.30.200.227:5005
  Successfully connected to the Datadog Cluster Agent.
{{< /code-snippet >}}

With Datadog and kube-state-metrics deployed, metrics and events from your OpenShift cluster should now be streaming into your Datadog account.

## Autodiscover your services
With the Datadog Agent successfully deployed, resource metrics and events from your cluster should be streaming into Datadog. In addition to metrics from your nodes' kubelets, data from services like kube-state-metrics and the Kubernetes API server automatically appear thanks to the Datadog Agent's Autodiscovery feature, which listens for container creation events, detects when certain services are running on those containers, and starts collecting data from supported services. 

Since kube-state-metrics and the API server are among the [integrations automatically enabled by Autodiscovery](https://docs.datadoghq.com/agent/autodiscovery/auto_conf/), there's nothing more you need to do to start collecting your cluster state metrics in Datadog. 
In the case of OpenShift, this gives you out-of-the-box access to cluster state information, including metrics that OpenShift exposes through the Kubernetes API that track OpenShift-specific objects like [cluster resource quotas](/blog/key-metrics-for-openshift-monitoring/#metrics-to-alert-on-resource-and-object-quota-used-vs-resource-and-object-quota-limits). (You can read more about what metrics are available in our [documentation](https://docs.datadoghq.com/integrations/openshift/#data-collected).)

Auto-configured services include common infrastructure technologies like Apache (httpd), Redis, and Apache Tomcat. When the Datadog Agent detects those containers running anywhere in the cluster, it will attempt to apply a standard configuration template to the containerized application and begin collecting monitoring data.

{{< img src="openshift-monitoring-datadog-autodiscovery.png" border="true" popup="true" caption="Datadog's Autodiscovery feature watches your containers and detects what services they are running." >}}

For services in your cluster that require user-provided configuration details (such as authentication credentials for a database), you can use Kubernetes pod annotations to specify which Datadog check to apply to that pod, as well as any details necessary to configure the monitoring check. For example, to configure the Datadog Agent to collect metrics from your MySQL database using an authorized `datadog` user, you would add the following pod annotations to your MySQL pod manifest:

{{< code-snippet lang="yaml" wrap="false" >}}
annotations:
  ad.datadoghq.com/mysql.check_names: '["mysql"]'
  ad.datadoghq.com/mysql.init_configs: '[{}]'
  ad.datadoghq.com/mysql.instances: '[{"server": "%%host%%", "user": "datadog","pass": "<UNIQUE_PASSWORD>"}]'
{{< /code-snippet >}}

Those annotations instruct Datadog to apply the MySQL monitoring check to any `mysql` pods, and to connect to the MySQL instances using a dynamically provided host IP address and authentication credentials for the `datadog` user. 

## Get visibility into your control plane
Datadog integrates with Kubernetes components including the API server, controller manager, scheduler, and etcd. This means that, once enabled, in addition to key metrics from your nodes and pods you can also monitor the [health and workload of your cluster's control plane](/blog/key-metrics-for-openshift-monitoring/#control-plane-metrics). Datadog provides out-of-the-box dashboards for several of these components, including the scheduler, shown below.

{{< img src="openshift-monitoring-datadog-dashboard.png" border="true" popup="true" caption="Datadog's out-of-the-box Kubernetes scheduler dashboard." >}}

See our documentation on steps to enable these integrations and start collecting metrics from your cluster's [API server](https://docs.datadoghq.com/integrations/kube_apiserver_metrics/), [controller manager](https://docs.datadoghq.com/integrations/kube_controller_manager/), [scheduler](https://docs.datadoghq.com/integrations/kube_scheduler/), and [etcd](https://docs.datadoghq.com/integrations/etcd/).

_Note that if you are running OpenShift in a managed cloud environment, the control plane is managed by the cloud provider, and you may not have access to metrics for all of these components._

## Monitor a changing environment with tags
Datadog automatically imports metadata from OpenShift, Kubernetes, cloud services, and other technologies, and creates tags that you can use to sort, filter, and aggregate your data. Tags (and their Kubernetes equivalent, [labels](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/)) are essential for monitoring dynamic infrastructure, where hostnames, IP addresses, and other identifiers are constantly in flux. With Datadog, you can filter and view your resources by tags, including ones that Datadog automatically imports from your environment such as Deployment, service, or container image. Datadog also automatically pulls in tags from your cloud provider, so you can view your nodes or containers by availability zone, instance type, and so on.

In the `datadog` section of your [values chart](#create-the-datadog-values-chart), you can add custom tags with the `DD_TAGS` environment variable, followed by key:value pairs. For example, you could apply the following tags to your node-based Agents to indicate the organizational name of the Kubernetes cluster and the team responsible for it:

{{< code-snippet lang="yaml" filename="datadog-values.yaml" wrap="false" >}}
datadog:
 [...]
 - cluster-name:melange
 - team:core-platform
{{< /code-snippet >}}

You can also use the `podLabelsAsTags` parameter to import Kubernetes [pod labels as tags](https://docs.datadoghq.com/agent/autodiscovery/tag/?tab=containerizedagent#extract-pod-labels-as-tags), which captures any pod-level metadata that you defined in your manifests as tags. This ensures that you can use that metadata to filter and aggregate your telemetry data in Datadog. 

## Go deeper with logs, traces, and more
We've [seen](#autodiscover-your-services) how the Datadog Agent automatically collects metrics from your nodes and containers. To get even more insight into your cluster, you can also configure Datadog to collect logs and distributed traces from the applications in your cluster. Note that to do this, your pods must have access to the host port of the node they run on. We handled this earlier by setting the `agents.hostNetwork` parameter to `true` in the [Helm values chart for the Datadog Agent](#create-the-datadog-values-chart).

### Collect and analyze cluster logs
Datadog can automatically collect logs from Kubernetes, Docker, and many [other technologies](https://docs.datadoghq.com/integrations/#cat-log-collection) you may be running on your cluster. Logs can be invaluable for troubleshooting problems, identifying errors, and giving you greater insight into the behavior of your infrastructure and applications.

In order to enable log collection from your containers, add the following variables to the Datadog Helm values chart you created earlier:

{{< code-snippet lang="yaml" filename="datadog-values.yaml" wrap="false" >}}
datadog:
  [...]
  logsEnabled: true
  containerCollectAll: true
{{< /code-snippet >}}

You can update your Agent with these changes with the following command:

{{< code-snippet lang="bash" wrap="false" >}}
helm upgrade -f path/to/datadog-values.yaml <AGENT_SERVICE_NAME> stable/datadog
{{< /code-snippet >}}

With log collection enabled, you should start seeing logs flowing into the [Log Explorer](https://app.datadoghq.com/logs) in Datadog. These logs include those emitted by pods running OpenShift's Operators. Use [tags](#monitor-a-changing-environment-with-tags) to filter your logs by project, node, Deployment, and more to drill down to the specific logs you need.

#### Bring order to your logs
Datadog automatically [ingests](/blog/logging-without-limits), processes, and parses all of the logs from your cluster for [analysis and visualization](/blog/log-analytics-dashboards). To get the most value from your logs, ensure that they have a `source` tag and a `service` tag attached. For logs coming from one of Datadog's [log integrations](https://docs.datadoghq.com/integrations/#cat-log-collection), the `source` sets the context for the log (e.g. `nginx`), enabling you to pivot between infrastructure metrics and related logs from the same system. The `source` tag also tells Datadog which [log processing pipeline](https://docs.datadoghq.com/logs/processing/pipelines/) to use to properly parse those logs in order to extract structured facets and attributes. Likewise, the `service` tag (which is a core tag in [Datadog APM](#track-application-performance-with-datadog-apm)) enables you to pivot seamlessly from logs to application-level metrics and request traces from the same service for rapid troubleshooting. 

{{< img src="openshift-monitoring-datadog-logs.png" border="true" popup="true" caption="Datadog can automatically pull out important information in logs from sources like NGINX." >}}

The Datadog Agent will attempt to automatically generate these tags for your logs from the image name. For example, logs from Redis containers will be tagged `source:redis` and `service:redis`. You can also provide custom values by including them in Kubernetes annotations in your deployment manifests:

{{< code-snippet lang="yaml" wrap="false" >}}
  annotations:
    ad.datadoghq.com/<CONTAINER_IDENTIFIER>.logs: '[{"source":"<SOURCE>","service":"<SERVICE>"}]'
{{< /code-snippet >}}

### Track application performance with Datadog APM
[Datadog APM](https://docs.datadoghq.com/tracing/) traces requests to your application as they propagate across infrastructure and services. You can then visualize the full lifespan of these requests from end to end. APM gives you deep visibility into application performance, database queries, dependencies between services, and other insights that enable you to optimize and troubleshoot application performance. 

Datadog APM auto-instruments a number of languages and application frameworks; consult the documentation for [supported languages](https://docs.datadoghq.com/tracing/setup/) and details on how to [get started](https://docs.datadoghq.com/tracing/send_traces/) with instrumenting your language or framework.

#### Enable APM in your OpenShift cluster
To enable tracing in your cluster, add the following to the [values chart](#create-the-datadog-values-chart) for the Datadog Agent:

{{< code-snippet lang="yaml" filename="datadog-values.yaml" wrap="false" >}}
datadog:
  [...]
  apm:
    enabled: true
    port: 8126
{{< /code-snippet >}}

By default, Datadog uses port 8126 for traces. You can customize this with the `apm.port` variable.

Update your Agent with these changes:

{{< code-snippet lang="bash" wrap="false" >}}
helm upgrade -f path/to/datadog-values.yaml <AGENT_SERVICE_NAME> stable/datadog
{{< /code-snippet >}}

Next, provide the host node's IP as an environment variable to ensure that application containers send traces to the Datadog Agent instance running on the correct node. This can be accomplished by configuring the application's Deployment manifest to provide the host node's IP as an environment variable using Kubernetes's [Downward API](https://kubernetes.io/docs/tasks/inject-data-application/downward-api-volume-expose-pod-information/#the-downward-api). Set the `DD_AGENT_HOST` environment variable in the manifest for the application to be monitored:

{{< code-snippet lang="yaml" wrap="false" >}}
spec:
      containers:
      - name: <CONTAINER_NAME>
        image: <CONTAINER_IMAGE>:<TAG>
        env:
          - name: DD_AGENT_HOST
            valueFrom:
              fieldRef:
                fieldPath: status.hostIP
{{< /code-snippet >}}

When you deploy your instrumented application, it will automatically begin sending traces to Datadog. From the APM tab of your Datadog account, you can see a breakdown of key performance indicators for each of your instrumented services, with information about request throughput, latency, errors, and the performance of any service dependencies.

{{< img src="openshift-monitoring-datadog-traces.png" border="true" popup="true" >}}

You can then dive in and inspect a flame graph that breaks down an individual trace into spans—each one representing an individual database query, function call, or operation carried out as part of fulfilling the request. For each span, you can view system metrics, application runtime metrics, error messages, and relevant logs that pertain to that unit of work.

{{< img src="openshift-monitoring-datadog-flame-graph.png" border="true" popup="true" >}}

## The Datadog Operator
The [Datadog Operator](https://github.com/DataDog/datadog-operator) simplifies the task of configuring and managing the Agents monitoring your cluster. You can deploy the node-based Agent DaemonSet, the Cluster Agent, and cluster check runners using a single [Custom Resource Definition (CRD)](https://docs.openshift.com/container-platform/4.2/operators/crds/crd-managing-resources-from-crds.html). 

The Datadog Operator is available on the [community operator hub](https://operatorhub.io/operator/datadog-operator) and has received [Red Hat OpenShift Operator Certification](https://blog.openshift.com/red-hat-openshift-operator-certification/), meaning that it has been tested to work with OpenShift clusters and screened for security risks.

## View your entire cluster from a single platform
If you followed along with the steps in this post, you have:

- Deployed the Datadog Cluster Agent and node-based Agent to collect cluster-level metrics and events from your OpenShift environment
- Seen how Autodiscovery can monitor your dynamic workloads even as containers are deployed and destroyed
- Ingested logs from your containers and the workloads running on them
- Set up APM and instrumented your applications to collect distributed traces

Datadog has additional features that can give you even deeper insights into your OpenShift cluster. You can see the documentation for our [OpenShift](https://docs.datadoghq.com/integrations/openshift/) and [Kubernetes](https://docs.datadoghq.com/agent/kubernetes) integrations for information on how to set up process monitoring, [network performance monitoring](https://docs.datadoghq.com/network_performance_monitoring/), custom metric collection, and more.

If you're not already using Datadog, sign up for a <a href="#" class="sign-up-trigger">free trial</a> and get end-to-end visibility into your OpenShift clusters along with more than {{< translate key="integration_count" >}} other technologies.

[part-one]: /blog/key-metrics-for-openshift-monitoring
[part-two]: /blog/openshift-monitoring-tools