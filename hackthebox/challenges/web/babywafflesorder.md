We have this page:

![image1](/images/htb-babywafflesorder/babywafflesorder1.png)

And here's the request and response:

![image2](/images/htb-babywafflesorder/babywafflesorder2.png)

Next thing that I'm going to do is change the content type to: `Content-Type: application/xml` and send the order with xml:

![image3](/images/htb-babywafflesorder/babywafflesorder3.png)

Now I know that I can use xml I'll try XXE:

![image4](/images/htb-babywafflesorder/babywafflesorder4.png)

And it is vulnerable to get the flag:

![image5](/images/htb-babywafflesorder/babywafflesorder5.png)


