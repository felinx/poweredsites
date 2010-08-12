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

from tornado.web import UIModule

from poweredsites.libs.handler import BaseHandler
from poweredsites.libs.decorators import cache
from poweredsites.libs.pagination import PaginationMixin


class FrontSearchHandler(BaseHandler):
    def get(self):
        self._context.title = "Search"
        self.render("search.html")


class FrontFeedsHandler(BaseHandler):
    @cache.page(condition="select count(*) from site")
    def get(self):
        entries = self.db.query("SELECT * FROM site order by id DESC LIMIT 40")
        self.set_header("Content-Type", "application/atom+xml")
        self.render("feed.xml", entries=entries, title="Powered Sites")


class FrontIndexHandler(BaseHandler):
    _order_by = "id DESC"
    _condition = ""
    _handler_template = "index.html"
    _ws_count_query = "select count(*) as c from site"
    _context_title = "Latest sites"

    @cache.page(3600, condition="select count(*) from site")
    def get(self):
        self._context.ws_count_query = self._ws_count_query
        self._context.ws_query = "select site.*, user.username, user.openid_name "\
                "from site, user where site.user_id = user.id %s order by %s" % \
                (self._condition, self._order_by)
        self._context.ws_query = str(self._context.ws_query)
        self._context.page = self.get_argument("page", 1)

        self._context.title = self._context_title
        self.render(self._handler_template)


class FrontTopHandler(FrontIndexHandler):
    _order_by = "click DESC, pr DESC, ar ASC"
    _handler_template = "top.html"
    _context_title = "Top sites"


class FrontOpensourceHandler(FrontIndexHandler):
    _order_by = "click DESC, pr DESC, ar ASC"
    _condition = "and site.source_url is not NULL"
    _ws_count_query = "select count(*) as c from site where source_url is not NULL"
    _handler_template = "opensource.html"
    _context_title = "Open source sites"


class WebsitesModule(UIModule, PaginationMixin):
    def render(self, count_query, query, page):
        pagination = self.get_pagination(count_query, query, page)

        return self.render_string("modules/websites.html", pagination=pagination)


class WebsitesIndexModule(UIModule):
    _module_template = "modules/websites_index.html"
    @cache.cache(condition="select count(*) from site")
    def render(self, count_query, query, page):
        return self.render_string(self._module_template,
                            count_query=count_query, query=query, page=page)


class WebsitesTopModule(WebsitesIndexModule):
    _module_template = "modules/websites_top.html"


class WebsitesOpensourceModule(WebsitesIndexModule):
    _module_template = "modules/websites_opensource.html"


handlers = [
            (r"/?", FrontIndexHandler),
            (r"/top", FrontTopHandler),
            (r"/opensource", FrontOpensourceHandler),
            (r"/search", FrontSearchHandler),
            (r"/feeds", FrontFeedsHandler),
            ]

ui_modules = {"websites":WebsitesModule,
              "websites_index":WebsitesIndexModule,
              "websites_top":WebsitesTopModule,
              "websites_opensource":WebsitesOpensourceModule,
              }
