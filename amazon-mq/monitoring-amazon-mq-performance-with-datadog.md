In [Part 2](/blog/collecting-amazon-mq-metrics-and-logs) of this series, we showed you how to use CloudWatch to monitor metrics and logs from Amazon MQ. With CloudWatch, you can easily create ad-hoc graphs to visualize the performance of your messaging infrastructure and other AWS services you use (such as EC2, Lambda, and S3). But to monitor your Amazon MQ brokers, destinations, and clients alongside the rest of your applications and infrastructure, you need a monitoring platform that easily integrates with your whole technology stack. In this post, we'll show you how to use Datadog to:

- [Collect](#collecting-amazon-mq-performance-data) Amazon MQ metrics
- Visualize metrics with pre-built and custom [dashboards](#visualizing-amazon-mq-performance)
- Analyze Amazon MQ [logs](#collecting-and-analyzing-amazon-mq-logs) 
- Create [alerts](#use-alerts-to-stay-informed) based on your metrics and logs

{{<img src="amazon-mq-built-in-dashboard.png" alt="As soon as you integrate Amazon MQ with Datadog, a built-in dashboard displays detailed broker and destination metrics." border="true" wide="true" popup="true" >}}

## Collecting Amazon MQ performance data
Datadog's AWS integration makes it easy to visualize and alert on your Amazon MQ metrics and logs. In the next section, we'll give an overview of how to integrate your AWS account with Datadog to begin collecting metrics and logs from your Amazon MQ infrastructure. If you're already using Datadog to collect metrics from any of your AWS services, you should [skip ahead to the following section](#enable-collection-of-amazon-mq-metrics).

### Integrate your AWS account with Datadog
If this is the first time you're using Datadog to collect AWS data, you'll need to create a new [IAM role][datadog-aws-integration-setup] in your AWS account and identify Datadog's AWS account as the trusted entity. Then you'll need to [attach a policy][datadog-aws-integration-policy] to this role that grants read-only access to Amazon MQ (and any other AWS services you want to monitor) so Datadog can collect your AWS metrics. See the instructions in our [documentation][datadog-aws-integration] for detailed guidance on setting up the AWS integration. 

### Enable collection of Amazon MQ metrics
Once you've created the Datadog integration role in AWS, you need to configure it to collect metrics from Amazon MQ, as well as any other AWS services you want to begin monitoring. In your Datadog account, navigate to the [AWS integration tile][datadog-aws-integration-tile] and click the **Configuration** tab. Make sure that the **MQ** box is checked under the **Limit metric collection by AWS Service** list. If you haven't done so already, you'll need to add your account ID and the name of the role you created earlier under the **AWS Accounts** section. Then, click the **Install Integration** button (or the **Update Configuration** button if you've already configured other AWS integrations).

If you want to collect and analyze Amazon MQ logs in Datadog, you'll also need to set up the logs integration. We'll show you how to do that [later on in this post](#collecting-and-analyzing-amazon-mq-logs).
### Tag your metrics
Adding tags to your metrics gives you [depth and flexibility][datadog-the-power-of-tagged-metrics] in how you visualize them, and helps you understand the information they convey. Datadog automatically creates tags from the CloudWatch dimensions associated with your Amazon MQ metrics, so you can filter and aggregate your metrics based on tags like `region`, `broker`, `queue`, and `topic`. 

You can easily add custom tags to a new or existing broker, whether you're using the [Amazon MQ console][aws-amazon-mq-console] or CloudFormation. The code snippet below shows a portion of a CloudFormation template that creates a broker with two custom tags applied to it:

```
  TestBroker1:
    Type: "AWS::AmazonMQ::Broker"
    Properties:
      Tags:
        -
          Key: "env"
          Value: "development"
        -
          Key: "app"
          Value: "enrollment"
```

Datadog will automatically pull these custom key-value tags and apply them to any metrics collected from this broker, so you can use them to slice and dice your data. For example, an `env` tag like the one shown above can help you easily distinguish metrics from your development stack from that of your production infrastructure.
## Visualizing Amazon MQ performance
Once your AWS integration is enabled, you can use the [out-of-the-box dashboard][dd-amazon-mq-oob-dash] to visualize Amazon MQ metrics. Each graph on the dashboard provides information about important [broker](/blog/amazon-mq-monitoring#broker-metrics) and [destination](/blog/amazon-mq-monitoring#destination-metrics) metrics we looked at in Part 1 of this series, and gives you a starting point to investigate potential problems.

This dashboard includes [template variables][datadog-template-variables], which you can use to filter the graphs based on your tags. In the screenshot below, we've used template variables to show only data from the queue named `renewal_queue` and the broker named `signupsvcmessagingbroker`. (Amazon MQ appends `-1` to the name of any standalone broker, and `-1` and `-2` to brokers deployed in redundant pairs for [high availability][aws-amazon-mq-ha].)

{{<img src="amazon-mq-dashboard-template-variables.png" alt="Datadog's out-of-the-box dashboard for Amazon MQ shows broker metrics and destination metrics." popup="true" border="true" wide="true" >}}

As you determine what metrics are most useful to you, you can hone your monitoring by [creating your own dashboards][dd-create-a-dashboard]. To quickly start customizing this out-of-the-box dashboard, you can click the gear in the upper right and select **Clone dashboard.**

{{< img src="amazon-mq-clone-dashboard.png" alt="The clone dashboard button is highlighted on the Datadog dashboard for Amazon MQ." >}}

Your dashboards aren't limited to Amazon MQ metrics. You can customize your dashboards to correlate Amazon MQ metrics with data from any of Datadog's {{< translate key="integration_count" >}}+ integrations, allowing you to get a unified view of your entire messaging infrastructure in a single pane of glass.

You can easily add graphs to your dashboard to track the performance of [AWS services][dd-aws-integrations] as well as any other technologies you're monitoring with Datadog. The custom dashboard below shows data from an example application that comprises a public-facing website backed by distributed services that communicate using Amazon MQ. The graphs show broker and destination metrics, [host maps][dd-host-map] displaying the CPU usage of the clients connected to the broker, and throughput information from the website's NGINX web server and MySQL database.

{{< img src="amazon-mq-custom-dashboard.png" alt="A dashboard shows metrics from a broker and its queues, as well as EC2, NGINX, and MySQL metrics" border="true" >}}

## Collecting and analyzing Amazon MQ logs
When the graphs on your dashboard indicate a possible issue with Amazon MQ performance, you can navigate to related logs to investigate the issue. In this section, we'll show you how to collect your Amazon MQ logs in Datadog so you can analyze, graph, search, and alert on them.

Log collection is disabled in Amazon MQ by default. You can enable it on a new or existing broker by configuring it to send general logs and/or audit logs to CloudWatch, as described in [Part 2](/blog/collecting-amazon-mq-metrics-and-logs#view-amazon-mq-logs) of this series. Our examples in this section will focus on general logs, since they provide information about the activity of the broker (whereas audit logs record configuration changes made to your broker). See the [Amazon MQ documentation][aws-amazon-mq-audit-and-general-logs] for more details about these two types of logs.
### Deploy the Datadog log forwarder
To forward logs from CloudWatch Logs to Datadog, you'll need to deploy the [`Datadog-Log-Forwarder` Lambda function][datadog-aws-log-collection]. You should configure the trigger to execute the function automatically when Amazon MQ logs are collected by CloudWatch, forwarding them to Datadog so you can view, search, and alert on them. See the [Datadog AWS integration documentation][datadog-aws-log-collection-lambda] for instructions on how to deploy this function from the [AWS Serverless Repository][aws-serverless-datadog-log-forwarder]. 

You can tag your Amazon MQ logs to differentiate them from logs emitted by other AWS services, or to aggregate related logs that come from different sources. For example, you could apply the same tag to your Amazon MQ logs and to EC2 logs from the instances that host your producers and consumers. You can use this tag to aggregate these logs into a single view to better understand the performance of your entire messaging infrastructure. 

To apply custom tags to your Amazon MQ logs, navigate to the Lambda console and click the name of the function that was created when you deployed the `Datadog-Log-Forwarder`. Scroll down to the **Environment variables** section of the page and create a new environment variable with the key `DD_TAGS`, then add a comma-delimited list of tags in key-value format, such as `app:enrollment,env:development`, as shown below. Note that, in this example, we are using the same tags we [added to the broker's metrics](#tag-your-metrics) via CloudFormation in an earlier section of this post.

{{< img src="amazon-mq-tagging-logs.png" alt="Adding tags as environment variables in the Lambda UI." border="true" >}}
### Search and filter your logs
Datadog's [log pipeline][datadog-log-pipeline] automatically parses your CloudWatch logs to extract log attributes you can use to search and filter your logs in the [Log Explorer][datadog-log-explorer]. 

{{< img src="amazon-mq-log-attributes.png" alt="The Log Explorer shows the attributes that have been automatically parsed from a CloudWatch log." border="true" >}}

In the screenshot below, the `host` attribute is available to use as a [facet][datadog-log-facets], making it easy to isolate logs from one or more brokers.

{{< img src="amazon-mq-logs-host-attribute.png" wide="true" border="true" alt="You can use the Host attribute to filter your CloudWatch logs and display only logs from specific brokers." >}}

If you've tagged your logs, you can filter by any combination of tags to display a targeted subset of your logs. The screenshot below illustrates how you can use the search field in the Log Explorer to display only logs from the enrollment application.

{{< img src="amazon-mq-logs-tags.png" wide="true" border="true" alt="Specify a tag in the Log Explorer's search field to filter your results to include only logs with that tag." >}}

### Tie your logs to your metrics
When you apply tags to metrics and logs, you can then use those tags to explore metrics and logs in more meaningful ways. The screenshot below shows a graph of memory usage of all Amazon MQ destinations with the tag `app:enrollment`. You can click a point on the graph and select **View related logs** to easily see logs that share that tag.

{{< img src="amazon-mq-pivot-to-logs.png" border="true" alt="This graph shows average memory usage across all destinations. When you click a point on the graph, you can pivot to view logs with the same tags that occurred at the same time." >}}

To learn more about the rising memory usage in the graph shown above, you can click **View related logs** to inspect the broker’s logs. The related log, shown below, indicates that [producer flow control (PFC)][apache-activemq-pfc] has been triggered to prevent the producer from enqueuing more messages. 

{{< img src="amazon-mq-related-logs.png" alt="The Log Explorer shows the detail of a log that includes the string 'Memory Limit reached.'" popup="true" border="true" >}}
## Use alerts to stay informed
[Alerts][datadog-alerts] keep you informed of potential issues in your Amazon MQ infrastructure. You can use tags in your alert definitions to create alerts that are focused and actionable. The screenshot below illustrates how you could set up an alert that will trigger if the average queue size of destinations tagged `app:enrollment` rises above 10,000.

{{< img src="amazon-mq-alert-definition.png" border="true" wide="true" popup="true" alt="The Datadog screen for creating a Threshold Alert. The metric to alert on is queue size and the alert threshold is 10,000 messages." >}}

You can set up alerts to automatically monitor any of the key Amazon MQ metrics we identified in [Part 1](/blog/amazon-mq-monitoring) of this series. The example below shows a [forecast alert][datadog-forecast-monitoring] that will trigger if the disk space used by the broker to store persistent messages (`aws.amazonmq.store_percent_usage`) is expected to rise above 80 percent of its limit in the next week. If this alert triggers, you may need to move your broker to a larger [instance type](/blog/amazon-mq-monitoring#broker-instances).

{{< img src="amazon-mq-alert.png" alt="Screenshot showing the controls you use to create a new alert." wide="true" border="true" >}}

You can also create [alerts based on your brokers' logs][datadog-log-monitors] to notify you of significant events such as a producer being blocked due to PFC. To make your log and metric alerts visible to your team, you can integrate your Datadog account with PagerDuty, Slack, and many other [notification][datadog-integration-notification] and [collaboration][datadog-integration-collaboration] services. 

## Monitor messaging and more
If the services in your distributed application coordinate their work by communicating through Amazon MQ, you need to ensure that your brokers and destinations are performing well. Datadog integrates with more than {{< translate key="integration_count" >}} technologies, giving you a single platform for monitoring all your applications, services, and infrastructure. If you're not already using Datadog, you can start by signing up for a <a href="#" class="sign-up-trigger">free 14-day trial</a>.

_Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/amazon-mq/monitoring-amazon-mq-with-datadog.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues)._

[apache-activemq-pfc]: http://activemq.apache.org/producer-flow-control.html
[aws-amazon-mq-audit-and-general-logs]: https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/amazon-mq-configuring-cloudwatch-logs.html
[aws-amazon-mq-console]: https://console.aws.amazon.com/amazon-mq/home
[aws-amazon-mq-ha]: https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/active-standby-broker-deployment.html
[aws-arn]: https://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html
[aws-serverless-datadog-log-forwarder]: https://serverlessrepo.aws.amazon.com/applications/arn:aws:serverlessrepo:us-east-1:464622532012:applications~Datadog-Log-Forwarder
[datadog-alerts]: https://www.datadoghq.com/blog/monitoring-101-alerting/
[datadog-aws-integration]: https://docs.datadoghq.com/integrations/amazon_web_services
[datadog-aws-integration-policy]: https://docs.datadoghq.com/integrations/amazon_web_services/?tab=allpermissions#datadog-aws-iam-policy
[datadog-aws-integration-setup]: https://docs.datadoghq.com/integrations/amazon_web_services/?tab=allpermissions#setup
[datadog-aws-integration-tile]: https://app.datadoghq.com/account/settings#integrations/amazon-web-services
[datadog-aws-log-collection]: https://docs.datadoghq.com/integrations/amazon_web_services/?tab=allpermissions#log-collection
[datadog-aws-log-collection-lambda]: https://docs.datadoghq.com/integrations/amazon_web_services/?tab=allpermissions#set-up-the-datadog-lambda-function
[datadog-forecast-monitoring]: https://docs.datadoghq.com/monitors/monitor_types/forecasts/
[datadog-graphing]: https://docs.datadoghq.com/graphing/
[datadog-integration-collaboration]: https://docs.datadoghq.com/integrations/#cat-collaboration
[datadog-integration-notification]: https://docs.datadoghq.com/integrations/#cat-notification
[datadog-log-explorer]: https://docs.datadoghq.com/logs/explorer/
[datadog-log-facets]: https://docs.datadoghq.com/logs/explorer/?tab=facets#setup
[datadog-log-monitors]: https://docs.datadoghq.com/monitors/monitor_types/log/
[datadog-log-pipeline]: https://docs.datadoghq.com/logs/processing/pipelines/
[datadog-template-variables]: https://docs.datadoghq.com/graphing/dashboards/template_variables/
[datadog-the-power-of-tagged-metrics]: https://www.datadoghq.com/blog/the-power-of-tagged-metrics/
[dd-amazon-mq-oob-dash]: https://app.datadoghq.com/screen/integration/257/amazon-mq
[dd-aws-integrations]: https://docs.datadoghq.com/integrations/#cat-aws
[dd-create-a-dashboard]: https://docs.datadoghq.com/graphing/dashboards/#create-a-dashboard
[dd-host-map]: https://docs.datadoghq.com/graphing/infrastructure/hostmap/
