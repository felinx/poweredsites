# encoding=utf-8
#
# Copyright(c) 2010 poweredsites.org
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import re
import urllib

from tornado.httpclient import AsyncHTTPClient

class AlexaRankMixin(object):
    def get_alexa_rank(self, url, callback):
        """Get a web site's alexa popularity rank."""
        http = AsyncHTTPClient(max_clients=20)
        url = 'http://data.alexa.com/data?cli=10&dat=snbamz&url=%s' % urllib.quote(url)
        http.fetch(url, self.async_callback(self._alexa_callback, callback))

    def _alexa_callback(self, callback, response):
        if response.error is None:
            data = response.body
            reach_rank = re.findall("REACH RANK[^\d]*(\d+)", data)
            if reach_rank:
                reach_rank = reach_rank[0]
            else:
                reach_rank = -1
            rank = int(reach_rank)
        else:
            rank = -1

        if rank == -1:
            rank = 100000000
        callback(rank)
