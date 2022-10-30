import os
from flask import Flask
from spell import *
from query import *

app = Flask(__name__)


@app.route('/create_positional_index', methods=['POST'])
def create_positional_index():
    os.system('python positional_index.py')

    return "Successfully created positional_index"


@app.route('/upload_spelling_dataset', methods=['POST'])
def upload_spelling_dataset():
    upload_dataset()

    return "Successfully uploaded spelling dataset"


@app.route('/<input_query>', methods=['GET'])
def search(input_query):
    query(input_query)


if __name__ == '__main__':
    app.run(host=os.getenv('HOST'), port=os.getenv('PORT'))
