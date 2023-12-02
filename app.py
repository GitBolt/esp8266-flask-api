from flask import Flask, request, jsonify
import json
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from flask_cors import CORS, cross_origin
import uuid  

load_dotenv()

app = Flask(__name__)
CORS(app)

client = MongoClient(os.environ["DB_URL"])
db = client["test"]

medication_model = {
    "name": str,
    "times": int,
    "counter": int
}

@app.route('/api/medications', methods=['GET', 'POST', 'PUT', 'DELETE'])
def medications():
    if request.method == 'GET':
        try:
            medications = list(db.medications.find())
            return json.dumps(medications), 200
        except Exception as e:
            print(e)
            return jsonify({"error": "Internal Server Error"}), 500

    elif request.method == 'POST':
        try:
            data = request.json
            data['_id'] = str(uuid.uuid4())
            new_medication = {**medication_model, **data}
            db.medications.insert_one(new_medication)
            return jsonify(new_medication), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == 'PUT':
        try:
            data = request.json
            medication_id = data["_id"]
            db.medications.update_one({"_id": medication_id}, {"$set": data})
            updated_medication = db.medications.find_one({"_id": medication_id})
            return jsonify(updated_medication), 200
        except Exception as e:
            return jsonify({"error": "Internal Server Error"}), 500

    elif request.method == 'DELETE':
        try:
            data = request.json
            medication_id = data["_id"]
            print(medication_id, "A")
            db.medications.delete_one({"_id": medication_id})
            return "", 204
        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
