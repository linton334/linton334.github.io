import requests

url = "http://127.0.0.1:8000/api/logout"

response = requests.post(url)

print(response.status_code)
print(response.text)