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

import os
from tornado.options import options

from poweredsites.libs.importlib import import_module
from poweredsites.libs.utils import find_models

def connect():
    """Connect to databases"""
    from poweredsites.db import mongodb, mysql
    mongodb.connect()
    mysql.connect()

    # Setup date base(eg. index for the first time)
    if options.setup_db:
        mds = find_models(os.path.dirname(__file__))
        for m in mds:
            try:
                mod = import_module("." + m, package="poweredsites.db")
                setup = getattr(mod, "setup", None)
                if setup is not None:
                    setup()
            except ImportError:
                pass


class _Connection(dict):
    def __init__(self):
        self["_db"] = {"mysql":None, "mongodb":None}

    def __getattr__(self, key):
        if key in self["_db"]:
            return self["_db"][key]
        else:
            raise AttributeError

    def __setattr__(self, key, value):
        if key in self["_db"]:
            self["_db"][key] = value
        else:
            raise AttributeError

conn = _Connection()
