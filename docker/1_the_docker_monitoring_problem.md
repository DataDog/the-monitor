*This post is part 1 in a 4-part series about monitoring Docker. [Part 2][part-2] explores metrics that are available from Docker, [part 3][part-3] covers the nuts and bolts of collecting those Docker metrics, and [part 4][part-4] describes how the largest TV and radio outlet in the U.S. monitors Docker. This article dives into some of the new challenges Docker creates for infrastructure monitoring.*

You have probably heard of Docker—it is a young container technology with a ton of momentum. But if you haven’t, you can think of containers as easily-configured, lightweight VMs that start up fast, often in under one second. Containers are ideal for microservice architectures and for environments that scale rapidly or release often. 

Docker is becoming such an important technology that it is likely that your organization will begin working with Docker soon, if it has not already. When we [explored real usage](https://www.datadoghq.com/docker-adoption/) data, we found an explosion of Docker usage in production: it has grown 5x in the last 12 months. 

Containers address several important operational problems; that is why Docker is taking the infrastructure world by storm. 

**But there is a problem:** containers come and go so frequently, and change so rapidly, that they can be an order of magnitude more difficult to monitor and understand than physical or virtual hosts. This article describes the Docker monitoring problem—and solution—in detail. 

We hope that reading this article will help you fall in love with monitoring containers, despite the challenges. In our experience, if you monitor your infrastructure in a way that works for containers—whether or not you use them—you will have great visibility into your infrastructure.

## What is a container?
A container is a lightweight virtual runtime. Its primary purpose is to provide software isolation. There are three environments commonly used to provide software isolation: 

1. physical machine *(heavyweight)* 
2. virtual machine *(medium-weight)*
3. container *(lightweight)*

A significant architectural shift toward containers is underway, and as with any architectural shift, that means new operational challenges. The well-understood challenges include orchestration, networking, and configuration—in fact [there](http://kubernetes.io/) [are](https://mesos.apache.org/) [many](https://github.com/coreos/fleet) [active](https://github.com/zettio/weave) [software](https://coreos.com/blog/introducing-rudder/) [projects](https://opsbot.com/advanced-docker-networking-pipework/) [addressing](https://coreos.com/using-coreos/etcd/) [these](https://www.digitalocean.com/community/tutorials/an-introduction-to-using-consul-a-service-discovery-system-on-ubuntu-14-04) [issues](https://zookeeper.apache.org/). 

The significant operational challenge of *monitoring* containers is much less well-understood.

## Monitoring is crucial 
![driving in the rain](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-03-container-monitoring/obscured-vision.png)
Running software in production without monitoring is like driving without visibility: you have no idea if you're about to crash, or how to stay on the road. 

[![diagram stack with no gap](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-03-container-monitoring/docker_p1_1.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-03-container-monitoring/docker_p1_1.png)

The need for monitoring is well understood, so traditional monitoring solutions cover the traditional stack: 

* application performance monitoring instruments your custom code to identify and pinpoint bottlenecks or errors
* infrastructure monitoring collects metrics about the host, such as CPU load and available memory

### Gap in the stack
[![diagram stack gap](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-03-container-monitoring/docker_p1_2.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-03-container-monitoring/docker_p1_2.png)

However, as we describe later in this post, containers exist in a twilight zone somewhere between hosts and applications where neither application performance monitoring nor traditional infrastructure monitoring are effective. This creates a blind spot in your monitoring, which is a big problem for containers and for the companies that adopt them.
![prod without container monitoring](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-03-container-monitoring/road-partial-view.png)

## A quick overview of containers
In order to understand why containers are a big problem for traditional monitoring tools, let's go deeper on what a container is and give some historical context.

### Original benefit: Security
Lightweight virtual runtimes have been around for a long time. Depending on the operating system, containers have been called different things: jail (BSD), zone (Solaris), cgroup (Linux), and more. As the name "jail" implies, containers were initially designed for security—they provided runtime isolation without the overhead of full virtualization. 

### Über-process or mini-host?
A container provides a way to run software in isolation, and it is neither a process nor a host—it exists somewhere on the continuum between. In the table below, note the  differences between processes and hosts; containers are often similar to both of them.

|                  | Process    | Container | Host        |
| :-----------: | :-----------: | :-----------: | :-----------: |
| Spec         | Source     | Dockerfile | Kickstart |
| On disk    | .TEXT       | /var/lib/docker | /       |
| In memory | PID | Container ID | Hostname | 
| In the network | Socket | veth*  | eth*            | 
| Runtime context | server core | host | data center | 
| Isolation | moderate: memory space, etc. | private OS view: own PID space, file system, network interfaces | full: including own page caches and kernel | 

#  Containers today
As mentioned, containers provide some (relative) security benefits with low overhead. But today there are two far more important reasons to use containers: they provide a pattern for scale, and an escape from dependency hell.

## Modern benefits
### A pattern for scale
Using a container technology like Docker, it is easy to deploy new containers programmatically using projects/services such as [Kubernetes](http://kubernetes.io/) or [ECS](https://www.datadoghq.com/blog/monitor-docker-on-aws-ecs/). If you also design your systems to have a [microservice architecture](http://martinfowler.com/articles/microservices.html) so that different pieces of your system may be swapped out or scaled up without affecting the rest, you've got a great pattern for scale. The system can be elastic; growing and shrinking automatically with load, and releases may be rolled out without downtime.

### Escape from dependency hell
[![Dependency Hell](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-03-container-monitoring/docker_p1_5-1.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-03-container-monitoring/docker_p1_5-1.png)

The second (and possibly more important) benefit of containers is that they free engineers from dependency hell. 

Once upon a time, libraries were compiled directly into executables. This was good until libraries grew too large and started taking up too much scarce RAM. 

To solve this problem, processes began to share libraries at runtime—only loading them into memory once. This reduced memory consumption, but created painful dependency problems when the necessary library was not available at runtime, or when two processes required different versions of the same library. The gates of dependency hell were opened, but the savings in memory made the tradeoff worthwhile.

Today there is a lot less memory pressure, but the legacy of dependency hell remains: the default way to build software today is with shared libraries. We kept the painful dependencies even when the original reason to use them subsided.

To partially address the pain created by dependencies, we created packages and package managers—apt, yum, rvm, virtualenv, etc.—to install groups of binaries that reliably work together. But packages required users to wait for upstream updates, which slowed the release cycle down so badly that crucial fixes and updates were held back for months or even years. This approach proved to be too slow for many companies. 

To address the slow-release problem, people started to bundle their code and dependencies into /opt. Then came tools like [omnibus](https://github.com/chef/omnibus) to make self-contained packages. And now here we are back, full circle, to static binaries.

Today, containers provide software engineers and ops engineers the best escape from dependency hell by packaging up an entire mini-host in a lightweight, isolated, virtual runtime that is unaffected by other software running on the same host—all with a manifest that can be checked in to git and versioned just like code.

## Container challenge: Massive operational complexity
We know that a container is basically a mini-host. Best practices for host ops are well-established, so you might suppose that container ops are basically the same—but they are not.
### Host proliferation
[![Host proliferation over time](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-03-container-monitoring/docker_p1_4.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-03-container-monitoring/docker_p1_4.png)

The diagram above shows how a standard application stack has evolved over the past 15 years. ("Off-the-shelf" could represent your J2EE runtime or your database.)

* Left: 15 years ago
* Middle: about 7 years ago, virtualization with a service like EC2 gained wide adoption. This evolution allowed better resource utilization and near-instant host provisioning, but for an engineer few things changed
* Right: today a containerized stack running on virtualized hardware is gaining popularity
 
From our vantage point at Datadog, we receive data from hundreds of thousands of hosts, which allows us to measure how many containers are running on each host in the wild today. In 2015, we're seeing that the median Docker-adopting company [runs four containers simultaneously](https://www.datadoghq.com/docker-adoption/#7) on each host. Given that containers tend to be shorter-lived than traditional hosts, the median VM runs nine containers in its life.

### Metrics Explosion
Before containers, you might monitor 150 metrics per Amazon EC2 host:

| Component        | # Metrics |
| :-----------: |:-------------:|
| OS (e.g. Linux)      | 100 |
| Off-the-shelf component | 50 |
| **Total** | **150** |

Now let's add containers to the stack. For each container, assume you collect 50 metrics from the container itself, plus another 50 metrics reported by an off-the-shelf component running in the container. (This is a conservative number, as we see our customers collect many more.) In that case we would add 100 new metrics per container. So the number of metrics we will collect is: 

OS + (Containers per host \* (Container + Off-the-shelf)) =  
100 + (4 \* (50 + 50)) =  **500 metrics per host**

![Metrics explosion: 100 hosts, 50,000 metrics](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-03-container-monitoring/docker_p1_5.png)

### Change acceleration 
But it is not quite that simple.

The lifetime of a host is much longer than that of a container—[4x longer](https://www.datadoghq.com/docker-adoption/#8) on average. Rather than having a mix of short-lived and long-lived EC2 instances with median uptime measured in days, weeks or months, instead your median uptime for containers will be measured in minutes or hours.

To make matters more complex, new versions of containers are created and ready to deploy as fast as you can git commit. You'll find yourself rotating your container fleet on a daily basis. 

To manage this, you'll likely want to use [Kubernetes](http://kubernetes.io/) or [AWS ECS](https://aws.amazon.com/ecs/) to move from manual, imperative provisioning to autonomic, declarative provisioning. This allows you to say, for example, "I need one container of type X per instance per zone, at all times," and your scheduler will make sure this is always the case. This kind of automation is necessary for modern container architectures, but opens the door to fresh new kinds of chaos.

In summary, with containers you'll be doing **a lot more, a lot faster** and you will need a modern monitoring solution to be prepared for this new reality.

## Host-centric monitoring
![Ptolemaic astronomy diagram](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-03-container-monitoring/ptolemaic-astronomy.png)

If your monitoring is centered around hosts, your world looks like Ptolemaic astronomy: complicated. It's pretty hard to account for the movement of planets this way.

Moving to a cloud environment forces many companies to rethink host-centric monitoring because instances come and go, and different groups within their organization spin up new stacks with little advance notice.

Whether or not you are using the cloud, if you add containers to your stack, your world gets much, much more complex. In fact, it gets so complex that host-centric monitoring tools simply can't explain your system, and you'll be left with two choices:

1. Treat containers as hosts that come and go every few minutes. In this case your life is miserable because the monitoring system always thinks half of your infrastructure is on fire.
2. Don't track containers at all. You see what happens in the operating system and the app, but everything in the middle is a gap, as discussed earlier.

If you're planning to monitor containers the same way as you've monitored hosts before, you should expect a very painful ride.

## Goal: Simplify monitoring
![Copernican Astronomy](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-03-container-monitoring/copernican-astronomy.png)
Instead we need a new approach, one that does not treat everything as a host.

The picture above represents Copernican astronomy. Compared with putting the earth at the center of the universe, Copernicus's radical suggestion is strikingly clear and simple.

If you forget about hosts and recenter your monitoring around layers and tags, the complexity will fall away and your operations will be sane and straightforward.

### Layers
[![Monitoring the stack in layers](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-03-container-monitoring/docker_p1_6.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-03-container-monitoring/docker_p1_6.png)

#### No Gaps
To avoid driving blind, you want your entire stack to be monitored from the top to the bottom, without gaps. If you're building on EC2, you probably use CloudWatch to monitor the VMs, infrastructure monitoring in the middle, and application performance monitoring at the top to measure throughput and help pinpoint problem areas in your code.

#### One timeline
[![Correlating metrics across the stack](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-03-container-monitoring/stack-infra.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-03-container-monitoring/stack-infra.png)

For monitoring layers to work, the key is that you must be able to see what's happening across the layers simultaneously, and determine how problems in one part of the stack ripple to the rest of the stack. For example, if you see slow response times in your application, but can't tell that it is being caused by a spike in IO at the VM layer, then your monitoring approach isn't helping you solve your problem.

### Tags
[![AWS tags](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-03-container-monitoring/tags-console.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-03-container-monitoring/tags-console.png)

To effectively monitor containers, you also need to tag (label) your containers. The good news is that you probably already use tags through AWS or server automation tools.

By centering your monitoring universe on tags, you can reorient from being imperative to declarative, which is analogous to how auto-scaling groups or Docker orchestration works. Rather than instructing your system to monitor a particular host or container, you can instruct your system to monitor everything that shares a common property (tag)—for example, all containers located in the same availability zone.

Tags allow you to monitor your containers with powerful queries such as this (tags are bold):
> Monitor all Docker containers running **image web**
> in region **us-west-2** across **all availability zones**
> that use more than 1.5x the average memory on **c3.xlarge**

With queryable tags you'll have a powerful system that makes monitoring your highly dynamic, container-based architecture straightforward and effective.

## Conclusion
Because containers provide both an escape from software dependency hell and scaffolding for scalable software architectures, they are already becoming increasingly common in production.

However, containers are typically used in large numbers and have a very short half-life, so they can easily increase operational complexity by an order of magnitude. Because of this, today many stacks that use containers do not monitor the containers themselves. This creates a huge blind spot and leaves the systems vulnerable to downtime.

Therefore:

1. **Monitor all layers of your stack** together, so that you can see what is happening everywhere, at the same time, with no gaps
2. **Tag your containers** so that you can monitor them as queryable sets rather than as individuals

With these guidelines in place, you should be ready for a painless containerized future. 

[Part two][part-2] of this series provides details about the key metrics that are available from Docker.

- - -

*Source Markdown for this post is available [on GitHub][markdown]. Questions, corrections, additions, etc.? Please [let us know][issues].*

[markdown]: https://github.com/DataDog/the-monitor/blob/master/docker/the_docker_monitoring_problem.md
[issues]: https://github.com/datadog/the-monitor/issues
[part-2]: https://www.datadoghq.com/blog/how-to-monitor-docker-resource-metrics/
[part-3]: https://www.datadoghq.com/blog/how-to-collect-docker-metrics
[part-4]: https://www.datadoghq.com/blog/iheartradio-monitors-docker/