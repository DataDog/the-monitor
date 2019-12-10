---
blog/category: ["series datadog"]
blog/tag: ["Apache", "http server", "web server", "performance"]
date: 2017-03-16T00:00:03Z
description: "Learn how to use Datadog to monitor Apache web server metrics."
draft: false
toc_cta_text: "Start monitoring Apache"
email: emily.chang@datadoghq.com
featured: false
image: apache-hero3.png
meta_title: null
preview_image: apache-hero3.png
scribbler: "Emily Chang"
scribbler_image: img-0791.jpg
slug: monitor-apache-web-server-datadog
sub_featured: true
title: "How to monitor Apache web server with Datadog"
twitter_handle: 
---

*This post is the last of a 3-part series about monitoring Apache performance. [Part 1][part-1] provides an overview of the Apache web server and its key performance metrics, and [part 2][part-2] describes how to collect and monitor Apache metrics using native and open source tools.* 

If you've read [Part 2][part-2] of this series, you know that there are a variety of ways to collect metrics from your Apache web servers, both natively and using open source tools. Although these methods are useful for checking Apache metrics in real time, they only provide one piece of the puzzle, since they do not readily reveal long-term trends and patterns, nor do they offer any context about the rest of your infrastructure and applications. 

In this post we'll show you how to integrate Datadog with Apache to automatically collect most of the metrics discussed in [Part 1][part-1] of this series, and visualize them in a dashboard like the one shown below. Datadog allows you to zoom out to see long-term performance trends, or to zoom in to see your real-time and historical metrics at full granularity. And with more than 150 integrations with popular infrastructure technologies, plus [end-to-end request tracing][apm], Datadog enables you to monitor Apache in context with the rest of your stack.

{{< img src="apache-final-screen.png" alt="Apache default dashboard in Datadog" popup="true" >}}

We will also show you how to [use FluentD to send Apache access log data to Datadog](#how-to-send-apache-logs-to-datadog-using-fluentd), and [set up useful alerts](#set-up-apache-alerts) to get informed of performance issues in real time.  

## Set up Datadog's Apache integration
### 1. Configure Apache to send metrics 
In order to collect metrics from Apache, you need to enable the status module and make sure that ExtendedStatus is on, as outlined in [Part 2][part-2-enablemodstatus].  

### 2. Install the Datadog Agent
The [Datadog Agent][agent-docs] is open source software that collects metrics and events from your hosts and forwards them to Datadog so that you can visualize, analyze, and alert on performance data, all in one place. Installing the Agent usually just takes a single command; see instructions for various platforms [here][agent-install-doc]. If you prefer, you can also install the Agent using tools like [Chef][chef-blog], [Puppet][puppet-blog], or [Ansible][ansible-blog].

### 3. Update the Agent configuration file
Once you've installed the Agent, you will need to create an Apache configuration file so that the Agent will know where to fetch your Apache metrics. Find the location of your example configuration file (`apache.yaml.example`) [here][agent-docs], which varies from platform to platform.  

Make a copy of the [example file][apache-config-example] and save it as `apache.yaml`. Update `apache.yaml` with the mod_status URL of your Apache instance (replacing "localhost" with the IP/hostname of your Apache instance, if you installed the Agent on a different host). The example below shows the configuration file for a user who is running Apache on the same host as the Agent. 

```
init_config:

instances:
  - apache_status_url: http://localhost/server-status?auto
    # apache_user: example_user
    # apache_password: example_password
    # tags:
    #   - optional_tag

    # The (optional) disable_ssl_validation will instruct the check
    # to skip the validation of the SSL certificate of the URL being tested.
    # Defaults to false, set to true if you want to disable SSL certificate validation.
    #
    # disable_ssl_validation: false

    # The (optional) connect_timeout will override the default value, and fail
    # the check if the time to establish the (TCP) connection exceeds the
    # connect_timeout value (in seconds)
    # connect_timeout: 5
    
    # The (optional) receive_timeout will override the default value, and fail
    # the check if the time to receive the server status from the Apache server
    # exceeds the receive_timeout value (in seconds)
    # receive_timeout: 15
```

If your Apache instance is not being accessed by localhost, make sure to enable access to your Agent's IP address in your [Apache status module's configuration file][part-2-config-file], and replace "localhost" in the URL with the IP of your Apache server. You also have the option to add a user and password if you configured one (see [Part 2][part-2] for details on how to only allow authenticated users to access the mod_status page).  

Save your changes and exit the file. [Restart the Agent and run the `info` command][agent-docs] to verify that the Apache check is configured correctly. If everything is working, you should see a snippet like this in the info output:

```
    apache
    ------
      - instance #0 [OK]
      - Collected 12 metrics, 0 events & 1 service check
```

### 4. Enable the Apache integration in the Datadog App
To start seeing your Apache metrics in Datadog, navigate to the Integrations page of the Datadog App, and click on the [Apache integration tile][apache-tile]. In the Configuration tab, click on "Install Integration". You should now be able to see your host reporting metrics in Datadog's infrastructure list, as shown below:

{{< img src="infra-apache-list.png" alt="Apache server in Datadog app" popup="true" >}}

## Customize your Apache dashboard
An [Apache dashboard][apache-datadog-dashboard] should now appear in your list of integration dashboards. This out-of-the-box dashboard displays most of the key metrics covered in [Part 1][part-1] of this series, along with helpful pre-computed metrics that make it easier to understand real-time usage and performance. For example, the metrics `apache.net.hits` and `apache.net.bytes` are taken directly from mod_status and represent ever-increasing counters of the total number of requests and bytes that have been served over the lifetime of the server. The Datadog Agent provides these metrics, but also provides per-second rates (`apache.net.request_per_s` and `apache.net.bytes_per_s`), which are calculated by averaging the change in the number of requests and bytes served over each ~15–20 second collection period. 

(Similarly, you should favor the real-time CPU metrics reported by the Datadog Agent over the CPU metrics collected from Apache's mod\_status page, which are aggregated over the lifetime of the server.)

{{< img src="clone-apache-dash.png" alt="Cloning your Apache screenboard in Datadog" popup="true" >}}

You can clone this dashboard and customize it with system-level metrics that are not available from Apache's status module, like memory usage and network traffic metrics, to add more context to your request throughput graphs. And because you can mix and match metrics from any source in Datadog, you can add metrics from databases, load balancers, or other services you are running alongside Apache, such as [Tomcat][tomcat-blog] or [NGINX][nginx-blog].

## How to send Apache logs to Datadog using FluentD 
As mentioned in [Part 1][part-1], certain metrics (including error rates and request latency) are only available in [Apache's access logs][apache-access-log]. Many log parsing and aggregation tools can help you collect, filter, and analyze your Apache logs to garner useful insights. FluentD is one such open source tool that can help you forward Apache log data to your monitoring platform. 

In this section, we will walk through an example of setting up the [DogStatsD FluentD plugin][fluentd-dogstatsd] to send Apache error metrics to Datadog.

### Install FluentD on your Apache server
If you're not already using FluentD, follow the [pre-installation steps][fluentd-preinstall] and [install FluentD][fluentd-install] on your Apache server. 

### Install the plugin
The FluentD DogStatsD plugin is available as a Ruby gem. Install it:

```
gem install fluent-plugin-dogstatsd
```

### Update the FluentD config file in 3 steps
Now it's time to update the [FluentD configuration file][fluentd-config]. Make sure to save a backup copy of this file in case you want to revert back to it at some point. To learn more about FluentD's configuration file syntax, consult the full [documentation here][fluentd-config]. 

In our basic example, we will add three directives to the configuration file: source, filter, and match. Make sure to add these three directives in the order stated below (e.g. do not place the match directive before the source directive).

#### 1. Define the source as your Apache access log
We need to add a **source** that uses the [in_tail input plugin][fluentd-tail] (which is already included in FluentD) to tail your access log.

In this example, we will assume that you are using the combined LogFormat:

```
LogFormat "%h %l %u %t \"%r\" %>s %O \"%{Referer}i\" \"%{User-Agent}i\" combined
```

This also assumes that you have specified in your Apache config that you want to use this LogFormat ([consult Part 2][part-2] for more detailed instructions).

In your `td-agent.conf` file, you should see a section that starts with `## Source descriptions`. [Consult the docs][fluentd-config-docs] if you need help locating the file. This is where we will add in information about the source we want to parse: the Apache access log. FluentD's in_tail plugin has a [built-in Apache parsing format][fluentd-apache2] that automatically parses the combined log format, called `apache2`. 

Add this snippet to your config file somewhere in the source descriptions section:

```
<source>
  @type tail
  format apache2
  time_format %d/%b/%Y:%H:%M:%S %z
  path /var/log/apache2/access.log
  tag apache.status
</source>
```

This snippet continuously tails the Apache access log, parses each line, and adds the FluentD tag "apache.status". You can customize the name of this tag as you wish.  

Remember to replace the path with the correct location of your access log. Now it's time to filter/reformat the information before forwarding it to Datadog, by using one of [FluentD's filter plugins][fluentd-filter].

#### 2. Filter the access log info
The [record-transformer **filter** plugin][fluentd-record-transformer] (also already included in FluentD) helps transform Apache access log data into a format that is suitable for ingesting into Datadog.

You can use this filter plugin to update each record with a key that will appear as your Datadog metric name once it is forwarded to Datadog.

Make sure to specify the same tag that you specified in the source directive (`apache.status`) in the previous step.

```
<filter apache.status>
  @type record_transformer
  <record>
    key apache.status.${record["code"]}
  </record>
</filter>
```

This section adds a key field called `apache.status.${record["code"]}`, to each record that is tagged with "apache.status". The value of `${record["code"]}` is equal to the request's final HTTP status code (the [combined log format's `%>s` variable][apache-log-vars]).  

#### 3. Match the filtered info to the DogStatsD plugin.
Now it's time to add a **match** section to tell FluentD where to send our filtered Apache log data. The section below shows an example of how to direct FluentD to send the data to the [DogStatsD output plugin][fluentd-dogstatsd].

```
<match apache.status>
  @type dogstatsd
  host localhost
  port 8125
  use_tag_as_key false
  flat_tags false
  metric_type increment
  value_key Value
</match>
```
Each Apache request will increment the **apache.status.${record["code"]}** metric and send it to DogStatsD via port 8125, which will forward it to Datadog. You can learn more about the available configuration settings [here][fluentd-dogstatsd].

For example, any request that results in a 502 status code will increment a counter for the `apache.status.502` metric in Datadog.

### Restart FluentD with the new configuration file
Once you've saved your changes, exit the configuration file and [start the FluentD daemon][fluentd-launch-docs]. To indicate which configuration file to use, [run the following command][fluentd-startup-docs] from the directory that contains your FluentD configuration file (replacing `td-agent.conf` with the name of your config file): 

    fluentd -c td-agent.conf

Within minutes, you should start to see metrics appearing under the name `apache.status.<HTTP_RESPONSE_CODE>` (e.g. `apache.status.200`, `apache.status.404`, etc.). 

Just like any other metric in Datadog, you can use these metrics to set alerts or to create rich, custom dashboards. For example, you can find out which Apache servers are generating the most 5xx error codes, and correlate their performance with metrics from other parts of your infrastructure. 

In the screenshot below, we've included Apache HTTP error counts on the same dashboard as system-level information (e.g. CPU and network traffic) from our Apache servers.

{{< img src="apache-timeboard-fluentd.png" alt="Use FluentD and Datadog to graph HTTP status code error count per Apache host" popup="true" >}}

### A note about other Apache log formats
According to the [FluentD in_tail plugin documentation][apache-fluentd-format-docs], specifying the `apache2` log format is the equivalent of writing out this configuration: 

```
/^(?<host>[^ ]*) [^ ]* (?<user>[^ ]*) \[(?<time>[^\]]*)\] "(?<method>\S+)(?: +(?<path>[^ ]*) +\S*)?" (?<code>[^ ]*) (?<size>[^ ]*)(?: "(?<referer>[^\"]*)" "(?<agent>[^\"]*)")?$/
```

In the configuration above, the in_tail plugin parses each log line to generate a FluentD record with the following fields: host, user, time, method, path, code, size, referer, and agent.

If you are using a custom LogFormat, you can write your own regular expression to parse information from your access log. [Fluentular][fluentular] is a great tool for testing out your FluentD regular expression.

### Do more with FluentD + Datadog
We just covered one example of the many ways you could use FluentD to send Apache access log metrics to Datadog. If you configured Apache to log the processing time (log variable `%D`) of each request (see [Part 2][part-2] for instructions), you might also want to use the DogStatsD output plugin to send that value to Datadog as a [histogram metric][dogstatsd-guide] (average, median, min, max, and 95th percentile). 

Apache's `%D` variable logs the processing time in microseconds, but you can use Datadog's graph editor to convert the value to milliseconds when graphing the metric, as shown below.

{{< img src="apache-responsetime.png" alt="Datadog graph Apache request processing time in milliseconds" popup="true" >}}

You can also experiment with other output plugins that forward metrics and events to Datadog, such as the [dd][dd-fluentd-plugin] and [datadog_event][dd-event-plugin] plugins.  

## Create Apache alerts
Next, we'll walk through two examples of alerts that can notify you when important issues occur on your Apache servers. 

### Status check
A status check can help you find out when one or more of your Apache servers is down—ideally before you hear about it from your users. 

The check automatically tries to connect to your Apache servers, and notifies you if it fails _x_ consecutive times. Setting up a check is easy; within the Datadog app, navigate to [Monitors > New Monitor > Integration][integration-monitor] and click on the Apache tile. 

Below, we set up the alert to notify us each time any particular Apache host fails the check two consecutive times. The alert will resolve on its own once the Agent is able to connect successfully.

{{< img src="apache-alert-check-datadog.png" alt="Datadog alert to detect when Apache host fails" popup="true" >}}

### Threshold alert
You can also create alerts to get notified when metrics cross fixed or [dynamic thresholds][anomalies]. If load testing has shown you that your servers' performance starts to degrade when they process more than a certain number of requests per second, you can set an alert to find out when you're nearing that threshold, as shown below.

{{< img src="create-apache-monitor.png" alt="Datadog alert to detect high number of Apache hits" popup="true" >}}

If you get notified about this alert, you may need to scale up or out to handle the increased load, with some guidance from the Apache [documentation's performance tuning tips][performance-tuning-docs].

## Start the monitoring process
You've now seen a few of the ways you can use Datadog to collect, visualize, and alert on Apache metrics and logs. In just a few minutes you can start capturing Apache metrics, building custom dashboards, and setting up alerts. Because Datadog also integrates with 150+ other services and tools, you can quickly create a comprehensive view of your servers along with all the other components of your stack. 

If you don't yet have a Datadog account, start monitoring Apache today with a <a class="sign-up-trigger" href="#">free trial</a>.

[apm]: /blog/announcing-apm/
[agent-docs]: http://docs.datadoghq.com/guides/basic_agent_usage/
[agent-install-doc]: https://app.datadoghq.com/account/settings#agent
[chef-blog]: /blog/monitor-chef-with-datadog/
[puppet-blog]: /blog/monitor-puppet-datadog/
[ansible-blog]: /blog/ansible-datadog-monitor-your-automation-automate-your-monitoring/
[part-1]: /blog/monitoring-apache-web-server-performance/
[part-2]: /blog/collect-apache-performance-metrics
[apache-agent-conf]: https://github.com/DataDog/integrations-core/blob/master/apache/conf.yaml.example
[part-2-enablemodstatus]: /blog/collect-apache-performance-metrics/#apaches-status-module
[apache-tile]: https://app.datadoghq.com/account/settings#integrations/apache
[apache-config-example]: https://github.com/DataDog/integrations-core/blob/master/apache/conf.yaml.example
[tomcat-blog]: https://www.datadoghq.com/blog/monitor-tomcat-metrics/
[nginx-blog]: https://www.datadoghq.com/blog/how-to-monitor-nginx/
[performance-tuning-docs]: http://httpd.apache.org/docs/2.4/misc/perf-tuning.html
[apache-access-log]: http://httpd.apache.org/docs/current/logs.html#accesslog
[fluentd]: http://www.fluentd.org/
[fluentd-preinstall]: http://docs.fluentd.org/v0.12/categories/installation
[fluentd-install]: http://docs.fluentd.org/v0.12/categories/installation
[fluentd-dogstatsd]: https://github.com/ryotarai/fluent-plugin-dogstatsd
[fluentd-apache2]: http://docs.fluentd.org/v0.12/articles/in_tail
[fluentd-filter]: http://docs.fluentd.org/v0.12/articles/filter-plugin-overview
[fluentd-record-transformer]: http://docs.fluentd.org/v0.12/articles/filter_record_transformer
[fluentd-config]: http://docs.fluentd.org/v0.12/articles/config-file
[fluentd-tail]: http://docs.fluentd.org/v0.12/articles/in_tail
[fluentd-grep]: http://docs.fluentd.org/v0.12/articles/filter_grep
[fluentd-startup-docs]: http://docs.fluentd.org/v0.12/articles/command-line-option
[dogstatsd-docs]: http://docs.datadoghq.com/guides/dogstatsd/
[dd-event-plugin]: https://github.com/inokappa/fluent-plugin-datadog_event
[dd-fluentd-plugin]: https://github.com/winebarrel/fluent-plugin-dd
[datadog-toplist]: /blog/easy-ranking-new-top-lists/
[anomalies]: /blog/introducing-anomaly-detection-datadog/
[apache-datadog-dashboard]: https://app.datadoghq.com/screen/integration/apache
[fluentd-launch-docs]: http://docs.fluentd.org/v0.12/articles/install-by-deb#step2-launch-daemon
[fluentd-config-docs]: http://docs.fluentd.org/v0.12/articles/config-file#config-file-location
[integration-monitor]: https://app.datadoghq.com/monitors#create/integration
[part-2-config-file]: /blog/collect-apache-performance-metrics/#apaches-status-module
[apache-log-vars]: http://httpd.apache.org/docs/current/mod/mod_log_config.html
[apache-fluentd-format-docs]: http://docs.fluentd.org/v0.12/articles/in_tail
[fluentular]: http://fluentular.herokuapp.com/
[dogstatsd-guide]: http://docs.datadoghq.com/guides/metrics/
