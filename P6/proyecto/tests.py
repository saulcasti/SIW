# -*- encoding:utf-8 -*-

# Estos test se ejecutan con el siguiente comando:
#    python -m unittest discover -v
# en la carpeta donde esta este fichero

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import unittest
from StringIO import StringIO
import json

# MODIFICAR EL NOMBRE DEL PAQUETE
from common import BagOfWords, Indexer


class TestBagOfWords(unittest.TestCase):
    def test_init(self):
        self.assertDictEqual(
            BagOfWords("cat dog cow").values, {
                "cat": 1,
                "dog": 1,
                "cow": 1
            })
        self.assertDictEqual(
            BagOfWords("Cat dog cat").values, {
                "cat": 2,
                "dog": 1
            })

    def test_from_values_dict(self):
        self.assertDictEqual(
            BagOfWords.from_values_dict({
                "cat": 1,
                "dog": 1,
                "cow": 1
            }).values, {
                "cat": 1,
                "dog": 1,
                "cow": 1
            })
        self.assertDictEqual(
            BagOfWords.from_values_dict({
                "cat": 2,
                "dog": 1
            }).values, {
                "cat": 2,
                "dog": 1
            })

    def test_from_dict(self):
        bag = BagOfWords.from_dict({
            "text": "cat dog cow",
            "values": {
                "cat": 1,
                "dog": 1,
                "cow": 1
            }
        })
        self.assertEqual(bag.text, "cat dog cow")
        self.assertDictEqual(bag.values, {"cat": 1, "dog": 1, "cow": 1})
        with self.assertRaises(ValueError):
            BagOfWords.from_dict({})
        with self.assertRaises(ValueError):
            BagOfWords.from_dict({"text": "blablabla"})
        with self.assertRaises(ValueError):
            BagOfWords.from_dict({"values": {"a": 1, "b": 1}})

    def test_init_with_symbols_in_str(self):
        self.assertDictEqual(
            BagOfWords(" cat, dog! cow.").values, {
                "cat": 1,
                "dog": 1,
                "cow": 1
            })
        self.assertDictEqual(
            BagOfWords(text="cat dog?? cat!!! ").values, {
                "cat": 2,
                "dog": 1
            })

    def test_str(self):
        txt = str(BagOfWords("cat dog cow"))
        self.assertTrue(txt.startswith("{"))
        self.assertIn("'cat': 1", txt)
        self.assertIn("'dog': 1", txt)
        self.assertIn("'cow': 1", txt)
        self.assertTrue(txt.endswith("}"))

    def test_len(self):
        self.assertEqual(len(BagOfWords("")), 0)
        self.assertEqual(len(BagOfWords("cat dog cow")), 3)
        self.assertEqual(len(BagOfWords(text="cat dog cat")), 2)

    def test_iter(self):
        self.assertSequenceEqual(sorted(iter(BagOfWords(""))), [])
        self.assertSequenceEqual(
            sorted(iter(BagOfWords("cat cow dog"))), [("cat", 1), ("cow", 1),
                                                      ("dog", 1)])
        self.assertSequenceEqual(
            sorted(iter(BagOfWords(text="cat dog cat"))), [("cat", 2),
                                                           ("dog", 1)])

    def test_intersection(self):
        bag1 = BagOfWords("cat dog cow fish cat cat fish")
        bag2 = BagOfWords("dog grape banana peach")
        self.assertDictEqual(bag1.intersection(bag2).values, {"dog": 1})

    def test_union(self):
        bag1 = BagOfWords("cat dog cow fish cat cat fish")
        bag2 = BagOfWords("dog grape banana peach")
        self.assertDictEqual(
            bag1.union(bag2).values, {
                "banana": 1,
                "cat": 3,
                "cow": 1,
                "dog": 2,
                "fish": 2,
                "grape": 1,
                "peach": 1
            })

    def test_document_len(self):
        bag1 = BagOfWords("cat dog cow fish cat cat fish")
        bag2 = BagOfWords("dog grape banana peach")
        self.assertEqual(bag1.document_len(), 7)
        self.assertEqual(bag2.document_len(), 4)
        self.assertEqual(bag1.intersection(bag2).document_len(), 1)
        self.assertEqual(bag1.union(bag2).document_len(), 11)

    def test_to_dict(self):
        self.assertDictEqual(
            BagOfWords(" cat, dog! cow.").to_dict(), {
                "text": " cat, dog! cow.",
                "values": {
                    "cat": 1,
                    "dog": 1,
                    "cow": 1
                }
            })


class TestIndexer(unittest.TestCase):
    """
    Esta prueba usa el siguiente ejemplo como modelo
    https://en.wikipedia.org/wiki/Tf%E2%80%93idf#Example_of_tf%E2%80%93idf
    """

    texts = [
        "this is a a sample", "this is another another example example example"
    ]

    expected = {
        "docs_index": [{
            "text": "this is a a sample",
            "values": {
                "a": 2,
                "is": 1,
                "sample": 1,
                "this": 1
            }
        },
                       {
                           "text":
                           "this is another another example example example",
                           "values": {
                               "another": 2,
                               "example": 3,
                               "is": 1,
                               "this": 1
                           }
                       }],
        "terms_index": {
            "a": [[[2, 5], 0]],
            "another": [[[2, 7], 1]],
            "example": [[[3, 7], 1]],
            "is": [[[1, 5], 0], [[1, 7], 1]],
            "sample": [[[1, 5], 0]],
            "this": [[[1, 5], 0], [[1, 7], 1]]
        }
    }

    def test_index_creation(self):
        self.maxDiff = None

        indexer = Indexer()
        for text in self.texts:
            text = text.strip()
            bag = BagOfWords(
                text, enable_stemming=False, filter_stopwords=False)
            indexer.index(bag)
        got = indexer.to_dict()

        self.assertSequenceEqual(self.expected["docs_index"],
                                 got["docs_index"])
        self.assertDictEqual(self.expected["terms_index"], got["terms_index"])

    def test_dump(self):
        indexer = Indexer()
        for text in self.texts:
            text = text.strip()
            bag = BagOfWords(
                text, enable_stemming=False, filter_stopwords=False)
            indexer.index(bag)
        fd = StringIO()
        indexer.dump(fd)
        fd.seek(0)
        got = json.load(fd)

        self.assertSequenceEqual(self.expected["docs_index"],
                                 got["docs_index"])
        self.assertDictEqual(self.expected["terms_index"], got["terms_index"])

    def test_load(self):
        indexer = Indexer()
        fd = StringIO()
        json.dump(self.expected, fd)
        fd.seek(0)
        indexer.load(fd)
        got = indexer.to_dict()

        self.assertSequenceEqual(self.expected["docs_index"],
                                 got["docs_index"])
        self.assertDictEqual(self.expected["terms_index"], got["terms_index"])


class TestSearch(unittest.TestCase):
    """
    Esta prueba usa el siguiente ejemplo como modelo
    https://janav.wordpress.com/2013/10/27/tf-idf-and-cosine-similarity/
    """

    texts = [
        "The game of life is a game of everlasting learning",
        "The unexamined life is not worth living",
        "Never stop learning"
    ]
    indexer = None

    def setUp(self):
        self.indexer = Indexer()
        for text in self.texts:
            text = text.strip()
            bag = BagOfWords(
                text, enable_stemming=False, filter_stopwords=False)
            self.indexer.index(bag)
    
    def test_search_1(self):
        bag = BagOfWords("life learning", enable_stemming=False, filter_stopwords=False)
        results = list(self.indexer.search(bag, 10))

        self.assertEqual(len(results), 3)
        result0,  _ = results[0]
        self.assertEqual(result0, self.texts[0])
        result1,  _ = results[1]
        self.assertEqual(result1, self.texts[1])
        result2,  _ = results[2]
        self.assertEqual(result2, self.texts[2])
    
    def test_search_2(self):
        bag = BagOfWords("learning", enable_stemming=False, filter_stopwords=False)
        results = list(self.indexer.search(bag, 10))

        self.assertEqual(len(results), 2)
        result0,  _ = results[0]
        self.assertEqual(result0, self.texts[0])
        result1,  _ = results[1]
        self.assertEqual(result1, self.texts[2])

    def test_search_3(self):
        bag = BagOfWords("ñu life", enable_stemming=False, filter_stopwords=False)
        results = list(self.indexer.search(bag, 10))

        self.assertEqual(len(results), 2)
        result0,  _ = results[0]
        self.assertEqual(result0, self.texts[0])
        result1,  _ = results[1]
        self.assertEqual(result1, self.texts[1])
    
    def test_search_4(self):
        bag = BagOfWords("life ñu", enable_stemming=False, filter_stopwords=False)
        results = list(self.indexer.search(bag, 10))

        self.assertEqual(len(results), 2)
        result0,  _ = results[0]
        self.assertEqual(result0, self.texts[0])
        result1,  _ = results[1]
        self.assertEqual(result1, self.texts[1])
    
    def test_search_5(self):
        bag = BagOfWords("foo bar", enable_stemming=False, filter_stopwords=False)
        results = list(self.indexer.search(bag, 10))

        self.assertEqual(len(results), 0)


if __name__ == '__main__':
    unittest.main()
