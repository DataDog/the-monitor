# Monitor HAProxy with Datadog
_This post is part 3 of a 3-part series on HAProxy monitoring. [Part 1](http://www.datadoghq.com/blog/monitoring-haproxy-performance-metrics) evaluates the key metrics emitted by HAProxy, and [Part 2](http://www.datadoghq.com/blog/how-to-collect-haproxy-metrics) details how to collect metrics from HAProxy._ If you’ve already read [our post](http://www.datadoghq.com/blog/how-to-collect-haproxy-metrics) on accessing HAProxy metrics, you’ve seen that it’s relatively simple to run occasional spot checks using HAProxy’s built-in tools. 

To implement ongoing, [meaningful monitoring](https://www.datadoghq.com/blog/haproxy-monitoring/), however, you will need a dedicated system that allows you to store, visualize, and correlate your HAProxy metrics with the rest of your infrastructure. You also need to be alerted when any system starts to misbehave. 

In this post, we will show you how to use Datadog to capture and monitor all the key metrics identified in [Part 1](http://www.datadoghq.com/blog/monitoring-haproxy-performance-metrics) of this series, and more. 

[![Default HAProxy dashboard in Datadog](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-10-haproxy/default-screen2.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-10-haproxy/default-screen2.png) 

<center>_Built-in HAProxy dashboard in Datadog_</center>

## Integrating Datadog and HAProxy

### Verify HAProxy’s status

Before you begin, you must verify that HAProxy is set to output metrics over HTTP. To read more about enabling the HAProxy status page, refer to [Part 2](http://www.datadoghq.com/blog/how-to-collect-haproxy-metrics#Stats) of this series. Simply open a browser to the stats URL listed in `haproxy.cfg`.  
You should see something like this:

 [![HAProxy Stats Page](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-10-haproxy/haproxy-stats-page.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-10-haproxy/haproxy-stats-page.png)

### Install the Datadog Agent

The [Datadog Agent](https://github.com/DataDog/dd-agent) is open-source software that collects and reports metrics from all of your hosts so you can view, monitor, and correlate them on the Datadog platform. Installing the Agent usually requires just a single command. Installation instructions are platform-dependent and can be found [here](https://app.datadoghq.com/account/settings#agent). As soon as the Datadog Agent is up and running, you should see your host reporting basic system metrics [in your Datadog account](https://app.datadoghq.com/infrastructure). [![Reporting host in Datadog](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-10-haproxy/default-host.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-10-haproxy/default-host.png)

### Configure the Agent

Next you will need to create an HAProxy configuration file for the Agent. You can find the location of the Agent configuration directory for your OS [here](http://docs.datadoghq.com/guides/basic_agent_usage/). In that directory you will find a [sample HAProxy config file](https://github.com/DataDog/dd-agent/blob/master/conf.d/haproxy.yaml.example) named **haproxy.yaml.example**. Copy this file to **haproxy.yaml**. You must edit the file to match the _username_, _password_, and _URL_ specified in your `haproxy.cfg`.

    init_config:

    instances:
      - url: http://localhost/admin?stats
        # username: username
        # password: password

Save and close the file.

### Restart the Agent

Restart the Agent to load your new configuration. The restart command varies somewhat by platform; see the specific commands for your platform [here](http://docs.datadoghq.com/guides/basic_agent_usage/).

### Verify the configuration settings

To check that Datadog and HAProxy are properly integrated, execute the Datadog `info` command. The command for each platform is available [here](http://docs.datadoghq.com/guides/basic_agent_usage/). If the configuration is correct, you will see a section resembling the one below in the `info` output:

    Checks
    ======
    [...]

    haproxy
    -------
      - instance #0 [OK] Last run duration: 0.00831699371338
      - Collected 26 metrics & 0 events

### Turn on the integration

Finally, click the HAProxy **Install Integration** button inside your Datadog account. The button is located under the _Configuration_ tab in the [HAProxy integration settings](https://app.datadoghq.com/account/settings#integrations/haproxy). [![Install the integration](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-10-haproxy/install-integration.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-10-haproxy/install-integration.png)

### Show me the metrics!

Once the Agent begins reporting metrics, you will see a comprehensive HAProxy dashboard among [your list of available dashboards](https://app.datadoghq.com/dash/list) in Datadog. The default HAProxy dashboard, as seen at the top of this article, displays the key metrics highlighted in our [introduction to HAProxy monitoring](http://www.datadoghq.com/blog/monitoring-haproxy-performance-metrics).

You can easily create a more comprehensive dashboard to monitor your entire web stack by adding additional graphs and metrics from your other systems. For example, you might want to graph HAProxy metrics alongside metrics from your [NGINX web servers](https://www.datadoghq.com/blog/how-to-monitor-nginx-with-datadog/), or alongside host-level metrics such as memory usage on application servers.

To start building a custom dashboard, clone the default HAProxy dashboard by clicking on the gear on the upper right of the dashboard and selecting **Clone Dash**. 

![Clone dash](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-10-haproxy/clone-dash.png)

### Alerting on HAProxy metrics

Once Datadog is capturing and visualizing your metrics, you will likely want to [set up some alerts](http://docs.datadoghq.com/guides/monitoring/) to be automatically notified of potential issues. With our recently released [outlier detection](https://www.datadoghq.com/blog/introducing-outlier-detection-in-datadog/) feature, you can get alerted on the things that matter. For example. you can set an alert if a particular backend is experiencing an increase in latency while the others are operating normally. Datadog can monitor individual hosts, containers, services, processes—or virtually any combination thereof. For instance, you can monitor all of your HAProxy frontends, backends, or all hosts in a certain availability zone, or even a single metric being reported by all hosts with a specific tag.

### Conclusion

In this post we’ve walked you through integrating HAProxy with Datadog to visualize your key metrics and notify the right team whenever your infrastructure shows signs of trouble. If you’ve followed along using your own Datadog account, you should now have improved visibility into what’s happening in your environment, as well as the ability to create automated alerts tailored to your infrastructure, your usage patterns, and the metrics that are most valuable to your organization. If you don’t yet have a Datadog account, you can sign up for a [free trial](https://app.datadoghq.com/signup) and start monitoring HAProxy right away.