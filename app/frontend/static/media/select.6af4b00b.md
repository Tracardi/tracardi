# SELECT query statement

Optional parts of the statement are in square brackets []. Multiple choice but required statement parts are in round brackets ().

```sql
SELECT 
[FRESH] 
(EVENT | RULE | SEGMENT | PROFILE)
    [WHERE where condition]
    [OFFSET integer]
    [LIMIT integer]
```

# SELECT statement examples

With select query you can search the following data types:

* EVENT
* PROFILE
* RULE
* SEGMENT

The simplest example of SELECT query looks like this:

```
SELECT PROFILE
```

It finds all profiles in the Unomi storage. 

```
SELECT PROFILE OFFSET 100 LIMIT 20
```

limits the results to 20 records and skips first 100 records

```
SELECT EVENT WHERE type=”view”
```

finds events with eventType equal to view. 

```
SELECT EVENT 
    WHERE type=”view” 
        AND (scope=”my-site-1” OR scope=”my-site-2”) 
        AND properties.target.pageInfo=”page-info’
```

finds view events that are in scope “my-site-1” OR  “my-site-2”  and target has property pageInfo that equals “page -info”.  You can limit or offset results with LIMIT and OFFSET as in the above example.


## WHERE|WHEN condition statement

The following grammar rules define expression syntax in UQL.
```
expr:
  | expr OR (expr AND expr)
  | expr AND (expr OR expr)
```

that means that expressions with similar operations e.g. OR must be in brackets.
The following where statement is forbidden:

```
field1=1 AND field2=2 OR field3=3
```
correct statement is either:
```
field1=1 AND (field2=2 OR field3=3)
```
or 
```
(field1=1 AND field2=2) OR field3=3
```
There is no auto resolution of priority operations

### Available operations mappings

Unomi operator maps to UQL where condition statement in the following way 

    * exists -> field EXISTS
    * between -> BETWEEN number AND number
    * equals -> filed EQUALS
    * notEquals -> field != string|number
    * greaterThanOrEqualTo -> field >= number
    * lessThanOrEqualTo -> field <= number
    * greaterThan -> field > number
    * lessThan -> field < number
    * missing -> field NOT EXISTS
    * contains -> CONTAINS
