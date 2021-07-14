# Profile merging

## Introduction

Profile merging is the process of finding customer profiles that 
belong to one person and have been saved as separate records for 
various reasons. In order to combine data into one record, 
it is necessary to indicate the field containing the value by 
which the customer data could be combined. 

This value must uniquely identify the customer. 
This can be an e-mail or other global identifier that can be used 
to group client profiles.

Aggregation is needed because on different devices the same person 
will have different user profiles with a different fragmented data set. 

For example, my profile may have id: 1 when I'm using my 
laptop with Firefox browser, or id: 2 when I'm using the 
same device but using Google Chrome, or id: 3 when I'm 
using a mobile phone. 

Even though I am the same person, I have 3 different profiles. 
Profile id: 1 will have data about my purchases, but not my name 
and surname. First and last name may be saved e.g. in profile 2.

## Merging process

Merging is a complex process with well-defined rules of operation.

It is done as follows. 

The current client profile is downloaded from the database, 
saved on the device that is currently used. If the sent event 
points to a workflow that has the profile merging process defined, 
then the `merge key` is read from profile, usually it is an e-mail. 

Then, all profiles with the same value for the `merging key` are 
searched in the database (in this case, all records with the same e-mail
as defined in the current profile are searched). 

The system then automatically excludes profiles that were previously merged.

Now comes the process of merging the data. If there are different values for the same 
field, e.g. for the `name` field, one is "Bill", the second time it is "Whiliam", 
then the data will be combined and we will get a value `name` = ["Bill", "Whiliam"].

The linked profiles are given the new ID and a new profile record is created. 
The merged profile is saved in the database and the remaining profiles 
are marked with `mergedWith` field equal to the id of the newly created merged profile.

Then the javascript code on the device saves the id of the merged 
profile in local database.

Thus, there is one linked profile in the database. However, it does not mean that the 
reference to the current profile has been changed on all devices.

## Profile propagation

Consider the following example. I use the online store with two devices: 
a laptop and a mobile phone. The devices have references to my profiles. 
On laptop it is profile id: 1, on the mobile phone it is profile id: 2 

At one point I entered my e-mail in to the web-shop using a laptop. 
New merged profile is created and it has id: 3. The reference to this profile 
will be saved in the browser. 

However, the reference to the old profile is still stored on my mobile phone. 

Next thime when I use my mobile, the old profile will be downloaded, 
but Tracardi will recognize that it has the mergedWith field set. 
The system will replace the old profile with the new one (defined in mergedWith) 
and the device will receive the new merged profile. 

This way, information about the linked profile will be propagated to all devices.
 