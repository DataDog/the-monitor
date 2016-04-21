*This is the final post in a 3-part series about MySQL monitoring. [Part 1][part-1] explores the key metrics available from MySQL, and [Part 2][part-2] explains how to collect those metrics.*

If you’ve already read [our post][part-2] on collecting MySQL metrics, you’ve seen that you have several options for ad hoc performance checks. For a more comprehensive view of your database's health and performance, however, you need a monitoring system that continually collects MySQL statistics and metrics, that lets you identify both recent and long-term performance trends, and that can help you identify and investigate issues when they arise. This post will show you how to set up comprehensive MySQL monitoring by installing the Datadog Agent on your database servers.

[![MySQL dashboard in Datadog][dash-img]][dash-img]

## Integrate Datadog with MySQL
As explained in [Part 1][part-1], MySQL exposes hundreds of valuable metrics and statistics about query execution and database performance. To collect those metrics on an ongoing basis, the Datadog Agent connects to MySQL at regular intervals, queries for the latest values, and reports them to Datadog for graphing and alerting.

### Installing the Datadog Agent 

Installing the Agent on your MySQL server is easy: it usually requires just a single command, and the Agent can collect basic metrics even if [the MySQL performance schema][p_s] is not enabled and the sys schema is not installed. Installation instructions for a variety of operating systems and platforms are available [here][agent-install].

### Configure the Agent to collect MySQL metrics

Once the Agent is installed, you need to grant it access to read metrics from your database. In short, this process has four steps:

1. Create a `datadog` user in MySQL and grant it permission to run metric queries on your behalf.
2. Copy Datadog's `conf.d/mysql.yaml.example` [template][conf] to `conf.d/mysql.yaml` to create a configuration file for Datadog. 
3. Add the login credentials for your newly created `datadog` user to `conf.d/mysql.yaml`.
4. Restart the agent.

The [MySQL configuration tile][mysql-config] in the Datadog app has the full instructions, including the exact SQL commands you need to run to create the `datadog` user and apply the appropriate permissions.

### Configure collection of additional MySQL metrics

Out of the box, Datadog collects more than 60 standard metrics from modern versions of MySQL. Definitions and measurement units for most of those standard metrics can be found [here][metric-list].

Starting with Datadog Agent version 5.7, many additional metrics are available by enabling specialized checks in the `conf.d/mysql.yaml` file (see [the configuration template][conf] for context):

```
    # options:
    #   replication: false
    #   galera_cluster: false
    #   extra_status_metrics: true
    #   extra_innodb_metrics: true
    #   extra_performance_metrics: true
    #   schema_size_metrics: false
    #   disable_innodb_metrics: false
```

To collect average statistics on query latency, as described in [Part 1][runtime] of this series, you will need to enable the `extra_performance_metrics` option and ensure that [the performance schema is enabled][p_s]. The Agent's `datadog` user in MySQL will also need the [additional permissions][mysql-config] detailed in the MySQL configuration instructions in the Datadog app. 

Note that the `extra_performance_metrics` and `schema_size_metrics` options trigger heavier queries against your database, so you may be subject to performance impacts if you enable those options on servers with a large number of schemas or tables. Therefore you may wish to test out these options on a limited basis before deploying them to production.

Other options include:

* `extra_status_metrics` to expand the set of server status variables reported to Datadog
* `extra_innodb_metrics` to collect more than 80 additional metrics specific to the InnoDB storage engine
* `replication` to collect basic metrics (such as replica lag) on MySQL replicas

To override default behavior for any of these optional checks, simply uncomment the relevant lines of the configuration file (along with the `options:` line) and restart the agent. 

The specific metrics associated with each option are detailed in [the source code][checks] for the MySQL Agent check.

## View your comprehensive MySQL dashboard

[![MySQL dashboard in Datadog][dash-img]][dash-img]

Once you have integrated Datadog with MySQL, a comprehensive dashboard called “[MySQL - Overview][mysql-dash]” will appear in your list of [integration dashboards][dash-list]. The dashboard gathers key MySQL metrics highlighted in [Part 1][part-1] of this series, along with server resource metrics, such as CPU and I/O wait, which are invaluable for investigating performance issues.

### Customize your dashboard

The Datadog Agent can also collect metrics from the rest of your infrastructure so that you can correlate your entire system's performance with metrics from MySQL. The Agent collects metrics from [Docker][docker], [NGINX][nginx], [Redis][redis], and 100+ other applications and services. You can also easily instrument your own application code to [report custom metrics to Datadog using StatsD][statsd]. 

To add more metrics from MySQL or related systems to your MySQL dashboard, simply clone [the template dash][mysql-dash] by clicking on the gear in the upper right. 

## Conclusion

In this post we’ve walked you through integrating MySQL with Datadog so you can access all your database metrics in one place, whether standard metrics from MySQL, more detailed metrics from the InnoDB storage engine, or automatically computed metrics on query latency.

Monitoring MySQL with Datadog gives you critical visibility into what’s happening with your database and the applications that depend on it. You can easily create automated alerts on any metric, with triggers tailored precisely to your infrastructure and your usage patterns.

If you don’t yet have a Datadog account, you can sign up for a [free trial][trial] to start monitoring all your servers, applications, and services today.

- - -

*Source Markdown for this post is available [on GitHub][markdown]. Questions, corrections, additions, etc.? Please [let us know][issues].*

[part-1]: https://www.datadoghq.com/blog/monitoring-mysql-performance-metrics/
[part-2]: https://www.datadoghq.com/blog/collecting-mysql-statistics-and-metrics/
[mysql-config]: https://app.datadoghq.com/account/settings#integrations/mysql
[mysql-dash]: https://app.datadoghq.com/dash/integration/mysql
[dd-agent]: https://github.com/DataDog/dd-agent
[agent-install]: https://app.datadoghq.com/account/settings#agent
[statsd]: https://www.datadoghq.com/blog/statsd/
[dash-list]: https://app.datadoghq.com/dash/list
[trial]: https://app.datadoghq.com/signup
[docker]: https://www.datadoghq.com/blog/the-docker-monitoring-problem/
[nginx]: https://www.datadoghq.com/blog/how-to-monitor-nginx/
[redis]: https://www.datadoghq.com/blog/how-to-monitor-redis-performance-metrics/
[elb]: https://www.datadoghq.com/blog/top-elb-health-and-performance-metrics/
[p_s]: https://www.datadoghq.com/blog/collecting-mysql-statistics-and-metrics/#querying-the-performance-schema-and-sys-schema
[checks]: https://github.com/DataDog/dd-agent/blob/master/checks.d/mysql.py
[conf]: https://github.com/DataDog/dd-agent/blob/master/conf.d/mysql.yaml.example
[metric-list]: http://docs.datadoghq.com/integrations/mysql/#metrics
[runtime]: https://www.datadoghq.com/blog/monitoring-mysql-performance-metrics/#query-performance
[dash-img]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2016-04-mysql/mysql-dash-dd.png
[markdown]: https://github.com/DataDog/the-monitor/blob/master/mysql/mysql_monitoring_with_datadog.md
[issues]: https://github.com/DataDog/the-monitor/issues

