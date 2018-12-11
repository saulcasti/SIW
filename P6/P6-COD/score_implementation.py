# -*- encoding:utf-8 -*-

# Este fichero compara el valor obtenido con el valor experado y da un score al metodo implementado

# Ejemplo de uso
#     python score_implementation.py common.py -d articles_99python score_implementation.py common.py -d articles_99

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import io
import argparse
import gzip


def main(args):
    try:
        python_file = args.file
        if python_file.endswith(".py"):
            python_file = python_file[:-3]
        implementation = __import__(python_file)
        Indexer = implementation.Indexer
        BagOfWords = implementation.BagOfWords
    except ImportError:
        print("Unable to import: {}".format(args.file))
        return 1
    except AttributeError:
        print("The Python file must define simhash: {}".format(args.file))
        return 1
    score_implementation(Indexer, BagOfWords, args.dataset)
    return 0


def score_implementation(Indexer, BagOfWords, dataset):
    expected_matches = read_truth(dataset + ".truth")
    indexer = create_indexer(dataset + ".train", Indexer, BagOfWords)
    got_matches = search(indexer)
    print_diff(expected_matches, got_matches)


def create_indexer(file, Indexer, BagOfWords):
    print("INDEXING")
    indexer = Indexer()
    with io.open(file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            bag = BagOfWords(line, filter_stopwords=False)
            indexer.index(bag)
            print(".", end="")
    print("DONE")
    return indexer


def search(indexer,):
    print("SEARCHING")
    matches = {}
    for bag in indexer.docs_index:
        query = bag.text.split(" ")[0]
        # CUIDADO: El primer resultado obtenido es la propia linea.
        # El segundo es el bueno porque es la siguiente linea con mayor similitud
        for result, score in indexer.search(bag, 2):
            result = result.split(" ")[0]
        matches[query] = (result, score)
        print(".", end="")
    print("DONE")
    return matches


def print_diff(expected_matches, got_matches):
    total = len(expected_matches)
    ok = 0
    for query, expected in expected_matches.iteritems():
        got, score = got_matches[query]
        if expected == got:
            print("[ OK ]    ", end="")
            ok += 1
        else:
            print("[FAIL]    ", end="")
        print("QUERY: {:<10} EXPECTED: {:<10} GOT: {:<10} SCORE: {:<10}".format(query, expected, got, score))
    print("\n\nSCORE: {} / {} = {}".format(ok, total, ok/total))


def read_truth(text):
    matches = {}
    with io.open(text, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            query, result = line.split(" ") 
            matches[query] = result
    return matches


def parse_args():
    parser = argparse.ArgumentParser(description='Test and score SimHash implmentations')
    parser.add_argument("file", help="Python file")
    parser.add_argument("-d", "--dataset", default="articles_100", help="Use this dataset: %(default)s")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    exit(main(parse_args()))