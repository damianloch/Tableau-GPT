import requests

def test_fetch_data():
    url = "http://127.0.0.1:5000/fetch_data"  # Ensure it matches your Flask server port
    headers = {"Content-Type": "application/json"}
    prompt = "Generate a line graph showing the monthly revenue trend for the year 2023."
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
