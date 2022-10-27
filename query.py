import collections
from hazm import *
import json
from ibm_cloud import *
import numpy as np
import operator
from preprocess import *
import re
from spell import *


def tfidf(tf, df, N):
    if tf * df == 0:
        return 0.
    return (1 + np.log10(tf)) * np.log10(1. * N / df)


def champion_lists_create(status, postings_list):
    if not status:
        for term in positional_index:
            postings_list[term] = list(positional_index[term].keys())
        return postings_list
    else:
        with open("postings_lists.json", "r") as read_file:
            postings_list = json.load(read_file)
        return postings_list


positional_index = dict()
doc_id_title = dict()
doc_id_url = dict()
term_frq_per_doc = dict()
term_frq = dict()

try:
    positional_index = get_file("positional_index.json")
    positional_index = load_dict(positional_index)

    doc_id_title = get_file("doc_id_title.json")
    doc_id_title = load_dict(doc_id_title)

    doc_id_url = get_file("doc_id_url.json")
    doc_id_url = load_dict(doc_id_url)

    term_frq_per_doc = get_file("term_frq_per_doc.json")
    term_frq_per_doc = load_dict(term_frq_per_doc)

    term_frq = get_file("term_frq.json")
    term_frq = load_dict(term_frq)

except Exception as e:
    log_error("Main Program Error: {0}".format(e))

query = input("Search: ")
parser(query)
query_list = query.split()

data = download_dataset()
count = 0

# Non-word spell detection and correction
for word in query_list:
    query_list[count] = non_word_spell_detection(word, positional_index, term_frq, data)
    count = count + 1

#print(query_list)
#exit()

# Real-word spell detection and correction


query_dict = dict()
for query_word in query_list:
    query_dict[query_word] = list()
    if "*" in query_word:
        convert_query_word = query_word.replace("*", ".+")
        for dictionary_term in positional_index.keys():
            if re.search(convert_query_word, dictionary_term):
                query_dict[query_word].append(dictionary_term)
        if len(query_dict[query_word]) == 0:
            query_dict[query_word].append(query_word.replace("*", ""))
    else:
        query_dict[query_word] = list()
        query_dict[query_word].append(query_word)

index_to_choose = list()
for key in query_dict:
    max = term_frq[query_dict[key][0]]
    index = 0
    for value in query_dict[key]:
        temp = term_frq[value]
        if temp > max:
            max = temp
            index = query_dict[key].index(value)
    index_to_choose.append(index)

query_list.clear()
counter = 0
for key in query_dict:
    query_list.append(query_dict[key][index_to_choose[counter]])
    counter = counter + 1

remove_stop_words(query_list)
q_l = list(query_list)
query_list.clear()
query_list = stemmer_and_lemmatizer(q_l)

counter = 0
docs_to_retrieve_from_positional_index_approach = list()
title_results = list()
dict1 = dict()
dict1[len(query)] = query

# Start
positional_postings_lists = list()
doc_id_list = list()
position_list = list()
dict1_values = list(dict1.values())
word_list = list(dict1_values[0])
for term in word_list:
    id_position_per_term = dict()
    for row in positional_index:
        if row == term:
            doc_ids_list = list(positional_index[row].keys())
            for word_doc in doc_ids_list:
                id_position_per_term[word_doc] = list(positional_index[row][word_doc])
    positional_postings_lists.append(id_position_per_term)

# Start positional index Algorithm
end = 0
doc_id = 0
flag = 0
flag3 = 0
check = 1
keys = list(positional_postings_lists[0].keys())
if len(keys) != 0:
    last_doc_id_term_1 = keys[len(keys) - 1]
    last_doc_id_term_1 = int(last_doc_id_term_1)
else:
    end = 1

while True:
    if end == 1:
        end = 0
        break
    if doc_id > last_doc_id_term_1:
        break
    d_i = 0
    for d_i in positional_postings_lists[0]:
        d_i = int(d_i)
        if doc_id > d_i:
            continue
        for term in positional_postings_lists:
            if term == positional_postings_lists[0]:
                continue
            d_i = str(d_i)
            if d_i in term.keys():
                pass
            else:
                flag = -1
        if flag == -1:
            flag = 0
            check = check + 1
            continue
        else:
            flag3 = 1
            d_i = int(d_i)
            doc_id = d_i
            break

    d_i = int(d_i)

    if check == (len(positional_postings_lists[0]) + 1):
        check = 1
        break

    if flag3 == 0 and doc_id == last_doc_id_term_1:
        break

    if flag3 == 0 and d_i == last_doc_id_term_1:
        break
    flag3 = 0

    d_i = str(d_i)

    doc_id = str(doc_id)
    if doc_id not in positional_postings_lists[0].keys():
        break
    term_1_positions_per_doc_id = positional_postings_lists[0][doc_id]
    flag1 = 0
    flag2 = 0
    list_found_docs = list()
    for o in term_1_positions_per_doc_id:
        o = int(o)
        pos = o
        for term in positional_postings_lists:
            if term == positional_postings_lists[0]:
                continue
            pos = pos + 1
            v = term[doc_id]
            pos = str(pos)
            if pos in v:
                pass
            else:
                flag1 = -1
            pos = int(pos)
        if flag == -1:
            flag = 0
            continue
        else:
            list_found_docs.append(doc_id)
            docs_to_retrieve_from_positional_index_approach.append(doc_id)
            break

    doc_id = int(doc_id)
    doc_id = doc_id + 1

# End positional index Algorithm
# End


# for i in docs_to_retrieve_from_positional_index_approach:
#    print(doc_id_title[i])
#    print(doc_id_url[i])

term_df = dict()
for term in positional_index:
    term_df[term] = len(positional_index[term].keys())
postings_list = dict()
# showing top 10 results
k = 10
# if champion_lists_status is set True we use Champion lists if is set to False we use the default Postings lists
champion_lists_status = False
postings_list = champion_lists_create(champion_lists_status, postings_list)
N = len(doc_id_title.keys())

lengths = list()
try:
    lengths = get_file("lengths.json")
    lengths = load_dict(lengths)

except Exception as e:
    log_error("Main Program Error: {0}".format(e))

scores = dict()
for qt in query_list:
    df = term_df[qt]
    qt_tf = query_list.count(qt)
    qt_weight = tfidf(df, qt_tf, N)
    qt_postings = postings_list[qt]
    for doc_id in qt_postings:
        doc_id = int(doc_id)
        if lengths[doc_id] == 0:
            continue
        doc_tf = term_frq_per_doc[doc_id][qt]
        doc_weight = tfidf(df, doc_tf, N)
        try:
            scores[doc_id] += qt_weight * doc_weight
        except KeyError:
            scores[doc_id] = qt_weight * doc_weight

for doc_id in scores:
    scores[doc_id] /= lengths[doc_id]

scores = dict(sorted(scores.items(), key=operator.itemgetter(1), reverse=True))
docs_to_retrieve_from_tfidf_approach = list(scores.keys())[:k]

for i in docs_to_retrieve_from_positional_index_approach:
    if i in docs_to_retrieve_from_tfidf_approach:
        i = int(i)
        docs_to_retrieve_from_tfidf_approach.remove(i)

for i in docs_to_retrieve_from_positional_index_approach:
    print("Title: ")
    print(doc_id_title[i])
    print("URL: ")
    print(doc_id_url[i])

for i in docs_to_retrieve_from_tfidf_approach:
    i = str(i)
    print("Title: ")
    print(doc_id_title[i])
    print("URL: ")
    print(doc_id_url[i])
