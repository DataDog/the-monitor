# MySQL monitoring with Datadog


*This is the final post in a 3-part series about MySQL monitoring. [Part 1](https://www.datadoghq.com/blog/monitoring-mysql-performance-metrics/) explores the key metrics available from MySQL, and [Part 2](https://www.datadoghq.com/blog/collecting-mysql-statistics-and-metrics/) explains how to collect those metrics.*

If you’ve already read [our post](https://www.datadoghq.com/blog/collecting-mysql-statistics-and-metrics/) on collecting MySQL metrics, you’ve seen that you have several options for ad hoc performance checks. For a more comprehensive view of your database’s health and performance, however, you need a monitoring system that continually collects MySQL statistics and metrics, that lets you identify both recent and long-term performance trends, and that can help you identify and investigate issues when they arise. This post will show you how to set up comprehensive MySQL monitoring by installing the Datadog Agent on your database servers.

{{< img src="mysql-dash-dd.png" alt="MySQL dashboard in Datadog" popup="true" >}}

Integrate Datadog with MySQL


As explained in [Part 1](https://www.datadoghq.com/blog/monitoring-mysql-performance-metrics/), MySQL exposes hundreds of valuable metrics and statistics about query execution and database performance. To collect those metrics on an ongoing basis, the Datadog Agent connects to MySQL at regular intervals, queries for the latest values, and reports them to Datadog for graphing and alerting.

### Installing the Datadog Agent


Installing the Agent on your MySQL server is easy: it usually requires just a single command, and the Agent can collect basic metrics even if [the MySQL performance schema](https://www.datadoghq.com/blog/collecting-mysql-statistics-and-metrics/#querying-the-performance-schema-and-sys-schema) is not enabled and the sys schema is not installed. Installation instructions for a variety of operating systems and platforms are available [here](https://app.datadoghq.com/account/settings#agent).

### Configure the Agent to collect MySQL metrics


Once the Agent is installed, you need to grant it access to read metrics from your database. In short, this process has four steps:


1. Create a `datadog` user in MySQL and grant it permission to run metric queries on your behalf.
2. Copy Datadog’s `conf.d/mysql.yaml.example` [template][config-template] to `conf.d/mysql.yaml` to create a configuration file for Datadog.
3. Add the login credentials for your newly created `datadog` user to `conf.d/mysql.yaml`.
4. Restart the Agent.

The [MySQL configuration tile](https://app.datadoghq.com/account/settings#integrations/mysql) in the Datadog app has the full instructions, including the exact SQL commands you need to run to create the `datadog` user and apply the appropriate permissions.

### Configure collection of additional MySQL metrics
Out of the box, Datadog collects more than 60 standard metrics from modern versions of MySQL. Definitions and measurement units for most of those standard metrics can be found [here](http://docs.datadoghq.com/integrations/mysql/#metrics).

Starting with Datadog Agent version 5.7, many additional metrics are available by enabling specialized checks in the `conf.d/mysql.yaml` file (see [the configuration template](https://github.com/DataDog/integrations-core/blob/master/mysql/datadog_checks/mysql/data/conf.yaml.example) for context):




        # options:      
          #   replication: false      
          #   galera_cluster: false      
          #   extra_status_metrics: true      
          #   extra_innodb_metrics: true      
          #   extra_performance_metrics: true      
          #   schema_size_metrics: false      
          #   disable_innodb_metrics: false
      
      



To collect average statistics on query latency, as described in [Part 1](https://www.datadoghq.com/blog/monitoring-mysql-performance-metrics/#query-performance) of this series, you will need to enable the `extraperformancemetrics` option and ensure that [the performance schema is enabled](https://www.datadoghq.com/blog/collecting-mysql-statistics-and-metrics/#querying-the-performance-schema-and-sys-schema). The Agent’s `datadog` user in MySQL will also need the [additional permissions](https://app.datadoghq.com/account/settings#integrations/mysql) detailed in the MySQL configuration instructions in the Datadog app.

Note that the `extraperformancemetrics` and `schemasizemetrics` options trigger heavier queries against your database, so you may be subject to performance impacts if you enable those options on servers with a large number of schemas or tables. Therefore you may wish to test out these options on a limited basis before deploying them to production.

Other options include:



-   `extra_status_metrics` to expand the set of server status variables reported to Datadog
-   `extra_innodb_metrics` to collect more than 80 additional metrics specific to the InnoDB storage engine
-   `replication` to collect basic metrics (such as replica lag) on MySQL replicas



To override default behavior for any of these optional checks, simply uncomment the relevant lines of the configuration file (along with the `options:` line) and restart the Agent.

The specific metrics associated with each option are detailed in [the source code](https://github.com/DataDog/integrations-core/blob/master/mysql/datadog_checks/mysql/mysql.py) for the MySQL Agent check.

View your comprehensive MySQL dashboard


{{< img src="mysql-dash-dd.png" alt="MySQL dashboard in Datadog" popup="true" >}}

Once you have integrated Datadog with MySQL, a comprehensive dashboard called “[MySQL - Overview](https://app.datadoghq.com/dash/integration/mysql)” will appear in your list of [integration dashboards](https://app.datadoghq.com/dash/list). The dashboard gathers key MySQL metrics highlighted in [Part 1](https://www.datadoghq.com/blog/monitoring-mysql-performance-metrics/) of this series, along with server resource metrics, such as CPU and I/O wait, which are invaluable for investigating performance issues.

### Customize your dashboard


The Datadog Agent can also collect metrics from the rest of your infrastructure so that you can correlate your entire system’s performance with metrics from MySQL. The Agent collects metrics from [Docker](https://www.datadoghq.com/blog/the-docker-monitoring-problem/), [NGINX](https://www.datadoghq.com/blog/how-to-monitor-nginx/), [Redis](https://www.datadoghq.com/blog/how-to-monitor-redis-performance-metrics/), and more than {{< translate key="integration_count" >}} other applications and services. You can also easily instrument your own application code to [report custom metrics to Datadog using StatsD](https://www.datadoghq.com/blog/statsd/).

To add more metrics from MySQL or related systems to your MySQL dashboard, simply clone [the template dash](https://app.datadoghq.com/dash/integration/mysql) by clicking on the gear in the upper right.

Conclusion


In this post we’ve walked you through integrating MySQL with Datadog so you can access all your database metrics in one place, whether standard metrics from MySQL, more detailed metrics from the InnoDB storage engine, or automatically computed metrics on query latency.

Monitoring MySQL with Datadog gives you critical visibility into what’s happening with your database and the applications that depend on it. You can easily create automated alerts on any metric, with triggers tailored precisely to your infrastructure and your usage patterns.

If you don’t yet have a Datadog account, you can sign up for a <a href="#" class="sign-up-trigger">free trial</a> to start monitoring all your servers, applications, and services today.

[config-template]: https://github.com/DataDog/integrations-core/blob/master/mysql/datadog_checks/mysql/data/conf.yaml.example
