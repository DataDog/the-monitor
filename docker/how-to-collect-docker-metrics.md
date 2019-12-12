# How to collect Docker metrics


*This post is part 3 in a 4-part series about monitoring Docker. [Part 1](https://www.datadoghq.com/blog/the-docker-monitoring-problem/) discusses the novel challenge of monitoring containers instead of hosts, [part 2](https://www.datadoghq.com/blog/how-to-monitor-docker-resource-metrics/) explores metrics that are available from Docker, and [part 4](https://www.datadoghq.com/blog/iheartradio-monitors-docker/) describes how the largest TV and radio outlet in the U.S. monitors Docker. This article covers the nuts and bolts of collecting Docker metrics.*

Docker exposes metrics via three mechanisms: pseudo-files in sysfs, the stats command, and API. Metrics coverage across these three mechanisms is uneven, as seen below:



<table>
<thead>
<tr class="header">
<th>Access via</th>
<th>CPU metrics</th>
<th>Memory metrics</th>
<th>I/O metrics</th>
<th>Network metrics</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><a href="#pseudofiles">pseudo-files</a></td>
<td><a href="#cpu-pseudofiles">Yes</a></td>
<td><a href="#memory-pseudofiles">Yes</a></td>
<td><a href="#io-pseudofiles">Some</a></td>
<td><a href="#network-pseudofiles">Yes, as of v1.6.1</a></td>
</tr>
<tr class="even">
<td><a href="#stats-command">stats command</a></td>
<td><a href="#cpu-stats">Basic</a></td>
<td><a href="#memory-stats">Basic</a></td>
<td><a href="#io-stats">Some, as of v1.9.0</a></td>
<td><a href="#network-stats">Basic</a></td>
</tr>
<tr class="odd">
<td><a href="#api">API</a></td>
<td><a href="#cpu">Yes</a></td>
<td><a href="#memory">Yes</a></td>
<td><a href="#io">Some</a></td>
<td><a href="#network">Yes</a></td>
</tr>
</tbody>
</table>



Pseudo-files
------------

Docker metrics reported via pseudo-files in sysfs by default do not require privileged (root) access. They are also the fastest and most lightweight way to read metrics; if you are monitoring many containers per host, speed may become a requirement. However, you cannot collect all metrics from pseudo-files. As seen in the table above, there may be limitations on I/O and network metrics.

### Pseudo-file location

This article assumes your metrics pseudo-files are located in `/sys/fs/cgroup` in the host OS. In some systems, they may be in `/cgroup` instead.

Your pseudo-file access path includes the long id of your container. For illustration purposes this article assumes that your have set an env variable `CONTAINER_ID` to the long ID of the container you are monitoring. If you’d like to copy-paste run commands in this article, you can set CONTAINER_ID like this: `CONTAINER_ID=$(docker run [OPTIONS] IMAGE [COMMAND] [ARG...] )` or you can save it after launching: `docker ps --no-trunc` and then copy-paste and save the long ID as an env variable like `CONTAINER_ID=<long ID>`

### CPU pseudo-files

CPU metrics are reported in cpu and cpuacct (CPU accumulated).

#### OS-specific metric paths

In the commands below, we use the metric directory for standard Linux systems (`/sys/fs/cgroup/cpuacct/docker/$CONTAINER_ID/`). 

#### Usage

```
$ cat /sys/fs/cgroup/cpuacct/docker/$CONTAINER_ID/cpuacct.stat
> user 2451  # time spent running processes since boot
> system 966 # time spent executing system calls since boot
```

If you’re using an x86 system, the times above are expressed in 10-millisecond increments, so the recently-booted container above has spent 24.51s running user processes, and 9.66s on system calls. (Technically the times are expressed in user jiffies. Deep jiffy info [here](http://www.makelinux.net/ldd3/chp-7-sect-1).)

#### CPU Usage per core

Per-CPU usage can help you identify core imbalances, which can be caused by bad configuration.

```
$ cat /sys/fs/cgroup/cpuacct/docker/$CONTAINER_ID/cpuacct.usage_percpu
> 45094018900  # nanoseconds CPU has been in use since boot (45.09s)      
```

If your container is using multiple CPU cores and you want a convenient total usage number, you can run:

```
$ cat /sys/fs/cgroup/cpuacct/docker/$CONTAINER_ID/cpuacct.usage
> 45094018900 # total nanoseconds CPUs have been in use (45.09s)
```

#### Throttled CPU

If you set a limit on the CPU time available to a container with [CPU quota constraint](https://www.datadoghq.com/blog/how-to-monitor-docker-resource-metrics/#throttling), your container will be throttled when it attempts to exceed the limit.

```
$ cat /sys/fs/cgroup/cpu/docker/$CONTAINER_ID/cpu.stat
> nr_periods 565 # Number of enforcement intervals that have elapsed
> nr_throttled 559 # Number of times the group has been throttled
> throttled_time 12119585961 # Total time that members of the group were throttled, in nanoseconds (12.12 seconds)
```

### Memory pseudo-files

The following command will print a lot of information of memory usage, probably more than you need. Note that the first half of the measures have no standard prefix; these measures exclude sub-cgroups. The second half all are prefixed with “total_”; these measures include sub-cgroups.

```
$ cat /sys/fs/cgroup/memory/docker/$CONTAINER_ID/memory.stat
  
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
```

You can get most interesting memory metrics directly by calling a specific command in the `/sys/fs/cgroup/memory/docker/$CONTAINER_ID/` directory:

```
# Total memory used: cached + rss 
$ cat /sys/fs/cgroup/memory/docker/$CONTAINER_ID/memory.usage_in_bytes
  
# Total memory used + swap in use
$ cat /sys/fs/cgroup/memory/docker/$CONTAINER_ID/memory.memsw.usage_in_bytes
    
# Number of times memory usage hit limts
$ cat /sys/fs/cgroup/memory/docker/$CONTAINER_ID/memory.failcnt
    
# Memory limit of the cgroup in bytes 
$ cat /sys/fs/cgroup/memory/docker/$CONTAINER_ID/memory.limit_in_bytes
```

Note that if the final command returns a long garbage number like 18446744073709551615, you did not set the limit when you launched the container. To set a 500MB limit, for example:

    $ docker run -m 500M IMAGE [COMMAND] [ARG...]  

Further information about the memory metrics can be found in the official [documentation](https://docs.docker.com/engine/admin/runmetrics/).

### I/O pseudo-files

The path to I/O stats pseudo-files for most operating systems is: `/sys/fs/cgroup/blkio/docker/$CONTAINER_ID/`. 

Depending on your system, you may have many metrics available from these pseudo-files: `blkio.io_queued_recursive`, `blkio.io_service_time_recursive`, `blkio.io_wait_time_recursive` and more.

On many systems, however, many of these pseudo-files only return zero values. In this case there are usually still two pseudo-files that work: `blkio.throttle.io_service_bytes` and `blkio.throttle.io_serviced`, which report total I/O bytes and operations, respectively. Contrary to their names, these numbers do not report *throttled* I/O but *actual* I/O bytes and ops.

The first two numbers reported by these pseudo-files are the major:minor device IDs, which uniquely identify a device. Example output from blkio.throttle.io\_service\_bytes:

```
253:0 Read 13750272
253:0 Write 180224
253:0 Sync 180224
253:0 Async 13750272
253:0 Total 13930496    
```

### Network pseudo-files

#### Docker version 1.6.1 and greater

In [release 1.6.1](https://github.com/docker/docker/blob/master/CHANGELOG.md#161-2015-05-07), Docker fixed read/write /proc paths.

```
$ CONTAINER_PID=`docker inspect -f '{{ .State.Pid }}' $CONTAINER_ID`
$ cat /proc/$CONTAINER_PID/net/dev    
    
Inter-|   Receive                                                |  Transmit
 face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
  eth0:     1296     16    0    0    0     0          0         0      816      10    0    0    0     0       0          0
    lo:        0      0    0    0    0     0          0         0        0       0    0    0    0     0       0          0
```

#### Older versions of Docker

You can get network metrics from `ip netns`, with some symlinking:

```
$ CONTAINER_PID=`docker inspect -f '{{ .State.Pid }}' $CONTAINER_ID`
$ mkdir -p /var/run/netns
$ ln -sf /proc/$CONTAINER_PID/ns/net /var/run/netns/$CONTAINER_ID
$ ip netns exec $CONTAINER_ID netstat -i 
```

{{< img src="p3-divider-1.png" alt="Visual break" >}}

Stats command
-------------

The `docker stats` command will continuously report a live stream of basic CPU, memory, and network metrics. As of [version 1.9.0](https://github.com/docker/docker/releases/tag/v1.9.0), `docker stats` also includes disk I/O metrics.

```
# Usage: docker stats CONTAINER [CONTAINER...]
$ docker stats $CONTAINER_ID
    
CONTAINER       CPU %     MEM USAGE/LIMIT     MEM %     NET I/O             BLOCK I/O
ecb37227ac84    0.12%     71.53 MiB/490 MiB   14.60%    900.2 MB/275.5 MB   266.8 MB/872.7 MB
```

### CPU stats

CPU is reported as % of total host capacity. So if you have two containers each using as much CPU as they can, each allocated the same CPU shares by docker, then the stat command for each would register 50% utilization, though in practice their CPU resources would be fully utilized.

### Memory stats

If you do not explicitly set the memory limits for the container, then the memory usage limit will be the memory limit of the host machine. If the host is using memory for other processes, your container will run out of memory before it hits the limit reported by the stats command.

### I/O stats

As of Docker version 1.9.0, `docker stats` now displays total bytes read and written.

### Network stats

Displays total bytes received (RX) and transmitted (TX).

### Requirements

1. Docker version 1.5.0 (released February 2015) or higher
1. Exec driver ‘libcontainer’, which has been the default since Docker 0.9.

{{< img src="p3-divider-2.png" alt="Visual break" >}}

API