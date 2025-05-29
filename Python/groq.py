import requests
import os

api_key = os.environ.get("GROQ_API_KEY") # Read API key from environment variable

if not api_key:
    print("Error:  environment variable not set.")
    exit()


url = "https://api.groq.com/openai/v1/audio/translations"
headers = {"Authorization": f"bearer {api_key}"}
files = {"file": open("./audio.wav", "rb")} # 'rb' for binary read
data = {
    "model": "whisper-large-v3",
    "prompt": "Specify context or spelling",
    "language": "en",
    "temperature": 0,
    "response_format": "json",
}

try:
    response = requests.post(url, headers=headers, files=files, data=data)
    response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

    print(response.json())  # Or response.text if response_format isn't JSON

except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
    if response is not None:
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text}")


finally:
    if 'file' in files and files['file']:
        files['file'].close()  # Always close the file after using it!