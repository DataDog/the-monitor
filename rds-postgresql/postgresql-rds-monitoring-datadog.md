---
authors:
- email: emily.chang@datadoghq.com
  image: img-0791.jpg
  name: Emily Chang
blog/category:
- series datadog
blog/tag:
- rds
- aws
- postgres
- performance
- database
date: 2018-04-12 00:00:03
description: In this post, we'll show you how set up PostgreSQL RDS monitoring with Datadog.
draft: false
image: postgresql-rds-monitoring-datadog-hero.jpg
preview_image: postgresql-rds-monitoring-datadog-hero.jpg
slug: postgresql-rds-monitoring-datadog
technology: rds postgres
title: PostgreSQL RDS monitoring with Datadog
series: rds-postgresql-monitoring
toc_cta_text: Start monitoring RDS PostgreSQL
---

In the [previous post][part-2] of this series on PostgreSQL RDS monitoring, we learned how to access RDS metrics from CloudWatch, and from the PostgreSQL database itself. Because PostgreSQL's built-in `pg_stat_*` statistics views provide cumulative counters for many metrics, an automated monitoring tool can help provide more meaningful insights into how your PostgreSQL metrics are evolving over time. It can also help provide more context when troubleshooting, by enabling you to compare and correlate RDS PostgreSQL data with metrics from other services throughout your environment. 

In this post, we will show you how to set up Datadog to automatically collect all of the key metrics covered in [Part 1][part-1] in two steps:

- Access CloudWatch metrics with [Datadog's AWS RDS integration](#collect-cloudwatch-metrics-for-postgresql-rds-monitoring)
- Query metrics directly from the database instance with the [PostgreSQL integration](#beyond-rds-querying-metrics-directly-from-postgresql)

We'll also show you how to get even more visibility into your RDS database instances (and the applications that rely on them) by:  

- setting up [RDS enhanced metrics](#enhanced-rds-metrics-in-datadog) with Datadog
- [deploying Datadog's distributed tracing and APM](#tracing-postgresql-rds-requests-in-datadog) to monitor an application that relies on RDS PostgreSQL

## Collect CloudWatch metrics for PostgreSQL RDS monitoring 
Integrating Datadog with AWS CloudWatch enables you to aggregate metrics from all of your AWS services so that you can visualize and alert on them from one central platform. If you're new to Datadog, you can sign up for a <a href="#" class="sign-up-trigger">14-day free trial</a> to follow along with the rest of this guide.

Datadog's [AWS CloudWatch integration][datadog-aws-docs] requires read-only access to your AWS account. You'll need to create a role (e.g., `DatadogAWS`) in the [AWS IAM Console][aws-iam], and attach a policy that provides your role with the necessary permissions to access metrics through the CloudWatch API, as explained in the [documentation][datadog-aws-docs].  

Once you're done creating your AWS role, navigate to the [AWS integration tile][datadog-aws-tile] in Datadog and fill in your AWS account ID and the name of your role in the "Role Delegation" section of the Configuration tab. Make sure to check off "RDS" (and any other AWS services you wish to monitor) under "Limit metric collection." If you'd like to monitor other AWS services in Datadog, check the [documentation][datadog-aws-docs] to see which additional permissions your role will need.  

{{< img src="postgresql-rds-monitoring-data-aws-tile.png" alt="PostgreSQL RDS monitoring data collection through Datadog integration" popup="true" >}}

By default, your CloudWatch RDS metrics will automatically be tagged in Datadog with metadata about each database instance, including:  

- `dbinstanceidentifier`: name of the database instance (determined in the initial setup process, and accessible in the AWS RDS console)  
- `dbinstanceclass`: [instance class][aws-instance-class] of the database instance  
- `dbname`: name of the database  
- `engine`: name of the database engine running on the instance 
- `engineversion`: version of the database engine this instance is using  
- `region`: AWS region where your instance is located  

These tags will be structured in `key:value` format. For example, all of your RDS PostgreSQL metrics will be tagged with `engine:postgres`. Tags give you the [power to slice and dice your metrics][tags-blog] by any dimension. For example, you can filter your RDS dashboard to view metrics from database instances located in a specific region, or limit your view to metrics from just one database instance at a time. Datadog will also ingest any [custom CloudWatch tags][rds-custom-tags] you may have added to your RDS database instances.

## Beyond RDS: Querying metrics directly from PostgreSQL
As mentioned in [Part 1][part-1], a comprehensive approach to PostgreSQL RDS monitoring will require you to collect PostgreSQL metrics that are not available in CloudWatch. These metrics will need to be accessed directly from the database itself. With [Datadog's PostgreSQL integration][dd-postgres-docs], you can automatically query key PostgreSQL data from each RDS instance and visualize and alert on those metrics in one central platform. 
 
### Installing the Datadog Agent on your EC2 instance
The Datadog Agent is [open source software][github-agent] that integrates with PostgreSQL and more than {{< translate key="integration_count" >}} other technologies. You cannot deploy the Datadog Agent directly on your PostgreSQL instance, since AWS RDS does not provide direct access to your database instance's host. Instead, you'll need to install the Agent on another server that can access your database, such as an EC2 instance in the same security group as your RDS instance. [Consult the documentation][dd-agent-docs] for OS-specific installation steps. 

Once you have installed the Agent on your server, and set up the server to connect to your PostgreSQL database on RDS (consult [Part 2][setup-ec2] for instructions), you are ready to configure the Agent to forward PostgreSQL metrics to Datadog. 
 
### Connecting the Agent to PostgreSQL
In order to configure the Agent to query and forward PostgreSQL database metrics to Datadog, you'll need to initialize a `psql` session from your EC2 instance, create a user for the Datadog Agent, and give that user permission to access statistics from `pg_stat_database`.   

You'll need to log into a `psql` session as a user that has [CREATEROLE privileges][create-user-docs]); see [Part 2][part-2] for more details. Once you've connected, create a `datadog` user and grant it read access to `pg_stat_database`:

```
create user datadog with password '<PASSWORD>';
grant SELECT ON pg_stat_database to datadog;
```

Exit the `psql` session and run this command from your EC2 instance to confirm that the `datadog` user can access your metrics:

```
psql -h <DB_INSTANCE_ENDPOINT> -U datadog postgres -c \ "select * from pg_stat_database LIMIT(1);" && echo -e "\e[0;32mPostgres connection - OK\e[0m" || \ || echo -e "\e[0;31mCannot connect to Postgres\e[0m"
```

You'll be prompted to enter the password for your `datadog` user. After you've done so, you should see the following output: `Postgres connection - OK`.  

### Configure the Agent to collect PostgreSQL metrics
Now it's time to create a configuration file that tells the Agent how to access PostgreSQL metrics from RDS. The Agent comes bundled with an [example configuration file for PostgreSQL][dd-pg-conf-file] that you can modify to your liking. The location of this file varies according to your OS and platform—consult the [documentation][dd-agent-config] for details on where to locate the file. 

Create a copy of the example configuration file and edit it with the information that the Datadog Agent needs to access metrics from your RDS instance. The example below instructs the Agent to access an RDS database instance through the default port (5432), using the `datadog` user and password we just created. You can also add custom tag(s) to your PostgreSQL metrics, and limit metric collection to specific schemas, if desired. We recommend adding a `dbinstanceidentifier:<DB_INSTANCE_IDENTIFIER>` tag to unify your RDS and PostgreSQL metrics. If you wish to collect and track table-level metrics (such as the amount of disk space used per table), add each table to the `relations` section of the YAML file. 

```
init_config:

instances:
  - host: <DB_INSTANCE_ENDPOINT>
    port: 5432
    username: datadog
    password: <PASSWORD>
    dbname: <DATABASE_NAME>
    tags:
      - dbinstanceidentifier:<DB_INSTANCE_IDENTIFIER>
    relations:
      - <TABLE_YOU_WANT_TO_MONITOR>
```

Save your changes as `conf.yaml`, restart the Agent, and run the status command to verify that it is collecting PostgreSQL metrics from your RDS database instance. These commands vary according to your OS; [consult the documentation][dd-agent-docs] to find instructions for your platform. 

If everything is configured correctly, you should see a section like this in the output:  

```
    postgres
    --------
      Total Runs: 2
      Metrics: 81, Total Metrics: 162
      Events: 0, Total Events: 0
      Service Checks: 1, Total Service Checks: 2
```

If you added the custom tag to your Datadog Agent's PostgreSQL configuration file as shown in the example above, your PostgreSQL metrics should be tagged with the name of your RDS instance (`dbinstanceidentifier:<NAME_OF_YOUR_INSTANCE>`). This enables you to unify metrics from the same database instance, whether they were collected from CloudWatch or directly from PostgreSQL. For example, the dashboard below enables use to compare a PostgreSQL metric (rows updated) side-by-side with a CloudWatch metric (write I/O operations per second) collected from a specific RDS database instance. 

{{< img src="postgresql-rds-monitoring-metric-comparison.png" alt="postgresql dashboard" wide="true" popup="true" >}}

### Collecting custom PostgreSQL metrics with Datadog
You can also use Datadog's PostgreSQL integration to collect custom metrics that map to specific SQL queries. In the `custom_metrics` section of the Datadog Agent's [example PostgreSQL configuration file][dd-pg-conf-file], you'll see some guidelines about the four main components you'll need to provide:

- `query` to run on your database    
- `metrics` in `key:value` format; each key corresponds to the name of a column from the `query` above. The value is a two-item list, in which the first value is the custom metric name and the second value is the metric type  
- `relation`: true or false, to indicate whether or not you want to query additional per-relation metrics from the tables and schemas listed in the `relations` section of your [integration configuration file](#configure-the-agent-to-collect-postgresql-metrics)   
- `descriptors` to tag your custom metrics; must include the column names in the `query` in the same order as they are queried    

For example, you can send a custom query to the [`pg_stat_activity` view][pg-stat-activity] to continuously gauge the number of applications connected to each of your backends, broken down by application name and user. Normally you'd query the view with something like:

```no-minimize
SELECT 
    application_name, usename, COUNT(*) FROM pg_stat_activity 
WHERE 
    application_name NOT LIKE 'psql' AND (application_name <> '') IS TRUE  
GROUP BY 
    application_name, usename;
 ```
 
You can set up the Agent to automatically query this data for you on a regular basis, and report the results as a custom metric in Datadog. Add your query to the `custom_metrics` section of the Datadog Agent's PostgreSQL configuration file:

```no-minimize
# your-postgres-config-file.yaml

[ ... ]

    custom_metrics:
    - # Capture simple data
      query: SELECT application_name, usename, %s FROM pg_stat_activity WHERE application_name NOT LIKE 'psql' AND (application_name <> '') IS TRUE GROUP BY application_name, usename;
      metrics:
          COUNT(*) as application_count: [postgresql.count_by_applications, GAUGE]
      relation: false
      descriptors:
          - [application_name, application_name]
          - [usename, pg_user]
```

In this example, we set `relation:false` because this query does not involve the `relations` section of our configuration file. Set this to `true` if you wish to gather additional per-relation custom metrics from each of the tables listed in the `relations` section of your integration YAML file. 

Save and exit the file, and restart the Datadog Agent (find the command for your OS [here][agent-docs]). We should now be able to see our custom `postgresql.count_by_applications` metric in Datadog, tagged with the `application_name` and `pg_user`.

{{< img src="postgresql-rds-monitoring-postgresql-custom-metric.png" alt="postgresql dashboard" wide="true" >}}

Consult [the documentation][custom-metrics-docs] and [this article][postgres-custom-doc] to see other examples of useful custom metrics you can collect from your RDS database instance. 

## PostgreSQL RDS monitoring: Customize your dashboard 
Now that you've set up Datadog to integrate with AWS RDS and PostgreSQL, you'll have access to an [out-of-the-box screenboard][rds-screenboard-link] that shows key metrics and events from your RDS PostgreSQL database instances. 

{{< img src="postgresql-rds-monitoring-screenboard-2.png" alt="RDS PostgreSQL data in Datadog's out-of-the-box screenboard" wide="true" popup="true" >}}

Since the Datadog Agent also integrates with {{< translate key="integration_count" >}}+ other technologies—including AWS services like EBS, ELB, and S3—you can clone and customize this dashboard to correlate metrics across all of those services in one place. You can also use the template variables at the top of the dashboard to filter metrics by a specific region, availability zone, or database instance. Remember that all of your RDS metrics will automatically be tagged with metadata about each instance, including its AWS `region` and `dbinstanceidentifier` (the name of your instance). You can also use the `scope` variable to filter RDS metrics using any other tag that can help you get more fine-grained insights into database performance. 

## Enhanced RDS metrics in Datadog
As explained in [Part 1][part-1] of this series, AWS RDS users have the option to enable enhanced monitoring for their PostgreSQL instances at an additional cost (note that this is not available for `db.m1.small` instances). Enhanced monitoring provides access to more than 50 detailed system metrics about your database instances' workload—including process-level memory and CPU usage—at a higher resolution than basic CloudWatch monitoring. Because enhanced monitoring metrics are gathered by an agent running directly on each instance, while CloudWatch metrics are gathered by the hypervisor for the instance, enhanced monitoring metrics provide deeper visibility into the actual work being performed. 

If you choose to enable enhanced monitoring on your RDS instances, you can set up Datadog's integration to help you automatically visualize and alert on your RDS enhanced monitoring metrics. See [our documentation][datadog-rds-docs] for step-by-step instructions. 

{{< img src="postgresql-rds-monitoring-enhanced-monitoring-dashboard2.png" alt="PostgreSQL RDS monitoring enhanced monitoring data in Datadog's out-of-the-box dashboard" popup="true" >}}

Once you enable the integration, you'll have access to a pre-built [RDS Enhanced Monitoring dashboard][rds-enhanced-dashboard], which you can clone, customize, and share with your team. 

## Tracing PostgreSQL RDS requests in Datadog
So far, we've set up PostgreSQL RDS monitoring in Datadog by collecting metrics from our database instances via integrations with CloudWatch and PostgreSQL. Now we can get visibility into the actual applications or services that need to access data from RDS by setting up distributed tracing and APM. If you're using Datadog to monitor [key metrics from your RDS PostgreSQL instances][part-1], correlating and comparing these metrics to application-level performance can help you dig deeper and investigate the source of increased latency or errors—is it an issue with your code, or a problem with the underlying infrastructure?

APM is packaged in the same lightweight, open source Datadog Agent that we already deployed on our EC2 instance, so we won't need to install anything else in order to trace requests to our application. Datadog's distributed tracing and APM can auto-instrument many popular frameworks and libraries in {{< translate key="apm_languages" >}}. For example, the open source Python tracing client includes out-of-the-box support for frameworks like Django, and databases and caches like PostgreSQL and Redis. 

In the following example, we'll show you how to set up the Agent to monitor key service-level metrics and [trace requests to a Django application][django-guide] that is hosted on our AWS EC2 instance. The application reads and writes requests to an RDS PostgreSQL database instance, and uses a Redis caching layer to speed up queries.

### 1. Install the Agent + Python tracing client
Normally, we would install the Datadog Agent on our Django app server. However, in this example, we can skip this step because the application is hosted on the same EC2 instance that we used to configure Datadog's PostgreSQL integration. Follow the instructions [here](#installing-the-datadog-agent-on-your-ec2-instance) if you need to install the Datadog Agent on a different server. Either way, make sure that your application server is able to connect to PostgreSQL on your RDS instance (see [Part 2][setup-ec2] for more details).

Now we need to install the Python tracing client in our environment:

```
pip install ddtrace
```

### 2. Update your Django `settings.py` file
Add the `ddtrace` library to the `INSTALLED_APPS` portion of the Django `settings.py` file:

```
INSTALLED_APPS = [
[...]
    'ddtrace.contrib.django',
]
```

Add a `DATADOG_TRACE` section, making sure to specify the name of your service, along with any custom tags to add to your service-level metrics :

```
DATADOG_TRACE = {
    'DEFAULT_SERVICE': '<MY_SERVICE>',
    'TAGS': {'env': 'myenv'},
}
```

Finally, if you haven't done so already, revise the `DATABASES` section to query the RDS instance:

```no-minimize
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '<DATABASE_NAME>',
        'USER': os.environ['DATABASE_USER'],
        'PASSWORD': os.environ['DATABASE_PASSWORD'],
        'HOST': '<RDS_DATABASE_ENDPOINT>',
        'PORT': '5432',
    }
}
```

`<DB_INSTANCE_ENDPOINT>` is the RDS instance endpoint your application needs to query (e.g., `my-db-instance.xxxxx.us-east-1.rds.amazonaws.com`).

Note that `DEBUG` mode needs to disabled in order for Datadog to trace your application. Save and exit the file. 

### 3. It's `ddtrace-run` time  
To collect request traces and service-level metrics from our application and forward to Datadog, we simply need to wrap the usual command with `ddtrace-run` when firing up our app server:

```
ddtrace-run python manage.py runserver 
```

### Tracing queries to RDS PostgreSQL
Without instrumenting our code at all, the Datadog Agent will automatically start tracing requests to our application, including calls to the database, because it integrates with PostgreSQL out of the box. Navigate to the [APM Services page][datadog-apm] in Datadog and click on the name of your application to view a dashboard of key service-level indicators like latency, throughput, and errors.

{{< img src="postgresql-rds-monitoring-data-service-dash2.png" alt="PostgreSQL RDS monitoring data - Datadog's out-of-the-box service-level dashboard" wide="true" >}}

On the [Trace Search][dd-trace-search] page, you can inspect individual request traces in detailed flame graphs that show the amount of time spent accessing various services throughout our environment. In the request below, we can see that the application is making several calls to the RDS database, and that it spends a small amount of time in Redis. We can dig deeper by clicking on any individual span to view more information, such as the exact SQL query that was executed. 

{{< img src="postgresql-rds-monitoring-data-flamegraph-pg-query.png" alt="PostgreSQL RDS monitoring - data flame graph inspect query" popup="true" wide="true" >}}

The Span Metadata panel displays the number of rows accessed by this query, as well as the RDS host that was queried. When you click on any particular span of a request trace, the [Host Info panel][host-info-blog] provides additional details about the host where this work was executed—in this case, the EC2 instance that is hosting our Django app. We can see the host tags that were inherited from AWS, as well as any custom tags added in the Datadog Agent configuration file. The time of the request trace has also been overlaid across graphs of host-level metrics like CPU, network, and memory. 

{{< img src="postgresql-rds-monitoring-data-host-info.png" alt="PostgreSQL RDS monitoring flame graph inspect host info" popup="true" wide="true" >}}

### Seeing the big picture
Now that we're monitoring our systems, applications, and services in the same platform, we can create custom dashboards that combine key metrics from all of these sources and consult them whenever we need to [troubleshoot or investigate an issue][monitoring-101-investigate]. In the dashboard below, we combined data from EC2, RDS, PostgreSQL, and our Django application to get comprehensive visibility into our deployment in a single pane of glass.   

{{< img src="postgresql-rds-monitoring-combo-dashboard.png" alt="PostgreSQL RDS monitoring - custom dashboard with EC2 and app-level metrics" popup="true" wide="true" >}}

You can also set up alerts to automatically get notified about potential issues in RDS PostgreSQL, such as high replication lag. With [forecasting][datadog-forecasts], you can set up Datadog to automatically notify you a week *before* any RDS database instance is predicted to run out of storage space, giving you enough time to allocate more storage to an instance if needed.  

{{< img src="postgresql-rds-monitoring-data-storage-forecast-2.png" alt="PostgreSQL RDS monitoring - forecast free storage in Datadog" popup="true" wide="true" >}}

You can also add forecasts and other machine learning–powered features like [anomaly detection][dd-anomaly-detection] to your dashboards in order to help you identify potential issues before they impact your users.

## Dive into PostgreSQL RDS monitoring with Datadog
If you've followed along with this guide, you should now have access to comprehensive PostgreSQL RDS monitoring, which will help you get a handle on database performance as you scale your deployment over time. If you're new to Datadog, you can sign up for a 14-day <a href="#" class="sign-up-trigger">free trial</a> to start monitoring PostgreSQL on RDS along with all of your other applications and services.


[part-2]: /blog/collect-rds-metrics-for-postgresql
[part-1]: /blog/aws-rds-postgresql-monitoring
[datadog-aws-docs]: https://docs.datadoghq.com/integrations/amazon_web_services/
[aws-iam]: https://console.aws.amazon.com/iam/home
[datadog-aws-tile]: https://app.datadoghq.com/account/settings#integrations/amazon_web_services
[dd-agent-docs]: https://docs.datadoghq.com/agent/
[agent-docs]: https://docs.datadoghq.com/guides/basic_agent_usage/
[dd-postgres-docs]: https://docs.datadoghq.com/integrations/postgres/
[dd-pg-conf-file]: https://github.com/DataDog/integrations-core/blob/master/postgres/conf.yaml.example
[create-user-docs]: https://www.postgresql.org/docs/current/static/app-createuser.html
[lambda-function]: https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions
[datadog-api]: https://app.datadoghq.com/account/settings#api
[rds-enhanced-dashboard]: hfollttps://app.datadoghq.com/dash/integration/65/aws-rds-enhanced-metrics
[custom-metrics-docs]: https://docs.datadoghq.com/integrations/postgres/#custom-metrics
[postgres-custom-doc]: https://help.datadoghq.com/hc/en-us/articles/208385813-Postgres-custom-metric-collection-explained
[dd-agent-config]: https://docs.datadoghq.com/agent/basic_agent_usage/#configuration-file
[pg-stat-activity]: https://www.postgresql.org/docs/current/static/monitoring-stats.html#PG-STAT-ACTIVITY-VIEW
[datadog-apm]: https://app.datadoghq.com/apm/services
[datadog-rds-docs]: https://docs.datadoghq.com/integrations/amazon_rds/
[rds-custom-tags]: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_Tagging.html
[aws-instance-class]: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html
[tags-blog]: /blog/the-power-of-tagged-metrics/
[setup-ec2]: /blog/collect-rds-metrics-for-postgresql/#connecting-to-your-rds-postgresql-instance
[dd-trace-search]: https://app.datadoghq.com/apm/search
[monitoring-101-investigate]: /blog/monitoring-101-investigation/#build-dashboards-before-you-need-them
[datadog-forecasts]: /blog/forecasts-datadog/
[dd-anomaly-detection]: /blog/introducing-anomaly-detection-datadog/
[host-info-blog]: /blog/host-info-panel/
[rds-screenboard-link]: https://app.datadoghq.com/screen/integration/239/aws-rds-postgresql
[django-guide]: /blog/monitoring-django-performance/
[github-agent]: https://github.com/DataDog/dd-agent