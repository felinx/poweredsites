# -*- coding: utf-8 -*-
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

from datetime import datetime
from tornado.options import options
from pymongo import ASCENDING, DESCENDING

from poweredsites.db.mongodb import MongodbModel
from poweredsites.db import conn

_collection = "access"

class Access(MongodbModel):
    accesses = []

    def collection(self):
        return _collection

    def attributes(self):
        return ["username", "host", "path", "full_url",
                "status_code", "ip", "lang", "agent", "referer",
                "duration", "date"
                ]

    def logging_access(self, handler):
        now = datetime.now()
        request = handler.request
        user = handler.current_user

        if user is not None:
            username = user.username
        else:
            username = None

        self.username = username
        self.host = request.host
        self.path = request.path
        self.full_url = request.full_url()
        self.status_code = handler._status_code
        self.ip = request.remote_ip
        self.lang = request.headers.get("Accept-Language", "en-us,en;q=0.5")
        self.agent = request.headers.get("User-Agent", "Unknown-Agent")
        self.referer = request.headers.get("Referer", None)
        self.duration = 1000.0 * request.request_time() # millisecond
        self.date = now

        self.accesses.append(self.record())

def logging_access_job():
    if len(Access.accesses) > options.access_log["valve"]:
        co = getattr(conn.mongodb, _collection)
        co.insert(Access.accesses)
        Access.accesses = []

def setup():
    co = getattr(conn.mongodb, _collection)
    co.ensure_index("full_url")
    co.ensure_index("referer")
    co.ensure_index([("date", DESCENDING), ("duration", DESCENDING)])
