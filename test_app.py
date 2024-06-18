import requests

def send_prompt(prompt, session):
    url = "http://localhost:5000/fetch_data"
    payload = {
        "prompt": prompt
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = session.post(url, json=payload, headers=headers)
    return response.json()

def main():
    with requests.Session() as session:
        while True:
            prompt = input("You: ")
            response = send_prompt(prompt, session)
            if 'response' in response:
                print("Assistant:", response['response'])
            elif 'data' in response:
                print("Data:", response['data'])
            elif 'labels' in response:
                print("Labels:", response['labels'])
                print("Datasets:", response['datasets'])
            else:
                print("Error:", response)

if __name__ == "__main__":
    main()
