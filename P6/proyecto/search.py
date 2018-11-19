# -*- encoding:utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import argparse
import io
import gzip
from common import Indexer, BagOfWords

def main(args):
    indexer = Indexer()
    open_func = gzip.open if args.zip else io.open
    index_ext = ".json.gz" if args.zip else ".json"
    with open_func(args.index + index_ext) as f:
        indexer.load(f)

    with io.open(args.texts, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue
            bag = BagOfWords(line, filter_stopwords=False)
            print(">" * 80)
            print("Query:\n    {}".format(bag.text))
            print(">" * 80)
            for result, score in indexer.search(bag, args.limit):
                print("{}:\n    {}".format(score, result[0:args.show].encode("utf-8")))
            print("<" * 80)
            print("\n\n")
    return 0


def parse_args():
    parser = argparse.ArgumentParser(description='Search engine')
    parser.add_argument("texts", help="Texts file")
    parser.add_argument("index", help="Index file")
    parser.add_argument(
        "-s",
        "--show",
        type=int,
        default=-1,
        help="Show only %(default)s chars in each found line. -1 means all")
    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=5,
        help="Show only %(default)s files")
    parser.add_argument(
        "-Z",
        "--dont-zip",
        action="store_false",
        dest="zip",
        help="Don't unzip index file. Load a plain JSON file")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    exit(main(parse_args()))