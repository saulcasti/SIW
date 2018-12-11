# -*- encoding:utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import argparse
import argparse
import io
import gzip
from common import Indexer, BagOfWords


def main(args):
    indexer = Indexer()

    with io.open(args.texts, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            bag = BagOfWords(line, filter_stopwords=False)
            indexer.index(bag)
    open_func = gzip.open if args.zip else io.open
    index_ext = ".json.gz" if args.zip else ".json"
    with open_func(args.index + index_ext, mode="wb") as f:
        indexer.dump(f)
    return 0


def parse_args():
    parser = argparse.ArgumentParser(description='Indexer')
    parser.add_argument("texts", help="Texts file")
    parser.add_argument("index", help="Index file")
    parser.add_argument(
        "-Z",
        "--dont-zip",
        action="store_false",
        dest="zip",
        help="Don't zip index file. Save a plain JSON file")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    exit(main(parse_args()))