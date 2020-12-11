## Unprotected admin funcionality

Go to `/robots.txt`

![image1](/images/portswigger-unprotected-admin-funcionality/portswigger-unprotected-admin-funcionality1.png)

Now go to `/administrator-panel`

![image2](/images/portswigger-unprotected-admin-funcionality/portswigger-unprotected-admin-funcionality2.png)

And delete the user carlos, (I already did it)

<br/>
 
## Unprotected admin functionality with unpredictable URL

Check the source code and found this:

![image1](/images/portswigger-unprotected-admin-funcionality-with-unpredictable-url/portswigger-unprotected-admin-functionality-with-unpredictable-url1.png)

Go to the directory and remove the user carlos

![image2](/images/portswigger-unprotected-admin-funcionality-with-unpredictable-url/portswigger-unprotected-admin-functionality-with-unpredictable-url2.png)

<br/>

## User role controlled by request parameter

Login with the given credentials

![image1](/images/portswigger-user-role-controlled-by-request-param/portswigger-user-role-controlled-by-request-parameter1.png)

Now go to `/admin`

![image2](/images/portswigger-user-role-controlled-by-request-param/portswigger-user-role-controlled-by-request-parameter2.png)

The request have and `Admin` parameter set to false

![image3](/images/portswigger-user-role-controlled-by-request-param/portswigger-user-role-controlled-by-request-parameter3.png)

Change it to true

![image4](/images/portswigger-user-role-controlled-by-request-param/portswigger-user-role-controlled-by-request-parameter4.png)

Now delete the user carlos, but intercept the request and change the admin param to true

![image5](/images/portswigger-user-role-controlled-by-request-param/portswigger-user-role-controlled-by-request-parameter5.png)

<br/>

## User role can be modified in user profile

Login with the given credentials

![image1](/images/portswigger-user-role-can-be-modified-in-user-profile/portswigger-user-role-can-be-modified-in-user-profile1.png)

Go to my account

![image2](/images/portswigger-user-role-can-be-modified-in-user-profile/portswigger-user-role-can-be-modified-in-user-profile2.png)

Intercept the request to change the email, and send it to the repeater

![image3](/images/portswigger-user-role-can-be-modified-in-user-profile/portswigger-user-role-can-be-modified-in-user-profile3.png)

and the response:

![image4](/images/portswigger-user-role-can-be-modified-in-user-profile/portswigger-user-role-can-be-modified-in-user-profile4.png)

Add to the JSON body `"roleid":2`

![image5](/images/portswigger-user-role-can-be-modified-in-user-profile/portswigger-user-role-can-be-modified-in-user-profile5.png)

And now go to `/admin` and delete the user

![image6](/images/portswigger-user-role-can-be-modified-in-user-profile/portswigger-user-role-can-be-modified-in-user-profile6.png)

<br/>

## User ID controlled by request parameter

Login with `wiener:peter`

Go to My Account

![image1](/images/portswigger-user-id-controlled-by-req-param/portswigger-user-ID-controlled-by-request-parameter1.png)

In the URL there's a parameter `id` with the username, change it to carlos

![image2](/images/portswigger-user-id-controlled-by-req-param/portswigger-user-ID-controlled-by-request-parameter2.png)

Save the API key and submit the solution

<br/>

## Insecure direct object references

Go to the live chat

![image1](/images/portswigger-insecure-direct-object-references/portswigger-insecure-direct-object-references1.png)

Send a message and click on view transcript

![image2](/images/portswigger-insecure-direct-object-references/portswigger-insecure-direct-object-references2.png)

And the transcript have a number in the name 

![image3](/images/portswigger-insecure-direct-object-references/portswigger-insecure-direct-object-references3.png)

![image4](/images/portswigger-insecure-direct-object-references/portswigger-insecure-direct-object-references4.png)

Intercept the request of view transcript and change in to 1

![image5](/images/portswigger-insecure-direct-object-references/portswigger-insecure-direct-object-references5.png)

![image6](/images/portswigger-insecure-direct-object-references/portswigger-insecure-direct-object-references6.png)

And download the file

![image7](/images/portswigger-insecure-direct-object-references/portswigger-insecure-direct-object-references7.png)

See the file

![image8](/images/portswigger-insecure-direct-object-references/portswigger-insecure-direct-object-references8.png)

And login with the password

![image9](/images/portswigger-insecure-direct-object-references/portswigger-insecure-direct-object-references9.png)
