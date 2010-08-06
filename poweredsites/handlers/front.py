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

from tornado import escape

from poweredsites.libs.handler import BaseHandler
from poweredsites.libs.decorators import cache
from poweredsites.libs import const

class FrontMainHandler(BaseHandler):
    _category_top_query = "select * from ("\
                "(select count(site_id) as c, project_id from project_sites "\
                "group by project_id) as ps "\
                "left join (select id, subdomain, category_id from project) "\
                "as p on ps.project_id = p.id) where p.category_id=%s order by ps.c DESC limit 0, 5"
    _category_count_query = "select sum(ps.c) as c from (select count(site_id) as c, project_id from "\
                "project_sites group by project_id) as ps "\
                "left join (select id, category_id from project) as p on ps.project_id = p.id "\
                "where p.category_id = %s"

    @cache.page()
    def get(self):

        top_projects = self.db.query("select * from ("
                "(select count(site_id) as c, project_id from project_sites "
                "group by project_id order by c DESC limit 0, 10) as ps "
                "left join (select id, subdomain from project) as p on ps.project_id = p.id)")
        top_projects_count = self._get_count("select count(*) as c from project_sites")

        top_frameworks = self.db.query(self._category_top_query, const.Category.FRAMEWORK)
        top_frameworks_count = self._get_count(self._category_count_query % const.Category.FRAMEWORK)

#        top_databases = self.db.query(self._category_top_query, const.Category.DATABASE)
#        top_databases_count = self._get_count(self._category_count_query % const.Category.DATABASE)
#
#        top_toolkits = self.db.query(self._category_top_query, const.Category.TOOLKIT)
#        top_toolkits_count = self._get_count(self._category_count_query % const.Category.TOOLKIT)

        top_projects = escape.json_encode(top_projects)
        top_frameworks = escape.json_encode(top_frameworks)
#        top_databases = escape.json_encode(top_databases)
#        top_toolkits = escape.json_encode(top_toolkits)

        self.render("index.html", top_projects_count=top_projects_count,
                    top_projects=top_projects,
                    top_frameworks=top_frameworks,
                    top_frameworks_count=top_frameworks_count,
#                    top_databases=top_databases,
#                    top_databases_count=top_databases_count,
#                    top_toolkits=top_toolkits,
#                    top_toolkits_count=top_toolkits_count,
                    )

    def _get_count(self, query):
        count = self.db.get(query)
        if count:
            count = count.c
        else:
            count = 0

        return count

class FrontSearchHandler(BaseHandler):
    def get(self):
        self._context.title = "Search"
        self.render("search.html")


handlers = [
            (r"/?", FrontMainHandler),
            (r"/search", FrontSearchHandler),
            ]
