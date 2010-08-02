# -*- coding: utf-8 -*-
#
#  Modify original one to use tornado's asynchronous feature (felinx)
#
#  Script for getting Google Page Rank of page
#  Google Toolbar 3.0.x/4.0.x Pagerank Checksum Algorithm
#
#  original from http://pagerank.gamesaga.net/
#  this version was adapted from http://www.djangosnippets.org/snippets/221/
#  by Corey Goldberg - 2010
#
#  Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php

import urllib

from tornado.httpclient import AsyncHTTPClient

class PageRankMinxin(object):
    def get_pagerank(self, url, callback):
        """Get a web site's page rank."""
        http = AsyncHTTPClient(max_clients=20)
        hash = check_hash(hash_url(url))
        url = 'http://www.google.com/search?client=navclient-auto&features=Rank:&q=info:%s&ch=%s' \
                    % (urllib.quote(url), hash)
        http.fetch(url, self.async_callback(self._pagerank_callback, callback))

    def _pagerank_callback(self, callback, response):
        if response.error is None:
            data = response.body
            try:
                rank = data.strip()[9:]
                if rank == '':
                    rank = 0
                else:
                    rank = int(rank)
            except:
                rank = None
        else:
            rank = None

        callback(rank)

def int_str(string, integer, factor):
    for i in range(len(string)) :
        integer *= factor
        integer &= 0xFFFFFFFF
        integer += ord(string[i])
    return integer


def hash_url(string):
    c1 = int_str(string, 0x1505, 0x21)
    c2 = int_str(string, 0, 0x1003F)

    c1 >>= 2
    c1 = ((c1 >> 4) & 0x3FFFFC0) | (c1 & 0x3F)
    c1 = ((c1 >> 4) & 0x3FFC00) | (c1 & 0x3FF)
    c1 = ((c1 >> 4) & 0x3C000) | (c1 & 0x3FFF)

    t1 = (c1 & 0x3C0) << 4
    t1 |= c1 & 0x3C
    t1 = (t1 << 2) | (c2 & 0xF0F)

    t2 = (c1 & 0xFFFFC000) << 4
    t2 |= c1 & 0x3C00
    t2 = (t2 << 0xA) | (c2 & 0xF0F0000)

    return (t1 | t2)


def check_hash(hash_int):
    hash_str = '%u' % (hash_int)
    flag = 0
    check_byte = 0

    i = len(hash_str) - 1
    while i >= 0:
        byte = int(hash_str[i])
        if 1 == (flag % 2):
            byte *= 2;
            byte = byte / 10 + byte % 10
        check_byte += byte
        flag += 1
        i -= 1

    check_byte %= 10
    if 0 != check_byte:
        check_byte = 10 - check_byte
        if 1 == flag % 2:
            if 1 == check_byte % 2:
                check_byte += 9
            check_byte >>= 1

    return '7' + str(check_byte) + hash_str
