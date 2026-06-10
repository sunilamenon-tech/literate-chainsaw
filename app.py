import requests

API_KEY = "your-api-key-here"  # Replace with your actual key

# Test different models
models_to_test = [
    "gemini-1.5-pro",
    "gemini-1.5-flash", 
    "gemini-pro",
    "gemini-2.0-flash-exp"
]

for model in models_to_test:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": "Say hello in one word"}]}]
    }
    response = requests.post(url, json=payload).json()
    
    if 'candidates' in response:
        print(f"✅ {model} WORKS!")
    else:
        print(f"❌ {model} FAILED: {response.get('error', {}).get('message', 'Unknown')}")
