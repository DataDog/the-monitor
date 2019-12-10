---
authors:
- email: paul.gottschling@datadoghq.com
  image: paulgottschling.jpg
  name: Paul Gottschling
blog/category:
- series metrics
blog/tag:
- rabbitmq
- alerts
- amqp
- message broker
- performance
date: 2018-01-24T00:00:02Z
description: With RabbitMQ monitoring, see how your messaging setup affects your system and holds up to demand.
draft: false
image: 160509_RabbitMQ-01.png
preview_image: 160509_RabbitMQ-01.png
slug: rabbitmq-monitoring
technology: rabbitmq
title: Key metrics for RabbitMQ monitoring
series: rabbitmq-monitoring
---
## What is RabbitMQ?
RabbitMQ is a message broker, a tool for implementing a messaging architecture. Some parts of your application publish messages, others consume them, and RabbitMQ routes them between producers and consumers. The broker is well suited for loosely coupled microservices. If no service or part of the application can handle a given message, RabbitMQ keeps the message in a queue until it can be delivered. RabbitMQ leaves it to your application to define the details of routing and queuing, which depend on the relationships of objects in the broker: exchanges, queues, and bindings.

If your application is built around RabbitMQ messaging, then comprehensive monitoring requires gaining visibility into the broker itself. RabbitMQ exposes metrics for all of its main components, giving you insight into your message traffic and how it affects the rest of your system.

{{< img alt="Out-of-the-box screenboard for RabbitMQ monitoring" src="rabbitmq-monitoring-screenboard.png" popup="true" wide="true" >}}

## How RabbitMQ works
RabbitMQ runs as an [Erlang runtime][erlang-nodes], called a **node**. A RabbitMQ server can include [one or more][clustering] nodes, and a cluster of nodes can operate across one machine or several. Connections to RabbitMQ take place through TCP, making RabbitMQ suitable for a [distributed setup][distributed]. While RabbitMQ supports a number of protocols, it [implements AMQP][amqp-concepts] (Advanced Message Queuing Protocol) and [extends][amqp-extensions] some of its concepts.

At the heart of RabbitMQ is the **message**. Messages feature a set of headers and a binary payload. Any sort of data can make up a message. It is up to your application to parse the headers and use this information to interpret the payload.

The parts of your application that join up with the RabbitMQ server are called producers and consumers. A **producer** is anything that publishes a message, which RabbitMQ then routes to another part of your application: the **consumer**. RabbitMQ clients are available in a [range of languages][tutorials], letting you implement messaging in most applications.

RabbitMQ passes messages through abstractions within the server called exchanges and queues. When your application publishes a message, it publishes to an **exchange**. An exchange routes a message to a **queue**. Queues wait for a consumer to be available, then deliver the message.

You'll notice that a message going from a producer to a consumer moves through two intermediary points, an exchange and a queue. This separation lets you specify the logic of routing messages. There can be multiple exchanges per queue, multiple queues per exchange, or a one-to-one mapping of queues and exchanges. Which queue an exchange delivers to depends on [the type of the exchange][exchange-types]. While RabbitMQ defines the basic behaviors of topics and exchanges, how they relate is up to the needs of your application.

There are many possible design patterns. You might use [work queues][work-queues], a [publish/subscribe][pub-sub] pattern, or a [Remote Procedure Call][rpc] (as seen in [OpenStack Nova][nova]), just to name examples from the official tutorial. The design of your RabbitMQ setup depends on how you configure its application objects (nodes, queues, exchanges...). RabbitMQ exposes metrics for each of these, letting you measure message traffic, resource use, and more.

{{< img src="rabbitmq-monitoring-layout-diagram.png" alt="RabbitMQ monitoring - a diagram of RabbitMQ's core elements" popup="true" wide="true" >}}

## Key RabbitMQ metrics
With so many moving parts within the RabbitMQ server, and so much room for configuration, you'll want to make sure your messaging setup is working as efficiently as possible. As we've seen, RabbitMQ has a whole cast of abstractions, and each has its own metrics. These include:

- [Exchange metrics](#exchange-performance)
- [Node metrics](#nodes)
- [Connection metrics](#connection-performance)
- [Queue metrics](#queue-performance)

This post, the first in the series, is a tour through these metrics. In some cases, the metrics have to do with RabbitMQ-specific abstractions, such as queues and exchanges. Other components of a RabbitMQ application demand attention to the same metrics that you'd monitor in the rest of your infrastructure, such as storage and memory resources.

You can gather RabbitMQ metrics through a set of plugins and built-in tools. One is `rabbitmqctl`, a RabbitMQ command line interface that lists queues, exchanges, and so on, along with various metrics. Another is a management plugin that reports metrics from a local web server. Several tools report events. We'll tell you how to use these tools in [Part 2][part2].

### Exchange performance
Exchanges tell your messages where to go. Monitoring exchanges lets you see whether messages are being routed as expected.

Name  | Description  | [Metric type][monitor-101] | Availability
:--|:---|:--|:--|
Messages published in| Messages published to an exchange (as a count and a rate per second) | Work: Throughput | management plugin
Messages published out | Messages that have left an exchange (as a count and a rate per second)| Work: Throughput | management plugin
Messages unroutable | Count of messages not routed to a queue | Work: Errors | management plugin

#### Metrics to watch: Messages published in, Messages published out
When RabbitMQ performs work, it performs work with messages: routing, queuing, and delivering them. Counts and rates of deliveries are available as metrics, including the number of messages that have entered the exchange and the number of messages that have left. Both metrics are available as rates (see the discussion of the management plugin in [Part 2][part2]). These are key indicators of throughput.

#### Metric to alert on: Messages unroutable
In RabbitMQ, you specify how a message will move from an exchange to a queue by defining [bindings][bindings]. If a message falls outside the rules of your bindings, it is considered unroutable. In some cases, such as a [Publish/Subscribe][pub-sub] pattern, it may not be important for consumers to receive every message. In others, you may want to keep missed messages to a minimum. RabbitMQ's [implementation][rabbit-amqp] of AMQP includes a way to detect unroutable messages, sending them to a dedicated (['Alternative'][alt-exchange]) exchange. In the management plugin (see [Part 2][part2]), use the `return_unroutable` metric, constraining the count to a given time interval. If some messages have not been routed properly, the rate of publications into an exchange will also exceed the rate of publications out of the exchange, suggesting that some messages have been lost.

### Nodes
RabbitMQ runs inside an Erlang runtime system called a [node][distrib-erlang]. For this reason the node is the primary reference point for observing the resource use of your RabbitMQ setup. 

When use of certain resources reaches a threshold, RabbitMQ [triggers an alarm][alarms] and blocks connections. These connections [appear][alarms] as `blocking` in built-in monitoring tools, but it is left to the user to set up notifications (see [Part 2][part2]). For this reason, monitoring resource use across your RabbitMQ system is necessary for ensuring availability.

Name  | Description  | [Metric type][monitor-101] | Availability
:--|:---|:--|:--|
| File descriptors used | Count of file descriptors used by RabbitMQ processes | Resource: Utilization | management plugin, `rabbitmqctl` |
| File descriptors used as sockets | Count of file descriptors used as network sockets by RabbitMQ processes | Resource: Utilization | management plugin, `rabbitmqctl` |
| Disk space used | Bytes of disk used by a RabbitMQ node | Resource: Utilization | management plugin, `rabbitmqctl` |
| Memory used | Bytes in RAM used by a RabbitMQ node (categorized by use) | Resource: Utilization | management plugin, `rabbitmqctl` |

#### Metrics to alert on: File descriptors used, file descriptors used as sockets
As you increase the number of connections to your RabbitMQ server, RabbitMQ uses a greater number of file descriptors and network sockets. Since RabbitMQ will [block new connections][alarms] for nodes that have reached their file descriptor limit, monitoring the available number of file descriptors helps you keep your system running (configuring the file descriptor limit depends on your system, as seen in the context of Linux [here][kernel-limits]). On the front page of the management plugin UI, you'll see a count of your file descriptors for each node. You can fetch this information through the HTTP API (see [Part 2][part2]). This timeseries graph shows what happens to the count of file descriptors used when we add, then remove, connections to the RabbitMQ server.

{{< img alt="RabbitMQ Monitoring: file descriptors used by RabbitMQ nodes" src="rabbitmq-monitoring-fd-used.png" >}}

#### Metrics to alert on: Disk space used
RabbitMQ goes into a state of alarm when the available disk space of a given node [drops below a threshold][disk-alarms]. Alarms [notify your application][connection-blocked] by passing an AMQP [method][amqp-methods], `connection.blocked`, which RabbitMQ clients handle differently (e.g. [Ruby][bunny-blocked], [Python][pika-blocked]). The default threshold is 50MB, and the number is configurable. RabbitMQ checks the storage of a given drive or partition every 10 seconds, and checks more frequently closer to the threshold. Disk alarms impact your whole cluster: once one node hits its threshold, the rest will stop accepting messages. By monitoring storage at the level of the node, you can make sure your RabbitMQ cluster remains available. If storage becomes an issue, you can check [queue-level metrics](#queue-performance) and see which parts of your RabbitMQ setup demand the most disk space.

#### Metrics to alert on: Memory used
As with storage, RabbitMQ [alerts on memory][memory-alarms]. Once a node's RAM utilization exceeds a threshold, RabbitMQ blocks all connections that are publishing messages. If your application requires a different threshold than the default of 40 percent, you can set the `vm_memory_high_watermark` in your RabbitMQ configuration file. Monitoring the memory your nodes consume can help you avoid surprise memory alarms and throttled connections. 

The challenge for monitoring memory in RabbitMQ is that it's used [across your setup][memory-use], at different scales and different points within your architecture, for application-level abstractions such as queues as well as for dependencies like [Mnesia][mnesia], Erlang's internal database management system. A crucial step in monitoring memory is to break it down by use. In [Part 2][part2], we'll cover tools that let you list application objects by memory and visualize that data in a graph.

### Connection performance
Any traffic in RabbitMQ flows through a TCP connection. Messages in RabbitMQ [implement][amqp-concepts] the structure of the AMQP frame: a set of headers for attributes like content type and routing key, as well as a binary payload that contains the content of the message. RabbitMQ is well suited for a [distributed network][distributed], and even single-machine setups work through local TCP connections. Like monitoring exchanges, monitoring your connections helps you understand your application's messaging traffic. While exchange-level metrics are observable in terms of RabbitMQ-specific abstractions such as message rates, connection-level metrics are reported in terms of computational resources.

Name  | Description  | [Metric type][monitor-101] | Availability
:--|:---|:--|:--|
Data rates | Number of octets sent/received within a TCP connection per second | Resource: Utilization | management plugin |

#### Metrics to watch: Data rates
The logic of publishing, routing, queuing and subscribing is independent of a message's size. RabbitMQ messages are always [first-in, first-out][queue-docs], and require a consumer to parse their content. From the perspective of a queue, all messages are equal.

One way to get insight into the payloads of your messages, then, is by monitoring the data that travels through a connection. If you're seeing a rise in memory or storage in your [nodes](#nodes), the messages moving to consumers through a connection may be holding a greater payload. Whether the messages use memory or storage depends on your [persistence][persistence] settings, which you can monitor along with your [queues](#queue-performance). A rise in the rate of sent octets may explain spikes in storage and memory use downstream.

### Queue performance
Queues receive, push, and store messages. After the exchange, the queue is a message's final stop within the RabbitMQ server before it reaches your application. In addition to [observing your exchanges](#exchange-performance), then, you will want to monitor your [queues][queue-docs]. Since the message is the top-level unit of work in RabbitMQ, monitoring queue traffic is one way of measuring your application's throughput and performance.

Name  | Description  | [Metric type][monitor-101] | Availability
:--|:---|:--|:--|
Queue depth | Count of all messages in the queue | Resource: Saturation | `rabbitmqctl`
Messages unacknowledged | Count of messages a queue has delivered without receiving acknowledgment from a consumer | Resource: Error | `rabbitmqctl`
Messages ready | Count of messages available to consumer | Other | `rabbitmqctl`
Message rates | Messages that move in or out of a queue per second, whether unacknowledged, delivered, acknowledged, or redelivered | Work: Throughput | management plugin
Messages persistent | Count of messages written to disk | Other | `rabbitmqctl`
Message bytes persistent | Sum in bytes of messages written to disk | Resource: Utilization | `rabbitmqctl`
Message bytes RAM | Sum in bytes of messages stored in memory | Resource: Utilization | `rabbitmqctl`
Number of consumers | Count of consumers for a given queue | Other | `rabbitmqctl`
Consumer utilization | Proportion of time that the queue can deliver messages to consumers | Resource: Availability | management plugin

#### Metrics to watch: Queue depth, messages unacknowledged, and messages ready
Queue depth, or the count of messages currently in the queue, tells you a lot and very little: a queue depth of  zero can indicate that your consumers are behaving efficiently or that a producer has thrown an error. The usefulness of queue depth depends on your application's expected performance, which you can compare against queue depths for messages in specific states. 

For instance, `messages_ready` indicates the number of messages that your queues have exposed to subscribing consumers. Meanwhile, `messages_unacknowledged` tracks messages that have been delivered but remain in a queue pending explicit [acknowledgment][confirms] (an `ack`) by a consumer. By comparing the values of `messages`, `messages_ready` and `messages_unacknowledged`, you can understand the extent to which queue depth is due to success or failure elsewhere.

#### Metrics to watch: Message rates
You can also retrieve rates for messages in different states of delivery. If your `messages_unacknowledged` rate is higher than usual, for example, there may be errors or performance issues downstream. If your deliveries per second are lower than usual, there may be issues with a producer, or your routing logic may have changed.

This dashboard shows message rates for three queues, all part of a test application that collects data about New York City.

{{< img alt="RabbitMQ monitoring: Screenboard of message-related metrics" src="rabbitmq-monitoring-queue-dash.png" popup="true" wide="true" >}}

#### Metric to watch: Messages persistent, message bytes persistent, and message bytes RAM
A queue may [persist messages][persistence] in memory or on disk, preserving them as pairs of keys and values in a message store. The way RabbitMQ stores messages depends on whether your queues and messages are [configured][tutorial-two] to be, respectively, [durable and persistent][amqp-concepts]. Transient messages are written to disk in conditions of memory pressure. Since a queue consumes both storage and memory, and does so dynamically, it's important to keep track of your queues' resource metrics. For instance you can compare two metrics, `message_bytes_persistent` and `message_bytes_ram`, to understand how your queue is allocating messages between resources.

#### Metric to alert on: Number of consumers
Since you configure consumers manually, an application running as expected should have a stable consumer count. A lower-than-expected count of consumers can indicate failures or errors in your application.

#### Metric to alert on: Consumer utilization
A queue's consumers are not always able to receive messages. If you have configured a consumer to acknowledge messages manually, you can stop your queues from releasing more than a certain number at a time before they are consumed. This is your channel's [prefetch setting][confirms]. If a consumer encounters an error and terminates, the proportion of time in which it can receive messages will shrink. By measuring [consumer utilization][bottlenecks], which the management plugin (see [Part 2][part2]) reports as a percentage and as a decimal between 0 and 1, you can determine the availability of your consumers.

## Get inside your messaging stack
Much of the work that takes place in your RabbitMQ setup is only observable in terms of abstractions within the server, such as exchanges and queues. RabbitMQ reports metrics on these abstractions in their own terms, for instance counting the messages that move through them. Abstractions you can monitor, and the metrics RabbitMQ reports for them, include:

- [Exchanges](#exchange-performance): Messages published in, messages published out, messages unroutable
- [Queues](#queue-performance): Queue depth, messages unacknowledged, messages ready, messages persistent, message bytes persistent, message bytes RAM, number of consumers, consumer utilization

Monitoring your message traffic, you can make sure that the loosely coupled services within your application are communicating as intended.

You will also want to track the resources that your RabbitMQ setup consumes. Here you'll monitor:

- [Nodes](#nodes): File descriptors used, file descriptors used as sockets, disk space used, memory used
- [Connections](#connection-performance): Octets sent and received

In [Part 2][part2] of this series, we'll show you how to use a number of RabbitMQ monitoring tools. In [Part 3][part3], we'll introduce you to comprehensive RabbitMQ monitoring with Datadog, including the [RabbitMQ integration][rabbitmq-integration].

## Acknowledgments
We wish to thank our friends at [Pivotal][pivotal] for their technical review of this series.

[alarms]: https://www.rabbitmq.com/alarms.html

[alt-exchange]: http://www.rabbitmq.com/amqp-0-9-1-quickref.html#exchange.declare

[amqp-concepts]: https://www.rabbitmq.com/tutorials/amqp-concepts.html

[amqp-extensions]: https://www.rabbitmq.com/extensions.html

[amqp-methods]: https://www.rabbitmq.com/tutorials/amqp-concepts.html#amqp-methods

[bindings]: https://www.rabbitmq.com/tutorials/tutorial-four-python.html

[bunny-confirm]: http://rubybunny.info/articles/extensions.html

[bunny-blocked]: http://reference.rubybunny.info/Bunny/Session.html#blocked%3F-instance_method

[clustering]: https://www.rabbitmq.com/clustering.html

[confirms]: https://www.rabbitmq.com/confirms.html

[disk-alarms]: https://www.rabbitmq.com/disk-alarms.html

[distributed]: https://www.rabbitmq.com/distributed.html

[distrib-erlang]: http://erlang.org/doc/reference_manual/distributed.html

[exchange-types]: https://www.rabbitmq.com/tutorials/amqp-concepts.html#exchanges

[bottlenecks]: https://www.rabbitmq.com/blog/2014/04/14/finding-bottlenecks-with-rabbitmq-3-3/

[connection-blocked]: https://www.rabbitmq.com/connection-blocked.html

[erlang-nodes]: http://erlang.org/doc/reference_manual/distributed.html

[http-stats]: https://pulse.mozilla.org/doc/stats.html

[kernel-limits]: https://www.rabbitmq.com/install-debian.html#kernel-resource-limits

[rabbitmq-integration]: https://docs.datadoghq.com/integrations/rabbitmq/

[management-plugin]: https://www.rabbitmq.com/management.html

[memory-alarms]: https://www.rabbitmq.com/memory.html

[memory-use]: https://www.rabbitmq.com/memory-use.html

[mnesia]: http://erlang.org/doc/man/mnesia.html

[nova]: https://www.datadoghq.com/blog/openstack-monitoring-nova/

[monitor-101]: https://www.datadoghq.com/blog/monitoring-101-collecting-data/

[part2]: /blog/rabbitmq-monitoring-tools

[part3]: /blog/monitoring-rabbitmq-performance-with-datadog/

[persistence]: https://www.rabbitmq.com/persistence-conf.html

[pika-blocked]: http://pika.readthedocs.io/en/0.10.0/modules/adapters/blocking.html#pika.adapters.blocking_connection.BlockingConnection.add_on_connection_blocked_callback

[pivotal]: https://pivotal.io/

[pub-sub]: https://www.rabbitmq.com/tutorials/tutorial-three-python.html

[protocols]: https://www.rabbitmq.com/protocols.html

[queue-docs]: https://www.rabbitmq.com/queues.html

[rabbit-amqp]: http://www.rabbitmq.com/amqp-0-9-1-quickref.html

[rabbitmqctl]: https://www.rabbitmq.com/man/rabbitmqctl.1.man.html

[rpc]: https://www.rabbitmq.com/tutorials/tutorial-six-python.html

[tutorials]: http://www.rabbitmq.com/getstarted.html

[tutorial-two]: https://www.rabbitmq.com/tutorials/tutorial-two-python.html

[work-queues]: https://www.rabbitmq.com/tutorials/tutorial-two-python.html