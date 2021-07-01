# Merge Profile Action

When there is a new Personally Identifiable Information(PII) appended to a profile then the profile may 
need merging with other profiles in the system. This is the way you maintain a consistent user profile.

Once the node is connected in flow it will mark profile to be merged. 
To do that have to provide a merge key in configuration tab.

## Configuration

This node needs a merge key to use during merging. That can be e-mail, telephone number, id, etc. System will look for other 
profiles that have the same merge key, e.g. e-mail and will merge these profiles into one record.  

If two or more keys are defined Tracardi will look for records that have all defined keys. 
For example if it is e-mail and name then record matched for merging will have both 
email and name equal to defined values. 

Provide merge key in form of JSON array. To access merge key data use dotted notation. 
Details on dotted notation can be found Notations / Dot notation in the documentation.

```json
{
  "mergeBy": ["event@properties.name"]
}

```

## Side effect

Profile merging will concatenate data if there is a conflict in data. For example lest assume there is a user John Doe with 
email john.does@mail.com in storage. New customer data also has name and surname associated with it e.g. name and surname equal to 
Jonathan Doe. THat means during merging the result record will be: 

```yaml
name: [John, Jothatan] 
surname: [Doe]   
```


