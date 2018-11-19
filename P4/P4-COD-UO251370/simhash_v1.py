# -*- encoding:utf-8 -*-

# Verisión con bags-of-words

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import string
import nltk

from nltk.stem.snowball import SnowballStemmer ## Se puede utilizar tambien otro
import binascii
import io
from pprint import pprint


import nltk
from nltk.tokenize import RegexpTokenizer

from nltk.corpus import stopwords

from nltk.stem import WordNetLemmatizer

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
        lemmatizer = WordNetLemmatizer()

        tokenizer = RegexpTokenizer(r'\w+')
        words = tokenizer.tokenize(text)

        for word in words:
            word = word.lower()
            if word in stopWords:
                continue
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








def main(args):
    prev =[]
    with io.open(args.texts, encoding="utf-8") as f: ## io.open se le pasa el agumento encoding para leer ya directamente a utf8
        for line in f:
            line = line.strip() ## quitar espacios para que solo quede el texto
            hash = simhash(line, args.restrictiveness) ##Calcular el hash
            if hash is None:
                continue
            for p in prev:
                if hash == p[0]:
                    print("\n\n\n")
                    print("FOUND:")
                    print(">" * 80)
                    print(line.encode("utf-8"))
                    print("<" * 80)
                    print(">" * 80)
                    print(p[1].encode("utf-8"))
                    print("<" * 80)
            prev.append((hash, line))


def simhash(line, restric):

    v = BagOfWords(line).values

    if len(v) == 0:
        return None
    hashes = calculate_hashes (v)

    simhash = 0
    for i in range(0, restric):
        simhash ^= hashes[i]

    return simhash



def calculate_hashes(vector):
    hashes = [binascii.crc32(w) & 0xffffffff for w in vector] # el 0xff.... es para que el número sea de un tamaño determinado (es decir, en este caso para que sea de 32bits)
    hashes.sort()
    return hashes



def parse_args():
    parser = argparse.ArgumentParser(description='SimHash')
    parser.add_argument("texts", help="Texts file")
    parser.add_argument(
        "-r",
        "--restrictiveness",
        type=int,
        default=10,
        help="Use %(default)s hashes")
    parser.add_argument( ## No lo vamos a utilizar
        "-s",
        "--show",
        type=int,
        default=-1,
        help="Show only %(default)s lines in each found line. -1 means all")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    exit(main(parse_args()))