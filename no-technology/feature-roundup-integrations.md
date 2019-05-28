# New feature roundup: Integrations and data collection


*This is the first post in a series about Datadog's latest feature enhancements. This post focuses on new and improved integrations and data collection features. The other installments in the series focus on [alerting enhancements][part-2] and [new features for graphing and collaboration][part-3], respectively.*

Whether your infrastructure is cloud-based, on-prem, serverless, containerized, or all of the above, being able to identify and troubleshoot issues across every layer of your stack is more important than ever before—and also more challenging. As our users' environments have become more diverse and dynamic, Datadog has continually expanded its capabilities to meet the challenges of [monitoring at scale][monitoring-scale-blog].

{{< img src="monitoring-at-scale.png" alt="datadog monitoring" size="1x" >}}

In this series, we will highlight several recent features and enhancements we've developed to help our users gain full observability. This post focuses on our newest integrations and data collection features. Even if you're already a Datadog customer, we hope you'll discover new features that will prove useful for monitoring your infrastructure and applications.

## More coverage, better observability
At Datadog, it's no secret that we believe in [collecting all of the data you can][monitoring-101], and analyzing it to quickly identify and resolve performance issues. With this objective in mind, we are always working to add new integrations to get more data into Datadog, and new features to make it easier to aggregate, analyze, and make decisions based on that data. Three highlights from the past several months:

* [Application performance monitoring](#application-performance-monitoring)
* [New integrations, metrics, and dashboards](#more-metrics-integrations-and-dashboards)
* [Autodiscovery: Monitoring services across containers](#autodiscovery-monitoring-services-across-containers)

### Application performance monitoring
Datadog's [expansion into application performance monitoring][datadog-apm] was arguably our biggest development over the past year. APM is now bundled with the Datadog Agent, so you can easily deploy it across your entire infrastructure with a one-line installation. Like the rest of the Datadog Agent, all of the [source code for our APM][trace-agent-github] instrumentation is open source and completely customizable.

At launch time, Datadog APM supported applications written in Ruby, Python, and Go, and more languages are now being added. APM also includes auto-instrumentation for popular web frameworks like Django, Ruby on Rails, and Gin, as well as data stores like Redis and Elasticsearch. You can also collect custom traces from your applications using our open source client libraries. With APM built into Datadog, you can track application performance and trace requests across service boundaries, then investigate issues by drilling down into the underlying infrastructure. Get the rundown in this two-minute video:

<iframe src="https://player.vimeo.com/video/203196972?title=0&byline=0&portrait=0" width="640" height="360" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>

### More metrics, integrations, and dashboards
In the past year or so, Datadog has added or expanded dozens of integrations to bring more visibility to the tools and services you’re already using. Among our newest integrations:

{{< img src="datadog-new-integrations-logos.jpg" alt="new datadog integrations" >}}

- **AWS**: [Application Load Balancer][aws-alb-docs], [Billing][billing-docs], [CloudFront][cloudfront-docs], [CloudSearch][cloudsearch-docs], [Elastic Block Store][ebs-docs], [Elastic File System][efs-docs], [Elasticsearch Service][aws-es-blog], [Firehose][firehose-docs], [IoT][aws-iot-docs], [Key Management Service][aws-kms], [Lambda][aws-lambda-blog], [Machine Learning][aws-machine-learning], [Polly][aws-polly], [Simple Workflow Service][aws-swf], [Trusted Advisor][trusted-advisor-blog], [Web Application Firewall][aws-waf], and [Workspaces][aws-workspaces]
- **Google Cloud Platform**: [Cloud Spanner][google-spanner], [Datastore][google-datastore], [Firebase][google-firebase], [Functions][google-functions], [Machine Learning][google-ml], [Storage][google-storage], and [VPN][google-vpn]
- **Microsoft Azure**: [App Services][app-services], [Event Hubs][event-hubs], [IoT Hub][iot-hub-docs], [Logic Apps][logic-app], [Redis Cache][redis-cache], [SQL Databases][sql-databases], [SQL Elastic Pool][sql-elastic-pool], [Storage][azure-storage-blog], and [VM Scale Set][vm-scale-set]
- **Hadoop**: [HDFS, MapReduce, YARN, and Spark][spark-blog]
- **Issue tracking tools**: [Bugsnag][bugsnag-docs], [JIRA][jira-blog], [Rollbar][rollbar-blog], [Zendesk][zendesk-blog]
- **Platforms and management tools**: [Ceph][ceph-blog], [CloudCheckr][cloudcheckr-blog], [Cloud Foundry][cf-blog], [CloudHealth][cloudhealth-blog], [Kong][kong-blog], [Lightbend][lightbend-blog], [Pusher][pusher-blog], and [Terraform by HashiCorp][terraform-blog]
- **Other monitoring tools**: [Catchpoint][catchpoint-docs], [IMMUNIO][immunio-blog], and [xMatters][xmatters]
- **DNS:** [DNS Service Check][dns-service-check] and [PowerDNS Recursor][powerdns-docs]

We also enhanced many of our existing integrations by adding new metrics and/or improved out-of-the-box dashboards.

{{< img src="elasticsearch-dashboard-final2.png" alt="elasticsearch dashboard in datadog" popup="true" caption="Datadog's new out-of-the-box dashboard for Elasticsearch monitoring" size="1x" >}}

We now support more than [{{< translate key="integration_count" >}} infrastructure technologies][datadog-integrations]. If you'd like to learn more about how to contribute new integrations or enhance existing ones, please consult our [contribution guide][dd-agent-contribution].

### Autodiscovery: Monitoring services across containers
According to our [latest Docker report][docker-report], containers churn nine times more quickly than VMs, with an average lifespan of only 2.5 days. With containers constantly starting, stopping, and shifting across hosts, it becomes increasingly difficult to keep track of where your services are running at any given moment.

{{< img src="datadog-docker-container-churn.png" alt="Datadog Docker report container churn" >}}

Datadog's [Autodiscovery][autodiscovery-blog] feature makes it much easier to automatically collect and aggregate data from your containerized services and track containers' lifecycle events. Autodiscovery can continuously detect and monitor which services are running where, enabling you to seamlessly track application performance on ephemeral containers. You can even use configuration variables like `%%host%%` and `%%port%%` to dynamically apply your monitoring across changing infrastructure.

{{< canvas-animation name="service_discovery" width="" height="" >}}

If you're using Docker and haven't yet enabled Autodiscovery, read [our guide][autodiscovery-guide] to get started.

## Metrics -> Alerts!
In this post, we highlighted a few ways in which we've helped our users collect more metrics from their infrastructure and applications. If you're already a customer, you can start using these new features right away. Otherwise, get started with a <a href="#" class="sign-up-trigger">free trial</a>.

Once you've collected all of the data you need to monitor, alerts will help you automatically detect if those metrics approach problematic thresholds or reflect abnormal patterns. In the [next article][part-2] in this series, we'll explore some of the enhancements we made to alerting and algorithmic monitoring.


[iot-hub-docs]: http://docs.datadoghq.com/integrations/azure_iot_hub/
[sql-elastic-pool]: http://docs.datadoghq.com/integrations/azure_sql_elastic_pool/
[vm-scale-set]: http://docs.datadoghq.com/integrations/azure_vm_scale_set/
[ebs-docs]: http://docs.datadoghq.com/integrations/awsebs/
[cloudsearch-docs]: http://docs.datadoghq.com/integrations/awscloudsearch/
[trusted-advisor-blog]: /blog/monitor-aws-trusted-advisor/
[ecs-blog]: /blog/monitor-docker-on-aws-ecs/
[catchpoint-docs]: http://docs.datadoghq.com/integrations/catchpoint/
[bugsnag-docs]: http://docs.datadoghq.com/integrations/bugsnag/
[zendesk-blog]: /blog/zendesk-integration/
[aws-alb-docs]: https://help.datadoghq.com/hc/en-us/articles/213132066-Does-Datadog-support-AWS-ALB-Application-Load-Balancer-
[cloudhealth-blog]: /blog/monitor-cloudhealth-assets-datadog/
[aws-es-blog]: /blog/monitor-amazon-elasticsearch-service/
[powerdns-docs]: http://docs.datadoghq.com/integrations/powerdns/
[azure-vm-blog]: /blog/monitor-azure-vms-using-datadog/
[mysql-blog]: /blog/mysql-monitoring-with-datadog/
[dns-service-check]: http://docs.datadoghq.com/integrations/dnscheck/
[route-53-docs]: http://docs.datadoghq.com/integrations/awsroute53/
[cloudfront-docs]: http://docs.datadoghq.com/integrations/awscloudfront/
[billing-docs]: http://docs.datadoghq.com/integrations/awsbilling/
[sns-blog]: /blog/monitor-aws-sns-datadog/
[elasticache-blog]: /blog/monitor-elasticache-with-aws-metrics-native-metrics/
[dynamodb-blog]: /blog/top-dynamodb-performance-metrics/
[ec2-docs]: http://docs.datadoghq.com/integrations/awsec2/
[gcp-pubsub]: http://docs.datadoghq.com/integrations/google_cloud_pubsub/
[gcp-sql]: http://docs.datadoghq.com/integrations/google_cloudsql/
[gce]: /blog/monitor-google-compute-engine-with-datadog/
[gke]: http://docs.datadoghq.com/integrations/google_container_engine/
[rds-blog]: /blog/monitor-rds-mysql-using-datadog/
[elb-blog]: /blog/monitor-elb-performance-with-datadog/
[kubernetes-blog]: /blog/monitoring-kubernetes-with-datadog/
[mongodb-blog]: /blog/monitor-mongodb-performance-with-datadog/
[elasticsearch-blog]: /blog/monitor-elasticsearch-datadog/
[windows-blog]: /blog/monitoring-windows-server-2012-datadog/
[autodiscovery-guide]: http://docs.datadoghq.com/guides/autodiscovery/
[autodiscovery-blog]: /blog/autodiscovery-docker-monitoring/
[aws-redshift-blog]: /blog/monitor-aws-redshift-with-datadog/
[aws-lambda-blog]: /blog/monitoring-lambda-functions-datadog/
[monitoring-101]: /blog/monitoring-101-collecting-data/
[jira-blog]: /blog/jira-issue-tracking/
[immunio-blog]: /blog/datadog-immunio-app-security-monitoring/
[app-services]: /blog/monitor-azure-app-service-applications-datadog/
[sql-databases]: /blog/monitor-azure-sql-databases-datadog/
[event-hubs]: /blog/monitor-your-azure-event-hubs-with-datadog/
[logic-app]: /blog/monitor-azure-logic-app-workflows-datadog/
[redis-cache]: /blog/monitor-azure-redis-cache-datadog/
[rollbar-blog]: /blog/error-monitoring-rollbar/
[ceph-blog]: /blog/monitor-ceph-datadog/
[kong-blog]: /blog/monitor-kong-datadog/
[spark-blog]: /blog/hadoop-spark-monitoring-datadog/
[jenkins-blog]: /blog/monitor-jenkins-datadog/
[efs-docs]: http://docs.datadoghq.com/integrations/awsefs/
[docker-blog]: /blog/monitor-docker-datadog/
[firehose-docs]: http://docs.datadoghq.com/integrations/awsfirehose/
[aws-iot-docs]: http://docs.datadoghq.com/integrations/awsiot/
[aws-kms]: http://docs.datadoghq.com/integrations/awskms/
[aws-machine-learning]: http://docs.datadoghq.com/integrations/awsml/
[aws-polly]: http://docs.datadoghq.com/integrations/awspolly/
[aws-swf]: http://docs.datadoghq.com/integrations/awsswf/
[aws-waf]: http://docs.datadoghq.com/integrations/awswaf/
[aws-workspaces]: http://docs.datadoghq.com/integrations/awsworkspaces/
[google-datastore]: http://docs.datadoghq.com/integrations/google_cloud_datastore/
[google-firebase]: http://docs.datadoghq.com/integrations/google_cloud_firebase/
[google-functions]: http://docs.datadoghq.com/integrations/google_cloud_functions/
[google-ml]: http://docs.datadoghq.com/integrations/google_cloud_ml/
[google-spanner]: http://docs.datadoghq.com/integrations/google_cloud_spanner/
[google-storage]: http://docs.datadoghq.com/integrations/google_cloud_storage/
[google-vpn]: http://docs.datadoghq.com/integrations/google_cloud_vpn/
[datadog-apm]: /blog/announcing-apm/
[part-2]: /blog/feature-roundup-alerting
[part-3]: /blog/feature-roundup-visualization-collaboration
[pusher-blog]: /blog/pusher-monitoring/
[cloudcheckr-blog]: /blog/rightsizing-cloudcheckr/
[lightbend-blog]: /blog/monitor-lightbend/
[datadog-integrations]: /product/integrations/
[dd-agent-contribution]: https://github.com/DataDog/dd-agent/blob/master/CONTRIBUTING.md
[datadog-apm]: /blog/announcing-apm/
[trace-agent-github]: https://github.com/DataDog/datadog-trace-agent
[monitoring-scale-blog]: /blog/2016-monitoring-at-scale/
[cloudcheckr-blog]: /blog/rightsizing-cloudcheckr/
[s3-docs]: http://docs.datadoghq.com/integrations/awss3/
[xmatters]: http://help.xmatters.com/integrations/monitoring/datadog.htm
[terraform-blog]: /blog/managing-datadog-with-terraform/
[docker-report]: /docker-adoption/
[cf-blog]: /blog/monitor-cloud-foundry/
[azure-storage-blog]: /blog/monitor-azure-storage-datadog/
