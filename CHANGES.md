Version: 0.8.1
----------------------------------------------------------
* New Dashboard
* New Profile Details Page
* Extended analytics
* Debugging in context of event
* Static Profile ID generator
* Passing Profile ID between owned domains
* Predefined events 
* New Data Schema
* Better Production/Testing switching
* Tracardi now can handle coping event data to profiles and event indexing on historical data (pro)
* Better autocomplete of event properties
* Session open, Session close, Internal events
* Update documentation
* Added or Modified Plugins
  * Weaviate (Vector store for AI) (pro)
    * Add
    * Read
    * Delete
    * Exists
  * Twilio plugin (pro)
  * Rating Widget (pro)
  * Youtube widget (pro)
  * Demo widget (pro)
  * Custom Javascript Widget (pro)
  * Send tweet
  * Google UA Events
  * Event aggregator (pro)
  * Event counter (pro)
  * ChatGPT prompt (pro)
* Misc
  * Upgrade to python 3.9
  * Performance tweaks

Version 0.8.0
----------------------------------------------------------

## Features

* Clear separation of test and production data
* Fixed profile merging
* Upgrade to React 18
* Cleaner Menu
* Visualisation of events routing 
* Routing added to event details
* Installer refactoring
* Plugins
  * Profile live time plugin
  * Corrected API call plugin
  * Several minor changes to plugins
  * Changed or added plugins:
    * API Call
    * Elastic query
    * Novu
    * Telegram
    * Property exists
    * Start
    * Event tag
    * Redis
    * Profile live time
    * Cut out traits
* Commercial features:
  * Wait and resume plugin
  * Identity resolution (Identification points)
  * Cleaner marking of Commercial features
  * ChatGPT plugin
  * Kafka bridge 
  * SMTP bridge for bounced emails.
  * Event to profile coping (realtime and manual)


Version 0.7.4
----------------------------------------------------------

## Features

* Plugins:
  * Google analytics 4 plugin
  * Github plugins
  * New if plugin
  * New discord plugin
* Upgrade to node v18.12.1
* Profile synchronisation configuration moved from envs to the event source
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
* New Bridge API for developers
* Installation token for protecting uninstalled instances
* Security fixes - Removing envs with credentials
* Errors
  * Fixed bridge error
  * Profile duplication fix
* Commercial features:
  * Event redirect bridge (collector)
  * Webhook bridge
  * Background processes for profile merging and deduplication

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
