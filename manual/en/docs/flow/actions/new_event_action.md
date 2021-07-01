# New Event Action

Raise event action triggers defined event type as if it was triggered for web-site or any other device.
This event can be intercepted by TRACARDI to run defined flow. Event can also send defined event properties.

## Configuration

You need to configure the action for it  to run. Below is an example of RAISE EVENT action configuration file.

You must profile event type and event properties that will be attached to event and then send again to TRACARDI.

```json
{
  "event": {
    "type": "purchase-order",
    "properties": {"name":  "iPhone 128 GB white", "delivery":  "next day"}
  }
}
```

You may want to set properties from payload. To do that start with @ and give a path (in dot notation) to json data. See the example below.

PAYLOAD example

```json
{
  "properties": {
    "private": {
      "email": "...",
      "name": "..."
    }
  }
}
```

RAISE EVENT configuration
```json
{
  "event": {
    "type": "merge-profile",
    "properties": "@traits.private"
  }
}
```

Above configuration will copy data from payload starting from properties.private. This will give you a slice of data equal to:

```json
{
  "email": "...",
  "name": "..."
}
```

This is an equivalent of the following configuration. Of course it is more dynamic as it will 
take any data that comes in payload. 

```json
{
  "event": {
    "type": "merge-profile",
    "properties": {
      "email": "...",
      "name": "..."
    }
  }
}
```

## Debugging

Debugging of flows with raised event can be pretty tricky as you will only see data from one flow.
You will not see data from other triggered flows by RAISE EVENT.

## Cyclic flows

Raised event can form a never ending cycles. For example flow-1 raises event X which triggers flow-2. And flow-2 raises event Y which tiggers flow-1, and flow-2 again triggers event X ... This execution can never end.

To prevent this type of cyclic execution TRACARDI will stop sending new events when it detects a possible cyclic execution.
