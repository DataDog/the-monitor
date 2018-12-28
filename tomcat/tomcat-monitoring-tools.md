In [Part 1][part-one-link] of this series, we discussed some key Tomcat and JVM metrics that are exposed through Java Management Extensions (JMX). Now that you are familiar with metrics necessary for monitoring Tomcat, we can look at how to collect and query that data. In this post, we'll walk through:

- [using Tomcat Manager](#using-tomcat-managers-web-interface), a built-in web management interface
- [enabling remote connections for JMX](#enabling-remote-jmx-connections-for-tomcat-monitoring-tools)
viewing metrics with other monitoring platforms like [JConsole](#using-jconsole) and [JavaMelody](#using-javamelody)
- [viewing and customizing Tomcat server and access logs](#customizing-tomcat-access-and-server-logs)

## Tomcat Manager
[Tomcat Manager](https://tomcat.apache.org/tomcat-9.0-doc/manager-howto.html) gives administrators the ability to manage applications and hosts in one place. The management interface comes with every installation of Tomcat and includes quick-start guides and links to documentation for your version of Tomcat. From this interface you can view Tomcat metrics, and query metric data through a JMX proxy servlet. 

{{< img src="2-tomcat-monitoring-manager.png" popup="true" alt="Tomcat monitoring page" >}}


### Tomcat Manager roles and permissions
Though the management interface is included out of the box, you won't be able to access it or query metrics through its JMX proxy servlet until you set up the appropriate users and roles. Tomcat includes [several roles](https://tomcat.apache.org/tomcat-9.0-doc/manager-howto.html#Configuring_Manager_Application_Access) that offer various levels of permissions needed for accessing various Tomcat Manager components, configuring applications and hosts, and querying metrics via JMX. The two roles that are most relevant for monitoring Tomcat are:  

- **manager-jmx**: provides access to both the JMX proxy servlet and Tomcat's server status page  
- **manager-gui**: grants access to Tomcat's application manager, where you can run diagnostics and manually trigger garbage collection

In order to access Tomcat metrics from the management interface, you will need to assign the appropriate role(s) to a user. You can do so by updating Tomcat's **conf/tomcat-users.xml** configuration file:

```
  <role rolename="manager-gui"/>
  <role rolename="manager-jmx"/>
  <user username="tomcat-jmx" password="<YOUR_PASSWORD>" roles="manager-jmx,manager-gui"/>
```

This code snippet first defines the two roles we want to assign to our user. Then it creates a new `tomcat-jmx` user, assigns it those roles, and sets a password for the user. If you are using a fresh install of Tomcat, you will need to create a new user; otherwise, you can assign roles to any existing user. Check out the [Tomcat docs](https://tomcat.apache.org/tomcat-9.0-doc/manager-howto.html#Configuring_Manager_Application_Access) for more information on the roles available for Tomcat Manager. 

### Using Tomcat Manager's web interface
By default, Tomcat Manager is accessible locally from `http://localhost:8080`, though you can change this in Tomcat's server configuration file. When you access the web interface, you will be prompted to log in. From there, you can navigate to the following areas to view metric data: 

- **Server and application status pages**: display high-level overviews of JVM, connector, and application metrics, including memory usage, thread counts, and request processing time 
- **Application Manager**: provides diagnostic tools for investigating memory leaks within your applications 
- **JMX Proxy**: a text-based interface for querying Tomcat metrics

#### Tomcat's server status page
If you need a high-level [view of application and server metrics](https://tomcat.apache.org/tomcat-9.0-doc/manager-howto.html#Server_Status), you can navigate to the `/manager/status` page or click on the "Server Status" button from the home page. This page includes information about the Tomcat server and its AJP and HTTP connectors, as well as memory usage for the JVM.

{{< img src="3-tomcat-monitoring-page-server-status.png" popup="true" alt="Tomcat monitoring using the manager server status page" >}}

Each connector section displays information about thread usage (e.g., max threads, current thread count, and current number of busy threads) and request throughput and performance (e.g., processing time, error counts, and bytes received), as well as information about each active thread, including its current stage. Each thread progresses through a series of stages as it processes a request:

- **Ready:** The thread is available to process a request.
- **Parse and Prepare Request:** The thread is parsing request headers or preparing to read the body of the request. 
- **Service:** The thread is processing and generating a response for an incoming request. 
- **Finishing:** The thread has finished processing the request and is sending a generated response back to the client.
- **Keep-Alive:** The thread is keeping the connection open for the same client to send another request. The maximum duration of this stage is determined by the `keepAliveTimeout` value set in the server's configuration file. After the connection times out, the thread goes back to the Ready stage.

Thread stages can help you accurately gauge the number of threads that are ready to accept incoming requests. You can also view the request count for each deployed application within Tomcat's application list on the server status page. 

#### Tomcat application status page
In order to view the status of all of your deployed applications, you can navigate to the `manager/status/all` page. This page lists all applications, including Tomcat Manager itself, so you can quickly view processing times, active sessions, and the number of JSP servlets loaded for each application, calculated as a cumulative count from the start of the server. 

{{< img src="4-tomcat-monitoring-manager-app-list.png" popup="true" alt="The Tomcat monitoring manager application list" >}}

#### The application manager
For running diagnostics, you can navigate to Tomcat's application manager interface at  `/manager/html` or by clicking on the "Manager App" button from the Tomcat Manager home page. The application manager provides a simple interface for quickly managing applications, and a _Diagnostics_ section for troubleshooting memory leaks. 

{{< img src="5-tomcat-monitoring-manager-diagnostics.png" popup="true" alt="Diagnostics and Tomcat health check using Tomcat manager" >}}

In this section, you can run a diagnostic check for memory leaks in your application. Memory leaks occur when the garbage collector cannot free up working memory by removing objects that are no longer needed by the application. This causes the application to use more resources until it runs out, generating a fatal memory error. Monitoring [Tomcat memory usage metrics][part-one-memory-link] will help catch problems before they become more serious. Note that this diagnostic check should be used with caution, because it triggers [garbage collection](https://tomcat.apache.org/tomcat-9.0-doc/html-manager-howto.html#Finding_memory_leaks), which can be a memory-intensive process. 

The Tomcat web interface provides easy access to the state of your Tomcat server, enabling you to quickly view high-level metric data. Tomcat also includes an interface for looking at MBean data related to your application, giving you more control over the metrics you need to monitor. In the next section, we'll look at using the JMX proxy servlet for querying these metrics. 

#### Query Tomcat metrics
Tomcat Manager includes access to a JMX proxy servlet with the `manager-jmx` role, which allows you to query metrics from your web browser. You can find a list of the available MBeans for Tomcat (in plain-text format) at `http://localhost:8080/manager/jmxproxy`.

{{< img src="6-Tomcat-monitoring-JMX-proxy.png" popup="true" alt="Proxy for Tomcat JMX monitoring" >}}

To see data about a specific MBean, you can add parameters to the URL for the MBean's domain, type, name, and attribute in the following format:

```
http://localhost:8080/manager/jmxproxy/?get=<DOMAIN>:type=<TYPE>,name="<NAME>"&att=<JMX_ATTRIBUTE> 
```

You can find these parameters in the JMX attribute and MBean columns of the metric tables in [Part 1][link-to-throughput-section]. For example, you can use the following to view data for the HTTP connector's maximum request processing time: 

```
http://localhost:8080/manager/jmxproxy/?get=Catalina:type=GlobalRequestProcessor,name="http-nio-8080"&att=maxTime
```

Which will yield the following result:

```
OK - Attribute get 'Catalina:type=GlobalRequestProcessor,name="http-nio-8080"' - maxTime = 189
```

The JMX proxy interface is a good way to quickly query and [update](https://tomcat.apache.org/tomcat-9.0-doc/manager-howto.html#JMX_Set_command) metrics within Tomcat Manager, and can be integrated into command line scripts or utilities. However, it doesn't give you an easy way to compare multiple metrics or view how that data changes over time. In order to get deeper insights into Tomcat health and performance, you'll need to use another tool like JConsole or JavaMelody.

## Enabling remote JMX connections for Tomcat monitoring tools
Before you can use a tool like JConsole or JavaMelody to monitor your Tomcat server, you will need to enable remote connections for JMX. JConsole can consume a lot of system resources, so Oracle [recommends](https://docs.oracle.com/javase/8/docs/technotes/guides/management/agent.html#gdemy) isolating JConsole from the server you are monitoring by connecting to remote hosts only. Note that enabling remote JMX access demands appropriate security precautions, as JMX provides limited access control. For the sake of demonstration, the simplified configuration in this section disables SSL; see [the Java documentation](https://docs.oracle.com/javase/8/docs/technotes/guides/management/agent.html#gdevo) and Tomcat's [security guide](https://tomcat.apache.org/tomcat-9.0-doc/security-howto.html#JMX) for information on securing remote JMX access for production environments.

First, create a **setenv.sh** file in Tomcat's **/bin** directory and include the following:

```
export JAVA_OPTS="${JAVA_OPTS} -Dcom.sun.management.jmxremote"
export JAVA_OPTS="${JAVA_OPTS} -Dcom.sun.management.jmxremote.port=<PORT>"
export JAVA_OPTS="${JAVA_OPTS} -Djava.rmi.server.hostname=<TOMCAT_HOST_OR_IP>"
export JAVA_OPTS="${JAVA_OPTS} -Dcom.sun.management.jmxremote.ssl=false"
export JAVA_OPTS="${JAVA_OPTS} -Dcom.sun.management.jmxremote.authenticate=true"
export JAVA_OPTS="${JAVA_OPTS} -Dcom.sun.management.jmxremote.access.file=${CATALINA_BASE}/conf/jmxremote.access
export JAVA_OPTS="${JAVA_OPTS} -Dcom.sun.management.jmxremote.password.file=${CATALINA_BASE}/conf/jmxremote.password
```

This sets the hostname and port that JConsole can use to connect remotely to your Tomcat server. You can specify any hostname and [unused port](https://docs.oracle.com/javase/8/docs/technotes/guides/management/agent.html#gdenl). Though this example does not include SSL, it does enable password authentication, and specifies where to find the access (username) and password files; you may need to create them if they don't already exist. You can add new users and give them one of two privileges (`readonly` and `readwrite`) by editing the **${CATALINA_BASE}/conf/jmxremote.access** file:

```
tomcatUserRead readonly
tomcatUserWrite readwrite
```

The first line grants a `tomcatUserRead` user with `readonly` privileges, which means that this user can view MBean attributes and receive notifications. The second line provides a `tomcatUserWrite` user with `readwrite` privileges, allowing that user to add and remove MBeans, set attributes, and run operations.

Next, set a password for those users in the **${CATALINA_BASE}/conf/jmxremote.password** file:

```
tomcatRead <PASSWORD>
tomcatWrite <PASSWORD>
```

Save the file and restart your Tomcat server. Next, open JConsole and run the following command, making sure to include the host and port you defined in your **setenv.sh** file:

```
jconsole <TOMCAT_HOST_OR_IP>:<PORT>
``` 

This will bring up the JConsole interface where you can begin viewing data related to your JVM and Tomcat server. 

## Using JConsole
[JConsole](https://docs.oracle.com/javase/8/docs/technotes/guides/management/jconsole.html) is a graphical interface included with the [Java SE Development Kit](http://www.oracle.com/technetwork/java/javase/downloads/index.html). JConsole provides a more visual way to monitor key JVM metrics like heap memory usage, thread usage, and CPU usage. And instead of querying data via a limited interface such as the JMX proxy, you can use JConsole to quickly view data across multiple metrics and drill down to a specific MBean type and attribute for Tomcat's **Catalina** and the JVM's **java.lang** domains. You can navigate to six different tabs: Overview, Memory, Threads, Classes, VM Summary, and MBeans. Each tab provides a dropdown menu that enables you to view data scoped to different time ranges, such as the last five minutes, the past month, or from the start of the server (shown as the "All" option in the dropdown).

### Overview
JConsole's Overview tab graphs information related to the JVM's memory usage, thread counts, Java classes loaded with your application(s), and CPU usage so you can monitor the health of your virtual machine at a glance. 

{{< img src="7-tomcat-monitoring-tools-jconsole-overview.png" popup="true" alt="Tomcat monitoring tool JConsole overview tab" >}}

### VM Summary
In the VM Summary tab, you can see more detailed information about the JVM architecture and its characteristics. This is useful if you need to quickly view system-level attributes, or JVM configuration settings. This includes any arguments you specify in Tomcat's **/bin/setenv.sh** configuration file.  

{{< img src="8-tomcat-monitoring-tools-jconsole-vm-summary.png" popup="true" alt="Tomcat monitoring tool JConsole VM Summary tab" >}}

### Memory
Under the Memory tab, you can view more detailed statistics about your virtual machine's heap and non-heap memory usage, along with data about memory pools. From this tab, you can click "Perform GC" to run garbage collection, just as you would in the Tomcat Manager.

{{< img src="9-tomcat-monitoring-tools-jconsole-memory.png" popup="true" alt="Tomcat monitoring tool JConsole memory tab" >}}

If you need to view data related to a specific memory pool, you can select it from the Chart dropdown in the top-left corner of the Memory tab. The official [JConsole docs](https://docs.oracle.com/javase/8/docs/technotes/guides/management/jconsole.html#gddzq) has more information about available memory pools. 

{{< img src="10-tomcat-monitoring-tools-jconsole-memory-pool.png" popup="true" alt="Select memory pool in JConsole for Tomcat JMX monitoring" >}}

### Threads
JConsole's Threads tab provides more detailed information about available JVM threads along with a check for deadlocked threads. The Threads list shows the thread name, state (similar to the thread "stage" you'd see on Tomcat's server status page), and stack trace for each available thread. The Deadlock check is useful for finding threads that may be causing your application to hang. If any deadlocked threads are found, you will see a new Deadlock tab with more information about what is causing the deadlocks.

{{< img src="11-tomcat-monitoring-tools-jconsole-threads.png" popup="true" alt="JConsole Threads tab for Tomcat JMX monitoring" >}}

### MBeans
To see real-time data related to the Tomcat metrics you are monitoring, you can view the **Catalina** and **java.lang** domains under the MBeans tab and drill down to specific attributes. Like Tomcat Manager, JConsole collects data from the MBean server, but provides a simpler interface for finding the metrics you need.
  
{{< img src="12-tomcat-monitoring-tools-jconsole-mbeans.png" popup="true" alt="JConsole MBeans tab for Tomcat JMX monitoring" >}}

JConsole provides a good summary of your JVM and MBean data, and it enables you to graph JVM data to visualize trends in resource usage. However, it does not include support for graphing Tomcat metrics. In the next section, we'll take a look at JavaMelody, a JConsole alternative that offers more insight into the health of Tomcat, not just the JVM.

## Using JavaMelody
[JavaMelody](https://github.com/javamelody/javamelody/wiki) is an open source monitoring platform that offers more fine-grained timeseries visualizations for Tomcat and JVM metrics. You can install JavaMelody by copying the [JavaMelody and JRobin JAR files](https://github.com/javamelody/javamelody/wiki/UserGuide#javamelody-setup) into the **WEB-INF/lib** directory of the application you want to monitor. Once you redeploy the application, you'll be able to access the monitoring page at `http://<TOMCAT_HOST_OR_IP>:<PORT>/<YOUR_APP>/monitoring`. 

Much like JConsole, JavaMelody provides timeseries graphs of JVM performance metrics. But unlike JConsole, JavaMelody also allows you to graph Tomcat health and performance metrics, including HTTP requests and database connections. You can change the time period for all graphs, and select an individual graph to get a more detailed look into any server, virtual machine, or database activity metric. 
 
{{< img src="13-tomcat-monitoring-tools-javamelody.png" popup="true" alt="Tomcat monitoring tool JavaMelody Overview" >}}

You can track Tomcat request throughput, latency, and error rates with  "HTTP hits per minute", "HTTP mean times" (average processing time), and "% of http errors" graphs (known as "charts" in JavaMelody). If you click on any chart, you will be able to see the mean, maximum, and 95th percentile values for the chosen metric. 

{{< img src="14-tomcat-monitoring-tools-javamelody-http-hits.png" popup="true" alt="Tomcat monitoring tool JavaMelody HTTP hits chart" >}}

It's important to note that JavaMelody charts persist and will not reset even if the Tomcat server restarts, though you will see a gap in chart data. 

The monitoring page also includes information about system and HTTP request errors. The **Statistics of http system errors** section shows the exceptions thrown by an application servlet along with HTTP errors generated from a request, while the **Statistics system errors logs** section shows Catalina server logs written for "WARNING" and "SEVERE" error levels.

{{< img src="15-tomcat-monitoring-tool-javamelody-stats.png" popup="true" alt="Tomcat monitoring tool JavaMelody HTTP stats" >}}

JavaMelody aggregates similar errors together so you can see how many of each type are generated. For the selected time frame, you can see the percentage of CPU time spent generating each type of error. In the example above, the Tomcat server generated errors with a 500 HTTP response code (Internal Server Error) 99 percent of the time it was running over the past week. 

JavaMelody pulls this data from Tomcat's server and access logs, which provide more fine-grained insights for analyzing request processing times and HTTP statuses. In the next section, we'll show you how to customize the information displayed in Tomcat's access and server logs by configuring [valves](https://tomcat.apache.org/tomcat-9.0-doc/config/valve.html#Access_Log_Valve) and [logging properties](https://tomcat.apache.org/tomcat-8.0-doc/logging.html#Using_java.util.logging_(default)). 

## Customizing Tomcat access and server logs
By default, Tomcat access logs use the [Common Log Format](https://httpd.apache.org/docs/1.3/logs.html#common), and record all requests processed by the server. You can view what is included in your access logs in Tomcat's **conf/server.xml** configuration file: 

```
 <Valve className="org.apache.catalina.valves.AccessLogValve" directory="logs"
               prefix="localhost_access_log" suffix=".txt"
               pattern="%h %l %u %t "%r" %s %b" />
```

The `Valve` element's `pattern` attribute specifies the information from each request (and its response) that should be included in each log entry: 

- the host name or IP address of the client that made the request (`%h`)
- the username from identd service (always returns '-') (`%l`)
- the authenticated username (returns `-` if not used) (`%u`) 
- the date and time of the request (`%t`) 
- the request method and URI (`%r`)
- the HTTP status code of the response (`%s`)
- the size of the object returned to the client, in bytes (`%b`)

The pattern used in the example above will log requests in the following format:

```
192.168.33.1 - - [21/Sep/2018:16:51:59 +0000] "GET /sample/ HTTP/1.1" 403 1145
```

You can change this format to also include the request processing time by including `%D` in the valve pattern. This pattern code logs the time taken to process the request in milliseconds—an important metric to track for understanding how well Tomcat processes individual requests. You can check out [Tomcat's documentation](https://tomcat.apache.org/tomcat-9.0-doc/config/valve.html#Access_Log_Valve/Attributes) to learn more about customizing your access logs to include other pattern codes.

Tomcat also generates server logs by default, and uses its [own implementation](https://tomcat.apache.org/tomcat-8.0-doc/logging.html#Java_logging_API_%E2%80%94_java.util.logging) of the **java.util.logging** [package](https://docs.oracle.com/javase/8/docs/api/java/util/logging/package-use.html). Server logs show information related to the Tomcat JVM and Catalina server, including out-of-memory (OOM) errors and deployment activity, as seen in the example below:

```
16-Oct-2018 18:37:08.624 INFO [main] org.apache.catalina.core.StandardService.startInternal Starting service [Catalina]
16-Oct-2018 18:37:08.625 INFO [main] org.apache.catalina.core.StandardEngine.startInternal Starting Servlet Engine: Apache Tomcat/9.0.10
16-Oct-2018 18:37:08.629 SEVERE [main] org.apache.catalina.startup.HostConfig.beforeStart Unable to create directory for deployment: [/opt/tomcat/conf/Catalina/localhost]
16-Oct-2018 18:37:08.672 INFO [main] org.apache.catalina.startup.HostConfig.deployWAR Deploying web application archive [/opt/tomcat/webapps/sample.war]
16-Oct-2018 18:37:09.341 INFO [main] org.apache.catalina.startup.HostConfig.deployWAR Deployment of web application archive [/opt/tomcat/webapps/sample.war] has finished in [667] ms
```

Tomcat writes server logs to the console and to a Catalina log file (e.g., **catalina.2018-07-03.log**). You can customize what type of information Tomcat should log, such as the minimum [log level](https://docs.oracle.com/javase/8/docs/api/java/util/logging/Level.html), output directory, and output format in Tomcat's logging properties file (**conf/logging.properties**). If you don't want to use the standard logging utility, you can use Apache's [Log4j2 utility](https://logging.apache.org/log4j/2.x/log4j-appserver/index.html) to manage log output by updating the logging handlers. 

Handlers are Java components that process incoming log messages and format their output, with formatters for logging to a file (`FileHandler`) or to your console (`ConsoleHandler`). Tomcat's logging properties file includes configurations for the Catalina server, Tomcat Manager, and deployed web application logs:

```
############################################################
# Handler specific properties.
# Describes specific configuration info for Handlers.
############################################################

1catalina.org.apache.juli.FileHandler.level = FINE
1catalina.org.apache.juli.FileHandler.directory = ${catalina.base}/logs
1catalina.org.apache.juli.FileHandler.prefix = catalina.

2localhost.org.apache.juli.FileHandler.level = FINE
2localhost.org.apache.juli.FileHandler.directory = ${catalina.base}/logs
2localhost.org.apache.juli.FileHandler.prefix = localhost.

3manager.org.apache.juli.FileHandler.level = FINE
3manager.org.apache.juli.FileHandler.directory = ${catalina.base}/logs
3manager.org.apache.juli.FileHandler.prefix = manager.
3manager.org.apache.juli.FileHandler.bufferSize = 16384

java.util.logging.ConsoleHandler.level = FINE
java.util.logging.ConsoleHandler.formatter = org.apache.juli.OneLineFormatter


############################################################
# Facility specific properties.
# Provides extra control for each logger.
############################################################

org.apache.catalina.core.ContainerBase.[Catalina].[localhost].level = INFO
org.apache.catalina.core.ContainerBase.[Catalina].[localhost].handlers = \
   2localhost.org.apache.juli.FileHandler

org.apache.catalina.core.ContainerBase.[Catalina].[localhost].[/manager].level = INFO
org.apache.catalina.core.ContainerBase.[Catalina].[localhost].[/manager].handlers = \
   3manager.org.apache.juli.FileHandler

```

By default, Tomcat sets two different log levels for its handlers (`FINE`) and facilities (`INFO`). The `FINE` log level includes detailed information about server activity, and the `INFO` level logs higher-level, informational messages. While handler properties manage your Tomcat logs overall, facility properties enable you to manage configurations for each deployed  application, including Tomcat Manager. For example, to adjust the log levels for Tomcat Manager, you can edit the following handler and facility properties:

```
3manager.org.apache.juli.FileHandler.level = FINE
3manager.org.apache.juli.FileHandler.directory = ${catalina.base}/logs
3manager.org.apache.juli.FileHandler.prefix = manager.
3manager.org.apache.juli.FileHandler.bufferSize = 16384

[...]

org.apache.catalina.core.ContainerBase.[Catalina].[localhost].[/manager].level = INFO
org.apache.catalina.core.ContainerBase.[Catalina].[localhost].[/manager].handlers = \
   3manager.org.apache.juli.FileHandler
``` 

## Comprehensive Tomcat monitoring
By setting a few simple permissions, you can immediately begin viewing Tomcat and JVM data with Tomcat Manager. And once you've enabled remote connections for JMX, you can use tools like JConsole and JavaMelody to monitor Tomcat data with simple graphical interfaces. Tomcat also provides low-level diagnostic information about requests and server activity in its access and server logs. 

Each of these platforms offers different capabilities for monitoring Tomcat, but none of them enable you to see the full picture when an issue occurs. And, if you are running Tomcat alongside other technologies like [Apache](https://www.datadoghq.com/blog/monitoring-apache-web-server-performance/) or [MySQL](https://www.datadoghq.com/blog/monitoring-mysql-performance-metrics/), then you'll need a way to monitor all of them in one platform. In the [next part][part-three-link] of this series, we'll show you how to use Datadog for comprehensive Tomcat monitoring.

[part-one-link]: /blog/tomcat-architecture-and-performance
[part-one-memory-link]: /blog/tomcat-architecture-and-performance/#jvm-memory-usage
[part-three-link]: /blog/analyzing-tomcat-logs-and-metrics-with-datadog
[link-to-throughput-section]: /blog/tomcat-architecture-and-performance#request-throughput-and-latency-metrics     
