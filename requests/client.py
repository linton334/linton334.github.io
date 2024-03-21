import requests
import getpass
from urllib.parse import urlparse
from requests.exceptions import MissingSchema
import json

class NewsClient:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = None

    def login(self, url):
        if "://" not in url:
            url = "http://" + url
        parsed_url = urlparse(url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            print("Error: Invalid URL. Please provide a valid URL.")
            return
        self.base_url = url
        username = input("Enter username: ")
        password = input("Enter password: ")
        response = self.session.post(f"{self.base_url}/api/login", data={"username": username, "password": password})
        print("-------------------------")
        print(response.text)
        return response.status_code

    def logout(self):
        print("-------------------------")
        try:
            response = self.session.get(f"{self.base_url}/api/logout")
            print(response.text)
            return response.status_code
        except MissingSchema:
            print("Error: Invalid base URL. Please login with a valid URL.")

    def post(self):
        headline = input("Enter headline: ")
        category = input("Enter category: ")
        region = input("Enter region: ")
        details = input("Enter details: ")
        print("-------------------------")
        try:
            response = self.session.post(f"{self.base_url}/api/stories", json={"headline": headline, "category": category, "region": region, "details": details})
            print(response.text)
            return response.status_code
        except MissingSchema:
            print("Error: Invalid base URL. Please login with a valid URL.")

    def news(self, agency_id=None, cat="*", reg="*", date="*"):
        directory_url = "http://newssites.pythonanywhere.com/api/directory/"
        response = self.session.get(directory_url)
        if response.status_code == 200:
            agencies = response.json()
            if agency_id != "*":
                agencies = [agency for agency in agencies if agency.get('agency_code') == agency_id]
            story_count = 0
            for agency in agencies:
                print(agency.get('agency_name'))
                if story_count >= 20:
                    break
                agency_url = agency.get('url')
                if agency_url:
                    try:
                        url = f'{agency_url}/api/stories?story_cat={cat}&story_region={reg}&story_date={date}'
                        response = self.session.get(url)
                        if response.status_code == 200:
                            response_text = response.text.strip()  # Remove leading/trailing whitespace
                            first_line = response_text.split('\n')[0]  # Get the first line
                            if first_line.lower() == '<!doctype html>':
                                print(f"Skipping agency {agency_url} because the response is HTML.")
                            elif response.json():
                                data = response.json()
                                news_stories = data.get('stories', [])  # Access the list of stories
                                for story in news_stories:
                                    if story_count >= 20:
                                        break
                                    print("-------------------------")
                                    print("TITLE:", story.get('headline'))
                                    print("CATEGORY:", story.get('story_cat'))  # Adjust the keys
                                    print("REGION:", story.get('story_region'))  # Adjust the keys
                                    print("AUTHOR FULL NAME:", story.get('author'))  # Adjust the keys
                                    print("DATE:", story.get('story_date'))
                                    print("\nDETAILS:", story.get('story_details'))
                                    print("-------------------------")
                                    story_count += 1
                            else:
                                print("Error: ", response.text)
                    except Exception as e:
                        print(f"Error while processing agency {agency_url}: {e}")
        else:
            print("Failed to retrieve the directory:", response.text)

    def list(self):
        print("-------------------------")
        response = self.session.get("http://newssites.pythonanywhere.com/api/directory/")
        if response.status_code == 200:
            agencies = response.json()
            for agency in agencies:
                print("-------------------------")
                print("AGENCY NAME:", agency.get('agency_name'))
                print("URL:", agency.get('url'))
                print("AGENCY CODE:", agency.get('agency_code'))
                print("-------------------------")
        else:
            print("Failed to retrieve the list of agencies:", response.text)

    def delete(self, story_key):
        print("-------------------------")
        try:
            response = self.session.delete(f"{self.base_url}/api/delete/{story_key}")
            print(response.text)
            return response.status_code
        except MissingSchema:
            print("Error: Invalid base URL. Please login with a valid URL.")

client = NewsClient()

def main():
    client = NewsClient()
    while True:
        print("1. Login")
        print("2. Logout")
        print("3. Post")
        print("4. News")
        print("5. List")
        print("6. Delete")
        print("7. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            url = input("Enter URL: ")
            print("Login status: ", client.login(url))
            print("-------------------------")
        elif choice == '2':
            print("Logout status: ", client.logout())
            print("-------------------------")
        elif choice == '3':
            print("Post status: ", client.post())
            print("-------------------------")
        elif choice == '4':
            id = input("Enter id (optional, press enter to skip): ")
            cat = input("Enter category (optional, press enter to skip): ")
            reg = input("Enter region (optional, press enter to skip): ")
            date = input("Enter date (optional, press enter to skip): ")
            print("News: ", client.news(agency_id=id or "*", cat=cat or "*", reg=reg or "*", date=date or "*"))
            print("-------------------------")
        elif choice == '5':
            print("List: ", client.list())
            print("-------------------------")
        elif choice == '6':
            story_key = input("Enter story key: ")
            print("Delete status: ", client.delete(story_key))
            print("-------------------------")
        elif choice == '7':
            break
        else:
            print("-------------------------")
            print("Invalid choice. Please enter a number between 1 and 7.")
            print("-------------------------")

if __name__ == "__main__":
    main()