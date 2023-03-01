import json
from ibm_cloud import *
import collections
from query import *
import numpy as np
from positional_index import *
from user_management import *
import requests

doc_id_content = dict()
language = ""


def split(word):
    return [char for char in word]


def NDCG_test(u_id, ibm_credentials_url):
    accuracy = 0
    response = requests.get(ibm_credentials_url)
    open("credentials.json", "wb").write(response.content)
    with open("credentials.json", "r") as read_file:
        credentials = json.load(read_file)
    try:
        file_name = u_id + "test.json"
        test_data = get_file(file_name, credentials)
        test_data = load_dict(test_data)

    except Exception as e:
        log_error("Main Program Error: {0}".format(e))

    for test_data_query in test_data.values():
        pattern = re.compile("[A-Za-z]+")
        match = re.search(pattern, test_data_query)
        if match is not None:
            language = "English"
        else:
            language = "Persian"

        try:
            with open("doc_id_content" + language + u_id + ".json", "r") as read_file:
                doc_id_content = json.load(read_file)

        except Exception as e:
            log_error("Main Program Error: {0}".format(e))

        if language == "English":
            parser_english(test_data_query)
        else:
            parser_persian(test_data_query)

        query_list = test_data_query.split()

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

        states = list()
        # Multiple Word Query
        for i in range(0, 2 ** len(query_list)):
            new_list = list(query_list)
            dic1 = dict()
            b = format(i, "b")
            b = split(b)

            while len(b) != len(query_list):
                b.insert(0, '0')

            for j in range(0, len(b)):
                if b[j] == '1':
                    new_list[j] = '0'
            count = 0
            for n in new_list:
                if n == '0':
                    count = count + 1
            for c in range(0, count):
                new_list.remove('0')

            dic1[len(new_list)] = new_list
            states.append(dic1)

        possible_strings = list(list())
        for i in states:
            str = " "
            for j in i.values():
                l = len(j)
                str = str.join(j)
                possible_strings.append([l, str])

        del possible_strings[len(possible_strings) - 1]
        doc_ids = list()
        doc_id_score = dict()
        search_result = query(test_data_query, u_id, ibm_credentials_url)
        for i in search_result:
            doc_ids.append(search_result[i]["ID"])
        for doc in doc_ids:
            for j in reversed(possible_strings):
                if j[1] in doc_id_content[doc]:
                    doc_id_score[doc] = j[0]
                break

        DCG_RF = 0
        DCG_GT = 0

        counter = 1
        for i in doc_id_score:
            if counter == 1:
                DCG_RF = doc_id_score[i]
                counter = counter + 1
            else:
                DCG_RF = DCG_RF + (doc_id_score[i] / np.log2(counter))
                counter = counter + 1

        doc_id_score = dict(sorted(doc_id_score.items(), key=operator.itemgetter(1), reverse=True))

        counter = 1
        for i in doc_id_score:
            if counter == 1:
                DCG_GT = doc_id_score[i]
                counter = counter + 1
            else:
                DCG_GT = DCG_GT + (doc_id_score[i] / np.log2(counter))
                counter = counter + 1

        NDCG = (DCG_RF / DCG_GT) * 100
        accuracy += NDCG
    accuracy = accuracy / len(test_data)
    accuracy = f'{accuracy:.3f}'
    return accuracy


