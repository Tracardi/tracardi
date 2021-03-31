# CREATE statement

Create statements can be used to create rules and segments.
```sql
CREATE (RULE|SEGMENT)
        [READONLY]
        [DISABLED]
        [HIDDEN]
[WITH TAGS [tag1, tag2, ...]]
"rule or segment name"
[DESCRIBE "rule or segment description"]
IN SCOPE "scope"
WHEN where condition
[THEN prefindedAction(), …]
```

When using CREATE SEGMENT statement there is no THEN part of statement.

Example of CREATE STATEMENT
```
CREATE SEGMENT
    WITH TAGS ["important"]
    "At least 1 visit"
    DESCRIBE "First time visitor"
    IN SCOPE \"site-1\"
    WHEN profile:properties.nbOfVisits>=1
```

Example of CREATE RULE

```
CREATE RULE 
    "if identify event then copy event properties to profile" 
    DESCRIBE "Copies user data from events target properties to profile"
    IN SCOPE "my-site" 
    WHEN event:type="identify" AND event:scope = "my-site"  
    THEN CopyEventsToProfileProperties()
```
