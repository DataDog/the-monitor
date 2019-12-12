# Monitoring Windows Server 2012 with Datadog


*This post is part 3 of a 3-part series on monitoring health and performance of the Windows operating system. [Part 1](https://datadoghq.com/blog/monitoring-windows-server-2012) details key Windows performance counters, events, and services to monitor; [Part 2](https://datadoghq.com/blog/collect-windows-server-2012-metrics) details how to monitor Windows with a variety of native tools. For an in-depth webinar and Q&A session based on this series, check out this [slide deck][slides] and [video][webinar-video].*

[slides]: http://www.slideshare.net/DatadogSlides/lifting-the-blinds-monitoring-windows-server-2012
[webinar-video]: https://vimeo.com/199077503/ce3175a2f5

For complete infrastructural observability, you will need a dedicated system that allows you to store, visualize, and correlate your Windows Server 2012 metrics with the rest of your infrastructure, be it on-prem, in the cloud, or a hybrid of the two.

{{< img src="server2012-dash.png" alt="Datadog Windows Dashboard" popup="true" size="1x" >}}

With Datadog, you can collect Windows metrics for visualization, alerting, and full-infrastructure correlation. Datadog will automatically collect the key metrics discussed in parts [one](https://datadoghq.com/blog/monitoring-windows-server-2012) and [two](https://datadoghq.com/blog/collect-windows-server-2012-metrics) of this series, and make them available in a customizable dashboard, as seen above.

Integrating Windows Server 2012 with Datadog
--------------------------------------------

### Install the Agent


The Datadog Agent is [open source software](https://github.com/DataDog/dd-agent) that collects and reports metrics from your hosts so that you can view and monitor them in Datadog.

First, download the [Datadog Agent installer for Windows](https://s3.amazonaws.com/ddagent-windows-stable/ddagent-cli.msi). Next, double-click the installer and follow the prompts to install the Agent.

To install the Agent from the command line (to automate installation), open a command prompt (`cmd.exe`) in the directory you downloaded the installer and run the following command (you may need to run cmd.exe with elevated privileges):

`msiexec /qn /i ddagent-cli.msi APIKEY="API_KEY"`

substituting `API_KEY` with an [API key from your account](https://app.datadoghq.com/account/settings#api). You can optionally add a hostname and tags, with the `HOSTNAME` and `TAGS` arguments, respectively.

If you're deploying the Agent on Azure, you can use the above method, or [Azure specific instructions](https://docs.datadoghq.com/integrations/azure/), to automatically monitor newly provisioned hosts.

### Start the Agent

The Agent should start running as soon as it's installed. If it didn't, you can manually start the Agent from the Datadog Agent Manager shortcut in the Start Menu.

{{< img src="default-host.png" alt="Host reporting in" popup="true" size="1x" >}}

As soon as the Agent is up and running, you should see your host reporting metrics in your [Datadog account](https://app.datadoghq.com/infrastructure).

### Configure the Agent

Next you will need to enable the Windows integrations in the Agent. In the Datadog Agent Manager, select and enable the **Win32 Event Log**, **Windows Service**, and **Wmi Check** integrations.

{{< img src="enable-integrations-1.gif" alt="Enable the integrations in the Agent" popup="true" size="1x" >}}

#### Copy and verify configuration

Once you've enabled each integration, download the integration configurations from [GitHub](https://github.com/vagelim/windows-server-2012) so you can begin collecting all of the metrics from [part 1 of this series](https://datadoghq.com/blog/monitoring-windows-server-2012) right away.

Copy and paste the new configurations into the corresponding integration pane. **Make sure** you press *Save* after pasting.

Last but not least, [restart the Agent](https://docs.datadoghq.com/agent/guide/agent-commands/#restart-the-agent) and check the Agent status to ensure that everything is working correctly.

{{< img src="restart-agent-windows1.gif" alt="Restart Agent and check status" popup="true" size="1x" >}}

### Enable the integration in Datadog

{{< img src="install-integration.png" alt="Enable the integrations" popup="true" size="1x" >}}

Next, click the *Windows Service* and *WMI* **Install Integration** buttons inside your Datadog account, under the Configuration tabs in the [Windows Service](https://app.datadoghq.com/account/settings#integrations/windows_service) and [WMI](https://app.datadoghq.com/account/settings#integrations/wmi) integration settings, respectively.

Customizing configuration
-------------------------

Over time, you may find that you want to monitor additional Windows Server metrics, not covered by the out-of-the-box configurations. All Datadog configuration is managed with YAML files ([read a quickstart here](https://learnxinyminutes.com/docs/yaml/)).

### Configuring additional metrics

To track more metrics than those covered in the basic configuration, in the Datadog Agent Manager, navigate to the *Wmi Check* integration configuration (or open the file directly at `C:\ProgramData\Datadog\conf.d\wmi_check.yaml`).

For example, if you want to track a CPU counter, you would start by adding its class the bottom of the file:

`- class: Win32_PerfFormattedData_PerfOS_Processor`

Here, the class which contains the counter is `Win32_PerfFormattedData_PerfOS_Processor`. Most performance counters are located under classes which begin with `Win32_PerfFormattedData_`.

If you're unsure of the class the performance counter is located in, you can use either [Powershell](#using-powershell-for-metric-classes-and-properties) or [wbemtest](#using-wbemtest-for-metric-classes-and-properties) for tracking down the class names and properties of the metrics you want to monitor.

#### Adding a new metric

To continue our example, we will add the Deferred Procedure Calls Queued per second metric to our WMI Check.

```
 - class: Win32_PerfFormattedData_PerfOS_Processor
    metrics:
      - [DPCsQueuedPersec, system.dpc.queue, gauge]
    tag_by: Name
```

The `class` matches the one found in wbemtest, `DPCsQueuedPersec` is the property we want to track, `system.dpc.queue` is how the name will appear in Datadog, and `gauge` is the [metric type](https://docs.datadoghq.com/developers/metrics/gauges/). The `tag_by` line indicates that the metric will be tagged with Name information (in this case, the processor number).

After saving your configuration, [restart the Agent](https://docs.datadoghq.com/agent/guide/agent-commands/?tab=agentv6#restart-the-agent).

If you're still having questions about configuring WMI metrics, check [our FAQ on retrieving WMI metrics](https://docs.datadoghq.com/integrations/faq/how-to-retrieve-wmi-metrics/) and [WMI documentation](https://docs.datadoghq.com/integrations/wmi_check/) for articles which go a bit more in-depth than the above example.

#### Using wbemtest for metric classes and properties

A good tool to help find the names of metric classes is `wbemtest.exe`. Open it up from `C:\Windows\System32\wbem\wbemtest.exe`.

{{< img src="wbemtest.gif" alt="Wbemtest run-through" popup="true" size="1x" >}}

Connect to the local host by clicking *Connect*, leaving the Namespace as `root\cimv2`, and clicking *Connect* once more.

{{< img src="wbem-connect.png" alt="Connect wbemtest" size="1x" >}}

Next, select *Enum Classes*, and in the popup, change the radio button to *Recursive* and click *OK*.

{{< img src="wbem-recursive.png" alt="Change radio button" size="1x" >}}

In the next window, navigate to the object for the metric you want and double-click it to open a window with all of its properties.

{{< img src="wbem-prop.png" alt="Wbemtest properties" size="1x" >}}

With both class name and property in hand, you can return to the WMI Check configuration and [add in your values](#adding-a-new-metric).

#### Using Powershell for metric classes and properties

You can also use Powershell to list all of the available WMI classes with the following line:

`Get-WmiObject -List`

and retrieve all of the properties of a class with:

`Get-WmiObject -Query "select * from <CLASS>"`

The following will show all properties of the `Win32_PerfFormattedData_PerfOS_Processor` class:

```
PS C:\programdata\Datadog\conf.d> Get-WmiObject -Query "select * from Win32_PerfFormattedData_PerfOS_Processor"

__PATH                : \\EVAN-SERVER2012\root\cimv2:Win32_PerfFormattedData_PerfOS_Processor.Name="_Total"
C1TransitionsPersec   : 15
C2TransitionsPersec   : 50
C3TransitionsPersec   : 0
Caption               :
Description           :
DPCRate               : 0
DPCsQueuedPersec      : 7
Frequency_Object      :
Frequency_PerfTime    :
Frequency_Sys100NS    :
InterruptsPersec      : 93
Name                  : _Total
PercentC1Time         : 20
PercentC2Time         : 75
PercentC3Time         : 0
PercentDPCTime        : 0
PercentIdleTime       : 96
PercentInterruptTime  : 0
PercentPrivilegedTime : 0
PercentProcessorTime  : 0
PercentUserTime       : 0
Timestamp_Object      :
Timestamp_PerfTime    :
Timestamp_Sys100NS    :
PSComputerName        : EVAN-SERVER2012
```

### Configuring additional events

You can customize the Windows Event Log integration to collect information from any event log on your local or remote system. Start by navigating to the *Win32 Event Log* pane in the Datadog Agent Manager or opening the configuration file directly at `C:\ProgramData\Datadog\conf.d\win32_event_log.yaml`.

The event log integration configuration follows this format:

```
  - log_file:
      - System
    type:
      - Error
    tags:
      - system
```

where:



-   `log_file` is either: `Application`, `System`, `Setup`, or `Security`
-   `type` is one of: `Critical`, `Error`, `Warning`, `Information`, `Audit Success`, `Audit Failure`
-   `tags` are any tags you'd like to add to the event



After saving your configuration, [restart the Agent](https://docs.datadoghq.com/agent/guide/agent-commands/#restart-the-agent).

### Configuring additional services

You can customize the Windows Service integration to collect information about any local or remote service. Start by navigating to the *Windows Service* pane in the Datadog Agent Manager or opening the configuration file directly at `C:\ProgramData\Datadog\conf.d\windows_service.yaml`.

First, find the short name (also referred to as "Service name" in contrast with the human-readable "Display name") of the service you want to monitor by opening the Service management snap-in `services.msc`. Next, find the name of the service, right-click, and select *Properties*. In the popup, you will find the short name listed as the Service name.

{{< img src="service-shortname-1.png" alt="Windows service shortname" size="1x" >}}

Add a dash and the short name of the service you want to monitor below the `services:` line, like so:

```
    -   host: . # "." means the current host
        services:
          - wmiApSrv
          - LSM
          - Win32Time
```

After saving your configuration, [restart the Agent](https://docs.datadoghq.com/agent/guide/agent-commands/#restart-the-agent).

Show me the servers!
--------------------

Once the Agent begins reporting metrics, events, and services, you will see a comprehensive Windows dashboard among your list of available dashboards in Datadog. The default Windows dashboard, as seen at the top of this article, displays all of the key metrics highlighted in our introduction on [how to monitor Windows](https://datadoghq.com/blog/monitoring-windows-server-2012).

You can easily create a more comprehensive dashboard to monitor your entire web stack by adding additional graphs and metrics from your other systems. For example, you might want to graph metrics alongside metrics from [Kafka](https://www.datadoghq.com/blog/monitoring-kafka-performance-metrics/), or alongside host-level metrics such as memory usage on application servers.

To start building a custom dashboard, clone the default Windows dashboard by clicking on the gear on the upper right of the dashboard and selecting **Clone Dash**.

{{< img src="windows-clone.png" alt="Clone dash image" popup="true" size="1x" >}}

Alerts
------

Once Datadog is capturing and visualizing your metrics, you will likely want to [set up some alerts](https://docs.datadoghq.com/monitors/) to be automatically notified of potential issues. With our powerful [outlier detection](https://www.datadoghq.com/blog/introducing-outlier-detection-in-datadog/) feature, you can get automatically alerted on strange server behavior. For example, you can set an alert if a particular host is experiencing an increase in latency while the others are operating normally.

Datadog can monitor individual hosts, containers, [virtual machines](https://www.datadoghq.com/blog/how-to-monitor-microsoft-azure-vms/), services, processes—or virtually any combination thereof. For instance, you can view all of your Windows hosts, SQL servers, Active Directory controllers, or all hosts in a certain availability zone or resource group, or even a single metric being reported by all hosts with a specific tag.

Conclusion
----------

In this post we’ve walked you through integrating Windows Server 2012 with Datadog to visualize your [key metrics](https://datadoghq.com/blog/monitoring-windows-server-2012) and [notify the right team](https://docs.datadoghq.com/monitors/notifications/) whenever your infrastructure shows signs of trouble.

If you’ve followed along using your own Datadog account, you should now have increased the observability of your environment, as well as the ability to create automated alerts tailored to your infrastructure, your usage patterns, and the metrics that are most valuable to your organization.

If you don’t yet have a Datadog account, you can <a href="#" class="sign-up-trigger">sign up for a free trial</a> and start to monitor Windows Server 2012 today.
