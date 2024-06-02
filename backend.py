from flask import Flask, request, jsonify
from sqlalchemy import create_engine
import pandas as pd
import openai

app = Flask(__name__)

# Database connection (replace with your credentials)
engine = create_engine('postgresql://username:password@localhost/my_database')

openai.api_key = 'your-openai-api-key'

def get_query_from_prompt(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100
    )
    query = response.choices[0].text.strip()
    return query

@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    prompt = request.json.get('prompt')
    query = get_query_from_prompt(prompt)
    with engine.connect() as connection:
        data = pd.read_sql(query, connection)
    return data.to_json(orient='records')

if __name__ == "__main__":
    app.run(debug=True)
