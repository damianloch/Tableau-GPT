import requests

def test_fetch_data():
    url = "http://127.0.0.1:5001/fetch_data"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json={}, headers=headers)
    
    if response.status_code == 200:
        print("Data fetched successfully:")
        print(response.json())
    else:
        print(f"Error: {response.status_code}")
        print(response.json())

if __name__ == "__main__":
    test_fetch_data()
