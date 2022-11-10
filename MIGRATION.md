# Migration issues

This file describes migration issues to version 0.7.3 form 0.7.2.

After migration, you should inspect the following configuration:

* Registered users - this migration does not copy registered users, only admin is available
* If you where using event tagging you should inspect event metadata. Event tagging was removed from the system and
  moved to event metadata. Please check if the tags are correct.
* If you where using event validation is will be removed. Please copy it form the old version.
* If you were using event reshaping is will be removed. Please copy it form the old version.
* If you had some plugins installed then it will be removed. Workflows will still run but the plugins will have to be
  reinstalled. 