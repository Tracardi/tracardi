1. Log-in to the chatwoot.com
2. Select Chatwoot icon
3. Click new inbox in the left menu
4. Select website
5. Fill the form 
6. Select agent
7. You will see the javascript snippet that you should copy and paste to you page.
   Do not do it. Copy only the website token. It is marked __<TOKEN-IS-HERE>__ below in the example script

```html
<script>
      (function(d,t) {
        var BASE_URL="https://app.chatwoot.com";
        var g=d.createElement(t),s=d.getElementsByTagName(t)[0];
        g.src=BASE_URL+"/packs/js/sdk.js";
        g.defer = true;
        g.async = true;
        s.parentNode.insertBefore(g,s);
        g.onload=function(){
          window.chatwootSDK.run({
            websiteToken: '<TOKEN-IS-HERE>',
            baseUrl: BASE_URL
          })
        }
      })(document,"script");
    </script>
```