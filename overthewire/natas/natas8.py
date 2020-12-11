import requests
import re

username = "natas8"
password = "DBfUBfqQG69KvJvJ1iAbMoIpwSNQ9bWe"
url = "http://natas8.natas.labs.overthewire.org/"

data = {"secret" : "oubWYf2kBq", "submit" : "submit"}

session = requests.Session()
response = session.post(url,auth=(username,password),data=data)
content = response.text

print(re.findall("The password for natas9 is (.*)",content)[0])
