# -*- encoding:utf-8 -*-

# Verisión con bags-of-words

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import string
import nltk

import binascii
import io
from pprint import pprint


import nltk
from nltk.tokenize import RegexpTokenizer

from nltk.corpus import stopwords

from nltk.stem import WordNetLemmatizer
from nltk import ngrams
from nltk.stem.snowball import SnowballStemmer ## Se puede utilizar tambien otro

"""""
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
        pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
    nltk.download()
"""""


def main(args):
    prev =[]
    with io.open(args.texts, encoding="utf-8") as f: ## io.open se le pasa el agumento encoding para leer ya directamente a utf8
        for line in f:
            line = line.strip() ## quitar espacios para que solo quede el texto
            hash = simhash(line, args.restrictiveness, args.ngram) ##Calcular el hash
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

def ngram_to_vector(line, n):
    s = []
    for ngram in nltk.ngrams(line, n):
        base_join = "".encode("utf8")
        s.append(base_join.join(str(i.encode("utf8")) for i in ngram))
    return s

def simhash(line, restric, n):

    v = ngram_to_vector(line, n)

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
    parser.add_argument(
        "-n",
        "--ngram",
        type=int,
        default=5,
        help="Show only %(default)s n in n-grams ")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    exit(main(parse_args()))