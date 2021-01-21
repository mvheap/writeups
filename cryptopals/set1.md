
### 1. Convert hex to base64

We have to convert this string:

```
49276d206b696c6c696e6720796f757220627261696e206c696b65206120706f69736f6e6f7573206d757368726f6f6d
```

to this:

```
SSdtIGtpbGxpbmcgeW91ciBicmFpbiBsaWtlIGEgcG9pc29ub3VzIG11c2hyb29t
```

The title challenge says: convert hex to base64 so here's the python script to do it:

```python
from base64 import b64encode

encoded = "49276d206b696c6c696e6720796f757220627261696e206c696b65206120706f69736f6e6f7573206d757368726f6f6d"

#Decoding from hex
hex_decoded = bytes.fromhex(encoded)
print(f"Hex coded: {hex_decoded.decode()}")

#Base64 encoding
b64_encoded = b64encode(hex_decoded)
print(f"Base64 encoded: {b64_encoded.decode()}")
```

### 2. Fixed XOR

Here we have to hex decode this:

```
1c0111001f010100061a024b53535009181c
```

XOR it against:

```
686974207468652062756c6c277320657965
```

And it should give you:

```
746865206b696420646f6e277420706c6179
```

The python script to solve:

```python
def xor(a,b):
    return bytes([x ^ y for (x,y) in zip(a,b)])


data = bytes.fromhex("1c0111001f010100061a024b53535009181c")
key = bytes.fromhex("686974207468652062756c6c277320657965")

solution = xor(data,key).hex()
print(solution)
```

First I created a function named `xor` to XOR each byte of the strings, then I hex encode the two strings, and send it over the function, after that save the output of the function on a variable called `solution` and I hex encoded this value.

### 3. Single-byte XOR cipher

We have a hex encoded string:

```
1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736
```

This string has been XOR'd	against a single character, we are going to bruteforce the key by trying each value from 1 to 256 as the key:

```python
def xor(a,b):
    output = b""
    for x in a:
        output += bytes([x ^ b])
    return output

string = bytes.fromhex("1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736")

for i in range(256):
        print(xor(string,i))
```

Running it there's a lot of strings but here's the important one:

```
b"Cooking MC's like a pound of bacon"
```

Now we can made this using the frequency of the characters:

```python
def get_english_score(input_bytes):
    character_frequencies = {
        'a': .08167, 'b': .01492, 'c': .02782, 'd': .04253,
        'e': .12702, 'f': .02228, 'g': .02015, 'h': .06094,
        'i': .06094, 'j': .00153, 'k': .00772, 'l': .04025,
        'm': .02406, 'n': .06749, 'o': .07507, 'p': .01929,
        'q': .00095, 'r': .05987, 's': .06327, 't': .09056,
        'u': .02758, 'v': .00978, 'w': .02360, 'x': .00150,
        'y': .01974, 'z': .00074, ' ': .13000
    }
    return sum([character_frequencies.get(chr(byte), 0) for byte in input_bytes.lower()])
```

Use this function to get the score, then I'll make a variable to save each score with the message and key, and then print the one with more score:

```python
def xor(a,b):
    output = b""
    for x in a:
    	output += bytes([x ^ b])
    return output

def get_english_score(input_bytes):
    character_frequencies = {
        'a': .08167, 'b': .01492, 'c': .02782, 'd': .04253,
        'e': .12702, 'f': .02228, 'g': .02015, 'h': .06094,
        'i': .06094, 'j': .00153, 'k': .00772, 'l': .04025,
        'm': .02406, 'n': .06749, 'o': .07507, 'p': .01929,
        'q': .00095, 'r': .05987, 's': .06327, 't': .09056,
        'u': .02758, 'v': .00978, 'w': .02360, 'x': .00150,
        'y': .01974, 'z': .00074, ' ': .13000
    }
    return sum([character_frequencies.get(chr(byte), 0) for byte in input_bytes.lower()])

string = bytes.fromhex("1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736")

messages_info = []

for i in range(256):
	guess = xor(string,i)
	score = get_english_score(guess)
	info = {"Message":guess,'score':score,'key':i}
	messages_info.append(info)

best = sorted(messages_info,key=lambda x: x['score'],reverse=True)[0]
print(best)
```

### 4. Detect single-character XOR

There's a file with xor'd strings, and we have to find which one is encryped with a single character.

This is similar to the last challenge, so we're going to modify the script to: read every line from the script and convert it to hex, the xor each line and calculate the score and from that score get the best:

```python
def xor(a,b):
    output = b""
    for x in a:
    	output += bytes([x ^ b])
    return output

def get_english_score(input_bytes):
    character_frequencies = {
        'a': .08167, 'b': .01492, 'c': .02782, 'd': .04253,
        'e': .12702, 'f': .02228, 'g': .02015, 'h': .06094,
        'i': .06094, 'j': .00153, 'k': .00772, 'l': .04025,
        'm': .02406, 'n': .06749, 'o': .07507, 'p': .01929,
        'q': .00095, 'r': .05987, 's': .06327, 't': .09056,
        'u': .02758, 'v': .00978, 'w': .02360, 'x': .00150,
        'y': .01974, 'z': .00074, ' ': .13000
    }
    return sum([character_frequencies.get(chr(byte), 0) for byte in input_bytes.lower()])

f = open("4.txt","r")
messages_info = []

for line in f:
	for i in range(256):
		hex_line = bytes.fromhex(line.strip('\n'))
		guess = xor(hex_line,i)
		score = get_english_score(guess)
		info = {"Message":guess,'score':score,'key':i}
		messages_info.append(info)

best = sorted(messages_info,key=lambda x: x['score'],reverse=True)[0]
print(best)
```

Running it you get:

```
{'Message': b'Now that the party is jumping\n', 'score': 2.03479, 'key': 53}
```

### 5. Implement repeating-key XOR

Now we have to use the repeating-key XOR to encrypt this two messages with the key ICE:

```
Burning 'em, if you ain't quick and nimble
I go crazy when I hear a cymbal
```

Reapiting-key xor is encrypt each byte of the key with each byte of the data, in this case, when you get to the 4rd byte it will start form the first one like this:

```
ABCDEFGHI
ICEICEICE
```

So you have to make a function to do this:

```python
def repeating_key_xor(data,key):
	i = 0
	encrypted = b""

	for c in data:
		encrypted += bytes([c ^ key[i]])
		i += 1
		if (i == len(key)): # When i is equal to the key length (the last character) start from zero
			i = 0
	return encrypted


string = b"Burning 'em, if you ain't quick and nimble\nI go crazy when I hear a cymbal"
key = b"ICE"

print(repeating_key_xor(string,key).hex())
```
