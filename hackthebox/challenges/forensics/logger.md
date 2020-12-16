We have a `.pcapng` file from a USB I'll open it on wireshark:

![image1](/images/htb-logger/logger1.png)

The length of the keyboard packet is 8 bytes, and the keystroke information is in the third byte

![image2](/images/htb-logger/logger2.png)

Here it is and `H` according to this table: [HID Usage Tables](https://www.usb.org/sites/default/files/documents/hut1_12v2.pdf)

![image3](/images/htb-logger/logger3.png)

When it's `0` it means nothing

![image4](/images/htb-logger/logger4.png)

And then a `T`

![image5](/images/htb-logger/logger5.png)

There's only keystroke inforamtion of the packets that have length of 35 so I filter it:

![image6](/images/htb-logger/logger6.png)

If you continue you'll find the flag, note that `39` is caps and the it starts with caps.
