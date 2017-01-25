# How to monitor Elasticsearch with Datadog

*This post is part 3 of a 4-part series on monitoring Elasticsearch performance. [Part 1][part-1-link] provides an overview of Elasticsearch and its key performance metrics, [Part 2][part-2-link] explains how to collect these metrics, and [Part 4][part-4-link] describes how to solve five common Elasticsearch problems.*

If you've read [our post][part-2-link] on collecting Elasticsearch metrics, you already know that the Elasticsearch APIs are a quick way to gain a  snapshot of performance metrics at any particular moment in time. However, to truly get a grasp on performance, you need to track Elasticsearch metrics over time and monitor them in context with the rest of your infrastructure.

[![elasticsearch datadog dashboard](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-09-elasticsearch/elasticsearch-dashboard-final2.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-09-elasticsearch/elasticsearch-dashboard-final2.png)
*Datadog's out-of-the-box Elasticsearch dashboard*

This post will show you how to set up Datadog to automatically collect the key metrics discussed in [Part 1][part-1-link] of this series. We'll also show you how to set alerts and use tags to effectively monitor your clusters by focusing on the metrics that matter most to you. 

## Set up Datadog to fetch Elasticsearch metrics
Datadog's integration enables you to automatically collect, tag, and graph all of the performance metrics covered in [Part 1][part-1-link], and correlate that data with the rest of your infrastructure. 

### Install the Datadog Agent
The [Datadog Agent][agent-docs] is open source software that collects and reports metrics from each of your nodes, so you can view and monitor them in one place. Installing the Agent usually only takes a single command. View installation instructions for various platforms [here][Agent-installation]. You can also install the Agent automatically with configuration management tools like [Chef][datadog-chef-blog] or [Puppet][datadog-puppet-blog].

### Configure the Agent 
After you have installed the Agent, it's time to create your integration configuration file. In your [Agent configuration directory][agent-docs], you should see a [sample Elasticsearch config file][elastic-config-file] named `elastic.yaml.example`. Make a copy of the file in the same directory and save it as `elastic.yaml`.

Modify `elastic.yaml` with your instance URL, and set `pshard_stats` to true if you wish to collect metrics specific to your primary shards, which are prefixed with `elasticsearch.primaries`. For example, `elasticsearch.primaries.docs.count` tells you the document count across all primary shards, whereas `elasticsearch.docs.count` is the total document count across all primary **and** replica shards. In the example configuration file below, we've indicated that we want to collect primary shard metrics. We have also added a custom tag, `elasticsearch-role:data-node`, to indicate that this is a data node.

```
# elastic.yaml 

init_config:

instances:

  - url: http://localhost:9200
    # username: username
    # password: password
    # cluster_stats: false
    pshard_stats: true
    # pending_task_stats: true
    # ssl_verify: false
    # ssl_cert: /path/to/cert.pem
    # ssl_key: /path/to/cert.key
    tags:
        - 'elasticsearch-role:data-node'
```

Save your changes and verify that the integration is properly configured by restarting the Agent and [running the Datadog `info` command][agent-docs]. If everything is working properly, you should see an `elastic` section in the output, similar to the below:

```
  Checks
  ======
[...]
    elastic
    -------
      - instance #0 [OK]
      - Collected 142 metrics, 0 events & 3 service checks
```

The last step is to navigate to [Elasticsearch's integration tile][es-tile] in the Datadog App and click on the **Install Integration** button under the "Configuration" tab. Once the Agent is up and running, you should see your hosts reporting metrics in [Datadog][datadog-infrastructure], as shown below:

![elastic-datadog-infra.png](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-09-elasticsearch/pt3-1-elastic-datadog-infra.png) 

## Dig into the Elasticsearch metrics!
Once the Agent is configured on your nodes, you should see an Elasticsearch overview screenboard among your [list of available dashboards][dashboard-link]. 

Datadog's [out-of-the-box dashboard][datadog-es-dash] displays many of the key performance metrics presented in [Part 1][part-1-link] and is a great starting point to gain more visibility into your clusters. You may want to clone and customize it by adding system-level metrics from your nodes, like I/O utilization, CPU, and memory usage, as well as metrics from other elements of your infrastructure.

### Tag your metrics
In addition to any [tags][tags-docs] assigned or inherited from your nodes' other integrations (e.g. Chef `role`, AWS `availability-zone`, etc.), the Agent will automatically tag your Elasticsearch metrics with `host` and `url`. Starting in Agent 5.9.0, Datadog also tags your Elasticsearch metrics with `cluster_name` and `node_name`, which are pulled from `cluster.name` and `node.name` in the node's Elasticsearch configuration file (located in `elasticsearch/config`). (Note: If you do not provide a `cluster.name`, it will default to `elasticsearch`.)

You can also add your own custom tags in the `elastic.yaml` file, such as the node type and  environment, in order to [slice and dice your metrics][tagging-blog] and alert on them accordingly.

For example, if your cluster includes dedicated master, data, and client nodes, you may want to create an `elasticsearch-role` tag for each type of node in the `elastic.yaml` configuration file. You can then use these tags in Datadog to view and alert on metrics from only one type of node at a time. 

### Tag, you're (alerting) it
Now that you've finished tagging your nodes, you can set up smarter, targeted alerts to watch over your metrics and notify the appropriate people when issues arise. In the screenshot below, we set up an alert to [notify team members][datadog-alerts] when any data node (tagged with `elasticsearch-role:data-node` in this case) starts running out of disk space. The `elasticsearch-role` tag is quite useful for this alert—we can exclude dedicated master-eligible nodes, which don't store any data.

![es-disk-space-monitor.png](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-09-elasticsearch/pt3-2-es-disk-space-monitor.png)

Other useful alert triggers include long garbage collection times and search latency thresholds. You might also want to set up an Elasticsearch integration check in Datadog to find out if any of your master-eligible nodes have failed to connect to the Agent in the past five minutes, as shown below:

[![es-status-check-monitor.png](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-09-elasticsearch/pt3-3-es-status-check-monitor.png)

## Conclusion
In this post, we've walked through how to use Datadog to collect, visualize, and alert on your Elasticsearch metrics. If you've followed along with your Datadog account, you should now have greater visibility into the state of your clusters and be better prepared to address potential issues. The [next part in this series][part-4-link] describes how to solve five common Elasticsearch scaling and performance issues.

If you don't yet have a Datadog account, you can start monitoring Elasticsearch right away with a <a class="sign-up-trigger" href="#">free trial</a>.

[datadog-agent]: https://github.com/DataDog/dd-agent
[agent-docs]: http://docs.datadoghq.com/guides/basic_agent_usage/
[Agent-installation]: https://app.datadoghq.com/account/settings#agent
[datadog-chef-blog]: https://www.datadoghq.com/blog/monitor-chef-with-datadog/
[datadog-puppet-blog]: https://www.datadoghq.com/blog/monitor-puppet-datadog/
[elastic-config-file]: https://github.com/DataDog/dd-agent/blob/master/conf.d/elastic.yaml.example
[datadog-es-dash]: https://app.datadoghq.com/dash/integration/elasticsearch
[datadog-infrastructure]: https://app.datadoghq.com/infrastructure
[dashboard-link]: https://app.datadoghq.com/dash/list
[system-docs]: http://docs.datadoghq.com/integrations/system/
[datadog-alerts]: https://www.datadoghq.com/blog/monitoring-101-alerting/
[tagging-blog]: https://www.datadoghq.com/blog/the-power-of-tagged-metrics/
[es-tile]: https://app.datadoghq.com/account/settings#integrations/elasticsearch
[tags-docs]: http://docs.datadoghq.com/guides/tagging/
[part-1-link]: https://www.datadoghq.com/blog/monitor-elasticsearch-performance-metrics
[part-2-link]: https://www.datadoghq.com/blog/collect-elasticsearch-metrics/
[part-4-link]: https://www.datadoghq.com/blog/elasticsearch-performance-scaling-problems/
