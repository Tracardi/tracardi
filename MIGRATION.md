# Migration issues

This file describes migration issues to version 0.7.3 form 0.7.2.

After migration, you should inspect the following configuration:

* Registered users - this migration does not copy registered users, only admin is available
* If you were using event tagging, you should inspect the event metadata. Event tagging was removed from the system and moved to event metadata. Please check if the tags are correct.
* If you were using event validation, it will be removed. Please copy it from the old version.
* If you were using event reshaping, it will be removed. Please copy it from the old version.
* If you have some plugins installed, then they will be removed. Workflows will still run, but the plugins will have to be reinstalled.
