import requests
import json # Import the json library to handle potential JSON response

# Replace 'YOUR_API_KEY' with your actual API key
api_key = 'YOUR_API_KEY'
url = "https://api.paxsenix.biz.id/ai-image/flux"

headers = {
  "Authorization": f"Bearer {api_key}",
  "Content-Type": "application/json"
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

    # Process the response (assuming it's JSON)
    try:
        data = response.json()
        print(json.dumps(data, indent=2)) # Pretty print the JSON response
    except json.JSONDecodeError:
        print("Response was not in JSON format:")
        print(response.text)

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")

param = {
  "model": "string",
  "messages": [
    {
      "role": "user",
      "content": "string"
    }
  ]
}