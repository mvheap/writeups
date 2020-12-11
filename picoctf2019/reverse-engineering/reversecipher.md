We're given this two files:

![image1](/images/picoctf2019-reversecipher/picoctf2019-reversecipher1.png)

The first one is a binary, and the second is the encrypted flag

![image2](/images/picoctf2019-reversecipher/picoctf2019-reversecipher2.png)

I'll open it on Ghidra to see the decompilation

![image3](/images/picoctf2019-reversecipher/picoctf2019-reversecipher3.png)

It is opening the file, then there's a loop that basically copies `picoCTF{`

![image4](/images/picoctf2019-reversecipher/picoctf2019-reversecipher4.png)

Then there's another that check if the number is even adds five and if it's odd decrements by two

![image5](/images/picoctf2019-reversecipher/picoctf2019-reversecipher5.png)

Now I'll do a python script doing the opposite

![image6](/images/picoctf2019-reversecipher/picoctf2019-reversecipher6.png)
