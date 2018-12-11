# -*- encoding:utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import argparse
import io
from comon_v1 import Graph

def main(args):
    with io.open(args.file) as f:
        edges = list(parse_graph(f))
    g = Graph(edges)
    scores = g.page_rank()
    print(">" * 80)
    for node, score in  sorted(scores.items(), key=lambda x: x[1], reverse=True):
        print("{} ({})".format(node, score))
    print("<" * 80)


def parse_graph(f):
    for line in f:
        line = line.strip()
        if not line:
            continue
        src, dst = line.split(",")
        src = src.strip()
        dst = dst.strip()
        yield src, dst


def parse_args():
    parser = argparse.ArgumentParser(description='Search engine')
    parser.add_argument("file", help="Graph file")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    exit(main(parse_args()))