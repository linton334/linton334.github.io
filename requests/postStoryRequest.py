import requests
import pickle

# Start a session
s = requests.Session()

url = "http://127.0.0.1:8000/api/login"

payload = {
    "username": "linton100",
    "password": "password100"
}

# Post a story
url = "http://127.0.0.1:8000/api/stories"
payload = {
    "headline": "Brand new new API!",
    "category": "tech",
    "region": "uk",
    "details": "This is a brand new news story for the API!"
}
response = s.post(url, json=payload)

print(response.status_code)
print(response.text)