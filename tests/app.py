from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text
import pandas as pd

app = Flask(__name__)

# Replace with your actual database connection URL
DATABASE_URL = 'postgresql://postgres:postgres2024@localhost/GPT-Demo'
engine = create_engine(DATABASE_URL)

@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    query = "SELECT * FROM revenue"
    try:
        with engine.connect() as connection:
            data = pd.read_sql(text(query), connection)
        return data.to_json(orient='records')
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
