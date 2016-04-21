# OpenStack: host aggregates, flavors, and availability zones

When discussing [OpenStack], correct word choice is essential. OpenStack uses many familiar terms in [unfamiliar ways][semantic-overloading], which can lead to confusing conversations. 

**Host aggregates** (or simply **aggregates**), are commonly confused with the more-familiar term **availability zones**—however the two are not identical. Customers using OpenStack as a service never see host **aggregates**; administrators use them to group hardware according to various properties. Most commonly, host aggregates are used to differentiate between physical host configurations. For example, you can have an aggregate composed of machines with 2GB of RAM and another aggregate composed of machines with 64GB of RAM. This highlights the typical use case of aggregates: defining static hardware profiles. 

Once an aggregate is created, administrators can then define specific public **flavors** from which clients can choose to run their virtual machines (the same concept as EC2 [instance types] on AWS). Flavors are used by customers and clients to choose the type of hardware that will host their instance.

Contrast aggregates with **availability zones** (AZ) in OpenStack, which are customer-facing and usually partitioned geographically. To cement the concept, think of availability zones and flavors as customer-accessible subsets of host aggregates.
[![Host aggregates and availability zones in OpenStack][agg-and-avail]][agg-and-avail]
_As you can see, host aggregates can span across availability zones._

## Host aggregate or availablity zone?
As an OpenStack end user, you don't really have a choice. Only administrators can create host aggregates, so you will be using availability zones and flavors defined by your cloud administrator.

OpenStack admins, on the other hand, should carefully consider the subtle distinction between the two when planning their deployments. Hosts separated geographically should be segregated with availability zones, while hosts sharing the same specs should be grouped with host aggregates.

## Conclusion
You should now have a better sense of the differences between host aggregates, flavors, and availability zones. More information on host aggregates and availability zones is available in the [OpenStack documentation]. Additional terms and definitions can be found in the OpenStack [glossary]. 

Check out our 3-part series about [how to monitor][part 1] and [collect][part 2] OpenStack Nova performance [metrics][part 3]. Also, be sure to take a look at our piece on [How Lithium monitors OpenStack][part 4].


[agg-and-avail]: http://d33tyra1llx9zy.cloudfront.net/blog/images/2015-12-OpenStack/host-aggregates/aggregates1.png
[glossary]: http://docs.openstack.org/glossary/content/glossary.html
[instance types]: https://aws.amazon.com/ec2/instance-types/
[OpenStack]: https://openstack.org
[OpenStack documentation]: http://docs.openstack.org/developer/nova/aggregates.html
[semantic-overloading]: https://en.wikipedia.org/wiki/Semantic_overload

[part 1]: https://www.datadoghq.com/blog/openstack-monitoring-nova
[part 2]: https://www.datadoghq.com/blog/collecting-metrics-notifications-openstack-nova
[part 3]: https://www.datadoghq.com/blog/openstack-monitoring-datadog
[part 4]: https://www.datadoghq.com/blog/how-lithium-monitors-openstack/