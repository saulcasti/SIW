# -*- encoding:utf-8 -*-

# Estos test se ejecutan con el siguiente comando:
#    python -m unittest discover -v
# en la carpeta donde esta este fichero

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import unittest

# MODIFICAR EL NOMBRE DEL PAQUETE

from comon_v1 import Graph


class TestBagOfWords(unittest.TestCase):
    
    def test_basic(self):
        edges = [
            ["A", "B"],
            ["A", "C"],
            ["A", "F"],
            ["B", "A"],
            ["B", "C"],
            ["B", "D"],
            ["C", "F"],
            ["D", "A"],
            ["D", "C"],
            ["D", "E"],
            ["E", "A"],
            ["E", "C"],
            ["F", "C"],
            ["F", "D"],
            ["F", "E"],
        ]
        g = Graph(edges)
        # scores se espera que sea {nodo1: score1, nodo2: score2, ...}
        scores = g.page_rank(damping=0.85, limit=1.0e-8)
        sorted_nodes = [node for node, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)]
        self.assertSequenceEqual(sorted_nodes, ["F", "C", "E", "A", "D", "B"])
    
    def test_sink(self):
        edges = [
            ["A", "B"],
            ["A", "C"],
            ["A", "F"],
            ["B", "A"],
            ["B", "C"],
            ["B", "D"],
            # ["C", "F"],
            ["D", "A"],
            ["D", "C"],
            ["D", "E"],
            ["E", "A"],
            ["E", "C"],
            ["F", "C"],
            ["F", "D"],
            ["F", "E"],
        ]
        g = Graph(edges)
        # scores se espera que sea {nodo1: score1, nodo2: score2, ...}
        scores = g.page_rank(damping=0.85, limit=1.0e-8)
        sorted_nodes = [node for node, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)]
        self.assertSequenceEqual(sorted_nodes, ["C", "A", "E", "D", "B", "F"])

    def test_source(self):
        edges = [
            # ["A", "B"],
            ["A", "C"],
            ["A", "F"],
            ["B", "A"],
            ["B", "C"],
            ["B", "D"],
            ["C", "F"],
            ["D", "A"],
            ["D", "C"],
            ["D", "E"],
            ["E", "A"],
            ["E", "C"],
            ["F", "C"],
            ["F", "D"],
            ["F", "E"],
        ]
        g = Graph(edges)
        # scores se espera que sea {nodo1: score1, nodo2: score2, ...}
        scores = g.page_rank(damping=0.85, limit=1.0e-8)
        sorted_nodes = [node for node, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)]
        self.assertSequenceEqual(sorted_nodes, ["F", "C", "E", "A", "D", "B"])
    
    def test_source2(self):
        edges = [
            ["A", "B"],
            ["A", "C"],
            # ["A", "F"],
            ["B", "A"],
            ["B", "C"],
            ["B", "D"],
            # ["C", "F"],
            ["D", "A"],
            ["D", "C"],
            ["D", "E"],
            ["E", "A"],
            ["E", "C"],
            ["F", "C"],
            ["F", "D"],
            ["F", "E"],
        ]
        g = Graph(edges)
        # scores se espera que sea {nodo1: score1, nodo2: score2, ...}
        scores = g.page_rank(damping=0.85, limit=1.0e-8)
        sorted_nodes = [node for node, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)]
        self.assertSequenceEqual(sorted_nodes, ["C", "A", "B", "D", "E", "F"])
    
    def test_sink2(self):
        edges = [
            ["A", "B"],
            ["A", "C"],
            ["A", "F"],
            ["B", "A"],
            ["B", "C"],
            ["B", "D"],
            ["C", "F"],
            ["D", "A"],
            ["D", "C"],
            ["D", "E"],
            ["E", "A"],
            ["E", "C"],
            # ["F", "C"],
            # ["F", "D"],
            # ["F", "E"],
        ]
        g = Graph(edges)
        # scores se espera que sea {nodo1: score1, nodo2: score2, ...}
        scores = g.page_rank(damping=0.85, limit=1.0e-8)
        sorted_nodes = [node for node, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)]
        self.assertSequenceEqual(sorted_nodes, ["F", "C", "A", "B", "D", "E"])
    
    def test_sink3(self):
        edges = [
            ["A", "B"],
            ["A", "C"],
            ["A", "F"],
            ["B", "A"],
            ["B", "C"],
            ["B", "D"],
            ["C", "F"],
            ["D", "A"],
            ["D", "C"],
            ["D", "E"],
            # ["E", "A"],
            # ["E", "C"],
            ["F", "C"],
            ["F", "D"],
            ["F", "E"],
        ]
        g = Graph(edges)
        # scores se espera que sea {nodo1: score1, nodo2: score2, ...}
        scores = g.page_rank(damping=0.85, limit=1.0e-8)
        sorted_nodes = [node for node, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)]
        self.assertSequenceEqual(sorted_nodes, ["E", "F", "C", "D", "A", "B"])

if __name__ == '__main__':
    unittest.main()
