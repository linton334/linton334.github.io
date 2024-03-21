import requests
import json

# API endpoint
api_url = "https://newssites.pythonanywhere.com/api/directory/"

# Sample data for the JSON payload
data = {
    "agency_name": "Linton Fogden News Agency",
    "url": "https://sc21lf.pythonanywhere.com",
    "agency_code": "LLF03"
}

# Convert data to JSON format
json_data = json.dumps(data)

# Set headers
headers = {
    "Content-Type": "application/json"
}

# Send POST request
response = requests.post(api_url, data=json_data, headers=headers)

# Check the response
if response.status_code == 201:
    print("News agency added successfully!")
else:
    print(f"Failed to add news agency. Status code: {response.status_code}")
    print(response.text)