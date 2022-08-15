import collections
from hazm import *
import json
from ibm_cloud import *
import numpy as np
import operator

punctuations = [':', '،', '.', ')', '(', '}', '{', '؟', '!', '-', '/', '؛', '#', '*', '\n', '\"',
                ']', '[', '«', '»', '٪', '+', '٠', '\\', '\"', '_', '\'']

english_numbers_signs = ['0', '1', '2', '3', '4',
                         '5', '6', '7', '8', '9', '%', '@', '_', "\"", '$', '&', ',', '"', '>', '<', '|',
                         '­', ';', 'é', '=', '+', '?']

escape = ['\u200c', '\u200b', '\u200f']

numbers = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹']

englsih_chars_s = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
                   'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

englsih_chars_c = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
                   'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

stop_words = stopwords_list()
stemmer = Stemmer()
lemmatizer = Lemmatizer()


def split(word):
    return [char for char in word]


def query_parser(query):
    for punctuation in punctuations:
        query = query.replace(punctuation, " ")

    for number_sign in english_numbers_signs:
        query = query.replace(number_sign, '')

    for num in numbers:
        query = query.replace(num, '')

    for esc in escape:
        query = query.replace(esc, '')

    for char_s in englsih_chars_s:
        query = query.replace(char_s, '')

    for char_c in englsih_chars_s:
        query = query.replace(char_c, '')

    query_list = query.split()

    counter1 = 0
    for words in stop_words:
        for term in query_list:
            counter1 = 0
            if term == words:
                counter1 = counter1 + 1
            for i in range(counter1):
                query_list.remove(words)

    q_l = list(query_list)
    query_list.clear()
    for term in q_l:
        res = stemmer.stem(term)
        res = lemmatizer.lemmatize(res)
        query_list.append(res)
    return query_list


positional_index = dict()
doc_id_title = dict()
doc_id_url = dict()
term_frq_per_doc = dict()

try:
    positional_index = get_file("positional_index.json")
    positional_index = load_dict(positional_index)

    doc_id_title = get_file("doc_id_title.json")
    doc_id_title = load_dict(doc_id_title)

    doc_id_url = get_file("doc_id_url.json")
    doc_id_url = load_dict(doc_id_url)

    term_frq_per_doc = get_file("term_frq_per_doc.json")
    term_frq_per_doc = load_dict(term_frq_per_doc)

except Exception as e:
    log_error("Main Program Error: {0}".format(e))

query = input("Search: ")
query = query_parser(query)

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
