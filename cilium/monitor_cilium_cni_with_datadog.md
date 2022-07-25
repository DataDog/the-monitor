# Monitor Cilium with Datadog

In [Part 2][part-2] of this series, we showed how Hubble, Cilium's observability platform, enables you to view network-level details about service dependencies and traffic flows. Cilium also integrates with various standalone monitoring tools, so you can track the other key metrics discussed in [Part 1][part-1]. But since the platform is an integral part of your infrastructure, you need the ability to easily correlate Cilium network and resource metrics with data from your Kubernetes resources. Otherwise, you may potentially miss issues that could lead to an outage. 

Datadog brings together all of Cilium's observability data under a single platform, providing end-to-end visibility into your Cilium network and Kubernetes environment. In this post, we'll show how to use Datadog to:

- [visualize Cilium metrics](#visualize-cilium-metrics-and-clusters) via Datadog's out-of-the-box integration 
- [analyze Cilium logs](#analyze-cilium-logs-for-network-and-performance-issues) for better insight into performance anomalies
- [monitor the state of your pods](#review-pods-in-the-live-containers-view) with Datadog's Live Container view
- [observe network traffic](#monitor-network-traffic-across-cilium-managed-infrastructure) with Datadog network performance and DNS monitoring

 
## Enable Datadog's Cilium integration
You can forward Cilium's metrics and logs to Datadog using the Datadog Agent, which can either be deployed directly onto the [physical or virtual hosts][host-install] supporting your Cilium-managed clusters, or as part of the Kubernetes manifests that manage your [containerized environment][k8s-install]. In this section, we'll look at enabling the Agent's Cilium integration via Kubernetes manifests. 

Datadog provides [Autodiscovery templates][autodiscovery-docs] that you can incorporate into your manifests, allowing the Agent to automatically identify Cilium services running in each of your {{< tooltip "clusters" "top" "kubernetes" >}}. These templates simplify the process for enabling the Cilium integration across your containerized environment so you do not have to individually configure hosts.

The manifest snippet below configures the Datadog Agent to leverage its built-in [OpenMetrics check][om-docs] in order to scrape metrics from [Prometheus endpoints][prometheus-setup] for Cilium's operator and agent: 

{{<code-snippet lang="yaml" filename="pod_annotation.yaml" wrap="false" >}}
apiVersion: v1
kind: Pod
# (...)
metadata:
  name: 'cilium-pod'
  annotations:
    ad.datadoghq.com/cilium_agent.check_names: '["cilium"]'
    ad.datadoghq.com/cilium_agent.init_configs: '[{...}]'
    ad.datadoghq.com/cilium_agent.logs: |
[ 
        {
          "source": "cilium-agent",
          "service": "cilium-agent"
        }
      ]
    ad.datadoghq.com/cilium_agent.instances: |
      [
        {
          "agent_endpoint": "http://%%host%%:9090/metrics",
          "use_openmetrics": "true"
        }
      ]

    # (...)
    ad.datadoghq.com/cilium_operator.check_names: '["cilium"]'
    ad.datadoghq.com/cilium_operator.init_configs: '[{...}]'
    ad.datadoghq.com/cilium_operator.logs: |
[ 
        {
          "source": "cilium-operator",
          "service": "cilium-operator"
        }
      ]
    ad.datadoghq.com/cilium_operator.instances: |
      [
        {
          "operator_endpoint": "http://%%host%%:6942/metrics",
          "use_openmetrics": "true"
        }
      ]
spec:
  containers:
    - name: 'cilium_agent'
    # (...)
    - name: 'cilium_operator'
# (...)
{{</code-snippet>}}

In addition to enabling metric and log collection, this YAML file configures `source` and `service` tags for Cilium data. Tags create a link between metrics and logs and enable you to pivot between [dashboards](#visualize-cilium-metrics-and-clusters), [log analytics](#analyze-logs-for-network-and-performance-issues), and [network maps](#monitor-network-traffic-across-cilium-managed-infrastructure) for easier troubleshooting. Once you deploy the manifest for your clusters, the Datadog Agent will automatically collect Cilium data and forward it to the Datadog platform.

## Visualize Cilium metrics and clusters
You can view all of the Cilium metrics collected by the Agent in the [integration's dashboard][dashboard-link], which provides a high-level overview of the state of your network, policies, and Cilium resources. For example, you can review the total number of deployed endpoints and unreachable nodes in your environment. You can also clone the integration dashboard and customize it to fit your needs. The example dashboard below includes log and event streams for Cilium's operator and agent, enabling you to compare Cilium-generated events, such as a sudden increase in errors, with relevant metrics.

 {{< img src="cilium-datadog-dashboard_edited.png" alt="Datadog's built-in Cilium dashboard" border="true" popup="true">}} 

The dashboard also enables you to monitor agent, operator, and Hubble metrics for historical trends in performance, enhancing Cilium's built-in monitoring capabilities. Metric trends can surface anomalies in both your network and Cilium resources so you can resolve any issues before they become more serious. For example, the screenshot below shows a sudden spike in the number of inbound [packets][packets-docs] that were dropped (i.e., drop_count_total) due to a stale destination IP address.

{{< img src="cilium-datadog-dropped-packets.png" alt="Cilium dashboard widget for dropped packets" border="true" popup="true">}} 

An uptick in dropped packets can occur when the Cilium operator fails to release an IP address from a deleted {{< tooltip "pod" "top" "kubernetes" >}}, causing the Cilium agent to route traffic to an endpoint that no longer exists. You can troubleshoot further by reviewing your logs, which provide more details about the state of your Kubernetes clusters and network.

It's important to note that Cilium provides the option to replace the IP address of a deleted pod with an [unreachable route](https://isovalent.com/blog/post/cilium-release-112/#send-icmp-unreachable). This capability ensures that services that communicate with the affected pod are notified that its IP address is no longer available, giving you more visibility into the state of your network.

## Analyze Cilium logs for network and performance issues
Datadog's [Log Explorer][log-docs] enables you to view, filter, and search through all of your infrastructure logs, including those generated by Cilium's operator and agent. But large Kubernetes environments can generate a significant volume of logs at any given time, so it can be difficult to sift through that data in order to identify the root cause of an issue. Datadog gives you the ability to quickly identify trends in Cilium log activity and surface error outliers via [custom alerts][alerts-docs]. In the example setup below, Datadog's anomaly alert will notify you of any unusual spikes in the number of unreachable {{< tooltip "nodes" "top" "kubernetes" >}} across Kubernetes services.


{{< img src="cilium-datadog-alert.png" alt="Anamoly alert for Cilium unreachable nodes" border="true" popup="true">}} 


This kind of issue can indicate that a particular node does not have a sufficient amount of disk space or memory to manage the running pods. Without adequate resources, a node will transition into the `NotReady` status, and it will start evicting running pods if it remains in this state for more than five minutes. As a next step for troubleshooting, you may need to review the status of your pods within an affected node to determine if any were terminated or failed to spin up.

## Review pods in the Live Containers view
The overall health of your network is largely dependent upon the state of your Kubernetes resources, and poorly performing clusters can limit Cilium's ability to manage their traffic. You can visualize all your Cilium-managed clusters in the [Live Containers view][live-containers-docs] and drill down to specific pods in order to get a better understanding of their performance and status. For example, you can view all pods within a particular service or application to determine if they are still running. The example screenshot below shows more details about an application pod in the `terminating` status, which indicates that its containers are not running as expected. The status for each of the pod's containers show that they were either intentionally deleted (terminated) or failed to spin up properly (exited), which would affect Cilium's ability to route traffic to them. 

{{< img src="cilium-datadog-containers_edited.png" alt="Review Cilium pods with Datadog's Live Container view" border="true" popup="true">}} 

This view also includes the pod's YAML configuration to help you determine if the problem is the result of a misconfiguration in your cluster (i.e., insufficient resource allocation for the Cilium agent to run alongside your pod's containerized workloads).

## Monitor network traffic across Cilium-managed infrastructure
In addition to monitoring the performance of your Cilium-managed clusters, you can also view network traffic as it flows through your Kubernetes environment with Datadog [Network Performance Monitoring][npm-docs] and [DNS monitoring][dns-docs]. These tools are available as soon as you deploy the Datadog Agent to your Kubernetes clusters and [enable the option][npm-setup] in your Helm chart or manifest. NPM and DNS monitoring extend Hubble's capabilities by giving you more visibility into the performance of your network and its underlying infrastructure. You can not only ensure that your policies are working as expected but also easily trace the cause of any connectivity issues back to their source. 

For example, you can use the network map to confirm that endpoints are able to communicate with each other after updating a DNS domain in one of your [L7 policies][p1-policies]. Datadog can automatically highlight which endpoints managed by a particular policy have the highest volume of DNS-related issues, as seen below.

{{< img src="cilium-datadog-network-map-edited.png" alt="View Cilium traffic with Datadog's network map" border="true" popup="true">}} 

DNS monitoring can help you troubleshoot further by providing more details about the different types of DNS errors affecting a particular pod. The example screenshot below shows an increase in the number of NXDOMAIN errors across several DNS queries, indicating that the affected pod (`tina`) is attempting to communicate with domains that may not exist.

{{< img src="cilium-datadog-dns_edited.png" alt="View Cilium DNS queries with Datadog NPM" border="true" popup="true">}} 

NXDOMAIN errors are often the result of simple misconfigurations in your network policies. If your policies are correct, however, caching could be the culprit. Cilium can leverage Kubernetes' [NodeLocal DNSCache][dns-cache-docs] feature to enable caching for certain responses, such as NXDOMAIN errors. Caching attempts to decrease latency by limiting the number of times a Kubernetes resource (e.g., pods) queries a DNS service for a domain. But in some cases, pods can cache outdated responses, triggering a DNS error for legitimate domains. Restarting the affected pod can help mitigate these kinds of issues. 

## Start monitoring Cilium with Datadog
In this post, we looked at how Datadog provides deep visibility into your Cilium environment. You can review key Cilium metrics in Datadog's integration dashboard and pivot to logs or the Live Container view for more insights into cluster performance. You can also leverage NPM and DNS monitoring to view traffic to and from pods in order to troubleshoot issues in your network. Check out our [documentation][cilium-docs] to learn more about our Cilium integration and start monitoring your Kubernetes applications today. If you don't already have a Datadog account, you can sign up for a <a href="#" class="sign-up-trigger">free 14-day trial</a>. 

[npm-docs]: https://docs.datadoghq.com/network_monitoring/performance/setup/?tab=agentlinux#cilium
[host-install]: https://docs.datadoghq.com/integrations/cilium/?tab=host#to-collect-cilium-agent-metrics-and-logs
[k8s-install]: https://docs.datadoghq.com/integrations/cilium/?tab=containerized#to-collect-cilium-agent-metrics-and-logs
[dashboard-link]: https://app.datadoghq.com/screen/integration/30295/cilium-overview
[packets-docs]: https://www.cloudflare.com/learning/network-layer/what-is-a-packet/
[autodiscovery-docs]: https://docs.datadoghq.com/getting_started/agent/autodiscovery/?tab=docker#overview
[prometheus-install]: https://docs.datadoghq.com/integrations/cilium/?tab=host#installation
[cilium-docs]: https://docs.datadoghq.com/integrations/cilium/?tab=host
[npm-docs]: https://docs.datadoghq.com/network_monitoring/performance/
[dns-docs]: https://docs.datadoghq.com/network_monitoring/dns/#pagetitle
[npm-setup]: https://docs.datadoghq.com/network_monitoring/performance/setup/?tab=kubernetes#setup
[log-docs]: https://docs.datadoghq.com/logs/explorer/
[op-docs]: https://docs.datadoghq.com/integrations/guide/prometheus-host-collection/#overview
[watchdog-post]: https://www.datadoghq.com/blog/datadog-watchdog-insights-log-management/
[live-containers-docs]: https://docs.datadoghq.com/infrastructure/livecontainers/
[dns-cache-docs]: https://kubernetes.io/docs/tasks/administer-cluster/nodelocaldns/
[prometheus-setup]: https://docs.cilium.io/en/stable/operations/metrics/#installation
[alerts-docs]: https://docs.datadoghq.com/monitors/
[om-docs]: https://github.com/DataDog/integrations-core/tree/master/openmetrics
[part-1]: /blog/cilium-metrics-and-architecture/
[part-2]: /blog/monitor-cilium-and-kubernetes-performance-with-hubble
[p1-policies]: /blog/cilium-metrics-and-architecture#network-policies
[p1-cluster-metrics]: /blog/cilium-metrics-and-architecture#endpoint-health-metrics