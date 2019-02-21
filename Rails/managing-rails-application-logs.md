---
Logging is an important part of understanding the behavior of your applications. Your logs contain essential records of application operations including database queries, server requests, and errors. With proper logging, you always have comprehensive, context-rich insights into application usage and performance. In this post, we'll walk through logging options for Rails applications and look at some best practices for creating informative logs. We will also show you how to further enhance the usefulness of your logs using the Lograge library. 

Note that this guide uses examples and commands for a Rails 5.2.0 application on a Linux host. If your environment is different, you may need to modify these commands where appropriate.
## Working with log levels
Rails applications come with three environment configurations, found in the **config/environments/** directory: _development.rb_, _test.rb_, and _production.rb_. All environments create a corresponding log file in the **logs** directory once the application begins generating logs. Since Rails serves applications in the development environment by default, logs are automatically written to a **development.log** file. 

Rails uses six different log levels: _debug_, _info_, _warn_, _error_, _fatal_, and _unknown_. Each level defines how much information your application will log:

* **Debug**: diagnostic information for developers and system administrators, including database calls or inspecting object attributes. This is the most verbose log level.
* **Info**: useful information about normal application operations such as services starting or stopping.
* **Warn**: operations that an application can easily recover from but should be addressed soon. This could include using an out-of-date gem or retrying an operation.
* **Error**: errors that cause an operation to fail (e.g., missing data or files) but not the application. The issue should be resolved soon, but the application can log the exception and continue running.
* **Fatal**: errors that cause the application to crash and should be addressed immediately to prevent further data loss.
* **Unknown**: messages that are not classified by any other level but should be logged. 

The _debug_ and _info_ levels log the most information about application behavior, while the higher levels only log warnings or errors. By default, Rails applications generate logs at the _debug_ level for all environments, including production. A single _debug_ log entry can carry a lot of information:

```
Started POST "/articles" for 127.0.0.1 at 2018-06-27 15:48:10 +0000
Processing by ArticlesController#create as HTML
  Parameters: {"utf8"=>"✓", "article"=>{"title"=>"Create New Post", "text"=>"Description for new post"}, "commit"=>"Save Article"}
  [1m[35m (0.2ms)[0m  [1m[35mBEGIN[0m
  ↳ app/controllers/articles_controller.rb:20
  [1m[36mArticle Create (1.0ms)[0m  [1m[32mINSERT INTO "articles" ("title", "text", "created_at", "updated_at") VALUES ($1, $2, $3, $4) RETURNING "id"[0m  [["title", "Create New Post"], ["text", "Description for new post"], ["created_at", "2018-06-27 15:48:11.116208"], ["updated_at", "2018-06-27 15:48:11.116208"]]
  ↳ app/controllers/articles_controller.rb:20
  [1m[35m (0.5ms)[0m  [1m[35mCOMMIT[0m
  ↳ app/controllers/articles_controller.rb:20
Redirected to http://localhost:3000/articles/29
Completed 302 Found in 25ms (ActiveRecord: 4.5ms)
```

Since this log level includes the most diagnostic information related to your application, it's valuable for development or test environments. However, it may be too verbose for production environments. You can adjust the log level for any environment by editing the applicable environment file:

```
# config/environments/development.rb
config.log_level = :info
```

The _info_ log level will still include information about individual requests but will exclude any low-level, diagnostic information:

```
Started POST "/articles" for 10.0.2.2 at 2018-06-06 18:06:18 +0000
Cannot render console from 10.0.2.2! Allowed networks: 127.0.0.1, ::1, 127.0.0.0/127.255.255.255
Processing by ArticlesController#create as HTML
  Rendering articles/new.html.erb within layouts/application
  Rendered articles/new.html.erb within layouts/application (1.8ms)
Completed 200 OK in 146ms (Views: 140.7ms | ActiveRecord: 0.3ms)
```
### Interpreting your logs
Both example logs shown above contain information useful for understanding typical application behavior and operations:

* **Request and URL endpoint**: an HTTP request method (e.g., GET, POST, or PUT) sent to a specific URL endpoint for the application
* **Controller and action**: a method called to complete the request, mapped by the application [router](http://guides.rubyonrails.org/routing.html) 
* **Templates and partials**: the files needed to generate the appropriate web page views for the URL endpoint
* **Request status**: the HTTP status codes generated for a completed request and their elapsed response time

At the _debug_ level, logs contain more diagnostic information, in addition to the data listed above:

* **Parameters**: data retrieved or sent as part of a URL or HTTP request method
* **Database calls**: the [ActiveRecord](http://guides.rubyonrails.org/active_record_basics.html) query called to retrieve data necessary for the request 

The status at the end of each log shows if a request generated either a successful response (2xx), a redirect (3xx), a client error (4xx), or a server error (5xx). A client error can indicate a page in the application is missing, while a server error could mean a server is rebooting (or down altogether). If your application generates either a client or server error, you will also see its stack trace in the log so you can more easily find the root cause and resolve the issue:

```
Started GET "/articles/1" for 127.0.0.1 at 2018-06-27 15:42:44 +0000
Processing by ArticlesController#show as HTML
  Parameters: {"id"=>"1"}
Completed 500 Internal Server Error in 49ms (ActiveRecord: 0.0ms)
  
NameError (uninitialized constant ArticlesController::Article):
  
app/controllers/articles_controller.rb:7:in `show'
```

When debugging an issue, you can refer to logs in order to understand what is causing unexpected or unwanted behavior in your application. For example, if you are not seeing the appropriate page for a request then you may see the following error: 

```
No route matches [GET] "/sign_up"
```

This error indicates that there may be an issue with your mapped routes in the **config/routes.rb** file.
The router maps URLs and HTTP requests through the appropriate controller so the application can respond by serving the right web page. This could include showing a specific page (GET) or editing existing data (PUT). 

Even in their default format, Rails logs provide information that can be very helpful in troubleshooting common application errors. To collect a greater amount of detail, you can add custom logging for Rails. 
## Customizing your logs
To further enhance the logs your application generates, you can create customized logs with the [ActiveSupport::Logger class](http://guides.rubyonrails.org/debugging_rails_applications.html#what-is-the-logger-questionmark). This class is built-in for Rails 5.2+ applications and offers methods for creating and tagging custom logs. Let's take a look at how the logger class can be used to instrument the following example method, which retrieves information about a single article selected from a list:

```
def show
  @article = Article.find(params[:id])
end
```

If you want to log specific attributes about an article when it is selected in the application, you can extend the method to include a custom logging statement:

```
def show
  @article = Article.find(params[:id])
  logger.debug "Article Information: #{@article.attributes.inspect}"
end
```

The Ruby [**inspect** method](https://ruby-doc.org/core-2.5.1/Object.html#method-i-inspect) prints out all attributes associated with the selected event, including timestamps, ids, and form field values. Now, whenever an article is selected, your application will generate a log similar to this at the _debug_ level:

```
Article Information: {"id"=>6, "title"=>"New Article", "text"=>"Creating a new article.", "created_at"=>Tue, 19 Jun 2018 14:46:48 UTC +00:00, "updated_at"=>Tue, 19 Jun 2018 14:46:48 UTC +00:00}
```

As with your Rails environments, you can set any log level to your custom logs. The **logger.debug** statement in the example above is best for showing more diagnostic information in your logs while you are developing features. Both **logger.warn** and **logger.error** statements can be used for custom warnings or exceptions wrapped around specific operations in your application. It's important to note the log level of your environment, as that determines what is logged. Your application won't log **logger.debug** statements, for example, if its environment is set to the _warn_ level. 

Rails enables you to create any type of log for your application out-of-the-box and set appropriate log levels. In small applications, Rails manages logs well, so you can easily debug issues without the need for third-party libraries. As your application grows, however, you will need to consider how to better manage the volume of logs it generates.
## Transforming logs with Lograge
Production applications can generate logs for multiple processes at the same time, mixing the data together and making it harder to piece together information from your logs. You can manage this complexity by using libraries that transform your Rails logs into a format that is easier to parse and read. Lograge, for example, is a library that easily cleans up Rails logs and converts them into several possible formats, including JSON. 

To get started with Lograge, add `gem 'lograge'` and `gem 'lograge-sql'` to your Gemfile and install them with: 

```
bundle install
```

The `lograge-sql` [gem](https://github.com/iMacTia/lograge-sql) is an extension of Lograge that adds all database queries generated at the _debug_ log level to your newly formatted JSON logs. 

You can easily enable and configure third-party libraries with initializer files, and Rails will include them automatically while serving the application. Rails loads initializer files after the application framework and associated gems. Create a **lograge.rb** file in your project’s **config/initializers** folder and include the following code snippet:

```
#config/initializers/lograge.rb
require 'lograge/sql/extension'

Rails.application.configure do
    # Lograge config
    config.lograge.enabled = true
    config.lograge.formatter = Lograge::Formatters::Json.new
    config.colorize_logging = false

    config.lograge.custom_options = lambda do |event|
      { :params => event.payload[:params] }
  end
end
```

The example initializer shown above loads the **lograge-sql** library and enables **Lograge**, replacing the standard Rails log format. Lograge supports [multiple formats](https://github.com/roidrage/lograge#installation), but this configuration uses the popular JSON formatter. We've also disabled [colorized logging](https://guides.rubyonrails.org/configuring.html#rails-general-configuration)—an option that is useful for console outputs but produces messy log files. You can add custom data to Lograge logs by using the `custom_options` hook; the example above incorporates all parameters related a request. 

Restart your Rails server so you can load the Lograge configuration and see the new log format in action:

```
rails s
```

Now, instead of seeing the standard, text-based log format, stripped of all ANSI color codes:  

```
Started GET "/articles" for 127.0.0.1 at 2018-06-19 14:46:53 +0000
Processing by ArticlesController#index as HTML
  Rendering articles/index.html.erb within layouts/application
  Article Load (0.4ms) SELECT "articles".* FROM "articles"
  ↳ app/views/articles/index.html.erb:11
  Rendered articles/index.html.erb within layouts/application (2.8ms)
Completed 200 OK in 150ms (Views: 119.9ms | ActiveRecord: 0.4ms)
```

You will see the following JSON log, which has much more structure:

```
{
"method":"GET",
"path":"/articles/",
"format":"html",
"controller":"ArticlesController",
"action":"index",
"status":200,
"duration":150,
"view":119.9,
"db":.4,
"params":{
   "controller":"articles",
   "action":"index"
},
"sql_queries":"'Article Load (0.47) SELECT \"articles\".* FROM \"articles\"'"
}
```

If you want to preserve your old logs and write the new JSON logs to a new file, you can include the following snippet in the same **lograge.rb** initializer file:

```
config.lograge.keep_original_rails_log = true
config.lograge.logger = ActiveSupport::Logger.new "#{Rails.root}/log/lograge_#{Rails.env}.log"
```
### Setting appropriate log levels
There is one important thing to note with how Lograge sets log levels. By default, Lograge sets all logs to an _info_ level, so even if your application logs an error, log aggregators may classify it as an info log. In order to set accurate log levels, you can customize how Lograge handles log levels by adding the following to your **application_controller.rb** file:

```
# controllers/application_controller.rb
def append_info_to_payload(payload)
      super
     case 
        when payload[:status] == 200
          payload[:level] = "INFO"
        when payload[:status] == 302
          payload[:level] = "WARN"
        else
          payload[:level] = "ERROR"
        end
end
```

This sets a conditional around specific request statuses and adds the appropriate log level to a new **level** variable, overriding the default level set by the Lograge library. Now you can add the `level` variable to the `custom_options` hook in your **lograge.rb** initializer file:

```
#config/initializers/lograge.rb
[...]
    config.lograge.custom_options = lambda do |event|
      { :params => event.payload[:params],
        :level => event.payload[:level],
      }
  end
```

Your logs will now include a new _level_ attribute set with the appropriate value, based on the request's HTTP status code:

```
{  
  [...]
   "status": 200,
   "level":"INFO"
}
```

With Rails and Lograge, you have a lot of flexibility in creating and generating logs in a format that works best for your needs. You can even create custom logs to view data for specific actions in your application. Rails works with multiple log levels so you can adjust your logging based on your environment. 

Now that your application is generating JSON logs with the appropriate log levels, you can [forward them to Datadog](https://docs.datadoghq.com/logs/) and begin monitoring your application logs alongside metrics, request traces, and other data from your applications and infrastructure. Read the [next post](/blog/managing-rails-logs-with-datadog/) in this series to learn more.
