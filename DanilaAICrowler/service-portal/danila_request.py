import asyncio
import json

import requests
_API_ENDPOINT = "http://195.242.16.26:8080/renderPages"# "http://localhost:8070/renderPages

urls = ["https://stackoverflow.com/questions/645312/what-is-the-quickest-way-to-http-get-in-python", "https://www.geeksforgeeks.org/get-post-requests-using-python/", "https://ru.wikipedia.org/wiki/Заглавная_страница"]
data = {
        "urls": urls,
        "maxTimeoutMs": 3000
    }
headers = {"Content-Type": "application/json", "Authorization": "Basic YXRvbTpoZWxwbWVoZWxwbWVoZWxwbWU="}


response = requests.post(_API_ENDPOINT, data=json.dumps(data), headers=headers)
result = []
print(f"Response: {response.text}")
if response.status_code == 200:
    response_data = json.loads(response.text)
    items = response_data["result"]["completeTasks"]
    print(len(items))
    for i in items:
        print(i["pageText"])
        print("<->"*7)