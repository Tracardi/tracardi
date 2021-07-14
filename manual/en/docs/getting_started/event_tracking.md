# Event tracking

## Introduction - keeping track of events

Sending events is a way to track customer behavior. Thanks to events, we can react to the 
customer actions and help them, e.g. in the purchasing process.

## Event example

Events consist of: 

* the event name, 
* event properties, and 
* context.

`The name` is a simple string of characters that identifies the event. An example event may be, 
for example, a `purchase of a product`, `a page scrolled to the end`, `sing-in`, etc.

`Event properties` are additional information on the event. For example, when signing-in, we can send the 
user's login. When registering `purchase order` we can send product name and price. 

`Context` is additional data not necessarily related to the event, e.g. type of browser used, 
phone screen size, weather conditions, etc.

## Event registration

To register an event, connect to the /track endpoint on the server where Tracardi is installed.

You need to write a code that will connect to the POST method to the url e.g. 
http://tracardi.page.com/track and send the data about event plus additional information 
on the source and session.

Example of track data payload.

```json
{
   "source": {
     "id": "source-id"
   },
   "session": {
     "id": "session-id"
   },
   "profile": {
     "id": "profile-id"
   },
   "context": {},
   "properties": {},
   "events": [
      {"type":  "purchase-order", "properties":  {"product": "Nike shoes", "quantity": 1}},
      {"type":  "page-view"}
   ],
   "options": {}
} 
```

Not all data is required. Below you can find only required data.

```json
{
   "source": {
     "id": "source-id"
   },
   "session": {
     "id": "session-id"
   },
   "events": [
      {"type":  "purchase-order", "properties":  {"product": "Nike shoes", "quantity": 1}},
      {"type":  "page-view"}
   ],
} 
```

When registering an event, we need the following data.

* Data about the event, i.e. `the type of the event` and its `properties`. There may be several events within one query.

* `Source id`. It must match the source defined in Tracardi. Otherwise the Authorization error wil be returned. 

* And the `session id`. The session id is the saved id of the last session. If this is the first visit, you should generate id, preferably using uuid4 and attach it to the payload. Visits are related with the session, so the session id should change with each new user visit.

Additionally, the `profile id` should be sent to the system. 
For the first visit, there is no profile id so profile id field is not sent. After first connection
Tracardi will return a profile id that should be attached with each subsequent connection to /track endpoint.

If no profile id is defined in sent data then new profile id will be generated. 

If you want to send `context` attach it to context field. Context as well as properties 
may have any schema. 

Example of event data payload with context `attached`.

```json
{
   "source": {
     "id": "source-id"
   },
   "session": {
     "id": "session-id"
   },
   "profile": {
      "id": "profile-id"
   },
   "events": [
      {"type":  "purchase-order", "properties":  {"product": "Nike shoes", "quantity": 1}},
      {"type":  "page-view"}
   ],
  "context": {
      "device": "iPhone X"
  }   
} 
```

# Response


# Usage

This type of event tracking integration is only required when you integrate your mobile app or any other 
device or service. If you want to use event tracing with your web page a javascript code is already prepared 
to help you do it more easily. 

# Javascript integration



