*This post is part 3 in a 4-part series about monitoring Docker. [Part 1][part-1] discusses the novel challenge of monitoring containers instead of hosts, [part 2][part-2] explores metrics that are available from Docker, and [part 4][part-4] describes how the largest TV and radio outlet in the U.S. monitors Docker. This article covers the nuts and bolts of collecting Docker metrics.*

Docker exposes metrics via three mechanisms: pseudo-files in sysfs, the stats command, and API. Metrics coverage across these three mechanisms is uneven, as seen below:

Access via | CPU metrics | Memory metrics | I/O metrics | Network metrics
--- | --- | --- | --- | ---
[pseudo-files](#pseudo-files) | [Yes](#pseudo-files-cpu) | [Yes](#pseudo-files-memory) | [Some](#pseudo-files-io) | [Yes, as of v1.6.1](#pseudo-files-network)
[stats command](#stats-command) | [Basic](#stats-cpu) | [Basic](#stats-memory) | [Some, as of v1.9.0](#stats-io) | [Basic](#stats-network)
[API](#api) | [Yes](#api-cpu) | [Yes](#api-memory) | [Some](#api-io) | [Yes](#api-network)

<h2 class="anchor" id="pseudo-files">Pseudo-files</h2>
Docker metrics reported via pseudo-files in sysfs by default do not require privileged (root) access. They are also the fastest and most lightweight way to read metrics; if you are monitoring many containers per host, speed may become a requirement. However, you can not collect all metrics from pseudo-files. As seen in the table above, there may be limitations on I/O and network metrics.

### Pseudo-file location
This article assumes your metrics pseudo-files are located in `/sys/fs/cgroup` in the host OS. In some systems, they may be in `/cgroup` instead.

Your pseudo-file access path includes the long id of your container. For illustration purposes this article assumes that your have set an env variable `CONTAINER_ID` to the long ID of the container you are monitoring. If you'd like to copy-paste run commands in this article, you can set CONTAINER\_ID like this: `CONTAINER_ID=$(docker run [OPTIONS] IMAGE [COMMAND] [ARG...] )` or you can save it after launching: `docker ps --no-trunc` and then copy-paste and save the long ID as an env variable like `CONTAINER_ID=<long ID>`

<h3 class="anchor" id="pseudo-files-cpu">CPU</h3>
CPU metrics are reported in cpu and cpuacct (CPU accumulated).

#### OS-specific metric paths

In the commands below, we use the metric directory for standard Linux systems (`/sys/fs/cgroup/cpuacct/docker/$CONTAINER_ID/`). For recent versions of CoreOS, you will need to use this path instead: `/sys/fs/cgroup/cpuacct/init.scope/system.slice/docker-$CONTAINER_ID.scope/`.

#### Usage
<pre>
$ cat /sys/fs/cgroup/cpuacct/docker/$CONTAINER_ID/cpuacct.stat
> user 2451  # time spent running processes since boot
> system 966 # time spent executing system calls since boot
</pre>

If you're using an x86 system, the times above are expressed in 10-millisecond increments, so the recently-booted container above has spent 24.51s running user processes, and 9.66s on system calls. (Technically the times are expressed in user jiffies. Deep jiffy info [here](http://www.makelinux.net/books/lkd2/ch10lev1sec3).)

#### CPU Usage per core
Per-CPU usage can help you identify core imbalances, which can be caused by bad configuration.
<pre>
$ cat /sys/fs/cgroup/cpuacct/docker/$CONTAINER_ID/cpuacct.usage_percpu
> 45094018900  # nanoseconds CPU has been in use since boot (45.09s)
</pre>
	
If your container is using multiple CPU cores and you want a convenient total usage number, you can run: 
<pre>
$ cat /sys/fs/cgroup/cpuacct/docker/$CONTAINER_ID/cpuacct.usage
> 45094018900 # total nanoseconds CPUs have been in use (45.09s)
</pre>
	
#### Throttled CPU
If you set a limit on the CPU time available to a container with [CPU quota constraint][cpu-quota-constraint], your container will be throttled when it attempts to exceed the limit.
<pre>
$ cat /sys/fs/cgroup/cpu/docker/$CONTAINER_ID/cpu.stat
> nr_periods 565 # Number of enforcement intervals that have elapsed
> nr_throttled 559 # Number of times the group has been throttled
> throttled_time 12119585961 # Total time that members of the group were throttled, in nanoseconds (12.12 seconds)
</pre>

<h3 class="anchor" id="pseudo-files-memory">Memory </h3>

The following command will print a lot of information of memory usage, probably more than you need. Note that the first half of the measures have no standard prefix; these measures exclude sub-cgroups. The second half all are prefixed with "total_"; these measures include sub-cgroups.
<pre>
$ cat /sys/fs/cgroup/memory/docker/$CONTAINER_ID/memory.stat
  # On CoreOS: cat /sys/fs/cgroup/memory/init.scope/system.slice/docker-$CONTAINER_ID.scope/memory.stat 
	
    cache 532480
    rss 10649600
    mapped_file 1576960
    writeback 0
    swap 0
    pgpgin 302242
    pgpgout 296556
    pgfault 1142200
    pgmajfault 125
    inactive_anon 16384
    active_anon 577536
    inactive_file 11386880
    active_file 11309056
    unevictable 0
    hierarchical_memory_limit 18446744073709551615
    hierarchical_memsw_limit 18446744073709551615
    total_cache 22798336
    total_rss 491520
    total_rss_huge 0
    total_mapped_file 1576960
    total_writeback 0
    total_swap 0
    total_pgpgin 302242
    total_pgpgout 296556
    total_pgfault 1142200
    total_pgmajfault 125
    total_inactive_anon 16384
    total_active_anon 577536
    total_inactive_file 11386880
    total_active_file 11309056
    total_unevictable 0
</pre>
	
You can get most interesting memory metrics directly by calling a specific command in the `/sys/fs/cgroup/memory/docker/$CONTAINER_ID/` directory (use `/sys/fs/cgroup/memory/init.scope/system.slice/docker-$CONTAINER_ID.scope/` instead on recent versions of CoreOS):
<pre>
# Total memory used: cached + rss 
$ cat /sys/fs/cgroup/memory/docker/$CONTAINER_ID/memory.usage_in_bytes
	
# Total memory used + swap in use
$ cat /sys/fs/cgroup/memory/docker/$CONTAINER_ID/memory.memsw.usage_in_bytes
		
# Number of times memory usage hit limts
$ cat /sys/fs/cgroup/memory/docker/$CONTAINER_ID/memory.failcnt
		
# Memory limit of the cgroup in bytes 
$ cat /sys/fs/cgroup/memory/docker/$CONTAINER_ID/memory.limit_in_bytes
</pre>

Note that if the final command returns a long garbage number like 18446744073709551615, you did not set the limit when you launched the container. To set a 500MB limit, for example:
<pre>
$ docker run -m 500M IMAGE [COMMAND] [ARG...]	
</pre>
Further information about the memory metrics can be found in the official [documentation](https://docs.docker.com/articles/runmetrics/).	

<h3 class="anchor" id="pseudo-files-io">I/O </h3>
The path to I/O stats pseudo-files for most operating systems is: `/sys/fs/cgroup/blkio/docker/$CONTAINER_ID/`. For CoreOS, the equivalent path is: `/sys/fs/cgroup/blkio/init.scope/system.slice/docker-$CONTAINER_ID.scope/`.

Depending on your system, you may have many metrics available from these pseudo-files: `blkio.io_queued_recursive`, `blkio.io_service_time_recursive`, `blkio.io_wait_time_recursive` and more. 

On many systems, however, many of these pseudo-files only return zero values. In this case there are usually still two pseudo-files that work: `blkio.throttle.io_service_bytes` and `blkio.throttle.io_serviced`, which report total I/O bytes and operations, respectively. Contrary to their names, these numbers do not report *throttled* I/O but *actual* I/O bytes and ops.

The first two numbers reported by these pseudo-files are the major:minor device IDs, which uniquely identify a device. Example output from blkio.throttle.io\_service\_bytes:
<pre>
253:0 Read 13750272
253:0 Write 180224
253:0 Sync 180224
253:0 Async 13750272
253:0 Total 13930496
</pre>

<h3 class="anchor" id="pseudo-files-network">Network </h3>
#### Docker version 1.6.1 and greater
In [release 1.6.1](https://github.com/docker/docker/blob/master/CHANGELOG.md#161-2015-05-07), Docker fixed read/write /proc paths.
<pre>
$ CONTAINER_PID=`docker inspect -f '{{ .State.Pid }}' $CONTAINER_ID`
$ cat /proc/$CONTAINER_PID/net/dev    
    
Inter-|   Receive                                                |  Transmit
 face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
  eth0:     1296     16    0    0    0     0          0         0      816      10    0    0    0     0       0          0
    lo:        0      0    0    0    0     0          0         0        0       0    0    0    0     0       0          0
</pre>

#### Older versions of Docker
You can get network metrics from `ip netns`, with some symlinking:

<pre>
$ CONTAINER_PID=`docker inspect -f '{{ .State.Pid }}' $CONTAINER_ID`
$ mkdir -p /var/run/netns
$ ln -sf /proc/$CONTAINER_PID/ns/net /var/run/netns/$CONTAINER_ID
$ ip netns exec $CONTAINER_ID netstat -i 
</pre>

![Visual break](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-03-container-monitoring/p3_divider_1.png)

<h2 class="anchor" id="stats-command">Stats command</h2>
The `docker stats` command will continuously report a live stream of basic CPU, memory, and network metrics. As of [version 1.9.0][v1.9.0], `docker stats` also includes disk I/O metrics.
<pre>
# Usage: docker stats CONTAINER [CONTAINER...]
$ docker stats $CONTAINER_ID
    
CONTAINER       CPU %     MEM USAGE/LIMIT     MEM %     NET I/O             BLOCK I/O
ecb37227ac84    0.12%     71.53 MiB/490 MiB   14.60%    900.2 MB/275.5 MB   266.8 MB/872.7 MB
</pre>
	
<h3 class="anchor" id="stats-cpu">CPU </h3>
CPU is reported as % of total host capacity. So if you have two containers each using as much CPU as they can, each allocated the same CPU shares by docker, then the stat command for each would register 50% utilization, though in practice their CPU resources would be fully utilized.	

<h3 class="anchor" id="stats-memory">Memory </h3>
If you do not explicitly set the memory limits for the container, then the memory usage limit will be the memory limit of the host machine. If the host is using memory for other processes, your container will run out of memory before it hits the limit reported by the stats command.

<h3 class="anchor" id="stats-io">I/O </h3>
As of Docker version 1.9.0, `docker stats` now displays total bytes read and written.

<h3 class="anchor" id="stats-network">Network </h3>
Displays total bytes received (RX) and transmitted (TX).

<h3 class="anchor" id="stats-requirements">Requirements </h3>
1. Docker version 1.5.0 (released February 2015) or higher
2. Exec driver 'libcontainer', which has been the default since Docker 0.9. If you are [overriding the default](http://docs.docker.com/reference/commandline/cli/#docker-exec-driver-option) exec driver, neither `docker stats` nor the API will report metrics. 

![Visual break](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-03-container-monitoring/p3_divider_2.png)
<h2 class="anchor" id="api">API</h2>
Like the `docker stats` command, the API will continuously report a live stream of CPU, memory, I/O, and network metrics. The difference is that the API provides far more detail than the stats command.

The daemon listens on `unix:///var/run/docker.sock` to allow only local connections by the root user. When you launch Docker, however, you can bind it to another port or socket; instructions and strong warnings are [here][other-sockets]. This article describes how to access the API on the default socket.

You can send commands to the socket with `nc`. All API calls will take this general form:
<pre>
echo "<HTTP API CALL>" | nc -U /var/run/docker.sock
</pre>

To collect all metrics in a continuously updated live stream of JSON, run:
<pre>
$ echo -ne "GET /containers/$CONTAINER_ID/stats HTTP/1.1\r\n\r\n" | sudo nc -U /var/run/docker.sock
</pre>

The response will be long, live-streaming chunks of JSON with metrics about the container. Rather than print an entire example JSON object here, its parts are discussed individually below.
    
<h3 class="anchor" id="api-cpu">CPU </h3>
<pre>
"cpu_stats": {
    "cpu_usage": {
      "total_usage": 44651120376,
      "percpu_usage": [
        44651120376
      ],
      "usage_in_kernelmode": 9660000000,
      "usage_in_usermode": 24510000000
    },
    "system_cpu_usage": 269321720000000,
    "throttling_data": {
      "periods": 0,
      "throttled_periods": 0,
      "throttled_time": 0
    }
}
</pre>

`system_cpu_usage` represents the host's cumulative CPU usage in nanoseconds; this includes user, system, idle, etc. (the sum of the `/proc/stat` CPU line). 

All other CPU metrics can also be accessed through pseudo-files, as described above, with a few differences:
  
*   `usage_in_kernelmode` is the same as system CPU usage reported by pseudo-files, although the API expresses this value in nanoseconds rather than 10-millisecond increments. As you can see, in the example reading in this article, both methods report the same number: 9.66s
*  `usage_in_usermode` is the  same as user CPU usage reported by pseudo-files. As above, this number is reported in nanoseconds.

<h3 class="anchor" id="api-memory">Memory </h3>
Most of the memory stats available through the API are also available through the pseudo-files as described in that section [above](#pseudo-files-memory). `usage` is memory.usage_in_bytes, `max_usage` is memory.max_usage_in_bytes, `stats` is memory.stat pseudo-file., `limit` is the memory limit set on the container memory.limit_in_bytes, if it is set; otherwise `limit` is the host memory limit in /proc/meminfo (MemTotal).

<pre>
"memory_stats": {
    "usage": 2699264,
    "max_usage": 20971520,
    "stats": {
      "active_anon": 577536,
      "active_file": 0,
      "cache": 2207744,
      "hierarchical_memory_limit": 20971520,
      "hierarchical_memsw_limit": 1.844674407371e+19,
      "inactive_anon": 16384,
      "inactive_file": 2105344,
      "mapped_file": 479232,
      "pgfault": 1821069,
      "pgmajfault": 2398,
      "pgpgin": 507907,
      "pgpgout": 507248,
      "rss": 491520,
      "rss_huge": 0,
      "swap": 0,
      "total_active_anon": 577536,
      "total_active_file": 0,
      "total_cache": 2207744,
      "total_inactive_anon": 16384,
      "total_inactive_file": 2105344,
      "total_mapped_file": 479232,
      "total_pgfault": 1821069,
      "total_pgmajfault": 2398,
      "total_pgpgin": 507907,
      "total_pgpgout": 507248,
      "total_rss": 491520,
      "total_rss_huge": 0,
      "total_swap": 0,
      "total_unevictable": 0,
      "total_writeback": 0,
      "unevictable": 0,
      "writeback": 0
    },
    "failcnt": 24422,
    "limit": 513851392
}
</pre>

<h3 class="anchor" id="api-io">I/O </h3>
The API currently reports a count of read, write, sync, and async operations, plus a total count of operations in `blkio_stats.io_serviced_recursive`. The total bytes corresponding to those operations are reported in `blkio_stats.io_service_bytes_recursive`. Depending on your system, other I/O stats may also be reported, or may be disabled (empty). Major and minor IDs uniquely identify a device.
<pre>
"blkio_stats": {
    "io_service_bytes_recursive": [
    {
        "major": 253,
    	"minor": 0,
    	"op": "Read",
    	"value": 13750272
   },
   {
    	"major": 253,
    	"minor": 0,
    	"op": "Write",
    	"value": 12288
   },
   ...
</pre>

<h3 class="anchor" id="api-network">Network </h3>
The API is the easiest way to get network metrics for your container. (RX represents "received", and TX represents "transmitted".)
<pre>
"network": {
    "rx_bytes": 197942,
    "rx_packets": 51,
    "rx_errors": 0,
    "rx_dropped": 0,
    "tx_bytes": 3549,
    "tx_packets": 50,
    "tx_errors": 0,
    "tx_dropped": 0
}
</pre>

### Selecting specific Docker metrics
By sending output from the API to grep to throw out non-JSON rows, and then to `jq` for JSON parsing, we can create a stream of selected metrics. Some examples are below.

* **CPU stats** : <pre>$ echo -ne "GET /containers/$CONTAINER_ID/stats HTTP/1.1\r\n\r\n" | nc -U /var/run/docker.sock | grep "^{" | jq '.cpu_stats'</pre>
* **IO bytes written**: <pre>echo -ne "GET /containers/$CONTAINER_ID/stats HTTP/1.1\r\n\r\n" | nc -U /var/run/docker.sock | grep "^{" | jq '.blkio_stats.io_service_bytes_recursive | .[1].value'</pre>
* **Network bytes received**: <pre>echo -ne "GET /containers/$CONTAINER_ID/stats HTTP/1.1\r\n\r\n" | nc -U /var/run/docker.sock | grep "^{" | jq '.network.rx_bytes'</pre>

### API requirements
Same as the stats command, [above](#stats-requirements).

### Additional API calls
Other useful Docker API calls are documented [here](https://docs.docker.com/reference/api/docker_remote_api/). You can call them using `nc` as described in above.

![Visual break](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-03-container-monitoring/p3_divider_3.png)
# Conclusion
Between pseudo-files, the stats command, and the API, there are several ways to get native Docker metrics, each with their own usage and completeness characteristics. Since Docker is evolving quickly, the metrics provided by these commands will likely continue to change significantly over the coming years. 

If you're using Docker in production, you probably can't afford to rely on manual metric spot-checks with these built-in tools—they won't provide sufficient visibility into your systems' health and performance. Most likely you'll need a dedicated monitoring service that collects and stores your metrics for display, correlation, and alerting. The next and final part of this article (coming soon) describes how the largest TV and radio outlet in the U.S. monitors their Docker metrics.
- - -

*Source Markdown for this post is available [on GitHub][markdown]. Questions, corrections, additions, etc.? Please [let us know][issues].*

[markdown]: https://github.com/DataDog/the-monitor/blob/master/docker/3_how_to_collect_docker_metrics.md
[issues]: https://github.com/datadog/the-monitor/issues
[part-1]: https://www.datadoghq.com/blog/the-docker-monitoring-problem/
[part-2]: https://www.datadoghq.com/blog/how-to-monitor-docker-resource-metrics/
[cpu-quota-constraint]: https://www.datadoghq.com/blog/how-to-monitor-docker-resource-metrics/#throttling
[v1.9.0]: https://github.com/docker/docker/releases/tag/v1.9.0
[other-sockets]: https://docs.docker.com/engine/userguide/basics/#bind-docker-to-another-host-port-or-a-unix-socket
[part-4]: https://www.datadoghq.com/blog/iheartradio-monitors-docker/
