import collections
import json
from ibm_cloud import *
import os
from preprocess import *
import nltk


def create_indices(language, u_id, bucket_name):
    try:
        file_name = language + u_id + "data.json"
        data = get_file(file_name)
        data = load_dict(data)

    except Exception as e:
        log_error("Main Program Error: {0}".format(e))

    positional_index = {}
    doc_id_title = {}
    term_frq_per_doc = []
    term_frq = {}
    doc_id_url = {}
    doc_id_content = {}

    count = 0
    doc_id = -1
    for row in data:
        dictionary = dict()
        term_position = dict()
        count = count + 1

        doc_id = doc_id + 1

        doc_id_title[doc_id] = data[row]['title']
        doc_id_url[doc_id] = data[row]['url']

        content = data[row]['content']
        doc_id_content[doc_id] = content
        if language == "Persian":
            parser_persian(content)
            terms = word_tokenize(content)
            remove_stop_words_persian(terms)
            terms = stemmer_and_lemmatizer_persian(terms)
            final_terms = terms
        elif language == "English":
            parser_english(content)
            terms = word_tokenize(content)
            remove_stop_words_english(terms)
            terms = stemmer_english(terms)
            final_terms = terms

        for i in final_terms:
            position_list = list()
            if i in dictionary:
                pass
            else:
                position_counter = 0
                for j in final_terms:
                    position_counter = position_counter + 1
                    if i == j:
                        # calculating word frequency per doc
                        frq = dictionary.get(i, 0)
                        dictionary[i] = frq + 1
                        # calculating word position per doc
                        position_list = term_position.get(i, [])
                        position_list.append(position_counter)
                        term_position[i] = position_list

        term_frq_per_doc.append(dictionary)

        # creating positional index
        for term in term_position.keys():
            if term in positional_index.keys():
                dic1 = positional_index.get(term, {})
                dic1[doc_id] = term_position[term]
                positional_index[term] = dic1
                # pass
            else:
                doc_list = dict()
                doc_list[doc_id] = term_position[term]
                positional_index[term] = doc_list

    positional_index = collections.OrderedDict(sorted(positional_index.items()))

    frequency = 0
    for term in positional_index.keys():
        for words_per_doc in term_frq_per_doc:
            if term in words_per_doc:
                frequency = frequency + words_per_doc[term]
        term_frq[term] = frequency
        frequency = 0

    try:
        names = ["positional_index", "doc_id_title", "doc_id_url", "term_frq", "term_frq_per_doc", "doc_id_content"]
        for i in names:
            file_name = i + language + u_id + ".json"
            if i == "positional_index":
                file_content = json.dumps(positional_index).encode('utf-8')
            elif i == "doc_id_title":
                file_content = json.dumps(doc_id_title).encode('utf-8')
            elif i == "doc_id_url":
                file_content = json.dumps(doc_id_url).encode('utf-8')
            elif i == "term_frq":
                file_content = json.dumps(term_frq).encode('utf-8')
            elif i == "term_frq_per_doc":
                file_content = json.dumps(term_frq_per_doc).encode('utf-8')
            else:
                file_content = json.dumps(doc_id_content).encode('utf-8')

            create_file(bucket_name, file_name, file_content)
    except Exception as e:
        log_error("Main Program Error: {0}".format(e))
