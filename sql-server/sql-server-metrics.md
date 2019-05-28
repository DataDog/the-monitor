# Custom SQL Server metrics for detailed monitoring


We've shown in [Part 3][part3] of this series how Datadog can help you monitor your SQL Server databases within the context of your application. In this post, we'll show you how to go one step further by collecting custom SQL Server metrics that let you choose the exact functionality you want to monitor and improve. You can configure the Agent to collect custom metrics and report them every time it runs its built-in SQL Server check.

We'll show you three ways to collect and monitor custom metrics:

1. Specifying [performance counters](#custom-datadog-metrics-with-the-performance-counters-view) beyond those the SQL Server integration queries by default
2. Executing a user-defined [stored procedure](#custom-datadog-metrics-from-stored-procedures)
3. Using the [Windows Management Instrumentation](#custom-datadog-metrics-from-windows-management-instrumentation) (WMI) integration

## Custom Datadog metrics with the performance counters view

Although the Agent already collects a number of [important metrics][dd-mssql-integration] from the [performance counters dynamic management view][part2-dmvs], you might be interested in monitoring additional [performance objects][performance-objects] such as page lookups per second, log flushes per second, or queued requests. You can see a list of all the performance counters you can monitor by running the following query:

```
SELECT counter_name, instance_name, cntr_value FROM sys.dm_os_performance_counters;
```

You'll see something resembling the following:

```no-minimize
counter_name         instance_name         cntr_value
Page lookups/sec                           30617439
Log Flushes/sec      tempdb                5664
Log Flushes/sec      model                 7
Log Flushes/sec      demo_db               15152
Queued requests      internal              0
```

To collect metrics automatically from specific performance counters, edit the SQL Server [configuration file][dd-mssql-config], which the Agent looks for within **C:\ProgramData\Datadog\conf.d\sqlserver.d**. [Create an entry][dd-custom-metrics] under `custom_metrics` for each metric you want to collect. For example, we can collect the metrics "Page lookups/sec," "Queued Requests," and "Log Flushes/sec," plus "Index Searches/sec," by adding the configuration below:

```no-minimize
    # ...
    custom_metrics:
        - name: sqlserver.buffer.page_lookups
          counter_name: Page lookups/sec
        
        - name: sqlserver.workload.queued_requests
          counter_name: Queued Requests
          instance_name: internal                  

        - name: sqlserver.databases.log_flushes
          counter_name: Log Flushes/sec
          instance_name: ALL
          tag_by: db        

        - name: sqlserver.index_searches
          counter_name: Index Searches/sec             
    # ...
```

For each entry, you must specify values for `name` and `counter_name`. The `name` value will be the name of the metric as you want it to appear in Datadog, whereas the `counter_name` maps to the `counter_name` column of `sys.dm_os_performance_counters`. In the case of "Page lookups/sec," the configuration above will cause the metric to appear in Datadog as `sqlserver.buffer.page_lookups`. 

Some performance objects are associated with multiple instances within SQL Server, and you can identify these with the `instance_name` column of `sys.dm_os_performance_counters`. You'll want to check the [documentation][performance-objects] for the performance objects you're interested in to see what `instance_name` means in that context. In our example above, `Log Flushes/sec` is a counter within the object [`SQLServer:Databases`][performance-objects-db]. There's a separate instance of the object (and its counters) for each database. The [resource pool performance object][performance-objects-pool] has a separate instance for each resource pool. Other performance objects, like the Buffer Manager object where you'll find `Page lookups/sec`, always have a single instance.

If a performance counter has multiple instances, you have two options for sending metrics to Datadog. One is to collect metrics from a single instance, by specifying `instance_name` in the `custom_metrics` section. In our example above, we've edited the item for `Queued Requests` to gather metrics only from the `internal` instance. 

If you want to collect metrics associated with _every_ instance, set the value of `instance_name` to `ALL`. Then add a `tag_by` line, which creates a key-value tag pair for each instance of a performance counter. If the metric `Log Flushes/sec` is reported for instances `tempdb`, `model`, and `demo_db`, for example, a `tag_by` prefix of `db` will create the tags `db:tempdb`, `db:model`, and `db:demo_db`. While you can name the prefix anything you'd like, you may want to name it after the object that each instance represents (a database, a resource pool, etc.).

After restarting the Agent, you'll be able to add your custom metrics to dashboards and alerts, just like any other metric in Datadog. Below, we're graphing the custom metric `sqlserver.index_searches`, which we've named from the counter `Index Searches/sec` within the [`Access Methods`][access-methods] performance object (see [above](#custom-datadog-metrics-with-the-performance-counters-view)).

{{< img src="SQL-Server-Metrics-index-searches-counter.png" alt="Selecting performance counters for custom SQL Server metrics" popup="true" >}}

## Custom Datadog metrics from stored procedures
While metrics from the performance counters view are useful for gauging the health and performance of your databases, you can use SQL Server's wealth of views, stored procedures, and functions to gain even more insights. For example, you may want to keep track of the size of specific tables in disk and memory—valuable data that is not available as a performance counter.

To create and monitor your own custom metrics, you will need to:

1. Create a [stored procedure][stored-procedure] that returns a temporary table with the metrics you want to report.
2. Edit the configuration file for the SQL Server integration and include an entry for the stored procedure you've created.

The Agent will then execute the stored procedure every few seconds and send the results to Datadog.

In the example that follows, we'll query metrics for a database’s disk usage with the stored procedure [`sp_spaceused`][sp_spaceused] (available since SQL Server 2012). We'll wrap our call to `sp_spaceused` within a stored procedure that returns results in a format Datadog can parse into three metrics: the size on disk of the data within the database, the size of indexes, and the total size of data and transaction logs. This is just one example of the many ways in which you can use stored procedures to report custom metrics to Datadog.

### Create a stored procedure to generate and collect metrics
A stored procedure for reporting custom metrics can use any T-SQL queries you'd like, as long as it culminates in a table with a certain structure. As you'll see in the SQL Server integration's [example YAML file][example-yaml], the Agent expects custom metrics from a stored procedure to take the form of a temporary table called `#Datadog`. The table must have the following columns:

- `metric`: the name of the metric as it appears in Datadog
- `type`: the metric type: gauge, rate, or count (see our [documentation][metric-types] on metric types)
- `value`: the value of the metric
- `tags`: the tags that will appear in Datadog. You can specify any number of tags, separating them with a comma, e.g., `db:master, role:primary`

In this case, we've create a stored procedure named `GetDiskMetrics`. This stored procedure begins by executing `sp_spaceused` and inserting the results into a temporary table. This allows us to select specific metrics from the results. 

`sp_spaceused` returns strings of numbers and their units, stating `index_size` and `data` in kilobytes (e.g., `1528 KB`), and `database_size` in megabytes (e.g., `80 MB`). We’ll declare a function that removes the units, converts the strings into floats, and stores the results in the table `#Datadog`. 

When writing your own stored procedure, make sure that the values you're storing in the table `#Datadog` are convertible to floats. SQL Server will attempt to convert certain data types automatically, but for other types it will throw an error (see [this chart][conversion-chart] for a breakdown of what SQL Server can convert). For example, the `ExtractFloat` function below returns a string that SQL Server will convert to a float before inserting.

```no-minimize
USE [<database name>];
GO

-- Remove units from the results of sp_spaceused

CREATE FUNCTION [dbo].[ExtractFloat] (
  @StringWithFloat nvarchar(50)
)
RETURNS float
BEGIN
  RETURN (SELECT SUBSTRING(
    @StringWithFloat,
    0,
    (select PATINDEX('% %', (@StringWithFloat)))
  ))
END
GO

-- Create a stored procedure with the name GetDiskMetrics

CREATE PROCEDURE [dbo].[GetDiskMetrics]
AS
BEGIN

  -- Remove row counts from result sets
  SET NOCOUNT ON;

  -- Create a temporary table per integration instructions

  CREATE TABLE #Datadog
  (
    [metric] VARCHAR(255) NOT NULL,
    [type] VARCHAR(50) NOT NULL,
    [value] FLOAT NOT NULL,
    [tags] VARCHAR(255)
  );

  -- Declare a temporary table to store the results of sp_spaceused

  DECLARE @disk_use_table table(
    database_name varchar(128),
    database_size varchar(18),
    unallocated_space varchar(18),
    reserved varchar(18),
    data varchar(18), 
    index_size varchar(18),
    unused varchar(18)
  );

  INSERT INTO @disk_use_table EXEC sp_spaceused @oneresultset=1;
	
  -- Remove the units from our custom metrics and insert them into the table #Datadog 

  INSERT INTO #Datadog(metric, type, value, tags) VALUES
    ('sqlserver.disk.database_size_mb', 'gauge', (SELECT dbo.ExtractFloat((SELECT [database_size] FROM @disk_use_table))), 'db:master,role:primary'),
    ('sqlserver.disk.index_size_kb', 'gauge', (SELECT dbo.ExtractFloat((SELECT [index_size] FROM @disk_use_table))), 'db:master,role:primary'),
    ('sqlserver.disk.data_size_kb', 'gauge', (SELECT dbo.ExtractFloat((SELECT [data] FROM @disk_use_table))), 'db:master,role:primary');

	-- Return the table
	SELECT * FROM #Datadog;

END
```

The stored procedure outputs three custom metrics:

- `sqlserver.disk.database_size_mb`: Size of the database, including both data and [transaction log files][part1-storage]
- `sqlserver.disk.index_size_kb`: Size of all indexes used by the database
- `sqlserver.disk.data_size_kb`: Size of all data within the database

The metrics will be tagged automatically with the values of the `tags` column in the table `#Datadog`, in this case `role:primary` and `db:master`. We’re also collecting each custom metric as a gauge, which reports the current value of a metric at each check. See [our documentation][metric-types] for more details about Datadog's metric types, gauges, rates, and counts.

The code above declares the stored procedure `GetDiskMetrics` and the function `ExtractFloat`. Before you configure Datadog to call `GetDiskMetrics`, you may want to make sure it's been declared successfully within SQL Server. You can run this query to verify that you've added the stored procedure.

```no-minimize
SELECT name FROM sys.procedures WHERE name = "GetDiskMetrics";
```

The output should resemble the following.

```no-minimize
name
GetDiskMetrics
```

### Configure the Datadog Agent to execute the stored procedure

Next, configure the Agent to execute the stored procedure created above, which reports custom metrics to Datadog. You'll need to edit the existing `host` section of the SQL Server integration's YAML file (located within **C:\ProgramData\Datadog\conf.d\sqlserver.d**) to specify the name of the stored procedure the Agent will call, plus the name of the `database` the Agent will use when calling it.

```no-minimize
# ...
  - host: 127.0.0.1,1433
    username: datadog
    password: <password>
    stored_procedure: GetDiskMetrics
    database: master
# ...
```

There are three caveats to note about using stored procedures for custom metrics. First, you can specify the `connector`, the interface between the Agent and SQL Server, in the integration's YAML file. If you plan to specify `odbc` as the connector, rather than the default of `adodbapi`, you will not able to collect custom metrics with a stored procedure. Second, since the Agent will be running the stored procedure with every check, obtaining custom metrics this way will cause SQL Server to consume more resources. Third, the custom metrics you report to the table `#Datadog` are subject to the same limits as any other custom metric in Datadog. [Consult our documentation][custom-metrics] for details.

## Custom Datadog metrics from Windows Management Instrumentation

If you’re running SQL Server on Windows, you can also collect custom metrics by using [Windows Management Instrumentation][wmi-intro] (WMI). WMI is a core feature of the Microsoft Windows operating system that allows applications to broadcast and receive data. Applications commonly use WMI to communicate information about resources, such as drivers, disks, or processes, including SQL Server. Datadog's [WMI integration][wmi-check-docs] can monitor the [hundreds of WMI classes][wmi-dd-classes] you'll find in a Windows environment, making this is a convenient way to add custom metrics for SQL Server.

To configure the Agent to send metrics from WMI, you'll need to edit the WMI integration's [configuration file][wmi-check-config]. Under `instances`, list the names of the [WMI classes][wmi-classes] from which you want to gather metrics. Under the item for each class, you'll list metrics as arrays with three elements: the name of a property of the WMI class, the name of the metric you'd like to report to Datadog, and the metric [type][metric-types].

You can collect the number of failed SQL Server jobs with the following configuration, for example:

```no-minimize
instances: 
    - class: Win32_PerfRawData_SQLSERVERAGENT_SQLAgentJobs
      metrics:
        - [Failedjobs, sqlserver.jobs.failed_jobs, gauge]
    # ...
```

Then enable the WMI integration by restarting the Agent.

[Click here][wmi-classes-mssql] to see all of the WMI classes that report data from SQL Server.

## SQL Server metrics for tailored monitoring 
In this series, we've [surveyed metrics][part1] that can expose SQL Server's core functionality, and have shown you how to use a number of [monitoring tools][part2] to get real-time views and detailed reports. We've demonstrated how you can combine live observation and on-demand insights by adding distributed tracing and log management, all with [Datadog][part3]. 

With custom metrics, it's possible to monitor every metric SQL Server collects internally, and to use this as a basis for optimizing your databases. With Datadog, you can correlate these metrics with others from SQL Server and the rest of your stack, making it clear where performance issues are originating or where you should focus your optimization efforts.

If you are not using Datadog and want to gain visiblity into the health and performance of SQL Server and more than {{< translate key="integration_count" >}} other supported technologies, you can get started by signing up for a <a class="sign-up-trigger" href="#">14-day free trial</a>.

[access-methods]: https://docs.microsoft.com/en-us/sql/relational-databases/performance-monitor/sql-server-access-methods-object?view=sql-server-2017

[conversion-chart]: https://docs.microsoft.com/en-us/sql/t-sql/functions/cast-and-convert-transact-sql?view=sql-server-2017#implicit-conversions

[custom-metrics]: https://docs.datadoghq.com/getting_started/custom_metrics/

[datadog-agent]: https://app.datadoghq.com/account/settings#agent/windows

[db-properties]: https://docs.microsoft.com/en-us/sql/t-sql/functions/databasepropertyex-transact-sql

[dd-conf-file]: https://help.datadoghq.com/hc/en-us/articles/203037169-Where-is-the-configuration-file-for-the-Agent-

[dd-custom-metrics]: https://help.datadoghq.com/hc/en-us/articles/209280186-How-can-I-collect-more-metrics-from-my-SQL-Server-integration-

[dd-mssql-integration]: https://docs.datadoghq.com/integrations/sqlserver/

[dd-mssql-config]: https://docs.datadoghq.com/integrations/sqlserver/#configuration

[example-yaml]: https://github.com/DataDog/integrations-core/blob/master/sqlserver/datadog_checks/sqlserver/data/conf.yaml.example

[gauges]: https://docs.datadoghq.com/developers/metrics/#gauges

[part1]: /blog/sql-server-monitoring

[part1-storage]: /blog/sql-server-monitoring#storage-caching-and-reliability

[part2]: /blog/sql-server-monitoring-tools

[part2-dmvs]: /blog/sql-server-monitoring-tools#dynamic-management-views

[part3]: /blog/sql-server-performance

[performance-counters-view]: https://docs.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-os-performance-counters-transact-sql

[performance-objects]: https://docs.microsoft.com/en-us/sql/relational-databases/performance-monitor/use-sql-server-objects

[performance-objects-db]: https://docs.microsoft.com/en-us/sql/relational-databases/performance-monitor/sql-server-databases-object?view=sql-server-2017

[performance-objects-pool]: https://docs.microsoft.com/en-us/sql/relational-databases/performance-monitor/sql-server-resource-pool-stats-object?view=sql-server-2017

[metric-types]: https://docs.datadoghq.com/developers/metrics/#metric-types

[sp_spaceused]: https://docs.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-spaceused-transact-sql

[stored-procedure]: https://docs.microsoft.com/en-us/sql/relational-databases/stored-procedures/stored-procedures-database-engine

[result-set]: https://docs.microsoft.com/en-us/sql/t-sql/queries/with-common-table-expression-transact-sql

[wmi-check-config]: https://docs.datadoghq.com/integrations/wmi_check/#configuration

[wmi-check-docs]: https://docs.datadoghq.com/integrations/wmi_check/

[wmi-classes]: https://msdn.microsoft.com/en-us/library/windows/desktop/aa394554.aspx

[wmi-classes-mssql]: http://wutils.com/wmi/root/cimv2/win32_perfrawdata/

[wmi-dd-classes]: https://help.datadoghq.com/hc/en-us/articles/205016075-How-to-retrieve-WMI-metrics

[wmi-intro]: https://msdn.microsoft.com/en-us/library/aa394582(v=vs.85).aspx
