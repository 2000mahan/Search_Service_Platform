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


def non_word_spell_correction(word, dictionary, word_frequency, data):
    final_candidates = dict()
    edits1_words = edits1(word, dictionary, word_frequency, data)
    edits2_words = edits2(word, dictionary, word_frequency, data)

    most_probable_edit1_word = max(edits1_words.items(), key=lambda x: x[1])
    most_probable_edit2_word = max(edits2_words.items(), key=lambda x: x[1])
    final_candidates[most_probable_edit1_word[0]] = most_probable_edit1_word[1]
    final_candidates[most_probable_edit2_word[0]] = most_probable_edit2_word[1]
    suggestion = max(final_candidates.items(), key=lambda x: x[1])
    return suggestion[0]


def known(words, dictionary):
    return [w for w in words if w in dictionary]


def edits0(word, dictionary, word_frequency, data):
    key = word + "|" + word
    p_w = 0
    p_x_w = 0
    p_w_x = 0
    word_itself = list()
    if key in data.keys():
        values = data[key][0].split(" ")
        p_x_w = values[0] / values[1]
        p_w = (word_frequency[word]) / (sum(word_frequency.values()))
        p_w_x = p_x_w * p_w
        word_itself.append(word)
        word_itself.append(p_w_x)
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
            p_w = (word_frequency[word]) / (sum(word_frequency.values()))
            p_w_x = p_x_w * p_w
            homophone_candidates[candidate] = p_w_x

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
            p_w = word_frequency[word] / (sum(word_frequency.values()))
            p_w_x = p_x_w * p_w
            edit1_candidates[deletes[counter]] = p_w_x

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
            p_w = word_frequency[word] / (sum(word_frequency.values()))
            p_w_x = p_x_w * p_w
            edit1_candidates[transposes[counter]] = p_w_x
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
                    p_w = word_frequency[word] / (sum(word_frequency.values()))
                    p_w_x = p_x_w * p_w
                    edit1_candidates[replace] = p_w_x
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
                    p_w = word_frequency[word] / (sum(word_frequency.values()))
                    p_w_x = p_x_w * p_w
                    edit1_candidates[insert] = p_w_x
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
