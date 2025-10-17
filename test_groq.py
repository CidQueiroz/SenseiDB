
import requests
import sys

def check_groq_key(api_key):
    """Checks if a Groq API key is valid by making a simple request."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": "test"}],
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 401:
            print("Error: Invalid Groq API Key.")
        elif response.status_code == 200:
            print("Success: Groq API Key is valid.")
        else:
            print(f"An error occurred: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"A network error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_groq.py <api_key>")
        sys.exit(1)
    check_groq_key(sys.argv[1])
