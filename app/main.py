from flask import Flask, request, jsonify
from google.cloud import firestore
import os

app = Flask(__name__)
db = firestore.Client()

@app.route('/api/data', methods=['POST'])
def create_data():
    """Creates a new document in Firestore."""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message in request body'}), 400
        
        doc_ref = db.collection('messages').document()
        doc_ref.set({
            'message': data['message'],
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        return jsonify({'id': doc_ref.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/<string:doc_id>', methods=['GET'])
def get_data(doc_id):
    """Retrieves a document from Firestore."""
    try:
        doc_ref = db.collection('messages').document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            return jsonify(doc.to_dict()), 200
        else:
            return jsonify({'error': 'Document not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def hello():
    """Returns a simple hello message."""
    return "Hello, World! This is the Flask API for the DevOps Capstone Project."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)