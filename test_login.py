import requests
from requests.auth import HTTPBasicAuth

url = "http://127.0.0.1:8000/api/history/"
username = "testuser_debug"
password = "testpassword123"

try:
    response = requests.get(url, auth=HTTPBasicAuth(username, password))
    print(f"Status Code: {response.status_code}")
    if response.status_code != 200:
        with open("error.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("Error content saved to error.html")
except Exception as e:
    print(f"Error: {e}")
