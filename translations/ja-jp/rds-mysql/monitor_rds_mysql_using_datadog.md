# Monitor RDS MySQL using Datadog

*This post is part 3 of a 3-part series on monitoring MySQL on Amazon RDS. [Part 1][part-1] explores the key metrics available from RDS and MySQL, and [Part 2][part-2] explains how to collect both types of metrics.*

If you’ve already read [our post][part-2] on collecting MySQL RDS metrics, you’ve seen that you can easily collect metrics from RDS and from MySQL itself to check on your database. For a more comprehensive view of your database's health and performance, however, you need a monitoring system that can integrate and correlate RDS metrics with native MySQL metrics, that lets you identify both recent and long-term trends in your metrics, and that can help you identify and investigate performance problems. This post will show you how to connect MySQL RDS to Datadog for comprehensive monitoring in two steps:

* [Connect Datadog to CloudWatch to gather RDS metrics](#connect-datadog-to-cloudwatch)
* [Integrate Datadog with MySQL to gather native metrics](#integrate-datadog-with-mysql)

<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/rds_dd_diagram.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/rds_dd_diagram.png"></a> 

<h2 class="anchor" id="connect-datadog-to-cloudwatch">Connect Datadog to CloudWatch</h2>

To start monitoring RDS metrics, you only need to configure our [integration with AWS CloudWatch][aws-integration], Amazon's metrics and monitoring service. Create a new user via [the IAM console][iam] in AWS and grant that user (or group of users) read-only permissions to these three services, at a minimum:

1. EC2
1. CloudWatch 
1. RDS 

You can attach managed [policies][policy] for each service by clicking on the name of your user in the IAM console and selecting "Permissions," or by using the Amazon API.

Once these settings are configured within AWS, create access keys for your read-only user and enter those credentials in [the AWS integration tile][aws-tile] on Datadog to start pulling RDS data.

Note that if you are using ELB, ElastiCache, SNS, or other AWS products in addition to RDS, you may need to grant additional permissions to the user. [See here][aws-integration] for the complete list of permissions required to take full advantage of the Datadog–AWS integration.

<h2 class="anchor" id="integrate-datadog-with-mysql">Integrate Datadog with MySQL</h2>
As explained in [Part 1][part-1], RDS provides you with several valuable metrics that apply to MySQL, Postgres, SQL Server, or any of the other supported RDS database engines. To collect metrics specifically tailored to MySQL, however, you must monitor the MySQL instance itself. 

### Installing the Datadog Agent on EC2

[Datadog's Agent][dd-agent] integrates seamlessly with MySQL to gather and report key performance metrics, many of which are not available through RDS. Where the same metrics are available through the agent and through RDS, agent metrics should be preferred, as they are reported at a higher resolution. Installing the Agent is easy: it usually requires just a single command, and the Agent can collect metrics even if [the MySQL performance schema][p_s] is not enabled and the sys schema is not installed. Installation instructions for different operating systems are available [here][agent-install].

Because RDS does not provide you direct access to the machines running MySQL, you cannot install the Agent on the MySQL instance to collect metrics locally. Instead you must run the Agent on another machine, often an EC2 instance in the same security group. See [Part 2][remote-ec2] of this series for more on accessing MySQL via EC2.

### Configuring the Agent for RDS

Collecting MySQL metrics from an EC2 instance is quite similar to running the Agent alongside MySQL to collect metrics locally, with two small exceptions:

1. Instead of `localhost` as the server name, provide the Datadog Agent with your RDS instance endpoint (e.g., `instance_name.xxxxxxx.us-east-1.rds.amazonaws.com`)
1. Tag your MySQL metrics with the DB instance identifier (`dbinstanceidentifier:instance_name`) to separate database metrics from the host-level metrics of your EC2 instance

The RDS instance endpoint and DB instance identifier are both available from the AWS console. Complete instructions for configuring the Agent to capture MySQL metrics from RDS are available [here][dd-doc].

### Unifying your metrics

Once you have set up the Agent, all the metrics from your database instance will be uniformly tagged with  `dbinstanceidentifier:instance_name` for easy retrieval, whether those metrics come from RDS or from MySQL itself.

## View your comprehensive MySQL RDS dashboard

Once you have integrated Datadog with RDS, a comprehensive dashboard called “Amazon - RDS (MySQL)” will appear in your list of [integration dashboards][dash-list]. The dashboard gathers the metrics highlighted in [Part 1][part-1] of this series: metrics on query throughput and performance, along with key metrics around resource utilization, database connections, and replication status.

<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/rds-dash-load.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/rds-dash-load.png"></a> 

By default the dashboard displays native MySQL metrics from all reporting instances, as well as RDS metrics from all instances running MySQL. You can focus on one particular instance by selecting a `dbinstanceidentifier` variable in the upper left.  

<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/db-id.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/db-id.png"></a> 

### Customize your dashboard

The Datadog Agent can also collect metrics from the rest of your infrastructure so that you can correlate your entire system's performance with metrics from MySQL. The Agent collects metrics from [ELB][elb], [NGINX][nginx], [Redis][redis], and 100+ other infrastructural applications. You can also easily instrument your own application code to [report custom metrics to Datadog using StatsD][statsd]. 

Once you have multiple systems reporting metrics to Datadog, you will likely want to build custom dashboards or modify your default dashboards to suit your use case: 

* Add new graphs to track application metrics alongside associated database metrics
* Add counters to track custom key performance indicators (e.g., number of users signed in)
* Add metric thresholds (e.g., normal/warning/critical) to your graphs to aid visual inspection

<a href="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/annotated_graph-2.png"><img src="https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-mysql-rds/annotated_graph-2.png"></a> 

To start customizing, clone the default RDS MySQL dashboard by clicking on the gear on the upper right of the default dashboard. (If you are running Aurora or MariaDB on RDS, you can easily use the same dashboard. Simply change the scope of the metric queries in the graphs from `engine:mysql` to, for instance, `engine:mariadb`.)

## Conclusion

In this post we’ve walked you through integrating RDS MySQL with Datadog so you can access all your database metrics in one place.

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