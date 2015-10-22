*This post is part 2 of a 3-part series on monitoring Amazon ELB. [Part 1](https://www.datadoghq.com/blog/top-elb-health-and-performance-metrics) explores its key performance metrics, and [Part 3](https://www.datadoghq.com/blog/monitor-elb-performance-with-datadog) shows you how Datadog can help you monitor ELB.*

This part of the series is about collecting ELB metrics, which are available from AWS via CloudWatch. They can be accessed in three different ways:

-   [Using the AWS Management Console](#console)
-   [Using the command-line interface (CLI)](#cli)
-   [Using a monitoring tool integrating the CloudWatch API](#tools)

We will also explain how [using ELB access logs](#logs) can be useful when investigating on specific request issues.

## Using the AWS Management Console

Using the online management console is the simplest way to monitor your load balancers with CloudWatch. It allows you to set up basic automated alerts and to get a visual picture of recent changes in individual metrics.

### Graphs

Once you are signed in to your AWS account, you can open the [CloudWatch console](https://console.aws.amazon.com/cloudwatch/home#metrics:) and then browse the metrics related to the different AWS services.

[![ELB metrics in AWS Console](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-01.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-01.png)

By clicking on the ELB Metrics category, you will see the list of available metrics per load balancer, per availability zone:

[![List of ELB metrics in AWS Console](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-02.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-02.png)

You can also view the metrics across all your load balancers:

[![List of ELB metrics across all load balancers](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-03.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-03.png)

Just select the checkbox next to the metrics you want to visualize, and they will appear in the graph at the bottom of the console:

[![ELB metrics graphs in AWS Console](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-04.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-04.png)

### Alerts

With the CloudWatch Management Console you can also create simple alerts that trigger when a metric crosses a specified threshold.

Click on the “Create Alarm” button at the right of your graph, and you will be able to set up the alert and configure it to notify a list of email addresses:

[![ELB alerts in AWS Console](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-05.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-10-elb/2-05.png)

## Using the AWS Command Line Interface

You can also retrieve metrics related to a load balancer from the command line. To do so, you will need to install the AWS Command Line Interface (CLI) by following [these instructions](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html). You will then be able to query for any CloudWatch metric, using different filters.

Command line queries can be useful for spot checks and ad hoc investigations when you can’t, or don’t want to, use a browser.

For example, if you want to know the health state of all the backend instances registered to a load balancer, you can run:

`aws elb describe-instance-health --load-balancer-name my-load-balancer`

That command should return a JSON output of this form:

<table>
<colgroup>
<col width="50%" />
<col width="50%" />
</colgroup>
<tbody>
<tr class="odd">
<td align="left"><div class="crayon-pre" style="font-size: 14px !important; line-height: 18px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;">
<div id="crayon-5627aa87106f2681009851-1" class="crayon-line">
 
</div>
<div id="crayon-5627aa87106f2681009851-2" class="crayon-line">
{
</div>
<div id="crayon-5627aa87106f2681009851-3" class="crayon-line">
  &quot;InstanceStates&quot;: [
</div>
<div id="crayon-5627aa87106f2681009851-4" class="crayon-line">
      {
</div>
<div id="crayon-5627aa87106f2681009851-5" class="crayon-line">
          &quot;InstanceId&quot;: &quot;i-xxxxxxxx&quot;,
</div>
<div id="crayon-5627aa87106f2681009851-6" class="crayon-line">
          &quot;ReasonCode&quot;: &quot;N/A&quot;,
</div>
<div id="crayon-5627aa87106f2681009851-7" class="crayon-line">
          &quot;State&quot;: &quot;InService&quot;,
</div>
<div id="crayon-5627aa87106f2681009851-8" class="crayon-line">
          &quot;Description&quot;: &quot;N/A&quot;
</div>
<div id="crayon-5627aa87106f2681009851-9" class="crayon-line">
      },
</div>
<div id="crayon-5627aa87106f2681009851-10" class="crayon-line">
      {
</div>
<div id="crayon-5627aa87106f2681009851-11" class="crayon-line">
          &quot;InstanceId&quot;: &quot;i-xxxxxxxx&quot;,
</div>
<div id="crayon-5627aa87106f2681009851-12" class="crayon-line">
          &quot;ReasonCode&quot;: &quot;N/A&quot;,
</div>
<div id="crayon-5627aa87106f2681009851-13" class="crayon-line">
          &quot;State&quot;: &quot;InService&quot;,
</div>
<div id="crayon-5627aa87106f2681009851-14" class="crayon-line">
          &quot;Description&quot;: &quot;N/A&quot;
</div>
<div id="crayon-5627aa87106f2681009851-15" class="crayon-line">
      },
</div>
<div id="crayon-5627aa87106f2681009851-16" class="crayon-line">
  ]
</div>
<div id="crayon-5627aa87106f2681009851-17" class="crayon-line">
}
</div>
<div id="crayon-5627aa87106f2681009851-18" class="crayon-line">
 
</div>
</div></td>
</tr>
</tbody>
</table>

[Here](http://docs.aws.amazon.com/cli/latest/reference/elb/index.html) are all the ELB commands you can run with the CLI.

## Monitoring tool integrated with CloudWatch

The third way to collect CloudWatch metrics is via your own monitoring tools, which can offer extended monitoring functionality.

You probably need a dedicated monitoring system if, for example, you want to:

-   Correlate metrics from one part of your infrastructure with others (including custom infrastructure or applications)
-   Dynamically slice, aggregate, and filter your metrics on any attribute
-   Access historical data
-   Set up sophisticated alerting mechanisms

CloudWatch can be integrated with outside monitoring systems  via API, and in many cases the integration just needs to be enabled to start working.

As explained in [Part 1](https://www.datadoghq.com/blog/top-elb-health-and-performance-metrics), CloudWatch’s ELB-related metrics give you great insight about your load balancers’ health and performance. However, for more precision and granularity on your backend instances’ performance, you should consider monitoring their resources directly. Correlating native metrics from your EC2 instances with ELB metrics will give you a fuller, more precise picture. In [Part 3](https://www.datadoghq.com/blog/monitor-elb-performance-with-datadog), we cover a concrete example of this type of metrics collection and detail how to monitor ELB using Datadog.

## ELB Access Logs

ELB access logs capture all the information about every request received by the load balancer, such as a time stamp, client IP address, path, backend response, latency, and so on. It can be useful to investigate the access logs for particular requests in case of issues.

### Configuring the access logs

First you must enable the access logs feature, which is disabled by default. Logs are stored in an Amazon S3 bucket, which incurs additional storage costs.

Elastic Load Balancing creates [log files](http://docs.aws.amazon.com/ElasticLoadBalancing/latest/DeveloperGuide/access-log-collection.html#access-log-file-format) at user-defined intervals, between 5 and 60 minutes. Every single request received by ELB is logged, including those requests that couldn’t be processed by your backend instances (see [Part 1](https://www.datadoghq.com/blog/top-elb-health-and-performance-metrics) for the different root causes of ELB issues). You can see more details [here](http://docs.aws.amazon.com/ElasticLoadBalancing/latest/DeveloperGuide/access-log-collection.html#access-log-entry-format) about the log entry format and the different fields containing information about a request.

### Analyzing logs

ELB access logs can be useful when troubleshooting and investigating specific requests. However, if you want to find and analyze patterns in the overall access log files, you might want to use dedicated log analytics tools, especially if you are dealing with large amount of traffic generating heavy log file volume.

## Conclusion

In this post we have walked through how to use CloudWatch to collect and visualize ELB metrics, how to generate alerts when these metrics go out of bounds, and how to use access logs for troubleshooting.

In the [next and final part on this series](https://www.datadoghq.com/blog/monitor-elb-performance-with-datadog) you will learn how you can monitor ELB metrics using the Datadog integration, along with native metrics from your backend instances for a complete view, with a minimum of setup.
