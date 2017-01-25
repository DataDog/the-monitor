_This post is part 3 of a 3-part series on monitoring health and performance of the Windows operating system. [Part 1][part 1] details key Windows performance counters, events, and services to monitor; [Part 2][part 2] details how to monitor Windows with a variety of native tools._

For complete infrastructural observability, you will need a dedicated system that allows you to store, visualize, and correlate your Windows Server 2012 metrics with the rest of your infrastructure, be it on-prem, in the cloud, or a hybrid of the two.

[![Datadog Windows Dashboard][windows-2012-dash]][windows-2012-dash]

With Datadog, you can collect Windows metrics for visualization, alerting, and full-infrastructure correlation. Datadog will automatically collect the key metrics discussed in parts [one][part 1] and [two][part 2] of this series, and make them available in a customizable dashboard, as seen above.

## Integrating Windows Server 2012 with Datadog

### Install the Agent
The Datadog Agent is [open source software][dd-agent] that collects and reports metrics from your hosts so that you can view and monitor them in Datadog. 

First, download the [Datadog Agent installer for Windows][installer]. Next, double-click the installer and follow the prompts to install the Agent.

To install the Agent from the command line (to automate installation), open a command prompt (`cmd.exe`) in the directory you downloaded the installer and run the following command  (you may need to run cmd.exe with elevated privileges):  

`msiexec /qn /i ddagent-cli.msi APIKEY="API_KEY"`

substituting `API_KEY` with an [API key from your account][api-key]. You can optionally add a hostname and tags, with the `HOSTNAME` and `TAGS` arguments, respectively.

If you're deploying the Agent on Azure, you can use the above method, or [Azure specific instructions][azure-specific], to automatically monitor newly provisioned hosts.

### Start the Agent
The Agent should start running as soon as it's installed. If it didn't, you can manually start the Agent from the Datadog Agent Manager shortcut in the Start Menu.

[![Host reporting in][host-reporting]][host-reporting]

As soon as the Agent is up and running, you should see your host reporting metrics in your [Datadog account][infra].

[api-key]: https://app.datadoghq.com/account/settings#api
[azure-specific]: http://docs.datadoghq.com/guides/azure/
[dd-agent]: https://github.com/DataDog/dd-agent
[infra]: https://app.datadoghq.com/infrastructure
[installer]: https://s3.amazonaws.com/ddagent-windows-stable/ddagent-cli.msi


### Configure the Agent
Next you will need to enable the Windows integrations in the Agent. In the Datadog Agent Manager, select and enable the **Win32 Event Log**, **Windows Service**, and **Wmi Check** integrations.

[![Enable the integrations in the Agent][enable-integration-agent]][enable-integration-agent]

#### Copy and verify configuration
Once you've enabled each integration, download the integration configurations from [GitHub][github-configuration] so you can begin collecting all of the metrics from [part 1 of this series][part 1] right away.

Copy and paste the new configurations into the corresponding integration pane. **Make sure** you press _Save_ after pasting.

Last but not least, [restart the Agent][windows-usage] and check the Agent status to ensure that everything is working correctly.

[![Restart Agent and check status][agent-restart]][agent-restart]

[windows-usage]: https://docs.datadoghq.com/guides/basic_agent_usage/windows/

### Enable the integration in Datadog

[![Enable the integrations][enable-int]][enable-int]

Next, click the _Windows Service_ and _WMI_ **Install Integration** buttons inside your Datadog account, under the Configuration tabs in the [Windows Service][win-service-dd] and [WMI][wmi-dd] integration settings, respectively.

[win-service-dd]: https://app.datadoghq.com/account/settings#integrations/windows_service
[wmi-dd]: https://app.datadoghq.com/account/settings#integrations/wmi

## Customizing configuration
Over time, you may find that you want to monitor additional Windows Server metrics, not covered by the out-of-the-box configurations. All Datadog configuration is managed with YAML files ([read a quickstart here][yaml-quickstart]).

[yaml-quickstart]: https://learnxinyminutes.com/docs/yaml/

### Configuring additional metrics
To track more metrics than those covered in the basic configuration, in the Datadog Agent Manager, navigate to the _Wmi Check_ integration configuration (or open the file directly at `C:\ProgramData\Datadog\conf.d\wmi_check.yaml`).

For example, if you want to track a CPU counter, you would start by adding its class the bottom of the file:  

`  - class: Win32_PerfFormattedData_PerfOS_Processor`  

Here, the class which contains the counter is `Win32_PerfFormattedData_PerfOS_Processor`. Most performance counters are located under classes which begin with `Win32_PerfFormattedData_`.

If you're unsure of the class the performance counter is located in, you can use either [Powershell](#metrics-ps) or [wbemtest](#metrics-wbemtest) for tracking down the class names and properties of the metrics you want to monitor.

<div id="add-metric"></div>

#### Adding a new metric

To continue our example, we will add the Deferred Procedure Calls Queued per second metric to our WMI Check.

```
 - class: Win32_PerfFormattedData_PerfOS_Processor
    metrics:
      - [DPCsQueuedPersec, system.dpc.queue, gauge]
    tag_by: Name
```

The `class` matches the one found in wbemtest, `DPCsQueuedPersec` is the property we want to track, `system.dpc.queue` is how the name will appear in Datadog, and `gauge` is the [metric type]. The `tag_by` line indicates that the metric will be tagged with Name information (in this case, the processor number).


After saving your configuration, [restart the Agent][windows-usage].

If you're still having questions about configuring WMI metrics, check our [Knowledge Base][wmi-kb] and [documentation][wmi-doc] for articles which go a bit more in-depth than the above example.

[wmi-doc]: http://docs.datadoghq.com/integrations/wmi/
[wmi-kb]: https://help.datadoghq.com/hc/en-us/articles/205016075-How-to-retrieve-WMI-metrics

<div id="metrics-wbemtest"></div>

#### Using wbemtest for metric classes and properties
A good tool to help find the names of metric classes is `wbemtest.exe`. Open it up from `C:\Windows\System32\wbem\wbemtest.exe`. 

[![Wbemtest run-through][wbemtest-gif]][wbemtest-gif]

Connect to the local host by clicking _Connect_, leaving the Namespace as `root\cimv2`, and clicking _Connect_ once more.

[![Connect wbemtest][wbem-connect]][wbem-connect]

Next, select _Enum Classes_, and in the popup, change the radio button to _Recursive_ and click _OK_.

[![Change radio button][wbem-recursive]][wbem-recursive]

In the next window, navigate to the object for the metric you want and double-click it to open a window with all of its properties.

[![Wbemtest properties][wbem-prop]][wbem-prop]

With both class name and property in hand, you can return to the WMI Check configuration and [add in your values](#add-metric).

[metric type]: https://help.datadoghq.com/hc/en-us/articles/206955236-Metric-types-in-Datadog

<div id="metrics-ps"></div>
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
You can customize the Windows Event Log integration to collect information from any event log on your local or remote system. Start by navigating to the _Win32 Event Log_ pane in the Datadog Agent Manager or opening the configuration file directly at `C:\ProgramData\Datadog\conf.d\win32_event_log.yaml`. 

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

- `log_file` is either: `Application`, `System`, `Setup`, or `Security` 
- `type` is one of: `Critical`, `Error`, `Warning`, `Information`, `Audit Success`, `Audit Failure`  
- `tags` are any tags you'd like to add to the event

After saving your configuration, [restart the Agent][windows-usage].

### Configuring additional services

You can customize the Windows Service integration to collect information about any local or remote service. Start by navigating to the _Windows Service_ pane in the Datadog Agent Manager or opening the configuration file directly at `C:\ProgramData\Datadog\conf.d\windows_service.yaml`. 

First, find the short name (also referred to as "Service name" in contrast with the human-readable "Display name") of the service you want to monitor by opening the Service management snap-in `services.msc`. Next, find the name of the service, right-click, and select _Properties_. In the popup, you will find the short name listed as the Service name.

[![Windows service shortname][windows-service]][windows-service]


Add a dash and the short name of the service you want to monitor below the `services:` line, like so:

```
    -   host: . # "." means the current host
        services:
          - wmiApSrv
          - LSM
          - Win32Time
```


After saving your configuration, [restart the Agent][windows-usage].
## Show me the servers!

Once the Agent begins reporting metrics, events, and services, you will see a comprehensive Windows dashboard among your list of available dashboards in Datadog. The default Windows dashboard, as seen at the top of this article, displays all of the key metrics highlighted in our introduction on [how to monitor Windows][part 1]. 

You can easily create a more comprehensive dashboard to monitor your entire web stack by adding additional graphs and metrics from your other systems. For example, you might want to graph metrics alongside metrics from [Kafka], or alongside host-level metrics such as memory usage on application servers. 

To start building a custom dashboard, clone the default Windows dashboard by clicking on the gear on the upper right of the dashboard and selecting **Clone Dash**.

[![Clone dash image][windows-clone]][windows-clone]

[Kafka]: https://www.datadoghq.com/blog/monitoring-kafka-performance-metrics/

## Alerts
Once Datadog is capturing and visualizing your metrics, you will likely want to [set up some alerts][alert] to be automatically notified of potential issues. With our powerful [outlier detection] feature, you can get automatically alerted on strange server behavior. For example, you can set an alert if a particular host is experiencing an increase in latency while the others are operating normally. 

Datadog can monitor individual hosts, containers, [virtual machines][vm], services, processes—or virtually any combination thereof. For instance, you can view all of your Windows hosts, SQL servers, Active Directory controllers, or all hosts in a certain availability zone or resource group, or even a single metric being reported by all hosts with a specific tag.

[alert]: https://docs.datadoghq.com/guides/monitoring/
[outlier detection]: https://www.datadoghq.com/blog/introducing-outlier-detection-in-datadog/
[vm]: https://www.datadoghq.com/blog/how-to-monitor-microsoft-azure-vms/

## Conclusion

In this post we’ve walked you through integrating Windows Server 2012 with Datadog to visualize your [key metrics][part 1] and [notify the right team][alert] whenever your infrastructure shows signs of trouble. 

If you’ve followed along using your own Datadog account, you should now have increased the observability of your environment, as well as the ability to create automated alerts tailored to your infrastructure, your usage patterns, and the metrics that are most valuable to your organization. 

If you don’t yet have a Datadog account, you can <a class="sign-up-trigger" href="#">sign up for a free trial</a> and start to monitor Windows Server 2012 today.


[]: imgs

[agent-restart]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-09-windows-server-2012/3/restart-agent-windows1.gif
[enable-eventlog-int]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-09-windows-server-2012/3/enable_integration.png
[enable-int]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-09-windows-server-2012/3/install-integration.png
[enable-integration-agent]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-09-windows-server-2012/3/enable-integrations-1.gif
[event-prop]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/20https://don08600y3gfm.cloudfront.net16-09-windows-server-2012/3/event-prop.png
[host-reporting]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-02-kafka/default-host.png
[windows-service]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-09-windows-server-2012/3/service-shortname-1.png 
[windows-2012-dash]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-09-windows-server-2012/3/server2012-dash.png
[windows-clone]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-09-windows-server-2012/3/windows-clone.png
[wbem-connect]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-09-windows-server-2012/3/wbem-connect.png
[wbemtest-gif]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-09-windows-server-2012/3/wbemtest.gif
[wbem-prop]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-09-windows-server-2012/3/wbem-prop.png
[wbem-recursive]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-09-windows-server-2012/3/wbem-recursive.png
[wbem-select]: https://don08600y3gfm.cloudfront.net/ps3b/blog/images/2016-09-windows-server-2012/3/wbem-select-class.png

[]: blog

[github-configuration]: https://github.com/vagelim/windows-server-2012
[part 1]: https://datadoghq.com/blog/monitoring-windows-server-2012
[part 2]: https://datadoghq.com/blog/collect-windows-server-2012-metrics
[part 3]: https://datadoghq.com/blog/monitoring-windows-server-2012-datadog