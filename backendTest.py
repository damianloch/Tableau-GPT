from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    sales_data = [
        {"month": "January", "sales": 12000},
        {"month": "February", "sales": 15000},
        {"month": "March", "sales": 17000},
        {"month": "April", "sales": 13000},
        {"month": "May", "sales": 16000},
        {"month": "June", "sales": 14000},
        {"month": "July", "sales": 18000},
        {"month": "August", "sales": 19000},
        {"month": "September", "sales": 20000},
        {"month": "October", "sales": 17000},
        {"month": "November", "sales": 21000},
        {"month": "December", "sales": 23000}
    ]
    response = {
        "data": sales_data,
        "tableauUrl": "https://public.tableau.com/app/profile/jocelyne.li/viz/GPT-Demo-test/sales_data?publish=yes"  # Update with your Tableau view URL
    }
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
