import collections
from hazm import *
import json
from ibm_cloud import *
import numpy as np
import operator
from preprocess import *
import re
from spell import *
from langdetect import detect

language = ""


def tfidf(tf, df, N):
    if tf * df == 0:
        return 0.
    return (1 + np.log10(tf)) * np.log10(1. * N / df)


def champion_lists_create(status, postings_list, positional_index, language, u_id):
    if not status:
        for term in positional_index:
            postings_list[term] = list(positional_index[term].keys())
        return postings_list
    else:
        try:
            with open("postings_lists" + language + u_id + ".json", "r") as read_file:
                postings_lists = json.load(read_file)
        except Exception as e:
            log_error("Main Program Error: {0}".format(e))
        return postings_list


def query(input_query, u_id, ibm_credentials_url):
    pattern = re.compile("[A-Za-z]+")
    match = re.search(pattern, input_query)
    if match is not None:
        language = "English"
    else:
        language = "Persian"

    final_result = dict()
    positional_index = dict()
    doc_id_title = dict()
    doc_id_url = dict()
    term_frq_per_doc = dict()
    term_frq = dict()
    statistics = dict()

    try:
        with open("positional_index" + language + u_id + ".json", "r") as read_file:
            positional_index = json.load(read_file)

        with open("doc_id_title" + language + u_id + ".json", "r") as read_file:
            doc_id_title = json.load(read_file)

        with open("term_frq_per_doc" + language + u_id + ".json", "r") as read_file:
            term_frq_per_doc = json.load(read_file)

        with open("doc_id_url" + language + u_id + ".json", "r") as read_file:
            doc_id_url = json.load(read_file)

        with open("term_frq" + language + u_id + ".json", "r") as read_file:
            term_frq = json.load(read_file)

        with open("statistics" + u_id + ".json", "r") as read_file:
            statistics = json.load(read_file)

    except Exception as e:
        log_error("Main Program Error: {0}".format(e))

    query = input_query
    if language == "English":
        query = parser_english(query)
    else:
        query = parser_persian(query)

    query_list = query.split()

    query_dict = dict()
    for query_word in query_list:
        query_dict[query_word] = list()
        if "*" in query_word:
            convert_query_word = query_word.replace("*", ".+")
            for dictionary_term in positional_index.keys():
                if re.search(convert_query_word, dictionary_term):
                    print(dictionary_term)
                    print(convert_query_word)
                    query_dict[query_word].append(dictionary_term)
            if len(query_dict[query_word]) == 0:
                query_dict[query_word].append(query_word.replace("*", ""))
        else:
            query_dict[query_word] = list()
            query_dict[query_word].append(query_word)

    index_to_choose = list()
    for key in query_dict:
        if key not in positional_index.keys():
            index_to_choose.append(0)
            continue
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

    if language == "English":
        remove_stop_words_english(query_list)
    else:
        remove_stop_words_persian(query_list)
    q_l = list(query_list)
    query_list.clear()
    if language == "English":
        query_list = stemmer_english(q_l)
    else:
        query_list = stemmer_and_lemmatizer_persian(q_l)

    data = download_dataset(u_id, ibm_credentials_url)
    count = 0
    for word in query_list:
        query_list[count] = spell_detection(word, positional_index, term_frq, data)
        count = count + 1

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
    # showing top top_k_results results
    k = int(statistics["top_k_results"])
    # if champion_lists_status is set True we use Champion lists if is set to False we use the default Postings lists
    champion_lists_status = " "
    if statistics["champion_lists_status"] == "False":
        champion_lists_status = False
    elif statistics["champion_lists_status"] == "True":
        champion_lists_status = True
    postings_list = champion_lists_create(champion_lists_status, postings_list, positional_index, language, u_id)
    N = len(doc_id_title.keys())

    lengths = list()
    try:
        with open("lengths" + language + u_id + ".json", "r") as read_file:
            lengths = json.load(read_file)

    except Exception as e:
        log_error("Main Program Error: {0}".format(e))

    scores = dict()
    for qt in query_list:
        if qt not in positional_index.keys():
            continue
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

    number = 1
    for i in docs_to_retrieve_from_positional_index_approach:
        final_result[number] = dict()
        final_result[number]["Title"] = doc_id_title[i]
        final_result[number]["URL"] = doc_id_url[i]
        final_result[number]["ID"] = i
        number = number + 1
        # print("Title: ")
        # print(doc_id_title[i])
        # print("URL: ")
        # print(doc_id_url[i])

    for i in docs_to_retrieve_from_tfidf_approach:
        i = str(i)
        final_result[number] = dict()
        final_result[number]["Title"] = doc_id_title[i]
        final_result[number]["URL"] = doc_id_url[i]
        final_result[number]["ID"] = i
        number = number + 1
        # print("Title: ")
        # print(doc_id_title[i])
        # print("URL: ")
        # print(doc_id_url[i])
    return final_result
