# -*- encoding:utf-8 -*-

#Crawler with robots.txt support and different searching algorithms

from __future__ import print_function
from __future__ import unicode_literals

from bs4 import BeautifulSoup
import requests
import argparse
import urlparse
import time
import robotparser

class Crawler(object):

    urls = []
    urls_order = 0
    max_downloads = 10
    wait_time = 0

    visited_links = set([])
    downloads = 0;

    def __init__(self, downloads=10, time=2, file = None):
        self.max_downloads = downloads
        self.wait_time = time

        if file is not None:
            urls_from_file = open(file)
            for line in urls_from_file:
                self.urls.append(line.split('\n')[0])



    def addNewUrl(self, link):
        self.urls.append(link)
        self.urls_order += 1
        #print(self.urls)

    def visit(self, url):
        self.visited_links.add(url)

    def wasVisited(self, url):
        return url in self.visited_links


def crawl(crawler):

    if (crawler.max_downloads == crawler.downloads or crawler.urls.__len__() == 0):
        return

    url = crawler.urls[crawler.urls_order] ## URL de la iteración

    request = requests.get(url, headers={"User-Agent": "my_super_cool_crawler"})

    crawler.downloads +=1;

    time.sleep(crawler.wait_time)

    if "text/html" not in request.headers["Content-Type"]:
        return

    print("Crawling: {}".format(url))

    bs = BeautifulSoup(request.text, "html.parser")

    links = bs.find_all('a', href=True)


    crawler.visit(url) ## Añadimos a visitados a la url actual

    for link in links:

        link = normalize_link(url, link.get("href"))

        if link is None:
            continue
        if (crawler.wasVisited(link) == False):
            crawler.addNewUrl(link) ## Añadimos una URL al la lista

    crawl(crawler)



def normalize_link(url, link):
    if link.startswith("javascript:"):
        return None
    if link.startswith('/') or link.startswith('#'):
        return urlparse.urljoin(url,link)
    return link

if __name__ == '__main__':

    crawler = Crawler(11, 2,'urls.txt')
    crawl(crawler)
