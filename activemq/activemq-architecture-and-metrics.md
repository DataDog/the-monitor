---
authors:
- email: david.lentz@datadoghq.com
  name: David M. Lentz
  image: lentz.jpg
blog/category: 
- series metrics
blog/tag:
- activemq
- metrics
- JMX
- architecture
- message broker
date: 2018-12-04
description: Understand the ActiveMQ architecture, and learn about key ActiveMQ metrics to track.
excerpt: Understand the ActiveMQ architecture, and learn about key ActiveMQ metrics to track.
draft: false
image: active-mq_longform_series_181009_Part_1.png
preview_image: active-mq_longform_series_181009_Part_1.png
slug: activemq-architecture-and-metrics
technology: activemq
title: ActiveMQ architecture and key metrics
series: activemq-monitoring
tcp:
- title: "eBook: Monitoring In The Cloud"
  desc: "Build a framework for monitoring dynamic infrastructure and applications."
  cta: "Download to learn more"
  link: "https://www.datadoghq.com/resources/monitoring-in-the-cloud-ebook/?utm_source=Content&utm_medium=eBook&utm_campaign=BlogCTA-MonitoringInTheCloud"
  img: Thumbnail-MonitoringInTheCloud.png
---

Apache ActiveMQ is message-oriented middleware (MOM), a category of software that sends messages between applications. Using standards-based, asynchronous communication, ActiveMQ allows loose coupling of the elements in an IT environment, which is often foundational to enterprise messaging and distributed applications.

ActiveMQ is a Java-based open source project developed by the [Apache Software Foundation](http://activemq.apache.org/). It's comparable to other messaging systems, such as [Apache Kafka](https://www.datadoghq.com/blog/monitoring-kafka-performance-metrics/), [RabbitMQ](https://www.datadoghq.com/blog/rabbitmq-monitoring/), and [Amazon Simple Queue Service](https://aws.amazon.com/sqs/). Amazon also offers [Amazon MQ](https://aws.amazon.com/amazon-mq/), which is a managed implementation of ActiveMQ, integrated into its AWS cloud services. Essentially, each of these technologies supports enterprise messaging through a loosely coupled infrastructure. 

ActiveMQ makes use of the Java Message Service (JMS) API, which defines a standard for software to use in creating, sending, and receiving messages. JMS is included in the Java Enterprise Edition, making it available for Java developers to use as they create the client applications that send, receive, and process messages. It's possible to write ActiveMQ clients in other languages (such as Node.js, Ruby, and Python), but ActiveMQ is built on Java, and is probably best suited for an organization that's already invested in Java.

In this post, we'll look at how ActiveMQ works, and at some key ActiveMQ metrics you can monitor to understand the performance of your messaging infrastructure.

## How does ActiveMQ work?

ActiveMQ sends messages between client applications—**producers**, which create messages and submit them for delivery, and **consumers**, which receive and process messages. The ActiveMQ **broker** routes each message through one of two types of **destinations**:

* a **queue**, where it awaits delivery to a single consumer (in a messaging domain called **point-to-point**), or 
* a **topic**, to be delivered to multiple consumers that are subscribed to that topic (in a messaging domain called **publish/subscribe**, or "pub/sub") 

ActiveMQ gives you the flexibility to send messages through both queues and topics using a single broker. In point-to-point messaging, the broker acts as a load balancer by routing each message from the queue to one of the available consumers in a round-robin pattern. When you use pub/sub messaging, the broker delivers each message to every consumer that is subscribed to the topic. 

{{< img src="activemq_diagram1.png" caption="The ActiveMQ architecture contains the broker, destinations, and client applications." alt="The ActiveMQ broker sends messages from producers to consumers." >}}


**JMS** is the communication standard that ActiveMQ uses to send and receive messages. ActiveMQ is a **JMS provider**, which means that it implements the functionality [specified in the JMS API][jms-api]. Client applications—producers and consumers—use the JMS API to send and receive messages. Non-JMS clients (written in PHP, Python, or other languages) can also connect to the ActiveMQ broker via the [AMQP][amqp-protocol], [MQTT][mqtt-protocol], and [STOMP][stomp-protocol] protocols.

ActiveMQ sends messages asynchronously, so consumers don't necessarily receive messages immediately. The producer's task of composing and sending a message is disconnected from the consumer's task of fetching it. Because ActiveMQ uses a broker as an intermediary, producers and consumers are independent (and even unaware) of each other. As soon as a producer sends a message to a broker, its task is complete, regardless of whether or when a consumer receives the message. Conversely, when a consumer receives a message from a broker, it does so without knowledge of the producer that created the message. 

This type of arrangement, in which clients function without knowledge of one another, is known as loose coupling. The benefits of loose coupling include:

* High throughput: Because producers don't need to wait for acknowledgment from the consumer or broker, they can send messages quickly. ActiveMQ can achieve throughput of [thousands of messages per second][activemq-performance]. 
* Flexibility: Clients can be temporarily unavailable, can be dynamically added to the environment, and can even be rewritten in a new language without affecting other clients or causing errors in the messaging process.
* Heterogeneity: Clients operate independently, communicating with the ActiveMQ broker but not directly with one another. As a result, they may be written in any of the [languages ActiveMQ supports][supported-languages]. 

Because the components of the ActiveMQ architecture are decoupled, you need to monitor producers, consumers, destinations, and brokers holistically to understand the context of any issues that may arise. For example, metrics that show a producer's output has paused may not indicate a problem, but if they are viewed alongside metrics showing a destination's rising memory usage, they can reveal a bottleneck in the larger system. Later, we'll look at some specific metrics that contribute to the big picture of ActiveMQ monitoring. But first, we'll examine ActiveMQ's fundamental unit of work—the message.

### Messages

Each **message** ActiveMQ sends is based on the JMS specification, and is made up of **headers**, optional **properties**, and a **body**. 

#### Headers

JMS message headers contain metadata about the message. Headers are defined in the JMS specification, and their values are set either when the producer creates the message, or when ActiveMQ sends it. 

Headers convey qualities of the message that affect how the broker and clients behave. Let's take a look at two key characteristics that ActiveMQ takes into account when delivering messages: expiration and persistence.

##### Message expiration
Depending on its content and purpose, a message may lose its value after a certain amount of time. When a producer creates a message, it can set an expiration value in the message header. If it does not, the header value remains empty and the message never expires.

ActiveMQ discards any expired messages from its queues and topics rather than delivering them, and consumer code is expected to disregard any message that remains unprocessed after its expiration. 

##### Message persistence
Persistence is a characteristic of a message. It's defined in the JMS spec and isn't unique to ActiveMQ. ActiveMQ messages are persistent by default, but you can [configure persistence][activemq-persistence] on a per-message or per-producer basis. When you send a persistent message, the broker saves the message to the message store on disk before attempting delivery. If the broker were to crash at that point, a copy of the message would remain and the process of sending the message could recover when the broker restarted. A non-persistent message, on the other hand, exists only in the broker's memory and would be lost in an event that caused the broker to restart.

Sending non-persistent messages is usually faster, because it doesn't require the broker to execute expensive write operations. Non-persistent messaging is appropriate for short-lived data that gets replaced at frequent intervals, such as a once-a-minute update of an item's location.

#### Properties
[Properties][activemq-message-properties] function similar to headers, and provide a way of adding optional metadata to a message. ActiveMQ supports some properties that are defined in the JMS specification, and also implements some properties that aren't part of the spec.

Producers can also define properties—arbitrarily and outside the JMS spec—and apply them to each message. Consumers can implement [selectors][activemq-selectors] to filter messages based on values present in the message properties. For example, you can configure an ActiveMQ producer to attach a `coin` property to each message, with a value of either `heads` or `tails`, and send them all to the same topic. You can write two consumers—a `heads` consumer and a `tails` consumer—that subscribe to that topic but that only receive messages with their selected value of the `coin` property.

#### Body
The content of an ActiveMQ message is the **body**. The body of a message can be text or binary data. (It's also acceptable for a message's body to be empty.) The value of the `JMSType` message header, which is set explicitly by the producer when the message is created, determines what can be carried in the body of the message: a file, a byte stream, a Java object, a stream of Java primitives, a set of name-value pairs, or a string of text.

For more information about message types, see [this JMS documentation][message-bodies].

### Memory and storage
ActiveMQ uses memory to store messages awaiting dispatch to consumers. Each message occupies some of the available memory (how much depends on the size of the message) until it is dequeued—delivered to a consumer that then processes the message and acknowledges receipt. At that point, ActiveMQ frees up the memory that had been used for that message. When producers are faster than consumers—there's more enqueuing than dequeuing over a given time period—ActiveMQ's memory use increases. 

ActiveMQ also writes messages to disk, in either a message store (where persistent messages go), or a temp store (where non-persistent messages go when the broker runs out of memory to store them).

In this section, we'll look at how ActiveMQ uses memory and disk to store messages.

#### Memory
The host system dedicates some of its memory as heap memory for the JVM in which ActiveMQ runs. By default, the ActiveMQ startup script tells Java to create a heap with a maximum size of 1 GB. To specify the maximum percentage of the JVM's heap memory that ActiveMQ can use, adjust the `memoryUsage` child of the `systemUsage` element in the **activemq.xml** file. You can express this as a percentage of the JVM's heap memory (e.g., `<memoryUsage percentOfJvmHeap="60" />`), or as a number of bytes, as shown in the following partial **activemq.xml** file. (Note that your `<broker>` element may look different than the one in this example, depending on your configuration.)

```
<broker xmlns="http://activemq.apache.org/schema/core" brokerName="MY_BROKER">
[...]
    <systemUsage>
        <systemUsage>
            <memoryUsage>
                <memoryUsage limit="1 gb" />
            </memoryUsage>
        </systemUsage>
    </systemUsage>
[...]
</broker>
```

This broker memory limit applies to all destinations, combined. In other words, the memory specified on the broker's `memoryUsage` element must be shared amongst all queues and topics. Each destination may be configured with an explicit memory limit, designated in the `memoryLimit` element inside an optional `policyEntry` in the **activemq.xml** file:

```
<broker xmlns="http://activemq.apache.org/schema/core" brokerName="MY_BROKER">
[...]
    <destinationPolicy>
        <policyMap>
            <policyEntries>
                <policyEntry queue="MY_QUEUE" memoryLimit="100mb" />
                <policyEntry topic="MY_TOPIC" memoryLimit="50mb" />
            </policyEntries>
        </policyMap>
    </destinationPolicy>
[...]
</broker>
```

ActiveMQ uses memory differently for non-persistent messages than it does for persistent messages. Each non-persistent message is stored in memory as it arrives. When the available memory is full, all messages in memory are moved to the temp store on the disk. Each persistent message is also stored in memory as it arrives, and is also written to the message store on disk. If no more memory is available, incoming persistent messages are written directly into the message store.

As long as the destination's memory doesn't fill up, incoming messages remain there and can be dispatched directly from memory without incurring any latency related to disk activity. If the message is not available in memory (either because it got flushed from memory to the temp store or because it was written to the message store when available memory was full), the broker must page the message data from disk in order to dispatch it to a consumer. 

#### Storage
You can specify the amount of storage to be used for persistent messages in the **activemq.xml** file's `storeUsage` element, as in the example below:

```
<systemUsage>
    <systemUsage>
        <storeUsage>
            <storeUsage limit="100 mb"/>
        </storeUsage>
    </systemUsage>
</systemUsage>
```

Storage for non-persistent messages is specified separately. Non-persistent messages are written to storage only after available memory is exhausted. You can specify the amount of storage to be used for non-persistent messages in the **activemq.xml** file's `tempUsage` element, which defaults to 50 GB. You can configure this as a percentage of available disk space ([`percentLimit`][activemq-pfc]) or as a number of bytes (as shown below):

```
<systemUsage>
    <systemUsage>
        <tempUsage>
            <tempUsage limit="100 mb"/>
        </tempUsage>
    </systemUsage>
</systemUsage>
```

[KahaDB][kahadb] is ActiveMQ's default message storage mechanism. It stores both persistent and non-persistent messages. KahaDB is designed to quickly persist a large number of messages to support a busy messaging system. KahaDB replaces [AMQ Message Store][amq-message-store], which is still available but is no longer the default message store as of ActiveMQ version 5.4. 

ActiveMQ also supports storing messages via [JDBC][activemq-jdbc]. Using this configuration, you can choose from a number of SQL databases to find the storage mechanism that best meets your needs for scalability and support.

We've looked at some characteristics of JMS messages, and at some different ways ActiveMQ stores and sends them. But ActiveMQ's work isn't done until a message is delivered to a consumer. In the next section we'll look at how consumers handle messages. 

### Consumers
Consumers are the applications that receive the messages ActiveMQ sends. In this section, we'll look at some key characteristics that influence the behavior of consumers: subscriptions and acknowledgment.

#### Durable vs. nondurable subscriptions
A consumer can subscribe to a topic as either a durable or nondurable subscriber. (Durability applies only to messages within a topic, not within a queue.) In the case of a durable subscription, ActiveMQ will retain messages if the subscriber is unavailable. When that subscriber reconnects, it receives new messages that arrived during the time it was disconnected. A nondurable subscriber would not receive any messages published to the topic during the time it was disconnected from the broker.

#### Acknowledgment
Each consumer is configured to use an [acknowledgment mode][acknowledgment-mode] that determines when and how it will acknowledge a message—either automatically upon receipt, or by making an explicit call to an `acknowledge` method. ActiveMQ's metrics show information about the number of messages acknowledged and not yet acknowledged, but the meaning of those metrics depends on the consumer's acknowledgment mode. A spike in unacknowledged messages could mean the consumer is offline and unable to receive messages, or that the consumer is failing to successfully execute its manual `acknowledge` call.

So far, we've covered what ActiveMQ is, and how it works. In the next section, we'll introduce some useful metrics to help you understand how to monitor ActiveMQ.

## Key ActiveMQ metrics
By tracking ActiveMQ metrics, you can effectively monitor resource usage, broker performance, and message activity. Monitoring these metrics can help you understand the performance of your messaging infrastructure and detect potential problems that might affect your services. 

{{< img src="activemq_dash1.png" wide="true" alt="Datadog's ActiveMQ dashboard is made up of graphs showing resource usage, broker performance, and message activity." >}}

ActiveMQ metrics come from:

* [the destinations](#destination-metrics) (topics and queues)
* [the broker](#broker-metrics)
* [the JVM](#jvm-metrics) in which the broker is running
* [the host system](#hostlevel-metrics) that runs the JVM

Because ActiveMQ is written in Java, you can query destination, broker, and JVM metrics via [Java Management Extensions][oracle-jmx] (JMX). You can view these metrics using [JConsole][oracle-jconsole], a GUI that's included in the JDK, or with other JMX-compliant monitoring systems. ActiveMQ also comes with a Web Console and a statistics plugin. In [Part 2][part-2] of this series, we'll look at the tools available to help you collect and view ActiveMQ metrics. 

In this section, we'll explore key ActiveMQ metrics—where to find them, and the reasons you might want to collect them. This builds on our [Monitoring 101 series][monitoring-101], which discusses how to identify high-value monitoring data, how to create a smart strategy for alerting, and how to investigate the issues your monitoring uncovers. 

### Destination metrics
All ActiveMQ messages pass through destinations. Monitoring destination metrics can give you information about the speed, volume, and resource usage of your messaging system.


|JMX attribute|Description|MBean|Metric type|
|---|---|---|---|
|`MemoryPercentUsage`|Percentage of configured memory used by the destination|org.apache.activemq:type=Broker,brokerName=\<MY_BROKER\>,destinationType=(Queue\|Topic),destinationName=\<MY_DESTINATION\>|Resource: Utilization|
|`ConsumerCount`|The number of consumers currently subscribed to the destination|org.apache.activemq:type=Broker,brokerName=\<MY_BROKER\>,destinationType=(Queue\|Topic),destinationName=\<MY_DESTINATION\>|Other|
|`ProducerCount`|The number of producers currently attached to the  destination|org.apache.activemq:type=Broker,brokerName=\<MY_BROKER\>,destinationType=(Queue\|Topic),destinationName=\<MY_DESTINATION\>|Other|
|`QueueSize`|The number of messages (per destination) that have not been acknowledged by a consumer. Includes those not yet dispatched|org.apache.activemq:type=Broker,brokerName=\<MY_BROKER\>,destinationType=(Queue\|Topic),destinationName=\<MY_DESTINATION\>|Resource: Saturation|
|`ExpiredCount`|The number of messages in the destination that expired before they could be delivered|org.apache.activemq:type=Broker,brokerName=\<MY_BROKER\>,destinationType=(Queue\|Topic),destinationName=\<MY_DESTINATION\>|Other|

#### Metric to alert on: MemoryPercentUsage
The `MemoryPercentUsage` metric represents the percentage of the destination's `memoryLimit` currently in use. If you haven't set a `memoryLimit` for the destination, it inherits the broker's configured `memoryUsage`, and the `MemoryPercentUsage` metric represents the percentage of that value currently being used by the destination. (See the [Memory and storage](#memory-and-storage) section for more details.)

As the destination's `MemoryPercentUsage` rises, you may see a decrease in the rate at which your producers send messages. This is thanks to [Producer Flow Control][activemq-pfc] (PFC), which is enabled by default for persistent messages. When destination memory becomes limited (or when the broker's disk space runs low), PFC throttles message flow by causing the broker to hold incoming messages instead of delivering them. When a message is held, the producer that sent it doesn't receive an acknowledgment from the broker, so it delays sending any further messages. 

PFC is triggered once the destination's memory usage is at or above the `cursorMemoryHighWaterMark` value defined for the destination. The `cursorMemoryHighWaterMark` defaults to 70 percent of the available memory (either the broker's `memoryUsage` limit or, if defined, the destination's `memoryLimit`). You can change this value by adding an attribute to the relevant `policyEntry` element in **activemq.xml**. The example below shows how you would set `cursorMemoryHighWaterMark` values of 80 percent for a queue named `MY_QUEUE`, and 50 percent for a topic named `MY_TOPIC`. 

```
<broker xmlns="http://activemq.apache.org/schema/core" brokerName="MY_BROKER">
[...]
    <destinationPolicy>
        <policyMap>
            <policyEntries>
                <policyEntry queue="MY_QUEUE" cursorMemoryHighWaterMark="80" />
                <policyEntry topic="MY_TOPIC" cursorMemoryHighWaterMark="50" />
            </policyEntries>
        </policyMap>
    </destinationPolicy>
[...]
</broker>
```

See [the ActiveMQ documentation][activemq-destination-policies] for more information about configuring memory limits.

Because PFC could have a noticeable effect on the performance of your messaging system, you should create an alert to notify you when a destination's `MemoryPercentUsage` value approaches its `cursorMemoryHighWaterMark` value, so you can take action before PFC is activated.

If you are using queues, you can reduce memory pressure by scaling out your consumer fleet to dequeue messages more quickly. If your system is using topics with durable subscribers, make sure those consumers are available often enough to prevent a backlog of messages. In either case, increasing memory available to your destinations will help, too.

#### Metric to watch: ConsumerCount
Sooner or later, each destination (queue or topic) needs to deliver messages to consumers. Consumers may come and go, though (for example, as your infrastructure dynamically scales), and a fluctuating consumer count could be normal in some cases. However, you should be able to identify some normal operating parameters for `ConsumerCount`, and watch this metric for abnormalities. If your `ConsumerCount` value changes unexpectedly, your consumer fleet may have scaled out more than usual, or some hosts may have become unavailable.

#### Metric to watch: ProducerCount
This metric tracks the number of producers currently attached to a broker. Whether a `ProducerCount` of zero indicates a problem depends on your expected pattern of activity. If your producers are typically active only sporadically (e.g., if they send a batch of messages once a day), this may be normal. However, if you expect to have active producers at all times, you should investigate a `ProducerCount` of zero, as it could indicate a service interruption.

#### Metric to watch: QueueSize
QueueSize tracks the number of messages that have not been acknowledged by consumers. If you see this metric consistently increasing, it could indicate that the producers are publishing messages faster than consumers are processing them, or that consumers are failing to acknowledge the messages they receive. This could cause the destination to run out of memory (which could even affect the performance of the broker's other destinations), so you should monitor the destination's `MemoryPercentUsage` metric alongside this one. 

{{< img src="activemq_dash3.png" alt="QueueSize and MemoryPercentUsage metrics rise together." >}}

Despite what its name suggests, you can track the `QueueSize` of queues _and_ topics. In the case of a queue, you may be able to reduce `QueueSize` by scaling out your consumer fleet so that more hosts are available to read from the queue. A topic's `QueueSize` could rise if durable consumers are unavailable to fetch messages—you can address this by decreasing the expiration time of new messages or by [removing durable subscribers][activemq-durable-subscribers] that are consistently unavailable.

#### Metric to watch: ExpiredCount
This metric represents the number of messages that expired before they could be delivered. If you expect all messages to be delivered and acknowledged within a certain amount of time, you can set an expiration for each message, and investigate if your `ExpiredCount` metric rises above zero.

In some cases, though, expired messages may not be a sign of trouble. For example, if your environment includes consumers with durable subscriptions but an unreliable network, some messages could expire while those consumers are disconnected. When the consumers reconnect, they’ll request all messages published in the interim, but if some of those messages contain information that frequently gets updated (e.g., status updates at one-minute intervals), it's better to discard them than deliver them.

### Broker metrics
As mentioned earlier, the ActiveMQ broker has configurable limits on the amount of memory and disk space it's allowed to use. Here are some of the metrics you should monitor to ensure that your broker is working properly within its resource limits.

|JMX attribute|Description|MBean|Metric type|
|---|---|---|---|
|`MemoryPercentUsage`|Percentage of available memory used by the broker|org.apache.activemq:type=Broker,brokerName=\<MY_BROKER\>|Resource: Utilization|
|`StorePercentUsage`|Percentage of available disk space ([`storeUsage`](#memory-and-storage)) used for persistent message storage|org.apache.activemq:type=Broker,brokerName=\<MY_BROKER\>|Resource: Utilization|
|`TempPercentUsage`|Percentage of available disk space ([`tempUsage`](#memory-and-storage)) used for non-persistent message storage|org.apache.activemq:type=Broker,brokerName=\<MY_BROKER\>|Resource: Utilization|
|`TotalEnqueueCount`|The total number of messages sent to the broker|org.apache.activemq:type=Broker,brokerName=\<MY_BROKER\>|Work: Throughput
|`TotalDequeueCount`|The total number of messages the broker has delivered to consumers|org.apache.activemq:type=Broker,brokerName=\<MY_BROKER\>|Work: Throughput|
|`Topics`|A count of topics currently attached to this broker|org.apache.activemq:type=Broker,brokerName=\<MY_BROKER\>|Other|
|`Queues`|A count of queues currently attached to this broker|org.apache.activemq:type=Broker,brokerName=\<MY_BROKER\>|Other|


#### Metric to alert on: MemoryPercentUsage
If you find that a broker's memory usage is rising, there are a few steps you can take to prevent resource constraints from affecting your application's performance.

* Scale out your consumers. This can increase the rate at which messages are consumed, allowing the broker to reclaim memory and disk space.
* Increase the memory available to the broker. (See the [Memory and storage](#memory-and-storage) section of this post for information.) To do this, you may need to scale up the amount of memory allocated to the JVM, which could require adding memory to the host.
* Reduce the memory available to the destinations associated with the broker (particularly if you have a large number of destinations). Although this will force the broker to persist messages to disk sooner, it also reduces the possibility of triggering PFC and enables producers to continue sending messages even when consumers are falling behind. See the [ActiveMQ documentation][activemq-out-of-memory] for more information.

If your host runs services in addition to ActiveMQ, comparing ActiveMQ memory usage to overall host-level usage may help you troubleshoot resource constraints by showing you specifically *how* your host's memory is being consumed.

#### Metric to alert on: StorePercentUsage
This is the percentage of available disk space ([`storeUsage`](#memory-and-storage)) used by the broker's persistent message store (which is KahaDB, by default). The broker can reach its persistent storage limit if consumers are slow or unavailable, and if messages are large. It's important to monitor this metric because if a broker runs out of persistent storage, PFC will cause producers to stop sending messages.

#### Metric to watch: TempPercentUsage
The broker holds non-persistent messages in memory. When memory fills up, the broker moves those messages to a temp location on the filesystem to free up memory. If the broker runs out of disk space to store temporary messages, producers will stop sending messages until storage space is freed up (assuming PFC is enabled). 

You might run out of temporary storage space for any number of reasons, including:

* Slow or absent consumers.
* Specifying a `tempUsage` value that is smaller than the broker's `memoryUsage`. In this case, the memory holds more message data than the temp store has room for, and `TempPercentUsage` will exceed 100% as soon as memory fills and messages are sent to the temp store.
* Specifying a `tempUsage` value that is smaller than [KahaDB's `journalMaxFileLength`][kahadb] (which is 32 MB by default). This could cause the temp store to fill up because the broker will create a 32 MB journal file to hold the message data on disk, regardless of the amount of message data in memory. 

If PFC is activated, your messaging throughput will drop, so it's important to monitor your `TempPercentUsage` value. You should alert on a value that gives you enough time to remove messages or add disk space before `TempPercentUsage` reaches 100% and triggers PFC.

#### Metrics to watch: TotalEnqueueCount and TotalDequeueCount
`TotalEnqueueCount` tracks the number of messages sent to the broker. You can monitor this metric to understand the volume of messages emitted by your producers. `TotalDequeueCount` is another throughput-related metric that shows the number of messages that have been delivered by the broker and acknowledged by your consumers. (Both `TotalEnqueueCount` and `TotalDequeueCount` are cumulative counts calculated over the entire time the broker has been running, and reset to zero when the broker is restarted.) 

You should monitor `TotalDequeueCount` alongside `TotalEnqueueCount` to understand your system's overall message volume and the degree to which consumers are keeping up with producers.

#### Metrics to watch: Topics and Queues
There's no correct number of topics or queues for any given ActiveMQ deployment, but you probably have expectations about what's right for your environment. This metric may help you troubleshoot any misbehavior like missing messages or producer errors, which could occur if a destination isn't available as expected. 

### JVM metrics
ActiveMQ runs within the JVM, so metrics that inform you of the health of the JVM can be critical in monitoring your messaging. In this section, we'll look at some key JVM metrics.

{{< img src="activemq_dash2.png" wide="true" alt="Dashboard graphs show JVM resource usage." >}}

|JMX attribute|Description|MBean|Metric type|
|---|---|---|---|
|`CollectionTime`|The total amount of time (in milliseconds) the JVM has spent executing garbage collection processes|java.lang:type=GarbageCollector,name=(Copy\|MarkSweepCompact\|PS MarkSweep\|PS Scavenge)|Other|
|`CollectionCount`|The total count of garbage collection processes executed by the JVM|java.lang:type=GarbageCollector,name=(Copy\|MarkSweepCompact\|PS MarkSweep\|PS Scavenge)|Other|
|`HeapMemoryUsage`|This contains values for the heap's `init`, `max`, `committed`, and `used` metrics|java.lang:type=Memory|Resource: Utilization|
|`ThreadCount`|Threads currently used by the JVM|java.lang:type=Threading|Other|


#### Metric to alert on: CollectionTime
Because ActiveMQ runs in the JVM, its memory is managed by [Java's garbage collection (GC) process][oracle-gc]. A running Java application requires memory to create the objects it uses, and the Java garbage collector periodically evaluates memory usage and frees up unused memory. As ActiveMQ's message volume increases, it will use more memory. As a result, the JVM will execute garbage collection more frequently, which could slow down messaging overall.

You can use JMX to query metrics that show the overall time spent on garbage collection. Any time the JVM spends on GC will have [some effect][understanding-gc] on the applications running there (like ActiveMQ), though it may not always be perceptible. GC metrics are cumulative, so you should expect to see them rise continually, returning to zero only when the JVM restarts. You should use a monitoring tool to track how frequently garbage collection is happening, and how long each process takes.

In [part 2][part-2] of this series, we'll look at some of the tools that use JMX to monitor ActiveMQ. You can use tools like these to watch for an increase in the frequency of GC activity. You can correlate GC activity with any corresponding spikes in the broker's `MemoryPercentUsage` that could explain a slowdown in your messaging activity.

#### Metric to watch: HeapMemoryUsage
The HeapMemoryUsage metric is a JSON object made up of `init`, `committed`, `max`, and `used` values.

* `init` is set when the JVM starts, and ActiveMQ's startup script passes an `init` value of 64 MB.
* `max` holds the value of the maximum possible size of the heap. By default, ActiveMQ sets this value to 1 GB.
* `committed` is set by the JVM, and fluctuates. This value indicates how much memory is guaranteed to be available for the JVM to use.
* `used` represents the amount of JVM heap memory currently in use.

You should watch `used` and `committed` together to ensure that the JVM isn't running out of available memory. Java will throw an `OutOfMemoryError` exception if the JVM's memory is exhausted. See the [Java documentation][java-out-of-memory] and the [ActiveMQ FAQ][activemq-out-of-memory] for guidance on resolving this problem.

#### Metric to watch: ThreadCount
Synchronous messaging requires a greater number of threads than asynchronous delivery. Using more threads causes the broker to incur the overhead of context switching, which requires more work from the host's CPU. This could cause a slowdown in the queueing and dispatching of messages, and ultimately could lead to lower message throughput. 

As described in the [ActiveMQ documentation][activemq-scaling], you can reduce the number of threads ActiveMQ requires by using thread pooling, [enabling optimized dispatch on your queues][activemq-per-destination-policies], or [using the NIO protocol][activemq-transports]. 

### Host-level metrics
Your host is the foundation of all the processes involved in ActiveMQ's messaging activities. To understand bottlenecks that may arise, and to make informed decisions about when to scale out, look to your host-level metrics.

|Name|Description|Metric type|
|---|---|---|
|Disk usage|The percentage of the host's available disk space currently in use|Resource: Utilization|
|Disk I/O|The rate of read and write operations per second|Resource: Utilization|

#### Metric to alert on: Disk usage
ActiveMQ uses disk space to store persistent messages, as well as non-persistent messages that get swapped to disk when memory fills up. After a message has been acknowledged by a consumer, ActiveMQ marks it to be deleted in the next cleanup cycle. (By default, this is every 30 seconds.) 

If your broker's `TotalEnqueueCount` is higher than its `TotalDequeueCount`, your host's disk could fill up. You'll also see this in the broker's `TempPercentUsage` and `StorePercentUsage` values. Create alerts to keep you informed of diminishing disk space so you can prevent performance problems.

#### Metric to watch: Disk I/O
When sending a persistent message, the broker first writes it to a journal. With multiple producers sending persistent messages, threads within the broker may compete for the chance to write to the journal. Rising disk I/O doesn't necessarily indicate contention between the threads, but it could be a sign that write operations are queuing up, reducing message throughput overall.

If you see high disk activity, it could mean that your broker is very busy, especially if you also see high `MemoryPercentUsage`. If this is the case, you should employ [ActiveMQ best practices][activemq-best-practices] for supporting many queues and topics. Additionally, you should consider creating a [network of brokers][activemq-network-of-brokers]. 

## Making meaning of the metrics
ActiveMQ metrics can help you proactively maintain your messaging infrastructure, providing you with information you need to investigate errors, missing messages, and unexpected latency. In this post, we've looked at the metrics you can collect from ActiveMQ, and highlighted some that are particularly valuable to monitor. In [part 2 of this series][part-2], we'll show you some of the tools you can use to gather metrics from your ActiveMQ brokers, queues, and topics.

## Acknowledgments
We'd like to thank Gary Tully of [Red Hat][red-hat] for his technical review of this series.

[acknowledgment-mode]: https://docs.oracle.com/cd/E19798-01/821-1841/bncfw/index.html
[activemq-best-practices]: http://activemq.apache.org/how-do-i-configure-10s-of-1000s-of-queues-in-a-single-broker-.html
[activemq-destination-policies]: http://activemq.apache.org/per-destination-policies.html
[activemq-durable-subscribers]: http://activemq.apache.org/manage-durable-subscribers.html
[activemq-jdbc]: http://activemq.apache.org/jdbc-support.html
[activemq-message-properties]: http://activemq.apache.org/activemq-message-properties.html
[activemq-network-of-brokers]: http://activemq.apache.org/networks-of-brokers.html
[activemq-out-of-memory]: https://activemq.apache.org/javalangoutofmemory.html
[activemq-per-destination-policies]: http://activemq.apache.org/per-destination-policies.html
[activemq-performance]: http://activemq.apache.org/performance.html
[activemq-persistence]: http://activemq.apache.org/what-is-the-difference-between-persistent-and-non-persistent-delivery.html
[activemq-pfc]: http://activemq.apache.org/producer-flow-control.html
[activemq-scaling]: http://activemq.apache.org/scaling-queues.html
[activemq-selectors]: http://activemq.apache.org/selectors.html
[activemq-transports]: http://activemq.apache.org/configuring-transports.html
[amq-message-store]: http://activemq.apache.org/amq-message-store.html
[amqp-protocol]: http://activemq.apache.org/amqp.html
[java-out-of-memory]: https://docs.oracle.com/javase/8/docs/technotes/guides/troubleshoot/memleaks002.html
[jms-api]: https://javaee.github.io/jms-spec/pages/JMS20FinalRelease
[kahadb]: http://activemq.apache.org/kahadb.html
[message-bodies]: https://docs.oracle.com/cd/E19798-01/821-1841/6nmq2cpps/index.html#bncex
[monitoring-101]: https://www.datadoghq.com/blog/tag/monitoring-101/
[mqtt-protocol]: http://activemq.apache.org/mqtt.html
[oracle-gc]: https://docs.oracle.com/javase/9/gctuning/introduction-garbage-collection-tuning.htm
[oracle-jconsole]: https://docs.oracle.com/javase/7/docs/technotes/guides/management/jconsole.html
[oracle-jmx]: https://www.oracle.com/technetwork/articles/java/javamanagement-140525.html
[part-2]: /blog/collecting-activemq-metrics/
[red-hat]: https://www.redhat.com/
[stomp-protocol]: https://activemq.apache.org/stomp.html
[supported-languages]: http://activemq.apache.org/cross-language-clients.html
[understanding-gc]: https://www.cubrid.org/blog/understanding-java-garbage-collection