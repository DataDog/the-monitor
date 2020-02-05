---
authors:
- email: mallory.mooney@datadoghq.com
  name: Mallory Mooney
  image: mallory_new.png
blog/category:
- series datadog
blog/tag:
- lambda
- AWS
- serverless
- functions
- cloudwatch
date: 2020-02-05
description: Learn how to use Datadog to collect metrics, traces, and logs from your AWS Lambda functions.
subheader: Learn how to use Datadog to collect metrics, traces, and logs from your AWS Lambda functions.
draft: false
image: lambda_part3.png
preview_image: lambda_part3.png
slug: monitoring-aws-lambda-with-datadog
technology: AWS Lambda
title: "Monitoring AWS Lambda with Datadog"
series: aws-lambda-monitoring
tcp:
- title: "eBook: Monitoring Modern Infrastructure"
  desc: "Explore key steps for implementing a successful cloud-scale monitoring strategy."
  cta: "Download to learn more"
  link: "https://www.datadoghq.com/ebook/monitoring-modern-infrastructure/?utm_source=Content&utm_medium=eBook&utm_campaign=BlogCTA-MonitoringModernInfrastructure"
  img: Thumbnail-MonitoringModernInfrastructure.png
---

In [Part 2][part-two] of this series, we looked at how Amazon's built-in monitoring services can help you get insights into all of your AWS Lambda functions. In this post, we'll show you how to use Datadog to monitor all of the metrics emitted by Lambda, as well as function logs and performance data, to get a complete picture of your serverless applications. 

{{< img src="lambda_ootb_dash.png" alt="View all of your Lambda metrics in Datadog's out-of-the-box integration dashboard" border="true" caption="Visualize your AWS Lambda metrics with Datadog's out-of-the-box integration dashboard.">}}

In this post, we will:

- Enable Datadog's AWS and [Lambda](#enable-datadogs-aws-integration) integrations 
- [Collect enhanced metrics](#get-more-insight-with-datadogs-lambda-layer) and more with Datadog's Lambda Layer
- Monitor Lambda [traces](#native-tracing-for-aws-lambda-functions) and [logs](#monitor-aws-lambda-logs-with-datadog)
- [Detect trends in Lambda performance and create alerts](#forecast-trends-and-detect-anomalies-in-aws-lambda-functions)


## Enable Datadog's AWS integration
Datadog integrates with AWS Lambda and [other services](https://docs.datadoghq.com/integrations/#cat-aws) such as Amazon API Gateway, S3, and DynamoDB. If you're already using Datadog's AWS integration and your [Datadog role has read-only access to Lambda](https://docs.datadoghq.com/integrations/amazon_lambda/?tab=awsconsole#metric-collection), make sure that "Lambda" is checked in your [AWS integration tile](https://app.datadoghq.com/account/settings#integrations/amazon_web_services) and [skip to the next section](#visualize-your-aws-lambda-metrics). 

### Configure AWS Lambda metric collection
To get started, [configure IAM role delegation](https://docs.datadoghq.com/integrations/amazon_web_services/?tab=allpermissions#installation) and an IAM policy that grants your Datadog role read-only access to AWS Lambda and any other services you wish to monitor. You can find an [example policy](https://docs.datadoghq.com/integrations/amazon_web_services/?tab=allpermissions#datadog-aws-iam-policy) in our documentation. 

To provide Datadog with read-only access to your Lambda monitoring data, make sure your Datadog IAM policy includes the following permissions:

- `lambda:List*`: Lists Lambda functions, metadata, and tags
- `tag:GetResources`: Collects custom tags applied to Lambda functions

Then navigate to the [AWS integration tile](https://app.datadoghq.com/account/settings#integrations/amazon_web_services) in your Datadog account. Add your AWS account information, along with the name of the IAM role you configured. Make sure that you select "Lambda" (along with the names of any other services you want to start monitoring).

{{< img src="aws_tile.png" alt="Enable Datadog's Lambda integration in the AWS integration tile." border="true">}}

## Visualize your AWS Lambda metrics
Datadog will automatically start collecting the key Lambda metrics discussed in [Part 1][part-one], such as `invocations`, `duration`, and `errors`, so you can visualize them in the [out-of-the-box Lambda dashboard](https://app.datadoghq.com/screen/integration/98/aws-lambda). Dashboards provide a high-level overview of your Lambda metrics. You can also customize your dashboards to include function logs and trace data, as well as metrics from all of your services, not just Lambda. Check out [our documentation](https://docs.datadoghq.com/dashboards/) for more information about creating custom dashboards for your services.

Datadog also provides an [out-of-the-box dashboard](https://app.datadoghq.com/screen/integration/30306/aws-lambda-enhanced-metrics) for visualizing real-time enhanced metrics from the Lambda Layer.

{{< img src="lambda_enhanced_metrics_dash.png" alt="View all of your Lambda enhanced metrics in Datadog's out-of-the-box integration dashboard" border="true">}}

## Get more insight with Datadog's Lambda Layer
Though Datadog's AWS Lambda integration automatically collects [standard metrics](https://docs.datadoghq.com/integrations/amazon_lambda/?tab=awsconsole#data-collected) (e.g., duration, invocations, concurrent executions), you can also set up Datadog's [Lambda Layer](https://docs.datadoghq.com/integrations/amazon_lambda/?tab=awsconsole#datadog-lambda-layer) to get deeper insights from your code. In this section, we'll show you how the Lambda Layer can help you collect custom business metrics, distributed traces, and [enhanced metrics][enhanced-metrics-doc] from your functions. Datadog's Lambda Layer runs as a part of each function's runtime, and works with the Datadog Lambda Forwarder to generate high-granularity enhanced metrics. Data collected with the Lambda Layer complements the metrics, logs, and other traces that you are already collecting from services outside of Lambda. 

### Set up the Lambda Layer
You can get started by adding the Datadog Lambda Layer ARN ([Amazon Resource Name](https://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html)) to your function.

{{< img src="lambda_arn.png" alt="Add Datadog's Lambda Layer ARN to your function" border="true">}}

This ARN requires a region, runtime, and version. Check out [our documentation](https://docs.datadoghq.com/integrations/amazon_lambda/?tab=awsconsole#installing-and-using-the-datadog-lambda-layer) to see supported runtimes and versions. You will also need to add your [Datadog API key](https://app.datadoghq.com/account/settings#api) to the function's environment variable section.

### Custom business metrics
[Custom metrics](https://www.datadoghq.com/blog/datadog-lambda-layer/#custom-metrics-for-serverless-monitoring) give additional insights into use cases that are unique to your application workflows, such as a user logging into your application, purchasing an item, or updating a user profile. 

The Lambda Layer can send custom metrics [asynchronously](https://docs.datadoghq.com/integrations/amazon_lambda/?tab=nodejs#synchronous-vs-asynchronous-custom-metrics) or synchronously. Sending metrics asynchronously is recommended because it does not add any overhead to your code, making it an ideal solution for functions that power performance-critical tasks for your applications. To emit metrics asynchronously, add the `DD_FLUSH_TO_LOG` environment variable to your Lambda function and set it to `True`. Make sure that you're using version 1.4.0+ of [Datadog's log forwarder function](#monitor-aws-lambda-logs-with-datadog). 

Datadog provides [several libraries](https://docs.datadoghq.com/integrations/amazon_lambda/?tab=nodejs#custom-metrics) for instrumenting your functions, including Go, Node.js, and Python. To get started, import the appropriate Lambda Layer methods and add a wrapper around your function, as seen in the example Node.js function snippet below:

{{<code-snippet lang="javascript" wrap="false" >}}
const { datadog, sendDistributionMetric } = require("datadog-lambda-js");

async function customHandler(event, context) {
  sendDistributionMetric(
    "delivery_application.meal_value",       // Metric name
    13.54,                                                  // Metric value
    "item:pizza", "order:online"                // Associated tags
  );
  return {
    statusCode: 200,
    body: "Item purchased for delivery",
  };
}
// Wrap your handler function:
module.exports.customHandler = datadog(customHandler);
{{</code-snippet>}} 

As the function code is invoked, the Lambda Layer will automatically emit the `delivery_application.meal_value` metric to Datadog. You can read more about instrumenting your Lambda functions to send custom metrics in our [documentation](https://docs.datadoghq.com/integrations/amazon_lambda/#custom-metrics). 

### Enhanced metrics
Along with collecting custom metrics, you will also be able to analyze [enhanced metrics][enhanced-metrics-doc] from your Lambda functions (collected by Datadog's Lambda Layer and Log Forwarder). Enhanced metrics will show up in Datadog with the `aws.lambda.enhanced` prefix. These metrics are collected at higher granularity than standard CloudWatch metrics, enabling you to view metric data at near real-time in Datadog. For example, while Lambda errors are available as a standard CloudWatch metric, you can create an alert on the enhanced metric (`aws.lambda.enhanced.errors`) to get higher-granularity insights into potential issues. 

Some enhanced metrics (such as billed duration and estimated execution cost) are automatically extracted from your Lambda logs, eliminating the need to create custom queries in CloudWatch. Enhanced metrics also include detailed metadata for your functions such as `cold_start` and any custom tags you added to your function in the Lambda console.   

{{< img src="lambda_cold_starts.png" alt="View a heat map of cold starts for your functions" border="true">}}


The Lambda Layer can also trace requests across all your Lambda functions instrumented with Datadog's native tracing libraries and other systems running the Datadog Agent. In the next sections, we'll show you how to start collecting and analyzing Lambda traces. 

## Native tracing for AWS Lambda functions
Datadog APM provides tracing libraries that you can use with the Lambda Layer in order to [natively trace request traffic](https://www.datadoghq.com/blog/tracing-lambda-datadog-apm/) across your serverless architecture. In the example below, you can see the full path of a request as it travels across services in your environment. 

{{< img src="lambda_traces.png" alt="View the full path of a request as it travels across services" border="true">}}

The Lambda Layer automatically propagates trace context across service boundaries, so you can get end-to-end visibility across requests, even as they travel across hosts, containers, and AWS Lambda functions. Traces are sent asynchronously so they don't add any latency overhead to your serverless applications. Datadog's native tracing libraries are community-driven and support the [OpenTelemetry standard](https://www.datadoghq.com/blog/opentelemetry-instrumentation/) so you can easily work with any existing instrumentation.

### Configure tracing
Currently, Datadog APM includes native support for tracing Lambda functions written in [Node.js](https://github.com/DataDog/dd-trace-js), with support for Ruby and Python coming soon. To get started, you will need to [set up (or upgrade)][native-tracing-docs] Datadog's Lambda Layer and Lambda Forwarder for your function.  Once configured, you can instrument your function code:

{{<code-snippet lang="javascript" filename="index.js" wrap="false" >}} 
const { datadog } = require("datadog-lambda-js");
const tracer = require("dd-trace").init(); // Any manual tracer config goes here.

// This function will be wrapped in a span
const myFunction = tracer.wrap("my-function", () => {
 [...]
});

// This function will also be wrapped in a span, (based on the current function ARN).
module.exports.hello = datadog((event, context, callback) => {
  myFunction();
  callback(null, {
    statusCode: 200,
    body: "Hello from Lambda!"
  });
});
{{</code-snippet>}} 

If you already use Datadog's [X-Ray integration](https://docs.datadoghq.com/integrations/amazon_xray/?tab=nodejs) for tracing, you can merge APM traces with any relevant X-Ray trace with the `mergeDatadogXrayTraces` option:

{{<code-snippet lang="javascript" filename="index.js" wrap="false" >}} 
const { datadog } = require("datadog-lambda-js");
const tracer = require("dd-trace").init(); // Any manual tracer config goes here.

[...]

// This function will also be wrapped in a span, (based on the current function ARN).
module.exports.hello = datadog((event, context, callback) => {
  await myFunction();
  const response = {
    statusCode: 200,
    body: JSON.stringify('Hello from Lambda!'),
  };
  return response;
  }, { mergeDatadogXrayTraces: true });
});
{{</code-snippet>}} 

Check out [our documentation][native-tracing-docs] for more information about instrumenting your functions.

### Explore your trace data
To start analyzing trace data from your serverless functions, navigate to Datadog's [Serverless view](https://docs.datadoghq.com/infrastructure/serverless/#overview). This view gives a comprehensive look at all of your functions and includes metrics such as invocation count and memory usage. You can search for a specific function or view performance metrics across all your functions. You can also sort your functions in the Serverless view by a specific metric such as invocations, as seen in the example below. 

{{< img src="lambda_serverless_view.png" alt="View all your functions in the Serverless view" border="true">}}

When you click on a function, you will see all of its associated traces and logs as well as the key metrics like the number of invocations, errors, and execution duration.

{{< img src="single_lambda_serverless.png" alt="View traces and logs and key metrics for a single AWS Lambda function in the Serverless view" border="true">}}

Datadog APM automatically generates a Service Map based on your trace data, so you can visualize all your Lambda functions in one place and understand the flow of traffic across microservices in your environment. 

{{< img src="lambda_service_map_updated.png" alt="View a service map of your AWS Lambda functions and connected services" border="true">}}

You can also analyze and explore your Lambda trace data with [App Analytics](https://docs.datadoghq.com/tracing/app_analytics/?tab=java#pagetitle). By using any combination of tags, you can quickly filter down to a specific service or function. App Analytics also uses the tags that are automatically created with Datadog's Lambda Layer so you can filter functions by tags such as `cold_start:true`. The graph below displays the top five functions with cold starts over time, broken down by function name. If you like, you can easily export this to a monitor or dashboard.

{{< img src="lambda_app_analytics.png" alt="Analyze your functions with App Analytics" border="true">}}

So far, we've shown you how to collect and analyze data with Datadog's Lambda integration and Lambda Layer. Now that all of your function data is flowing into Datadog, we'll explore how you can get more out of your data with Datadog's predictive monitoring and alerts.

## Monitor AWS Lambda logs with Datadog
Datadog provides a Lambda-based log forwarder that you can use to send logs and other telemetry to your account such as Amazon S3 events and Amazon Kinesis data stream events. You can deploy this function to your AWS account using the provided [CloudFormation stack](https://github.com/DataDog/datadog-serverless-functions/tree/master/aws/logs_monitoring#datadog-forwarder). [Lambda applications](https://docs.aws.amazon.com/lambda/latest/dg/deploying-lambda-apps.html) use CloudFormation to package functions, AWS resources, and event sources together in order to perform specific tasks. When you deploy Datadog's Lambda Forwarder as an application, AWS will automatically create the Lambda function with the appropriate role, add Datadog's Lambda Layer, and create relevant tags that you can search on in Datadog like `functionname` and `cloud_provider`. 

Because the log forwarder is a Lambda function, it relies on triggers to execute, which you can let Datadog [automatically set up](https://docs.datadoghq.com/integrations/amazon_web_services/?tab=allpermissions#automatically-setup-triggers) for you. You can choose which AWS services the log forwarder should start collecting logs from (e.g., Lambda, S3, classic ELBs) in the **Collect Logs** tab of your Datadog account's [AWS integration tile](https://app.datadoghq.com/account/settings#integrations/amazon_web_services). Alternatively, you can [manually set up triggers](https://docs.datadoghq.com/integrations/amazon_web_services/?tab=allpermissions#manually-setup-triggers) on S3 buckets or CloudWatch log groups. Once configured, Datadog's Lambda Forwarder will begin sending logs from Lambda (and any other AWS services you've configured) to your Datadog account.

### Search and analyze your Lambda logs
Datadog enables you to search on, analyze, and easily discover patterns in your logs. You can use identifiers such as the function's log group or name to search for your logs in the Log Explorer, as seen in the example below.

{{< img src="lambda_log_explorer.png" alt="Explore your AWS Lambda logs in the Log Explorer" border="true">}}

Lambda functions generate a large volume of logs, making it difficult to pinpoint issues during an incident or simply monitor the current state of your functions. You can use [Log Patterns](https://www.datadoghq.com/blog/log-patterns/) to help you surface interesting trends in your logs.

For example, if you notice a spike in Lambda errors on your dashboard, you can use Log Patterns to quickly search for the most common types of errors. In the example below, you can see a cluster of function logs for an `AccessDeniedException` permissions error. The logs provide a stack trace so you can troubleshoot further. 

{{< img src="lambda_log_patterns.png" alt="Quickly point out patterns in your AWS Lambda logs with Log Patterns" border="true">}}

When you select a pattern, you can click on the **View All** button to pivot to the Log Explorer and inspect individual logs that exhibit that pattern, or you can [analyze trends in your logs](https://docs.datadoghq.com/logs/explorer/analytics/?tab=timeseries#overview) by clicking on the **Graph** button. For example, you can view the most invoked functions or a top list of the most common function errors. You can then export the graph to a Lambda dashboard to monitor it alongside real-time performance data from your functions. 

{{< img src="lambda_errors_export.png" alt="Visualize your logs with Log Analytics and export to a dashboard" border="true">}}


## Proactively monitor AWS Lambda with alerts
Once you're aggregating all your Lambda metrics, logs, and traces with Datadog, you can automatically detect anomalies and forecast trends in key Lambda metrics. You can also set up alerts to quickly find out about issues. 

### Forecast trends and detect anomalies in AWS Lambda functions
As mentioned earlier, Datadog generates enhanced metrics from your function code and Lambda logs that help you track data such as errors in near real time, memory usage, and estimated costs. You can apply [anomaly detection](https://www.datadoghq.com/blog/introducing-anomaly-detection-datadog/) to metrics like max memory used (e.g., `aws.lambda.enhanced.max_memory_used`) in order to see any unusual trends in memory usage.

{{< img src="lambda_memory_anomalies.png" alt="View anomalies in memory usage for your Lambda functions" border="true">}}

You can also apply a forecast to the `estimated_cost` metric to determine if your costs are expected to increase, based on historical data.

{{< img src="lambda_forecast.png" alt="Forecast trends in your AWS Lambda functions" border="true">}}

### Alert on critical AWS Lambda metrics
Monitoring Lambda enables you to visualize trends and identify issues during critical outages, but it's easy to overlook an issue when you are monitoring a large volume of datapoints in complex infrastructures. In order to ensure that you are aware of critical issues affecting your applications, you can create monitors to get notified about key issues detected in the Lambda metrics logs, or traces. 

For example, you can create an alert to notify you if a function has been throttled frequently over a specific period of time. If you configure the alert to automatically trigger separate notifications per affected function, this saves you from creating duplicate alerts and enables you to get continuous, scalable coverage of your environment, no matter how many functions you're running. 

{{< img src="lambda_alert.png" alt="Create alerts on key AWS Lambda metrics" border="true">}}

Throttles occur when there is not enough capacity for a function, either because available concurrency is used up or because requests are coming in faster than the function can scale. You can use an alert to notify you if you are reaching the threshold of concurrent executions for your account or per region, as seen below. 

{{< img src="lambda_alert_status.png" alt="View the status of all of your Lambda alerts" border="true">}}

There are several [monitor types](https://docs.datadoghq.com/monitors/monitor_types/), including anomaly detection and forecasts, so you can be notified about only the issues you care about. For example, you can create a forecast alert to notify you a week before you run out of concurrency.

## Start monitoring AWS Lambda with Datadog
In this post, we've looked at how to get deep visibility into all your AWS Lambda functions with Datadog. Once you integrate Lambda with Datadog, you can monitor the performance of your serverless applications, and optimize your functions by analyzing concurrency utilization, memory usage execution costs, and other metrics. And, if you use Lambda@Edge with [Amazon CloudFront](https://docs.datadoghq.com/integrations/amazon_cloudfront/#overview), [Step Functions](https://docs.datadoghq.com/integrations/amazon_step_functions/#overview), or [AppSync](https://docs.datadoghq.com/integrations/amazon_appsync/#overview) on top of your Lambda functions, you can automatically pull in monitoring data from those services with Datadog's built-in integrations. Check out our [AWS documentation](https://docs.datadoghq.com/integrations/#cat-aws) for more information.

If you don’t yet have a Datadog account, sign up for a <a href="#" class="sign-up-trigger">free 14-day trial</a> to start monitoring your AWS Lambda functions today.

_Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/aws-lambda/monitoring-aws-lambda-with-datadog.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues)._

[part-one]: /blog/key-metrics-for-monitoring-aws-lambda/
[part-two]: /blog/tools-for-collecting-aws-lambda-data
[alerts-section]: #alert-on-critical-aws-lambda-metrics
[enhanced-metrics-doc]: https://docs.datadoghq.com/integrations/amazon_lambda/?tab=awsconsole#real-time-enhanced-lambda-metrics
[logs-section]: #monitor-aws-lambda-with-datadog
[anomaly-section]: #forecast-trends-and-detect-anomalies-in-aws-lambda-functions
[native-tracing-docs]: https://docs.datadoghq.com/integrations/amazon_lambda/?tab=awsconsole#tracing-with-datadog-apm
