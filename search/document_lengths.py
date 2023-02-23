import json
import numpy as np
from ibm_cloud import *


def tfidf(tf, df, N):
    if tf * df == 0:
        return 0.
    return (1 + np.log10(tf)) * np.log10(1. * N / df)


def document_lengths(language, u_id):
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

    term_df = dict()
    for term in positional_index:
        term_df[term] = len(positional_index[term].keys())

    N = len(doc_id_title.keys())
    lengths = np.zeros(N)
    for term in positional_index:
        df = term_df[term]
        docs = positional_index[term].keys()
        for doc_id in docs:
            doc_id = int(doc_id)
            if term not in term_frq_per_doc[doc_id]:
                continue
            tf = term_frq_per_doc[doc_id][term]
            weight = tfidf(tf, df, N)
            lengths[doc_id] += weight ** 2
    lengths = np.sqrt(lengths)
    lengths = list(lengths)
    try:
        file_name = "lengths" + language + u_id + ".json"
        with open(file_name, "w") as write_file:
            json.dump(lengths, write_file)
    except Exception as e:
        log_error("Main Program Error: {0}".format(e))
