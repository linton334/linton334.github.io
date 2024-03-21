import requests
import pickle

s = requests.Session()

url = "http://127.0.0.1:8000/api/login"

payload = {
    "username": "linton100",
    "password": "password100"
}

response = s.post(url, data=payload)

print(response.status_code)
print(response.text)