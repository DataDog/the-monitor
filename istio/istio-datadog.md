# How to monitor Istio with Datadog
In [Part 2][part2], we showed you how to use Istio's built-in features and integrations with third-party tools to visualize your service mesh, including the metrics that we introduced in [Part 1][part1]. While Istio's containerized architecture makes it straightforward to plug in different kinds of visualization software like Kiali and Grafana, you can get deeper visibility into your service mesh and reduce the time you spend troubleshooting by monitoring Istio with a single platform.

In this post, we'll show you how to use Datadog to monitor Istio, including how to:

- [Collect metrics, traces, and logs](#how-to-run-datadog-in-your-istio-mesh) automatically from Istio's internal components and the services running within your mesh
- Use [dashboards](#visualize-all-of-your-istio-metrics-together) to visualize Istio metrics alongside metrics from Kubernetes and your containerized applications 
- [Visualize request traces](#visualize-mesh-topology-with-the-service-map) between services in your mesh to find bottlenecks and misconfigurations
- Search and analyze [all of the logs in your mesh](#understand-your-istio-logs) to understand trends and get context
- [Set alerts](#set-alerts-for-automatic-monitoring) to get notified automatically of issues within your mesh

 With Datadog, you can seamlessly navigate between Istio metrics, traces, and logs to place your Istio data in the context of your infrastructure as a whole. You can also use alerts to get notified automatically of possible issues within your Istio deployment.  

{{< img src="oob-dash.png" popup="true" border="true" >}}
 
Istio currently has full support only for [Kubernetes][istio-status-core], with alpha support for Consul and Nomad. As a result, we'll assume that you're running Istio with Kubernetes.

 
## How to run Datadog in your Istio mesh
The Datadog Agent is [open source software][dd-gh] that collects metrics, traces, and logs from your environment and [sends them to Datadog][dd-agent]. Datadog's [Istio integration][dd-istio] queries Istio's Prometheus endpoints automatically, meaning that you don't need to run your own Prometheus server to collect data from Istio. In this section, we'll show you how to set up the Datadog Agent to get deep visibility into your Istio service mesh. 


### Set up the Datadog Agent
To start monitoring your Istio Kubernetes cluster, you'll need to deploy: 

- A node-based Agent that runs on every node in your cluster, gathering metrics, traces, and logs to send to Datadog
- A [Cluster Agent][dd-k8s-intro] that runs as a [Deployment][kube-deployment], communicating with the Kubernetes API server and providing [cluster-level metadata][meta-response] to node-based Agents

With this approach, we can [avoid the overhead][dd-cluster-agent] of having all node-based Agents communicate with the Kubernetes control plane, as well as enrich metrics collected from node-based Agents with cluster-level metadata, such as the names of services running within the cluster. 

You can install the Datadog Cluster Agent and node-based Agents by taking the following steps, which we'll lay out in more detail below.

- [Assign permissions](#configure-permissions-for-the-cluster-agent-and-node-based-agents) that allow the Cluster Agent and node-based Agents to communicate with each other and to access your metrics, traces, and logs. 
- Apply Kubernetes manifests for both the [Cluster Agent](#configure-the-cluster-agent) and [node-based Agents](#configure-the-node-based-agent) to deploy them to your cluster.
 

#### Configure permissions for the Cluster Agent and node-based Agents
Both the Cluster Agent and node-based Agents take advantage of Kubernetes' built-in role-based access control (RBAC), and the first step is enabling the following:

- A [ClusterRole][cluster-role] that declares a named set of permissions for accessing Kubernetes resources, in this case to allow the Agent to collect data on your cluster
- A [ClusterRoleBinding][cluster-role-binding] that assigns the ClusterRole to the [service account][service-account] that the Datadog Agent will use to access the Kubernetes [API server][k8s-api]

The Datadog Agent GitHub repository contains manifests that enable RBAC for the [Cluster Agent][rbac-cluster] and [node-based Agents][rbac-nodes]. One of these grants permissions to the Datadog Cluster Agent's ClusterRole:

{{< code-snippet lang="yaml" filename="rbac-cluster-agent.yaml " >}}
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
 name: datadog-cluster-agent
 namespace: <DATADOG_NAMESPACE>
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
  - datadogtoken                     
  - datadog-leader-election          
  verbs:
  - get
  - update
- apiGroups:                         
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
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
 name: datadog-cluster-agent
 namespace: <DATADOG_NAMESPACE>
roleRef:
 apiGroup: rbac.authorization.k8s.io
 kind: ClusterRole
 name: datadog-cluster-agent
subjects:
- kind: ServiceAccount
  name: datadog-cluster-agent
  namespace: <DATADOG_NAMESPACE>
---
kind: ServiceAccount
apiVersion: v1
metadata:
 name: datadog-cluster-agent
 namespace: <DATADOG_NAMESPACE>
{{</ code-snippet >}}

You'll also need to create a manifest that grants the appropriate permissions to the node-based Agent's ClusterRole. 

{{< code-snippet lang="yaml" filename="rbac-agent.yaml" >}}
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
 name: datadog-agent
 namespace: <DATADOG_NAMESPACE>
rules:
- apiGroups:                     
  - ""
  resources:
  - nodes/metrics
  - nodes/spec
  - nodes/proxy                  
  verbs:
  - get
---
kind: ServiceAccount
apiVersion: v1
metadata:
 name: datadog-agent
 namespace: <DATADOG_NAMESPACE>
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
 name: datadog-agent
 namespace: <DATADOG_NAMESPACE>
roleRef:
 apiGroup: rbac.authorization.k8s.io
 kind: ClusterRole
 name: datadog-agent
subjects:
- kind: ServiceAccount
  name: datadog-agent
  namespace: <DATADOG_NAMESPACE>

{{</ code-snippet >}}

Next, deploy the resources you've created.

{{< code-snippet lang="bash" >}}
$ kubectl apply -f /path/to/rbac-cluster-agent.yaml
$ kubectl apply -f /path/to/rbac-agent.yaml
{{</ code-snippet >}}

You can verify that all of the appropriate ClusterRoles exist in your cluster by running this command:

{{< code-snippet lang="bash" >}}
$ kubectl get clusterrole | grep datadog
datadog-agent                                                          1h
datadog-cluster-agent                                                  1h
{{</ code-snippet >}}

#### Enable secure communication between Agents
Next, we'll ensure that the Cluster Agent and node-based Agents can securely communicate by creating a [Kubernetes secret][k8s-secret], which stores a cryptographic token that the Agents can access.

To generate the token (a 32-character string that we'll encode in Base64), run the following:

{{< code-snippet lang="bash" >}}
echo -n '<32_CHARACTER_LONG_STRING>' | base64
{{</ code-snippet >}}

Create a file named **dca-secret.yaml** and add your newly created token:

{{< code-snippet lang="yaml" filename="dca-secret.yaml" >}}
apiVersion: v1
kind: Secret
metadata:
 name: datadog-auth-token
 namespace: <DATADOG_NAMESPACE>
type: Opaque
data:
 token: <NEW_SECRET_TOKEN>
{{</ code-snippet >}}

Once you've added your token to the manifest, `apply` it to create the secret:

{{< code-snippet lang="bash" >}}
$ kubectl apply -f /path/to/dca-secret.yaml
{{</ code-snippet >}}

Run the following command to confirm that you've created the secret:

{{< code-snippet lang="bash" >}}
$ kubectl get secret | grep datadog
datadog-auth-token          Opaque                                1         21h
{{</ code-snippet >}}


#### Configure the Cluster Agent
To configure the Cluster Agent, create the following manifest, which declares two Kubernetes resources:

- A [Deployment][k8s-deployment] that adds an instance of the Cluster Agent container to your cluster
- A [Service][k8s-service] that allows the Datadog Cluster Agent to communicate with the rest of your cluster

This manifest links these resources to the service account we deployed above and points to the newly created secret. Make sure to add your [Datadog API key][dd-api] where indicated. (Or use a [Kubernetes secret][k8s-secret] as we did for the Cluster Agent authorization token.)

{{< code-snippet lang="yaml" filename="datadog-cluster-agent.yaml" >}}
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: datadog-cluster-agent
  namespace: <DATADOG_NAMESPACE>
spec:
  template:
    metadata:
      labels:
        app: datadog-cluster-agent
      name: datadog-agent
    spec:
      serviceAccountName: datadog-cluster-agent
      containers:
      - image: datadog/cluster-agent:latest
        imagePullPolicy: Always
        name: datadog-cluster-agent
        env:
          - name: DD_API_KEY
            value: "<DATADOG_API_KEY>"
          - name: DD_COLLECT_KUBERNETES_EVENTS
            value: "true"
          - name: DD_EXTERNAL_METRICS_PROVIDER_ENABLED
            value: "true"
          - name: DD_CLUSTER_AGENT_AUTH_TOKEN
            valueFrom:
              secretKeyRef:
                name: datadog-auth-token
                key: token
---
apiVersion: v1
kind: Service
metadata:
 name: datadog-cluster-agent
 namespace: <DATADOG_NAMESPACE>
 labels:
   app: datadog-cluster-agent
spec:
 ports:
 - port: 5005 # Has to be the same as the one exposed in the Cluster Agent. Default is 5005.
   protocol: TCP
 selector:
   app: datadog-cluster-agent
{{</ code-snippet >}}


#### Configure the node-based Agent
The node-based Agent collects metrics, traces, and logs from each node and sends them to Datadog. We'll ensure that an Agent pod runs on each node in the cluster, even for newly launched nodes, by declaring a [DaemonSet][k8s-daemonset]. Create the following manifest, adding your Datadog API key where indicated:

{{< code-snippet lang="yaml" filename="datadog-agent.yaml" >}}
apiVersion: extensions/v1beta1
kind: DaemonSet
metadata:
 name: datadog-agent
 namespace: <DATADOG_NAMESPACE>
spec:
 template:
   metadata:
     labels:
       app: datadog-agent
     name: datadog-agent
   spec:
     serviceAccountName: datadog-agent
     containers:
     - image: datadog/agent:latest
       imagePullPolicy: Always
       name: datadog-agent
       ports:
         - containerPort: 8125
           hostPort: 8125
           name: dogstatsdport
           protocol: UDP
       env:
         - name: DD_API_KEY
           value: "<DATADOG_API_KEY>"
         - name: DD_COLLECT_KUBERNETES_EVENTS
           value: "true"
         - name: KUBERNETES
           value: "true"
         - name: DD_KUBERNETES_KUBELET_HOST
           valueFrom:
             fieldRef:
               fieldPath: status.hostIP
         - name: DD_CLUSTER_AGENT_ENABLED
           value: "true"
         - name: DD_CLUSTER_AGENT_AUTH_TOKEN
           valueFrom:
             secretKeyRef:
               name: datadog-auth-token
               key: token
         - name: DD_TAGS
           value: "env:<YOUR_ENV_NAME>"
       resources:
         requests:
           memory: "256Mi"
           cpu: "200m"
         limits:
           memory: "256Mi"
           cpu: "200m"
       volumeMounts:
         - name: dockersocket
           mountPath: /var/run/docker.sock
         - name: procdir
           mountPath: /host/proc
           readOnly: true
         - name: cgroups
           mountPath: /host/sys/fs/cgroup
           readOnly: true
       livenessProbe:
         exec:
           command:
           - ./probe.sh
         initialDelaySeconds: 15
         periodSeconds: 5
     volumes:
       - hostPath:
           path: /var/run/docker.sock
         name: dockersocket
       - hostPath:
           path: /proc
         name: procdir
       - hostPath:
           path: /sys/fs/cgroup
         name: cgroups
{{</ code-snippet >}}

#### Disable automatic sidecar injection for Datadog Agent pods
You'll also want to prevent Istio from [automatically injecting Envoy sidecars][istio-auto-inject] into your Datadog Agent pods and interfering with data collection. You need to [disable automatic sidecar injection][dd-no-sidecar] for both the Cluster Agent and node-based Agents by revising each manifest to include the following annotation: 

{{< code-snippet lang="yaml" >}}
[...]
spec:
 [...]
  template:
    metadata:
      annotations:
        sidecar.istio.io/inject: "false"
   [...]
{{</ code-snippet >}}

Then deploy the Datadog Agents:

{{< code-snippet lang="bash" >}}
$ kubectl apply -f /path/to/datadog-cluster-agent.yaml
$ kubectl apply -f /path/to/datadog-agent.yaml
{{</ code-snippet >}}

Use the following `kubectl` command to verify that your Cluster Agent and node-based Agent pods are running. There should be one pod named `datadog-agent-<STRING>` running per node, and a single instance of `datadog-cluster-agent-<STRING>`.

{{< code-snippet lang="bash">}}
$ kubectl -n <DATADOG_NAMESPACE> get pods
NAME                                    READY   STATUS    RESTARTS   AGE
datadog-agent-bqtdt                     1/1     Running   0          4d22h
datadog-agent-gb5fs                     1/1     Running   0          4d22h
datadog-agent-lttmq                     1/1     Running   0          4d22h
datadog-agent-vnkqx                     1/1     Running   0          4d22h
datadog-cluster-agent-9b5b56d6d-jwg2l   1/1     Running   0          5d22h

{{</ code-snippet >}}

Once you've deployed the Cluster Agent and node-based Agents, Datadog will start to report host– and platform-level metrics from your Kubernetes cluster.


{{< img src="kube-metrics.png" popup="true" border="true" >}}

Before you can get metrics from Pilot, Galley, Mixer, Citadel, and services within your mesh, you'll need to set up Datadog's Istio integration.

### Set up the Istio integration
The Datadog Agent's [Istio integration][dd-istio-integ] automatically queries Istio's Prometheus metrics endpoints, enriches all of the data with tags, and forwards it to the Datadog platform. The Datadog Cluster Agent uses a feature called [endpoints checks][endpoint-check] to detect Istio's Kubernetes services, identify the pods that back them, and [send configurations][cluster-checks] to the Agents on the nodes running those pods. Each node-based Agent then uses these configurations to query the Istio pods running on the local node for data.

If you horizontally scale an Istio component, there is a risk that requests to that component's Kubernetes service will load balance randomly across the component's pods. Endpoints checks enable the Datadog Agent to bypass Istio's Kubernetes services and query the backing pods directly, avoiding the risk of load balancing queries.

{{< img src="mesh-tag-dash.png" border="true" popup="true" >}}

The Datadog Agent uses [Autodiscovery][ad] to track the services exposing Istio's Prometheus endpoints. We can enable the Istio integration by [annotating][kube-annot] these services. The annotations contain Autodiscovery [templates][ad-template]—when the Cluster Agent detects that a currently deployed service contains a relevant annotation, it will identify each backing pod, populate the template with the pod's IP address, and send the resulting configuration to a node-based Agent. We'll create one Autodiscovery template per Istio component—each Agent will only load configurations for Istio pods running on its own node. 

Note that you'll need to run [versions][717] 6.17+ or 7.17+ of the node-based Agent and version [1.5.2+][152] of the Datadog Cluster Agent.

Run the following script to annotate each Istio service using `kubectl patch`. Since there are [multiple ways][istio-install] to install Istio, this approach lets you annotate your services without touching their manifests.

{{< code-snippet lang="bash" >}}
#!/bin/bash
kubectl -n istio-system patch service istio-telemetry --patch "$(cat<<EOF
metadata:
    annotations:
        ad.datadoghq.com/endpoints.check_names: '["istio"]'
        ad.datadoghq.com/endpoints.init_configs: '[{}]'
        ad.datadoghq.com/endpoints.instances: |
            [
              {
                "istio_mesh_endpoint": "http://%%host%%:42422/metrics",
                "mixer_endpoint": "http://%%host%%:15014/metrics",
                "send_histograms_buckets": true
              }
            ]
EOF
)"

kubectl -n istio-system patch service istio-galley --patch "$(cat<<EOF
metadata:
    annotations:
        ad.datadoghq.com/endpoints.check_names: '["istio"]'
        ad.datadoghq.com/endpoints.init_configs: '[{}]'
        ad.datadoghq.com/endpoints.instances: |
            [
              {
                "galley_endpoint": "http://%%host%%:15014/metrics",
                "send_histograms_buckets": true
              }
            ]
EOF
)"

kubectl -n istio-system patch service istio-pilot --patch "$(cat<<EOF
metadata:
    annotations:
        ad.datadoghq.com/endpoints.check_names: '["istio"]'
        ad.datadoghq.com/endpoints.init_configs: '[{}]'
        ad.datadoghq.com/endpoints.instances: |
            [
              {
                "pilot_endpoint": "http://%%host%%:15014/metrics",
                "send_histograms_buckets": true
              }
            ]
EOF
)"

kubectl -n istio-system patch service istio-citadel --patch "$(cat<<EOF
metadata:
    annotations:
        ad.datadoghq.com/endpoints.check_names: '["istio"]'
        ad.datadoghq.com/endpoints.init_configs: '[{}]'
        ad.datadoghq.com/endpoints.instances: |
            [
              {
                "citadel_endpoint": "http://%%host%%:15014/metrics",
                "send_histograms_buckets": true
              }
            ]
EOF
)"
{{</ code-snippet >}}

When the Cluster Agent identifies a Kubernetes service that contains these annotations, it uses them to fill in configuration details for the Istio integration. The `%%host%%` [template variable][ad-tv] becomes the IP of a pod backing the service. The Cluster Agent sends the configuration to a Datadog Agent running on the same node, and the Agent uses the configuration to query the pod's metrics endpoint.

You can also provide a value for the option `send_histograms_buckets`—if this option is enabled (the default), the Datadog Agent will tag any [histogram-based metrics][prom-histogram] with the `upper_bound` prefix, [indicating the name][config-hist-bucket] of the metric's quantile bucket.  

Next, update the node-based Agent and Cluster Agent manifests to enable endpoints checks. The Datadog Cluster Agent sends endpoint check configurations to node-based Agents using [cluster checks][cluster-checks], and you will need to enable these as well. In the node-based Agent manifest, add the following environment variables:

{{< code-snippet lang="yaml" filename="datadog-agent.yaml" >}}
# [...]
spec:
  template:
    spec:
      containers:
      - image: datadog/agent:latest
        # [...]
        env:
          # [...]
          - name: DD_EXTRA_CONFIG_PROVIDERS
            value: "endpointschecks clusterchecks"
{{</ code-snippet >}}

If you set `DD_EXTRA_CONFIG_PROVIDERS` to `endpointschecks`, the node-based Agents will collect endpoint check configurations from the Cluster Agent. We also need to add the value `clusterchecks`, which tells the node-based Agent to pull configurations from the Cluster Agent.

Now add the following environment variables to the Cluster Agent manifest:

{{< code-snippet lang="yaml" filename="datadog-cluster-agent.yaml" >}}
# [...]
spec:
  template:
    spec:
      containers:
      - image: datadog/agent:latest
        # [...]
        env:
          # [...]
          - name: DD_CLUSTER_CHECKS_ENABLED
            value: "true"
          - name: DD_EXTRA_CONFIG_PROVIDERS
            value: "kube_endpoints kube_services"
          - name: DD_EXTRA_LISTENERS
            value: "kube_endpoints kube_services"
{{</ code-snippet >}}

The `DD_EXTRA_CONFIG_PROVIDERS` and `DD_EXTRA_LISTENERS` variables tell the Cluster Agent to query the Kubernetes API server for the status of currently active endpoints and services. 

Finally, apply the changes.

{{< code-snippet lang="shell" >}}
$ kubectl apply -f path/to/datadog-agent.yaml
$ kubectl apply -f path/to/datadog-cluster-agent.yaml
{{</ code-snippet >}}

After running these commands, you should expect to see Istio metrics flowing into Datadog. The easiest way to confirm this is to navigate to our [out-of-the-box dashboard for Istio][istio-dash], which we'll explain in more detail later.

Finally, enable the Istio integration by [clicking the tile][istio-tile] in your Datadog account.

You can also use Autodiscovery to collect metrics, traces, and logs from the applications running in your mesh with minimal configuration. Consult Datadog's [documentation][dd-integ-docs] for the configuration details you'll need to include. 


## Get high-level views of your Istio mesh
When running a complex distributed system using Istio, you'll want to ensure that your nodes, containers, and services are performing as expected. This goes for both Istio's internal components (Pilot, Mixer, Galley, Citadel, and your mesh of Envoy proxies) and the services that Istio manages. Datadog helps you visualize the health and performance of your entire Istio deployment in one place.

### Visualize all of your Istio metrics together
After installing the Datadog Agent and enabling the Istio integration, you'll have access to an out-of-the-box dashboard showing key Istio metrics. You can see request throughput and latency from throughout your mesh, as well as resource utilization metrics for each of Istio's internal components. 

You can then clone the out-of-the-box Istio dashboard and customize it to produce the most helpful view for your environment. Datadog imports [tags][dd-tags] automatically from Docker, Kubernetes, and Istio, as well as from the mesh-level metrics that Mixer exports to Prometheus (e.g., `source_app` and `destination_service_name`). You can use tags to group and filter dashboard widgets to get visibility into Istio's performance. For example, the following timeseries graph and toplist use the `adapter` tag to show how many dispatches Mixer makes to each adapter.
{{< img src="mixer-tags.png" border="true" >}}
 
You can also quickly understand the scope of an issue (does it affect a host, a pod, or your whole cluster?) by using Datadog's mapping features: the host map and container map. Using the container map, you can easily localize issues within your Kubernetes cluster. And if issues are due to resource constraints within your Istio nodes, this will become apparent within the host map.


 {{< img src="istio-maps.png" popup="true" border="true" >}}

You can color the host map based on the current value of any metric (and the container map based on any resource metric), making it clear which parts of your infrastructure are underperforming or overloaded. You can then use tags to group and filter the maps, helping you answer any questions about your infrastructure. 

The dashboard above shows CPU utilization in our Istio deployment. In the upper-left widget, we can see that this metric is high for two hosts. To investigate, we can use the container map on the bottom left to see if any container running within those hosts is facing unusual load. Istio's components might run on any node in your cluster—the same goes for the pods running your services. To monitor our pods regardless of where they are running, we can group containers by the `service` tag, making it clear which Istio components or mesh-level services are facing the heaviest demand. The `kube_namespace` tag allows us to view components and services separately.

### Get insights into mesh activity
Getting visibility into traffic between Istio-managed services is key to understanding the health and performance of your service mesh. With Datadog's distributed tracing and application performance monitoring, you can [trace requests][dd-istio-trace] between your Istio-managed services to understand your mesh and troubleshoot issues. You can display your entire service topology using the Service Map, visualize the path of each request through your mesh using flame graphs, and get a detailed performance portrait of each service. From APM, you can easily navigate to related metrics and logs, allowing you to troubleshoot more quickly than you would with dedicated graphing, tracing, and log collection tools. 


#### Set up tracing

##### Receiving traces
First, you'll need to instruct the node-based Agents to accept traces. [Edit the node-based Agent manifest][dd-k8s-apm] to include the following attributes. 

{{< code-snippet lang="yaml" filename="datadog-agent.yaml" >}}
[...]
      env:
        [...]
        - name: DD_APM_ENABLED
          value: "true"
        - name: DD_APM_NON_LOCAL_TRAFFIC
          value: "true"
        - name: DD_APM_ENV
          value: "istio-demo"
[...]
{{</ code-snippet >}}

`DD_APM_ENABLED` instructs the Agent to collect traces. `DD_APM_NON_LOCAL_TRAFFIC` configures the Agent to listen for traces from containers on other hosts. Finally, if you want to keep traces from your Istio cluster separate from other projects within your organization, use the `DD_APM_ENV` variable to customize the `env:` tag for your traces (`env:none` by default). You can then filter by this tag within Datadog.

Next, forward port 8126 from the node-based Agent container to its host, allowing the host to listen for distributed traces.

{{< code-snippet lang="yaml" filename="datadog-agent.yaml" >}}
[...]
      ports:
        [...]
        - containerPort: 8126
          hostPort: 8126
          name: traceport
          protocol: TCP
[...]
{{</ code-snippet >}}

This example configures Datadog to trace requests between Envoy proxies, so you can visualize communication between your services without having to instrument your application code. If you want to trace activity within an application, e.g., a function call, you can use Datadog's [tracing libraries][dd-instrument] to either auto-instrument your application or declare traces within your code for fine-grained benchmarking and troubleshooting.

Finally, [create a service][dd-istio-service] for the node-based Agent, so it can receive traces from elsewhere in the mesh. We'll use a [headless service][k8s-headless-svc] to avoid needlessly allocating a cluster IP to the Agent. Create the following manifest and apply it using `kubectl apply`:

{{< code-snippet filename="dd-agent-service.yaml" lang="yaml" >}}
apiVersion: v1
kind: Service
metadata:
  labels:
    app: datadog-agent
  name: datadog-agent
  namespace: <DATADOG_NAMESPACE>
spec:
  clusterIP: None
  ports:
  - name: dogstatsdport
    port: 8125
    protocol: UDP
    targetPort: 8125
  - name: traceport
    port: 8126
    protocol: TCP
    targetPort: 8126
  selector:
    app: datadog-agent
{{</ code-snippet >}}

After you apply this configuration, the Datadog Agent should be able to receive traces from Envoy proxies throughout your cluster. In the next step, you'll configure Istio to send traces to the Datadog Agent.


##### Sending traces
Istio has [built-in support][istio-tracing] for distributed tracing using [several possible backends][istio-global-opts], including Datadog. You need to configure tracing by setting three options:

1. `pilot.traceSampling` is the [percentage of requests][trace-sample] that Istio will record as traces. Set this to `100.00` to send all traces to Datadog—you can then determine [within Datadog][dd-trace-sample] how long to retain your traces.
2.`global.proxy.tracer` instructs Istio to use a particular tracing backend, in our case `datadog`. 
3. `tracing.enabled` instructs Istio to record traces of requests within your service mesh.

Run [the following command][dd-istio-helm] to enable Istio to send traces automatically to Datadog: 

{{< code-snippet lang="bash" >}}
helm upgrade --install istio <ISTIO_INSTALLATION_PATH>/install/kubernetes/helm/istio --namespace istio-system --set pilot.traceSampling=100.0,global.proxy.tracer=datadog,tracing.enabled=true
{{</ code-snippet>}}


#### Visualize mesh topology with the Service Map
Datadog automatically generates a [Service Map][dd-service-map] from distributed traces, allowing you to quickly understand how services communicate within your mesh. The Service Map gives you a quick read into the results of your Istio configuration, so you can identify issues and determine where you might begin to optimize your network.

If you have set up alerts for any of your services (we'll introduce these [in a moment](#set-alerts-for-automatic-monitoring)), the Service Map will show their status. In this example, an alert has triggered for the `productpage` service in the `default` namespace. We can navigate directly from the Service Map to see which alerts have triggered.

{{< img src="service-map.png" border="true" popup="true" >}}



And if you click on "View service overview," you can get more context into service-level issues by viewing request rates, error rates, and latencies for a single service over time. For example, we can navigate to the overview of the `productpage` service to see when the service started reporting a high rate of errors, and correlate the beginning of the issue with metrics, traces, and logs from the same time.

{{< img src="service-ov.png" popup="true" border="true" >}}

## Understand your Istio logs
If services within your mesh fail to communicate as expected, you'll want to consult logs to get more context. As traffic flows throughout your Istio mesh, Datadog can help you cut through the complexity by collecting all of your Istio logs in one platform for visualization and analysis.

### Set up Istio log collection
To [enable log collection][dd-logs-k8s], edit the **datadog-agent.yaml** manifest you created [earlier](#tk) to provide a [few more environment variables][dd-log-env]:

- `DD_LOGS_ENABLED`: switches on Datadog log collection
- `DD_LOGS_CONFIG_CONTAINER_COLLECT_ALL`: tells each node-based Agent to collect logs from all containers running on that node
- `DD_AC_EXCLUDE`: filters out logs from certain containers before they reach Datadog, such as, in our case, those from Datadog Agent containers 

{{< code-snippet lang="yaml" filename="datadog-agent.yaml" >}}
[...]
  env:
    [...]
    - name: DD_LOGS_ENABLED
        value: "true"
    - name: DD_LOGS_CONFIG_CONTAINER_COLLECT_ALL
        value: "true"
    - name: DD_AC_EXCLUDE 
        value: "name:datadog-agent name:datadog-cluster-agent"
[...]
{{</ code-snippet >}}

Next, edit the file to mount the node-based Agent container to the local node's Docker socket. Since you'll be deploying the Datadog Agent pod as a DaemonSet, each Agent will read logs from the Docker socket on its local node, enrich them with tags imported from Docker, Kubernetes, and your cloud provider, and send them to Datadog. Istio's components publish logs to `stdout` and `stderr` [by default][part2-logs], meaning that the Datadog Agent can collect all of your Istio logs from the Docker socket.

{{< code-snippet lang="yaml"  filename="datadog-agent.yaml" >}}
  (...)
    volumeMounts:
      (...)
      - name: dockersocket
        mountPath: /var/run/docker.sock
  (...)
  volumes:
    (...)
    - hostPath:
        path: /var/run/docker.sock
      name: dockersocket
  (...)
{{</ code-snippet >}}

Note that if you plan to run more than 10 containers in each pod, you'll want to configure the Agent to use a [Kubernetes-managed log file][dd-logs-kfile] instead of the Docker socket.  

Once you run `kubectl apply -f path/to/datadog-agent.yaml`, you should start seeing your logs within Datadog.


### Discover trends with Log Patterns
Once you're collecting logs from your Istio mesh, you can start exploring them in Datadog. The [Log Patterns view][dd-log-patterns] helps you extract trends by displaying common strings within your logs and generalizing the fields that vary into regular expressions. The result is a summary of common log types. This is especially useful for reducing noise within your Istio-managed environment, where you might be gathering logs from all of Istio's internal components in addition to Envoy proxies and the services in your mesh. 

{{< img src="log-patterns.png" border="true" popup="true" >}}

In this example, we used the sidebar to display only the patterns having to do with our Envoy proxies. We also filtered out INFO-level logs. Now that we know which error messages are especially common—Mixer is having trouble connecting to its upstream services—we can determine how urgent these errors are and how to go about resolving them.

## Set alerts for automatic monitoring
When running a complex distributed system, it's impossible to watch every host, pod, and container for possible issues. You'll want some way to automatically get notified when something goes wrong in your Istio mesh. Datadog allows you to set alerts on any kind of data it collects, including metrics, logs, and request traces. 

In this example, we're creating an alert that will notify us whenever requests to the `productpage` service in Istio's "Bookinfo" sample application take place at an unusual frequency, using APM data and Datadog's [anomaly detection][dd-anomaly] algorithm.


{{< img src="anomaly-alert.png" border="true" popup="true" >}}

You can also get automated insights into aberrant trends with Datadog's [Watchdog feature][dd-watchdog], which automatically flags performance anomalies in your dynamic service mesh. With Watchdog, you can easily detect issues like heavy request traffic, service outages, or spikes in demand, without setting up any alerts. Watchdog searches your APM-based metrics (request rates, request latencies, and error rates) for possible issues, and presents these to you as a feed when you first log in.


## A view of your mesh at every scale
In this post, we’ve shown you how to use Datadog to get comprehensive visibility into metrics, traces, and logs from throughout your Istio mesh. Integrated views allow you to navigate easily between data sources, troubleshoot issues, and manage the complexity that comes with running a service mesh. If you’re not already using Datadog, you can sign up for a <a href="#" class="sign-up-trigger">free trial</a>.



<!--links-->
[152]: https://hub.docker.com/layers/datadog/cluster-agent/1.5.2/images/sha256-cd9148640d4e41d4294765529a9569ef6d0b6a11d04844e745b9f9c1d6eebdf3?context=explore
[717]: https://github.com/DataDog/datadog-agent/releases/tag/7.17.0
[ad]: https://docs.datadoghq.com/agent/autodiscovery/
[ad-template]: https://docs.datadoghq.com/agent/autodiscovery/integrations/?tab=kubernetes
[ad-tv]: https://docs.datadoghq.com/agent/autodiscovery/template_variables/
[cluster-checks]: https://docs.datadoghq.com/agent/cluster_agent/clusterchecks/#cluster-agent
[cluster-role]: https://kubernetes.io/docs/reference/access-authn-authz/rbac/#role-and-clusterrole
[cluster-role-binding]: https://kubernetes.io/docs/reference/access-authn-authz/rbac/#rolebinding-and-clusterrolebinding
[config-hist-bucket]: https://docs.datadoghq.com/integrations/prometheus/#metrics
[dd-ad]: https://docs.datadoghq.com/agent/autodiscovery/?tab=agent
[dd-ad-autoconf]: https://www.datadoghq.com/blog/autodiscovery-docker-monitoring/#i-want-it-what-do-i-need-to-do
[dd-agent]: https://docs.datadoghq.com/agent/
[dd-agent-host-use]: https://docs.datadoghq.com/tracing/setup/python/#change-agent-hostname
[dd-anomaly]: https://www.datadoghq.com/blog/introducing-anomaly-detection-datadog/
[dd-api]: https://app.datadoghq.com/account/settings#api
[dd-cluster-agent]: https://docs.datadoghq.com/agent/kubernetes/cluster/
[dd-gh]: https://github.com/datadog/datadog-agent
[dd-instrument]: https://docs.datadoghq.com/tracing/setup/
[dd-integ-docs]: https://docs.datadoghq.com/integrations/
[dd-istio]: https://docs.datadoghq.com/integrations/istio/
[dd-istio-helm]: https://docs.datadoghq.com/tracing/setup/istio/#istio-configuration-and-installation
[dd-istio-integ]: https://docs.datadoghq.com/integrations/istio
[dd-istio-service]: https://docs.datadoghq.com/tracing/setup/istio/#create-a-headless-service-for-the-datadog-agent
[dd-istio-trace]: https://docs.datadoghq.com/tracing/setup/istio/
[dd-k8s-apm]: https://docs.datadoghq.com/agent/kubernetes/daemonset_setup/?tab=dockersocket#apm-and-distributed-tracing
[dd-k8s-intro]: https://www.datadoghq.com/blog/datadog-cluster-agent/
[dd-log-env]: https://docs.datadoghq.com/agent/docker/log/?tab=containerinstallation#one-step-install-to-collect-all-the-container-logs
[dd-log-patterns]: https://docs.datadoghq.com/logs/explorer/patterns/
[dd-logs-k8s]: https://docs.datadoghq.com/agent/kubernetes/daemonset_setup/?tab=dockersocket#log-collection
[dd-logs-kfile]: https://docs.datadoghq.com/agent/kubernetes/daemonset_setup/?tab=k8sfile#log-collection
[dd-no-sidecar]: https://docs.datadoghq.com/tracing/setup/istio/#disable-sidecar-injection-for-the-datadog-agent
[dd-service-map]: https://www.datadoghq.com/blog/service-map/
[dd-tags]: https://docs.datadoghq.com/tagging/
[dd-trace-sample]: https://docs.datadoghq.com/tracing/guide/trace_sampling_and_storage/
[dd-tracing-lib]: https://docs.datadoghq.com/developers/libraries/
[dd-tsa]: https://docs.datadoghq.com/tracing/trace_search_and_analytics/?tab=java
[dd-watchdog]: https://docs.datadoghq.com/watchdog/
[endpoint-check]: https://docs.datadoghq.com/agent/cluster_agent/endpointschecks/
[istio-auto-inject]: https://istio.io/docs/setup/kubernetes/additional-setup/sidecar-injection/#automatic-sidecar-injection
[istio-canary]: https://istio.io/blog/2017/0.1-canary/
[istio-dash]: https://app.datadoghq.com/screen/integration/30287/istio-dashboard
[istio-global-opts]: https://istio.io/docs/reference/config/installation-options/#global-options
[istio-install]: https://istio.io/docs/setup/install/
[istio-status-core]: https://istio.io/about/feature-stages/#core
[istio-tile]: https://app.datadoghq.com/account/settings#integrations/istio
[istio-tracing]: https://istio.io/docs/tasks/telemetry/distributed-tracing/overview/
[k8s-api]: https://kubernetes.io/docs/concepts/overview/kubernetes-api/
[k8s-daemonset]: https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/
[k8s-deployment]: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
[k8s-headless-svc]: https://kubernetes.io/docs/concepts/services-networking/service/#headless-services
[k8s-secret]: https://kubernetes.io/docs/concepts/configuration/secret/
[k8s-service]: https://kubernetes.io/docs/concepts/services-networking/service/
[kube-annot]: https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/
[kube-deployment]: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
[mesh-labels]: https://github.com/istio/istio/blob/99f158b9ab9b524617bc6e0b0fb903028cc7756e/install/kubernetes/helm/istio/charts/mixer/templates/config.yaml#L665-L684
[meta-response]: https://godoc.org/github.com/DataDog/datadog-agent/pkg/clusteragent/api/v1#MetadataResponse
[part1]: /blog/istio-metrics
[part2]: /blog/istio-monitoring-tools
[part2-logs]: /blog/istio-monitoring-tools#istio-and-envoy-logging
[prom-addon-retention]: https://github.com/istio/istio/blob/5fcf87485eee9f6a2ddee4af0a56ba1b93844865/install/kubernetes/helm/istio/charts/prometheus/values.yaml#L9
[prom-histogram]: https://prometheus.io/docs/concepts/metric_types/#histogram
[rbac-cluster]: https://github.com/DataDog/datadog-agent/blob/a4cb7a99967d589477b405697c6eef58895364e9/Dockerfiles/manifests/cluster-agent/rbac/rbac-cluster-agent.yaml
[rbac-nodes]:https://github.com/DataDog/datadog-agent/blob/a4cb7a99967d589477b405697c6eef58895364e9/Dockerfiles/manifests/cluster-agent/rbac/rbac-agent.yaml
[service-account]: https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/
[service-map-color]: https://docs.datadoghq.com/tracing/visualization/services_map/#color
[trace-sample]: https://istio.io/docs/tasks/telemetry/distributed-tracing/overview/#trace-sampling

