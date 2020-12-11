## vault-door-training

We're given a .java file, when you open it in a text editor you'll see this:

![image1](/images/picoctf2019-vaultdoortraining/vaultdoortraining1.png)

In the `checkpPassword()` there's the flag in plaintext, just add the picocCTF{}

<br/>

## vault-door-1

We have a .java file that tere's an array with the characters unordered:

![image1](/images/picoctf2019-vaultdoor1/picoctf2019-vaultdoor1.png)

Take this and order it by the number with sublime text you can do edit -> sort lines:

![image2](/images/picoctf2019-vaultdoor1/picoctf2019-vaultdoor12.png)

And the final:

![image3](/images/picoctf2019-vaultdoor1/picoctf2019-vaultdoor13.png)

<br/>

## asm1 

We're given a .s, if we open it there's assembly code:

![image1](/images/picoctf2019-asm1/picoctf2019-asm11.png)

So we have to know what's does it return if the input is 0x76, there's the code commented with the solution:

![image2](/images/picoctf2019-asm1/picoctf2019-asm12.png)

<br/>

## vault-door-3

We're given a .java file, when you open it, there's a `checkPassword()` function

![image1](/images/picoctf2019-vaultdoor3/picoctf2019-vaultdoor31.png)

I'll code a C++ that doest the same to get the flag

![image2](/images/picoctf2019-vaultdoor3/picoctf2019-vaultdoor32.png)


<br/>

## asm2

We're given a file that contains the next assembly instructions:

![image1](/images/picoctf2019-asm2/picoctf2019-asm21.png)

We have to know what asm2(0x7,0x18) return,I commented the instructions

![image2](/images/picoctf2019-asm2/picoctf2019-asm22.png)

I'll make a python script to make it for me:

![image3](/images/picoctf2019-asm2/picoctf2019-asm23.png)

<br/>

## vault-door-4

We're given a .java file, when you open it, there's a `checkPassword()` function, there's an array with values in ascii, hex and octal

![image1](/images/picoctf2019-vaultdoor4/picoctf2019-vaultdoor41.png)

I'll make a python script that decodes all

![image2](/images/picoctf2019-vaultdoor4/picoctf2019-vaultdoor42.png)

<br/>

## asm3

We're given a file with assembly

![image1](/images/picoctf2019-asm3/picoctf2019asm31.png)

We have to know what does asm3(0xc264bd5c,0xb5a06caa,0xad761175) return, so these are the registers on little endian

![image2](/images/picoctf2019-asm3/picoctf2019asm32.png)

Now let's analyze the code, <+3> does xor eax with eax thats, 0

![image3](/images/picoctf2019-asm3/picoctf2019asm33.png)

Then move the byte at `[ebp+0x9]` that is `bd` to `ah` so now eax = 0xbd00, see the image of the registers

![image4](/images/picoctf2019-asm3/picoctf2019asm34.png)

![image5](/images/picoctf2019-asm3/picoctf2019asm35.png)

Next, shift left 0x10 bytes in ax, eax = 0x00000000

![image6](/images/picoctf2019-asm3/picoctf2019asm36.png)

Substract the byte at `[ebp+0xd]` that is `6c` to al, so eax = 0xbd000094

![image7](/images/picoctf2019-asm3/picoctf2019asm37.png)

![image8](/images/picoctf2019-asm3/picoctf2019asm38.png)

Add the byte at `[ebp+0xf]` that is `b5` to ah, so eax = 0xbd00b594

![image9](/images/picoctf2019-asm3/picoctf2019asm39.png)

xor the word at `[ebp+0x10]` that is `1175` with ax, so eax = 0x0000a4e1

![image10](/images/picoctf2019-asm3/picoctf2019asm310.png)

![image11](/images/picoctf2019-asm3/picoctf2019asm311.png)

<br/>

## droids0

We're given a `.apk` file, I'll open it on android studio

![image1](/images/picoctf2019-droids0/picoctf2019-droids01.png)

I'll run the emulator

![image2](/images/picoctf2019-droids0/picoctf2019-droids02.png)

If you send input, check the logcat and search for picoctf and you'll find the flag:


![image3](/images/picoctf2019-droids0/picoctf2019-droids03.png)

<br/>

## reverse_cipher

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

<br/>

## vault-door-5

We're given a java file:

![image1](/images/picoctf2019-vaultdoor5/picoctf2019-vaultdoor51.png)

This url encodes a string and then base64 encode it, i'll make a python script that decode de base64 string and then url decode it

![image2](/images/picoctf2019-vaultdoor5/picoctf2019-vaultdoor52.png)

<br/>

## droids1

We're given a `.apk` file, I'll open it on Android Studio

![image1](/images/picoctf2019-droids1/picoctf2019-droids11.png)

And run it with the emulator

![image2](/images/picoctf2019-droids1/picoctf2019-droids12.png)

Now I started searching trough the files and I found in `resources.arsc`, in string the password `opossum`

![image3](/images/picoctf2019-droids1/picoctf2019-droids13.png)

![image4](/images/picoctf2019-droids1/picoctf2019-droids14.png)


<br/>

## vault-door-6

We're given a `.java` file:

![image1](/images/picoctf2019-vaultdoor6/picoctf2019-vaultdoor61.png)

There's a xor array, and then a loop that xor every value with 0x55 i'll do a python script to undo the xor and get the flag

![image2](/images/picoctf2019-vaultdoor6/picoctf2019-vaultdoor62.png)



