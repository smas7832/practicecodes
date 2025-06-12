import requests as rq
import json # Import the json library to handle potential JSON response

# Replace 'YOUR_API_KEY' with your actual API key
api_key = None
url = "https://api.paxsenix.biz.id/lyrics/plain"

data = {
  "model": "pax-uncensor",
  "messages": [
    {
      "role": "user",
      "content": "input"
    }
  ]
}
params = {
    "title": "Ek Raat",
    "artist": "Vilen" 
}
headers = {
  "Authorization": f"Bearer {api_key}",
  "Content-Type": "application/json"
}

response = rq.post(url, params=params)
print(response.url)
response.raise_for_status
print(response.status_code)