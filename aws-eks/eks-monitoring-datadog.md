# Monitoring your EKS cluster with Datadog

In Parts [1][part-one] and [2][part-two] of this series, we saw that key EKS metrics come from several sources, and can be broken down into the following main types:

- Cluster state metrics from the Kubernetes API
- Node and container resource metrics from your nodes' kubelets
- AWS service metrics from AWS CloudWatch

In this post, we'll explore how Datadog's integrations with Kubernetes, Docker, and AWS will let you track the full range of EKS metrics, as well as logs and performance data from your cluster and applications. Datadog gives you comprehensive coverage of your dynamic infrastructure and applications with features like Autodiscovery to track services across containers; sophisticated graphing and alerting options; and full support for AWS services.

In this post, we will cover:

- [Installing the Datadog Agent](#deploy-the-agent-to-your-eks-cluster) across your cluster to track  host- and container-level resource metrics
- [Enabling Datadog's AWS integration](#enable-datadogs-aws-integrations) to collect CloudWatch metrics and events
- Using [Datadog's full feature set](#the-full-power-of-datadog) to get end-to-end visibility into your EKS infrastructure and hosted applications and services

If you don't already have a Datadog account but want to follow along and start monitoring your EKS cluster, sign up for a <a href="#" class="sign-up-trigger">free trial</a>.

## Deploy the Agent to your EKS cluster

The [Datadog Agent][agent] is [open source software][agent-source] that collects and forwards metrics, logs, and traces from each of your nodes and the containers running on them.

Once you deploy the Agent, you will have immediate access to the full range of Kubernetes cluster state and resource metrics discussed in [Part 1][part-one]. The Agent will also begin reporting additional system-level metrics from your nodes and containers.

We will go over how to deploy the [Datadog Cluster Agent](/blog/datadog-cluster-agent) and node-based Datadog Agents across your EKS cluster. The Cluster Agent communicates with the Kubernetes API servers to collect cluster-level information, while the node-based Agents report data from each node's kubelet.

{{< img src="eks-monitoring-datadog-cluster-agent.png" alt="Datadog Cluster Agent diagram" popup="true" >}}

While it is possible to deploy the Datadog Agent [without the Cluster Agent][daemonset-docs], using the Cluster Agent is recommended as it offers several benefits, particularly for large-scale EKS clusters:

- It reduces overall load on the Kubernetes API by using a single Cluster Agent as a proxy for querying cluster-level metrics.
- It provides additional security because only one Agent needs the permissions required to access the API server.
- It lets you automatically scale your pods using any metric that is collected by Datadog.

You can read more about the Datadog Cluster Agent [here][dca-readme].

Before turning to the Agent, however, make sure that you've [deployed `kube-state-metrics`][kube-state-metrics] Recall that `kube-state-metrics` is an add-on service that generates cluster state metrics and exposes them to the Metrics API. After you install the service, Datadog will be able to aggregate these metrics along with other resource and application data.

### Deploying the Datadog Cluster Agent

The Datadog Cluster Agent runs on a single node and serves as a proxy between the API servers and the rest of the node-based Agents in your cluster. It also makes it possible to configure Kubernetes's Horizontal Pod Autoscaling to use any metric that Datadog collects (more on this [below](#autoscale-your-eks-cluster-with-datadog-metrics)).

There are several steps needed to prepare your cluster for the Agent. These involve providing the appropriate permissions to the Cluster Agent and to the node-based Agents so each can access the information it needs. First, we need to configure RBAC permissions, and then create and deploy the Cluster Agent and node-based Agent manifests.

#### Configure RBAC permissions for the Cluster Agent and node-based Agents

EKS uses AWS IAM for [user authentication and access to the cluster][aws-iam-auth], but it relies on Kubernetes role-based access control (RBAC) to authorize calls by those users to the Kubernetes API. So, for both the Cluster Agent and the node-based Agents, we'll need to set up a [service account][service-account], a [ClusterRole][cluster-role] with the necessary RBAC permissions, and then a [ClusterRoleBinding][cluster-role-binding] that links them so that the service account can use those permissions.

First, create the Cluster Agent's RBAC file, **cluster-agent-rbac.yaml**:

```yaml
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: datadog-cluster-agent
rules:
- apiGroups:
  - ""
  resources:
  - services
  - events
  - endpoints
  - pods
  - nodes
  - componentstatuses
  verbs:
  - get
  - list
  - watch
- apiGroups:
  - "autoscaling"
  resources:
  - horizontalpodautoscalers
  verbs:
  - list
  - watch
- apiGroups:
  - ""
  resources:
  - configmaps
  resourceNames:
  - datadogtoken             # Kubernetes event collection state
  - datadog-leader-election  # Leader election token
  verbs:
  - get
  - update
- apiGroups:                 # To create the leader election token
  - ""
  resources:
  - configmaps
  verbs:
  - create
  - get
  - update
- nonResourceURLs:
  - "/version"
  - "/healthz"
  verbs:
  - get