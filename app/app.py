import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from positional_index import *
from query import *
from spell import *

app = Flask(__name__)

load_dotenv(os.getenv('ENV_FILE', '.env'))


# Request format: curl -X POST -H "Content-type: application/json" -d "{\"query\" : \"دانشگاه صنعتی امیرکبیر\"}"
# "http://127.0.0.1:5000/search"

# curl -X POST -H "Content-type: application/json" -d "{\"query\" : \"دانشگاه صنعتی امیرکبیر\"}" "app-service/search"

@app.route('/search', methods=['POST'])
def search():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        input_query = request.json
        search_result = query(input_query['query'])
        return search_result
    else:
        return 'Content-Type not supported!'


@app.route('/upload_spelling_dataset', methods=['GET'])
def upload_spelling_dataset():
    upload_dataset()

    return "Successfully uploaded spelling dataset"


@app.route('/create_positional_index', methods=['GET'])
def create_positional_index():
    create_indices()

    return "Successfully created positional_index"


if __name__ == '__main__':
    app.run(host=os.getenv('HOST'), port=os.getenv('PORT'))
