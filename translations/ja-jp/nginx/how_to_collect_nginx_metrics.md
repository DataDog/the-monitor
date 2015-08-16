# Protected: How to collect NGINX metrics

> *This post is part 2 of a 3-part series on NGINX monitoring. [Part 1](/blog/how-to-monitor-nginx/) explores the key metrics available in NGINX, and [Part 3](/blog/how-to-monitor-nginx-with-datadog/) details how to monitor NGINX with Datadog.*

*このポストは、"NGINXの監視"3回シリーズのPart 2です。 Part 1は、[「NGINXの監視方法」](/blog/how-to-monitor-nginx/)で、Part 3は、[「Datadogを使ったNGINXの監視」](/blog/how-to-monitor-nginx-with-datadog/)になります。*

## How to get the NGINX metrics you need

> How you go about capturing metrics depends on which version of NGINX you are using, as well as which metrics you wish to access. (See [the companion article](/blog/how-to-monitor-nginx/) for an in-depth exploration of NGINX metrics.) Free, open-source NGINX and the commercial product NGINX Plus both have status modules that report metrics, and NGINX can also be configured to report certain metrics in its logs:

NGINXからメトリクスを集める方法は、採用しているNGINXのバージョンに依存すると共に、収集したいメトリクスに依存しています。(NGINXのメトリクスについて詳しく知りたい場合は、このシリーズのPart 1 [「NGINXの監視方法」](/blog/how-to-monitor-nginx/)を参照してください。) オープンソース版のNGINXと商用版のNGINX Plusには、基本メトリクスをリポーティングするためにステータスモジューが実装されています。更にNGINXは、特定のメトリクスをログへ出力できるようにする設定も装備されています。:

<table><colgroup> <col style="text-align: left;" /> <col style="text-align: center;" /> <col style="text-align: center;" /> <col style="text-align: center;" /> </colgroup>
<thead>
<tr>
<th style="text-align: left;" rowspan="2">Metric</th>
<th style="text-align: center;" colspan="3">Availability</th>
</tr>
<tr>
<th style="text-align: center;"><a href="#open-source">NGINX (open-source)</a></th>
<th style="text-align: center;"><a href="#plus">NGINX Plus</a></th>
<th style="text-align: center;"><a href="#logs">NGINX logs</a></th>
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

### Metrics collection: NGINX (open-source)

> Open-source NGINX exposes several basic metrics about server activity on a simple status page, provided that you have the HTTP [stub status module](http://nginx.org/en/docs/http/ngx_http_stub_status_module.html) enabled. To check if the module is already enabled, run:

オープンソース版のNGINXでは、HTTP [stub status module](http://nginx.org/en/docs/http/ngx_http_stub_status_module.html)を有効にすることにより、サーバーの稼働状況に関する複数の基本メトリクスを、ステータスページで閲覧することができるようになります。このモジュールが有効になっているか確認するためには、次のコマンドを実行します:

```
nginx -V 2>&1 | grep -o with-http_stub_status_module
```

> The status module is enabled if you see `with-http_stub_status_module` as output in the terminal.

ターミナル出力に`with-http_stub_status_module` が表示されて場合は、ステータスモジュールが有効になっています。

> If that command returns no output, you will need to enable the status module. You can use the `--with-http_stub_status_module` configuration parameter when [building NGINX from source](http://wiki.nginx.org/InstallOptions):

コマンの実行結果として何も表示されない場合は、ステータス·モジュールを有効にする必要があります。[ソースからNGINXをコンパイル ](http://wiki.nginx.org/InstallOptions)する際に、`--with-http_stub_status_module`をパラメーターに追記する必要があります:

```
./configure \
… \
--with-http_stub_status_module
make
sudo make install
```

> After verifying the module is enabled or enabling it yourself, you will also need to modify your NGINX configuration to set up a locally accessible URL (e.g., `/nginx_status`) for the status page:

先のコマンドでモジュールが有効になっていることを確認できたか、オプションを追記してソールからコンパイルしなおすことができたなら、NGINXの設定ファイルを変更し、ローカルサーバーのステータスページにアクセスするためのURL(例:`/nginx_status`)を設定します:

```
server {
    location /nginx_status {
        stub_status on;

        access_log off;
        allow 127.0.0.1;
        deny all;
    }
}
```

> Note: The `server` blocks of the NGINX config are usually found not in the master configuration file (e.g., `/etc/nginx/nginx.conf`) but in supplemental configuration files that are referenced by the master config. To find the relevant configuration files, first locate the master config by running:

注: 通常、NGINXの`server`設定をするブロックは、マスター設定ファイル (例:`/etc/nginx/nginx.conf`)内には記述されていません。マスター設定ファイル内で参照設定されている補助的な設定ファイルに記述されています。関連する構成ファイルを検索するには、まず次のコマンドを実行し、マスター設定ファイルを場所を確認します。

```
nginx -t
```

> Open the master configuration file listed, and look for lines beginning with `include` near the end of the `http` block, such as:

マスター設定ファイルを表示し、ファイル内の`http`ブロックの末尾で、次の例ように`include`から始まる行を探します:

```
include /etc/nginx/conf.d/*.conf;
```

> In one of the referenced config files you should find the main `server` block, which you can modify as above to configure NGINX metrics reporting. After changing any configurations, reload the configs by executing:

参照してるどれかの設定ファイル内で、`server`ブロックを見つけることができるはずです。この`server`ブロックを上に紹介したように変更することで、NGINXがメトリクスをリポーティングするように設定できます。NGINXの設定を変更した場合は、次のコマンドを実行し、設定を読み込ませます:

```
nginx -s reload
```

> Now you can view the status page to see your metrics:

このまでの作業が完了したら、ステータスページにアクセスし、メトリクスを閲覧することができます。

```
Active connections: 24
server accepts handled requests
1156958 1156958 4491319
Reading: 0 Writing: 18 Waiting : 6
```

> Note that if you are trying to access the status page from a remote machine, you will need to whitelist the remote machine’s IP address in your status configuration, just as 127.0.0.1 is whitelisted in the configuration snippet above.

リモートマシンからステータスページにアクセスしようとしている場合、先の`server`ブロック例の`allow`部分にリモートマシンのIPアドレスを追記する必要があります。(上記の紹介例は、127.0.0.1のみかホワイトリストとして記述されています。)

> The NGINX status page is an easy way to get a quick snapshot of your metrics, but for continuous monitoring you will need to automatically record that data at regular intervals. Parsers for the NGINX status page already exist for monitoring tools such as [Nagios](https://exchange.nagios.org/directory/Plugins/Web-Servers/nginx) and [Datadog](http://docs.datadoghq.com/integrations/nginx/), as well as for the statistics collection daemon [collectD](https://collectd.org/wiki/index.php/Plugin:nginx).

NGINXのステータスページは、メトリクスの現状を把握するための簡単な方法です。しかし、継続的な監視のためには、データを一定時間ごとに自動で記録していく必要があります。NGINXのステータスページを読み取るパーサーは、[Nagios](https://exchange.nagios.org/directory/Plugins/Web-Servers/nginx) や [Datadog](http://docs.datadoghq.com/integrations/nginx/)や[collectD](https://collectd.org/wiki/index.php/Plugin:nginx)(統計データーを収集するためのデーモンソフト)のようなモニタリングツール向けに既に存在しています。

### Metrics collection: NGINX Plus

> The commercial NGINX Plus provides [many more metrics](http://nginx.org/en/docs/http/ngx_http_status_module.html#data) through its ngx\_http\_status\_module than are available in open-source NGINX. Among the additional metrics exposed by NGINX Plus are bytes streamed, as well as information about upstream systems and caches. NGINX Plus also reports counts of all HTTP status code types (1xx, 2xx, 3xx, 4xx, 5xx). A sample NGINX Plus status board is available [here](http://demo.nginx.com/status.html).

商用版のNGINX Plusは、ngx\_http\_status\_moduleを介し、オープンソース版のNGINXよりも[多くのメトリクス](http://nginx.org/en/docs/http/ngx_http_status_module.html#data) を提供しています。NGINX Plus上で追加提供されているメトリクスには、送信したバイト数、Upstreamシステムやキャシュの情報などが有ります。更に、NGINX Plusは、HTTPのステータスコードタイプ(1xx, 2xx, 3xx, 4xx, 5xx)の集計値もリポーティングしています。NGINX Plusのステータスボードのサンプルは[ここから](http://demo.nginx.com/status.html)見ることができます。

[![NGINX Plus status board](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/status_plus-2.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-06-nginx/status_plus-2.png)

> *Note: the “Active” connections on the NGINX Plus status dashboard are defined slightly differently than the Active state connections in the metrics collected via the open-source NGINX stub status module. In NGINX Plus metrics, Active connections do not include connections in the Waiting state (aka Idle connections).*

*注: NGINX Plusのステータスダッシュボード上の"Active"コネクション数と、オープンソース版のNGINXの”stub status module”を介して収集した"Active"コネクション数とは、微妙に異なった定義がされています。NGINX Plus メトリクスでは、"Active"コネクションには、"Waiting"ステータス(NGINX Plusでは、"Idle"ステータス)のコネクションは含まれていません。*

> NGINX Plus also reports [metrics in JSON format](http://demo.nginx.com/status) for easy integration with other monitoring systems. With NGINX Plus, you can see the metrics and health status [for a given upstream grouping of servers](http://demo.nginx.com/status/upstreams/demoupstreams), or drill down to get a count of just the response codes [from a single server](http://demo.nginx.com/status/upstreams/demoupstreams/0/responses) in that upstream:

更にNGINX Plusでは、他の監視システムと連携しやすいように、[JSON形式でメトリクス](http://demo.nginx.com/status) をレポーティングできるようになっています。NGINX Plusを使用すると、[特定のUpstreamサーバーグループ](http://demo.nginx.com/status/upstreams/demoupstreams)のメトリクスや健全性を把握することができます。また、upstreamに属している[単一サーバー](http://demo.nginx.com/status/upstreams/demoupstreams/0/responses)にドリルインし、レスポンスコードの数を取得することもできます。

```
{"1xx":0,"2xx":3483032,"3xx":0,"4xx":23,"5xx":0,"total":3483055}
```

> To enable the NGINX Plus metrics dashboard, you can add a status `server` block inside the `http` block of your NGINX configuration. ([See the section above](#open-source) on collecting metrics from open-source NGINX for instructions on locating the relevant config files.) For example, to set up a status dashboard at `http://your.ip.address:8080/status.html` and a JSON interface at `http://your.ip.address:8080/status`, you would add the following server block:

NGINX Plusのメトリクスダッシュボードを有効にすには、NGINXの設定ファイルの`http`ブロック内の`server`ブロックに設定情報を追記します。（該当する設定ファイルを特定する手順については、[「collecting metrics from open-source NGINX」](#open-source)のセクションを参照してください）
例えば、`http://your.ip.address:8080/status.html` にステータスダッシュボードを設定し、`http://your.ip.address:8080/status`にJSONインターフェースを設定するには、次のような`server`ブロックを追記ます。

```
server {
    listen 8080;
    root /usr/share/nginx/html;

    location /status {
        status;
    }

    location = /status.html {
    }
}
```

> The status pages should be live once you reload your NGINX configuration:

以下のコマンドでNGINXの設定を再度読み込めば、ステータスページは閲覧可能になります:

```
nginx -s reload
```

> The official NGINX Plus docs have [more details](http://nginx.org/en/docs/http/ngx_http_status_module.html#example) on how to configure the expanded status module.

NGINX Plusの公式ドキュメントには、拡張ステータスモジューの[設定に関し更に詳しい](http://nginx.org/en/docs/http/ngx_http_status_module.html#example) 記述があります。

### Metrics collection: NGINX logs

> NGINX’s [log module](http://nginx.org/en/docs/http/ngx_http_log_module.html) writes configurable access logs to a destination of your choosing. You can customize the format of your logs and the data they contain by [adding or subtracting variables](http://nginx.org/en/docs/http/ngx_http_log_module.html#log_format). The simplest way to capture detailed logs is to add the following line in the `server` block of your config file (see [the section](#open-source) on collecting metrics from open-source NGINX for instructions on locating your config files):

NGINXの[log module](http://nginx.org/en/docs/http/ngx_http_log_module.html)は、任意の保存先に対してアクセスログをかき出してくれます。出力するログのフォーマットとそれに含まれるデーターは、設定ファイルの[変数を追加したり削除する]http://nginx.org/en/docs/http/ngx_http_log_module.html#log_format)ことでカスタマイズすることができます。詳細なログを記録する最も簡単な方法は、設定ファイルに、次に紹介する行を`server`ブロック内に追記することです。（該当する設定ファイルを特定する手順については、[「collecting metrics from open-source NGINX」](#open-source)のセクションを参照してください）

```
access_log logs/host.access.log combined;
```

> After changing any NGINX configurations, reload the configs by executing:

NGINXの設定を変更した場合は、次のコマンドを実行し、設定を読み込ませます:

```
nginx -s reload
```

> The “combined” log format, included by default, captures [a number of key data points](http://nginx.org/en/docs/http/ngx_http_log_module.html#log_format), such as the actual HTTP request and the corresponding response code. In the example logs below, NGINX logged a 200 (success) status code for a request for /index.html and a 404 (not found) error for the nonexistent /fail.

デフォルトで設定されている“combined”のログ形式は、実際のHTTPリクエストと、そのリクエストの処理結果のレスポンスコードなどの[重要なデーター](http://nginx.org/en/docs/http/ngx_http_log_module.html#log_format)を記録します。以下に示すログの例では、NGINXは、`/index.html`のURLに対し200 (success)のステータスをログ出力し、存在していない`/fail`のURLに対し404 (not found)のエラーをログ出力します。

```
127.0.0.1 - - [19/Feb/2015:12:10:46 -0500] "GET /index.html HTTP/1.1" 200 612 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari 537.36"

127.0.0.1 - - [19/Feb/2015:12:11:05 -0500] "GET /fail HTTP/1.1" 404 570 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36"
```

> You can log request processing time as well by adding a new log format to the `http` block of your NGINX config file:

NGINXの設定ファイルの`http`ブロックに新しいログフォーマットを追記することで、`request processing time`をログ出力することができます:

```
log_format nginx '$remote_addr - $remote_user [$time_local] '
                 '"$request" $status $body_bytes_sent $request_time '
                 '"$http_referer" "$http_user_agent"';
```

> And by adding or modifying the access\_log line in the `server` block of your config file:

その上で、設定ファイルの`server`ブロックのaccess\_logの部分を以下に紹介する行で着替えたり、追記したりします:

```
access_log logs/host.access.log nginx;
```

> After reloading the updated configs (by running `nginx -s reload`), your access logs will include response times, as seen below. The units are seconds, with millisecond resolution. In this instance, the server received a request for /big.pdf, returning a 206 (success) status code after sending 33973115 bytes. Processing the request took 0.202 seconds (202 milliseconds):

`nginxの-s reload`を実行し更新した設定ファイルを再度読み込むと、以下に示したように、アクセスログには"response times"を含んだログが出力されるようになります。単位は秒で、分解能はミリ秒です。この例では、サーバーは`/big.pdf`を送信するリクエストを受信しました。その結果、33973115 bytesを送信し、206 (success)コードを送信しました。このリクエストを処理するのに0.202秒(202ミリ秒)の時間がかかりました:

```
127.0.0.1 - - [19/Feb/2015:15:50:36 -0500] "GET /big.pdf HTTP/1.1" 206 33973115 0.202 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36"
```

> You can use a variety of tools and services to parse and analyze NGINX logs. For instance, [rsyslog](http://www.rsyslog.com/) can monitor your logs and pass them to any number of log-analytics services; you can use a free, open-source tool such as [logstash](https://www.elastic.co/products/logstash) to collect and analyze logs; or you can use a unified logging layer such as [Fluentd](http://www.fluentd.org/) to collect and parse your NGINX logs.

NGINXのログをパースして解析するには、さまざまなツールやサービスを利用することができます。例えば、[rsyslog](http://www.rsyslog.com/) は、ログを監視し、各種のログ解析サービスに転送することができます。また、無料でオープンソースのツールの[logstash](https://www.elastic.co/products/logstash)でログを収取し解析することもできます。更に、[Fluentd](http://www.fluentd.org/)のような統合的ログハンドリングツールを使いNGINXのログを収集しパースすることもできます。

## Conclusion

> Which NGINX metrics you monitor will depend on the tools available to you, and whether the insight provided by a given metric justifies the overhead of monitoring that metric. For instance, is measuring error rates important enough to your organization to justify investing in NGINX Plus or implementing a system to capture and analyze logs?

どのNGINXメトリクスを監視するかは、利用可能なツールに依存します。又、それぞれのメトリクスが提供する見識の価値こそがそのメトリクスを監視するためにかかる労力を正当化してくれるでしょう。例えば、NGINX Plusに投資したり、ログを取り込んで解析するシステムを構築するほどエラーの発生率はあなたの組織にとって重要なのでしょうか？

> At Datadog, we have built integrations with both NGINX and NGINX Plus so that you can begin collecting and monitoring metrics from all your web servers with a minimum of setup. Learn how to monitor NGINX with Datadog [in this post](/blog/how-to-monitor-nginx-with-datadog/), and get started right away with [a free trial of Datadog](https://app.datadoghq.com/signup).

Datadogでは、NGINXとNGINX Plus用の両方に向けてIntegrationを提供しています。これらのIntegrationを採用することで、最小限の設定で全てのwebのメトリクスを収集し監視できるようになります。このシリーズに含まれる[「How to monitor NGINX with Datadog」][31]では、Datadogを使ったNGINXの監視方法を解説しています。このポストを参考に、Datadogの[無料トライアルアカウント][32]に登録し、NGINXの監視を是非始めてみてください。

------------------------------------------------------------------------

> *Source Markdown for this post is available [on GitHub](https://github.com/DataDog/the-monitor/blob/master/nginx/how_to_collect_nginx_metrics.md). Questions, corrections, additions, etc.? Please [let us know](https://github.com/DataDog/the-monitor/issues).*

*このポストのMarkdownソースは、[GitHub](https://github.com/DataDog/the-monitor/blob/master/nginx/how_to_collect_nginx_metrics.md)で閲覧することができます。質問、訂正、追加、などがありましたら、[GitHubのissueページ](https://github.com/DataDog/the-monitor/issues)を使って連絡を頂けると幸いです。*
