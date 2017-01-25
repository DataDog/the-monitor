#How to Collect DynamoDB Metrics

*This post is part 2 of a 3-part series on monitoring DynamoDB. [Part 1](https://www.datadoghq.com/blog/top-dynamodb-performance-metrics) explores its key performance metrics, and [Part 3](https://www.datadoghq.com/blog/how-medium-monitors-dynamodb-performance) describes the strategies Medium uses to monitor DynamoDB.*

This section of the article is about collecting native DynamoDB metrics, which are available exclusively from AWS via CloudWatch. For other non-native metrics, see [Part 3](https://www.datadoghq.com/blog/how-medium-monitors-dynamodb-performance).

CloudWatch metrics can be accessed in three different ways:

-   [Using the AWS Management Console and its web interface](#console)
-   [Using the command-line interface (CLI)](#cli)
-   [Using a monitoring tool integrating the CloudWatch API](#integrations)

<div class="anchor" id="console" />

## Using the AWS Management Console

Using the online management console is the simplest way to monitor DynamoDB with CloudWatch. It allows you to set up simple automated alerts, and get a visual picture of recent changes in individual metrics.

### Graphs

Once you are signed in to your AWS account, you can open the [CloudWatch console](https://console.aws.amazon.com/cloudwatch/home) where you will see the metrics related to the different AWS technologies.

[![CloudWatch console](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-dynamodb/2-01b.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-dynamodb/2-01b.png)

By clicking on DynamoDB’s “Table Metrics” you will see the list of your tables with the available metrics for each one:

[![DynamoDB metrics in CloudWatch](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-dynamodb/2-02b.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-dynamodb/2-02b.png)

Just select the checkbox next to the metrics you want to visualize, and they will appear in the graph at the bottom of the console.

[![DynamoDB metric graph in CloudWatch](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-dynamodb/2-03b.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-dynamodb/2-03b.png)

### Alerts

With the CloudWatch Management Console you can also create alerts which trigger when a certain metric threshold is crossed.

Click on **Create Alarm** at the right of your graph, and you will be able to set up the alert, and configure it to notify a list of email addresses:

[![DynamoDB CloudWatch alert](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-dynamodb/2-04b.png)](https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2015-09-dynamodb/2-04b.png)

<div class="anchor" id="cli" />

## Using the Command Line Interface

You can also retrieve metrics related to a specific table using the command line. To do so, you will need to install the AWS Command Line Interface by following [these instructions](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html). You will then be able to query for any CloudWatch metrics you want, using different filters.

Command line queries can be useful for spot checks and ad hoc investigations when you can’t or don’t want to use a browser.

For example, if you want to retrieve the metrics related to `PutItem` requests throttled during a specified time period, you can run:

<table>
<colgroup>
<col width="50%" />
<col width="50%" />
</colgroup>
<tbody>
<tr class="odd">
<td align="left"><div class="crayon-pre" style="font-size: 14px !important; line-height: 18px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;">
<div id="crayon-55fc5b58d1fde637588618-1" class="crayon-line">
 
</div>
<div id="crayon-55fc5b58d1fde637588618-2" class="crayon-line">
aws cloudwatch get-metric-statistics
</div>
<div id="crayon-55fc5b58d1fde637588618-3" class="crayon-line">
--namespace AWS/DynamoDB  --metric-name ThrottledRequests
</div>
<div id="crayon-55fc5b58d1fde637588618-4" class="crayon-line">
--dimensions Name=TableName,Value=YourTable Name=Operation,Value=PutItem
</div>
<div id="crayon-55fc5b58d1fde637588618-5" class="crayon-line">
--start-time 2015-08-02T00:00:00Z --end-time 2015-08-04T00:00:00Z
</div>
<div id="crayon-55fc5b58d1fde637588618-6" class="crayon-line">
--period 300 --statistics=Sum
</div>
<div id="crayon-55fc5b58d1fde637588618-7" class="crayon-line">
 
</div>
</div></td>
</tr>
</tbody>
</table>

Here is an example of a JSON output format you will see from a “get-metric-statistics“ query like above:

<table>
<colgroup>
<col width="50%" />
<col width="50%" />
</colgroup>
<tbody>
<tr class="odd">
<td align="left"><div class="crayon-pre" style="font-size: 14px !important; line-height: 18px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;">
<div id="crayon-55fc5b58d1fed521769294-1" class="crayon-line">
 
</div>
<div id="crayon-55fc5b58d1fed521769294-2" class="crayon-line">
{
</div>
<div id="crayon-55fc5b58d1fed521769294-3" class="crayon-line">
    &quot;Datapoints&quot;: [
</div>
<div id="crayon-55fc5b58d1fed521769294-4" class="crayon-line">
        {
</div>
<div id="crayon-55fc5b58d1fed521769294-5" class="crayon-line">
            &quot;Timestamp&quot;: &quot;2015-08-02T11:18:00Z&quot;,
</div>
<div id="crayon-55fc5b58d1fed521769294-6" class="crayon-line">
            &quot;Average&quot;: 44.79,
</div>
<div id="crayon-55fc5b58d1fed521769294-7" class="crayon-line">
            &quot;Unit&quot;: &quot;Count&quot;
</div>
<div id="crayon-55fc5b58d1fed521769294-8" class="crayon-line">
        },
</div>
<div id="crayon-55fc5b58d1fed521769294-9" class="crayon-line">
        {
</div>
<div id="crayon-55fc5b58d1fed521769294-10" class="crayon-line">
            &quot;Timestamp&quot;: &quot;2015-08-02T20:18:00Z&quot;,
</div>
<div id="crayon-55fc5b58d1fed521769294-11" class="crayon-line">
            &quot;Average&quot;: 47.92,
</div>
<div id="crayon-55fc5b58d1fed521769294-12" class="crayon-line">
            &quot;Unit&quot;: &quot;Count&quot;
</div>
<div id="crayon-55fc5b58d1fed521769294-13" class="crayon-line">
        },
</div>
<div id="crayon-55fc5b58d1fed521769294-14" class="crayon-line">
        {
</div>
<div id="crayon-55fc5b58d1fed521769294-15" class="crayon-line">
            &quot;Timestamp&quot;: &quot;2015-08-02T19:18:00Z&quot;,
</div>
<div id="crayon-55fc5b58d1fed521769294-16" class="crayon-line">
            &quot;Average&quot;: 50.85,
</div>
<div id="crayon-55fc5b58d1fed521769294-17" class="crayon-line">
            &quot;Unit&quot;: &quot;Count&quot;
</div>
<div id="crayon-55fc5b58d1fed521769294-18" class="crayon-line">
        },
</div>
<div id="crayon-55fc5b58d1fed521769294-19" class="crayon-line">
    ],
</div>
<div id="crayon-55fc5b58d1fed521769294-20" class="crayon-line">
    &quot;Label&quot;: &quot;ThrottledRequests&quot;
</div>
<div id="crayon-55fc5b58d1fed521769294-21" class="crayon-line">
}
</div>
<div id="crayon-55fc5b58d1fed521769294-22" class="crayon-line">
 
</div>
</div></td>
</tr>
</tbody>
</table>

<div class="anchor" id="integrations" />

## Integrations

The third way to collect CloudWatch metrics is via your own monitoring tools which can offer extended monitoring functionality. For example if you want the ability to correlate metrics from one part of your infrastructure with other parts (including custom infrastructure or applications), or you want to dynamically slice, aggregate, and filter your metrics on any attribute, or you need specific alerting mechanisms, you probably are using a dedicated monitoring tool or platform. CloudWatch can be integrated with these platforms via API, and in many cases the integration just needs to be enabled to start working.

In [Part 3](https://www.datadoghq.com/blog/how-medium-monitors-dynamodb-performance), we cover a real-world example of this type of metrics collection: [Medium](https://medium.com/)’s engineering team monitors DynamoDB using an integration with Datadog.

## Conclusion

In this post we have walked through how to use CloudWatch to collect and visualize DynamoDB metrics, and how to generate alerts when these metrics go out of bounds.

As discussed in [Part 1](https://www.datadoghq.com/blog/top-dynamodb-performance-metrics), DynamoDB can’t see, or doesn’t report on all the events that you likely want to monitor, including true latency and error rates. In the [next and final part on this series](https://www.datadoghq.com/blog/how-medium-monitors-dynamodb-performance) we take you behind the scenes with Medium’s engineering team to learn about the issues they’ve encountered, and how they’ve solved them with a mix of tools which includes CloudWatch, ELK, and Datadog.
