import collections
from hazm import *
import json
from ibm_cloud import *
import os

try:
    data = get_file("data.json")
    data = load_dict(data)

except Exception as e:
    log_error("Main Program Error: {0}".format(e))

positional_index = {}
doc_id_title = {}
term_frq_per_doc = []
term_frq = {}
doc_id_url = {}

punctuations = [':', '،', '.', ')', '(', '}', '{', '؟', '!', '-', '/', '؛', '#', '*', '\n', '\"',
                ']', '[', '«', '»', '٪', '+', '٠', '\\', '\"', '_', '\'']

english_numbers_signs = ['0', '1', '2', '3', '4',
                         '5', '6', '7', '8', '9', '%', '@', '_', "\"", '$', '&', ',', '"', '>', '<', '|',
                         '­', ';', 'é', '=', '+', '?']

escape = ['\u200c', '\u200b', '\u200f']

numbers = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹']

english_chars_s = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
                   'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

english_chars_c = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
                   'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

stop_words = stopwords_list()
stemmer = Stemmer()
lemmatizer = Lemmatizer()

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

    for punctuation in punctuations:
        content = content.replace(punctuation, " ")

    for number_sign in english_numbers_signs:
        content = content.replace(number_sign, '')

    for num in numbers:
        content = content.replace(num, '')

    for esc in escape:
        content = content.replace(esc, '')

    for char_s in english_chars_s:
        content = content.replace(char_s, '')

    for char_c in english_chars_c:
        content = content.replace(char_c, '')

    terms = word_tokenize(content)
    counter = 0

    # removing stop words
    for words in stop_words:
        for term in terms:
            if term == words:
                counter = counter + 1
        for i in range(counter):
            terms.remove(words)
        counter = 0

    final_terms = list()

    for term in terms:
        res = stemmer.stem(term)
        res = lemmatizer.lemmatize(res)
        final_terms.append(res)

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
    bucket_name = "ir-data"
    names = ["positional_index", "doc_id_title", "doc_id_url", "term_frq", "term_frq_per_doc"]
    for i in names:
        file_name = i + ".json"
        if i == "positional_index":
            file_content = json.dumps(positional_index).encode('utf-8')
        elif i == "doc_id_title":
            file_content = json.dumps(doc_id_title).encode('utf-8')
        elif i == "doc_id_url":
            file_content = json.dumps(doc_id_url).encode('utf-8')
        elif i == "term_frq":
            file_content = json.dumps(term_frq).encode('utf-8')
        else:
            file_content = json.dumps(term_frq_per_doc).encode('utf-8')

        create_file(bucket_name, file_name, file_content)

except Exception as e:
    log_error("Main Program Error: {0}".format(e))

