---
authors:
- email: paul.gottschling@datadoghq.com
  image: paulgottschling.jpg
  name: Paul Gottschling
blog/category:
- series metrics
blog/tag:
- sql-server
- alerts
- dbms
- sql
- microsoft
date: 2018-05-04T17:00:02Z
description: "Use these SQL Server monitoring tools to get detailed views of performance and resource use"
draft: false
image: "SQL-Server-Monitoring-Tools-Datadog-Hero.png"
preview_image: "SQL-Server-Monitoring-Tools-Datadog-Hero.png"
slug: sql-server-monitoring-tools
technology: sql-server
title: SQL Server monitoring tools
series: sql-server-monitoring
header_video:
    mp4: superheroes_microsoftsq_v24.mp4
    no_loop: false
    no_autoplay: false
    stop_time: 0
---
In [Part 1][part1] of this series, we covered a number of features that SQL Server provides for optimizing its resource usage. You can, for example, adjust the way your query batches are compiled, configure your buffer cache to flush at different intervals, and create memory-optimized tables. Making the most of these features requires that you get real-time insights into the health and performance of SQL Server. Here we'll survey SQL Server monitoring tools within built-in features and commonly used applications, including:

- **[T-SQL queries](#using-tsql-queries):** Use SQL Server's query language to gather internally collected data
- **[SQL Server Management Studio](#sql-server-management-studio) (SSMS):** Get real-time views into your system, diagrams of T-SQL queries, and on-demand reports 
- **[Performance Monitor](#performance-monitor):** Correlate metrics from SQL Server with data from your Windows hosts  

SQL Server monitoring tools can help you access the metrics we discussed in [Part 1][part1]. Some of these tools report the same metrics, and you may prefer one interface over the other. For example, you can use either the Performance Monitor or T-SQL queries to obtain metrics from SQL Server's [performance counters](#dynamic-management-views). You might opt for the real-time graphs of the former versus the ability to script the latter. In this post, we'll explain how to use SQL Server monitoring tools to gain a comprehensive view of your database infrastructure.

## Using T-SQL queries
You can monitor SQL Server by using its own query language, T-SQL, to gather metrics. T-SQL queries are flexible. You can run them with a graphical management tool like [SSMS](#sql-server-management-studio) or a command line utility like [`sqlcmd`][sqlcmd]. And since they are executed and return data just like any other database query, you can easily incorporate them into a homegrown automated monitoring solution. In this section, we'll show how T-SQL queries can be a powerful tool for SQL Server monitoring, whether you're using dynamic management views, built-in functions, stored procedures, or system data collection sets.

### Dynamic management views
SQL Server tracks data about its own health and performance, and makes this information available through [dynamic management views][mssql-dmvs] (DMVs). Because DMVs are displayed as [virtual tables][mssql-views], they lend themselves to both ad-hoc and automated querying. Some DMVs return the current value of a metric or setting (e.g., the [current size of the transaction log][log-stats] in megabytes). Others, particularly the metrics for rates within the [performance counters DMV][performance-counters], measure values at regular intervals and take the difference between consecutive samples (e.g., [batch requests per second][general-stats]). You can read about specific DMVs in the SQL Server [documentation][dmv-categories].

If you're monitoring SQL Server with dynamic management views, you'll probably want to query the [performance counters][performance-counters] DMV, `sys.dm_os_performance_counters`. Each SQL Server [performance object][mssql-objects] (which can represent anything from a [database][object-databases] to the [plan cache][object-plan-cache]) maintains its own set of performance counters, which map to many of the categories of metrics discussed in [Part 1][part1]: [SQL statistics][object-sql-stats], [locks][object-locks], and the [buffer manager][object-buffer-manager]. 

For example, you can query the performance counters DMV to view data from the buffer manager performance object and limit the results to metrics with nonzero values:

```no-minimize
SELECT object_name, counter_name, cntr_value 
FROM sys.dm_os_performance_counters 
WHERE object_name="SQLServer:Buffer Manager" AND cntr_value != 0;
GO
```

You'll get a result similar to this (but with many more rows!):

```no-minimize
object_name                            counter_name                         cntr_value
---------------------------------------------------------------------------------------
SQLServer:Buffer Manager               Buffer cache hit ratio               30
SQLServer:Buffer Manager               Buffer cache hit ratio base          30
SQLServer:Buffer Manager               Page lookups/sec                     11091500
SQLServer:Buffer Manager               Database pages                       5819
SQLServer:Buffer Manager               Target pages                         212992
SQLServer:Buffer Manager               Integral Controller Slope            10

```

You can find a list of the available dynamic management views organized by category [here][dmv-categories]. Within each category, views are diverse—while some calculate performance metrics and output numbers, others report names and properties. You can list [the SQL Server nodes in a cluster][dmv-ex-cluster], retrieve [index usage data][dmv-ex-index-usage], and get statistics for your [execution plans][dmv-ex-queries] like completion time and resource use. And since dynamic management views behave like tables, you can use built-in functions to [aggregate][built-in-fx-aggregation] and [rank][built-in-fx-rank] the data.

It's important to check the [documentation][dmv-categories] for any DMV you plan to use. One reason is that DMVs require different permissions, and the documentation for each DMV explains the required level. Another reason is that DMVs may contain thousands of rows, and columns may change with new versions of SQL Server.

### Built-in functions
SQL Server also includes [built-in functions][built-in-fnx] to help you access system information. Unlike dynamic management views, which return data in the form of virtual tables, built-in functions return [system data][built-in-fx-data] as single numerical values, calculated since the server was last started. You can [call each built-in function][built-in-fx-calling] as the argument of a `SELECT` statement. For example, you can use the built-in function `@@connections` to return the sum of successful and unsuccessful [connections][built-in-fx-connections] over time: 

```no-minimize
SELECT @@connections AS "Total Connections";
GO
```
You'll receive output similar to:

```no-minimize
Total Connections
-----------------
             1571
```

Built-in functions sometimes resemble dynamic management views. `@@connections` is similar to the `User Connections` counter within the [general statistics object][object-general-stats]. But while `User Connections` tracks the number of currently connected users, `@@connections` increments every time a user attempts to log in (even if the attempt is unsuccessful).

The only built-in system statistics function that doesn't return a single numerical value is [`sys.fn_virtualfilestats`][built-in-fx-vfs], which returns [a table][table-valued-functions] with data on disk I/O for database files, and yields [the same information][dmv-vfs] as the `sys.dm_io_virtual_file_stats` dynamic management view.

### System stored procedures
Another built-in feature you can use to query metrics is the [system stored procedure][system-stored-procedure]. Most stored procedures help with administrative tasks such as [attaching a database][stored-proc-attach-db] or [adding a login][stored-proc-add-login], but some stored procedures report metrics. For example, [`sp_spaceused`][sp-spaceused] measures disk consumption within a database. You call system stored procedures with `EXEC` rather than `SELECT` statements. This command calls the `sp_spaceused` stored procedure, which will return disk usage information as two result sets (that is, two table rows, each row including different columns):

```no-minimize
EXEC sp_spaceused;
GO
```

The output will have a similar format to the following:

```no-minimize
database_name     database_size      unallocated space
--------------- ----------------- ---------------------
master            6.00 MB            0.52 MB

reserved           data               index_size         unused
--------------- ----------------- ------------------ ------------
3568 KB            1536 KB           1600 KB             432 KB
```

### System data collection sets
If you're using T-SQL queries to gather metrics from SQL Server, and you want to be able to store the data and generate reports, you might consider using SQL Server's collection sets. A collection set draws data from a range of reporting commands and dynamic management views, and sends the data to a dedicated database called a Management Data Warehouse.

The [process][collection-sets-how-works] relies on [SQL Server Integration Services][collection-sets-ssis] to automate the task of querying the database and writing the results to the Management Data Warehouse.

For example, as of SQL Server 2008, the [disk usage collection set][collection-sets-2008-disk-usage] queries the `sys.dm_io_virtual_file_stat` dynamic management view and other views such as `sys.partitions` and `sys.allocation_units`. You can also create a [custom collection set][collection-sets-custom] that corrals a sequence of T-SQL queries into a periodic job that runs in the background. You can learn more about configuring the Data Management Warehouse [here][collection-sets-dmw]. 

## SQL Server Management Studio
SQL Server Management Studio (SSMS) is a graphical environment that helps you monitor your system in several ways: 

- Live statistics in the [Activity Monitor](#activity-monitor)
- A [data-rich map](#visualizing-queries) of a given query
- Reports that combine [tables, graphs, and text](#reports) in a printer-friendly format

To use SSMS, you'll need to [download it][ssms-download] on one of your hosts, open the installer, and follow the prompts. The software can monitor remote instances of SQL Server, including any instances running on Linux. To connect to a host, navigate to the "File" menu and click "Connect Object Explorer." In the dialogue that follows, specify the host and port in the "Server name" field, in the [format][ssms-connections] `0.0.0.0,0000` (note the comma). Select "SQL Server Authentication" in the "Authentication" dropdown menu, and fill in the username ("Login") and password.

{{< img src="SQL-Server-Monitoring-Tools-Host-Login.png" alt="SQL Server monitoring tools: Specifying a remote host in SSMS" popup="true" size="1x" >}}

If you've connected successfully, you'll see the "Object Explorer" window populate with a file tree that shows the components of your SQL Server instance, including databases. You'll then be able to monitor your instance with the features shown below.

### Activity Monitor
[The Activity Monitor][activity-monitor] makes it possible to view SQL Server metrics in real time, with a gallery of graphs, an overview of processes, and statistics about your queries. If you're already using SSMS for management tasks like configuring resource pools or creating tables, the Activity Monitor is easy to add to your workflow. To use the Activity Monitor, type "Ctrl-Alt-A" or [click the icon][activity-monitor-open] within the SSMS toolbar.

{{< img src="SQL-Server-Monitoring-Tools-Activity-Monitor.png" alt="SQL Server monitoring tools: Activity Monitor window" popup="true" size="1x" >}}

You can use the Activity Monitor to get real-time insights into the demand on your SQL Server instance. The "Overview" section shows four graphs that display work and resource metrics in real time. By default, these metrics refresh every 10 seconds, but you can update the refresh interval by right-clicking on the "Overview" pane. While the refresh interval can be as frequent as once per second, this comes with the performance cost of more frequent database queries.

The "Recent Expensive Queries" pane within the Activity Monitor can help provide the information you need to make your queries more efficient. Here you'll find query-related metrics like executions per minute, physical reads per second, and the number of duplicates of an execution plan within the cache. If a single execution plan has a high number of duplicates or executions per minute, you may be able to boost performance by using query hints as discussed in [Part 1][part1-tsql].

The Activity Monitor provides a convenient high-level overview of your database, but it does have its limits. For one, you can't adjust the sizes of the graphs or the metrics they show. Nor can you change the way the Activity Monitor aggregates its statistics for query performance, or view data beyond the preset display window. 

### Visualizing queries
SSMS can help you optimize query performance by enabling you to visualize how SQL Server executes its query plans, and showing you the resource usage associated with executing each step of a query plan. As we discussed in [Part 1][part1-tsql], SQL Server compiles batches of T-SQL statements by using an automatic optimizer to transform the batch into an execution plan. You can inspect an execution plan in SSMS as a diagram of computational steps, and find out exactly how the optimizer interpreted your batch. To visualize a query, navigate to the Activity Monitor's "Recent Expensive Queries" pane, right-click on one of the queries, and click "Show Execution Plan." The view that follows will look something like this:

{{< img src="SQL-Server-Monitoring-Tools-Execution-Plan-Visualization.png" alt="SQL Server monitoring tools: Diagram of a query plan in SQL Server" popup="true" wide="true" >}} 

If you mouse over a node within the diagram, you can see a brief explanation of the step the node represents, as well as a quick readout of the node's "Estimated Operator Cost." This value is calculated by the [SQL Server optimizer][estimated-op-cost] when executing the query. Since the optimization process is automatic, this gives you a way to check that your batches have compiled as intended. And because each step in the execution plan is scored by cost, you can see which steps you should focus on if you want to boost performance.

In this example, we can see that `Compute Scalar` (converting a string to a float) is minimal, with zero cost in the execution plan. The most costly operation is an optimization technique, [table spooling][table-spooling], which copies rows into a hidden temporary table. 

### Reports
SSMS offers 20 standard reports that provide a high-altitude survey of your SQL Server deployment, ranging from your database's resource usage to historical data about schema changes and database consistency. You can find a detailed breakdown of the reports [here][ssms-standard-reports-list]. 

{{< img src="SQL-Server-Monitoring-Tools-SSMS-Report.png" alt="SQL Server monitoring tools: An example of a SQL Server Management Studio report" popup="true" >}}

Reports are fixed in layout and content—they show data available the moment you create the report, rather than updating in real time. Interactivity in the standard reports is limited. You can sort some tables by column and expand others when information is nested. The fixed layout makes it straightforward to create printouts or documents (PDF, Word, and Excel).

In 2017, Microsoft added the [Performance Dashboard report][ssms-performance-dashboard], which shows CPU utilization, current counts of user sessions, and other system information for SQL Server instances. 

To generate a report, right-click the name of a database in Object Explorer, mouse over "Reports," then over "Standard Reports," and select a report from the menu.

If you can't find the view you need from the SSMS standard reports, you can [create a custom report][ssms-custom-reports]. Custom reports are written in Report Definition Language (RDL), an [extension of XML][rdl]. After you've specified the structure of a custom report, you can populate it from the "Reports" menu by clicking "Custom Reports." These remain separate from the list of standard reports. 

It's also worth noting that Microsoft has developed several tools for creating graphical reports that go beyond the functionality of SSMS. [Power BI][power-bi] can visualize data from a number of sources, [including SQL Server][power-bi-mssql-connection], and comes with a more full-featured set of visual editing tools. SQL Server Reporting Services ([SSRS][ssrs]) is a graphical reporting tool designed for SQL Server that can generate paginated, PDF-ready reports as well as data visualizations for mobile devices and the web.

## Performance Monitor
Windows Performance Monitor helps you visualize system-level [resource usage][performance-monitor] from your Windows hosts, and enables you to correlate these metrics with SQL Server performance counters in timeseries graphs.   

{{< img src="SQL-Server-Monitoring-Tools-Perfmon-Graph.png" alt="SQL Server monitoring tools: Performance Monitor graph showing percent processor time" wide="true" popup="true" >}}

Performance Monitor is built into the Windows operating system. To use it, open the Run window from the Start Menu and enter the program name `perfmon`. A real-time graph will appear in the navigation tree under "Monitoring Tools." You can then select SQL Server performance counters and system resource metrics you'd like to plot, and use the options to style your graphs.

{{< img src="SQL-Server-Monitoring-Tools-Add-Counters.png" alt="Selecting SQL Server performance counters to display in Performance Monitor" size="1x" >}}

## Richer real-time SQL Server monitoring tools
In this post, we've shown how to use SQL Server monitoring tools and built-in features to generate real-time overviews of your databases as well as to get detailed, on-demand data on SQL Server health and performance.

In the [next part][part3] of this series, we'll show you how to use Datadog to collect, graph, and alert on real-time and historical SQL Server metrics. We'll also show you how to set up dashboards with drag-and-drop visualizations, and correlate SQL Server metrics with data from across your stack. 

[activity-monitor]: https://technet.microsoft.com/en-us/library/cc879320(v=sql.105).aspx

[activity-monitor-open]:https://docs.microsoft.com/en-us/sql/relational-databases/performance-monitor/open-activity-monitor-sql-server-management-studio

[activity-monitor-overview]: https://technet.microsoft.com/en-us/library/cc879320(v=sql.105).aspx#Anchor_0

[built-in-fnx]:https://docs.microsoft.com/en-us/sql/t-sql/functions/functions

[built-in-fx-aggregation]: https://technet.microsoft.com/en-us/library/ms173454(v=sql.110).aspx

[built-in-fx-calling]:https://technet.microsoft.com/en-us/library/dd402107.aspx?f=255&MSPPError=-2147217396

[built-in-fx-connections]:https://docs.microsoft.com/en-us/sql/t-sql/functions/connections-transact-sql

[built-in-fx-data]:https://docs.microsoft.com/en-us/sql/t-sql/functions/system-statistical-functions-transact-sql

[built-in-fx-rank]: https://technet.microsoft.com/en-us/library/ms189798(v=sql.110).aspx

[built-in-fx-vfs]: https://docs.microsoft.com/en-us/sql/relational-databases/system-functions/sys-fn-virtualfilestats-transact-sql

[collection-sets-2008-disk-usage]: https://technet.microsoft.com/en-us/library/bb964725(v=sql.105).aspx#Anchor_0

[collection-sets-custom]: https://docs.microsoft.com/en-us/sql/relational-databases/data-collection/create-custom-collection-set-generic-t-sql-query-collector-type

[collection-sets-dmw]: https://docs.microsoft.com/en-us/sql/relational-databases/data-collection/configure-the-management-data-warehouse-sql-server-management-studio

[collection-sets-how-works]: https://docs.microsoft.com/en-us/sql/relational-databases/data-collection/data-collection

[collection-sets-ssis]: https://docs.microsoft.com/en-us/sql/integration-services/sql-server-integration-services

[dmv-categories]: https://docs.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/system-dynamic-management-views#in-this-section

[dmv-ex-cluster]: https://docs.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-hadr-cluster-members-transact-sql

[dmv-ex-index-usage]: https://docs.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-db-index-usage-stats-transact-sql

[dmv-ex-queries]: https://docs.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-exec-query-stats-transact-sql

[dmv-vfs]:https://docs.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-io-virtual-file-stats-transact-sql

[estimated-op-cost]: https://blogs.msdn.microsoft.com/sqlqueryprocessing/2006/10/11/whats-this-cost/

[general-stats]: https://docs.microsoft.com/en-us/sql/relational-databases/performance-monitor/sql-server-sql-statistics-object?view=sql-server-2017

[object-locks]: https://docs.microsoft.com/en-us/sql/relational-databases/performance-monitor/sql-server-locks-object

[log-stats]: https://docs.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-db-log-stats-transact-sql?view=sql-server-2017

[mssql-dmvs]: https://docs.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/system-dynamic-management-views

[mssql-objects]: https://docs.microsoft.com/en-us/sql/relational-databases/performance-monitor/use-sql-server-objects

[mssql-views]: https://docs.microsoft.com/en-us/sql/relational-databases/views/views

[object-buffer-manager]: https://docs.microsoft.com/en-us/sql/relational-databases/performance-monitor/sql-server-buffer-manager-object

[object-databases]: https://docs.microsoft.com/en-us/sql/relational-databases/performance-monitor/sql-server-databases-object

[object-general-stats]: https://docs.microsoft.com/en-us/sql/relational-databases/performance-monitor/sql-server-general-statistics-object

[object-plan-cache]: https://docs.microsoft.com/en-us/sql/relational-databases/performance-monitor/sql-server-plan-cache-object

[object-sql-stats]: https://docs.microsoft.com/en-us/sql/relational-databases/performance-monitor/sql-server-sql-statistics-object

[part1]: /blog/sql-server-monitoring

[part1-tsql]: /blog/sql-server-monitoring#t-sql-metrics

[part3]: /blog/sql-server-performance

[part4-sp]: /blog/sql-server-metrics#create-a-stored-procedure-to-generate-and-collect-metrics

[performance-counters]: https://docs.microsoft.com/en-us/sql/relational-databases/system-dynamic-management-views/sys-dm-os-performance-counters-transact-sql

[performance-monitor]: https://docs.microsoft.com/en-us/sql/relational-databases/performance-monitor/monitor-resource-usage-system-monitor

[power-bi]:https://powerbi.microsoft.com/en-us/

[power-bi-mssql-connection]: https://docs.microsoft.com/en-us/power-bi/service-gateway-enterprise-manage-sql

[query-hints]: https://docs.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-query?view=sql-server-2017

[rdl]: https://docs.microsoft.com/en-us/sql/reporting-services/reports/report-definition-language-ssrs

[sp-spaceused]: https://docs.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-spaceused-transact-sql

[ssms-connections]: https://social.technet.microsoft.com/wiki/contents/articles/2102.how-to-troubleshoot-connecting-to-the-sql-server-database-engine.aspx

[ssms-custom-reports]: https://docs.microsoft.com/en-us/sql/ssms/object/custom-reports-in-management-studio

[ssms-download]: https://docs.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms

[ssms-performance-dashboard]: https://blogs.msdn.microsoft.com/sql_server_team/new-in-ssms-performance-dashboard-built-in/

[ssms-standard-reports-list]: https://blogs.msdn.microsoft.com/buckwoody/2008/04/17/sql-server-management-studio-standard-reports-the-full-list/

[ssrs]: https://docs.microsoft.com/en-us/sql/reporting-services/create-deploy-and-manage-mobile-and-paginated-reports

[sqlcmd]: https://docs.microsoft.com/en-us/sql/tools/sqlcmd-utility

[stored-proc-add-login]: https://docs.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-addlogin-transact-sql

[stored-proc-attach-db]: https://docs.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sp-attach-db-transact-sql

[system-stored-procedure]: https://docs.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/system-stored-procedures-transact-sql

[table-spooling]: https://technet.microsoft.com/en-us/library/ms181032(v=sql.105).aspx

[table-valued-functions]: https://docs.microsoft.com/en-us/dotnet/framework/data/adonet/sql/linq/how-to-use-table-valued-user-defined-functions
