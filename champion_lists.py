import json
import operator
from ibm_cloud import *

positional_index = dict()
doc_id_title = dict()
term_frq_per_doc = dict()

try:
    positional_index = get_file("positional_index.json")
    positional_index = load_dict(positional_index)

    doc_id_title = get_file("doc_id_title.json")
    doc_id_title = load_dict(doc_id_title)

    term_frq_per_doc = get_file("term_frq_per_doc.json")
    term_frq_per_doc = load_dict(term_frq_per_doc)

except Exception as e:
    log_error("Main Program Error: {0}".format(e))

r = input("Enter r: ")
r = int(r)
postings_lists = dict()

for term in positional_index:
    doc_id_tf = dict()
    for doc_id in range(0, len(doc_id_title)):
        if term in term_frq_per_doc[doc_id]:
            doc_id_tf[doc_id] = term_frq_per_doc[doc_id][term]

    res = sorted(doc_id_tf.items(), key=operator.itemgetter(1), reverse=True)[:r]
    postings_lists[term] = [t[0] for t in res]

try:
    bucket_name = "ir-data"
    file_name = "postings_lists.json"
    file_content = json.dumps(postings_lists).encode('utf-8')
    create_file(bucket_name, file_name, file_content)
except Exception as e:
    log_error("Main Program Error: {0}".format(e))

