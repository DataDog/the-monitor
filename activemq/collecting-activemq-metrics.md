# Collecting ActiveMQ&nbsp;metrics


In [Part 1 of this series][part-1], we looked at how ActiveMQ works, and the key metrics you can monitor to ensure proper performance of your messaging infrastructure. In this post, we'll show you some of the tools that you can use to collect ActiveMQ metrics. This includes tools that ship with ActiveMQ, and some other tools that make use of Java Management Extensions (JMX) to monitor ActiveMQ brokers and destinations.

|Tool|Description|Metrics it collects|
|[ActiveMQ command line tools](#activemq-command-line-tools)|Scripts that are included with ActiveMQ|Limited broker and destination metrics|
|[ActiveMQ Web Console](#activemq-web-console)|A GUI-based tool that's included with ActiveMQ|Limited broker and destination metrics|
|[JConsole](#collecting-activemq-metrics-with-jmx-and-jconsole)|A GUI-based tool that's included with the JDK and uses JMX to fetch metrics|Broker and destination metrics, JVM metrics|
|[Hawtio](#hawtio)|A GUI-based tool that uses JMX to fetch metrics|Broker and destination metrics, JVM metrics|
|[Statistics plugin](#statistics-plugin)|An ActiveMQ plugin that sends metrics as JMS messages|Broker and destination metrics|

## ActiveMQ command line tools
ActiveMQ comes with scripts you can execute from a [Windows][activemq-cli-windows] or [Unix-like command line][activemq-cli-linux] to retrieve basic metrics about your broker and destinations (queues and topics). The commands differ across platforms, and the ActiveMQ documentation describes the syntax of the commands and their arguments. 

The `bstat` command shows you the number of messages enqueued and dequeued by each destination, as well as the `TotalEnqueueCount` and `TotalDequeueCount` [broker metrics][part-1-broker-metrics] we looked at in Part 1 of this series. The example below shows an excerpt of the output of the `bstat` command on an Ubuntu host.

```
[...]
BrokerName = localhost
TotalEnqueueCount = 57100
TotalDequeueCount = 0
TotalMessageCount = 57100
TotalConsumerCount = 0
Uptime = 1 hour 6 minutes

Name = TEST_QUEUE
destinationName = TEST_QUEUE
destinationType = Queue
EnqueueCount = 57100
DequeueCount = 0
ConsumerCount = 0
DispatchCount = 0
[...]
```

You can use the `dstat` command to view the [destination metrics][part-1-destination-metrics] from Part 1 of this series, minus the `ExpiredCount` metric. The output below shows a sample of the statistics returned by the `dstat` command on an Ubuntu host. As you can see, the `dstat` output names these metrics differently than their JMX attribute names: `ProducerCount` appears in the `Producer #` column, `ConsumerCount` appears as `Consumer #`, `QueueSize` as `Queue Size`, and `MemoryPercentUsage` as `Memory %`.

```
[...]
Name		Queue Size	Producer #	Consumer #	Enqueue #	Dequeue #	Forward #	Memory %	Inflight #
TEST_QUEUE	57100	        1		0               57100           0		0               70              0

```
You can use these commands to view some of the key metrics we introduced in Part 1 of this series, but you won't see data on key metrics like `ExpiredCount`, `StorePercentUsage`, or `TempPercentUsage`. In the following sections, we'll describe several other tools that provide more complete visibility into the performance of your broker and destinations.

## ActiveMQ Web Console
The ActiveMQ [Web Console][activemq-web-console] is an interactive, GUI-based tool that gives you an easy way to view metrics. Since it ships with ActiveMQ, you don't need to install anything to start using it. The Web Console operates on port 8161 by default, so your ActiveMQ host will need to be configured to accept connections on that port (or you can [update your ActiveMQ configuration][activemq-web-console-port] to use a different port). To use the Web Console, browse to `http://<YOUR_ACTIVEMQ_HOST_IP>:8161/admin` and log in with the username **admin** and the password **admin**. 

To change the default password, edit the **jetty-realm.properties** file in the **conf/** subdirectory of your ActiveMQ installation. Locate the following line:

```
admin: admin, admin
```
This line follows the format `<USERNAME>: <PASSWORD>, <ROLE>`, meaning that it creates an **admin** user, gives this user a password of **admin**, and assigns it to the **admin** role. To update the password for the **admin** user, edit the second instance of  **admin**, as shown below.

```
admin: <MY_NEW_PASSWORD>, admin
```

Locate this line and comment it out to limit Web Console access to **admin** users:

```
# user: user, user
```

[Stop, then restart ActiveMQ][activemq-stop-start]. You can now log in with the username **admin** and the password **\<MY_NEW_PASSWORD\>** to access the Web Console as an admin-level user.

{{< img src="web_console1.png" alt="ActiveMQ's Web Console displays basic information about the broker." wide="true" >}}

The main page of the Web Console displays information about the [broker's memory usage][part-1-broker-metrics] (`MemoryPercentUsage`), as well as store usage (`StorePercentUsage`) and temp usage (`TempPercentUsage`). You can use the top navigation bar to view pages that list data from your queues and topics. These lists display each destination's [metrics][part-1-destination-metrics], including the number of pending messages  (`QueueSize`) and the number of consumers (`ConsumerCount`).

{{< img src="web_console2.png" alt="The Queues page of the Web Console lists some metrics from each queue, including the number of enqueued messages." caption="The Queues page of the Web Console lists some metrics from each queue, including the number of enqueued messages." wide="true" >}}

The Web Console shows most (but not all) of the broker and destination metrics we highlighted in [our guide to key ActiveMQ metrics][part-1], plus information about some optional features like [broker networks][activemq-networks-of-brokers] and [scheduled messages][activemq-scheduled-messages]. To get access to all of the metrics we covered in Part 1, and to view historical data about your JVM's resource usage, you'll need to directly query Java Management Extensions (JMX) by using a tool like JConsole.

## Collecting ActiveMQ metrics with JMX and JConsole
Like other Java applications, ActiveMQ exposes metrics through [JMX][oracle-jmx]. [JConsole][oracle-jconsole] is an application you can use to monitor any Java app that implements JMX, [including ActiveMQ][activemq-jmx]. JConsole is included in the Java Development Kit (JDK), and it can communicate with any Java application that provides MBeans: JMX-compliant objects that expose the app's attributes and operations.

In this section, we'll show you how to configure and launch JConsole, then we'll look at how to view ActiveMQ metrics in JConsole.

### Configuring ActiveMQ to allow remote monitoring via JConsole
JConsole is a GUI-based tool, so it requires a platform that provides a GUI environment in which it can run. Because your ActiveMQ infrastructure may not provide a GUI environment, and because JConsole is fairly resource intensive, you'll often need to run JConsole on a machine other than your ActiveMQ host. To do so, you’ll need to configure your ActiveMQ host to allow remote access, which demands  appropriate security considerations. For the sake of demonstration, the simplified configuration in this section disables SSL; see the [Oracle][oracle-monitoring] or [Apache][apache-jmx-ssl] documentation for guidance on configuring secure remote JMX access for production environments. 

To configure your ActiveMQ host to allow remote monitoring, open your hosts file (**/etc/hosts** on Linux systems) and find the line that reads `127.0.0.1 <MY_HOSTNAME>`. Replace `127.0.0.1` with your ActiveMQ host's public IP address. (Depending on your distribution, this line might read `127.0.1.1` instead of `127.0.0.1`.)

Then, edit [ActiveMQ's **env** file][activemq-env], which is normally located in the **bin/** subdirectory of your ActiveMQ installation.  Change the `ACTIVEMQ_SUNJMX_START` line to read:
``` 
ACTIVEMQ_SUNJMX_START="-Dcom.sun.management.jmxremote.port=1099 -Dcom.sun.management.jmxremote.ssl=false -Dcom.sun.management.jmxremote.access.file=${ACTIVEMQ_BASE}/conf/jmx.access -Dcom.sun.management.jmxremote.password.file=${ACTIVEMQ_BASE}/conf/jmx.password"
```

This change designates the paths to two configuration files you can use to manage access to your JMX monitoring, **jmx.access** and **jmx.password**. These files are created when you install ActiveMQ, and you can find them in the **conf/** subdirectory of your ActiveMQ installation. By default, **jmx.access** designates an `admin` user that has an access level of `readwrite`. You can add other users by adding lines to this file. For example, to create a user named `user1` with read-only privileges, you would add this line to **jmx.access**:

```
user1 readonly
```

The **jmx.password** file contains a line for each user named in **jmx.access**. Each line is in the format `<username> <password>`. To update the `admin` user's password, update **jmx.password** to reflect the new password, as shown in this example:

```
admin <MY_PASSWORD>
```

Make sure **jmx.access** and **jmx.password** are owned by the user that runs the ActiveMQ process, and are readable only by that user.

The `ACTIVEMQ_SUNJMX_START` line shown above will also configure ActiveMQ to make JMX information available via port 1099, which is the default port for the JVM's JMX connector. (See ActiveMQ's [JMX documentation][activemq-jmx] for more information about remotely accessing ActiveMQ's MBeans.) To secure the JMX connection for production use, follow the instructions [here][apache-jmx-ssl].

Restart ActiveMQ to apply the configuration change. Refer to the [ActiveMQ documentation][activemq-stop-start] to see the commands for stopping and starting ActiveMQ on your platform.

Your ActiveMQ host is now configured to accept remote connections for JMX monitoring. Next we'll show you how to get JConsole running on your client machine.

### Launching JConsole
JConsole is included in the JDK, so you'll need to [install that][oracle-jdk] on your client machine if you haven't already. Launch JConsole from a command line by typing the full path to the JConsole program. In the example below, JConsole is installed in the **/usr/bin/** directory. (See Oracle's [JConsole documentation][oracle-using-jconsole] for more information about launching JConsole.)

```
/usr/bin/jconsole
```

Select **Remote Process** in the JConsole GUI and enter your ActiveMQ host's IP address, followed by the port number, 1099. Enter the username and password you created earlier, then click **Connect.**

{{< img src="jconsole5.png" alt="When JConsole opens, you can enter connection information for your ActiveMQ host." >}}

### Viewing ActiveMQ metrics in JConsole
JConsole's **MBeans** tab shows all the JMX sources available in the JVM, formatted as a tree. The top level of each JMX source is its domain, and below that are the MBeans that belong to that domain. ActiveMQ's JMX domain is `org.apache.activemq`. Under that is a `Broker` MBean which contains MBeans for all the queues and topics associated with that broker. Part 1 of this series lists ActiveMQ's [broker][part-1-broker-metrics] metrics and [destination][part-1-destination-metrics] metrics, and lists the name of the JMX attribute that holds the value of each metric. You'll see all those attributes listed within the MBeans shown in JConsole.

{{< img src="jconsole1.png" caption="JConsole shows ActiveMQ as one of the applications available to it as an MBean." wide="true" alt="JConsole screenshot showing the ActiveMQ MBean." >}}

The broker and destination data you see in JConsole is current as of when you load the page, but it doesn't update automatically. Use the **Refresh** button to ensure your data is up to date. 

In addition to displaying metrics about ActiveMQ, JConsole shows you operating information about the JVM in which ActiveMQ is running. Under the **VM Summary** tab, you can see information about threads and memory usage that can provide useful context when you're investigating ActiveMQ performance issues.

{{< img src="jconsole2.png" wide="true" alt="Screenshot of the JConsole VM Summary tab which shows a summary of the JVM's thread count, classes loaded, and memory in use." caption="Use JConsole's VM Summary to monitor resource metrics from the JVM in which ActiveMQ is running, like thread count and memory usage." >}}

Like the Web Console, JConsole is a graphical user interface. Unlike the Web Console, JConsole allows you to see some historical data. Although JConsole doesn't show historical data about ActiveMQ's metrics, you can view timeseries data about JVM resource usage. You can graph the JVM's memory and CPU usage metrics, and also the count of classes and threads used by the JVM. These visualizations can help you spot trends in your JVM's performance. Use the **Time Range** dropdown to select your desired range—scaled down to the past minute, or zoomed out to the entire time JConsole has been running.

{{< img src="jconsole3.png" wide="true" alt="JConsole's overview tab shows graphs of CPU usage, heap memory usage, and classes loaded." >}}

We've shown how to use JConsole to remotely view ActiveMQ metrics using JMX. But JConsole doesn't provide graphs of your ActiveMQ metrics, and it requires you to open a port to allow traffic specifically for JMX requests. In the next section, we'll look at Hawtio, a JMX monitoring tool that works over HTTP and helps you visualize ActiveMQ metrics with timeseries graphs.

## Hawtio
[Hawtio][hawtio] is an open source, GUI-based tool that you can use to monitor Java applications that expose metrics via JMX. Hawtio has built-in support for ActiveMQ, and it works as a web app inside your ActiveMQ installation, similar to the Web Console. Hawtio displays broker and destination metrics as numerical data, and as timeseries graphs, which Hawtio calls **Charts**. 

{{< img src="hawtio1.png" caption="One of the views in Hawtio shows queue metrics as a timeseries graph." wide="true" alt="This Hawtio screenshot shows ten different ActiveMQ metrics visualized as timeseries graphs in one view." >}}

Hawtio uses [horizon graphs][horizon-graphs] to visualize metrics. This format uses color to maintain a consistent height even if the maximum y-axis value changes over time. The darkest regions represent the highest values. A new value that would fall above the graph's preexisting upper limit is represented in a darker shade and is plotted within the graph's existing height.

{{< img src="hawtio2.png" wide="true" caption="Instead of increasing the height of the graph as values rise, a horizon graph applies darker shades to higher values, allowing it to plot a dynamic range of y-axis values in the same vertical space." alt="A simple horizon graph shows higher values in darker colors." >}}

### Unique features of Hawtio
The timeseries graphs available in Hawtio's **Charts** tab differentiate it from JConsole and the ActiveMQ Web Console. These graphs allow you to identify trends in the performance of your messaging infrastructure, and can be helpful for troubleshooting issues.

Hawtio works over the web, which gives it some advantages over tools like JConsole and the Web Console. The Hawtio frontend makes HTTP calls to a Jolokia server that's included in your ActiveMQ installation. Jolokia's role is to serve JMX data via REST endpoints. The Hawtio UI sends requests and receives JSON responses over HTTP, which could make it easier to use in your environment, since HTTP ports are likely already in use and not blocked by a firewall. 

### Installing Hawtio
The [Hawtio documentation][hawtio-docs] describes several ways to install and run Hawtio. In this section, we'll provide example commands for installing Hawtio on an Ubuntu host that's already running ActiveMQ.

To install and configure Hawtio, first download and unzip it:

```
wget -c https://oss.sonatype.org/content/repositories/public/io/hawt/hawtio-default/2.3.0/hawtio-default-2.3.0.war
unzip hawtio-default-2.3.0.war -d hawtio
```

Note that the commands above reference version `2.3.0`. To ensure you're installing the latest version, visit the [Hawtio documentation][hawtio-docs] and find the **Download hawtio-default.war** button.

Next, move the unzipped Hawtio directory into the **webapps/** subdirectory of your ActiveMQ installation:

```
mv hawtio <PATH_TO_ACTIVEMQ_INSTALLATION>/webapps
```

Then, edit the **env** file in the **bin** directory of your ActiveMQ installation. Add the following line at the end of the file:
```
ACTIVEMQ_OPTS="$ACTIVEMQ_OPTS -Dhawtio.realm=activemq -Dhawtio.role=admins -Dhawtio.rolePrincipalClasses=org.apache.activemq.jaas.GroupPrincipal"
```

ActiveMQ relies on [Jetty][jetty] to serve its web applications, such as Hawtio and the Web Console. Jetty is included in the ActiveMQ download. To configure Jetty for Hawtio, edit **jetty.xml** in the **conf/** subdirectory under your ActiveMQ installation directory to add Hawtio as a web component of your ActiveMQ installation. Find the `<ref bean="rewriteHandler"/>` tag and add this block immediately after it:

```
<bean class="org.eclipse.jetty.webapp.WebAppContext">
<property name="contextPath" value="/hawtio" />
<property name="resourceBase" value="${activemq.home}/webapps/hawtio" />
<property name="logUrlOnStart" value="true" />
</bean>
```

Hawtio's **admin** user comes with a default password of **admin**. To customize your Hawtio installation with a secure password, edit the **conf/users.properties** file. Locate  the line that reads:

```
admin=admin
```

Edit it by specifying your desired password:

```
admin=<MY_NEW_PASSWORD>
```

Restart ActiveMQ and browse to `http://<YOUR_ACTIVEMQ_HOST_IP>:8161/hawtio`. You can now log in with the username **admin** and the password **\<MY_NEW_PASSWORD\>**. 

### Using Hawtio
After you've logged in to Hawtio, click the **ActiveMQ** link in the left navigation. If you have one or more queues, you'll see a **Queue** item beneath the broker name (which is `localhost` in the screenshot below). Click the pointer next to **Queue** to reveal a list of queues you're monitoring. (The **Topic** item below this one works the same way.) Click the name of a queue to view a table of its attributes.

{{< img src="hawtio3.png" wide="true" alt="Hawtio's attributes tab shows a number of queue metrics as numerical values." >}}

Click the **Chart** tab to load a visualization showing all of the queue's metrics. By default, the chart displays all metrics available from this queue. Click the **Edit** button to select a subset of attributes to view.

{{< img src="hawtio4.png" wide="true" alt="Hawtio's chart tab includes a control that allows you to select the JMX attributes to be included in the chart." >}}

As the horizon graph continues to collect metric data, it reflects the changing values of the attributes you're monitoring.

{{< img src="hawtio5.png" wide="true" alt="Hawtio's chart tab shows graphs of a subset of the available JMX metrics." >}}

Hawtio, JConsole, and the ActiveMQ Web Console are GUI-based tools that don't allow you to programmatically fetch ActiveMQ metrics. But for a more thorough approach to monitoring your ActiveMQ setup, you can use tools that allow you to write code to automate your monitoring.

Next, we'll look at the statistics plugin, which allows you to collect metrics by sending and receiving JMS messages.

## Statistics plugin
As of version 5.3+, ActiveMQ includes a [statistics plugin][activemq-statistics-plugin] that uses its native messaging functionality to send metrics. The gateway for communicating with the statistics plugin is a set of destinations created automatically by ActiveMQ. When you send an empty message to one of the statistics destinations, ActiveMQ will respond by sending broker or destination metrics in a JMS message to a destination you specify.

For example, to generate a JMS message containing broker metrics, you can send an empty message to the broker statistics destination (named `ActiveMQ.Statistics.Broker`). To fetch metrics for a destination named `MY_DESTINATION`, send an empty message to `ActiveMQ.Statistics.Destination.MY_DESTINATION`. You can also use wildcards in the names of statistics destinations: to generate statistics messages for all destinations, send a message to `ActiveMQ.Statistics.Destination.>`. See the [ActiveMQ documentation][activemq-wildcards] for more information about wildcards.

### Enabling the statistics plugin
The statistics plugin isn't enabled by default. To enable it, edit the **activemq.xml** file in the **conf/** subdirectory under your ActiveMQ installation. Extend the `<broker>` element to include a `<plugins>` child element if there isn't one, and add the `<statisticsBrokerPlugin/>` element inside it, as shown in the partial **activemq.xml** file below. Note that your `<broker>` and `<plugins>` elements might look different, depending on your broker configuration:

```
<broker xmlns="http://activemq.apache.org/schema/core" brokerName="myBroker">
[...]
    <plugins>
        <statisticsBrokerPlugin/>
    </plugins>
[...]
</broker>
```
### Collecting metrics via the statistics plugin
Though you're most likely to benefit by interacting programmatically with the statistics plugin, the screenshot below illustrates using the Web Console to send an empty message to the `ActiveMQ.Statistics.Broker` destination, which will trigger the statistics plugin to retrieve broker statistics.

{{< img src="web_console3a.png" caption="Send an empty message to the statistics plugin to receive metrics via JMS messages." wide="true" alt="ActiveMQ web console screenshot shows the form to send an empty message to one of the destinations monitored by the statistics plugin." >}}

The statistics plugin will respond by sending a message to the queue specified in the **Reply to** field (in this example, `MY_REPLY_QUEUE`). That message contains current values of broker metrics, formatted as JSON, as in the example below. 

```
{  
   averageMessageSize=1024,
   minEnqueueTime=4029.0,
   expiredCount=0,
   stomp+ssl=,
   inflightCount=0,
   ssl=,
   tempUsage=0,
   tempLimit=23829045248,
   stomp=stomp://activemq-test-wed5:61613?maximumConnections=1000&wireFormat.maxFrameSize=104857600,
   storePercentUsage=0,
   dequeueCount=0,
   brokerId=ID:activemq-test-wed5-45417-1533846745754-0:1,
   memoryUsage=1024,
   consumerCount=0,
   storeUsage=426786,
   dataDirectory=/root/activemq/data,
   memoryPercentUsage=0,
   averageEnqueueTime=5346.0,
   messagesCached=0,
   maxEnqueueTime=6663.0,
   dispatchCount=2,
   size=1,
   openwire=tcp://activemq-test-wed5:61616?maximumConnections=1000&wireFormat.maxFrameSize=104857600,
   vm=vm://localhost,
   storeLimit=23829445796,
   producerCount=0,
   memoryLimit=726571418,
   brokerName=localhost,
   enqueueCount=10,
   tempPercentUsage=0
}
 ```

To automate your ActiveMQ monitoring, you can write a producer to prompt the statistics plugin for metrics, and a consumer to receive and process them. You can get started with the sample code that's included in the [statistics plugin documentation][activemq-statistics-plugin].

## Comprehensive ActiveMQ monitoring
ActiveMQ works in conjunction with other applications (such as producers and consumers you've written) to send and receive messages. The tools covered in this post can provide you with metrics from some of your messaging infrastructure (brokers, destinations, and the JVM) but don't help you monitor the rest (producers, consumers, and infrastructure). With a complete ActiveMQ monitoring strategy, you can correlate metrics and logs from ActiveMQ with [APM][java-monitoring-apm] and infrastructure metrics from your producers and consumers to identify bottlenecks and troubleshoot performance issues. 

Datadog allows you to collect, visualize, and alert on data from more than {{< translate key="integration_count" >}} technologies across your messaging infrastructure. Coming up in [part 3][part-3] of this series, we'll look at how Datadog can help you monitor all the pieces of your ActiveMQ setup.

## Acknowledgments
We'd like to thank Gary Tully of [Red Hat][red-hat] for his technical review of this series.

_Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/activemq/collecting-activemq-metrics.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues)._

[activemq-cli-linux]: http://activemq.apache.org/unix-shell-script.html
[activemq-cli-windows]: http://activemq.apache.org/activemq-command-line-tools-reference.html
[activemq-env]: https://github.com/apache/activemq/blob/master/assembly/src/release/bin/env
[activemq-jmx]: http://activemq.apache.org/jmx.html
[activemq-networks-of-brokers]: https://activemq.apache.org/networks-of-brokers.html
[activemq-scheduled-messages]: http://activemq.apache.org/delay-and-schedule-message-delivery.html
[activemq-statistics-plugin]: http://activemq.apache.org/statisticsplugin.html
[activemq-stop-start]: http://activemq.apache.org/version-5-getting-started.html#Version5GettingStarted-StartingActiveMQStartingActiveMQ
[activemq-web-console]: https://activemq.apache.org/web-console.html
[activemq-web-console-port]: http://activemq.apache.org/web-console.html#WebConsole-Changingtheport
[activemq-wildcards]: http://activemq.apache.org/wildcards.html
[apache-jmx-ssl]: https://db.apache.org/derby/docs/10.9/adminguide/radminjmxenablepwdssl.html
[hawtio]: http://hawt.io/
[hawtio-docs]: http://hawt.io/docs/get-started/
[horizon-graphs]: http://www.stonesc.com/Vis08_Workshop/DVD/Reijner_submission.pdf
[java-monitoring-apm]: https://www.datadoghq.com/blog/java-monitoring-apm/
[jetty]: https://www.eclipse.org/jetty/
[oracle-jconsole]: https://docs.oracle.com/javase/10/management/using-jconsole.htm
[oracle-monitoring]: https://docs.oracle.com/javase/10/management/monitoring-and-management-using-jmx-technology.htm
[oracle-jdk]: https://docs.oracle.com/javase/10/install/overview-jdk-10-and-jre-10-installation.htm
[oracle-jmx]: http://www.oracle.com/technetwork/java/javase/tech/javamanagement-140525.html
[oracle-using-jconsole]: https://docs.oracle.com/javase/10/management/using-jconsole.htm
[part-1]: /blog/activemq-architecture-and-metrics/
[part-1-broker-metrics]: /blog/activemq-architecture-and-metrics/#broker-metrics
[part-1-destination-metrics]: /blog/activemq-architecture-and-metrics/#destination-metrics
[part-1-what-is-activemq]: /blog/activemq-architecture-and-metrics/#what-is-activemq
[part-3]: /blog/monitoring-activemq-with-datadog/
[red-hat]: https://www.redhat.com/
