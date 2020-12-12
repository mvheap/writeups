## 64 bits

```bash
$ checksec badchars
[*] '/home/localuser/ropemporium/badchars/64bits/badchars'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
    RUNPATH:  b'.'
```

This binary has badchars:

```
$ ./badchars 
badchars by ROP Emporium
x86_64

badchars are: 'x', 'g', 'a', '.'
> 
Thank you!
```

Let's open it on gdb

```
pwndbg> info func
All defined functions:

Non-debugging symbols:
0x00000000004004d8  _init
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
0x0000000000400640  __libc_csu_init
0x00000000004006b0  __libc_csu_fini
0x00000000004006b4  _fini
```

