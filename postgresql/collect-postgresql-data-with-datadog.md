---
authors:
- email: emily.chang@datadoghq.com
  image: img-0791.jpg
  name: Emily Chang
blog/category:
- series datadog
blog/tag:
- postgres
- performance
- database
date: 2017-12-15 00:00:03
description: In this post, we'll show you how to use Datadog to monitor key PostgreSQL metrics.
draft: false
image: postgresql-data-monitor-postgresql-performance-hero3.jpg
preview_image: postgresql-data-monitor-postgresql-performance-hero3.jpg
slug: collect-postgresql-data-with-datadog
technology: postgres
title: How to collect and monitor PostgreSQL data with Datadog
series: postgresql-monitoring
toc_cta_text: Start monitoring PostgreSQL
---

If you've already read Parts 1 and 2 of this series, you've learned about the [key metrics to monitor in PostgreSQL][part-1], and [how to start collecting this data][part-2] with native and open source tools. 

Datadog's PostgreSQL integration helps you automatically collect PostgreSQL data from the statistics collector, so that you can monitor everything in one place. And, because Datadog integrates with more than {{< translate key="integration_count" >}} other technologies, you'll be able to correlate metrics from your PostgreSQL servers with other services throughout your environment. 

In this post, we'll walk through the process of installing Datadog on your PostgreSQL servers, so you can visualize database performance in an out-of-the-box screenboard like the one shown below. We'll also show you how to identify bottlenecks in your code by tracing application requests (including PostgreSQL queries) with Datadog APM. 

{{< img src="postgresql-data-monitor-postgresql-dashboard-pt3v3.png" alt="postgresql data - postgresql dashboard" popup="true" wide="true" border="true" >}}

## Datadog's PostgreSQL integration
Instead of querying PostgreSQL metrics manually through the utilities covered in [Part 2][part-2] of this series, you can use the Datadog Agent to automatically aggregate these metrics and make them visible in a customizable template dashboard that shows you how these metrics evolve over time. 

### Install the Datadog Agent
The Datadog Agent is open source software that aggregates and reports metrics from your servers, so that you can graph and alert on them in real time. Installing the Agent usually takes just a single command—to get started, follow the instructions for your platform [here][agent-install].

### GRANT the Agent permission to monitor PostgreSQL
Next, you'll need to give the Agent permission to access statistics from the `pg_stat_database` view, by following the instructions in our [documentation][postgres-datadog-docs]. Basically, you'll need to log into a psql session as a superuser, create a `datadog` user and password, and grant it read access to `pg_stat_database`:

```
create user datadog with password '<PASSWORD>';
grant SELECT ON pg_stat_database to datadog;
```

Run this command on your PostgreSQL server to confirm that the datadog user can access your metrics:

```
psql -h localhost -U datadog postgres -c \ "select * from pg_stat_database LIMIT(1);" && echo -e "\e[0;32mPostgres connection - OK\e[0m" || \ || echo -e "\e[0;31mCannot connect to Postgres\e[0m"
```

You'll be prompted to enter the password you just created for your `datadog` user; once you've done so, you should see the following output: `Postgres connection - OK`. 

### Configure the Agent to collect PostgreSQL metrics
After you've installed the Agent on each of your PostgreSQL servers, you'll need to create a configuration file that provides the Agent with the information it needs in order to begin collecting PostgreSQL data. The location of this file varies according to your OS and platform; consult the [documentation][agent-docs] for more details. 

Copy the [example config file][postgres-example-config] (**postgres.yaml.example**) and save it as **postgres.yaml**. Now you can customize the config file to provide Datadog with the correct information and any tags you'd like to add to your metrics. 

The example below instructs the Agent to access metrics locally through port 5432, using the datadog user and password we just created. You also have the option to add custom tag(s) to your PostgreSQL metrics, and to limit metric collection to specific schemas, if desired. 

{{< code-snippet lang="yaml" filename="postgres.yaml" wrap="false"  >}}
init_config:

instances:
  - host: localhost
    port: 5432
    username: datadog
    password: MYPASSWORD
    tags:
      - optional_tag

{{< /code-snippet >}}

Save your changes, [restart the Agent, and run the `info` command][agent-docs] to verify that the Agent is properly configured. If all is well, you should see a section like this in the resulting output:

```
Checks
======

  [...]
  
    postgres 
    -----------------
      - instance #0 [OK]
      - Collected 70 metrics, 0 events & 1 service check
```

## Diving into your PostgreSQL data with dashboards
Now that you've integrated Datadog with PostgreSQL, you should see metrics populating an out-of-the-box PostgreSQL screenboard, located in your [list of integration dashboards][integration-dash]. This screenboard provides an overview of many of the key metrics covered in [Part 1][part-1] of this series, including locks, index usage, and replication delay. You can also clone and customize it by adding your own custom PostgreSQL metrics. We'll show you how to set up the Agent to collect custom metrics in the next section.

## Collecting custom PostgreSQL metrics with Datadog
Datadog's PostgreSQL integration provides you with an option to collect custom metrics that are mapped to specific queries. In the `custom_metrics` section of the **postgres.yaml** configuration file, you'll see some guidelines about the four main components you'll need to provide:

- `descriptors` to tag your custom metrics
- `metrics` in key:value format; each key corresponds to the name of a column from the `query` below. The value is a two-item list, in which the first value is the custom metric name and the second value is the metric type 
- `query` to run on your database, making sure to include the same column names included in your `descriptors`
- `relation`: true/false to indicate whether you or not you want to include the schema relations listed in the `relations` section of the configuration file as part of the custom query. 

For example, you can send a custom query to the [`pg_stat_activity` view][pg-stat-activity] to continuously gauge the number of applications connected to each of your backends, broken down by application name and user. Normally you'd query the view with something like:

```
SELECT application_name, usename, COUNT(*) FROM pg_stat_activity 
WHERE application_name NOT LIKE 'psql' AND (application_name <> '') IS TRUE  
GROUP BY application_name, usename;
 ```
 
Now you can set up the Agent to automatically query this data for you on a regular basis. In your Datadog Agent **postgres.yaml** file, you would add this to your `custom_metrics` section:

{{< code-snippet lang="yaml" filename="postgres.yaml" wrap="false"  >}}

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
{{< /code-snippet >}}

Save and exit the file, and restart the Datadog Agent (find the command for your OS [here][agent-docs]). We should now be able to see our custom `postgresql.count_by_applications` metric in Datadog, tagged with the `application_name` and `pg_user`.

{{< img src="postgresql-data-monitor-postgresql-datadog-custom-metric-v2.png" alt="postgresql dashboard" border="true" >}}

Consult [the documentation][custom-metrics-docs] and [this article][postgres-custom-doc] to see more examples of other custom PostgreSQL metrics you can collect. 


## Tracing PostgreSQL queries with APM 
Now that we've set up the Agent to track PostgreSQL data from our servers, let's gain visibility into code-level performance with distributed tracing and APM. 

Datadog APM is bundled in the same lightweight, open source Datadog Agent we installed earlier. With all of your services, hosts, and containers reporting to one unified platform, you'll be able to view key metrics from your applications in the same place as their underlying infrastructure. You'll also be able to trace requests as they travel across service boundaries in your environment. 

Distributed tracing and APM are designed to work with minimal configuration. For example, the Python tracing client auto-instruments web frameworks like Django and Flask, as well as commonly used libraries like Redis and PostgreSQL. In the following example, we'll show you how to start tracing a Django app that uses PostgreSQL as its database.

### 1. Install the Datadog Agent + Python tracing client
First, install the Datadog Agent on your app server, by following the instructions for your OS, as specified [here][agent-install]. Now you will need to install the Python tracing client:

```
pip install ddtrace
```

### 2. Update your Django `settings.py` file
Add the tracing client's Django integration to the `INSTALLED_APPS` section of your Django **settings.py** file:

{{< code-snippet lang="yaml" filename="settings.py" wrap="false"  >}}
INSTALLED_APPS = [
[...]
    'ddtrace.contrib.django',
]
{{< /code-snippet >}}

You'll also need to add a `DATADOG_TRACE` section to your `settings.py` file, making sure to specify the name of your service, and any tags you'd like to add to your service-level metrics:

{{< code-snippet lang="yaml" filename="settings.py" wrap="false"  >}}
DATADOG_TRACE = {
    'DEFAULT_SERVICE': '<MY_SERVICE>',
    'TAGS': {'env': 'myenv'},
}
{{< /code-snippet >}}

And, if you haven't done so already, make sure you've specified the name of your database and user permissions in the `DATABASES` section. You also have the option to add the name of your application if desired:

{{< code-snippet lang="yaml" filename="settings.py" wrap="false"  >}}
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '<YOUR_DB>',
        'USER': os.environ['DATABASE_USER'],
        'PASSWORD': os.environ['DATABASE_PASSWORD'],
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'application_name': '<MY_APP>'
        }
    }
}
{{< /code-snippet >}}

Since we specified `application_name`, the Agent will add this in the metadata for each trace it collects and forwards to Datadog. Also, note that `DEBUG` mode needs to be off in order for Datadog to trace your application. 

Save and exit the file. We're ready to trace!

### 3. Run the `ddtrace` command.
You're just one command away from seeing traces and service-level metrics from your app in Datadog. Add `ddtrace-run` as a wrapper around the usual command you use to start your app server:

```
ddtrace-run python manage.py runserver 
```

### Inspecting PostgreSQL database queries in Datadog
The Agent will quickly start collecting metrics and traces from your application, and forwarding them to Datadog for visualization and alerting. Navigate to the Datadog APM page, select the environment you specified in the `DATADOG_TRACE` section of your **settings.py** file, and click on your service to see a dashboard of key metrics (latency, errors, and hits). 

{{< img src="postgresql-data-tracing-django-app-dashboard-v2.png" alt="Monitor PostgreSQL data with Datadog: postgresql and django service in Datadog APM dashboard" popup="true" wide="true" border="true" >}}

At the bottom of the dashboard, you can see a list of various endpoints recently accessed throughout your application. In this example, the endpoints map to [views][django-views-docs] in our Django app. We can click into a trace to follow the path of an individual request as it travels across various components of our app, including multiple PostgreSQL database calls. In the flame graph below, we can click into any PostgreSQL span to view the exact query that was executed. 

{{< img src="postgresql-data-monitor-postgresql-datadog-redis-flamegraph-v3.png" alt="Monitor PostgreSQL with Datadog: flame graph of a Django web app request including PostgreSQL requests" popup="true" wide="true" border="true" >}}

You can also filter through your sampled traces for errors, and start debugging the issue. In the example below, the stack trace shows us that our app is trying to query a nonexistent field in the database.

{{< img src="postgresql-data-monitor-postgresql-datadog-error-trace-v4.png" alt="Monitor PostgreSQL data with Datadog: flame graph of a Django web app request with error" popup="true" wide="true" border="true" >}}

Auto-instrumentation gives you a head start on collecting traces from popular libraries and frameworks, but you can also set up the Agent to collect custom traces by instrumenting and tagging specific spans of your code. You can also trace requests across hosts and collect distributed traces from your environment. Read [the documentation][python-apm-docs] for more details.

### Creating custom dashboards
You can combine APM metrics with infrastructure-wide metrics on any dashboard in order to identify and investigate bottlenecks. You can click on the button in the upper right corner of any APM graph to add it to an existing timeboard.

{{< img src="postgresql-data-postgres-infra-apm-combo-dash-v3.png" alt="Monitor PostgreSQL with Datadog: Combining PostgreSQL APM and infrastructure metrics in the same dashboard" popup="true" wide="true" border="true" >}}

Once you create dashboards that combine service-level metrics with infrastructure metrics, you'll be able to correlate across graphs to help investigate issues. In the dashboard above, it looks like many rows were fetched recently, and requests were spending a higher percentage of time executing PostgreSQL queries. We can investigate further by viewing a trace of a request that occurred around that time:

{{< img src="postgresql-data-monitor-postgresql-tracing-flame-graph-v2.png" alt="inspecting postgresql data in a flame graph of a Django web app request containing many PostgreSQL queries" popup="true" wide="true" >}}

This trace shows us that many different PostgreSQL queries were running sequentially within a single request. We can go even deeper by clicking on each span to see the exact SQL query that was executed, which can help us determine how to reduce the number of database calls and optimize performance.

## Alerting
Once you've implemented APM and started tracing your applications, you can quickly enable default service-level alerts on latency, error rate, or throughput, or set up custom alerts. 

{{< img src="postgresql-data-monitor-postgresql-datadog-service-alerts.png" alt="Monitor PostgreSQL data with Datadog: Enable default alerts to monitor your PostgreSQL-powered services" wide="true" border="true" >}}

You can also set up automated alerts on any of the PostgreSQL data you're collecting. For example, you can configure Datadog to automatically notify you if replication delay increases beyond a certain level, or your databases accumulate too many dead rows. 

## Start monitoring PostgreSQL
In this post, we've shown you how to use Datadog to automatically collect, visualize, and alert on PostgreSQL data to ensure the health and performance of your databases. We've also walked through an example of how to auto-instrument traces from an application that relies on PostgreSQL. If you've followed along, you should now have increased visibility into your PostgreSQL databases, as well as the applications that rely on them. If you're new to Datadog, you can start monitoring PostgreSQL with a <a href="#" class="sign-up-trigger">free trial</a>.


[part-1]: /blog/postgresql-monitoring
[part-2]: /blog/postgresql-monitoring-tools
[agent-install]: https://app.datadoghq.com/account/settings#agent
[postgres-datadog-docs]: https://docs.datadoghq.com/integrations/postgres/
[custom-metrics-docs]: https://docs.datadoghq.com/integrations/postgres/#custom-metrics
[agent-docs]: https://docs.datadoghq.com/guides/basic_agent_usage/
[postgres-example-config]: https://github.com/DataDog/integrations-core/blob/master/postgres/conf.yaml.example
[postgres-integration-tile]: https://app.datadoghq.com/account/settings#integrations/postgres
[django-views-docs]: https://docs.djangoproject.com/en/1.11/topics/http/views/
[python-apm-autoinstrument]: http://pypi.datadoghq.com/trace/docs/#instrumented-libraries
[python-apm-docs]: http://pypi.datadoghq.com/trace/docs/
[integration-dash]: https://app.datadoghq.com/dashboard/lists/preset/3
[pg-stat-activity]: https://www.postgresql.org/docs/current/static/monitoring-stats.html#PG-STAT-ACTIVITY-VIEW
[postgres-custom-doc]: https://help.datadoghq.com/hc/en-us/articles/208385813-Postgres-custom-metric-collection-explained
