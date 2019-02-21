---

*This is the final post in a three-part series about Datadog's recent feature enhancements. This post highlights our latest visualization and collaboration features. The other installments in the series focus on [new integrations and data collection features][part-1] and [alerting enhancements][part-2], respectively.*

Datadog aggregates data from more than {{< translate key="integration_count" >}} technologies ([and growing!][part-1-enhanced]), and enables you to [create intelligent, custom alerts][part-2] to automatically detect issues in your environment. But data collection and alerting are only part of the picture—you also need to be able to visualize performance, and collaborate with others to remedy issues and document your findings. In this article, we will highlight a few of the latest additions to the Datadog platform that have helped our users visualize their metrics and collaborate with team members to [investigate issues][investigation-101] in real time:

- [Notebooks](#collaboration--exploration-with-notebooks)
- [Flame graphs for request tracing](#trace-the-path-of-requests-in-flame-graphs)
- [Service-level performance dashboards](#servicelevel-dashboards)
- [Read-only users](#readonly-users)

## Collaboration & exploration with Notebooks
Fostering a [postmortem culture][postmortem-culture] is a great way to improve the reliability and resilience of your services. It can also prepare your team to respond more effectively to incidents. Our new [Notebooks][notebooks-blog] feature is a great way to explore, investigate, and document your findings in a visual, collaborative format that's accessible to your whole team.

<iframe src="https://player.vimeo.com/video/198697459?title=0&byline=0&portrait=0" width="640" height="360" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>

Anyone can contribute and add feedback to Notebooks, which helps them evolve into rich resources for your team. Notebooks are formatted in Markdown, and supplemented with real-time or historical Datadog graphs for additional context. You can use Notebooks to:

- create descriptive postmortems that record specific incidents, their underlying causes, any steps that were taken to resolve the situation, and recommended actions to prevent the same issue from reoccurring
- compose detailed runbooks that outline procedures and step-by-step instructions for fixing the issue(s)
- graph metrics in an exploration sandbox, without editing or creating dashboards

Notebooks make it easy for teams to create up-to-date, easily accessible internal documentation that prepares them to respond to incidents more quickly. Click the Notebook icon in the Datadog nav bar [to try it out][notebooks-in-app].

## New ways to visualize application performance
As part of [our expansion into application performance monitoring][apm], we developed two new types of visualizations to help you gather insights about application performance: flame graphs and service-level dashboards.

### Trace the path of requests in flame graphs
Datadog APM collects traces from each of your services and helps you visualize their performance in detailed flame graphs. Each flame graph breaks down the latency of a request, as well as the time spent accessing various databases, caches, and other services across your environment. Drilling down into a flame graph of a problematic request allows you to pinpoint which services or calls are slowing down user requests or returning errors.

{{<img src="apm-flamegraph.png" alt="Datadog flame graph of request" caption="Each span in a request trace includes detailed metadata, such as the actual SQL query executed." size="1x" >}}

### Service-level dashboards
Service-level dashboards provide an immediate overview of the health and performance of your applications' underlying services. Each service you're monitoring with Datadog APM will automatically generate its own out-of-the-box dashboard, which displays graphs of throughput, errors, and latency, as well as a histogram of sampled latency values.

{{<img src="service-level-dash.png" alt="Datadog dashboard: service-level dashboard" size="1x" >}}

You can also combine infrastructure and application-level metrics in a customizable Datadog dashboard—simply drag and drop the Service Summary widget onto any screenboard.

{{<img src="service-and-infra-dashboard.png" alt="Datadog dashboard: combine service-level performance with infrastructure-wide metrics in one dashboard" caption="The Service Summary widget (top) adds an auto-generated view of service performance to your Datadog dashboards, which you can supplement with infrastructure metric graphs (bottom)." size="1x" >}}

## Read-only users
In addition to improving the visualization and collaboration features available to Datadog users, we've also added new management tools for account admins (such as [SAML-based authentication][saml-docs]). One of the most powerful features for expanding data-driven collaboration across your organization is the addition of read-only users.

Although you may share key metrics with people across your company, you may not want everyone to be able to edit your Datadog alerts and dashboards without your knowledge. Instead of having to watch out for unwanted changes, you now have the option to invite read-only users to your Datadog organization. Read-only users can view everything in Datadog, but they are not able to edit or create monitors, dashboards, or Notebooks.

Categorizing your organization into read-only, standard, and admin-level users ensures that everyone can access and create the Datadog resources they need—nothing more, and nothing less.

## More to come
Thanks to the hard work of our engineering teams and the Datadog community, you can begin using all of the new features mentioned in this series (or sign up for a <a href="#" class="sign-up-trigger">free trial</a>) today. Stay tuned for even more exciting developments in monitoring and observability!

[part-1]: /blog/feature-roundup-integrations/
[part-1-enhanced]: /blog/feature-roundup-integrations/#more-datadog-metrics-integrations-and-dashboards
[notebooks-blog]: /blog/data-driven-notebooks/
[part-2]: /blog/feature-roundup-alerting
[investigation-101]: /blog/monitoring-101-investigation/
[notebooks-in-app]: https://app.datadoghq.com/notebook/list
[apm]: /blog/announcing-apm/
[metadata-blog]: /blog/metric-units-descriptions-metadata/
[composite-monitors]: /blog/composite-monitors/
[postmortem-culture]: https://landing.google.com/sre/book/chapters/postmortem-culture.html
[datadog-integrations]: /product/integrations/
[saml-docs]: http://docs.datadoghq.com/guides/saml/
[saml-api-docs]: https://help.datadoghq.com/hc/en-us/articles/207061333-Manage-organizations-programmatically
