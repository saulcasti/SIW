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
from indexer_v1 import BagOfWords, Indexer


class TestBagOfWords(unittest.TestCase):
    def test_init_with_str(self):
        """Prueba la inicialización con strings
        """
        self.assertDictEqual(
            BagOfWords("cat dog cow").values, {
                "cat": 1,
                "dog": 1,
                "cow": 1
            })
        self.assertDictEqual(
            BagOfWords(text="Cat dog cat").values, {
                "cat": 2,
                "dog": 1
            })

    def test_init_with_dict(self):
        """Prueba la inicialización con diccinoarios
        """
        self.assertDictEqual(
            BagOfWords(values={
                "cat": 1,
                "dog": 1,
                "cow": 1
            }).values, {
                "cat": 1,
                "dog": 1,
                "cow": 1
            })
        self.assertDictEqual(
            BagOfWords(values={
                "cat": 2,
                "dog": 1
            }).values, {
                "cat": 2,
                "dog": 1
            })

    def test_init_with_symbols_in_str(self):
        """Prueba la inicialización con strings que contengan símbolos de puntuación
        """
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
        """Prueba la conversión a string
        """
        txt = str(BagOfWords("cat dog cow"))
        self.assertTrue(txt.startswith("{"))
        self.assertIn("'cat': 1", txt)
        self.assertIn("'dog': 1", txt)
        self.assertIn("'cow': 1", txt)
        self.assertTrue(txt.endswith("}"))

    def test_len(self):
        """Prueba el tamaño del vector
        """
        self.assertEqual(len(BagOfWords()), 0)
        self.assertEqual(len(BagOfWords("cat dog cow")), 3)
        self.assertEqual(len(BagOfWords(text="cat dog cat")), 2)

    def test_iter(self):
        """Prueba el iterador
        """
        self.assertSequenceEqual(sorted(iter(BagOfWords())), [])
        self.assertSequenceEqual(
            sorted(iter(BagOfWords("cat cow dog"))), [("cat", 1), ("cow", 1),
                                                      ("dog", 1)])
        self.assertSequenceEqual(
            sorted(iter(BagOfWords(text="cat dog cat"))), [("cat", 2),
                                                           ("dog", 1)])

    def test_intersection(self):
        """Prueba la interesección de dos bag-of-words
        """
        bag1 = BagOfWords("cat dog cow fish cat cat fish")
        bag2 = BagOfWords("dog grape banana peach")
        self.assertDictEqual(bag1.intersection(bag2).values, {"dog": 1})

    def test_union(self):
        """Prueba la union de dos bag-of-words
        """
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
        """Prueba el tamaño del documento, no del vector
        """
        bag1 = BagOfWords("cat dog cow fish cat cat fish")
        bag2 = BagOfWords("dog grape banana peach")
        self.assertEqual(bag1.document_len(), 7)
        self.assertEqual(bag2.document_len(), 4)
        self.assertEqual(bag1.intersection(bag2).document_len(), 1)
        self.assertEqual(bag1.union(bag2).document_len(), 11)


class TestIndexer(unittest.TestCase):
    """
    Esta prueba usa el siguiente ejemplo como modelo
    https://en.wikipedia.org/wiki/Tf%E2%80%93idf#Example_of_tf%E2%80%93idf
    """

    texts = [
        "this is a a sample",
        "this is another another example example example"
    ]

    expected = {
        "docs_index": [{
            "a": 2,
            "is": 1,
            "sample": 1,
            "this": 1
        }, {
            "another": 2,
            "example": 3,
            "is": 1,
            "this": 1
        }],
        "words_index": {
            "a": [[[2, 5], 0]],
            "another": [[[2, 7], 1]],
            "example": [[[3, 7], 1]],
            "is": [[[1, 5], 0], [[1, 7], 1]],
            "sample": [[[1, 5], 0]],
            "this": [[[1, 5], 0], [[1, 7], 1]]
        }
    }

    def test_index_creation(self):
        """Prueba la creación del indice

        Esta prueba usa el siguiente ejemplo como modelo
        https://en.wikipedia.org/wiki/Tf%E2%80%93idf#Example_of_tf%E2%80%93idf
        """

        self.maxDiff = None
        
        indexer = Indexer()
        for text in self.texts:
            text = text.strip()
            bag = BagOfWords(text, enable_stemming=False, filter_stopwords=False)
            indexer.index(bag)
        
        self.assertSequenceEqual(self.expected["docs_index"], indexer.docs_index)
        self.assertDictEqual(self.expected["words_index"], indexer.words_index)

    def test_score(self):
        """Prueba los scores de una palabra para cada documento

        Esta prueba usa el siguiente ejemplo como modelo
        https://en.wikipedia.org/wiki/Tf%E2%80%93idf#Example_of_tf%E2%80%93idf
        """
        indexer = Indexer()
        for text in self.texts:
            text = text.strip()
            bag = BagOfWords(text, enable_stemming=False, filter_stopwords=False)
            indexer.index(bag)

        # Tests the score of "example"
        scores = sorted(indexer.score("example", enable_stemming=False, filter_stopwords=False), reverse=True)
        self.assertAlmostEqual(scores[0][0], 0.129, places=3)
        self.assertEqual(scores[0][1], 1)

        # Tests the score of "this"
        scores = sorted(indexer.score("this", enable_stemming=False, filter_stopwords=False), reverse=True)
        self.assertAlmostEqual(scores[0][0], 0, places=3)
        self.assertEqual(scores[0][1], 1)
        self.assertAlmostEqual(scores[1][0], 0, places=3)
        self.assertEqual(scores[1][1], 0)

        # Tests the score of "sample"
        scores = sorted(indexer.score("sample", enable_stemming=False, filter_stopwords=False), reverse=True)
        self.assertAlmostEqual(scores[0][0], 0.060, places=3)
        self.assertEqual(scores[0][1], 0)
    
    def test_dump(self):
        """Prueba que el fichero JSON generado sea correcto
        """
        indexer = Indexer()
        for text in self.texts:
            text = text.strip()
            bag = BagOfWords(text, enable_stemming=False, filter_stopwords=False)
            indexer.index(bag)
        fd = StringIO()
        indexer.dump(fd)
        fd.seek(0)
        got = json.load(fd)

        self.assertSequenceEqual(self.expected["docs_index"], got["docs_index"])
        self.assertDictEqual(self.expected["words_index"], got["words_index"])


if __name__ == '__main__':
    unittest.main()
