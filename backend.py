from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text
import pandas as pd
import openai
import httpx
from dotenv import load_dotenv
import os
from flask_cors import CORS

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
            {"role": "system", "content": """
                You are a helpful assistant that only outputs SQL queries for a PostgreSQL database.
                The database contains the following tables:
                - monthly_revenue (columns: month, revenue)
                - monthly_expenses (columns: month, expenses)
                - quarterly_profits (columns: quarter, profit)
                - annual_revenue (columns: year, revenue)
                - annual_expenses (columns: year, expenses)
                - monthly_net_income (columns: month, net_income)
                - monthly_cash_flow (columns: month, cash_flow)
                - quarterly_operating_costs (columns: quarter, operating_costs)
                - annual_dividends (columns: year, dividends)
                Only generate queries that reference these tables and their columns.
                Example prompts and queries:
                - "Plot a line chart to show the annual revenue growth from 2021 to 2023."
                  SQL: SELECT * FROM annual_revenue WHERE year BETWEEN '2021-01-01' AND '2023-01-01';
                - "Create a line graph to illustrate the monthly net income for each month in 2023."
                  SQL: SELECT * FROM monthly_net_income WHERE month BETWEEN '2023-01-01' AND '2023-12-01';
                """},
            {"role": "user", "content": f"Generate a SQL query for the following request: '{user_prompt}'. Only provide the SQL query without any additional text."}
        ]
    }

    with httpx.Client(timeout=timeout) as client:
        response = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip()
        else:
            raise Exception("Failed to generate text: " + response.text)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://damianloch.github.io"}})  # Update with your GitHub Pages URL

# Replace with your actual database connection URL
DATABASE_URL = 'postgresql://postgres:postgres2024@localhost/GPT-Demo'
engine = create_engine(DATABASE_URL)

@app.route('/fetch_data', methods=['POST', 'OPTIONS'])
def fetch_data():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers.add('Access-Control-Allow-Origin', 'https://damianloch.github.io')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    try:
        prompt = request.json.get('prompt')
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400

        query = get_query_from_prompt(prompt)
        with engine.connect() as connection:
            data = pd.read_sql(text(query), connection)
        
        # Convert data to the format required by your frontend
        data_json = data.to_dict(orient='records')
        response = jsonify({"data": data_json})
        response.headers.add('Access-Control-Allow-Origin', 'https://damianloch.github.io')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    except Exception as e:
        response = jsonify({"error": str(e)})
        response.headers.add('Access-Control-Allow-Origin', 'https://damianloch.github.io')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response, 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
