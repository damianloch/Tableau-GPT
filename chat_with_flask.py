import requests

def send_prompt(prompt):
    url = "http://localhost:5000/fetch_data"
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        "prompt": prompt
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get("response", data.get("data", "No response"))
    else:
        return f"Failed to get response: {response.status_code}"

def main():
    print(">>")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break
        response = send_prompt(user_input)
        print(f"Assistant: {response}")

if __name__ == "__main__":
    main()
