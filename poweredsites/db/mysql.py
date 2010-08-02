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

from tornado.database import Connection
from tornado.options import options
from tornado.ioloop import PeriodicCallback

from poweredsites.db import conn

def connect():
    conn.mysql = Connection(
        host=options.mysql["host"] + ":" + options.mysql["port"],
        database=options.mysql["database"],
        user=options.mysql["user"],
        password=options.mysql["password"])

    # ping db periodically to avoid mysql go away
    PeriodicCallback(_ping_db, int(options.mysql["recycle"]) * 1000).start()

def _ping_db():
    # Just a simple query
    conn.mysql.query("show variables")
