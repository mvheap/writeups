We have this website that we can login

![image1](/images/htb-babyauth/babyauth1.png)

And we can register

![image2](/images/htb-babyauth/babyauth2.png)

And then we log in as the user we registered

![image3](/images/htb-babyauth/babyauth3.png)

This is the request we have when we login in the response there's a cookie:

![image4](/images/htb-babyauth/babyauth4.png)

If we decode it we have this:

![image5](/images/htb-babyauth/babyauth5.png)

And when we log in we hasve this message:

![image6](/images/htb-babyauth/babyauth6.png)

And the request is this, that we're using the cookie:

![image7](/images/htb-babyauth/babyauth7.png)

We are going to create a cookie with the username admin:

![image8](/images/htb-babyauth/babyauth8.png)

And use it to get the flag:

![image9](/images/htb-babyauth/babyauth9.png)




