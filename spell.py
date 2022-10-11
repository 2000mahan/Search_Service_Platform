import re
from ibm_cloud import *


def upload_dataset():
    dictionary = dict()
    with open("spell_correction_dataset.txt", encoding="latin-1") as file:
        for line in file:
            temp = re.split(r"\t+", line)

            dictionary[temp[0]] = list()
            dictionary[temp[0]].append(temp[1])
            dictionary[temp[0]].append(temp[2].strip())
        try:
            bucket_name = "ir-data"
            file_name = "spell_correction_dataset" + ".json"
            file_content = json.dumps(dictionary).encode('utf-8')
            create_file(bucket_name, file_name, file_content)
        except Exception as e:
            log_error("Main Program Error: {0}".format(e))


def download_dataset():
    try:
        data = get_file("spell_correction_dataset.json")
        data = load_dict(data)
        return data

    except Exception as e:
        log_error("Main Program Error: {0}".format(e))


def non_word_spell_detection(word, dictionary, word_frequency, data):
    if word not in dictionary:
        return non_word_spell_correction(word, dictionary, word_frequency, data)
    else:
        return word


def real_word_spell_detection_correction(query_words, dictionary, word_frequency, data):
    final_candidates = dict()
    for word in query_words:
        word_index = query_words.index(word)
        candidates = {**edits0(word, dictionary, word_frequency, data),
                      **edits1(word, dictionary, word_frequency, data),
                      **edits2(word, dictionary, word_frequency, data),
                      **homophones(word, dictionary, word_frequency, data)}
        candidate_sentences = dict()
        for term in candidates:
            query_words[word_index] = term
            # P(w1, ..., wn) = P(w1) * P(w2|w1) * P(w3|w2) * ... * P(wn|wn-1)
            p_w1 = (word_frequency[query_words[0]]) / (sum(word_frequency.values()))
            bigram_probabilities = 1
            counter = 1
            for w in query_words[1:]:
                c01 = 0
                if query_words.index(word) == len(query_words):
                    for doc in dictionary[word]:
                        for position in dictionary[word][doc]:
                            if (position + 1) in dictionary[query_words[counter + 1]][doc]:
                                c01 = c01 + 1
                bigram_probabilities = bigram_probabilities * (c01 / (word_frequency[word]))
                counter = counter + 1
            p_w = p_w1 * bigram_probabilities
            p_x_w = 1
            for w in query_words:
                if w == term:
                    continue
                word_itself = edits0(w, dictionary, word_frequency, data)
                p_x_w = p_x_w * word_itself[1]
            p_w_x = p_w * p_x_w
            sentence = ''.join(query_words)
            candidate_sentences[sentence] = p_w_x
        candidate_sentence = max(candidate_sentences.items(), key=lambda x: x[1])
        final_candidates[candidate_sentence[0]] = candidate_sentence[1]
        query_words[word_index] = word
    most_probable_sentence = max(final_candidates.items(), key=lambda x: x[1])
    return most_probable_sentence[0]


def non_word_spell_correction(word, dictionary, word_frequency, data):
    final_candidates = dict()

    edits1_words = edits1(word, dictionary, word_frequency, data)
    edits1_words_keys = edits1_words.keys()
    for term in edits1_words_keys:
        p_w = (word_frequency[term]) / (sum(word_frequency.values()))
        p_w_x = edits1_words[term] * p_w
        edits1_words[term] = p_w_x

    edits2_words = edits2(word, dictionary, word_frequency, data)
    edits2_words_keys = edits2_words.keys()
    for term in edits2_words_keys:
        p_w = (word_frequency[term]) / (sum(word_frequency.values()))
        p_w_x = edits2_words[term] * p_w
        edits2_words[term] = p_w_x

    most_probable_edit1_word = max(edits1_words.items(), key=lambda x: x[1])
    most_probable_edit2_word = max(edits2_words.items(), key=lambda x: x[1])
    final_candidates[most_probable_edit1_word[0]] = most_probable_edit1_word[1]
    final_candidates[most_probable_edit2_word[0]] = most_probable_edit2_word[1]
    suggestion = max(final_candidates.items(), key=lambda x: x[1])
    return suggestion[0]


def edits0(word, dictionary, word_frequency, data):
    key = word + "|" + word
    p_w = 0
    p_x_w = 0
    p_w_x = 0
    word_itself = list()
    if key in data.keys():
        values = data[key][0].split(" ")
        p_x_w = values[0] / values[1]
        word_itself.append(word)
        word_itself.append(p_x_w)
        return word_itself


def homophones(word, dictionary, word_frequency, data):
    homophone_candidates = dict()
    key = word + "|"
    p_w = 0
    p_x_w = 0
    p_w_x = 0
    for k in data.keys():
        if key in k and data[k][1] == "Homophone" and key[(len(word) + 1):] in dictionary:
            candidate = key[(len(word) + 1):]
            values = data[k][0].split(" ")
            p_x_w = values[0] / values[1]
            homophone_candidates[candidate] = p_x_w

    return homophone_candidates


def edits1(word, dictionary, word_frequency, data):
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    edit1_candidates = dict()
    pairs = splits(word)
    counter = 0

    deletes = [a + b[1:] for (a, b) in pairs if b]
    # Deletion Probability Calculation
    for (a, b) in pairs:
        if b and deletes[counter] in dictionary:
            if len(a) != 0:
                c0 = a[len(a) - 1]
            else:
                c0 = " "
            c1 = b[0]
            c01 = c0 + "" + c1
            key = c0 + "|" + c01
            summation = 0
            if key in data.keys():
                for w in word_frequency:
                    if c01 in w:
                        summation = summation + word_frequency[w]

            p_x_w = data.keys()[0] / summation
            edit1_candidates[deletes[counter]] = p_x_w

        counter = counter + 1
        summation = 0

    transposes = [a + b[1] + b[0] + b[2:] for (a, b) in pairs if len(b) > 1]

    # Transposition Probability Calculation
    for (a, b) in pairs:
        if len(b) > 1 and transposes[counter] in dictionary:
            c0 = b[0]
            c1 = b[1]
            c01 = b[0] + "" + b[1]
            c10 = b[1] + "" + b[0]
            key = c10 + "|" + c01
            summation = 0
            if key in data.keys():
                for w in word_frequency:
                    if c01 in w:
                        summation = summation + word_frequency[w]
            p_x_w = data.keys()[0] / summation
            edit1_candidates[transposes[counter]] = p_x_w
        counter = counter + 1
        summation = 0

    # Replacement Probability Calculation
    for (a, b) in pairs:
        if b:
            for c in alphabet:
                replace = a + c + b[1:]
                if replace in dictionary:
                    c0 = b[0]
                    c1 = c
                    key = c1 + "|" + c0
                    summation = 0
                    if key in data.keys():
                        for w in word_frequency:
                            if c0 in w:
                                summation = summation + word_frequency[w]
                    p_x_w = data.keys()[0] / summation
                    edit1_candidates[replace] = p_x_w
        summation = 0

    # Insertion Probability Calculation
    for (a, b) in pairs:
        if b:
            for c in alphabet:
                insert = a + c + b
                if insert in dictionary:
                    key = a + c + "|" + a
                    summation = 0
                    if key in data.keys():
                        for w in word_frequency:
                            if a in w:
                                summation = summation + word_frequency[w]
                    p_x_w = data.keys()[0] / summation
                    edit1_candidates[insert] = p_x_w
        summation = 0

    return edit1_candidates


def edits2(word, dictionary, word_frequency, data):
    return {e2 for e1 in edits1(word, dictionary, word_frequency, data) for e2 in
            edits1(e1, dictionary, word_frequency, data)}


def splits(word):
    return [(word[:i], word[i:])
            for i in range(len(word) + 1)]

# uncomment the following code if any updates happened to the spell_correction_dataset
# if __name__ == '__main__':
#    upload_dataset()
#    data = download_dataset()
#    print(data)
