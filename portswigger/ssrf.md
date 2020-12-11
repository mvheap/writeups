## Basic SSRF against local server 

First, intercept the request when you click check stock from a product

![image1](/images/portswigger-basic-ssrf-against-local-server/portswigger-basic-ssrf-against-localserver1.png)

![image2](/images/portswigger-basic-ssrf-against-local-server/portswigger-basic-ssrf-against-localserver2.png)

Now change the `stockApi=` to `http://localhost/admin`

![image3](/images/portswigger-basic-ssrf-against-local-server/portswigger-basic-ssrf-against-localserver3.png)

We have access to the admin panel, now delete de user carlos

![image4](/images/portswigger-basic-ssrf-against-local-server/portswigger-basic-ssrf-against-localserver4.png)

![image5](/images/portswigger-basic-ssrf-against-local-server/portswigger-basic-ssrf-against-localserver5.png)

<br/>

## Basic SSRF against another back-end system

Intercept the request of the check stock of a product

![image1](/images/portswigger-basic-ssrf-against-another-backend-system/portswigger-basic-SSRF-against-another-back-end-system1.png)

![image2](/images/portswigger-basic-ssrf-against-another-backend-system/portswigger-basic-SSRF-against-another-back-end-system2.png)

Now the modify the `stockApi=` with `http://192.168.0.x:8080/admin`, but you don't know the last octet so you have to bruteforce it using burp interceptor for example

![image3](/images/portswigger-basic-ssrf-against-another-backend-system/portswigger-basic-SSRF-against-another-back-end-system3.png)

And the list is numbers from 1 to 255

![image4](/images/portswigger-basic-ssrf-against-another-backend-system/portswigger-basic-SSRF-against-another-back-end-system4.png)

Start the attack

![image5](/images/portswigger-basic-ssrf-against-another-backend-system/portswigger-basic-SSRF-against-another-back-end-system5.png)

And the correct one is the one with `200` status code

![image6](/images/portswigger-basic-ssrf-against-another-backend-system/portswigger-basic-SSRF-against-another-back-end-system6.png)

Now use `http://192.168.0.129:8080/admin`

![image7](/images/portswigger-basic-ssrf-against-another-backend-system/portswigger-basic-SSRF-against-another-back-end-system7.png)

And delete the user
