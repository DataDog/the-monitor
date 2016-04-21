# Monitor Redis using Datadog

*This post is part 3 of a 3-part series on Redis monitoring. [Part 1](http://www.datadoghq.com/blog/how-to-monitor-redis-performance-metrics) explores the key metrics available in Redis, and [Part 2](http://www.datadoghq.com/blog/how-to-collect-redis-metrics/) is about collecting those metrics on an ad-hoc basis.*

To implement ongoing, meaningful monitoring, you will need a dedicated system that allows you to store, visualize, and correlate your Redis metrics with the rest of your infrastructure. You also need to be alerted when any system starts to misbehave. In this post, we will show you how use Datadog to capture and report on all the key metrics identified in [Part 1](http://www.datadoghq.com/blog/how-to-monitor-redis-performance-metrics), and more.

## Integrating Datadog and Redis

### Verify that Redis and redis-cli are working

Before you begin, run this command on your server to verify that Redis is running properly:

<table>
<colgroup>
<col width="50%" />
<col width="50%" />
</colgroup>
<tbody>
<tr class="odd">

<td align="left"><div class="crayon-pre" style="font-size: 14px !important; line-height: 18px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;">
<div id="crayon-55e8b35499885289873843-1" class="crayon-line">
 
</div>
<div id="crayon-55e8b35499885289873843-2" class="crayon-line">
redis-cli info | grep uptime_in_seconds
</div>
<div id="crayon-55e8b35499885289873843-3" class="crayon-line">
 
</div>
</div></td>
</tr>
</tbody>
</table>

If you are running the command from a different host or port, add arguments to the command as follows:

<table>
<colgroup>
<col width="50%" />
<col width="50%" />
</colgroup>
<tbody>
<tr class="odd">

<td align="left"><div class="crayon-pre" style="font-size: 14px !important; line-height: 18px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;">
<div id="crayon-55e8b35499894171718885-1" class="crayon-line">
 
</div>
<div id="crayon-55e8b35499894171718885-2" class="crayon-line">
redis-cli -h &lt;host&gt; -p &lt;port&gt; info | grep uptime_in_seconds
</div>
<div id="crayon-55e8b35499894171718885-3" class="crayon-line">
 
</div>
</div></td>
</tr>
</tbody>
</table>

Make sure the output displays “uptime\_in\_seconds: &lt;number&gt;”:

<table>
<colgroup>
<col width="50%" />
<col width="50%" />
</colgroup>
<tbody>
<tr class="odd">
<td align="left"><div class="crayon-pre" style="font-size: 14px !important; line-height: 18px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;">
<div id="crayon-55e8b3549989a246982303-1" class="crayon-line">
 
</div>
<div id="crayon-55e8b3549989a246982303-2" class="crayon-line">
uptime_in_seconds: 162
</div>
<div id="crayon-55e8b3549989a246982303-3" class="crayon-line">
 
</div>
</div></td>
</tr>
</tbody>
</table>

### Install the Datadog Agent

The [Datadog Agent](https://github.com/DataDog/dd-agent) is open-source software that collects and reports metrics from your different hosts so you can view, monitor, and correlate them on the Datadog platform. Installing the Agent usually requires just a single command. Installation instructions for different systems are available [here](https://app.datadoghq.com/account/settings#agent).

As soon as the Datadog Agent is up and running, you should see your host reporting basic system metrics [in your Datadog account](https://app.datadoghq.com/infrastructure).

[![Reporting host in Datadog ](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-redis/3-img1.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-redis/3-img1.png)

### Configure the Agent

Next you will need to create a Redis configuration file for the Agent. You can find the location of the Agent configuration directory for your OS [here](http://docs.datadoghq.com/guides/basic_agent_usage/). In that directory you will find [a sample Redis config file](https://github.com/DataDog/dd-agent/blob/master/conf.d/redisdb.yaml.example) named **redisdb.yaml.example**. Copy this file to **redisdb.yaml**. You can edit the file to change the port setting if you are running Redis on a non-default port, have multiple Redis instances running, and can include a  list of tags that will be applied to every collected metric:

<table>
<colgroup>
<col width="50%" />
<col width="50%" />
</colgroup>
<tbody>
<tr class="odd">

<td align="left"><div class="crayon-pre" style="font-size: 14px !important; line-height: 18px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;">
<div id="crayon-55e8b354998a0280399811-1" class="crayon-line">
 
</div>
<div id="crayon-55e8b354998a0280399811-2" class="crayon-line">
init_config:
</div>
<div id="crayon-55e8b354998a0280399811-3" class="crayon-line">
 
</div>
<div id="crayon-55e8b354998a0280399811-4" class="crayon-line">
instances:
</div>
<div id="crayon-55e8b354998a0280399811-5" class="crayon-line">
  - host: localhost
</div>
<div id="crayon-55e8b354998a0280399811-6" class="crayon-line">
    port: 6379
</div>
<div id="crayon-55e8b354998a0280399811-7" class="crayon-line">
 
</div>
<div id="crayon-55e8b354998a0280399811-8" class="crayon-line">
    tags:
</div>
<div id="crayon-55e8b354998a0280399811-9" class="crayon-line">
instance:production
</div>
<div id="crayon-55e8b354998a0280399811-10" class="crayon-line">
 
</div>
</div></td>
</tr>
</tbody>
</table>

Save and close the file.

### Restart the Agent

Restart the Agent to load your new configuration. The restart command varies somewhat by platform; see the specific commands for your platform [here](http://docs.datadoghq.com/guides/basic_agent_usage/).

### Verify the configuration settings

To check that Datadog and Redis are properly integrated, execute the Datadog `info` command. The command for each platform is available [here](http://docs.datadoghq.com/guides/basic_agent_usage/).

If the configuration is correct, you will see a section like this in the `info` output:

<table>
<colgroup>
<col width="50%" />
<col width="50%" />
</colgroup>
<tbody>
<tr class="odd">

<td align="left"><div class="crayon-pre" style="font-size: 14px !important; line-height: 18px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;">
<div id="crayon-55e8b354998a6710556324-1" class="crayon-line">
 
</div>
<div id="crayon-55e8b354998a6710556324-2" class="crayon-line">
Checks
</div>
<div id="crayon-55e8b354998a6710556324-3" class="crayon-line">
======
</div>
<div id="crayon-55e8b354998a6710556324-4" class="crayon-line">
  [...]
</div>
<div id="crayon-55e8b354998a6710556324-5" class="crayon-line">
 
</div>
<div id="crayon-55e8b354998a6710556324-6" class="crayon-line">
    redisdb
</div>
<div id="crayon-55e8b354998a6710556324-7" class="crayon-line">
    -------
</div>
<div id="crayon-55e8b354998a6710556324-8" class="crayon-line">
      - instance #0 [OK] Last run duration: 0.00831699371338
</div>
<div id="crayon-55e8b354998a6710556324-9" class="crayon-line">
      - Collected 26 metrics, 0 events &amp; 2 service checks
</div>
<div id="crayon-55e8b354998a6710556324-10" class="crayon-line">
 
</div>
</div></td>
</tr>
</tbody>
</table>

The snippet above shows two service checks in addition to the collected metrics. For Redis, the service checks report the availability of your Redis instance, as well as on the status of the master link (when using Redis’s replication features).

### Turn on the integration

Finally, click the Redis **Install Integration** button inside your Datadog account. The button is located under the Configuration tab in the [Redis integration settings](https://app.datadoghq.com/account/settings#integrations/redis).

[![Redis integration installation](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-redis/3-img2.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-redis/3-img2.png)

## Metrics!

Once the Agent begins reporting Redis metrics, you will see [a Redis dashboard](https://app.datadoghq.com/dash/integration/redis) among your list of available dashboards in Datadog.

The default Redis dashboard displays the key metrics to watch highlighted in our introduction on how to monitor Redis. 

[![default Redis dashboard](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-redis/part3-dashboard.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-redis/part3-dashboard.png)

You can easily create a more comprehensive dashboard to monitor Redis alongside your entire web stack by adding additional graphs and metrics from your other systems. For example, you might want to graph Redis metrics alongside metrics from your [NGINX web servers](https://www.datadoghq.com/blog/how-to-monitor-nginx-with-datadog/), or alongside host-level metrics such as network traffic. To start building a custom dashboard, clone the default Redis dashboard by clicking on the gear on the upper right of the dashboard and selecting **Clone Dash**.

[![Clone Redis dashboard](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-redis/3-img4.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-redis/3-img4.png)

## Alerting on Redis metrics

Once Datadog is capturing and visualizing your metrics, you will likely want to set up some [alerts](https://www.datadoghq.com/blog/monitoring-101-alerting/) to be automatically notified of potential issues.

Datadog can monitor individual hosts, containers, services, processes—or virtually any combination thereof. For instance, you can monitor all of your Redis hosts, or all hosts in a certain availability zone, or a single key metric being reported by all hosts corresponding to a specific tag.

## Conclusion

In this post we’ve walked you through integrating Redis with Datadog to visualize your key metrics and notify the right team whenever your infrastructure shows signs of trouble.

If you’ve followed along using your own Datadog account, you should now have improved visibility into what’s happening in your environment, as well as the ability to create automated alerts tailored to your infrastructure, your usage patterns, and the metrics that are most valuable to your organization.

If you don’t yet have a Datadog account, you can sign up for a [free trial](https://www.datadoghq.com/blog/monitor-redis-using-datadog/#sign-up) and start monitoring Redis right away.

