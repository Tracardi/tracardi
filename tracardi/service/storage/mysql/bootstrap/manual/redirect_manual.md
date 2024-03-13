# Link bride

Inbound Traffic/Event Redirects is a feature that allows you to redirect traffic from specific links to a defined URL,
while sending an event to Tracardi. When a user clicks on one of the links that you have
defined in Inbound Traffic/Event Redirects, they will be redirected to the specified URL. At the same time, an event
will be sent to Tracardi, providing information about the redirect and any event properties that you have defined.

The process of setting up Inbound Traffic/Event Redirects involves the following steps:

* Define the links that you want to redirect: This could be any link on your website or in an email that you want to
  redirect to a specific URL.

* Set the target URL: This is the URL that the user will be redirected to when they click on one of the defined links.

* Define the event properties: These are additional pieces of information that you want to send to Tracardi along with
  the event. This could include information such as the type of event, the source of the event, or any other relevant
  data that you want to track.

* Set up the event tracking in Tracardi: This involves configuring Tracardi to receive and process the events that will
  be sent from your Inbound Traffic/Event Redirects setup.

Once you have completed these steps, your Inbound Traffic/Event Redirects setup will be ready to use. When a user clicks
on one of your defined links, they will be redirected to the target URL and an event will be sent to Tracardi, providing
information about the redirect and any event properties that you have defined.

## Redirect links

All redirect links are in the form of:

```
http://<tracardi-api-url>/redirect/<redirect-id>
```

* __tracardi-api-url__ the url to Tracardi API server
* __redirect-id__ id of the redirection. Click on any item in __Inbound Traffic/Event redirects___ to see the full url
  path.

All redirect links are available at __Inbound Traffic/Event redirects___. Click on the selected row to see full url
path. 
