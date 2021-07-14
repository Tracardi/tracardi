# Profile segmentation

## Introduction

The segment is the result of the segmentation of customer profiles.
A segment can be described by a simple logical rule or by more 
complex AI models. The segment is part of the profile. A segment 
defined in the Tracardi system can be used in the segmentation 
workflow. The segment is represented by a simple sentence such 
as "Customers with high volume of purchases".

## How to segment

The segmentation process is started after each update of profile 
data or if the segmentation has been forced within the 
workflow by placing the action "Segment profile".

The criteria for segmentation are defined in the 
segmentation tab. When we define segmentation, we don't have 
to change anything in the workflow. If segmentation is enabled, 
it will be run after each workflow is completed. 

## Segmentation

A segment consists of a name and segmentation criteria. 
At the time of segmentation the name will be converted into 
the segmentation id. Name will be lower-cased and spaces 
will be replaced with dashes.

## Segmentation criteria

A profile will be attached to a given segment if the data 
contained in it meet the defined segment criteria.

Criteria is nothing more than a logical rule. For example, 
a user must visit our website at least 10 times.

For example:

Segment named: `Frequent visitor`.
He has a criterion that looks like this:

``
profile@stats.visits > 10
``

#### Result of segmentation

If the profile in its statistical data has been saved that the 
number is more than 10, then the segmentation id will be added 
in the profile in the segments item, which will look 
like `frequent-visitor`. 

A profile can belong to multiple segments. 




