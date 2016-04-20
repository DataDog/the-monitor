# How Lithium monitors OpenStack

[Lithium] was founded in 2001 as an offshoot from gamers.com (a gaming community) and has since evolved into a leading social software provider whose Total Community platform helps brands connect, engage and understand their customers. With more than [400 communities][communities] and growing, Lithium uses [OpenStack] as a private datacenter, with flexibility to deploy customized, public-facing communities to major brands across industries and regions.

In this article we will pull back the curtain to learn Lithium's best practices and tips for using OpenStack, and how Lithium monitors OpenStack with the help of Datadog.

## Why monitoring OpenStack is critical

[OpenStack] is a central component in Lithium's infrastructure, forming the backbone of their service platform. Lithium leverages OpenStack for both production and development environments, with OpenStack hosting a large number of production communities, as well as demo communities for sales engineers.  
In addition to community hosting, OpenStack also hosts infrastructure services, including [Kubernetes], [Chef] servers and [BIND] slaves. 

With such a far-reaching deployment, failure is not an option. If OpenStack were not properly monitored and managed, numerous and noticeable failures can occur: sales engineers wouldn't be able to create demo environments for prospects, developers wouldn't be able to spawn test environments, and the communities in production could go down or see increased response times as computing resources became unavailable. 

That's why Lithium's engineers monitor OpenStack around the clock. Using [Datadog], they can correlate all the relevant OpenStack metrics with metrics from other parts of their infrastructure, all in one place. Lithium engineers can spot issues at a glance and determine the root cause of the problem, in addition to setting up advanced alerts on mission-critical metrics.

[![Lithium OpenStack dashboard][lithium-dash]][lithium-dash]
_A Datadog dashboard that Lithium uses to monitor OpenStack_

## Key metrics for Lithium

### Number of instances running
Lithium engineers track the total number of instances running across their OpenStack deployment to correlate with changes in other metrics. For example, a large increase in total RAM used makes sense in light of additional instances being spun up. Tracking the number of instances running alongside other metrics helps inform decisions for capacity and [tenant quota][quotas] planning.
 
### Instances per project
Like the total number of instances running, Lithium tracks the number of instances used per project to get a better idea of how their private cloud is being used. A common problem they found was that engineers would often spin up development environments and forget to shut them down, which means resources were provisioned but unused. By tracking the number of instances per project, admins could rein in excessive or unnecessary usage and free up resources without resorting to installing additional hardware.

### Available memory
As mentioned in [Part 1][part 1] of our [series][part 2] on [monitoring OpenStack Nova][part 3], visibility into OpenStack's resource consumption is essential to ensuring smooth operation and preventing user frustration. If available resources were insufficient, sales engineers would be breathing down the neck of the techops team, unable to create demo accounts for prospects, and developers would be stuck without a dev environment.

### VCPU available
Just like available memory, tracking the number of VCPUs available for allocation is critical—a lack of available CPUs prevents provisioning of additional instances. 

### Metric deltas
[![Change in instances used][instance-change-graph]][instance-change-graph]

Finally, Lithium tracks the changes in metrics' values over time to give insight into the causes of changes in resource availability and consumption. 

Using Datadog's [Change graph feature][graph-change], engineers have a bird's eye view of week-to-week changes in resource usage. By analyzing resource deltas, engineers and decision makers have the data they need to inform hardware purchasing decisions and perform diligent capacity planning.

## Alerting the right people
Alerting is an [essential component][alerting-101] of any monitoring strategy—alerts let engineers react to issues as they occur, before users are affected. With Datadog alerts, Lithium is able to send notifications via their usual communication channels (chat, PagerDuty, email, etc.), as well as provide engineers with suggested fixes or troubleshooting techniques—all without human intervention.

Lithium generally uses [PagerDuty] for priority alerts, and [HipChat] or email for lower-priority alerts and for alerting specific engineers to a particular issue. For OpenStack, Lithium alerts on excessive resource consumption. As mentioned in [Part 1][part 1] of our OpenStack series, monitoring resource consumption is a **critical** part of a comprehensive OpenStack monitoring strategy.

[![Lithium alerts][lithium-alert]][lithium-alert]

Datadog alerts give Lithium engineers the flexibility to inform the right people that a problem has occurred, at the right time, across an [ever-growing][integration-list] list of platforms. 

## Why Datadog?
Before adopting Datadog, Lithium admins were relying on [Horizon][Horizon] (OpenStack's canonical dashboard) to extract meaningful metrics from their deployment. This approach was severely limited—engineers could only access rudimentary statistics about their deployment and lacked the ability to correlate metrics from OpenStack with metrics from across their infrastructure.

With Datadog [screenboards], they can combine the historical perspective of graphed timeseries data with alert values to put current operations metrics in context. 

[![Lithium widgets][lithium-widgets]][lithium-widgets]

Datadog also makes it easy to collect and monitor [RabbitMQ] and MySQL metrics, in addition to general OpenStack metrics, for even deeper insight into performance issues. For Lithium, having Datadog in place has allowed engineers to adjust internal workflows, reducing the total number of elements that need monitoring.

### Saving time, money, and reputation
Adopting Datadog has allowed Lithium to catch problems in OpenStack as well as applications running on their OpenStack cloud. Now, Lithium engineers have the tools and information they need to react quickly to problems and resolve infrastructure issues with minimal customer impact, saving time, money, and reputation.

## Conclusion
[![Nova default dash][nova-dash]][nova-dash]
_Default Datadog OpenStack dashboard_

If you're already using OpenStack and Datadog, we hope these strategies will help you gain improved visibility into what's happening in your deployment. If you don't yet have a Datadog account, you can [start monitoring][part 3] OpenStack performance today with a [free trial].

## Acknowledgments

Thanks to [Lithium] and especially [Mike Tougeron][twit], Lead Cloud Platform Engineer, for generously sharing their OpenStack expertise and monitoring strategies for this article.

<iframe width="100%" height="100" style="border: 0;" src="https://go.pardot.com/l/38172/2015-03-02/h6c2r" scrolling="no" type="text/html" frameborder="0" allowtransparency="true"></iframe>

[alerting-101]: https://www.datadoghq.com/blog/monitoring-101-alerting/
[BIND]: https://www.isc.org/downloads/bind/
[Chef]: https://www.chef.io/chef/
[communities]: http://www.lithium.com/why-lithium/customer-success/
[Datadog]: https://datadoghq.com
[graph-change]: http://docs.datadoghq.com/graphing/#select-your-visualization
[HipChat]: https://www.hipchat.com/
[Horizon]: http://docs.openstack.org/developer/horizon/
[instance-change-graph]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-OpenStack/lithium/instances-change-graph.png
[integration-list]: http://docs.datadoghq.com/integrations/
[Kubernetes]: https://www.datadoghq.com/blog/corral-your-docker-containers-with-kubernetes-monitoring/
[Lithium]: http://www.lithium.com
[lithium-alert]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-OpenStack/lithium/lithium-alert.png
[lithium-dash]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-OpenStack/lithium/lithium-dashboard.png
[lithium-widgets]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-OpenStack/lithium/lithium-widgets.png
[OpenStack]: https://www.openstack.org
[PagerDuty]: https://www.pagerduty.com/
[quotas]: http://docs.openstack.org/user-guide-admin/dashboard_set_quotas.html
[nova-dash]: https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-OpenStack/default-dash.png
[RabbitMQ]: https://www.datadoghq.com/blog/openstack-monitoring-nova/#rabbitmq-metrics
[screenboards]: http://help.datadoghq.com/hc/en-us/articles/204580349-What-is-the-difference-between-a-ScreenBoard-and-a-TimeBoard-
[twit]: https://twitter.com/mtougeron

[free trial]: https://app.datadoghq.com/signup
[part 1]: https://www.datadoghq.com/blog/openstack-monitoring-nova/
[part 2]: https://www.datadoghq.com/blog/collecting-metrics-notifications-openstack-nova/
[part 3]: https://www.datadoghq.com/blog/openstack-monitoring-datadog/