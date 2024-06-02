from flask import Flask, request, jsonify
from sqlalchemy import create_engine
import pandas as pd
import openai
import httpx

app = Flask(__name__)

# Database connection (replace with your credentials)
engine = create_engine('postgresql://username:password@localhost/my_database')

openai.api_key = 'sk-proj-8W1tHA2pEDS5VTVw0rDHT3BlbkFJN0mGTTl6JbkhUqBJ81Wo'

def get_query_from_prompt(user_prompt, timeout=60):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai.api_key}'
    }
    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that only outputs SQL queries."},
            {"role": "user", "content": f"Generate a SQL query for the following request: {user_prompt}. Only provide the SQL query without any additional text."}
        ]
    }

    with httpx.Client(timeout=timeout) as client:
        response = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip()
        else:
            raise Exception("Failed to generate text: " + response.text)

@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    prompt = request.json.get('prompt')
    query = get_query_from_prompt(prompt)
    with engine.connect() as connection:
        data = pd.read_sql(query, connection)
    return data.to_json(orient='records')

if __name__ == "__main__":
    app.run(debug=True)
