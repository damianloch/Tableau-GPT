import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
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
def get_query_and_table_from_prompt(user_prompt, timeout=60):
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
                - monthly_sales (columns: month, product_name, sales)
                - employee_performance (columns: quarter, employee_name, performance_rating)
                - department_expenses (columns: month, department_name, expenses)
                - customer_feedback (columns: month, product_name, feedback_score)
                Only generate queries that reference these tables and their columns.
                Use the format 'YYYY-MM-DD' for date values.
                For quarters, use the date range to specify the quarter.
                Example prompts and queries:
                - "Plot a line chart to show the annual revenue growth from 2021 to 2023."
                  SQL: SELECT * FROM annual_revenue WHERE year BETWEEN '2021-01-01' AND '2023-12-31';
                - "Create a line graph to illustrate the monthly net income for each month in 2023."
                  SQL: SELECT * FROM monthly_net_income WHERE month BETWEEN '2023-01-01' AND '2023-12-31';
                - "Generate a line graph showing the monthly revenue trend for the year 2023."
                  SQL: SELECT * FROM monthly_revenue WHERE month BETWEEN '2023-01-01' AND '2023-12-31';
                - "Produce a bar graph comparing quarterly profits for the four quarters of 2023."
                  SQL: SELECT * FROM quarterly_profits WHERE quarter BETWEEN '2023-01-01' AND '2023-12-31';
                - "Generate a line chart showing the monthly sales trend for Product A in 2023."
                  SQL: SELECT month, sales FROM monthly_sales WHERE product_name = 'Product A' AND month BETWEEN '2023-01-01' AND '2023-12-31';
                - "Create a bar graph comparing the quarterly performance ratings of Alice and Bob in 2023."
                  SQL: SELECT quarter, employee_name, performance_rating FROM employee_performance WHERE quarter BETWEEN '2023-01-01' AND '2023-12-31';
                - "Produce a line chart to illustrate the monthly expenses for the Marketing department in 2023."
                  SQL: SELECT month, expenses FROM department_expenses WHERE department_name = 'Marketing' AND month BETWEEN '2023-01-01' AND '2023-12-31';
                - "Generate a bar graph showing the monthly feedback scores for Product B in 2023."
                  SQL: SELECT month, feedback_score FROM customer_feedback WHERE product_name = 'Product B' AND month BETWEEN '2023-01-01' AND '2023-12-31';
            """},
            {"role": "user", "content": f"Generate a SQL query for the following request: '{user_prompt}'. Only provide the SQL query without any additional text."}
        ]
    }
    with httpx.Client(timeout=timeout) as client:
        response = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        if response.status_code == 200:
            response_data = response.json()['choices'][0]['message']['content'].strip()
            # Assuming the response_data is a plain string SQL query
            # You may need to parse the response appropriately based on actual API response
            query = response_data
            table_name = query.split('FROM')[1].split()[0].strip()  # Extract table name from query
            return query, table_name
        else:
            logging.error(f"Failed to generate text: {response.text}")
            raise Exception("Failed to generate text: " + response.text)
# Configure logging
logging.basicConfig(level=logging.DEBUG)
# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'c1f680bac80ec50ef314dd7041dc110688d3c02df2951cdb'  # Replace with your actual secret key
CORS(app, resources={r"/*": {"origins": ["http://localhost:8000", "http://127.0.0.1:8000", "https://damianloch.github.io"]}})
# Database connection URL
DATABASE_URL = 'postgresql://postgres:1234burger@localhost/postgres'
engine = create_engine(DATABASE_URL)
@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    try:
        prompt = request.json.get('prompt')
        logging.debug(f"Received prompt: {prompt}")
        if not prompt:
            logging.error("No prompt provided")
            return jsonify({"error": "No prompt provided"}), 400
        # Generate the SQL query and table name from the prompt
        query, table_name = get_query_and_table_from_prompt(prompt)
        logging.debug(f"Generated query: {query}")
        logging.debug(f"Extracted table name: {table_name}")
        with engine.connect() as connection:
            data = pd.read_sql(text(query), connection)
            logging.debug(f"Query result: {data}")
        # Convert data to the format required by your frontend
        data_json = data.to_dict(orient='records')
        return jsonify({"data": data_json, "tableName": table_name, "query": query})
    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
if __name__ == "__main__":
    app.run(debug=True, port=5000)