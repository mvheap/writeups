We have this inforamtion about the challenge: *One of our web servers triggered an AV alert, but none of the sysadmins say they were logged onto it. We've taken a network capture before shutting the server down to take a clone of the disk. Can you take a look at the PCAP and see if anything is up?*

First I open the `.pcapng` with wireshark and I filter `http`, It looks like they got a reverse shell exploiting an upload funcionality of the webpage

![image1](/images/htb-chase/chase1.png)

Following the tcp stream didn't get the flag, but at the end there's a `GET` to a `.txt` with a name that seems encoded, decode it using base32 and get the flag

![image2](/images/htb-chase/chase2.png)
