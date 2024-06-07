import requests

def test_fetch_data():
    url = "http://127.0.0.1:3000/api/fetch_data"  # Ensure it matches your Flask server port
    headers = {"Content-Type": "application/json"}
    prompt = "Create a line graph to illustrate the monthly net income for each month in 2023."
    response = requests.post(url, json={"prompt": prompt}, headers=headers)

    if response.status_code == 200:
        try:
            print("Data fetched successfully:")
            print(response.json())
        except ValueError:
            print("Response is not in JSON format")
            print(response.text)
    else:
        print(f"Error: {response.status_code}")
        try:
            print(response.json())
        except ValueError:
            print("Response is not in JSON format")
            print(response.text)

if __name__ == "__main__":
    test_fetch_data()