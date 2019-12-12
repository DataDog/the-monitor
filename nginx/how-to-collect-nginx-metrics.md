# How to collect NGINX metrics


## How to get the NGINX metrics you need

How you go about capturing metrics depends on which version of NGINX you are using, as well as which metrics you wish to access. (See [the companion article](https://www.datadoghq.com/blog/how-to-monitor-nginx/) for an in-depth exploration of NGINX metrics.) Free, open source NGINX and the commercial product NGINX Plus both have status modules that report metrics, and NGINX can also be configured to report certain metrics in its logs:



<table>
  <colgroup>
    <col style="text-align: left;"></col>
    <col style="text-align: center;"></col>
    <col style="text-align: center;"></col>
    <col style="text-align: center;"></col>
  </colgroup>
  <thead>
    <tr>
      <th style="text-align: left;" rowspan="2">Metric</th>
      <th style="text-align: center;" colspan="3">Availability</th>
    </tr>
    <tr>
      <th style="text-align: center;">
        <a href="#metrics-collection-nginx-opensource">NGINX (open source)</a>
      </th>
      <th style="text-align: center;">
        <a href="#metrics-collection-nginx-plus">NGINX Plus</a>
      </th>
      <th style="text-align: center;">
        <a href="#metrics-collection-nginx-logs">NGINX logs</a>
      </th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="text-align: left;">accepts / accepted</td>
      <td style="text-align: center;">x</td>
      <td style="text-align: center;">x</td>
      <td style="text-align: center;"></td>
    </tr>
    <tr>
      <td style="text-align: left;">handled</td>
      <td style="text-align: center;">x</td>
      <td style="text-align: center;">x</td>
      <td style="text-align: center;"></td>
    </tr>
    <tr>
      <td style="text-align: left;">dropped</td>
      <td style="text-align: center;">x</td>
      <td style="text-align: center;">x</td>
      <td style="text-align: center;"></td>
    </tr>
    <tr>
      <td style="text-align: left;">active</td>
      <td style="text-align: center;">x</td>
      <td style="text-align: center;">x</td>
      <td style="text-align: center;"></td>
    </tr>
    <tr>
      <td style="text-align: left;">requests / total</td>
      <td style="text-align: center;">x</td>
      <td style="text-align: center;">x</td>
      <td style="text-align: center;"></td>
    </tr>
    <tr>
      <td style="text-align: left;">4xx codes</td>
      <td style="text-align: center;"></td>
      <td style="text-align: center;">x</td>
      <td style="text-align: center;">x</td>
    </tr>
    <tr>
      <td style="text-align: left;">5xx codes</td>
      <td style="text-align: center;"></td>
      <td style="text-align: center;">x</td>
      <td style="text-align: center;">x</td>
    </tr>
    <tr>
      <td style="text-align: left;">request time</td>
      <td style="text-align: center;"></td>
      <td style="text-align: center;"></td>
      <td style="text-align: center;">x</td>
    </tr>
  </tbody>
</table>




### Metrics collection: NGINX (open source)
Open source NGINX exposes several basic metrics about server activity on a simple status page, provided that you have the HTTP [stub status module](http://nginx.org/en/docs/http/ngx_http_stub_status_module.html) enabled. To check if the module is already enabled, run:

    nginx -V 2>&1 | grep -o with-http_stub_status_module

The status module is enabled if you see `with-http_stub_status_module` as output in the terminal.

If that command returns no output, you will need to enable the status module. You can use the `--with-http_stub_status_module` configuration parameter when [building NGINX from source](https://www.nginx.com/resources/wiki/start/topics/tutorials/installoptions/):

```no-minimize
./configure \
… \
--with-http_stub_status_module
make
sudo make install
```

After verifying the module is enabled or enabling it yourself, you will also need to modify your NGINX configuration to set up a locally accessible URL (e.g., `/nginx_status`) for the status page:

```no-minimize
server {
    location /nginx_status {
        stub_status;

        access_log off;
        allow 127.0.0.1;
        deny all;
    }
}
```

Note: The `server` blocks of the NGINX config are usually found not in the master configuration file (e.g., `/etc/nginx/nginx.conf`) but in supplemental configuration files that are referenced by the master config. To find the relevant configuration files, first locate the master config by running:

    nginx -t

Open the master configuration file listed, and look for lines beginning with `include` near the end of the `http` block, such as:

    include /etc/nginx/conf.d/*.conf;

In one of the referenced config files you should find the main `server` block, which you can modify as above to configure NGINX metrics reporting. After changing any configurations, reload the configs by executing:

    nginx -s reload

Now you can view the status page to see your metrics:

```no-minimize
Active connections: 24
server accepts handled requests
1156958 1156958 4491319
Reading: 0 Writing: 18 Waiting : 6
```

Note that if you are trying to access the status page from a remote machine, you will need to whitelist the remote machine’s IP address in your status configuration, just as 127.0.0.1 is whitelisted in the configuration snippet above.

The NGINX status page is an easy way to get a quick snapshot of your metrics, but for continuous monitoring you will need to automatically record that data at regular intervals. Parsers for the NGINX status page already exist for monitoring tools such as [Nagios](https://exchange.nagios.org/directory/Plugins/Web-Servers/nginx) and [Datadog](https://docs.datadoghq.com/integrations/nginx/), as well as for the statistics collection daemon [collectD](https://collectd.org/wiki/index.php/Plugin:nginx).


### Metrics collection: NGINX Plus
The commercial NGINX Plus provides [many more metrics](http://nginx.org/en/docs/http/ngx_http_api_module.html#definitions) through its ngx_http_api_module than are available in open source NGINX. Among the additional metrics exposed by NGINX Plus are bytes streamed, as well as information about upstream systems and caches. NGINX Plus also reports counts of all HTTP status code types (1xx, 2xx, 3xx, 4xx, 5xx). A sample NGINX Plus status board is available [here](http://demo.nginx.com/status.html).

{{< img src="nginx_plus_dash.png" alt="NGINX Plus status board" popup="true" >}}

*Note: the “Active” connections on the NGINX Plus status dashboard are defined slightly differently than the Active state connections in the metrics collected via the open source NGINX stub status module. In NGINX Plus metrics, Active connections do not include connections in the Waiting state (aka Idle connections).*

NGINX Plus also reports [metrics in JSON format](http://demo.nginx.com/api/3) for easier integration with external monitoring systems. With NGINX Plus, you can see the metrics and health status for a given upstream grouping of servers, or drill down to get a count of just the response codes from a single server in that upstream. Sending a request to `/http/server_zones/<SERVER_ZONE_NAME>`, for example, will [return metrics](http://nginx.org/en/docs/http/ngx_http_api_module.html#http_server_zones_http_server_zone_name) resembling the following JSON object, which you can access in the NGINX Plus [live demo API](http://demo.nginx.com/api/3/http/server_zones):

```
{
  "processing": 0,
  "requests": 50818,
  "responses": {
    "1xx": 0,
    "2xx": 46127,
    "3xx": 3822,
    "4xx": 825,
    "5xx": 1,
    "total": 50775
  },
  "discarded": 43,
  "received": 14137130,
  "sent": 1429876113
}
```

To [enable](https://www.nginx.com/blog/live-activity-monitoring-nginx-plus-3-simple-steps/) the NGINX Plus metrics dashboard, you can add a status `server` block inside the `http` block of your NGINX configuration. ([See the section above](#metrics-collection-nginx-opensource) on collecting metrics from open source NGINX for instructions on locating the relevant config files.) For example, to set up a status dashboard at `http://<SERVER_IP_ADDRESS>:8080/status.html` and a JSON interface at `http://<SERVER_IP_ADDRESS>:8080/status`, you would add the following server block:

```no-minimize
server {
  listen 8080;
  root /usr/share/nginx/html;

  location /status {
      api;
  }

  location = /status.html {
  }
}
```

You can find an annotated example of a config file for an NGINX Plus status module [here](https://gist.githubusercontent.com/nginx-gists/a51341a11ff1cf4e94ac359b67f1c4ae/raw/bf9b68cca20c87f303004913a6a9e9032f24d143/nginx-plus-api.conf). To collect metrics from an upstream server group on your dashboard, you'll need to add a `status_zone` [directive](http://nginx.org/en/docs/http/ngx_http_api_module.html#directives) to your `server` block.

The status pages should be live once you reload your NGINX configuration:

    nginx -s reload

The official NGINX Plus docs have [more details](http://nginx.org/en/docs/http/ngx_http_api_module.html#example) on how to configure the expanded status module.



### Metrics collection: NGINX logs
NGINX’s [log module](http://nginx.org/en/docs/http/ngx_http_log_module.html) writes configurable access logs to a destination of your choosing. You can customize the format of your logs and the data they contain by [adding or subtracting variables](http://nginx.org/en/docs/http/ngx_http_log_module.html#log_format). The simplest way to capture detailed logs is to add the following line in the `server` block of your config file (see [the section](#metrics-collection-nginx-opensource) on collecting metrics from open source NGINX for instructions on locating your config files):

    access_log logs/host.access.log combined;

After changing any NGINX configurations, reload the configs by executing:

    nginx -s reload

The “combined” log format, included by default, captures [a number of key data points](http://nginx.org/en/docs/http/ngx_http_log_module.html#log_format), such as the actual HTTP request and the corresponding response code. In the example logs below, NGINX logged a 200 (success) status code for a request for /index.html and a 404 (not found) error for the nonexistent /fail.

    127.0.0.1 - - [19/Feb/2015:12:10:46 -0500] "GET /index.html HTTP/1.1" 200 612 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari 537.36"

    127.0.0.1 - - [19/Feb/2015:12:11:05 -0500] "GET /fail HTTP/1.1" 404 570 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36"

You can log request processing time as well by adding a new log format to the `http` block of your NGINX config file:

```no-minimize
log_format nginx '\$remote_addr - \$remote_user [\$time_local] '
                  '"\$request" \$status \$body_bytes_sent \$request_time '
                  '"\$http_referer" "\$http_user_agent"';
```

And by adding or modifying the `access_log` line in the `server` block of your config file (the `nginx` parameter names the format we defined earlier):

    access_log logs/host.access.log nginx;

After reloading the updated configs (by running `nginx -s reload`), your access logs will include response times, as seen below. The units are seconds, with millisecond resolution. In this instance, the server received a request for /big.pdf, returning a 206 (success) status code after sending 33973115 bytes. Processing the request took 0.202 seconds (202 milliseconds):

    127.0.0.1 - - [19/Feb/2015:15:50:36 -0500] "GET /big.pdf HTTP/1.1" 206 33973115 0.202 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36"

You can use a variety of tools and services to parse and analyze NGINX logs. For instance, [rsyslog](https://github.com/rsyslog/rsyslog) can monitor your logs and pass them to any number of log-analytics services; you can use a free, open source tool such as [logstash](https://www.elastic.co/products/logstash) to collect and analyze logs; or you can use a unified logging layer such as [Fluentd](http://www.fluentd.org/) to collect and parse your NGINX logs. You can also use Datadog to collect and analyze NGINX logs, which we'll explore in [part 3](https://www.datadoghq.com/blog/how-to-monitor-nginx-with-datadog/) of this series.


## Conclusion

Which NGINX metrics you monitor will depend on the tools available to you, and whether the insight provided by a given metric justifies the overhead of monitoring that metric. For instance, is measuring error rates important enough to your organization to justify investing in NGINX Plus or implementing a system to capture and analyze logs?

At Datadog, we have built a single integration that supports both NGINX and NGINX Plus so that you can begin collecting and monitoring metrics from all your web servers with a minimum of setup. Learn how to monitor NGINX metrics with Datadog [in this post](https://www.datadoghq.com/blog/how-to-monitor-nginx-with-datadog/), and get started right away with <a href="#" class="sign-up-trigger">a free trial of Datadog</a>.

<br>
*Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/nginx/how_to_collect_nginx_metrics.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues).*
