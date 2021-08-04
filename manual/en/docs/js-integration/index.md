# Web page JS integrations

## Connecting the script and configuration

Tracardi comes with Javascript snippet that integrate any webpage with Tracardi. 
In order to use it you must paste it in your web page header. 
This is the example of the snippet:

```html
    <script>
        const options = {
            tracker: {
                url: {
                    script: 'http://192.168.1.103:8686/tracker',
                    api: 'http://192.168.1.103:8686'
                },
                source: {
                    id: "<your-source-id-HERE>"
                }
            }
        }

        !function(e){"object"==typeof exports&&"undefine...

    </script>
```

If you refresh your page with the above javascript code you will notice that the response from tracardi will be like this:

```
Headers:
Status: 401 Unauthorized

Body:
detail"Access denied. Invalid source."
```

This is because of the invalid source id that was not defined in the option.source.id section of the snippet. To obtain source id create it 
in Tracardi and then replace string ‘<your-source-id-HERE>‘ with your source id like this:

```html
    <script>
        const options = {
            tracker: {
                url: {
                    script: 'http://192.168.1.103:8686/tracker',
                    api: 'http://192.168.1.103:8686'
                },
                source: {
                    id: "ee2db027-46cf-4034-a759-79f1c930f80d"
                }
            }
        }

        !function(e){"object"==typeof exports&&"undefined"!=ty...

    </script>
```

Please notice that there is also defined the URL of tracardi backend server. Please replace the IP 192.168.1.103 with the address of your Tracardi server installation.

## Sending events

Now we are ready to send events to Tracardi. 

In a separate script define events that you would like to send.

```javascript
window.response.context.profile = true;
window.tracker.track("purchase-order", {"product": "Sun glasses - Badoo", "price": 13.45})
window.tracker.track("interest", {"Eletronics": ["Mobile phones", "Accessories"]})
window.tracker.track("page-view",{});
```

Events consist of a event type. Event type is any string that describes what happened. 
In our example we have 3 events: "purchase-order", "interest", "page-view".

### Events data, properties

Each event may have additional data that describes the details of the event.
For example, we have the event "interest" and it sends data `{"Eletronics": ["Mobile phones", "Accessories"]}`

Tracardi collects all events and sends it as one request to the Tracradi tracker endpoint.

All events are send when page fully loads. 

## Binding events to page elements

You can also bind events to page elements. To do that you will need to be sure that the page loads and every element of the page is accessible.

To do that add the following configuration to options. 

```javascript
listeners: {
    onInit: ({helpers, context}) => {
      // Code that binds events.
    }
}
```
The whole configuration should look like this.

```html
<script>

        const options = {
            listeners: {
                onInit: ({helpers, context}) => {
                    // Code that binds events.
                },
            tracker: {
                url: {
                    script: 'http://192.168.1.103:8686/tracker',
                    api: 'http://192.168.1.103:8686'
                },
                source: {
                    id: "ee2db027-46cf-4034-a759-79f1c930f80d"
                }
            }
        }

        !function(e){"object"==typeof exports&&"undefined"!=typeof module?module.exports=e():"function"==typeof define&&define.amd?define([],e):("undefined"!=typeo...
    
</script>
```

Then you can write a code that binds for example onClick event on a button to 
tracardi event.

This is the example code:

```javascript
onInit: ({helpers, context}) => {
    const btn0 = document.querySelector('#button')

    helpers.onClick(btn0, async ()=> {
        const response = await helpers.track("page-view", {"page": "hello"});

        if(response) {
            const responseToCustomEvent = document.getElementById('response-to-custom-event');
            responseToCustomEvent.innerText = JSON.stringify(response.data, null, " ");
            responseToCustomEvent.style.display = "block"
        }
    });
}
```
It looks for the element with id="button"

```javascript
const btn0 = document.querySelector('#button')
```

Then using helpers binds onClick on that element to function:

```javascript
async ()=> {
        // Send event to tracardi
        const response = await helpers.track("page-view", {"page": "hello"});

        if(response) {
            const responseToCustomEvent = document.getElementById('response-to-custom-event');
            responseToCustomEvent.innerText = JSON.stringify(response.data, null, " ");
            responseToCustomEvent.style.display = "block"
        }
    }
``` 

Inside the function we send the event to Tracardi:

```javascript
const response = await helpers.track("page-view", {"page": "hello"});
```

And on response we make a string from JSON response and bind it as innerText of 
element with id='response-to-custom-event'

## Wrap up

The whole configuration looks like this:
 
```html
 <script>
 
         const options = {
             listeners: {
                 onInit: ({helpers, context}) => {
                     const btn0 = document.querySelector('#button')
                 
                     helpers.onClick(btn0, async ()=> {
                         const response = await helpers.track("page-view", {"page": "hello"});
                 
                         if(response) {
                             const responseToCustomEvent = document.getElementById('response-to-custom-event');
                             responseToCustomEvent.innerText = JSON.stringify(response.data, null, " ");
                             responseToCustomEvent.style.display = "block"
                         }
                     });
                 },
             tracker: {
                 url: {
                     script: 'http://192.168.1.103:8686/tracker',
                     api: 'http://192.168.1.103:8686'
                 },
                 source: {
                     id: "ee2db027-46cf-4034-a759-79f1c930f80d"
                 }
             }
         }
 
         !function(e){"object"==typeof exports&&"undefined"!=typeof module?module.exports=e():"function"==typeof define&&define.amd?define([],e):("undefined"!=typeo...
     
 </script>
 ```

## Tracardi helpers

You probably noticed that we use helpers to bind events. We used onClick method to bind
to click event. You might need to bind to other than click event. To do that use addEventListener:

```javascript
const btn0 = document.querySelector('#button')                 
helpers.addListener(btn0, 'mouseover', async ()=> {
    // Code
});
```

Helpers also have track method that let you send custom event to Tracardi at any time. 
