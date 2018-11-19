# -*- encoding:utf-8 -*-

#Crawler with robots.txt support and different searching algorithms

from __future__ import print_function
from __future__ import unicode_literals


import argparse
import urlparse

import operator

import nltk
from nltk.tokenize import RegexpTokenizer

from nltk.corpus import stopwords

from nltk.stem import WordNetLemmatizer

import math
import json
import numpy as np

"""
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
        pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
    nltk.download()
"""

class Indexer(object):

    def __init__(self):
        self.docs_index = []
        self.words_index = {}
        self.text = ''

        self.index_next_word = 0

    def index (self, bag_of_words):
        #self.docs_index.append(bag_of_words.values)

        doc_index = {"text":bag_of_words.text,
                     "values": bag_of_words.values}
        self.docs_index.append(doc_index)

        len_doc = bag_of_words.document_len();
        for key in bag_of_words.values.keys():
            tf = self.getTF(bag_of_words.values[key], len_doc=len_doc)
            if key in self.words_index:
                self.words_index[key].append([tf, self.index_next_word])
            else:
                self.words_index[key] = [[tf, self.index_next_word]]


        self.index_next_word += 1

    def score(self, text, enable_stemming, filter_stopwords):
        score = []
        bag_of_words_values = BagOfWords(text=text, enable_stemming=enable_stemming, filter_stopwords=filter_stopwords).values

        for text_key in bag_of_words_values.keys():
            if text_key in self.words_index:
                idf = self.getIDF(text_key)
                for t in self.words_index[text_key]:
                    tf = (t[0][0]) / float(t[0][1])
                    score.append([(tf*idf), t[1]])
                score.sort(reverse=True)

        return score


    def dump(self, fd):
        json_indexer = {}
        json_indexer["docs_index"] = self.docs_index
        json_indexer["terms_index"] = self.words_index
        return json.dump(json_indexer, fd)

    def getTF(self, value, len_doc):
        return [value, len_doc]

    def getIDF(self, text):
        idf = [len(self.words_index[text]), len(self.docs_index)]
        return  1 + math.log(idf[1] / float(idf[0]))


    def to_dict(self):
        return { "docs_index": self.docs_index,
                 "terms_index": self.words_index   }
    def load(self, fd):
        data = json.load(fd)
        self.words_index = data["terms_index"]
        self.docs_index = data["docs_index"]

    def search(self, bag_of_words, number):


        docs={}

        for word in bag_of_words.values:
            score = self.score(word,enable_stemming=False, filter_stopwords=False)
            for s in score:
                if s[1] not in docs:
                    docs[s[1]] = []
                docs[s[1]].append({"text": word, "score": s[0]})

        cos_similarity = self.cosine_similarity(bag_of_words= bag_of_words, docs=docs)

        return cos_similarity


    def cosine_similarity(self, bag_of_words, docs):

        len_doc = bag_of_words.document_len();
        result = []
        for key in docs.keys():
            cos_similarity = {
                "dot_product": 0,
                "query_mod": 0,
                "doc_mod": 0
            }


            for v in docs[key]:
                idf = self.getIDF(v["text"])
                tf = self.getTF(bag_of_words.values[v["text"]], len_doc=len_doc)
                tf_num = float(tf[0]) / tf[1]

                idf_mul_tf = idf * tf_num
                score = v["score"]

                cos_similarity["dot_product"] += score * (idf_mul_tf)
                cos_similarity["doc_mod"] += math.pow(score, 2)

            for w in bag_of_words.values:
                cos_similarity["query_mod"] += math.pow(idf_mul_tf, 2)


            calculate = float(cos_similarity["dot_product"]) / float(math.sqrt(cos_similarity["query_mod"])*math.sqrt(cos_similarity["doc_mod"]))
            result.append([self.docs_index[key]["text"], calculate])


        np.sort(result)
        return result



class BagOfWords(object):
    values = {}
    text = ''



    def __init__(self, text=None, values = None, enable_stemming=False, filter_stopwords=False):
        """Constructor
            Si recibe un string mediante el argumento text lo convierte a un
            diccionario.Si recibe un diccionario simplemente lo copia para su usointerno.
        """
        if (values != None):
            self.values = values;
            if(text != None):
                self.text = text
        if (text != None):
            self.text = text
            self.values = self.string_to_bag_of_words(text, enable_stemming=enable_stemming, filter_stopwords=filter_stopwords);

    @classmethod
    def from_values_dict(self, dict):
        return BagOfWords(values=dict)

    @classmethod
    def from_dict(self, dict):

            bag =  BagOfWords()
            bag.text = dict.get("text")
            bag.values=dict.get("values")
            if(bag.text ==None or bag.values == None): raise ValueError()

            return bag


    def to_dict(self):
        return {
            "text": self.text,
            "values": self.values
        }

    def string_to_bag_of_words(self, text, enable_stemming, filter_stopwords):

        bag = {}
        stopWords = set(stopwords.words('english'))
        lemmatizer = WordNetLemmatizer()

        tokenizer = RegexpTokenizer(r'\w+')
        words = tokenizer.tokenize(text)

        for word in words:
            word = word.lower()
            if ((word in stopWords) and filter_stopwords == True):
                continue
            if enable_stemming == True:
                word = lemmatizer.lemmatize(word, pos='v')
                word = lemmatizer.lemmatize(word, pos='n')
            if word in bag:
                bag[word] += 1
            else:
                bag[word] = 1
        return bag

    def __str__(self):
        """Devuelve un string con la representación del objeto. El objeto
            BagOfWords(“A b a”) está representado por el string “{‘a’: 2, ‘b’: 1}”
        """

        return str(self.values)

    def __len__(self):
        """Devuelve
            el tamaño del diccionario
        """

        return len(self.values)

    def document_len(self):
        cont = 0
        for key, value in self.values.items():
            cont += value
        return cont

    def __iter__(self):
        """Crea un iterador
            que devuelve la clave y el valor de cada elemento del diccionario
            El diccionario {‘a’: 1, ‘b’: 2} devuelve: - (‘a’, 1) en
            la primera llamada - (‘b’, 2) en la primera llamada
        """

        return self.values.iteritems()

    def intersection(self, other):
        """Intersecta 2 bag - of - words
        La intersección de “a b c a” con “a b d” es:
        {‘a’: 1, ‘b’: 1}
        """
        other_bag_of_words = other.values.copy()
        intersection_bag_of_words ={}

        for key, value in self.values.items():
            if key in intersection_bag_of_words:
                intersection_bag_of_words[key] += value
            elif (other_bag_of_words.get(key) != None):
                intersection_bag_of_words[key] = value

        return BagOfWords(values=intersection_bag_of_words)

    def union(self, other):
        """Une 2 bag - of - words
        La unión de “a b c a” con “a b d” es:
        {‘a’: 3, ‘b’: 2, ‘c’: 1, ‘d’: 1}
        """
        union_bag_of_words = other.values.copy()


        for key, value in self.values.items() :
            if key in union_bag_of_words:
                union_bag_of_words[key] += value
            else:
                union_bag_of_words[key] = value


        return BagOfWords(values=union_bag_of_words)



def main():
    texts = [
        "The game of life is a game of everlasting learning",
        "The unexamined life is not worth living",
        "Never stop learning"
    ]

    indexer = Indexer()
    for text in texts:
        text = text.strip()
        bag = BagOfWords(
            text, enable_stemming=False, filter_stopwords=False)
        indexer.index(bag)

    bag = BagOfWords("life learning", enable_stemming=False, filter_stopwords=False)
    results = indexer.search(bag, 10)


    #bag = BagOfWords("life ñu", enable_stemming=False, filter_stopwords=False)
    #results = list(indexer.search(bag, 10))
    print((results))


if __name__ == '__main__':
    main();
