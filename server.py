from flask import Flask, jsonify, request,render_template
from flask_cors import CORS
import pymongo
from bson import ObjectId
from datetime import datetime

app = Flask(__name__)
CORS(app)

# MongoDB Configuration
client = pymongo.MongoClient("mongodb://localhost:27017")
db = client["RyoTenLux"]
transactions_collection = db["transactions"]

# Sample Data for demonstration purposes
sample_transactions = [
    {
        "transactionId": "1",
        "merchantName": "Merchant A",
        "amount": 100.0,
        "status": "success",
        "initiatedAt": datetime(2024, 1, 15, 8, 0, 0),
        "lastUpdatedAt": datetime(2024, 1, 23, 12, 30, 0),
        "timeline": [
        {"date": datetime(2024, 1, 15, 8, 0, 0), "status": "Initiated"},
        {"date": datetime(2024, 1, 23, 12, 30, 0), "status": "Completed"}
        ]

    },
    {
    "transactionId": "123456789",
    "merchantName": "LuxuryGoods Inc.",
    "amount": 500.00,
    "status": "success",
    "initiatedAt": datetime(2024, 1, 15, 8, 0, 0),
    "lastUpdatedAt": datetime(2024, 1, 23, 12, 30, 0),
    "timeline": [
        {"date": datetime(2024, 1, 15, 8, 0, 0), "status": "Initiated"},
        {"date": datetime(2024, 1, 23, 12, 30, 0), "status": "Completed"}
    ]
    },
    {
    "transactionId": "987654321",
    "merchantName": "FashionHub Ltd.",
    "amount": 750.00,
    "status": "in_progress",
    "initiatedAt": datetime(2024, 1, 15, 10, 0, 0),
    "lastUpdatedAt": datetime(2024, 1, 23, 15, 45, 0),
    "timeline": [
        {"date": datetime(2024, 1, 15, 10, 0, 0), "status": "Initiated"},
        {"date": datetime(2024, 1, 21, 12, 0, 0), "status": "Estimated date of settlement"}
    ]
    },
    {
    "transactionId": "456789012",
    "merchantName": "GadgetEmpire Inc.",
    "amount": 300.00,
    "status": "reversed",
    "initiatedAt": datetime(2023, 9, 21, 14, 30, 0),
    "lastUpdatedAt": datetime(2023, 9, 29, 11, 15, 0),
    "timeline": [
        {"date": datetime(2023, 9, 21, 14, 30, 0), "status": "Initiated"},
        {"date": datetime(2023, 9, 26, 18, 45, 0), "status": "Completed"},
        {"date": datetime(2023, 9, 29, 11, 15, 0), "status": "Reversal settlement date"},
        {"date": datetime(2023, 9, 29, 15, 30, 0), "status": "Reversal completed"}
    ]
    },



]

# Insert sample transactions into MongoDB (Remove in production)
#transactions_collection.insert_many(sample_transactions)


@app.route('/transactions')
def dashboard():
    # Retrieve filters from the request parameters
    merchant_name_filter = request.args.get('merchant_name', '')
    # Check if amount_min and amount_max are not empty before converting to float
    amount_min_filter = float(request.args.get('amount_min', 0)) if request.args.get('amount_min', '') != '' else 0
    amount_max_filter = float(request.args.get('amount_max', float('inf'))) if request.args.get('amount_max', '') != '' else float('inf')


    # Build the MongoDB query based on filters
    query = {}
    if merchant_name_filter:
        query['merchantName'] = {'$regex': f'.*{merchant_name_filter}.*', '$options': 'i'}
    query['amount'] = {'$gte': amount_min_filter, '$lte': amount_max_filter}


    transactions = list(transactions_collection.find(query))

    return render_template('dashboard.html', transactions=transactions)

@app.route("/transactions/<transaction_id>", methods=["GET"])
def transaction_details(transaction_id):
    transaction = transactions_collection.find_one({"transactionId": transaction_id})
    return render_template('transaction_details.html', transaction=transaction)


@app.route("/", methods=["GET"])
def get_homepage_summary():
    pipeline = [
    {
        '$group': {
            '_id': '$merchantName',
            'transaction_count': {'$sum': 1}
        }
    }
    ]
    transactions_data = list(transactions_collection.aggregate(pipeline))
    return render_template('homepage.html', transactions_data=transactions_data)

if __name__ == "__main__":
    app.run(debug=True)
