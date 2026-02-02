import requests
endpoint = "https://api.paxsenix.org/ai-img2img/nano-banana/v3"
api_key = "sk-paxsenix-O8zghnJUeoT8lvH40zfIkPD8YMZKJeVXdepQgrz7ouk8Se3N"


url = str (input("Enter image uri: "))
prompt = str (input("Enter prompt: "))
payload = {
    "prompt": prompt,
    "url": url,
    "model": "nano-banana-pro",
    "ratio": "16:9"
}

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

response = requests.post(endpoint, json=payload, headers=headers)

if response.status_code == 200:
    data = response.json()
    image_uri = data.get("url")

    if image_uri:
        print(f"Image generated! Downloading from: {image_uri}")

        img_data = requests.get(image_uri).content
        with open("generated_image.png", "wb") as handler:
            handler.write(img_data)

        print("Image saved successfully as 'generated_image.png'")
    else:
        print("Success, but no image URI found in the response.")
else:
    print(f"Error {response.status_code}: {response.text}")