# Monitoring Amazon EBS volumes with Datadog


Datadog’s AWS integration lets you connect CloudWatch to Datadog in order to automatically collect metrics from multiple AWS services—including EBS. Datadog’s more than {{< translate key="integration_count" >}} integrations let you correlate AWS metrics with those from other services in your environment. And your data will be accessible for {{< translate key="retention" >}} at full granularity.

For even greater visibility into your Amazon EBS volumes and your entire infrastructure, you can install the Datadog Agent on your instances. This enables you to gather system-level metrics from your volumes, including disk usage, at 15-second resolution. And with [Datadog APM](/blog/announcing-apm/) and the addition of [logging](/blog/announcing-logs/), installing the Datadog Agent provides a fully unified monitoring platform.

## Monitoring Amazon EBS volumes with Datadog

There are two ways to start using Datadog to monitor your EBS volumes. You can [enable the AWS integration](#enable-the-aws-integration) to automatically pull in all metrics outlined in the [first part][part-one] of this series, or you can [install Datadog’s Agent](#deploying-the-agent) on your [EC2 instances](/blog/monitoring-ec2-instances-with-datadog/) to collect detailed metrics from your volumes, applications, and infrastructure.

These approaches can be used in a complementary fashion. The AWS integration allows you to pull the full suite of AWS metrics into Datadog immediately, whereas the Agent allows you to monitor your applications and infrastructure with greater detail and depth.

### Enable the AWS integration

The fastest way to start monitoring EBS metrics in Datadog is to [enable the AWS integration][aws-integration]. This lets Datadog collect metrics from EBS and the rest of the AWS platform via the CloudWatch API without needing to install anything on your instances.

Activating the integration requires correctly [delegating AWS IAM roles][iam-roles] and [giving the Datadog role read-only access][datadog-aws-install]. Once you’ve set up the Datadog role within AWS and connected it to your Datadog account, you will start to see EBS metrics (as well as metrics for EC2 and any other AWS services you are monitoring with Datadog) flowing into Datadog. You can then visualize and monitor them on your dashboards. 

{{< img src="amazon-ebs-volumes-dashboard-rev.png" alt="An Amazon EBS volumes dashboard in Datadog" caption="A dashboard showing Amazon EBS volume metrics in Datadog" wide="true" popup="true" >}}

You can create fully customized dashboards that meet your specific monitoring needs. For instance, you can view your EBS metrics alongside data from EC2 or other AWS services. You can also bring in application performance metrics to correlate throughput, errors, and latency with key resource metrics from the volumes those applications rely on.

### Deploying the Agent

The [Datadog Agent](/blog/dont-fear-the-agent/) is [open source software][dd-agent] that can collect and forward metrics, logs, and request traces from your instances. 

Once the Agent is installed on an instance, it will automatically report system-level metrics for that instance and any EBS volumes that are [mounted to it][ebs-using-volumes]. You can also enable [integrations][integrations] for any supported applications and services that are running on your instances to begin collecting metrics specific to those technologies.

#### Installing the Agent

The Agent is installed on the root volume of an instance. On most platforms this can be done with just a [one-line command][agent-install]. For example, to install the Agent on an instance running Amazon Linux, simply use the following:

```
DD_API_KEY=<user_api_key> bash -c "$(curl -L https://raw.githubusercontent.com/DataDog/dd-agent/master/packaging/datadog-agent/source/install_agent.sh)"
```

You should then see your instance reporting metrics in your [Datadog account][infrastructure]. You can also quickly and easily automate deployment of the Agent across your entire infrastructure with popular configuration management tools like [Chef][chef], [Puppet][puppet], and [Ansible][ansible], or to your container fleet via [Docker][docker] or [Kubernetes][kubernetes]. See the [Datadog Agent documentation][agent-docs] for more information. 

The screenshot below shows a default host dashboard for an EC2 instance with the Agent installed. You can see that both CloudWatch EC2 and EBS metrics are automatically gathered. In addition, Datadog’s system check collects instance- and volume-level metrics that are not automatically available through CloudWatch, such as disk usage.

{{< img src="amazon-ebs-volumes-instance-system-dashboard.png" alt="System dashboard of EC2 instance with Agent including EBS volume metrics" wide="true" popup="true" >}}

Compared to monitoring only the metrics that CloudWatch reports, installing the Agent provides a number of benefits. You can view many of the same disk I/O metrics that are collected by CloudWatch, but the Agent collects them at 15-second intervals, providing much higher resolution. For example, the screenshot below compares the number of read operations reported by the Agent’s system check (top) with that reported by the EBS integration (bottom) for the same volume. 

{{< img src="amazon-ebs-volumes-cloudwatch-vs-system-rev.png" alt="CloudWatch versus system metrics granularity for Amazon EBS volumes" wide="true" popup="true" >}}

Besides the difference in granularity, note that the volume or device name is different. This is because the Agent is reporting from within the instance and will report any mounted volume names as they are identified by the kernel’s block device driver, which may be different than how CloudWatch lists them. In this case, the device name `sdf` reported by CloudWatch is labeled as `xvdf` by the system check. See more information about device naming [here][device-naming]. In Datadog, tags make it easy to see that each device name comes from the same source. Here, both are identified by the same host name.

#### Getting the Agent to work for you

Installing the Agent also enables you to begin tracing requests with Datadog APM after [instrumenting your applications][tracing]. With Datadog Agent versions 6 and later, you can take advantage of [Datadog log management](/blog/announcing-logs/) to collect logs from the applications and technologies running on your EC2 instances and attached volumes. This includes custom log collection as well as logs from Datadog’s integrations with popular technologies like Apache, NGINX, HAProxy, IIS, Java, and MongoDB. With combined aggregation of metrics, distributed request traces, and logs, Datadog provides a unified platform for full visibility into your infrastructure.

If you are running containers on your instances, Datadog's [Live Container view](/blog/introducing-live-container-monitoring/) gives you complete coverage of your fleet, with metrics reported at two-second resolution. And [Live Process monitoring](/blog/live-process-monitoring/) means you have the same level of visibility into all processes running across your entire distributed architecture.


### Slicing and dicing Amazon EBS volumes with tags

All of your monitored EBS volumes will be attached to an EC2 instance as either a root volume or a mounted device. So being able to filter to show the EBS metrics for a particular set of instances can help isolate the source of a problem. [Tags][tagging] enable you to easily slice your hosts and [drill down](/blog/the-power-of-tagged-metrics/) into particular problem areas in your infrastructure.

In addition to any custom tags you add to the instance, Datadog imports all of CloudWatch’s EC2-specific [dimensions](/blog/collecting-ec2-metrics/#dimensions)—such as `InstanceType` and `ImageId`—as default tags. Datadog automatically collects metrics from instances across all regions, so `region` and `availability-zone` are also imported as tags attached to all of your instances, along with other EC2 metadata such as `name`, `security-group`, and, if the instance is part of an ECS group, the ECS cluster name.

### Advanced alerting

Once Datadog is gathering your EBS metrics and events, you can easily set up alerts for any potential issues. Tag-based alerting allows you to monitor large groups of EC2 instances and their attached EBS volumes, without having to update your alerting rules as your infrastructure changes. Tags let you filter or scope your alerts to specific instance groups and automatically monitor new instances that include the tag. For example, you may want to create an alert that monitors disk read operations averaged by device for all EBS volumes attached to instances with a certain role. If disk read levels increase and trigger the alert, you can be notified and take action, like booting up new instances to shoulder the load.

You can also create alerts based on events from AWS. As discussed in [part one](/blog/amazon-ebs-monitoring/#events), it is important to monitor events to head off potential availability or performance issues, or to be notified if you need to migrate important data from a soon-to-be-terminated instance. Datadog can alert your team, for example, if more than a set number of instances in a single availability zone are scheduled for maintenance.

Datadog alerts allow you to move beyond monitoring based on fixed thresholds to effectively identify issues in dynamic environments. With sophisticated alerting features like [anomaly](/blog/introducing-anomaly-detection-datadog/) and [outlier](/blog/introducing-outlier-detection-in-datadog/) detection, Datadog can automatically notify you of unexpected instance behavior. And [forecasting](/blog/forecasts-datadog/) lets you stay ahead of future problems in your infrastructure and applications. For example, you might want to create a forecast alert for a volume's [burst balance](/blog/amazon-ebs-monitoring/#metric-to-alert-on-burst-balance) that will notify you ahead of time if the balance is predicted to cross a certain threshold. This can give you time to investigate if there is some kind of problem, or to scale your volumes up to accomodate a rise in resource demand before you experience any sort of performance throttling from an exhausted burst bucket.

{{< img src="amazon-ebs-volumes-burst-balance-forecast.png" alt="Amazon EBS volumes burst balance forecast" wide="true" >}}

## Getting started

In this post, we’ve walked you through integrating Amazon EC2 and EBS with Datadog so you can visualize and alert on key metrics from all your volumes. Monitoring your instances and any attached EBS volumes with Datadog gives you critical visibility into what’s happening in your core application infrastructure, and the rich suite of Datadog integrations with other applications and services means you can get a complete view of your entire environment.

If you don’t yet have a Datadog account, you can sign up for a <a class="sign-up-trigger" href="#">free 14-day trial</a> and start monitoring your cloud infrastructure, your applications, and your services today.

_Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/aws-ebs/monitoring-amazon-ebs-volumes-with-datadog.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues)._

[part-one]: /blog/amazon-ebs-monitoring/
[aws-integration]: https://docs.datadoghq.com/integrations/aws/
[iam-roles]: http://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#delegate-using-roles
[datadog-aws-install]: https://docs.datadoghq.com/integrations/aws/#installation
[dd-agent]: https://github.com/DataDog/dd-agent
[ebs-using-volumes]: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-using-volumes.html
[integrations]: https://app.datadoghq.com/account/settings
[agent-install]: https://app.datadoghq.com/account/settings#agent
[infrastructure]: https://app.datadoghq.com/infrastructure
[chef]: https://docs.datadoghq.com/integrations/chef/
[puppet]: https://docs.datadoghq.com/integrations/puppet/
[ansible]: https://docs.datadoghq.com/integrations/ansible/
[docker]: https://docs.datadoghq.com/integrations/docker_daemon/
[kubernetes]: https://docs.datadoghq.com/integrations/kubernetes/
[agent-docs]: https://docs.datadoghq.com/agent/
[device-naming]: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/device_naming.html
[tracing]: https://docs.datadoghq.com/tracing/
[datadog-aws-logs]: https://docs.datadoghq.com/integrations/amazon_web_services/#log-collection
[tagging]: https://docs.datadoghq.com/guides/tagging/
