#this is meant to create a JSON file placeholder

import json

# Create a sample JSON data with different values
sample_data = {
    "data": [
        {"month": "Sun, 01 Jan 2023 00:00:00 GMT", "net_income": 6000},
        {"month": "Wed, 01 Feb 2023 00:00:00 GMT", "net_income": 9000},
        {"month": "Wed, 01 Mar 2023 00:00:00 GMT", "net_income": 15000},
        {"month": "Sat, 01 Apr 2023 00:00:00 GMT", "net_income": 20000},
        {"month": "Mon, 01 May 2023 00:00:00 GMT", "net_income": 25000},
        {"month": "Thu, 01 Jun 2023 00:00:00 GMT", "net_income": 30000},
        {"month": "Sat, 01 Jul 2023 00:00:00 GMT", "net_income": 35000},
        {"month": "Tue, 01 Aug 2023 00:00:00 GMT", "net_income": 40000},
        {"month": "Fri, 01 Sep 2023 00:00:00 GMT", "net_income": 45000},
        {"month": "Sun, 01 Oct 2023 00:00:00 GMT", "net_income": 50000},
        {"month": "Wed, 01 Nov 2023 00:00:00 GMT", "net_income": 55000},
        {"month": "Fri, 01 Dec 2023 00:00:00 GMT", "net_income": 60000}
    ]
}

# Save the sample data to a JSON file
file_path = "./sample_data.json"
with open(file_path, "w") as file:
    json.dump(sample_data, file, indent=4)

file_path
