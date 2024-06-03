from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text
import pandas as pd
import openai
import httpx
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Set the API key from the environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_query_from_prompt(user_prompt, timeout=60):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai.api_key}'
    }
    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that only outputs SQL queries."},
            {"role": "user", "content": f"Generate a SQL query to select all columns and rows from the table mentioned in the following request: {user_prompt}. Only provide the SQL query without any additional text."}
        ]
    }

    with httpx.Client(timeout=timeout) as client:
        response = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip()
        else:
            raise Exception("Failed to generate text: " + response.text)

app = Flask(__name__)

# Replace with your actual database connection URL
DATABASE_URL = 'postgresql://postgres:1234burger@localhost/my_database'
engine = create_engine(DATABASE_URL)

@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    prompt = request.json.get('prompt')
    query = get_query_from_prompt(prompt)
    with engine.connect() as connection:
        data = pd.read_sql(text(query), connection)
    
    tableau_url = "https://prod-ca-a.online.tableau.com/#/site/damianloch3e5bf99f5a/views/Book1/Dashboard1?:iid=1"
    return jsonify({"tableauUrl": tableau_url})
    #return data.to_json(orient='records')

if __name__ == "__main__":
    app.run(debug=True)
