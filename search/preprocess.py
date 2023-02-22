import nltk

from hazm import *
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('stopwords')

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


def split(word):
    return [char for char in word]


def parser_persian(input):
    for punctuation in punctuations:
        input = input.replace(punctuation, " ")

    for number_sign in english_numbers_signs:
        input = input.replace(number_sign, '')

    for num in numbers:
        input = input.replace(num, '')

    for esc in escape:
        input = input.replace(esc, '')

    for char_s in english_chars_s:
        input = input.replace(char_s, '')

    for char_c in english_chars_c:
        input = input.replace(char_c, '')


def remove_stop_words_persian(my_list):
    stop_words = stopwords_list()
    counter = 0
    for words in stop_words:
        for term in my_list:
            counter = 0
            if term == words:
                counter = counter + 1
            for i in range(counter):
                my_list.remove(words)


def stemmer_and_lemmatizer_persian(my_list):
    stemmer = Stemmer()
    lemmatizer = Lemmatizer()
    new_list = list()
    for term in my_list:
        res = stemmer.stem(term)
        res = lemmatizer.lemmatize(res)
        new_list.append(res)
    return new_list


def parser_english(input):
    for punctuation in punctuations:
        input = input.replace(punctuation, " ")

    for number_sign in english_numbers_signs:
        input = input.replace(number_sign, '')

    for num in numbers:
        input = input.replace(num, '')

    for esc in escape:
        input = input.replace(esc, '')


def remove_stop_words_english(my_list):
    stop_words = set(stopwords.words('english'))
    counter = 0
    for words in stop_words:
        for term in my_list:
            counter = 0
            if term == words:
                counter = counter + 1
            for i in range(counter):
                my_list.remove(words)


def stemmer_english(my_list):
    stemmer = PorterStemmer()
    new_list = list()
    for term in my_list:
        term = term.lower()
        res = stemmer.stem(term)
        new_list.append(res)
    return new_list
