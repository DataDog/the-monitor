# Consul monitoring tools
In [Part 1][part1], we looked at metrics and logs that can give you visibility into the health and performance of your Consul cluster. In this post, we'll show you how to access this data—and other information that can help you troubleshoot your Consul cluster—in four ways:
 
- Running [CLI and API commands](#commands-for-ondemand-overviews) to retrieve information on demand
- Configuring [sinks](#configure-telemetry-sinks-for-comprehensive-monitoring) to collect and visualize Consul metrics
- [Logging events](#get-more-visibility-with-consul-logs) from throughout your Consul cluster
- Using a browser-based UI as well as the Consul API to [monitor the health](#monitor-consul-health-checks) of nodes and services running in your cluster

 
## Commands for on-demand overviews
Consul provides a built-in CLI and API that you can use to query the most recent information about your cluster, giving you a high-level read into Consul's health and performance. And you can use the `consul debug` command to produce a rich cross-section that includes logs, benchmarks, and telemetry data, including snapshots of the metrics we introduced in [Part 1][part1].

### The `/status` endpoint and `list-peers` command
Each Consul agent runs a [local API][consul-api] and CLI that allow you to perform management tasks and retrieve data about your cluster. Both techniques can help you troubleshoot disruptions to Raft and losses of cluster availability. One Consul API endpoint, [`<CONSUL_ADDRESS>/v1/status`][consul-status-api], provides information that can help diagnose Raft-related availability issues. In addition, Consul CLI commands can help you troubleshoot losses in Raft quorum—Raft-based consensus cannot take place when the number of Consul servers has become less than [half the size of the peer set plus one][consul-raft]. 

You can send a GET request to the `<CONSUL_ADDRESS>/v1/status/leader` endpoint to return the network address of the current leader node and check whether Consul is currently leaderless:

{{< code-snippet lang="bash" >}}
curl localhost:8500/v1/status/leader
{{</ code-snippet >}}

The response is a single IP address followed by a port, such as:

{{< code-snippet lang="text" >}}
206.189.229.121:8300
{{</ code-snippet >}}

In the case of a leaderless cluster, the response will be an empty string:

{{< code-snippet lang="json" >}}
""
{{</ code-snippet >}}

You can also use the `list-peers` command to get insights into a loss of cluster quorum. Using the  following command allows you to obtain a list of IP addresses for servers within the cluster, as well as the their node names and [other information][consul-list-peers].

{{< code-snippet lang="bash" >}}
consul operator raft list-peers
{{</ code-snippet >}}

The response will resemble the following, indicating that there are three servers in the cluster, and the cluster currently has a leader (`consul-demo-server-1`).

{{< code-snippet lang="text" >}}
Node                  ID                                    Address             State     Voter  RaftProtocol
consul-demo-server-3  dba2dd26-f417-b3da-17c1-47bdc4c8a785  198.199.66.69:8300  follower  true   3
consul-demo-server-1  7cfd4df5-dd15-c191-e7db-d8128066f896  198.199.91.25:8300  leader    true   3
consul-demo-server-2  127aa843-78f5-7eb3-4b21-88c5ebeb7730  198.199.86.66:8300  follower  true   3

{{</ code-snippet >}}




### Go deep with `consul debug`
The [`consul debug`][consul-debug] CLI command monitors your Consul cluster for a configurable period of time (two minutes by default, over 30-second intervals) and writes the results to a `tar.gz` file. You can also specify [the type of information to collect][consul-debug-targets] (e.g., agent configuration details, host resources, telemetry metrics, and `DEBUG`-level logs). `consul debug` gives you a trove of health and performance information, allowing you to gather as much context as possible when you notice an issue.

The `consul debug` command will return a link to a `tar.gz` file. The unpacked directory includes a number of files. Here is an example of the format you can expect (the actual list of files will be much longer):

{{< code-snippet lang="text" wrap="false"  >}}
consul-debug-1556041302
consul-debug-1556041302/1556041302
consul-debug-1556041302/1556041302/consul.log
consul-debug-1556041302/1556041302/goroutine.prof
consul-debug-1556041302/1556041302/heap.prof
consul-debug-1556041302/1556041302/metrics.json
{{</ code-snippet >}}

Files ending in `.json` include both statistics and configuration details, depending on the file. For example, you can use the contents of **metrics.json** to get the values of Consul metrics collected during the debug interval. Files with the `.prof` extension include profiling information that you can use to visualize execution traces. And files ending in `.log` are standard [Consul logs](#get-more-visibility-with-consul-logs).

#### Metrics dumps for on-demand monitoring
As one result of `consul debug`, Consul will dump the values of metrics collected over the sampling interval to the file **metrics.json**, outputting all of the [aggregates][go-metrics-agg] available for that metric from Consul's [in-memory sink][part1-sinks]. This is useful for getting a full complement of Consul metrics at a specific moment in time. 

For example, this output shows the latency of requests to one Consul API endpoint as well as the number of Gossip messages broadcast to other nodes in the cluster. 

{{< code-snippet lang="json" wrap="false" >}}
                {
                        "Name": "consul.http.GET.v1.status.peers",
                        "Count": 1,
                        "Sum": 0.22652000188827515,
                        "Min": 0.22652000188827515,
                        "Max": 0.22652000188827515,
                        "Mean": 0.22652000188827515,
                        "Stddev": 0,
                        "Labels": {}
                },
                {
                        "Name": "consul.memberlist.gossip",
                        "Count": 70,
                        "Sum": 1.250169008038938,
                        "Min": 0.007327999919652939,
                        "Max": 0.06497199833393097,
                        "Mean": 0.017859557257699114,
                        "Stddev": 0.008475803353512407,
                        "Labels": {}
                },
{{</ code-snippet >}}

You can view a similar metrics dump by sending a GET request to the `<CONSUL_ADDRESS>/v1/agent/metrics` [endpoint][consul-metrics-endpoint] of the Consul HTTP API. Note that this output shows only the most recently collected metrics, rather than those collected during a user-specified interval.


#### Profiling Consul for fine-grained performance monitoring
As part of the `debug` command, Consul can use the Golang [`pprof` profiling package][go-pprof] to get detailed information about the performance of Consul's subsystems (e.g., Raft and Gossip). You can enable profiling by setting [`enable_debug`][consul-enable-debug] to `true` within your Consul configuration file, then [stopping and restarting Consul][consul-reload].

If you enable profiling, the `debug` command will output files ending in `.prof`, which represent profiles of heap memory usage, CPU utilization, and execution traces. These files need to be opened with the [`pprof` visualization tool][pprof-github] included in a standard [Golang installation][pprof-cmd]. After installing Golang, you can run this command to enter the interactive `pprof` console.

{{< code-snippet lang="bash" wrap="false"  >}}
go tool pprof <PATH_TO_PROF_FILE>
{{</ code-snippet >}}

You can use `pprof` to benchmark function calls within the Consul agent (or any other Golang application), allowing you to identify performance issues at a granular level. `pprof` can complement the performance metrics we introduced in [Part 1][part1], such as consul.raft.commitTime, by illustrating the source of delays within a specific operation.

As shown below, `pprof` generates an image that visualizes the order in which Consul calls various Golang functions, as well as the duration of each function call. This example shows a  profile of CPU utilization. You can generate GIF and SVG files, as well as text outputs in a variety of formats. To generate a GIF file that maps out the 15 most pivotal functions within the call tree (based on what `pprof` calls an [`entropyScore`][pprof-entropy-score]),  enter this command in the `pprof` console: 

{{< code-snippet lang="text" wrap="false" >}}
gif 15
{{</ code-snippet >}}

This command will produce an image similar to the following.

{{< img src="profile-example.gif" border="true" popup="true" >}}

You can also [filter][pprof-focus] nodes (i.e., functions) in the image to only those matching a regular expression, making it easier to see into Consul subsystems (Raft, Gossip, the KV store, etc.) that metrics have shown to be underperforming.

The `consul debug` command provides detailed information that is useful for investigating issues. However, because `consul debug` collects data for a limited period (beginning when you run the command), it's not possible to see trends within their full historical context or to gather performance data about an event that has already occurred. 

    
## Configure telemetry sinks for comprehensive monitoring
While ad-hoc commands can provide helpful information about your Consul cluster, they don't provide comprehensive visibility into all of the metrics we introduced in [Part 1][part1]. You can configure a metrics sink to retain your Consul metrics beyond the default [one-minute window][consul-telemetry]. By retaining metrics for a longer period, you can track your metrics over time, compare them to metrics and logs from other parts of your infrastructure, and get more comprehensive visibility into your Consul cluster.

Consul uses the [`go-metrics` library][go-metrics-github] to expose metrics, and gives you flexibility in choosing where to send them, destinations called **metrics sinks**. You can then use your sink of choice to filter metrics and construct visualizations. In [Part 3][part3], we'll show you how to configure a Consul metrics sink to visualize all of your metrics in Datadog alongside logs and request traces for alerting and troubleshooting.

You can specify a metrics sink in the `telemetry` section of your Consul agent configuration, whether by configuring each agent separately or using a configuration management solution. Different key/value pairs are required to point your metrics toward different sinks—for example, you would use `statsd_address` to indicate the address of a local StatsD server as shown in the following JSON snippet: 

{{< code-snippet lang="json" wrap="false">}}
{
  "telemetry": {
    "statsd_address": "127.0.0.1:8125"
}
{{</ code-snippet >}}

You will need to stop and restart each Consul agent to load the new `telemetry` section. Once you do, each agent will report metrics to your new sink, using that sink's functionality to aggregate and retain metrics. In the [case of StatsD][go-metrics-statsd], for example, the sink will push new metrics to a queue, then [flush the queue][go-metrics-statsd-flush] via a UDP stream to a user-specified StatsD server every [100 ms][go-metrics-flushinterval].

## Get more visibility with Consul logs
Consul and its dependencies (Serf, Raft, and Memberlist) log state changes and events, and tracking these logs can expose trends that Consul does not surface through metrics. Consul does not provide metrics to track failed remote procedure calls across datacenters, for example, but it does record each failure [in a log][part1-communication-metrics]. 

Logs include a timestamp and the name of the package from which they originate, making it easier to localize issues. The example below illustrates the types of logs that Consul might generate when booting server nodes for the first time:

{{< code-snippet lang="text" wrap="false"  >}}
2019/04/26 17:55:22 [INFO] consul: Found expected number of peers, attempting bootstrap: 67.205.153.246:8300,67.205.157.176:8300,142.93.118.146:8300
2019/04/26 17:55:22 [INFO] consul: Adding LAN server consul-demo-server-2 (Addr: tcp/67.205.157.176:8300) (DC: dc1)
2019/04/26 17:55:22 [INFO] serf: EventMemberJoin: consul-demo-server-2.dc1 67.205.157.176
2019/04/26 17:55:22 [INFO] serf: EventMemberJoin: consul-demo-server-3.dc1 67.205.153.246
2019/04/26 17:55:22 [INFO] consul: Handled member-join event for server "consul-demo-server-2.dc1" in area "wan"
2019/04/26 17:55:22 [INFO] consul: Handled member-join event for server "consul-demo-server-3.dc1" in area "wan"
2019/04/26 17:55:28 [WARN] raft: Heartbeat timeout from "" reached, starting election
2019/04/26 17:55:28 [INFO] raft: Node at 142.93.118.146:8300 [Candidate] entering Candidate state in term 2
2019/04/26 17:55:28 [INFO] raft: Election won. Tally: 2
2019/04/26 17:55:28 [INFO] raft: Node at 142.93.118.146:8300 [Leader] entering Leader state
{{</ code-snippet >}}

Some logs include dynamically updated fields. For example, the Consul agent automatically logs an error when it [fails to set up a watch][consul-watch-code] (an [automatic handler][consul-watch] for changes in Raft-managed data), using the `%v` format (from [Go's `fmt` package][go-fmt]) to print the [default format][go-printf] of the `err` message passed to it (e.g., an error surfaced within user-defined script used as a watch handler).

{{< code-snippet lang="go" wrap="true"  >}}
logger.Printf("[ERR] agent: Failed to setup watch: %v", err)
{{</ code-snippet >}}

Consul logs contain three standard fields (timestamp, level, and package name), and a message that communicates specific details about an event. Because each message has its own format, with different values that are dynamically updated with every log event, it can be challenging to aggregate Consul logs. We'll show you one technique for processing and analyzing your logs in the [next part][part3] of this series.

Consul will [write logs to STDOUT][consul-log-stdout] by default. If Consul is running in the background, you can use the [`consul monitor`][consul-monitor] CLI command to stream logs to STDOUT until the command exits. This command automatically displays logs at a minimum severity of `INFO`; you can use the `-log-level` flag to revise this if needed:

{{< code-snippet lang="bash" wrap="true" >}}
consul monitor -log-level trace
{{</ code-snippet >}}

This command will output logs to `STDOUT` at all log levels (since `TRACE` is the lowest).

Writing your logs [to a file][log-file] makes it possible to retain your logs and ship them to a centralized platform so you can search, analyze, and alert on them. To log to a file, you can use the [`log_file`][consul-logs-file] key within a Consul configuration file, or the `-log-file` option when running the Consul agent on the command line, for example:

{{< code-snippet lang="bash" wrap="true" >}}
consul agent -log-file /var/log/consul/consul.log
{{</ code-snippet >}}

## Monitor Consul health checks

Consul can provide visibility into the status of nodes and services in your cluster. Consul runs [health checks][consul-health-checks] to monitor node and service availability based on user-defined techniques such as custom scripts and HTTP requests to a certain endpoint. You can view summaries of these checks with the Consul browser UI and HTTP API.

### Convenient visibility with the browser UI
The Consul agent ships with a browser-based [graphical user interface][consul-ui] that provides a high-level overview of services and nodes running in your cluster, and allows you to edit cluster metadata and configuration details within the key-value store. You can use the UI to navigate between lists of services, nodes, and entries in the KV store, as well as [intentions][consul-intentions] (rules regarding which services can connect to one another), and [Access Control Lists][consul-acls], which restrict management tasks to certain Consul agents. The UI also has some benefit for monitoring, giving you a synopsis of your cluster's status, including the results of health checks on Consul nodes and services ("Passing," "Warning," or "Critical"), and allowing you to discover issues quickly. You have the option of accessing each view separately for different datacenters.

For example, this UI view tells us the names and IP addresses of each node in our cluster, and shows us that all nodes are healthy.


{{< img src="ui.png" popup="true" border="true" >}} 


To enable the UI, add the `-ui` option when starting a Consul agent from the command line:

{{< code-snippet lang="bash" wrap="false"  >}}
consul agent -ui
{{</ code-snippet >}}

As an alternative, you can add the pair `"ui": true` to your [Consul configuration][consul-config-files] to enable the UI every time Consul starts. 
 
Once an agent is running, you can access the UI from the same address as the HTTP API, `<CONSUL_AGENT_HOST>:<API_PORT>/ui`. Note that the server for the UI, DNS, and HTTP APIs listens on loopback (127.0.0.1) and port 8500 by default. You can specify another host address with the [`client_addr`][consul-client-addr] key in a Consul configuration file, which allows for multiple IP addresses separated by spaces (e.g., `127.0.0.1 <PUBLIC_IP>`).

Note that the UI is less suited for monitoring the internal health and performance of Consul itself than for tracking the status of nodes and services deployed within your Consul cluster.

### API endpoints
You can also access summaries of Consul health checks by using the HTTP API. You'll find the same sort of information you can view with the UI, but with the machine readability of JSON.

To see the status of Consul health checks, you can query the `/health` [API endpoint][consul-health-api], which allows you to list health checks by node and service. You can filter by parameters such as the name, service name, and status of the check. 

You can also interact with the checks registered with a particular Consul agent directly (rather than through the catalog) by using the [`/agent/checks`][consul-agent-checks] endpoint, which returns similar information as the `/health` endpoint but allows you to register, deregister, and update health checks.



## Many machines, one monitoring platform
In this post, we've shown you a number of built-in techniques for getting visibility into your Consul cluster. Consul exposes a variety of data from all of its components—to make the data meaningful, you'll want a way to move easily between logs and metrics, both from Consul and from the applications running within your cluster. In [Part 3][part3], we'll show you how to use Datadog to get full visibility into your Consul environment.


## Acknowledgment
_We wish to thank our friends at HashiCorp for their technical review of an early draft of this post._
<!--links-->

[consul-acls]: https://learn.hashicorp.com/consul/security-networking/production-acls
[consul-agent-checks]: https://www.consul.io/api/agent/check.html
[consul-api]: https://www.consul.io/api/index.html
[consul-catalog-api]: https://www.consul.io/api/catalog.html
[consul-catalog-cli]: https://www.consul.io/docs/commands/catalog.html
[consul-client-addr]: https://www.consul.io/docs/agent/options.html#client_addr
[consul-config-files]: https://www.consul.io/docs/agent/options.html#configuration-files
[consul-debug]: https://www.consul.io/docs/commands/debug.html
[consul-debug-targets]: https://www.consul.io/docs/commands/debug.html#capture-targets
[consul-enable-debug]: https://www.consul.io/docs/agent/options.html#enable_debug
[consul-health-api]: https://www.consul.io/api/health.html
[consul-health-checks]: https://www.consul.io/docs/agent/checks.html
[consul-info]: https://www.consul.io/docs/commands/info.html
[consul-intentions]: https://www.consul.io/docs/connect/intentions.html
[consul-list-datacenters]: https://www.consul.io/api/catalog.html#list-datacenters
[consul-list-peers]: https://www.consul.io/docs/commands/operator/raft.html#list-peers
[consul-logs-file]: https://www.consul.io/docs/agent/options.html#log_file
[consul-metrics-endpoint]:https://www.consul.io/api/agent.html#view-metrics
[consul-monitor]: https://www.consul.io/docs/commands/monitor.html
[consul-raft]: https://www.consul.io/docs/internals/consensus.html#raft-protocol-overview
[consul-reload]: https://www.consul.io/docs/commands/reload.html
[consul-reload-config]: https://www.consul.io/docs/agent/options.html#reloadable-configuration
[consul-telemetry]: https://www.consul.io/docs/agent/telemetry.html
[consul-log-stdout]: https://support.hashicorp.com/hc/en-us/articles/115015668287-Where-are-my-Consul-logs-and-how-do-I-access-them
[consul-secure]: https://www.consul.io/docs/internals/security.html#secure-configuration
[consul-status-api]: https://www.consul.io/api/status.html
[consul-ui]: https://learn.hashicorp.com/consul/getting-started/ui
[consul-watch]: https://www.consul.io/docs/agent/watches.html
[consul-watch-code]: https://github.com/hashicorp/consul/blob/b5abf61963c7b0bdb674602bfb64051f8e23ddb1/agent/watch_handler.go#L130
[go-fmt]: https://golang.org/pkg/fmt/
[go-log]: https://golang.org/pkg/log/
[go-metrics-agg]: https://godoc.org/github.com/armon/go-metrics#AggregateSample
[go-metrics-flushinterval]: https://github.com/armon/go-metrics/blob/58588f401c2cc130a7308a52ca3bc6c0a76db04b/statsite.go#L17
[go-metrics-github]: https://github.com/armon/go-metrics
[go-metrics-inmem]: https://godoc.org/github.com/armon/go-metrics#InmemSink
[go-metrics-statsd]: https://godoc.org/github.com/armon/go-metrics#StatsdSink
[go-metrics-statsd-flush]: https://github.com/armon/go-metrics/blob/master/statsd.go#L115
[go-pprof]: https://golang.org/pkg/net/http/pprof/
[go-printf]: https://golang.org/pkg/fmt/#hdr-Printing
[log-file]: https://www.datadoghq.com/blog/go-logging/#write-your-logs-to-a-file
[memberlist-godoc]: https://godoc.org/github.com/hashicorp/consul/vendor/github.com/hashicorp/memberlist
[part1]: /blog/consul-metrics/
[part1-communication-metrics]: /blog/consul-metrics/#communication-metrics
[part1-sinks]: /blog/consul-metrics/#how-consul-reports-metrics
[part3]: /blog/consul-datadog/
[pprof-cmd]: https://golang.org/cmd/pprof/
[pprof-entropy-score]: https://github.com/google/pprof/blob/1647c5607f3828cf18db05be65fd22ac5a3c1bcc/internal/graph/graph.go#L1038
[pprof-focus]: https://github.com/google/pprof/blob/master/doc/README.md#options
[pprof-github]: https://github.com/google/pprof

