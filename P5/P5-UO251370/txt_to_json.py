# -*- encoding:utf-8 -*-

#Crawler with robots.txt support and different searching algorithms

from __future__ import print_function
from __future__ import unicode_literals


import argparse
import json
import io
from StringIO import StringIO
from indexer_v1 import Indexer, BagOfWords

def parse_args():
    parser = argparse.ArgumentParser(description='txtToJson')
    parser.add_argument("texts", help="Texts file")
    args = parser.parse_args()
    return args


def create_json(indexer, file_name, file_name_json):
    """Método que a partir de: un objeto Indexer, el fichero fuente y el nombre
    del futuro fichero json; crea y guarda un fichero .json
        """
    with io.open(file_name,encoding="utf-8") as f:
        for line in f:
            bag_of_words = BagOfWords(text=line)
            indexer.index(bag_of_words=bag_of_words)

    fd = StringIO()
    indexer.dump(fd)
    fd.seek(0)


    with open(file_name_json, 'w') as file:
       json.dump(json.load(fd), file)


def load_json(file_name):
    """Método que carga el fichero json indicado en el parámetro
    """
    json_readed = json.loads(open(file_name).read())
    cont_words_index = 0
    cont_docs_index = 0

    for key in (json_readed["words_index"]).items():
        cont_words_index += 1
    for doc in (json_readed["docs_index"]):
        cont_docs_index += 1

    print("Contador words_index:\t")
    print(cont_words_index)
    print("\nContador docs_index:\t")
    print(cont_docs_index)

def main(args):
    indexer = Indexer()
    file_name_json = args.texts.split('.')[0] + '.json'

    create_json(indexer=indexer, file_name=args.texts, file_name_json=file_name_json)

    load_json(file_name_json)


if __name__ == '__main__':
    exit(main(parse_args()))
