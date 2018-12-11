# -*- encoding:utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals


import sys

import copy
import argparse
import math
import numpy




class Graph(object):

    def __init__(self, edges = None):
        self.nodes_sum = []
        if(edges!=None):
            self.edges = edges
            self.nodes_pos = self.get_pos()
            self.matrix_edges = self.get_matrix()


    def page_rank(self, damping=0.85, limit=1.0e-8):
        """
        Método que llama a diferentes métodos para poder conocer los scores de cada nodo.
        Para ello se obtendrá por parametro del damping y del límite del error cuadrático,
        devolviendo un diccionario con cada uno de los scores asignado al identificativo de cada nodo.
        :param damping:
        :param limit:
        :return:
        """
        matrix_edges_mul_damping = self.matrix_edges * damping # Multiplicamos la matriz por el damping
        matrix_damping = self.inic_matrix_damping(damping= damping) # Inicializamos la matriz damping

        sum_matrix = matrix_damping + matrix_edges_mul_damping

        sX = self.get_scores(sum_matrix=sum_matrix, limit=limit)

        result ={}
        for node in self.nodes_pos.keys():
            result[node] = sX[self.nodes_pos[node]]
        return result


    def get_scores(self, sum_matrix, limit):
        """
        Método auxiliar que dada la matriz suma y el límite del error cuadrático,
        devuelve el score de cada uno de los nodos en una matriz columna numpy.
        :param sum_matrix:
        :param limit:
        :return:
        """
        sX = self.get_S0()  # S0

        while True:
            error = 0
            sX_b = copy.deepcopy(sX)  # Anterior S
            sX = sum_matrix * copy.deepcopy(sX_b)  # Nueva S

            index = 0
            while index < len(sX_b):
                error += math.pow(float(sX[index] - sX_b[index]), 2)
                index += 1

            error = error / float(len(self.nodes_pos))
            if (error < limit): break

        return sX

    def get_S0(self):
        """
        Método que genera una columna
        :return:
        """
        column = self.get_empty_row()
        index = 0
        while index < len(column):
            column[index] = []
            column[index].append(1.0/len(self.nodes_pos))
            index += 1

        column_numpy = numpy.matrix(column)
        return column_numpy

    def get_pos(self):
        """
        Método que deveulve los nodos que tiene el grafo con un valor
        númerico relativo al orden que llevan.
        :return:
        """
        nodes = {}
        position = 0
        for edge in self.edges:
            if edge[0] not in nodes:
                nodes[edge[0]] = position
                position += 1
            if edge[1] not in nodes:
                nodes[edge[1]] = position
                position += 1

        return nodes


    def get_matrix(self):
        """
        Método para obtener la matriz de las relaciones entre nodos según el atributo "edges"
        :return: matriz en formato numpy
        """
        matrix= self.inic_matrix()
        nodes_edges = self.get_nodes_num_edges()
        nodes = self.nodes_pos


        for node_key in nodes.keys():
            row = self.get_empty_row()
            for edge in self.edges:
                if edge[1] == node_key:
                    row[self.nodes_pos[edge[0]]] = 1.0/nodes_edges[edge[0]]

            if node_key in self.nodes_sum:
                row[self.nodes_pos[node_key]] = 1.0 / nodes_edges[node_key]

            matrix[nodes[node_key]] = row

        numpy_matrix = numpy.matrix(matrix)
        return numpy_matrix

    def get_nodes_num_edges(self):
        """
        Método con el que se obtiene un diccionario con el número de nodos a
        los que el nodo va.

        La intención del segundo bucle for es la de hallar los nodos sumideros,
        pudiendo así solucionar problemas futuros.
        :return:
        """
        nodes = {}
        for edge in self.edges:
            if edge[0] not in nodes:
                nodes[edge[0]] = 1
            else:
                nodes[edge[0]] = nodes[edge[0]] + 1

        if len(nodes) != len(self.nodes_pos):
            for node in self.nodes_pos.keys():
                if node not in nodes:
                    self.nodes_sum.append(node)
                    nodes[node] = 1
        return nodes

    def get_empty_row(self):
        """
        Método auxiliar que crea una lista de 0 con tantos valores como nodos tenga
        el grafo, siempre ordenado como se indique en
        :return: array de 0 con un tamaño igual al número de nodos
        """
        row = []
        for node_key in self.nodes_pos:
            row.append(0)
        return row

    def inic_matrix(self):
        """
        Método auxiliar que crea una lista de listas, simulando la matriz.
        Cada lista dentro de esta lista representa una columna de la matriz.
        :return: array de arrays con un tamaño igual al número de nodos
        """
        matrix = []
        for node_key in self.nodes_pos:
            matrix.append([])
        return matrix





    def inic_matrix_damping(self, damping):
        """
        Método que crea la matriz damping.
        :param damping:
        :return:
        """
        matrix = self.inic_matrix()
        index = 0
        while index < len(matrix):
            matrix[index] = self.get_empty_row()
            i = 0
            while i < len(matrix[index]):
                matrix[index][i] = float(1.0 - damping)/len(self.nodes_pos)
                i += 1
            index += 1

        numpy_matrix = numpy.matrix(matrix)
        return numpy_matrix



def main():

    pass

if __name__ == '__main__':
    exit(main())
