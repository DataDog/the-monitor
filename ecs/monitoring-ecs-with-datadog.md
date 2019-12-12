# Monitoring ECS with&nbsp;Datadog


As we explained in [Part 1][part1], it's important to monitor task status and resource use at the level of ECS constructs like clusters and services, while also paying attention to what's taking place within each host or container. In this post, we'll show you how Datadog can help you:

- Automatically [collect metrics](#from-ecs-to-datadog) from every layer of your ECS deployment
- Track data from your ECS cluster, plus its hosts and running services in [dashboards](#get-comprehensive-visibility-with-datadog-dashboards)
- Visualize your ECS deployment with the [container map](#visualize-your-ecs-deployment-with-the-host-map-and-container-map)
- Detect services running on your ECS cluster [automatically](#keep-up-with-ecs-task-placement-using-autodiscovery)
- Get real-time insights into the health and performance of your ECS [services](#troubleshoot-your-ecs-applications-with-distributed-tracing-and-apm) and [processes](#get-inside-your-ecs-deployment-with-live-containers-and-live-processes)
- Collect and analyze your [ECS logs](#get-context-by-processing-and-analyzing-ecs-logs) to show trends beyond those visible to CloudWatch
- [Create alerts](#ensure-ecs-cluster-availability-with-datadog-alerts) to track potential issues with your ECS cluster

## From ECS to Datadog
Datadog gathers information about your ECS clusters from two sources. First, Datadog [queries][dd-cloudwatch] CloudWatch for metrics and tags from ECS and any other AWS services you'd like to monitor. Second, you can deploy the [Datadog Agent][dd-agent] to your ECS clusters to gather metrics, request traces, and logs from Docker and other software running within ECS, as well as host-level resource metrics that are not available from CloudWatch (such as [memory][dd-ec2]).

In this section, we'll show you how to set up Datadog to collect ECS data from both of these sources—first, by configuring the AWS integration, then by installing the Datadog Agent on your clusters. If you're new to Datadog, you can follow along with this post by signing up for a <a href="#" class="sign-up-trigger">free trial</a>.

### Set up Datadog's AWS integration
Datadog's [AWS integration][dd-ecs-integration] automatically collects ECS metrics from CloudWatch—and it expands on those metrics by querying the ECS API for additional information, including ECS [events][dd-ecs-events] and tags, and the status of container instances, tasks, and services. To set up [Datadog's AWS integration][dd-cloudwatch-install], you'll need to delegate an AWS Identity and Access Management ([IAM][aws-iam]) role that gives Datadog read-only access to ECS (and any other services you'd like to monitor), [as specified in our documentation][dd-ecs-iam].

In the [AWS integration tile][dd-aws-tile], add the name of this IAM role, and make sure to check the "ECS" box under "Limit metric collection". You should start to see metrics and events populating the out-of-the-box dashboard for ECS, making it possible to get full visibility into the health and performance of your cluster.

{{< img src="ecs-screenboard.png" caption="You can clone and customize this out-of-the-box dashboard for ECS to include data from Docker, other AWS services, and ECS logs." alt="You can clone and customize this out-of-the-box dashboard for ECS to include data from Docker, other AWS services, and ECS logs." popup="true" wide="true" >}}

### Deploying the Datadog Agent on ECS
The [Datadog Agent][dd-agent] is open source software that collects metrics, request traces, logs, and process data from your ECS environment, and sends this information to Datadog. The Agent runs inside your ECS cluster, gathering resource metrics as well as metrics from containerized web servers, message brokers, and other services.

You can [deploy the containerized Datadog Agent to your ECS cluster][dd-agent-install] in the same way as any other container: within the `containerDefinitions` object of an ECS task. The definition will vary based on whether the task is running in the Fargate or the EC2 launch type, as explained below.

#### Deploying the Agent in the Fargate launch type
If you're using the Fargate launch type, add the following object to the `containerDefinitions` array within a new or existing task definition:

```
{
  "name": "datadog-agent",
  "image": "datadog/agent:latest",
  "environment": [
    {
      "name": "DD_API_KEY",
      "value": "<YOUR_DATADOG_API_KEY>"
    },
    {
      "name": "ECS_FARGATE",
      "value": "true"
    }
  ]
}
```

You'll need to include two objects within the `environment` array: one that specifies your Datadog API key (available [in your account][datadog-api-key]) and another that sets `ECS_FARGATE` to `true`.

After you've declared the Datadog Agent container within a task definition, name the task within a service to run it automatically. To enable Datadog's [Fargate integration][dd-fargate-integration], navigate to the Datadog integrations view and click "Install Integration" in the [Fargate tile][dd-fargate-tile]. Once the task that includes the Datadog Agent reaches a `RUNNING` status, the Agent has begun to send metrics to Datadog.

The [Fargate integration][dd-fargate-integration] complements the ECS integration, gathering system metrics from each container in your Fargate cluster. This makes it easier to [monitor Docker containers][part2-docker] within Fargate, taking away the need to write your own scripts to query the ECS [task metadata endpoint][ecs-task-metadata] and process the response to track container-level resource metrics.

#### Deploying the Agent in the EC2 launch type
Deploying the Agent to your EC2 container instances is similar: add a task definition that names the container image of the Agent. You'll find the [JSON][dd-task-ec2-json] for the Agent container definition in our [documentation][dd-task-json-doc].

You'll notice that this container definition looks slightly different from what we used with Fargate, mainly in that it specifies volumes and mount points. Once you've defined a task that includes the Datadog Agent, create a service that runs it. We recommend [running the Datadog Agent as an ECS daemon task][dd-agent-daemon] to make sure the Agent deploys to, and can collect system metrics from, each EC2 instance in your cluster.

## Get comprehensive visibility with Datadog dashboards
Once you've enabled Datadog's AWS integration, you'll have access to an [out-of-the-box dashboard][dd-ecs-oobd] (see [above](#from-ecs-to-datadog)) that provides detailed information about your ECS clusters, including the status of your deployments, cluster-level resource utilization, and a live feed of ECS events. You can also clone your ECS dashboard and add graphs of Docker metrics to see how the health and performance of your containers correlates with that of the tasks running them. And if you want to drill into issues with your ECS container instances, or a specific container, you can turn to the out-of-the-box dashboards for [EC2][dd-ec2-dash] and [Docker][dd-docker-dash].

{{< inline-cta text="Use Datadog to gather and visualize real-time data from your ECS clusters in minutes." btn-text="Try it free" data-event-category="Signup" signup="true" >}}

Datadog pulls tags from Docker and Amazon CloudWatch automatically, letting you group and filter metrics by `ecs_cluster`, `region`, `availability_zone`, `servicename`, `task_family`, and `docker_image`. This makes it possible to, for instance, monitor ECS CPU utilization for a single cluster, then drill in to see how each Docker container contributes—a view that's not available with [ECS CloudWatch metrics alone][ecs-cloudwatch-metrics].

{{< img src="ecs-tags-dash2.png" alt="Dashboard of CPU utilization across Docker images and ECS tasks." >}}

In addition to Docker, you can use Datadog dashboards to track [all the AWS technologies][dd-aws] running alongside ECS.

## Visualize your ECS deployment with the host map and container map
To get an overview of your ECS infrastructure as a collection of EC2 hosts or Docker containers, you can use Datadog's two map views, the container map and host map. Here you'll see how many members are in your cluster, how they are organized, and how much variation they show for any metric. You can then get a quick read into the health and performance of your ECS cluster.

The Datadog host map lets you [filter tags][dd-host-map-filter], making it possible to show all the EC2 instances running within ECS clusters (as you can see below). You can then group by EC2 instance type, showing whether any part of your cluster is over- or underprovisioned for a given resource.

{{< img src="ecs-host-map.png" alt="Host map organized by EC2 instance type for all ECS clusters reporting to a single Datadog account." popup="true" >}}

The [container map][container-map] has all the functionality of the host map, but displays containers rather than hosts. Since Datadog pulls tags from CloudWatch, you can use the same categories that identify parts of your ECS cluster to organize the container map. For example, since ECS tasks are tagged by version, we've used the `task_family` and `task_version` tags to see how many containers in a single task family (i.e., containers running any version of a specific task definition) are still outdated, and whether that has impacted CPU utilization in our cluster.

{{< img src="ecs-container-map.png" alt="Container map organized by ECS task definition version." popup="true" >}}

## Keep up with ECS task placement using Autodiscovery
What we've called the [Docker monitoring problem][dd-docker-problem] is just as true for ECS: containers spin up and shut down dynamically as ECS schedules tasks, making it a challenge to locate your containers, much less monitor them. With [Autodiscovery][dd-autodiscovery], the Datadog Agent can detect every container that enters or leaves your cluster, and configure monitoring for those containers—and the services they run.

The Datadog Agent includes Autodiscovery configuration details for more than a dozen technologies out of the box (including Apache, MongoDB, and Redis). You can configure Autodiscovery to add your own [check templates][dd-ad-check-templates] for other services using three [Docker labels][dd-ad-docker-labels].


| Label | What it specifies |
|:-----|:-----|
| `com.datadoghq.ad.check_names` | The integrations to configure, corresponding with the names of individual checks (as given in the Agent's [configuration directory][dd-agent-config-dir]). |
| `com.datadoghq.ad.init_configs` | Integration-specific options, similar to the `init_config` key within **/etc/datadog-agent/conf.d/\<CHECK_NAME\>/*.yaml**. If this is blank in the example configuration file for a given check (**conf.yaml.example**), leave it blank here |
| `com.datadoghq.ad.instances`| Describes the host and port where a service is running, often using [template variables][dd-ad-template-vars]|

In your ECS task definitions, you'll need to add these labels to the `dockerLabels` [object][ecs-task-def-params-labels] in the definition of each container you'd like to monitor.

The Datadog Agent will look for containers in your ECS clusters that include the names of Datadog integrations in their [names, image names, or labels][dd-ad-labels-names], and configure the corresponding checks based on the labels you've added earlier (or the out-of-the-box templates).

In the example below, we're using ECS tags to track Redis metrics across three tasks in a Fargate cluster. Lines that begin partway along the x-axis represent new Redis containers that Autodiscovery has detected and started tracking. We've also ranked memory usage across the containers that are running our Redis service.


{{< img src="fargate-dash.png" caption="Redis metrics per instance within a single Fargate cluster." alt="Redis metrics per instance within a single Fargate cluster." >}}


## Troubleshoot your ECS applications with distributed tracing and APM

We've shown you how to use Datadog to monitor every layer of your ECS deployment. But in order to effectively troubleshoot your applications, you also need to get visibility into runtime errors, high response latency, and other application-level issues. Datadog APM can help you optimize your applications by tracing requests across the containers, hosts, and services running in your ECS cluster.

ECS is well suited to complex, scalable applications, and APM lets you cut through the complexity to discover issues and opportunities for optimization. With [Watchdog][dd-watchdog], you can see whether any services running your application have unexpected changes in throughput, error rates, or latency, without having to set up alerts manually. And because the Agent receives traces from every component of your ECS infrastructure, you can monitor your applications even as tasks terminate and re-launch.

### Set up APM on ECS

Enabling your application to send traces to Datadog requires two steps: instrumenting your application to send traces and configuring your Datadog Agent container to receive them.

#### Instrumenting your application code
You can instrument your application for APM by using one of our [tracing libraries][dd-apm-setup], which include support for auto-instrumenting popular languages and frameworks. You can also send custom traces to Datadog with a few method calls. And with [distributed tracing][dd-distributed-tracing], Datadog can follow requests no matter which  containers, tasks, and hosts they've passed through in your ECS network.

The example below shows you how to instrument an application based on the [tutorial for Docker Compose][docker-compose-tutorial], which runs two containers: [Redis][ddtrace-redis] and a [Flask][ddtrace-flask] application server. The Flask application imports the library, `ddtrace`, which [sends traces][dd-apm-python] to the Datadog Agent. To make `ddtrace` available to your application, simply add it to your **requirements.txt** file and include this command in the Dockerfile for your application container:

```
RUN pip install -r requirements.txt
```

The steps will vary depending on the language you're using, but usually involve importing a Datadog tracing library and declaring traces within your code (consult our [documentation][dd-apm-setup] for what to do in your environment).

Our application code looks like this:

```no-minimize
import time
import redis
from flask import Flask
import blinker as _ # Required for instrumenting Flask
from ddtrace import tracer, Pin, patch
from ddtrace.contrib.flask import TraceMiddleware

# Required for instrumenting tracing in Redis
patch(redis=True)

app = Flask(__name__)

cache = redis.StrictRedis(host='localhost', port=6379)

traced_app = TraceMiddleware(app, tracer, service="paulg-ecs-demo-app")

# Pin, or "Patch Info," assigns metadata to a connection for tracing.
Pin.override(cache, service="paulg-ecs-demo-redis")

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/')
def hello():
    count = get_hit_count()
    return 'Hello World! I have been seen {} times.\n'.format(count)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="4999", debug=False)

```

In Datadog APM, you can use a different `service` tag to represent each microservice, database, web server—anything that receives requests and issues a response. Note that `service` is a [reserved tag][dd-tag-collection] within Datadog APM, and is not the same thing as the `servicename` tag, which automatically gets added to certain ECS metrics as part of Datadog's ECS integration. In the example above, we assigned a service to our Flask application as an argument to the `TraceMiddleware` constructor, and to our Redis instance in our call to `Pin.override`.

Datadog APM categorizes services by their [environment][dd-apm-env] (assigned with the tag key `env`), which might represent your development or production environment, a demo project, or any scope you'd like to keep isolated. On the [services page][dd-services-page] within your Datadog account, you can use a dropdown menu to navigate between environments. By default, applications send traces with the environment tag, `env:none`. In our Python example, you could assign an `env:prod` tag [with the code][dd-apm-env-python]:

```
from ddtrace import tracer
tracer.set_tags({'env': 'prod'})
```
The `env` tag is one of many tags that can add valuable context to your distributed request traces. You can use `set_tags()` to associate all the code you are instrumenting with a specific tag, such as `service`.

#### Editing your Datadog Agent task definition
Before the containerized Agent can accept traces from ECS tasks and forward them to your Datadog account, you'll need to make two changes to the task definition that includes the containerized Datadog Agent.

First, you'll want to make sure the Agent is listening on a port from which it can receive traces ([port 8126][dd-apm-port], by default). In this case, we deployed a task in the Fargate launch type using the `awsvpc` network mode, and included the following `portMappings` object within the definition for our Agent container (the configuration would be the same for the EC2 launch type, as long as the Agent container can receive traces on port 8126):

```
"portMappings": [
        {
          "protocol": "tcp",
          "containerPort": 8126
        }
```

Next, you'll want to enable APM in your ECS cluster. Add the following environment variable to the `environment` object of the container definition for the Agent:

```
"environment": [
        {
          "name": "DD_APM_ENABLED",
          "value": "true"
        },
      ],

```

The Agent uses environment variables to set configuration details in ECS and other Dockerized environments. See the full list of available variables in our [documentation][dd-apm-docker]. Now that tracing is enabled and the Agent is running in a container deployed by your tasks, you should see traces from your application in Datadog.

### Latencies and request rates

Once you've set up Datadog APM, you can inspect individual request traces or aggregate them to get deeper insights into your applications. Datadog gives you a per-service summary of request rates, latencies, and error rates, so you can easily track the overall health and performance of different components within your application. Below, you can see high-level metrics for the services within your infrastructure, such as the `paulg-ecs-demo-app` application we instrumented earlier, as well as other microservices it makes requests to.

{{< img src="all-services.png" alt="Service dashboard for an application running on ECS." >}}

If you click on a service, you'll see a dashboard that displays key metrics like request throughput and error rates. You can also add each of these graphs to any other dashboard, making it straightforward to compare application-level metrics with data from ECS and other components of your infrastructure.


{{< img src="service-summary.png" alt="Datadog service dashboard for a single microservice." popup="true" >}}

You can also inspect a single trace to see how long a request has spent accessing different services, along with relevant metadata, host metrics, and ECS logs. You'll see application metrics from throughout your ECS deployment, regardless of the host, container, task, or service that generated them. And you can easily track the path of a single request, whether it remained within a single task or traveled between them. The flame graph below traces a request that involves three services within our ECS cluster: a web application (`paulg-ecs-demo-app`) that waits for responses from the service, `paulg-ecs-demo-publisher` (which is external to our Flask application) and our Redis instance, `paulg-ecs-demo-redis`.

{{< img src="flame-graph.png" alt="A flame graph of a request within an ECS cluster, including the option to view related metadata and ECS logs." popup="true" >}}

### The Service Map

ECS gives you a framework for organizing your applications into microservices, and leeway over how you [configure networking][ecs-network-mode] between containers, tasks, and (on EC2) container instances. Datadog's [Service Map][service-map] makes it easy to ensure that the web servers, databases, and other microservices within your ECS deployment are communicating properly, and that latency and errors are at a minimum.

Now that you've set up APM on your ECS cluster, you can use the Service Map with no additional configuration. The Service Map can help you make sense of your ECS network by showing you how data flows across all the components of your infrastructure, how services relate to one another, and how healthy their connections are.


{{< img src="service-map.png" alt="Example of the Service Map." >}}


## Get inside your ECS deployment with live containers and live processes
Once you've [deployed the containerized Datadog Agent][dd-live-containers-install], you can start tracking the health and status of your ECS containers in the [Live Container view][dd-live-containers]. Each graph displays real-time graphs of container resource metrics at two-second resolution. Below, we're examining two containers in the Live Container view: one running the ECS Container Agent and another running our web application. You can then use the facets within the sidebar—such as the "ECS Cluster" and "Region" facets we've selected below—to filter by tags.

{{< img src="live-containers-procs-ec2.png" alt="The Live Container view helps you visualize ECS container-level resource metrics in Datadog." popup="true" wide="true" >}}

If you [enable Live Processes][dd-live-processes] for your containers, you can also view CPU utilization and RSS (resident set size) memory for each process they run. To gather information about container-level processes, the Datadog Agent [requires access][dd-live-processes-setup] to the [Docker socket][docker-socket], which the Docker daemon uses to communicate with containers. Fargate does not provide direct access to the Docker daemon or socket, so the Agent can only track processes in ECS containers that use the EC2 launch type.

To configure Docker process monitoring, simply make two modifications to any task definition that includes the Datadog Agent. First, assign the environment variable `DD_PROCESS_AGENT_ENABLED` to `true`. Second, designate a volume for the system directory **/etc/passwd** (see our [documentation][dd-live-proc-docker]) and create a [bind mount][docker-bind-mount] to that volume. Once Datadog begins collecting process-level metrics, you can determine with greater precision why a container is using the resources that it is, and how this resource utilization has changed over time.

## Get context by processing and analyzing ECS logs

When running dynamic, containerized applications in ECS, it's important to be able to filter, aggregate, and analyze logs from all your services. You might want to investigate, for example, if a series of runtime errors is associated with a single application container image, or if new levels of resource reservation in a task definition are triggering errors on a specific EC2 instance.

Datadog can collect ECS logs from any containers in your clusters, and lets you group and filter logs to discover trends. There are two ways to configure Datadog to collect and process your ECS logs. In the first, the Datadog Agent sends logs directly from ECS containers running in an EC2-based cluster, bypassing CloudWatch Logs (and the additional billing the service entails), while also giving you more configuration options and access to logs from the ECS Container Agent. The second method works with either launch type, and uses a Lambda function to forward container logs from CloudWatch Logs to Datadog. In Fargate, since you're [restricted to CloudWatch Logs][ecs-task-def-logging], using this method is the only available option.


### Sending ECS logs from your EC2 instances
For tasks deployed with the EC2 launch type, you can configure the Agent to send your ECS logs directly from your EC2 cluster to Datadog. This option preserves all of your AWS-based tags and lets Datadog collect any logs from your container instances as well as from the ECS Container Agent.

Edit the task definition that includes the Datadog Agent container as explained in our [documentation][dd-logs-ecs-ec2], adding the required volume, mount point, and environment variables. You'll also want to edit the definitions for any containers from which you'd like to collect logs so that they use a log driver that writes to a local file—`json-file` does, for instance, while `awslogs` does not.

The containerized Datadog Agent will listen for logs from all of the containers on your container instances, including the ECS Container Agent, unless you opt to limit log collection to [specific containers][dd-logs-collection-filter]. There's nothing specific to ECS in this technique: since ECS containers are regular Docker containers, you can [customize][dd-logs-collection-docker] the way Datadog collects logs from them just as you can with any other container. This also means that logs from ECS containers have no one format—you can set up a [log processing pipeline][dd-logs-pipelines] to enrich your logs with metadata that Datadog can use for grouping, filtering, and analytics, regardless of how your logs are structured.

For example, you can create a new log processing pipeline to handle logs from the [ECS Container Agent][ecs-agent-logs]. This lets you correlate metrics from your ECS deployment with messages from the ECS Agent, such as changes in the status of particular tasks and notifications that ECS is removing unused images. When you create a pipeline, fill in the "Filter" field (see the image below) so the `image_name` attribute matches the name of the ECS Container Agent's [image][ecs-agent-container-name], `amazon/amazon-ecs-agent`.

{{< img src="log-pipeline-filter.png" alt="Setting up a processing pipeline for logs from the ECS Agent." >}}

The new pipeline will start processing logs into the following format.

{{< img src="ecs-agent-logs.png" alt="ECS logs for the Container Agent." popup="true" wide="true" >}}

You can then add log processing rules to the pipeline. For example, a [log status remapper][dd-logs-status-remapper] lets you use the log level (e.g., `INFO`) to group and filter your logs, letting you investigate only those logs with a certain severity.

### Using AWS Lambda to collect ECS logs from CloudWatch
Datadog provides a [custom AWS Lambda function][dd-logs-lambda-intro] that helps you automatically collect logs from any AWS service that sends logs to CloudWatch. The [Lambda][aws-lambda] function triggers when CloudWatch receives new logs within a particular [log group][cloudwatch-log-group], then sends the logs to Datadog so that you can visualize, analyze, and alert on them.

#### Update your task definition to publish ECS logs to CloudWatch Logs
To start collecting logs from ECS containers, you'll need to make sure that your tasks are publishing logs to AWS in the first place. Check whether each container definition has a `logConfiguration` object similar to the following:

```
"logConfiguration": {
  "logDriver": "awslogs",
  "options": <OPTIONS_OBJECT>
}
```

Setting the `logDriver` to `awslogs` directs the container to [send ECS logs to CloudWatch Logs][ecs-awslogs]. Later, we'll show you how to use the `options` object to customize the way ECS publishes logs to CloudWatch. When editing a container definition in the CloudWatch console, you can either specify the name of an existing CloudWatch log group, or check the box, "Auto-configure CloudWatch Logs," to automatically create a CloudWatch log group based on the name of the container's task definition (e.g., `/ecs/paulg-ecs-demo-app`). This configures AWS to forward all CloudWatch logs from the container to the specified log group. By default, your container will log the `STDOUT` and `STDERR` of the process that runs from its `ENTRYPOINT`.

#### Configure a Lambda function to send ECS logs to Datadog
The next step is to get AWS Lambda to send ECS logs from your CloudWatch log group to Datadog. If you've configured Datadog to collect logs from other AWS services, the process is identical. Create an AWS Lambda function and paste in the [code from our GitHub repo][dd-logs-lambda-code], as [described in our documentation][dd-logs-lambda-create], following our instructions to [configure your Lambda][dd-logs-lambda-code-configure] function.

Finally, [set the function to trigger][dd-logs-lambda-trigger] based on activity from your CloudWatch log group (the same log group you used to collect ECS container logs in your task definition). Your screen should resemble the following.


{{< img src="ecs-log-trigger.png" alt="Configuring a Lambda function to forward ECS logs to Datadog." popup="true" >}}

Now that you've configured the Lambda function to forward ECS logs from the appropriate log group to Datadog, you'll be able to access all of your logs automatically in the Datadog platform, even as tasks using that definition launch and terminate.

## Ensure ECS cluster availability with Datadog alerts
You can alert on every kind of ECS data that Datadog collects, from the status of tasks and services to the resource use of your containers and hosts. In the example below, we're using the `task_family` tag to alert on a certain frequency of error logs (500 over the course of five minutes) from the task hosting our application.

{{< img src="log-alerts.png" alt="Setting alerts on ECS logs." popup="true" >}}

At other times, you'll want to alert at the level of the ECS service. If you've configured a service to place multiple instances of a task definition, you can create an alert to ensure that the service is operating as expected. Below, we set up an alert that will trigger if the number of running containers within a single ECS service has decreased by two —which means that two containers have entered a `STOPPED` state—over the past hour. This way, you can find out if, say, an error in our application code has prevented containers in a newly placed task from starting.

{{< img src="dd-change-alert.png" alt="Setting alerts on changes in the number of running tasks in an ECS service." popup="true" >}}

You can also create a similar alert for `aws.ecs.running_tasks_count`, the number of tasks per container instance in the `RUNNING` state, to help ensure that our cluster remains available. Datadog lets you be flexible with how you use tags and choose data for setting alerts, letting you customize your alerting for whichever complex distributed system you deploy with ECS.

## Monitoring as dynamic as your ECS cluster
In this post, we've shown how Datadog can help address the challenges of monitoring ECS environments. We've also shown you how to use tags and built-in visualization features to track the health and performance of your clusters from any level of abstraction—across tasks, services, and containers—within the same view. And as tasks advance through their lifecycles, Datadog can monitor them in real time and alert you to any potential issues.

If you're new to Datadog, you can start collecting metrics, traces, and logs from ECS with a <a href="#" class="sign-up-trigger">14-day free trial</a>.

<br />
_We wish to thank our friends at AWS for their technical review of this series._

<!--sources-->

[aws-cloudwatch-pricing]: https://aws.amazon.com/cloudwatch/pricing/

[aws-iam]: https://aws.amazon.com/iam/

[aws-lambda]: https://aws.amazon.com/lambda/

[cloudwatch-log-group]: https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/Working-with-log-groups-and-streams.html

[container-map]: /blog/container-map/

[datadog-api-key]: https://app.datadoghq.com/account/settings#api

[ddtrace-flask]: http://pypi.datadoghq.com/trace/docs/web_integrations.html#flask

[ddtrace-py]: http://pypi.datadoghq.com/trace/docs/

[ddtrace-redis]: http://pypi.datadoghq.com/trace/docs/db_integrations.html#id12

[dd-ad-check-templates]: https://docs.datadoghq.com/agent/autodiscovery/?tab=docker#setting-up-check-templates

[dd-ad-docker-labels]: https://docs.datadoghq.com/agent/autodiscovery/?tab=docker#template-source-docker-label-annotations

[dd-ad-labels-names]: https://docs.datadoghq.com/agent/autodiscovery/?tab=docker#alternate-container-identifier-labels


[dd-ad-template-vars]: https://docs.datadoghq.com/agent/autodiscovery/?tab=docker#supported-template-variables

[dd-agent]: https://docs.datadoghq.com/agent/?tab=linux

[dd-agent-daemon]: https://docs.datadoghq.com/integrations/amazon_ecs/#run-the-agent-as-a-daemon-service

[dd-agent-config-dir]: https://docs.datadoghq.com/agent/guide/agent-configuration-files/?tab=agentv6#agent-configuration-directory

[dd-agent-install]: https://docs.datadoghq.com/integrations/amazon_ecs/?tab=nodejs#metric-collection

[dd-apm-docker]: https://docs.datadoghq.com/tracing/setup/docker/?tab=java

[dd-apm-ecs-task]: https://docs.datadoghq.com/integrations/amazon_ecs/#create-an-ecs-task

[dd-apm-env]: https://docs.datadoghq.com/tracing/getting_further/first_class_dimensions/?tab=python#environment

[dd-apm-env-python]: https://docs.datadoghq.com/tracing/getting_further/first_class_dimensions/?tab=python#environment

[dd-apm-port]: https://docs.datadoghq.com/tracing/setup/docker/?tab=java#tracing-from-the-host

[dd-apm-python]: https://docs.datadoghq.com/tracing/setup/python/

[dd-apm-setup]: https://docs.datadoghq.com/tracing/setup/

[dd-apm-setup-docker]: https://docs.datadoghq.com/tracing/setup/docker/

[dd-autodiscovery]: https://docs.datadoghq.com/agent/autodiscovery/?tab=docker

[dd-aws]: https://docs.datadoghq.com/integrations/amazon_web_services/

[dd-aws-tile]: https://app.datadoghq.com/account/settings#integrations/amazon_web_services

[dd-cloudwatch]: https://docs.datadoghq.com/integrations/amazon_web_services/#permissions

[dd-cloudwatch-install]: https://docs.datadoghq.com/integrations/amazon_web_services/#installation

[dd-docker-dash]: https://app.datadoghq.com/screen/integration/52/docker---overview

[dd-docker-labels-tags]: https://docs.datadoghq.com/agent/basic_agent_usage/docker/#tagging

[dd-docker-problem]: https://www.datadoghq.com/blog/the-docker-monitoring-problem/#docker-monitoring-is-crucial

[dd-ec2]: https://www.datadoghq.com/blog/monitoring-ec2-instances-with-datadog/

[dd-ec2-dash]: https://app.datadoghq.com/screen/integration/60/aws-ec2

[dd-ecs-events]: https://docs.datadoghq.com/integrations/amazon_ecs/#events

[dd-ecs-oobd]: https://app.datadoghq.com/screen/integration/82/aws-ecs

[dd-ecs-tile]: https://app.datadoghq.com/account/settings#integrations/amazon_ecs


[dd-fargate-integration]: https://docs.datadoghq.com/integrations/ecs_fargate/

[dd-fargate-tile]: https://app.datadoghq.com/account/settings#integrations/amazon_fargate

[dd-live-containers]: https://docs.datadoghq.com/graphing/infrastructure/livecontainers/

[dd-live-containers-install]: https://docs.datadoghq.com/graphing/infrastructure/livecontainers/#installation

[dd-live-proc-docker]: https://docs.datadoghq.com/graphing/infrastructure/process/#docker-process-collection

[dd-live-processes]: https://docs.datadoghq.com/graphing/infrastructure/process/?tab=docker

[dd-live-processes-setup]: https://docs.datadoghq.com/graphing/infrastructure/process/?tab=docker#installation

[dd-logs-collection-docker]: https://docs.datadoghq.com/logs/log_collection/docker/?tab=containerinstallation

[dd-logs-collection-filter]: https://docs.datadoghq.com/logs/log_collection/docker/?tab=containerinstallation#filter-containers

[dd-logs-ecs-ec2]: https://docs.datadoghq.com/integrations/amazon_ecs/#log-collection

[dd-logs-facets]: https://docs.datadoghq.com/logs/explorer/search/#facets

[dd-logs-fargate]: https://docs.datadoghq.com/integrations/ecs_fargate/#log-collection

[dd-logs-grok-parser]: https://docs.datadoghq.com/logs/processing/processors/#grok-parser

[dd-logs-lambda-code]: https://github.com/DataDog/dd-aws-lambda-functions/blob/master/Log/lambda_function.py

[dd-logs-lambda-intro]: https://docs.datadoghq.com/integrations/amazon_web_services/#create-a-new-lambda-function

[dd-logs-lambda-code-configure]: https://docs.datadoghq.com/integrations/amazon_web_services/#provide-the-code-and-configure-the-lambda

[dd-logs-lambda-create]: https://docs.datadoghq.com/integrations/amazon_web_services/#create-a-new-lambda-function

[dd-logs-lambda-trigger]: https://docs.datadoghq.com/integrations/amazon_lambda/#log-collection

[dd-logs-parsing-rules]: https://docs.datadoghq.com/logs/processing/parsing/

[dd-logs-pipelines]: https://docs.datadoghq.com/logs/processing/pipelines/

[dd-logs-processor]: https://docs.datadoghq.com/logs/processing/processors/

[dd-logs-remapper]: https://docs.datadoghq.com/logs/processing/processors/#remapper

[dd-logs-status-remapper]:https://docs.datadoghq.com/logs/processing/processors/#log-status-remapper

[dd-distributed-tracing]:https://docs.datadoghq.com/tracing/faq/distributed-tracing/

[dd-ecs-iam]: https://docs.datadoghq.com/integrations/amazon_ecs/#create-or-modify-your-iam-policy

[dd-ecs-integration]: https://docs.datadoghq.com/integrations/amazon_ecs/

[dd-fargate-announcement]: https://www.datadoghq.com/blog/monitor-aws-fargate/

[dd-host-map-filter]: https://docs.datadoghq.com/graphing/infrastructure/hostmap/#filter-by

[dd-services-page]: https://app.datadoghq.com/apm/services

[dd-tag-collection]: https://docs.datadoghq.com/tagging/assigning_tags/?tab=go#environment-variables

[dd-task-ec2-json]: https://docs.datadoghq.com/json/datadog-agent-ecs.json

[dd-task-json-doc]: https://docs.datadoghq.com/integrations/amazon_ecs/#aws-cli

[dd-watchdog]: https://docs.datadoghq.com/watchdog/

[docker-bind-mount]: https://docs.docker.com/storage/bind-mounts/

[docker-compose-tutorial]: https://docs.docker.com/compose/gettingstarted/

[docker-entrypoint]: https://docs.docker.com/engine/reference/builder/#entrypoint

[docker-socket]: https://docs.docker.com/engine/reference/commandline/dockerd/#daemon-socket-option

[ecs-agent-container-name]: https://hub.docker.com/r/amazon/amazon-ecs-agent/

[ecs-agent-logs]: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/logs.html

[ecs-awslogs]: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/using_awslogs.html

[ecs-awslogs-options]: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/using_awslogs.html#create_awslogs_logdriver_options

[ecs-cloudwatch-metrics]: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/cloudwatch-metrics.html

[ecs-network-mode]: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definition_parameters.html?shortFooter=true#network_mode

[ecs-task-def-logging]: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definition_parameters.html#container_definition_storage

[ecs-task-def-params]: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definition_parameters.html#container_definitions

[ecs-task-def-params-labels]: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definition_parameters.html#container_definition_labels

[ecs-task-metadata]: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-metadata-endpoint.html

[service-map]: /blog/service-map/

[part1]: /blog/amazon-ecs-metrics

[part2]: /blog/ecs-monitoring-tools

[part2-docker]: /blog/ecs-monitoring-tools/#collecting-docker-metrics-from-fargate-containers
