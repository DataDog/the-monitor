# How to monitor Google Compute Engine with Datadog


_This post is the final part of a 3-part series on how to monitor Google Compute Engine. [Part 1][part1] explores the key metrics available from GCE, and [part 2][part2] is about collecting those metrics using Google-native tools._

To have a clear picture of GCE's operations, you need a system dedicated to storing, visualizing, and correlating your Google Compute Engine metrics with metrics from the rest of your infrastructure. If you’ve read [our post][part2] on collecting GCE metrics, you've seen how you can quickly and easily pull metrics using the Stackdriver Monitoring API and gcloud, and had a chance to see Google's monitoring service, Stackdriver, in action.

Though these solutions are excellent starting points, they have their limitations, especially when it comes to integration with varied infrastructure components and platforms, as well as data retention for long-term monitoring and trend analysis.

{{< img src="gce-dashboard1.png" alt="Datadog's out-of-the-box, customizable Google Compute Engine dashboard" popup="true" >}}

Datadog enables you to collect metrics from many Google Cloud platform services, including GCE, for visualization, alerting, and full-infrastructure correlation. Datadog will automatically collect the key performance metrics discussed in [parts one][part1] and [two][part2] of this series, and make them available in a customizable dashboard, as seen above. Datadog retains your data for {{< translate key="retention" >}} at full granularity, so you can easily compare real-time metrics against values from last month, last quarter, or last year. And if you [install the Datadog Agent](#install-the-agent), you gain additional system resource metrics (including memory usage, disk I/O, and more) and benefit from integrations with more than {{< translate key="integration_count" >}} technologies and services.

You can integrate Datadog with GCE in two ways:

- [Enable the Google Cloud Platform integration](#enable-integration) to collect all of the metrics from the first part of this series
- [Install the Agent](#install-the-agent) to collect all system metrics, including those not available from Google's monitoring APIs


### Enable the Google Cloud Platform integration
Enabling the [Google Cloud Platform integration][gcp-tile] is the quickest way to start monitoring your GCE instances and the rest of your GCP resources, including Google App Engine applications and Google Container Engine (GKE) containers. And since Datadog supports OAuth login with your GCP account, you can start seeing your GCE metrics in just a few clicks.

{{< img src="gcp-oauth-login.png" alt="Integrating GCP with Datadog is as easy as signing into your Google account." popup="true" >}}

Once signed in, add the [id of the project][project-id] you want to monitor, optionally restrict the set of hosts to monitor, and click _Update Configuration_.

After a couple of minutes you should see metrics streaming into the customizable [Google Compute Engine][gce-dash-link] dashboard. And if you're using other Google services, like [Google App Engine][gae] or [Google Pub/Sub][gpub], you'll automatically have access to built-in dashboards for those services, too.

[gae]: https://app.datadoghq.com/screen/integration/gae_base_screenboard
[gpub]: https://app.datadoghq.com/screen/integration/gcp_pub_sub_screen

[gce-dash-link]: https://app.datadoghq.com/screen/integration/gce
[gcp-tile]: https://app.datadoghq.com/account/settings#integrations/google_cloud_platform
[project-id]: https://console.cloud.google.com/project

### Install the Agent

The Datadog Agent is [open source software](https://github.com/DataDog/dd-agent) that collects and reports metrics from your hosts so that you can view and monitor them in Datadog. Installing the Agent usually takes just a single command.

Installation instructions for a variety of platforms are available [here](https://app.datadoghq.com/account/settings#agent).

As soon as the Agent is up and running, you should see your host reporting metrics in your [Datadog account](https://app.datadoghq.com/infrastructure).

{{< img src="host1.png" alt="Hosts reporting in." popup="true" >}}

No additional configuration is necessary, but if you want to collect more than just host metrics, head over to the [integrations page](https://app.datadoghq.com/account/settings) to enable monitoring for over {{< translate key="integration_count" >}} applications and services.

### Monitoring GCE with Datadog dashboards

The template GCE dashboard in Datadog is a great resource, but you can easily create a more comprehensive dashboard to monitor your entire application stack by adding graphs and metrics from your other systems. For example, you might want to graph GCE metrics alongside metrics from [Kubernetes](https://www.datadoghq.com/blog/monitoring-kubernetes-era/) or [Docker](https://www.datadoghq.com/blog/the-docker-monitoring-problem/), [performance metrics](https://www.datadoghq.com/blog/announcing-apm/) from your applications, or host-level metrics such as memory usage on application servers. To start extending the template dashboard, clone the default GCE dashboard by clicking on the gear on the upper right of the dashboard and selecting _Clone Dashboard_.

{{< img src="clone-dash.png" alt="Customize the out-of-the-box dashboard by making a clone." popup="true" >}}

### Drilling down with tags
All Google Compute Engine metrics are [tagged](https://docs.datadoghq.com/tagging/) with the following information:

- `availability-zone`
- `cloud_provider`
- `instance-type`
- `instance-id`
- `automatic-restart`
- `on-host-maintenace`
- `numeric_project_id`
- `name`
- `project`
- `zone`
- any additional labels and tags you added in GCP

{{< img src="template-vars.png" alt="Use template variables to slice and dice with tags." popup="true" >}}

You can easily [slice your metrics](https://www.datadoghq.com/blog/the-power-of-tagged-metrics/) to isolate a particular subset of hosts using tags. In the out-of-the-box GCE screenboard, you can use the template variable selectors in the upper left to drill down to a specific host or set of hosts. And you can similarly use tags in any Datadog graph or alert definition to filter or aggregate your metrics.

### Alerts

Once Datadog is capturing and visualizing your metrics, you will likely want to [set up some alerts](https://docs.datadoghq.com/monitors/) to be automatically notified of potential issues. With powerful algorithmic alerting features like [outlier](https://www.datadoghq.com/blog/introducing-outlier-detection-in-datadog/) [detection](https://www.datadoghq.com/blog/scaling-outlier-algorithms/) and [anomaly detection](https://www.datadoghq.com/blog/introducing-anomaly-detection-datadog/), you can be automatically alerted to unexpected instance behavior.


### Observability awaits
We’ve now walked through how to use Datadog to collect, visualize, and alert on your Google Compute Engine metrics. If you’ve followed along with your Datadog account, you should now have greater visibility into the state of your instances.

If you don’t yet have a Datadog account, you can start monitoring Google Compute Engine right away with a <a href="#" class="sign-up-trigger">free trial</a>.


_Source Markdown for this post is available [on GitHub][the-monitor]. Questions, corrections, additions, etc.? Please [let us know][issues]._

[the-monitor]: https://github.com/datadog/the-monitor

[part1]: /blog/monitoring-google-compute-engine-performance
[part2]: /blog/how-to-collect-gce-metrics
[part3]: /blog/monitor-google-compute-engine-with-datadog

[issues]: https://github.com/DataDog/the-monitor/issues
