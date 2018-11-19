# -*- encoding:utf-8 -*-

# Crawler

# Author: Saúl Castillo Valdés - UO251370

from __future__ import print_function
from __future__ import unicode_literals

from bs4 import BeautifulSoup
import requests
import urlparse
import time


class Crawler(object):

    urls = []
    urls_order = -1

    visited_links = set([])
    downloads = 0;

    def __init__(self, downloads=10, time=2, file=None, type=1):
        """Costructor
                Recibe las descargas máximas, el tiempo de espera,
                el path del fichero de URLs y el tipo de búsqueda
                que se va a utilizar en el crawler.
        """
        self.max_downloads = downloads
        self.wait_time = time
        self.search_type = type

        if (type == 1):
            self.search_type = False
        elif (type == 2):
            self.search_type = True

        if file is not None:
            urls_from_file = open(file)
            for line in urls_from_file:
                self.urls.append(line.split('\n')[0])

    def addNewUrl(self, link):
        """Método que añade una URL a la lista de URLs ha visitar.
        """
        self.urls.append(link)

    def visit(self, url):
        """Método que añade a la lista de URLs visitadas la URL que se pase por parametro.
        """
        self.visited_links.add(url)

    def wasVisited(self, url):
        """Método que comprueba si la URL ha sido ya visitada.
        """
        return url in self.visited_links


def crawl(crawler):

    if (crawler.max_downloads == crawler.downloads or crawler.urls.__len__() == 0):
        return

    url = crawler.urls[crawler.urls_order]  # URL de la iteración

    request = requests.get(url, headers={"User-Agent": "my_super_cool_crawler"})

    crawler.downloads += 1
    crawler.urls_order += 1

    time.sleep(crawler.wait_time)

    if "text/html" not in request.headers["Content-Type"]:
        return

    print("Crawling: {}".format(url))

    bs = BeautifulSoup(request.text, "html.parser")

    links = bs.find_all('a', href=True)
    crawler.visit(url)

    for link in links:
        link = normalize_link(url, link.get("href"))
        if link is None:
            continue
        if (crawler.wasVisited(link) == False):
            crawler.addNewUrl(link)
            if (crawler.search_type == False):
                crawl(crawler)

    if (crawler.search_type == True):
        crawl(crawler)


def normalize_link(url, link):
    """Método que filtra las URLs para que sean válidas para ejecutar el crawler.
    """
    if link.startswith("javascript:"):
        return None
    if link.startswith('/') or link.startswith('#'):
        return urlparse.urljoin(url, link)
    return link


if __name__ == '__main__':
    downloads = input("Introduce número de descargas: ")
    second = input("Introduce segundos: ")
    file = raw_input("Introduce archivo: ")
    type = input("Tipo de Búsqueda (1 -> Prof. /2 -> Anch.): ")

    crawler = Crawler(downloads, second, file, type)
    crawl(crawler)
