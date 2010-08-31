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

from tornado.options import options
from tornado.web import HTTPError
from webhelpers.paginate import Page
from webhelpers.util import update_params

class PaginationMixin(object):
    def get_pagination(self, count_query, query, page, page_size=options.page_size, *args):
        try:
            try:
                page = int(page)
                page_size = int(page_size)
            except ValueError:
                page = 1
                page_size = 20

            if page < 1:
                page = 1

            start = (page - 1) * page_size

            if getattr(self, "db", None) is None:
                # UI Module
                self.db = self.handler.db

            # should add a c(count) alias in the count query
            count = self.db.get(count_query)
            count = int(count.c) if count else 0
            if start > count:
                page = (count % page_size)
                start = (page - 1) * page_size

            start = max(0, start)

            pagination = Page(None, page=page, items_per_page=page_size, item_count=count, url=self.get_page_url)
            pages = pagination.pager('$link_previous ~3~ $link_next (Page $page of $page_count)')
            rows = self.db.query(query + str(" limit %s, %s" % (start, page_size)), *args)

            return {"pages":pages, "rows":rows}
        except TypeError:
            raise HTTPError(404)

    def get_page_url(self, **kw):
        return update_params(self.request.full_url(), **kw)
