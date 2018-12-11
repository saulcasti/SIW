# -*- encoding:utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import sys

reload(sys)
sys.setdefaultencoding('utf8')


import argparse
import urlparse

import operator

import nltk
from nltk.tokenize import RegexpTokenizer

from nltk.corpus import stopwords

from nltk.stem import WordNetLemmatizer

import math
import json


class BagOfWords(object):

    def __init__(self, text=None, values = None, enable_stemming=False, filter_stopwords=False):
        """Constructor
            Si recibe un string mediante el argumento text lo convierte a un
            diccionario.Si recibe un diccionario simplemente lo copia para su usointerno.
        """
        self.values ={}
        self.text =''
        if (values != None):
            self.values = values
            if(text != None):
                self.text = text
        if (text != None):
            self.text = text
            self.values = self.string_to_bag_of_words(text, enable_stemming=enable_stemming, filter_stopwords=filter_stopwords)

    @classmethod
    def from_values_dict(self, dict):
        return BagOfWords(values=dict)

    @classmethod
    def from_dict(self, dict):

            bag =  BagOfWords()
            bag.text = dict.get("text")
            bag.values=dict.get("values")
            if(bag.text ==None or bag.values == None): raise ValueError()

            return bag


    def to_dict(self):
        return {
            "text": self.text,
            "values": self.values
        }

    def string_to_bag_of_words(self, text, enable_stemming, filter_stopwords):

        bag = {}
        stopWords = set(stopwords.words('english'))
        lemmatizer = WordNetLemmatizer()

        tokenizer = RegexpTokenizer(r'\w+')
        words = tokenizer.tokenize(text)

        for word in words:
            word = word.lower()
            if ((word in stopWords) and filter_stopwords == True):
                continue
            if enable_stemming == True:
                word = lemmatizer.lemmatize(word, pos='v')
                word = lemmatizer.lemmatize(word, pos='n')
            if word in bag:
                bag[word] += 1
            else:
                bag[word] = 1
        return bag

    def __str__(self):
        """Devuelve un string con la representación del objeto. El objeto
            BagOfWords(“A b a”) está representado por el string “{‘a’: 2, ‘b’: 1}”
        """

        return str(self.values)

    def __len__(self):
        """Devuelve
            el tamaño del diccionario
        """

        return len(self.values)

    def document_len(self):
        cont = 0
        for key, value in self.values.items():
            cont += value
        return cont

    def __iter__(self):
        """Crea un iterador
            que devuelve la clave y el valor de cada elemento del diccionario
            El diccionario {‘a’: 1, ‘b’: 2} devuelve: - (‘a’, 1) en
            la primera llamada - (‘b’, 2) en la primera llamada
        """

        return self.values.iteritems()

    def intersection(self, other):
        """Intersecta 2 bag - of - words
        La intersección de “a b c a” con “a b d” es:
        {‘a’: 1, ‘b’: 1}
        """
        other_bag_of_words = other.values.copy()
        intersection_bag_of_words ={}

        for key, value in self.values.items():
            if key in intersection_bag_of_words:
                intersection_bag_of_words[key] += value
            elif (other_bag_of_words.get(key) != None):
                intersection_bag_of_words[key] = value

        return BagOfWords(values=intersection_bag_of_words)

    def union(self, other):
        """Une 2 bag - of - words
        La unión de “a b c a” con “a b d” es:
        {‘a’: 3, ‘b’: 2, ‘c’: 1, ‘d’: 1}
        """
        union_bag_of_words = other.values.copy()


        for key, value in self.values.items() :
            if key in union_bag_of_words:
                union_bag_of_words[key] += value
            else:
                union_bag_of_words[key] = value


        return BagOfWords(values=union_bag_of_words)

class Indexer(object):

    def __init__(self):
        self.docs_index = []
        self.words_index = {}
        self.text = ''

        self.index_next_word = 0

    def index (self, bag_of_words):

        doc_index = bag_of_words
        self.docs_index.append(doc_index)

        len_doc = bag_of_words.document_len()
        for key in bag_of_words.values.keys():
            tf = self.getTF(bag_of_words.values[key], len_doc=len_doc)
            if key in self.words_index:
                self.words_index[key].append([tf, self.index_next_word])
            else:
                self.words_index[key] = [[tf, self.index_next_word]]


        self.index_next_word += 1

    def score(self, text, enable_stemming, filter_stopwords):
        score = []
        bag_of_words_values = BagOfWords(text=text, enable_stemming=enable_stemming, filter_stopwords=filter_stopwords).values

        for text_key in bag_of_words_values.keys():
            if text_key in self.words_index:
                idf = self.getIDF(text_key)
                for t in self.words_index[text_key]:
                    tf = (t[0][0]) / float(t[0][1])
                    score.append([(tf*idf), t[1]])
                score.sort(reverse=True)

        return score


    def dump(self, fd):
        json_indexer = {}

        json_indexer["docs_index"] = self.doc_index_to_dict()
        json_indexer["terms_index"] = self.words_index
        return json.dump(json_indexer, fd)

    def getTF(self, value, len_doc):
        return [value, len_doc]

    def getIDF(self, text):
        idf = [len(self.words_index[text]), len(self.docs_index)]
        return  1 + math.log(idf[1] / float(idf[0]))


    def to_dict(self):
        return { "docs_index": self.doc_index_to_dict(),
                 "terms_index": self.words_index   }
    def load(self, fd):
        data = json.load(fd)
        self.words_index = data["terms_index"]

        self.docs_index = []
        for doc in data["docs_index"]:
            self.docs_index.append(BagOfWords(text=doc['text'], values=doc['values']))

    def doc_index_to_dict(self):
        aux =[]
        for doc in self.docs_index:
            aux.append({'text': doc.text, 'values': doc.values})
        return aux

    def create_vector_query(self, bag_of_words):
        """
           Método que recibe el bag of words de la query y
           devuelve un diccionario que tiene como claves las
           palabras del bag of words y de valor su tf*idf.

           El diccionario resultante tienen además un clave '##mod##',
           que tiene como valor el módulo de la query.
        :param bag_of_words: bag of words de query
        :return: diccionario descrito en el parrafo anterior
        """
        queries = {}
        mod= 0.0
        for word in bag_of_words.values:
            mul_tf_idf = 0
            if word in self.words_index:
                idf = self.getIDF(word)
                tf = self.getTF(bag_of_words.values[word], bag_of_words.document_len())
                tf_num = float(tf[0]) / tf[1]
                mul_tf_idf = idf * tf_num

            queries[word] = mul_tf_idf
            mod += math.pow(mul_tf_idf, 2)


        queries['##mod##'] = math.sqrt(mod)
        return queries


    def create_vector__documentX(self,bag_of_words):
        """
            Método que dado el bag of words de la query
            devuelve un diccionario cuyas claves serán las
            palabras de la query y cuyo valor será una lista con
            los valores score para cada documento.
        :param bag_of_words: bag of words de query
        :return: diccionario descrito en el parrafo anterior
        """
        docs = {}

        for word in bag_of_words.values:
            docs[word] = []
            i = 0
            while (i < len(self.docs_index)):
                docs[word].append(0)
                i += 1

            score = self.score(word,enable_stemming=False, filter_stopwords=False)
            for s in score:
                if s[1] not in docs:
                    docs[s[1]] = []
                docs[word][s[1]] = s[0]
        return docs

    def dot_product(self, vector_documents, vector_query):
        """
           Método que dado el vector de documentos y el de query,
           devulve un diccionario cuyas claves serán el índice del
           documento en self.docs_index y cuyo valor será el dot product,
           siguiendo la formula aquí disponible:
            https://janav.wordpress.com/2013/10/27/tf-idf-and-cosine-similarity/

        :param vector_documents: vector de documentos
        :param vector_query: vector de query
        :return: diccionario descrito en el parrafo anterior
        """
        result = {}
        for word in vector_documents:
            for doc, score in enumerate(vector_documents[word]):
                if doc not in result:
                    result[doc]=0
                result[doc] += score*vector_query[word]
        return result

    def mod_documentx(self, vector_documents):
        """
            Método que dado el vector de documentos, devuelve
            un diccionario con clave índice del documento y valor
            modulo del vector de scores para cada palabra de la query.
        :param vector_documents: vector de documentos
        :return:diccionario descrito en el parrafo anterior
        """
        result = {}
        for word in vector_documents:
            for doc, score in enumerate(vector_documents[word]):
                if doc not in result:
                    result[doc] = 0
                result[doc] += math.pow(score, 2)

        for key in result.keys():
            result[key] = math.sqrt(result[key])

        return result

    def cosine_similarity(self, dot_prod, mod_query, mod_docx):
        """
            Método que dado todos los parametros necesarios para calcular
            la similitud coseno, devuelve una lista de:
                ["texto del documento", sim_cose]
            Todo se ha hecho de acuerdo a lo mostrado en el paper:
                https://janav.wordpress.com/2013/10/27/tf-idf-and-cosine-similarity/

        :param dot_prod:
        :param mod_query:
        :param mod_docx:
        :return:
        """
        result=[]
        for key in dot_prod.keys():
            if dot_prod[key] >0:
                cos_sim = dot_prod[key]/(mod_docx[key]*mod_query)
                result.append([self.docs_index[key].text, cos_sim])

        result = sorted(sorted(result, key=lambda x: x[0], reverse=True), key=lambda x: x[1], reverse=True)

        return result

    def search(self, bag_of_words, number):

        vector_documents = self.create_vector__documentX(bag_of_words)
        vector_query = self.create_vector_query(bag_of_words)

        dot_prod = self.dot_product(vector_documents, vector_query) #Diccionario
        mod_query = vector_query['##mod##'] #Número
        mod_docx = self.mod_documentx(vector_documents) #Diccionario

        cos_similarity = self.cosine_similarity(
                dot_prod=dot_prod,
                mod_query=mod_query,
                mod_docx=mod_docx)

        if len(cos_similarity)> number:
            return cos_similarity[:number]

        return cos_similarity






def read_cran(text, query, limit):
    """
        Método que busca las queries del fichero 'query' (pasado por parámetro), en el fichero 'text' (pasado por parámetro).
        Solo se buscarán las queries dentro del limite indicado por el parámetro 'limit'.
    """
    texts = open(text).readlines()
    queries = open(query).readlines()

    indexer = Indexer()
    for text in texts:
        text = text.strip()
        bag = BagOfWords(
            text, enable_stemming=False, filter_stopwords=False)
        indexer.index(bag)

    for q in queries[:limit]:
        print('\n')
        print("> Query: {}".format(q.encode('utf-8')))
        q = q.strip()
        bag = BagOfWords(q, enable_stemming=False, filter_stopwords=False)
        results = indexer.search(bag, 10)
        print("> Results:")
        for idx, val in enumerate(results):
            print('\t>> {} [{}] >>> {}'.format(idx +1 , round(val[1],4), val[0]))
        print('\n')



def main(args):
    read_cran(args.texts, args.queries, args.limit)


def parse_args():
    parser = argparse.ArgumentParser(description='searchQueryText')
    parser.add_argument("texts", help="Texts file")
    parser.add_argument("queries", help="Queries file")
    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=5,
        help="Use %(default)s queries")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    exit(main(parse_args()))
