#How to Collect DynamoDB Metrics

*This post is part 2 of a 3-part series on monitoring DynamoDB. [Part 1](https://www.datadoghq.com/blog/top-dynamodb-performance-metrics) explores its key performance metrics, and [Part 3](https://www.datadoghq.com/blog/how-medium-monitors-dynamodb-performance) describes the strategies Medium uses to monitor DynamoDB.*

This section of the article is about collecting native DynamoDB metrics, which are available exclusively from AWS via CloudWatch. For other non-native metrics, see [Part 3](https://www.datadoghq.com/blog/how-medium-monitors-dynamodb-performance).

CloudWatch metrics can be accessed in three different ways:

-   [Using the AWS Management Console and its web interface](#console)
-   [Using the command-line interface (CLI)](#cli)
-   [Using a monitoring tool integrating the CloudWatch API](#integrations)

## Using the AWS Management Console

Using the online management console is the simplest way to monitor DynamoDB with CloudWatch. It allows you to set up simple automated alerts, and get a visual picture of recent changes in individual metrics.

### Graphs

Once you are signed in to your AWS account, you can open the [CloudWatch console](https://console.aws.amazon.com/cloudwatch/home) where you will see the metrics related to the different AWS technologies.

[![CloudWatch console](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/2-01b.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/2-01b.png)

By clicking on DynamoDB’s “Table Metrics” you will see the list of your tables with the available metrics for each one:

[![DynamoDB metrics in CloudWatch](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/2-02b.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/2-02b.png)

Just select the checkbox next to the metrics you want to visualize, and they will appear in the graph at the bottom of the console.

[![DynamoDB metric graph in CloudWatch](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/2-03b.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/2-03b.png)

### Alerts

With the CloudWatch Management Console you can also create alerts which trigger when a certain metric threshold is crossed.

Click on **Create Alarm** at the right of your graph, and you will be able to set up the alert, and configure it to notify a list of email addresses:

[![DynamoDB CloudWatch alert](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/2-04b.png)](https://d33tyra1llx9zy.cloudfront.net/blog/images/2015-09-dynamodb/2-04b.png)

## Using the Command Line Interface

You can also retrieve metrics related to a specific table using the command line. To do so, you will need to install the AWS Command Line Interface by following [these instructions](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html). You will then be able to query for any CloudWatch metrics you want, using different filters.

Command line queries can be useful for spot checks and ad hoc investigations when you can’t or don’t want to use a browser.

For example, if you want to retrieve the metrics related to `PutItem` requests throttled during a specified time period, you can run:

<table>
<colgroup>
<col width="50%" />
<col width="50%" />
</colgroup>
<tbody>
<tr class="odd">
<td align="left"><div class="crayon-pre" style="font-size: 14px !important; line-height: 18px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;">
<div id="crayon-55fc5b58d1fde637588618-1" class="crayon-line">
 
</div>
<div id="crayon-55fc5b58d1fde637588618-2" class="crayon-line">
aws cloudwatch get-metric-statistics
</div>
<div id="crayon-55fc5b58d1fde637588618-3" class="crayon-line">
--namespace AWS/DynamoDB  --metric-name ThrottledRequests
</div>
<div id="crayon-55fc5b58d1fde637588618-4" class="crayon-line">
--dimensions Name=TableName,Value=YourTable Name=Operation,Value=PutItem
</div>
<div id="crayon-55fc5b58d1fde637588618-5" class="crayon-line">
--start-time 2015-08-02T00:00:00Z --end-time 2015-08-04T00:00:00Z
</div>
<div id="crayon-55fc5b58d1fde637588618-6" class="crayon-line">
--period 300 --statistics=Sum
</div>
<div id="crayon-55fc5b58d1fde637588618-7" class="crayon-line">
 
</div>
</div></td>
</tr>
</tbody>
</table>

Here is an example of a JSON output format you will see from a “get-metric-statistics“ query like above:

<table>
<colgroup>
<col width="50%" />
<col width="50%" />
</colgroup>
<tbody>
<tr class="odd">
<td align="left"><div class="crayon-pre" style="font-size: 14px !important; line-height: 18px !important; -moz-tab-size:4; -o-tab-size:4; -webkit-tab-size:4; tab-size:4;">
<div id="crayon-55fc5b58d1fed521769294-1" class="crayon-line">
 
</div>
<div id="crayon-55fc5b58d1fed521769294-2" class="crayon-line">
{
</div>
<div id="crayon-55fc5b58d1fed521769294-3" class="crayon-line">
    &quot;Datapoints&quot;: [
</div>
<div id="crayon-55fc5b58d1fed521769294-4" class="crayon-line">
        {
</div>
<div id="crayon-55fc5b58d1fed521769294-5" class="crayon-line">
            &quot;Timestamp&quot;: &quot;2015-08-02T11:18:00Z&quot;,
</div>
<div id="crayon-55fc5b58d1fed521769294-6" class="crayon-line">
            &quot;Average&quot;: 44.79,
</div>
<div id="crayon-55fc5b58d1fed521769294-7" class="crayon-line">
            &quot;Unit&quot;: &quot;Count&quot;
</div>
<div id="crayon-55fc5b58d1fed521769294-8" class="crayon-line">
        },
</div>
<div id="crayon-55fc5b58d1fed521769294-9" class="crayon-line">
        {
</div>
<div id="crayon-55fc5b58d1fed521769294-10" class="crayon-line">
            &quot;Timestamp&quot;: &quot;2015-08-02T20:18:00Z&quot;,
</div>
<div id="crayon-55fc5b58d1fed521769294-11" class="crayon-line">
            &quot;Average&quot;: 47.92,
</div>
<div id="crayon-55fc5b58d1fed521769294-12" class="crayon-line">
            &quot;Unit&quot;: &quot;Count&quot;
</div>
<div id="crayon-55fc5b58d1fed521769294-13" class="crayon-line">
        },
</div>
<div id="crayon-55fc5b58d1fed521769294-14" class="crayon-line">
        {
</div>
<div id="crayon-55fc5b58d1fed521769294-15" class="crayon-line">
            &quot;Timestamp&quot;: &quot;2015-08-02T19:18:00Z&quot;,
</div>
<div id="crayon-55fc5b58d1fed521769294-16" class="crayon-line">
            &quot;Average&quot;: 50.85,
</div>
<div id="crayon-55fc5b58d1fed521769294-17" class="crayon-line">
            &quot;Unit&quot;: &quot;Count&quot;
</div>
<div id="crayon-55fc5b58d1fed521769294-18" class="crayon-line">
        },
</div>
<div id="crayon-55fc5b58d1fed521769294-19" class="crayon-line">
    ],
</div>
<div id="crayon-55fc5b58d1fed521769294-20" class="crayon-line">
    &quot;Label&quot;: &quot;ThrottledRequests&quot;
</div>
<div id="crayon-55fc5b58d1fed521769294-21" class="crayon-line">
}
</div>
<div id="crayon-55fc5b58d1fed521769294-22" class="crayon-line">
 
</div>
</div></td>
</tr>
</tbody>
</table>

## Integrations

The third way to collect CloudWatch metrics is via your own monitoring tools which can offer extended monitoring functionality. For example if you want the ability to correlate metrics from one part of your infrastructure with other parts (including custom infrastructure or applications), or you want to dynamically slice, aggregate, and filter your metrics on any attribute, or you need specific alerting mechanisms, you probably are using a dedicated monitoring tool or platform. CloudWatch can be integrated with these platforms via API, and in many cases the integration just needs to be enabled to start working.

In [Part 3](https://www.datadoghq.com/blog/how-medium-monitors-dynamodb-performance), we cover a real-world example of this type of metrics collection: [Medium](https://medium.com/)’s engineering team monitors DynamoDB using an integration with Datadog.

## Conclusion

In this post we have walked through how to use CloudWatch to collect and visualize DynamoDB metrics, and how to generate alerts when these metrics go out of bounds.

As discussed in [Part 1](https://www.datadoghq.com/blog/top-dynamodb-performance-metrics), DynamoDB can’t see, or doesn’t report on all the events that you likely want to monitor, including true latency and error rates. In the [next and final part on this series](https://www.datadoghq.com/blog/how-medium-monitors-dynamodb-performance) we take you behind the scenes with Medium’s engineering team to learn about the issues they’ve encountered, and how they’ve solved them with a mix of tools which includes CloudWatch, ELK, and Datadog.





この投稿は、監視DynamoDBの上の3回シリーズの第2部です。第1部では、その主要なパフォーマンスメトリックを探り、そして第3部はミディアムDynamoDBのを監視するために使用する戦略を説明します。
記事のこのセクションでは、CloudWatchのを経由して、AWSからのみ利用可能ですネイティブDynamoDBのメトリックを収集についてです。他の非ネイティブメトリックの場合、パート3を参照してください。
CloudWatchのメトリックは、次の3つの方法でアクセスできます。
AWS Management ConsoleおよびWebインターフェイスを使用します
コマンドラインインターフェイス（CLI）を使用して
CloudWatchのAPIを統合監視ツールを使用して
AWS管理コンソールを使用して
オンライン管理コンソールを使用すると、CloudWatchのでDynamoDBのを監視するための最も簡単な方法です。それはあなたが簡単な自動化されたアラートを設定し、個々のメトリックの最近の変化を視覚的に把握することができます。
グラフ
あなたのAWSアカウントにサインインしたら、あなたは別のAWS技術に関連するメトリックが表示されますCloudWatchのコンソールを開くことができます。
CloudWatchのコンソール
DynamoDBのの「表メトリック」をクリックすると、それぞれで使用可能なメトリックを使用してテーブルの一覧が表示されます。
CloudWatchの中DynamoDBのメトリック
ちょうどあなたが視覚化するメトリックの横にあるチェックボックスを選択して、彼らは、コンソールの下部にグラフに表示されます。
CloudWatchの中DynamoDBのメトリックグラフ
アラート
CloudWatchの管理コンソールを使用すると、特定のメトリックしきい値を超えた場合にトリガし、アラートを作成することができます。
グラフの右側にアラームの作成をクリックすると、アラートを設定し、電子メールアドレスのリストを通知するように設定することができるようになります：
DynamoDBのCloudWatchのアラート
コマンドラインインタフェースの使用
また、コマンドラインを使用して、特定のテーブルに関連するメトリックを取得することができます。これを行うには、次の手順に従って、AWSコマンドラインインタフェースをインストールする必要があります。その後、別のフィルタを使用して、あなたが望む任意のCloudWatchのメトリックを照会することができるようになります。
あなたがまたはブラウザを使用したくないことができない場合、コマンドラインクエリは、スポットチェックやアドホック調査のために有用であり得ます。
あなたが指定した期間に絞らPutItem要求に関連するメトリックを取得したい場合たとえば、次のコマンドを実行します。
1
2
3
4
5
6
7
 
AWS CloudWatchのGETメトリック統計
--namespace AWS / DynamoDBの--metric名ThrottledRequests
--dimensions名=テーブル名、値= YourTable名前=操作、値= Put​​Item
--start-時間2015-08-02T00：00：00Z --end-時間2015-08-04T00：00：00Z
--period 300 --statistics =合計
 
ここでは、上記のようには、「get-メトリック統計」をクエリから表示されますJSON出力フォーマットの例を示します。
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
 
{
    「データポイント」：[
        {
            「タイムスタンプ」： "2015-08-02T11：18：00Z」、
            "平均"：44.79、
            "単位"： "カウント"
        }、
        {
            「タイムスタンプ」： "2015-08-02T20：18：00Z」、
            "平均"：47.92、
            "単位"： "カウント"
        }、
        {
            「タイムスタンプ」： "2015-08-02T19：18：00Z」、
            "平均"：50.85、
            "単位"： "カウント"
        }、
    ]、
    「ラベル」：「ThrottledRequests」
}
 
統合
CloudWatchのメトリックを収集するための第三の方法は、拡張された監視機能を提供することができ、独自の監視ツールを介して行われます。たとえば、あなたが（カスタムインフラストラクチャやアプリケーションを含む）他の部分と、インフラストラクチャの一部からメトリックを相互に関連付けることをしたい、またはあなたが動的にスライスする場合、集約、および任意の属性にあなたのメトリックをフィルタリングするか、特定の警告メカニズムを必要とします、あなたはおそらく、専用の監視ツールやプラットフォームを使用しています。 CloudWatchのは、APIを介してこれらのプラットフォームに統合することができ、多くの場合、統合は、単に作業を開始するために有効にする必要があります。
第3部では、指標の収集のこのタイプの実際の例をカバー：ミディアムのエンジニアリングチームはDatadogとの統合を使用してDynamoDBのを監視します。
まとめ
この記事では、DynamoDBのメトリックを収集し、視覚化するCloudWatchの使用方法を歩いていると、これらの指標が範囲外に行くとどのようにアラートを生成します。
第1部で述べたように、DynamoDBのは見ることができない、または真の待ち時間とエラーレートを含む、あなたが可能性が監視するすべてのイベント、に報告しません。このシリーズの次のと最後の部分で我々は、彼らが遭遇した問題について学ぶ中のエンジニアリングチームとの舞台裏あなたを取る、と彼らはCloudWatchの、ELK、およびDatadogを含んツールの組み合わせでそれらを解決しましたか。
