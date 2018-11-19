# -*- encoding:utf-8 -*-

#Crawler with robots.txt support and different searching algorithms

from __future__ import print_function
from __future__ import unicode_literals


import argparse
import urlparse



import nltk
from nltk.tokenize import RegexpTokenizer

from nltk.corpus import stopwords

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

class BagOfWords(object):
    values = {}

    def __init__(self, text=None, values=None):
        """Constructor
            Si recibe un string mediante el argumento text lo convierte a un
            diccionario.Si recibe un diccionario simplemente lo copia para su usointerno.
        """

        if (values != None):
            self.values = values;
        elif (text != None):
            self.values = self.string_to_bag_of_words(text);


    def string_to_bag_of_words(self, text):

        bag = {}
        stopWords = set(stopwords.words('english'))
        #for t in text:
        tokenizer = RegexpTokenizer(r'\w+')
        words = tokenizer.tokenize(text)

        for word in words:
            word = word.lower();
            if word in stopWords:
                continue
            if word in bag:
                bag[word] += 1
            else:
                bag[word] = 1
        return bag

    def __str__(self):
        """Devuelve un string con la representación del objeto. El objeto
            BagOfWords(“A b a”) está representado por el string “{‘a’: 2, ‘b’: 1}”
        """
        text = "{"
        cont = 1;

        for key, value in self.values.items():
            if(cont == 1):
                text +=  "'" + key + "': " + str(value) + ","
            elif (cont == self.values.items().__len__()):
                text += " '" + key + "': " + str(value)
            else:
                text += " '" + key + "': " + str(value) + ","

            cont += 1;
        return text + "}"

    def __len__(self):
        """Devuelve
            el tamaño del diccionario
        """

        return self.values.__len__()


    def __iter__(self):
        """Crea un iterador
            que devuelve la clave y el valor de cada elemento del diccionario
            El diccionario {‘a’: 1, ‘b’: 2} devuelve: - (‘a’, 1) en
            la primera llamada - (‘b’, 2) en la primera llamada
        """

        for key, value in self.values.items():
            yield ((key, value))


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



def coef_dice(bag1, bag2):
    len_intersection = float(bag1.intersection(bag2).__len__())
    sum = bag1.__len__() + bag2.__len__()
    return 2*(len_intersection/sum)

def coef_jaccard(bag1, bag2):
    len_intersection = float( bag1.intersection(bag2).__len__())
    len_union = bag1.union(bag2).__len__()
    return (len_intersection / len_union)

def coef_cosine(bag1, bag2):
    len_intersection = float(bag1.intersection(bag2).__len__())
    mul = float(bag1.__len__() * bag2.__len__())
    return (len_intersection / mul)

def coef_overlapping(bag1, bag2):
    len_intersection = float(bag1.intersection(bag2).__len__())
    min_bag = min(bag1.__len__(), bag2.__len__())
    return (len_intersection / min_bag)

def find_best_text(query, texts, coef):
    best_coef = -1.0
    best_text = None
    bag_q = BagOfWords(query)
    for t in texts:
        coef_new = coef(bag_q, BagOfWords(t))
        if best_coef < coef_new:
            best_coef= coef_new
            best_text = t

    return best_text


def main():
    text = open("cran-1400.txt").readlines();
    queries = open("cran-queries.txt").readlines();

    for q in queries:

        print("Query: {}".format(q))

        best_text = find_best_text(q, text, coef_dice)
        print ("\tPara Dice: {}".format(best_text))

        best_text = find_best_text(q, text, coef_jaccard)
        print("\tPara Jaccard: {}".format(best_text))

        best_text = find_best_text(q, text, coef_cosine)
        print("\tPara Cosine: {}".format(best_text))

        best_text = find_best_text(q, text, coef_overlapping)
        print("\tPara Overlapping: {}".format(best_text))


if __name__ == '__main__':
    main();
