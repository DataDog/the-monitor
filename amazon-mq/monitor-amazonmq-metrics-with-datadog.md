---
authors:
- email: maxim.brown@datadoghq.com
  image: brown-maxim.jpg
  name: Maxim Brown
blog/category:
- integration
blog/tag:
- aws
- amazon mq
- activemq
Date: 2019-02-22
description: Monitor your Amazon MQ brokers and destinations with Datadog.
draft: false
image: amazonmq-hero.png
preview_image: amazonmq-hero.png
slug: monitor-amazonmq-metrics-with-datadog
technology: AmazonMQ
title: Monitor Amazon MQ metrics with&nbsp;Datadog
tcp:
- title: "eBook: Monitoring Modern Infrastructure"
  desc: "Explore key steps for implementing a successful cloud-scale monitoring strategy."
  cta: "Download to learn more"
  link: "https://www.datadoghq.com/ebook/monitoring-modern-infrastructure/?utm_source=Content&utm_medium=eBook&utm_campaign=BlogCTA-MonitoringModernInfrastructure"
  img: Thumbnail-MonitoringModernInfrastructure.png
---

[Amazon MQ][amazon-mq] is a cloud-based, AWS-managed service for the popular [Apache ActiveMQ](/blog/activemq-architecture-and-metrics) message broker. It offers many advantages of being part of the AWS ecosystem as AWS automatically provisions and maintains infrastructure components from services including EC2 and EBS.

Datadog's Amazon MQ integration gives you visibility into key metrics from your messaging infrastructure, allowing you to ensure that your brokers are sending and receiving messages properly.

{{< img src="amazonmq-dashboard.png" alt="Datadog's Amazon MQ dashboard" popup="true" wide="true" caption="Datadog's out-of-the-box Amazon MQ dashboard." >}}

## How Amazon MQ works

Amazon MQ creates and manages brokers that route messages from producers to the appropriate consumers through one of two types of message destination:

- queues, which deliver messages directly to a single consumer
- topics, which deliver messages to any consumers that subscribe to that topic

Amazon MQ makes it easy to migrate an existing application to the cloud by supporting many existing APIs and message protocols like [JMS][jms], [AMQP][amqp], [MQTT][mqtt], [OpenWire][openwire], [STOMP][stomp], and [WebSocket][websocket]. Amazon MQ supports many different broker configurations, from [single-instance][single-instance] to complex topologies like [hub-and-spoke][hub-and-spoke] and [concentrator][concentrator]. You can configure your brokers individually or launch full networks using [AWS CloudFormation][cloudformation] templates.

For networks with multiple brokers, Amazon MQ provides high availability by automatically launching instances in other availability zones. Security features include security groups to control outside access to your broker network, API authorization through [IAM][iam], and automatic at-rest and in-transit message encryption.

## Key Amazon MQ metrics

Datadog's Amazon MQ integration automatically pulls in metrics from your brokers and message destinations to help you track your entire messaging infrastructure in one place. Broker resource usage metrics provide insight into broker performance and capacity while message destination metrics help track message throughput.

Amazon MQ brokers can be launched using several different [EC2 instance types][instance-types], which are appropriate for different use cases. Tracking broker instance resource metrics, such as CPU utilization, network throughput, and heap memory usage, provides insight into whether your broker fleet is properly scaled and made up of the most appropriate instance type.

{{< img src="amazonmq-resource-metrics.png" alt="Amazon MQ resource metric graphs" >}}

Tracking destination metrics, such as the number of messages sent to and received by your queues and topics, as well as the number of expired messages, can help you understand if your messaging infrastructure is configured properly and able to handle its workload. For example, an increasing disparity between the number of messages sent and messages received by destinations might indicate that your producer throughput is overwhelming the consumers and so more consumers are needed.

Monitoring a combination of Amazon MQ broker resource and message throughput metrics can help ensure that your existing brokers have enough resources to handle the volume of messages for your use case.

## Start monitoring your Amazon MQ messages with Datadog
Datadog's Amazon MQ integration lets you easily monitor and alert on your message broker and destination metrics. If you're already monitoring other AWS services with Datadog's main [AWS integration][aws-integration], simply make sure that "MQ" is selected in the AWS integration tile to start collecting metrics from your Amazon MQ brokers and destinations along with the rest of your [AWS infrastructure](/blog/aws-monitoring). If you don't already have a Datadog account, sign up for a free <a href="#" class="sign-up-trigger">14-day trial</a>.

[amazon-mq]: https://aws.amazon.com/amazon-mq/
[jms]: https://javaee.github.io/javaee-spec/javadocs/javax/jms/package-summary.html
[amqp]: https://www.amqp.org/
[mqtt]: http://mqtt.org/
[openwire]: http://activemq.apache.org/openwire.html
[stomp]: https://stomp.github.io/
[websocket]: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API
[single-instance]: https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/single-broker-deployment.html
[hub-and-spoke]: https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/network-of-brokers.html#nob-topologies-hub
[concentrator]: https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/network-of-brokers.html#nob-topologies-concentrator
[cloudformation]: https://aws.amazon.com/cloudformation/
[instance-types]: https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/broker.html#broker-instance-types
[aws-integration]: https://docs.datadoghq.com/integrations/amazon_web_services/
[vpc]: https://aws.amazon.com/vpc/
[iam]: https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/amazon-mq-api-authentication-authorization.html