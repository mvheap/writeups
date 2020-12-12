We are given an image:

![image1](/images/picoctf2019-thenumbers/thenumbers1.png)

It's the flag but with the characters changed, you can tell by the `{`, so every position here is a letter of the alphabet trying I found this:

```python
>>> ascii_uppercase[16]
'Q'
>>> ascii_uppercase[15]
'P'
```

So it's the uppercase -1 for every character here's a script:

```python
from string import ascii_uppercase

nums = [16,9,3,15,3,20,6,"{",20,8,5,14,21,13,2,5,18,19,13,1,19,15,14,"}"]

fl = []
for i in nums:
    if type(i) == str:
        fl.append(i)
    else:
        fl.append(ascii_uppercase[i-1])

print(''.join(fl))
```
