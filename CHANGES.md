Version: 1.0.1
----------------------------------------------------------
* Refactored Data Access Layer


Version: 1.0.0
----------------------------------------------------------
* Versio 1.0.0 doe not require migration from version 0.9.0.x
* Refactored merging mechanism for commercial version
* New APM 
* News feed
* Bug fixes
* Fully compatible with 0.9.0
* WIth this version we will start using semantic version version 2
* New manual and documentation

Version: 0.9.0
----------------------------------------------------------
* GUI Dark theme.
* MySQL as a metadata store. Now only big data is stored in elastic search.
* New deployment process
* All workers have been replaced by one worker - simplifies the commercial installation
* Huge cost savings for multi tenant installations
* Audiences and Activations replaced the Workflow Segmentation
* Post Event Segmentation was removed.
* GitHub Workflow Push
* Auto events - not documented
* New build-in event types

Version: 0.8.2
----------------------------------------------------------
* Upgrade to pytantic v2
* Refactoring of the collector
  * Improved performance
  * Simpler code
  * Asynchronous workflows, destinations, etc. (pro)
* Auto profile merging - Automates merging profiles for difference sources/channels.
* Workers
  * Redone the scheduler worker (pro)
  * New distributed storage worker (pro)
  * New in-memory storage for profiles
  * New metrics worker (pro)
  * Redone visit-ended worker (pro)
  * Redone workflow async worker (pro)
* Fixed some GUI errors
* Preparation for KeyCloak oAuth authorisation (pro)
* New plugins:
  * Send SMS via ClickSend gateway.
  * Set Operation Plugin - Perform set operations on two sets of data.
  * Max/Min Value
  * String to date - converts string to date
  * String replace
  * Tag Mailchimp Contact
  * Time delay
* Profile Metrics
* Configurable data partitioning
* Preparation for configurable profile merging strategies (pro)
* Fixing missing plugin documentation
* Extended integration with mailchimp.
* Time is zone aware now (no longer naive dates) - All timestamps are UTC with UTC zone. 
* Fail over database for better fault tolerance (pro)
* All records have insert, create, update timestamps. 
* Information on fields updates.
* Updates profile details page.
* Numerous error fixes


Version: 0.8.1
----------------------------------------------------------
* New Dashboard
* New Profile Details Page
* Extended analytics
* Multi-tenant setup available (pro)
* Debugging in context of event
* Static Profile ID generator
* Passing Profile ID between owned domains
* Predefined events 
* New Data Schema
* Customer journey mapping
* Better Production/Testing switching
* Tracardi now can handle coping event data to profiles and event indexing on historical data (pro)
* Better autocomplete of event properties
* Session open, Session close, Internal events
* Device fingerprinting (pro)
* New bridge for Javascript integration with the web page (pro)
* New workflow triggers (pro)
* Updated documentation
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
  * Upgrade to python 3.10
  * Performance tweaks
  * More configuration flags for better configuration

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
