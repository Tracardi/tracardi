Version 0.7.4
----------------------------------------------------------

## Features

* Plugins:
  * Google analytics 4 plugin
  * Github plugins
  * New if plugin
  * New discord plugin
* Event redirect bridge (collector)
* Upgrade to node v18.12.1
* Profile synchronisation configuration in the event source
* Storage access refactoring
* Event source configuration caching
* Event validation schema caching
* Event tagging schema caching
* Minor GUI changes
* Event source configuration form display for more advanced bridges
* Performance tweaks
* Event data display configuration 
* Major redo of collection engine.
* Event indexing inside the event metadata configuration
* New GUI display configuration 
* Errors
  * Fixed bridge error
  * Profile duplication fix

Version 0.7.3
----------------------------------------------------------

## Features

* Livechat plugin
* Hubspot plugin
* Google translator plugin
* Twitter plugin
* SMS77 plugin
* Zendesk chat plugin
* Intercom plugin
* Chatwoot chat plugin
* Plugin that sorts dictionary
* Join array of strings into string plugin
* String similarity plugin
* Whois plugin
* New resource details page
* New event source details page
* Command CONTAINS, STARTS_WTH and ENDS_WITH to IF plugin
* SMTP Mail bride
* MQTT bridge
* Added plugins regarding segmentation (has segment, memorize segment, recall segment, etc.)
* "Load profile by ..." plugin
* Live segmentation server
* Adds missing documentation for:
  * ActiveCampaign resource
  * SendGrid resource
  * Salesforce resource
  * MQTT Resource
  * RabbitMQ resource 
  * Zapier resource
  * InfluxDB resource
* Adds missing documentation for some plugins
* New menu and data layout
* Better debugging. More information on logs. Plugins now have their error log.
* Better time zone handling
* Errors
  * Problem with connecting nodes in graph 
  * Missing session timeline
  * Solves problem with missing destinations
  * Fixed issues with dates
* Misc
  * Upgrade to python 3.9
