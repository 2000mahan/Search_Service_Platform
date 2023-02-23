import json
import operator
from ibm_cloud import *


def champion_lists(r, language, u_id):
    positional_index = dict()
    doc_id_title = dict()
    term_frq_per_doc = dict()

    try:
        with open("positional_index" + language + u_id + ".json", "r") as read_file:
            positional_index = json.load(read_file)

        with open("doc_id_title" + language + u_id + ".json", "r") as read_file:
            doc_id_title = json.load(read_file)

        with open("term_frq_per_doc" + language + u_id + ".json", "r") as read_file:
            term_frq_per_doc = json.load(read_file)

    except Exception as e:
        log_error("Main Program Error: {0}".format(e))

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
        file_name = "postings_lists" + language + u_id + ".json"
        with open(file_name, "w") as write_file:
            json.dump(postings_lists, write_file)
    except Exception as e:
        log_error("Main Program Error: {0}".format(e))
