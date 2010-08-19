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

from poweredsites.libs.handler import StaffBaseHandler, AdminBaseHandler
from poweredsites.db.caches import clearup
from poweredsites.libs import const


class AdminIndexHandler(AdminBaseHandler):
    def get(self):
        self.render("admin/index.html")


class AdminClearCacheHandler(AdminBaseHandler):
    def get(self):
        clearup()
        self.write("Clearup cache OK")


class AdminNewUsersHandler(AdminBaseHandler):
    def get(self):
        # New users list, temp
        users = self.db.query("select * from user order by id DESC limit 0, 200")
        count = self.db.get("select count(*) as c from user")
        if count:
            count = count.c
        else:
            count = 0
        self.render("admin/newusers.html", users=users, count=count, const=const)


class AdminAddSiteSlugHandler(AdminBaseHandler):
    def get(self):
        import re
        import unicodedata
        import uuid

        _domain_prefix_re = re.compile("(http://www\.|http://)")
        sites = self.db.query("select * from site")
        if sites:
            for site in sites:
                slug = site.website.lower().strip()
                slug = _domain_prefix_re.sub("", slug)
                slug = unicodedata.normalize("NFKD", slug).encode("ascii", "ignore")
                slug = re.sub(r"[^\w]+", " ", slug)
                slug = "-".join(slug.split())
                if not slug:
                    slug = "site"
                while True:
                    e = self.db.get("SELECT * FROM site WHERE slug = %s", slug)
                    if not e:
                        break
                    slug += "-" + uuid.uuid4().hex[0:2]

                self.db.execute("UPDATE site SET slug = %s where id = %s", slug, site.id)

        self.write("Update slug OK")

sub_handlers = ["^admin.poweredsites.org$",
                [(r"/?", AdminIndexHandler),
                 (r"/clearcache", AdminClearCacheHandler),
                 (r"/newusers", AdminNewUsersHandler),
                 (r"/addsiteslug", AdminAddSiteSlugHandler),
               ]
            ]
