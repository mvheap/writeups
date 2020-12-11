There's `.trash` direcotory that has a file named bin

```
file bin
setuid ELF 32-bit LSB executable
```

It has setuid of leviathan5

```
./bin
01010100 01101001 01110100 01101000 00110100 01100011 01101111 01101011 01100101 01101001 00001010
```

It's binary decoding it gives Tith4cokei

Looking what does this program:

```
ltrace ./bin
fopen("/etc/leviathan_pass/leviathan5", "r")
```

Opens the leviathan5 password file

Tith4cokei
