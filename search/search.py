import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from positional_index import *
from document_lengths import *
from champion_lists import *
from statistics_file import *
from user_management import *
from NDCG import *
from query import *
from spell import *
import time
from nltk_downloader import *

app = Flask(__name__)

load_dotenv(os.getenv('ENV_FILE', '.env'))


# Request format: curl -X POST -H "Content-type: application/json" -d "{\"query\" : \"دانشگاه صنعتی امیرکبیر\"}"
# "http://127.0.0.1:5000/search"

# curl -X POST -H "Content-type: application/json" -d "{\"query\" : \"دانشگاه صنعتی امیرکبیر\"}" "app-service/search"
# curl -X POST -H "Content-type: application/json" -d "{\"query\" : \"extraordinarily succesful mission\"}"
# "http://127.0.0.1:5000/search"
@app.route('/search', methods=['POST'])
def search():
    content_type = request.headers.get('Content-Type')
    token = request.headers.get('token')
    u_id = user_id(token)
    if content_type == 'application/json':
        input_query = request.json
        start_time = time.time()
        search_result = query(input_query['query'], u_id)
        t = time.time() - start_time
        t = str(t)
        t = "Retrieval Time: " + t + " seconds"
        return '{} {} {}'.format(input_query['query'], search_result, t)
    else:
        return 'Content-Type not supported!'


# curl -X POST -H "Content-type: application/json" -d "{\"top_k_results\" : \"10\", \"champion_lists_status\" :
# \"False\"}" "http://127.0.0.1:5000/create_statistics"
@app.route('/create_statistics', methods=['POST'])
def create_statistics():
    content_type = request.headers.get('Content-Type')
    token = request.headers.get('token')
    bucket_name = request.headers.get('bucket_name')
    u_id = user_id(token)
    if content_type == 'application/json':
        input_query = request.json
        create_statistics_file(input_query["top_k_results"], input_query["champion_lists_status"], u_id, bucket_name)
        return "Successfully created statistics file"
    else:
        return "Content-Type not supported!"


# curl get "http://127.0.0.1:5000/upload_spelling_dataset"
@app.route('/upload_spelling_dataset', methods=['GET'])
def upload_spelling_dataset():
    token = request.headers.get('token')
    bucket_name = request.headers.get('bucket_name')
    u_id = user_id(token)
    upload_dataset(u_id, bucket_name)

    return "Successfully uploaded spelling dataset"


# curl -X POST -H "Content-type: application/json" -d "{\"range\" : \"20\"}"
# "http://127.0.0.1:5000/create_champion_lists"
@app.route('/create_champion_lists', methods=['POST'])
def create_champion_lists():
    content_type = request.headers.get('Content-Type')
    token = request.headers.get('token')
    bucket_name = request.headers.get('bucket_name')
    u_id = user_id(token)
    if content_type == 'application/json':
        input_query = request.json
        champion_lists(input_query["range"], "English", u_id, bucket_name)
        champion_lists(input_query["range"], "Persian", u_id, bucket_name)
        return "Successfully created champion lists"
    else:
        return "Content-Type not supported!"


# curl -X POST -H "Content-type: application/json" -d "{\"language\" : \"English\"}"
# "http://127.0.0.1:5000/create_positional_index"
@app.route('/create_positional_index', methods=['POST'])
def create_positional_index():
    content_type = request.headers.get('Content-Type')
    token = request.headers.get('token')
    bucket_name = request.headers.get('bucket_name')
    u_id = user_id(token)
    if content_type == 'application/json':
        input_query = request.json
        create_indices(input_query["language"], u_id, bucket_name)
        document_lengths(input_query["language"], u_id, bucket_name)
        return "Successfully created positional_index"
    else:
        return "Content-Type not supported!"


@app.route('/test', methods=['POST'])
def test():
    token = request.headers.get('token')
    u_id = user_id(token)
    return '{}'.format(NDCG_test(u_id))


if __name__ == '__main__':
    app.run(host=os.getenv('HOST'), port=os.getenv('PORT'))
