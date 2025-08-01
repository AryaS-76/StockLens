import requests
import os
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
params = {
    "key": os.getenv("GOOGLE_API_KEY") # Your API key
}

payload = {
    "contents": [
        {
            "parts": [
                {"text": "Explain how AI works in a few words"}
            ]
        }
    ]
}

response = requests.post(url, params=params, json=payload)
print(response.status_code)
print(response.json())
