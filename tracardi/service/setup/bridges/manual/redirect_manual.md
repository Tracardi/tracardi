# Link redirect bride

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

## Passing Profile ID or Session ID

To ensure accurate tracking of user interactions, you can pass either a Profile ID or a Session ID when creating redirect links. This allows Tracardi to associate the event with a specific user profile or session, ensuring the event is tracked properly.

- **Passing Profile ID**: When a Profile ID is included in the redirect link, Tracardi will create a new session for the user and associate the event with the provided profile. This is useful when you want to track the event for a known user but start a new session. The redirect link will look like this:

    ```
    GET http://<tracardi-api-url>/redirect/<redirect-id>/p/<profile-id>
    ```

    Example: `GET http://api.tracardi.com/redirect/12345/p/abc123`

    In this case, a new session will be created for the event, and it will be linked to the profile with ID `abc123`.

- **Passing Session ID**: If a Session ID is passed instead, Tracardi will link the event to the existing session. This is useful when you want to continue tracking a user’s activity within the same session. The Profile ID will be automatically fetched from the session, and the event will be linked to both the session and the profile.

    ```
    GET http://<tracardi-api-url>/redirect/<redirect-id>/s/<session-id>
    ```

    Example: `GET http://api.tracardi.com/redirect/12345/s/xyz789`

    In this case, the event will be attached to the session with ID `xyz789`, and the associated profile will be fetched from the session information.

Both approaches allow you to control whether a new session is created or an existing session is reused, providing flexibility for tracking different types of events and user behaviors.


```
GET http://<tracardi-api-url>/redirect/<redirect-id>/p/<profile-id>
```
New session will be created for this event. 

```
GET http://<tracardi-api-url>/redirect/<redirect-id>/s/<session-id>
```

when session is passed the profile id is fetched from session id and event will be attached to the passed session id. 