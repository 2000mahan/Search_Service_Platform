import json
import numpy as np
from ibm_cloud import *


def tfidf(tf, df, N):
    if tf * df == 0:
        return 0.
    return (1 + np.log10(tf)) * np.log10(1. * N / df)


def document_lengths(language, u_id, bucket_name):
    positional_index = dict()
    doc_id_title = dict()
    term_frq_per_doc = dict()

    try:
        positional_index = get_file("positional_index" + language + u_id + ".json")
        positional_index = load_dict(positional_index)

        doc_id_title = get_file("doc_id_title" + language + u_id + ".json")
        doc_id_title = load_dict(doc_id_title)

        term_frq_per_doc = get_file("term_frq_per_doc" + language + u_id + ".json")
        term_frq_per_doc = load_dict(term_frq_per_doc)

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
        file_content = json.dumps(lengths).encode('utf-8')
        create_file(bucket_name, file_name, file_content)
    except Exception as e:
        log_error("Main Program Error: {0}".format(e))
