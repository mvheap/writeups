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
