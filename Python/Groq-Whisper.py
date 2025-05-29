import requests
import os

api_key = os.environ.get("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")
url = "https://api.groq.com/openai/v1/models"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)

print(response.json())