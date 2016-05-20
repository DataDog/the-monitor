# 8 surprising facts about real Docker adoption

!["8 surprising facts about real Docker adoption" hero image](https://www.datadoghq.com/wp-content/themes/datadog/assets/images/dockerhero-new.png)

With thousands of companies using Datadog to track their infrastructure, we can see software trends emerging in real time. Today we're excited to share what we can see about true Docker adoption—no hype, just the facts.

Docker is probably the most talked-about infrastructure technology of 2015. We started this project to investigate how much Docker is used in production, and how fast real adoption is growing. We found the answers to these questions—and more that we discovered along the way—to be fascinating.

Our research was based on a sample of 7,000 companies and tracks real usage, not just anecdotally-reported usage. As far as we know, this is the largest and most accurate review of Docker adoption that has ever been published.

Throughout this article we refer to companies' adoption status: "adopted", "dabbling", or "abandoned". Our method for determining adoption status is described in the [Methodology](https://www.datadoghq.com/docker-adoption/#methodology) section below.

----- 

ONE<a name="1"></a>

----

!["Real Docker adoption is up 5x within one year" image badge](https://www.datadoghq.com/wp-content/themes/datadog/assets/images/badges_1.png)

## Real Docker Adoption Is Up 5x in One Year
At the beginning of September 2014, 1.8 percent of Datadog's customers had adopted Docker. One year later that number has grown to 8.3 percent. That's almost 5x growth in 12 months. 

![Docker adoption graph showing adoption up 5x over the last year](https://www.datadoghq.com/wp-content/themes/datadog/assets/images/graph_1-3.png)

["Tweet this"](https://twitter.com/intent/tweet?text=Real%20%23docker%20adoption%20is%20up%205x%20in%20one%20year.%20@datadoghq%20research%3A%20http%3A//dtdg.co/dckr-adopt%231%20https%3A//twitter.com/dd_docker/status/659048053505179649/photo/1&)

----

TWO<a name="2"></a>

----

!["Docker Now Runs on 6% of the Hosts We Monitor" image badge](https://www.datadoghq.com/wp-content/themes/datadog/assets/images/badges_2.png)

## Docker Now Runs on 6% of the Hosts We Monitor
This is an amazing fact: one year ago Docker had almost no market share, and now it's running on six percent of the hosts we monitor. Six percent may not sound high as an absolute number, but since we monitor [120+ different technologies](https://www.datadoghq.com/product/integrations/), it represents a meaningful part of our users' stacks. 

However, as seen below, growth as a percentage of hosts seems to have stalled last quarter. This could be seasonal; major infrastructure initiatives are often paused until after summer vacations. We will be interested to see what happens this quarter.

![Docker adoption graph showing adoption up 5x over the last year](https://www.datadoghq.com/wp-content/themes/datadog/assets/images/graph_1-3.png)

["Tweet this"](https://twitter.com/intent/tweet?text=Docker%20now%20runs%20on%206%25%20of%20the%20hosts%20@datadoghq%20monitors.%20More%20on%20%23docker%20adoption%3A%20http%3A//dtdg.co/dckr-adopt%232%20https%3A//twitter.com/dd_docker/status/659048037742964736/photo/1&)

---- 

THREE<a name="3"></a>

----

!["Larger Companies Are the Early Adopters" image badge](https://www.datadoghq.com/wp-content/themes/datadog/assets/images/badges_3.png)

## Larger Companies Are the Early Adopters
This one bucks the stereotype that larger companies are slower to move. The more hosts a company uses, the more likely it is to have tried Docker, and the more likely it is to be have adopted Docker. This fact is particularly surprising since the more hosts a company uses, the higher the number of Docker containers the company must use to be considered an “adopter”. As discussed in [Methodology](https://www.datadoghq.com/docker-adoption/#methodology) below, this finding is resilient to different infrastructure-size segmentation thresholds.

![Docker adoption graph decomposed by infrastructure size](https://www.datadoghq.com/wp-content/themes/datadog/assets/images/graph_3-4.png)

["Tweet this"](https://twitter.com/intent/tweet?text=Who%20are%20the%20early%20Docker%20adopters%3A%20smaller%20or%20larger%20co%27s%3F%20This%20may%20surprise%20you%3A%20http%3A//dtdg.co/dckr-adopt%233%20%23docker%20https%3A//twitter.com/dd_docker/status/659048006470246400/photo/1&)

---- 

FOUR<a name="4"></a>

----

!["2/3 of Companies That Try Docker Adopt It" image badge](https://www.datadoghq.com/wp-content/themes/datadog/assets/images/badges_4.png)

## 2/3 of Companies That Try Docker Adopt It
Good news for Docker just keeps coming. We were surprised to find how many companies who try Docker actually adopt it, and fast. Most companies who will adopt have already done so within 30 days of initial production usage, and almost all the remaining adopters convert within 60 days.

![Image showing 6 buildings, 4 of which have adopted Docker, 1 dabbler, 1 abandoner](https://www.datadoghq.com/wp-content/themes/datadog/assets/images/infographic_4-2.png)

["Tweet this"](https://twitter.com/intent/tweet?text=2/3%20of%20companies%20that%20try%20Docker%20adopt%20it.%20Details%20here%3A%20http%3A//dtdg.co/dckr-adopt%234%20%23docker%20via%20@datadoghq%20research%20https%3A//twitter.com/dd_docker/status/659047973964398592/photo/1&)

---- 

FIVE<a name="5"></a>

----

!["Users Triple the Number of Containers They Use within 5 Months" image badge](https://www.datadoghq.com/wp-content/themes/datadog/assets/images/badges_5.png)

## Users Triple the Number of Containers They Use within 5 Months
Both adopters and dabblers approximately triple the average number of running containers they have in production between their first and sixth month of use. This phenomenal increase in usage—even amongst dabblers—is great news for Docker.

![An image showing a stork making 5 stacks of containers, the first has two containers, the last has 6](https://www.datadoghq.com/wp-content/themes/datadog/assets/images/infographic_5-01.png)

["Tweet this"](https://twitter.com/intent/tweet?text=Avg%20co%20triples%20its%20number%20of%20Docker%20containers%20in%205%20months.%20More%20on%20%23docker%20adoption%3A%20%20http%3A//dtdg.co/dckr-adopt%235%20https%3A//twitter.com/dd_docker/status/659047954347630593/photo/1&)


---- 

SIX<a name="6"></a>

----

!["The Most Widely Used Images Are Registry, NGINX, and Redis" image badge](https://www.datadoghq.com/wp-content/themes/datadog/assets/images/badges_6.png)

## The Most Widely Used Images Are Registry, NGINX, and Redis
The most common technologies running in Docker are:

* **Registry**: Fully 25% of companies running Docker are using Registry, presumably instead of Docker Hub.
* **NGINX**: Docker is being used to contain a lot of HTTP servers, it seems. It is interesting that Apache (httpd) didn’t make the top 10.
* **Redis**: This popular in-memory key/value data store is often used as an in-memory database, message queue, or cache.
* **Ubuntu**: Still the default to build images.
* Logspout: For collecting logs from all containers on a host, and routing them to wherever they need to go.
* **MongoDB**: The widely-used NoSQL datastore.
* **Elasticsearch**: Full text search.
* **CAdvisor**: Used by Kubernetes to collect metrics from containers.
* **MySQL**: The most widely used open source database in the world.
* **Postgres**: The second-most widely used open source database in the world. Adding the Postgres and MySQL numbers, it appears that using Docker to run relational databases is surprisingly common.


![Bar chart showing the relative adoption percentages of different technologies on Docker](https://www.datadoghq.com/wp-content/themes/datadog/assets/images/graph_6-01.png)

["Tweet this"](https://twitter.com/intent/tweet?text=The%20top-10%20most-used%20%23docker%20images%20are%20Registry%2C%20NGINX%2C%20Redis...%20http%3A//dtdg.co/dckr-adopt%236%20via%20@datadoghq%20research%20https%3A//twitter.com/dd_docker/status/659047930385596416/photo/1&)

---- 

SEVEN<a name="7"></a>

----

!["Docker Hosts Often Run Four Containers at a Time" image badge](https://www.datadoghq.com/wp-content/themes/datadog/assets/images/badge_7.png)

## Docker Hosts Often Run Four Containers at a Time 
The median company that adopts Docker runs four containers simultaneously on each host. This finding seems to indicate that Docker is in fact commonly used as a lightweight way to share compute resources; it is not solely valued for providing a knowable, versioned runtime environment.

![Image showing four containers](https://www.datadoghq.com/wp-content/themes/datadog/assets/images/infographic_7-new.png)

["Tweet this"](https://twitter.com/intent/tweet?text=Fact%3A%20The%20avg%20Docker%20host%20runs%20four%20containers%20at%20a%20time.%20More%20@datadoghq%20research%3A%20http%3A//dtdg.co/dckr-adopt%237%20%23docker%20https%3A//twitter.com/dd_docker/status/659047898827595776/photo/1&)

----

EIGHT<a name="8"></a>

----

!["VMs Live 4x Longer Than Containers" image badge](https://www.datadoghq.com/wp-content/themes/datadog/assets/images/badge_8.png)

## VMs Live 4x Longer Than Containers 
At companies that adopt Docker, containers have an average lifespan of 3 days, while across all companies, traditional and cloud-based VMs have an average lifespan of 12 days.

As discussed in fact [#7](#7), it is common to run 4 containers per host simultaneously. So you might expect that the median VM would run 16 containers total in its lifetime (4 generations of 4 simultaneous containers). But due to uneven distributions, the median VM actually runs 9 containers in its life.

Containers' short lifetimes and increased density have significant implications for infrastructure monitoring. They represent an order-of-magnitude increase in the number of things that need to be individually monitored. Monitoring solutions that are host-centric, rather than role-centric, quickly become unusable. We thus expect Docker to continue to drive the sea change in monitoring practices that the cloud began several years ago.

![Graph decay curve of host and container lifespans](https://www.datadoghq.com/wp-content/themes/datadog/assets/images/graph_8-01.png)

["Tweet this"](https://twitter.com/intent/tweet?text=Fact%3A%20VMs%20live%204x%20longer%20than%20Docker%20containers%2C%20on%20avg.%20More%20@datadoghq%20research%3A%20http%3A//dtdg.co/dckr-adopt%238%20%23docker%20https%3A//twitter.com/dd_docker/status/659041172300632064/photo/1&)

----

# METHODOLOGY

## Population

As noted in the introduction, we compiled usage data from a sample of 7,000 companies, so this is probably the largest and most accurate review of Docker adoption that has been published to date. However, Datadog's customers skew toward "early adopters" and toward companies that take their software infrastructure seriously. All the results in this article are biased by the fact that the data comes from our customers, an imperfect sample of the entire global market. Caveat lector.

## Averages

When we talk about average numbers within our customer base (for example, the average container lifespan) we are not actually talking about the mean value within the population. Rather we compute the average for each customer individually, and then report the median customer’s number. We found that when we took a true average, results were unduly skewed by unusual Docker practices employed by relatively few companies. For example, using a container as a queueable unit of work could cause individual companies to use thousands of containers per hour.


## Adoption Segments

This article categorizes companies as Docker "adopters", "dabblers", and "abandoners". Each company is recategorized at the end of each month, based on their Docker activity that month.

* **Adopter:** the average number of containers running during the month was at least 50% the number of distinct hosts run, or there were at least as many distinct containers as distinct hosts run during the month.
* **Dabbler:** used Docker during the month, but did not reach the “adopter” threshold.
* **Abandoner:** a currently active company that used Docker in the past, but hasn't used it at all in the last month.

Note that the adoption-segmentation thresholds are not derived from a natural grouping within the data; the data covers a continuous spectrum of use. Rather we used numbers that we felt would be intuitively meaningful to our readers.

Interestingly, the findings in this article are surprisingly resilient to different adoption-segmentation thresholds. For example, regardless of whether the adopter threshold is lower (25% containers on average, or 0.75x distinct containers compared to hosts) or higher (75% containers on average, or 1.5x distinct containers compared to hosts), most findings are unaltered:

* **Fact #1:** Real adoption is still up 5x in one year.
* **Fact #2:** Adoption segmentation is not relevant to these findings.
* **Fact #3:** Large companies are still 2–4x more likely than smaller companies to be Docker adopters or dabblers. Relative to one another, the graphs are almost unchanged.
* **Fact #4:** Findings are almost unaltered: adoption percentage changes only by ±3%.
* **Fact #5:** Adopters still triple their container use between month 1 and month 6.
* **Fact #6:** Adoption segmentation is not relevant to these findings.
* **Facts #7, 8:** Results are not altered.

We also ran this analysis with absolute-usage thresholds, using segmentation rules such as “adopters had at least 20 containers running on average during the month”. While most of our findings were surprisingly similar (almost exactly the same, in fact), this strategy made it too likely that we would consider small companies to be dabblers when in fact a large percentage of their infrastructure was running Docker.

## Counting

Containers running only the Datadog Agent were excluded from this investigation, so Docker hosts that were only running the Agent were also excluded.

## Fact #1

We thought maybe we were seeing such a large increase in Docker use on Datadog precisely because Datadog is good at monitoring Docker. Maybe new Docker growth was fueled by new customers who needed Docker monitoring and came to Datadog specifically for that purpose. However, when we created cohorts of longtime Datadog customers, we saw almost identical adoption percentages.

## Fact #2

For each technology we monitor, we exclude from this calculation the organizations that are in the top 1% of its users. In other words, if a small number of companies use a particular technology in an unusual way, and use it quite heavily, they are excluded from the calculation.

Note, too, that the same basic shape of the “Percent hosts running Docker” graph persists even if we limit our population to Docker-using companies, or if we exclude the top 5%, 10%, or 25% of the Docker-using companies. There is a distinct flattening of the percent of hosts running Docker during the last quarter.

## Fact #3

This finding is resilient to different infrastructure-size cut-points. Several different cut-points are below. The middle set of cut-points were used for this article.

| Infrastructure size cut-points | Percent of companies that have tried Docker |
|--------------------------------|---------------------------------------------|
| 1–49, 50–99, 100+              | 11%, 22%, 43%                               |
| 1–99, 100–499, 500+            | 11%, 28%, 56%                               |
| 1–249, 250-749, 750+           | 12%, 37%, 58%                               |


----

#SIGN UP
##Get Started with Datadog

To monitor your Docker environment, your own [custom metrics](http://docs.datadoghq.com/guides/metrics/), or any of Datadog's other [120+ pre-built integrations](https://www.datadoghq.com/product/integrations/), sign up for a free 14-day trial account below.