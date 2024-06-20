import re
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from sqlalchemy import create_engine, text
import pandas as pd
import openai
import logging
import httpx
from dotenv import load_dotenv
import os
import uuid

# Load environment variables from .env file
load_dotenv()
# Set the API key from the environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

# Configure logging
logging.basicConfig(level=logging.DEBUG)
# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'c1f680bac80ec50ef314dd7041dc110688d3c02df2951cdb'  # Replace with your actual secret key
CORS(app, resources={r"/*": {"origins": ["http://localhost:8000", "http://127.0.0.1:8000", "https://damianloch.github.io"]}})

# Database connection URL
DATABASE_URL = 'postgresql://postgres:1234burger@localhost/my_database'
engine = create_engine(DATABASE_URL)

def get_query_and_table_from_prompt(user_prompt, session_id, timeout=60):
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
                - monthly_shipping_costs ((columns: month, shipping_cost)
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
                - manufacturing_monthly_defects (columns: month, product_name, defect_count)
                - manufacturing_monthly_orders (columns: month, product_name, total_orders)
                - manufacturing_monthly_production (columns: month, product_name, total_produced)
                - manufacturing_monthly_shipping_costs (columns: month, product_name, shipment_cost)
                - product_defects (ciolumns: quarter, product, defects)
        
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
                - "Create a line graph to illustrate the monthly defect rate for each month in 2023."
                  SQL: SELECT month, defect_rate FROM manufacturing_monthly_defects WHERE month BETWEEN '2023-01-01' AND '2023-12-31';
                - "Generate a line graph showing the monthly shipment costs for each month in 2023."
                  SQL: SELECT month, shipment_cost FROM manufacturing_monthly_shipping_costs WHERE month BETWEEN '2023-01-01' AND '2023-12-31';
                - "Produce a bar graph comparing the total supplier orders for each month in 2023."
                  SQL: SELECT month, total_orders FROM manufacturing_monthly_supplier_orders WHERE month BETWEEN '2023-01-01' AND '2023-12-31';
                -"Generate a multi line chart for production quantities of Product C, and Product D for 2023."
                  SQL: SELECT month, product_name, sales FROM manufacturing_monthly_sales WHERE product_name IN ('Product C', 'Product D') AND month BETWEEN '2023-01-01' AND '2023-12-31';"
                -"Produce a multi line chart about the monthly orders for the manufacturing department for product A, product B and product C."
                  SQL: SELECT month, product_name, total_orders FROM manufacturing_monthly_orders WHERE product_name IN ('Product A', 'Product B', 'Product C') AND month BETWEEN '2023-01-01' AND '2023-06-01';
                "Generate a line graph showing the monthly shipping costs for the year 2023."
                  SQL: SELECT * FROM monthly_shipping_costs WHERE month BETWEEN '2023-01-01' AND '2023-12-31';
                "Create a multi line chart about the monthly defect rate for each product in 2023"
                  SQL: SELECT * FROM product_defects WHERE month BETWEEN '2023-01-01' AND '2023-12-31';
             """},
            {"role": "user", "content": f"Generate a SQL query for the following request: '{user_prompt}'. Only provide the SQL query without any additional text."}
        ],
        # "session": session_id
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

# New function to get a response from the LLM for normal chat, with context
def get_response_from_llm(user_prompt, session_id, timeout=60):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai.api_key}'
    }
    
    # Retrieve conversation history from the session
    messages = session.get('messages', [])
    
    # Add the new user prompt to the conversation
    messages.append({"role": "user", "content": f"{user_prompt}"})
    
    data = {
        "model": "gpt-4o",
        "messages": messages,
        # "session": session_id
    }
    
    with httpx.Client(timeout=timeout) as client:
        response = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        if response.status_code == 200:
            response_data = response.json()['choices'][0]['message']['content'].strip()
            
            # Update the conversation history with the assistant's response
            messages.append({"role": "assistant", "content": response_data})
            session['messages'] = messages
            
            return response_data
        else:
            logging.error(f"Failed to generate text: {response.text}")
            raise Exception("Failed to generate text: " + response.text)

@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    try:
        prompt = request.json.get('prompt')
        logging.debug(f"Received prompt: {prompt}")
        if not prompt:
            logging.error("No prompt provided")
            return jsonify({"error": "No prompt provided"}), 400

        # Generate a unique session ID for maintaining context
        session_id = session.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
        
        # Check if the prompt is asking for a graph
        # if 'graph' in prompt.lower() or 'plot' in prompt.lower() or 'create' in prompt.lower() or 'generate' in prompt.lower()  or 'produce' in prompt.lower():
        if not prompt.endswith(' '):
            # Generate the SQL query and table name from the prompt
            query, table_name = get_query_and_table_from_prompt(prompt, session_id)
            logging.debug(f"Generated query: {query}")
            logging.debug(f"Extracted table name: {table_name}")

            # Extract table name from query
            table_name = re.search(r'FROM\s+(\w+)', query, re.IGNORECASE)
            if table_name:
                table_name = table_name.group(1)
            else:
                logging.error("Table name could not be extracted from the query")
                return jsonify({"error": "Table name could not be extracted from the query"}), 500

            with engine.connect() as connection:
                data = pd.read_sql(text(query), connection)
                logging.debug(f"Query result: {data}")
            # Convert data to the format required by your frontend
            data_json = data.astype(object).to_dict(orient='records')


            if 'multi-line' in prompt.lower() or 'multi line' in prompt.lower():
                # Identify date and value columns dynamically
                date_columns = ['month', 'year', 'quarter']
                value_columns = data.select_dtypes(include=[float, int]).columns.tolist()
                string_columns = data.select_dtypes(include=[object]).columns.tolist()

                date_column = next((col for col in date_columns if col in data.columns), None)
                value_column = next((col for col in value_columns if col not in date_columns), None)
                entity_column = next((col for col in string_columns if col != date_column), None)

                if not all([date_column, value_column, entity_column]):
                    logging.error("Expected columns not found in the data")
                    return jsonify({"error": "Expected columns not found in the data"}), 500

                labels = sorted(list(set(data[date_column].apply(lambda x: x.strftime('%Y-%m')))))
                logging.debug(f"Extracted labels: {labels}")

                entities = sorted(data[entity_column].unique())
                logging.debug(f"Extracted entities: {entities}")

                datasets = {entity: [0] * len(labels) for entity in entities}
                logging.debug(f"Initialized datasets: {datasets}")

                for idx, label in enumerate(labels):
                    for entity in entities:
                        entity_data = data[(data[entity_column] == entity) & (data[date_column].apply(lambda x: x.strftime('%Y-%m')) == label)]
                        if not entity_data.empty:
                            datasets[entity][idx] = entity_data[value_column].sum()

                formatted_datasets = [
                    {
                        'label': entity,
                        'data': values
                    } for entity, values in datasets.items()
                ]

                return jsonify({"labels": labels, "datasets": formatted_datasets, "query": query})

            return jsonify({"data": data_json, "tableName": table_name, "query": query})
        else:
            # New code for handling normal chat response
            response = get_response_from_llm(prompt, session_id)
            return jsonify({"response": response})

    except KeyError as ke:
        logging.error(f"KeyError: {ke}", exc_info=True)
        return jsonify({"error": str(ke)}), 500
    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
