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
from tornado.web import HTTPError, authenticated

from poweredsites.libs.utils import url
from poweredsites.libs.handler import BaseHandler
from poweredsites.libs.decorators import cache, staff

class HelpHandler(BaseHandler):
    @cache.page(anonymous=True)
    def get(self, slug):
        entry = self.db.get("SELECT * FROM entries WHERE slug = %s", slug)
        entries = self.db.query("SELECT * FROM entries WHERE is_help = 1")
        if not entry: raise HTTPError(404)

        self._context.title = entry.title
        self._context.keywords = self._context.keywords + ",help"

        self.render("help.html", entry=entry, entries=entries)

handlers = [
            (r"/help/([a-z]{2,20})", HelpHandler),
            ]
