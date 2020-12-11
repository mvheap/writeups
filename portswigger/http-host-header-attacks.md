## Basic password reset poisoning

First, let's try to reset our password

![passwordresetpoisoning1](/images/portswigger-password-reset-poisoning/passwordresetpoisoning1.png)

And put your email or username

![passwordresetpoisoning2](/images/portswigger-password-reset-poisoning/passwordresetpoisoning2.png)

Intercept this request with burp and send it to the repeater

![passwordresetpoisoning3](/images/portswigger-password-reset-poisoning/passwordresetpoisoning3.png)

Here, I changed the value of the host header and now check the email inbox

![passwordresetpoisoning4](/images/portswigger-password-reset-poisoning/passwordresetpoisoning4.png)

It's vulnerable, the host is changed

Let's exploit this, send a request with the host header value of your exploit server and change the username paramater to carlos

![passwordresetpoisoning5](/images/portswigger-password-reset-poisoning/passwordresetpoisoning5.png)

Now check the access log

![passwordresetpoisoning6](/images/portswigger-password-reset-poisoning/passwordresetpoisoning6.png)

Save this token into your clipboard and send a request to change the password with this token

![passwordresetpoisoning7](/images/portswigger-password-reset-poisoning/passwordresetpoisoning7.png)

Change the password and login with carlos and the new password

<br/>

## Web cache poisoning via ambigous requests

First send a random query parameter to see how the server handles it

![webcachepoisoningviaambigousrequests1](/images/portswigger-web-cache-poisoning-via-ambigous-requests/webcachepoisoningviaambigousrequests1.png)

See that the X-Cache is miss, send another time the request

![webcachepoisoningviaambigousrequests2](/images/portswigger-web-cache-poisoning-via-ambigous-requests/webcachepoisoningviaambigousrequests2.png)

Now it's hit

Put another host header with something random and send the request

![webcachepoisoningviaambigousrequests3](/images/portswigger-web-cache-poisoning-via-ambigous-requests/webcachepoisoningviaambigousrequests3.png)

See that the value is injected, now go to the exploit server and create a file like this:

![webcachepoisoningviaambigousrequests4](/images/portswigger-web-cache-poisoning-via-ambigous-requests/webcachepoisoningviaambigousrequests4.png)

Store it

Now in the second host header put your exploit server host and send the request without the query parameter only ```/```

![webcachepoisoningviaambigousrequests5](/images/portswigger-web-cache-poisoning-via-ambigous-requests/webcachepoisoningviaambigousrequests5.png)

Send it until you get the alert (Mine took like 5 requests)

![webcachepoisoningviaambigousrequests6](/images/portswigger-web-cache-poisoning-via-ambigous-requests/webcachepoisoningviaambigousrequests6.png)
