import requests

url = "https://api.avalai.ir/v1/models"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer aa-**" # add you api key here
}
response = requests.get(url, headers=headers)
print(response.json())