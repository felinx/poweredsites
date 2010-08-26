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

import re
import unicodedata
import uuid
import logging
from formencode import validators
import markdown
from tornado import escape

from poweredsites.forms.base import BaseForm, URL
from poweredsites.libs import const

_domain_prefix_re = re.compile("(http://www\.|http://)")

class ProjectPreForm(BaseForm):
    website = URL(not_empty=True, max=600, add_http=True)


class ProjectForm(BaseForm):
    subdomain = validators.PlainText(not_empty=True, strip=True)
    name = validators.String(not_empty=True, min=3, max=30, strip=True)
    category = validators.Int(not_empty=True)

    keywords = validators.String(not_empty=False, max=100)
    desc = validators.String(not_empty=False, max=600)
    website = URL(not_empty=False, max=600, add_http=True)
    logo = URL(not_empty=False, max=600, add_http=True)

    def __after__(self):
        try:
            v = self._values
            status = const.Status.ACTIVE
            length = len(v["subdomain"])

            if length < 3 or length > 20:
                self.add_error("subdomain", "Name should be more than three and less than twenty charaters.")
            if self._handler.db.get("select * from project where subdomain = %s", v["subdomain"]):
                self.add_error("subdomain", "This name already be registered.")
            elif self._handler.db.get("select * from domains where domain = %s", v["subdomain"]):
                self.add_error("subdomain", "This name is reserved by poweredsites.org.")
            else:
                user_id = self._handler.current_user.id
                if (not self._handler.is_staff):
                    user_projects = self._handler.db.get("select count(*) as c from project where user_id = %s", \
                                                    user_id)

                    if user_projects is not None and user_projects.c >= 3:
                        # It will need approve if someone create more than three projects
                        status = const.Status.PENDING

                stmt = "INSERT INTO project (subdomain,project,website,keywords,description,"\
                        "category_id,user_id,logo,uuid_,created,status_) "\
                        "VALUES (%s,%s,%s,%s,%s,"\
                        "%s,%s,%s,%s,UTC_TIMESTAMP(),%s)"

                args = (v["subdomain"].lower(), v["name"], v["website"], v["keywords"], v["desc"], \
                        v["category"], user_id, v["logo"], uuid.uuid4().hex, status)

                self._handler.db.execute(stmt, *args)
        except Exception, e:
            logging.error(str(e))
            self.add_error("subdomain", "Submit project error, please try it later.")


class SitePreForm(ProjectPreForm):
    pass


class SiteForm(BaseForm):
    sitename = validators.String(not_empty=True, min=3, max=100, strip=True)
    website = URL(not_empty=True, max=600, add_http=True)

    desc = validators.String(not_empty=False, max=600)
    usecase = validators.String(not_empty=False, max=2000)
    site = validators.String(not_empty=False, max=32) # uuid_

    source_url = URL(not_empty=False, max=600, add_http=True)
    logo = URL(not_empty=False, max=600, add_http=True)

    def __after__(self):
        try:
            v = self._values
            # strip / to avoid treating http://example.com and http://example.com/ 
            # as different sites
            v["website"] = v["website"].strip("/")

            user_id = self._handler.current_user.id
            usecase_md = markdown.markdown(escape._unicode(v["usecase"]))

            if v.get("site", ""):
                stmt = "UPDATE site SET sitename = %s,website = %s,description = %s, "\
                        "usecase = %s,usecase_md = %s,source_url = %s, logo = %s, "\
                        "updated = UTC_TIMESTAMP() where uuid_ = %s"

                args = (v["sitename"], v["website"], v["desc"], \
                        v["usecase"], usecase_md, v["source_url"], v["logo"], \
                        v["site"])
                self._handler.db.execute(stmt, *args)
            else:
                if self._handler.db.get("select * from site where website = %s", v["website"]):
                    self.add_error("website", "This web site already be registered.")
                else:
                    if (not self._handler.is_staff):
                        user_projects = self._handler.db.get("select count(*) as c from site where user_id = %s", \
                                                        self._handler.current_user.id)

                        if user_projects is not None and user_projects.c >= 3:
                            # It will need approve if someone create more than three sites
                            status = const.Status.PENDING
                        else:
                            status = const.Status.UNVERIFIED
                    else:
                        status = const.Status.ACTIVE

                    slug = v["website"].lower().strip()
                    slug = _domain_prefix_re.sub("", slug)
                    slug = unicodedata.normalize("NFKD", escape._unicode(slug)).encode("ascii", "ignore")
                    slug = re.sub(r"[^\w]+", " ", slug)
                    slug = "-".join(slug.split())
                    if not slug:
                        slug = "site"
                    while True:
                        e = self._handler.db.get("SELECT * FROM site WHERE slug = %s", slug)
                        if not e:
                            break
                        slug += "-" + uuid.uuid4().hex[0:2]

                    stmt = "INSERT INTO site (sitename,website,description,usecase,usecase_md,source_url,"\
                            "user_id,logo,uuid_,created,updated,updated_ss,status_,slug) "\
                            "VALUES (%s,%s,%s,%s,%s,%s,"\
                            "%s,%s,%s,UTC_TIMESTAMP(),UTC_TIMESTAMP(),UTC_TIMESTAMP(),%s,%s)"

                    args = (v["sitename"], v["website"], v["desc"], v["usecase"], usecase_md, v["source_url"], \
                            user_id, v["logo"], uuid.uuid4().hex, status, slug)

                    self._handler.db.execute(stmt, *args)
        except Exception, e:
            logging.error(str(e))
            self.add_error("sitename", "Submit project error, please try it later.")

class SitePoweredForm(BaseForm):
    site_id = validators.Int(not_empty=True)
    projects = validators.Set(not_empty=True, use_set=True)
    powered_projects = validators.PlainText()

    def __after__(self):
        try:
            values = []
            del_values = []
            if self._values["powered_projects"] is not None:
                powered_projects = self._values["powered_projects"].split("-")
            else:
                powered_projects = []

            for project in self._values["projects"]:
                if project not in powered_projects:
                    values.append((self._values["site_id"], project))

            for project in powered_projects:
                if project not in self._values["projects"]:
                    del_values.append((self._values["site_id"], project))


            self._handler.db.executemany("INSERT INTO project_sites (site_id, project_id) "
                                         "VALUES (%s, %s)", values)
            if del_values:
                self._handler.db.executemany("DELETE from project_sites where site_id = %s and project_id = %s", del_values)

            if values or del_values:
                self._handler.db.execute("UPDATE site SET updated = UTC_TIMESTAMP() where id = %s", self._values["site_id"])

        except Exception, e:
            logging.error(str(e))
            self.add_error("projects", "Submit powered by information error, please try it later.")
