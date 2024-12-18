import requests
import json

def get_links(question):
    url = "https://google.serper.dev/search"
    payload = json.dumps({
      "q": "apple inc",
      "gl": "ru"
    })
    headers = {
      'X-API-KEY': '9bfd930bbc25fa413f6d5c308a8487e307ae6a24',
      'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    data = json.loads(response.text)
    organic_results = data.get("organic", [])
    ret_data = [{"title": item["title"], "snippet": item["snippet"], "link": item["link"]} for item in
                            organic_results]
    return ret_data



print(len(get_links("Apple")))