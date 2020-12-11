## Exploiting XXE using external entities to retrieve files

First, intercept the requests when you click the check stock button

![image1](/images/Exploiting-XXE-using-external-entities-to-retrieve-files/Exploiting-XXE-using-external-entities-to-retrieve-files1.png)

And here's the requests, with the XML that is vulnerable

![image2](/images/Exploiting-XXE-using-external-entities-to-retrieve-files/Exploiting-XXE-using-external-entities-to-retrieve-files2.png)

Add the payload and send it to retrive `/etc/passwd`

![image3](/images/Exploiting-XXE-using-external-entities-to-retrieve-files/Exploiting-XXE-using-external-entities-to-retrieve-files3.png)
