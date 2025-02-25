import requests
from bs4 import BeautifulSoup


url = "https://www.4th-ir.com/quest-ai"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}




try:
    response = requests.get(url, headers=headers)
    print(response)
except requests.exceptions.HTTPError as err:
    print(f"HTTP error occurred: {err}")
    exit(1)

# Check if the request was successful
# if response.status_code == 200:
#     print("Successfully fetched the webpage!")
# else:
#     print(f"Failed to fetch the webpage. Status code: {response.status_code}")
