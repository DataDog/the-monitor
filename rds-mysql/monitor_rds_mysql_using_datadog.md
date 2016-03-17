# Monitor RDS MySQL using Datadog

*This post is part 3 of a 3-part series on monitoring MySQL on Amazon RDS. [Part 1][part-1] explores the key metrics available from RDS and MySQL, and [Part 2][part-2] explains how to collect both types of metrics.*

If you’ve already read [our post][part-2] on collecting MySQL RDS metrics, you’ve seen that you can easily collect metrics from RDS and from MySQL itself to check on your database. For a more comprehensive view of your database's health and performance, however, you need a monitoring system that can integrate and correlate RDS metrics with native MySQL metrics, that lets you identify both recent and long-term trends in your metrics, and that can help you identify and investigate performance problems. This post will show you how to connect MySQL RDS to Datadog for monitoring in two steps:

* [Connect Datadog to CloudWatch to gather RDS metrics](#connect-datadog-to-cloudwatch)
* [Integrate Datadog with MySQL to gather native metrics](#integrate-datadog-with-mysql)

For an even more expansive view of your database instances, you can enable the new RDS [enhanced monitoring][aws-enhanced] feature, which provides more than 50 system-level metrics at a frequency as high as once per second. Those metrics can be ingested into Datadog for monitoring in just minutes:

* [Monitor RDS enhanced metrics with Datadog](#monitor-rds-enhanced-metrics-with-datadog)

## Connect Datadog to CloudWatch

<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/rds_dd_diagram.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/rds_dd_diagram.png"></a> 

To start monitoring RDS metrics, you only need to configure our [integration with AWS CloudWatch][aws-integration], Amazon's metrics and monitoring service. Create a new user via [the IAM console][iam] in AWS and grant that user (or group of users) read-only permissions to these three services, at a minimum:

1. EC2
1. CloudWatch 
1. RDS 

You can attach managed [policies][policy] for each service by clicking on the name of your user in the IAM console and selecting "Permissions," or by using the Amazon API.

Once these settings are configured within AWS, create access keys for your read-only user and enter those credentials in [the AWS integration tile][aws-tile] on Datadog to start pulling RDS data.

Note that if you are using ELB, ElastiCache, SNS, or other AWS products in addition to RDS, you may need to grant additional permissions to the user. [See here][aws-integration] for the complete list of permissions required to take full advantage of the Datadog–AWS integration.

## Integrate Datadog with MySQL</h2>
As explained in [Part 1][part-1], RDS provides you with several valuable metrics that apply to MySQL, Postgres, SQL Server, or any of the other supported RDS database engines. To collect metrics specifically tailored to MySQL, however, you must monitor the MySQL instance itself. 

### Installing the Datadog Agent on EC2

[Datadog's Agent][dd-agent] integrates seamlessly with MySQL to gather and report key performance metrics, many of which are not available through RDS. Where the same metrics are available through the Agent and through basic CloudWatch metrics, Agent metrics should be preferred, as they are reported at a higher resolution. Installing the Agent is easy: it usually requires just a single command, and the Agent can collect metrics even if [the MySQL performance schema][p_s] is not enabled and the sys schema is not installed. Installation instructions for different operating systems are available [here][agent-install].

Because RDS does not provide you direct access to the machines running MySQL, you cannot install the Agent on the MySQL instance to collect metrics locally. Instead you must run the Agent on another machine, often an EC2 instance in the same security group. See [Part 2][remote-ec2] of this series for more on accessing MySQL via EC2.

### Configuring the Agent for RDS

Collecting MySQL metrics from an EC2 instance is quite similar to running the Agent alongside MySQL to collect metrics locally, with two small exceptions:

1. Instead of `localhost` as the server name, provide the Datadog Agent with your RDS instance endpoint (e.g., `instance_name.xxxxxxx.us-east-1.rds.amazonaws.com`)
1. Tag your MySQL metrics with the DB instance identifier (`dbinstanceidentifier:instance_name`) to separate database metrics from the host-level metrics of your EC2 instance

The RDS instance endpoint and DB instance identifier are both available from the AWS console. Complete instructions for configuring the Agent to capture MySQL metrics from RDS are available [here][dd-doc].

### Unifying your metrics

Once you have set up the Agent, all the metrics from your database instance will be uniformly tagged with  `dbinstanceidentifier:instance_name` for easy retrieval, whether those metrics come from RDS or from MySQL itself.

## View your comprehensive MySQL RDS dashboard

Once you have integrated Datadog with RDS, a comprehensive dashboard called “[Amazon - RDS (MySQL)][rds-mysql-dash]” will appear in your list of [integration dashboards][dash-list]. The dashboard gathers the metrics highlighted in [Part 1][part-1] of this series: metrics on query throughput and performance, along with key metrics around resource utilization, database connections, and replication status.

<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/rds-dash-load.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/rds-dash-load.png"></a> 

By default the dashboard displays native MySQL metrics from all reporting instances, as well as RDS metrics from all instances running MySQL. You can focus on one particular instance by selecting a `dbinstanceidentifier` variable in the upper left.  

<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/db-id.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/db-id.png"></a> 

### Customize your dashboard

The Datadog Agent can also collect metrics from the rest of your infrastructure so that you can correlate your entire system's performance with metrics from MySQL. The Agent collects metrics from [ELB][elb], [NGINX][nginx], [Redis][redis], and 100+ other infrastructural applications. You can also easily instrument your own application code to [report custom metrics to Datadog using StatsD][statsd]. 

To add more metrics from MySQL or other systems to your RDS dashboard, clone [the template dash][rds-mysql-dash] by clicking on the gear in the upper right. 

## Monitor RDS enhanced metrics with Datadog
AWS [recently announced][aws-enhanced] enhanced monitoring for RDS instances running MySQL, MariaDB, and Aurora. Enhanced monitoring includes more than 50 new CPU, memory, file system, and disk I/O metrics that can be collected on a per-instance basis as frequently as once per second. 

[AWS has worked with Datadog][aws-guest-post] to help customers monitor this new, high-resolution data. With a few minutes of work your enhanced RDS metrics will immediately begin populating a pre-built, customizable dashboard in Datadog.
[![Pre-built Datadog RDS dashboard with enhanced metrics](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/AWS-RDS-enhanced-monitoring-Datadog-dashboard-2.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/AWS-RDS-enhanced-monitoring-Datadog-dashboard-2.png)

### Connect RDS to Datadog

When you enable enhanced RDS metrics, the metrics will be written to CloudWatch Logs. You will then use a [Lambda] function to process those metrics and send them to Datadog. Enhanced metrics can be collected even if you do not use the Datadog Agent to monitor your RDS instances. 

#### Enable enhanced metrics reporting to CloudWatch logs
You can enable enhanced RDS metrics during instance creation, or on an existing RDS instance by selecting it in the [RDS Console][rds-console] and then choosing Instance Options &#8594; Modify:
![UI for enabling enhanced RDS monitoring](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/AWS-RDS-enhanced-monitoring-dialog.png)

Set "Granularity" to 1–60 seconds; every 15 seconds is often a good choice. These metrics will be sent to CloudWatch logs.

#### Send CloudWatch log data to Datadog
Next you can use a ready-made Lambda function to process the logs and send the metrics to Datadog.

1. Create a [role for your Lambda function][iam-roles]. Name it something like `lambda-datadog-enhanced-rds-collector` and select "AWS Lambda" as the role type. ![Role type selector](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/AWS-RDS-enhanced-monitoring-role-type.png)
2. From the **Encryption Keys** tab on the IAM Management Console, create a new encryption key. Enter an Alias for the key like `lambda-datadog-key`. On the next page, add the appropriate administrators for the key. Next you'll be prompted to add users to the key. Add at least two: yourself (so that you can *encrypt* the Datadog API key from the AWS CLI in the next step), and the role created above, e.g. `lambda-datadog-enhanced-rds-collector` (so that it can *decrypt* the API key and submit metrics to Datadog). Finish creating the key.
3. Encrypt the token using the [AWS CLI][aws-cli], providing the Alias of your just-created key (e.g. `lambda-datadog-key`) as well as your Datadog keys, available [here][dd-api-keys]:
    ```
    $ aws kms encrypt --key-id alias/<Alias key name> --plaintext '{"api_key":"<datadog_api_key>", "app_key":"<datadog_app_key>"}'
    ``` 
    You'll need the output of this command in the next steps.
4. From the [Lambda Management Console][lambda-console], create a new Lambda Function. Filter blueprints by "datadog", and select the "datadog-process-rds-metrics" blueprint.
5. Choose RDSOSMetrics from the Log Group dropdown, enter anything as a Filter Name, and click **Next**. Note that you must have [enabled enhanced metrics](#enable-enhanced-metrics-reporting-to-cloudwatch-logs) before RDSOSMetrics will appear as an option.
![Set up Datadog Lambda blueprent](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/AWS-RDS-enhanced-monitoring-datadog-blueprint.png)
6. Give your function a name like `send-enhanced-rds-to-datadog`. In the Lambda function code area, replace the string after KMS_ENCRYPTED_KEYS with the ciphertext blob part of the CLI command output above. ![Configure Datadog Lambda blueprint](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/AWS-RDS-enhanced-monitoring-datadog-blueprint-config.png)
7. Under "Lambda function handler and role", choose the role you created earlier, e.g. `lambda-datadog-enhanced-rds-collector`. Go to the next page, select the **Enable Now** radio button, and create your function.

### Customize your enhanced metrics dashboard
Once you have enabled "RDS" in [Datadog's AWS integration tile][aws-tile], Datadog will immediately begin displaying your enhanced RDS metrics. You can clone the [pre-built dashboard][enhanced-metrics-dash] for enhanced metrics and customize it however you want: add MySQL-specific metrics that are not displayed by default, or start correlating database metrics with the performance of the rest of your stack.

## Conclusion

In this post we’ve walked you through integrating RDS MySQL with Datadog so you can access all your database metrics in one place, whether standard metrics from MySQL and CloudWatch or enhanced metrics from RDS.

Monitoring RDS with Datadog gives you critical visibility into what’s happening with your database and the applications that depend on it. You can easily create automated alerts on any metric, with triggers tailored precisely to your infrastructure and your usage patterns.

If you don’t yet have a Datadog account, you can sign up for a [free trial][trial] and start monitoring your cloud infrastructure, your applications, and your services today.

- - -

*Source Markdown for this post is available [on GitHub][markdown]. Questions, corrections, additions, etc.? Please [let us know][issues].*

[markdown]: https://github.com/DataDog/the-monitor/blob/master/rds-mysql/monitor_rds_mysql_using_datadog.md
[issues]: https://github.com/DataDog/the-monitor/issues
[part-1]: https://www.datadoghq.com/blog/monitoring-rds-mysql-performance-metrics
[part-2]: https://www.datadoghq.com/blog/how-to-collect-rds-mysql-metrics
[aws-integration]: http://docs.datadoghq.com/integrations/aws/
[iam]: https://console.aws.amazon.com/iam/home
[policy]: https://console.aws.amazon.com/iam/home?#policies
[aws-tile]: https://app.datadoghq.com/account/settings#integrations/amazon_web_services
[dd-agent]: https://github.com/DataDog/dd-agent
[agent-install]: https://app.datadoghq.com/account/settings#agent
[remote-ec2]: https://www.datadoghq.com/blog/how-to-collect-rds-mysql-metrics#connecting-to-your-rds-instance
[dd-doc]: http://docs.datadoghq.com/integrations/rds/
[statsd]: https://www.datadoghq.com/blog/statsd/
[dash-list]: https://app.datadoghq.com/dash/list
[trial]: https://app.datadoghq.com/signup
[nginx]: https://www.datadoghq.com/blog/how-to-monitor-nginx/
[redis]: https://www.datadoghq.com/blog/how-to-monitor-redis-performance-metrics/
[elb]: https://www.datadoghq.com/blog/top-elb-health-and-performance-metrics/
[p_s]: https://www.datadoghq.com/blog/how-to-collect-rds-mysql-metrics#querying-the-performance-schema-and-sys-schema
[aws-enhanced]: https://aws.amazon.com/blogs/aws/new-enhanced-monitoring-for-amazon-rds-mysql-5-6-mariadb-and-aurora/
[aws-guest-post]: https://aws.amazon.com/blogs/aws/using-enhanced-rds-monitoring-with-datadog/
[Lambda]: https://aws.amazon.com/lambda/
[iam-roles]: https://console.aws.amazon.com/iam/home#roles
[aws-cli]: https://aws.amazon.com/cli/
[dd-api-keys]: https://app.datadoghq.com/account/settings#api
[lambda-console]: https://console.aws.amazon.com/lambda/home#/functions
[rds-mysql-dash]: https://app.datadoghq.com/screen/integration/aws_rds_mysql
[enhanced-metrics-dash]: https://app.datadoghq.com/dash/integration/aws_rds_enhanced_metrics
[rds-console]: https://console.aws.amazon.com/rds/home
