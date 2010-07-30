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

import logging
from tornado.web import asynchronous
from tornado import escape
from tornado.httpclient import AsyncHTTPClient
from tornado.web import UIModule

#import chardet
from BeautifulSoup import BeautifulSoup

from poweredsites.libs.handler import BaseHandler, StaffBaseHandler
from poweredsites.forms.submit import ProjectForm, ProjectPreForm
from poweredsites.libs.decorators import cache, authenticated


class ProjectHandler(BaseHandler):
    @property
    def categories(self):
        return self.db.query("select * from category order by id ASC")


class SubmitProjectHandler(ProjectHandler):
    _submit_template = "project/submit.html"

    @authenticated
    @asynchronous
    def get(self):
        self._context.title = "Submit a project"

        website = self.request.arguments.get("url", [""])[0]
        if website:
            http = AsyncHTTPClient()
            http.fetch(escape.url_unescape(website), self._on_fetch)
        else:
            self._context.metainfos = {}
            self.render(self._submit_template)

    def _on_fetch(self, response):
        metainfos = {"website":response.request.url}

        if response.code == 200:
            #encoding = chardet.detect(response.body)["encoding"]
            try:
                bs = BeautifulSoup(response.body)
                metas = bs.findAll("meta")
                metainfos["sitename"] = bs.find("title")
                if metainfos["sitename"] is None:
                    metainfos["sitename"] = ""
                else:
                    metainfos["sitename"] = metainfos["sitename"].contents[0]

                for meta in metas:
                    name = meta.get("name")
                    if name is not None:
                        content = meta.get("content")
                        if content is None:
                            content = ""
                        #metainfos[name] = unicode(content, encoding).encode("utf-8")
                        metainfos[name] = content
            except Exception, e:
                logging.error(str(e))

        self._context.metainfos = metainfos
        self.render(self._submit_template)

    @authenticated
    def post(self):
        fm = ProjectForm(self)
        self._context.metainfos = {}

        if fm.validate():
            self.redirect("http://" + fm._values["subdomain"].lower() + ".poweredsites.org/")
        else:
            fm.render(self._submit_template)

class SubmitProjectPreHandler(ProjectHandler):
    @authenticated
    def get(self):
        self._context.title = "Submit a project"
        self.render("project/submit_pre.html")

    @authenticated
    def post(self):
        fm = ProjectPreForm(self)

        if fm.validate():
            self.redirect("/submit/project?url=%s" % escape.url_escape(fm._values["website"]))
        else:
            fm.render("project/submit_pre.html")


class ProjectIndexHandler(ProjectHandler):
    _order_by = "id DESC"
    _condition = ""
    _handler_template = "site/index.html"
    _ws_count_query = "select count(*) as c from project_sites where project_id = %s"

    @property
    def cache_condition(self):
        subdomain = self.request.host.split(".")[0]
        if not subdomain.islower():
            self.redirect(self.request.host.lower())
        else:
            current_project = self.db.get("select * from project where subdomain = %s", subdomain)
            if current_project:
                condition = "select id from project_sites where project_id = %s order by id DESC" % current_project.id
                return str(condition)

        return ""

    @cache.page(3600)
    def get(self):
        subdomain = self.request.host.split(".")[0]
        if not subdomain.islower():
            self.redirect(self.request.host.lower())
        else:
            current_project = self.db.get("select * from project where subdomain = %s", subdomain)
            if current_project:
                self._context.ws_count_query = str(self._ws_count_query % current_project.id)
                self._context.ws_query = "select site.*, user.username, user.openid_name "\
                        "from site, user, project_sites where site.user_id = user.id "\
                        "and project_sites.project_id = %s "\
                        "and site.id = project_sites.site_id "\
                        "%s order by %s" % \
                        (current_project.id, self._condition, self._order_by)
                self._context.ws_query = str(self._context.ws_query)
                self._context.page = self.get_argument("page", 1)

                self._context.current_project = current_project
                self._context.project_name = current_project.project
                self._context.project_slogan = current_project.description

                self._context.title = current_project.project
                self._context.keywords = self._context.keywords + ",%s,%s" % \
                    (current_project.project, current_project.subdomain)
                self._context.description = current_project.description

                self.render(self._handler_template)
            else:
                self.redirect(self._context.options.home_url)

class ProjectPrHandler(ProjectIndexHandler):
    _order_by = "pr DESC, ar ASC"
    _handler_template = "site/pr.html"


class ProjectArHandler(ProjectIndexHandler):
    _order_by = "ar ASC"
    _handler_template = "site/ar.html"

class ProjectOpensourceHandler(ProjectIndexHandler):
    _order_by = "ar ASC"
    _condition = "and site.source_url is not NULL"
    _ws_count_query = "select count(*) as c from project_sites, site "\
            "where project_id = %s and source_url is not NULL and "\
            "project_sites.site_id=site.id"
    _handler_template = "site/opensource.html"


class ProjectWikiHandler(BaseHandler):
    @cache.page(3600 * 24)
    def get(self):
        self.render("wiki/index.html")


class HotProjectsModule(UIModule):
    _cache_key = "project/hot_projects_10"
    @cache.mem(key=_cache_key)
    def get_hot_projects(self, offset=10):
        return self.handler.db.query("select * from ("
                "(select *, count(site_id) from project_sites "
                "group by project_id order by count(site_id) DESC) as ps "
                "left join (select * from project) as p on ps.project_id = p.id) limit 0, %s", offset)

    def render(self):
        return self.render_string("modules/hot_projects.html", hot_projects=self.get_hot_projects())


class SideProjectsModule(HotProjectsModule):
    _cache_key = "project/hot_projects_15"
    _module_template = "modules/side_projects.html"
    @cache.cache()
    def render(self):
        projects = self.handler.db.query("select * from project order by subdomain ASC")
        hots = self.get_hot_projects(15)

        hot_projects = [hot.id for hot in hots]

        return self.render_string(self._module_template,
                                  projects=projects, hot_projects=hot_projects)

class ChatProjectsModule(SideProjectsModule):
    _module_template = "modules/chat_projects.html"


handlers = [
            (r"/submit/project", SubmitProjectHandler),
            (r"/submit/projectpre", SubmitProjectPreHandler),
            ]

sub_handlers = ["^[a-zA-Z_\-0-9]*\.poweredsites.org$",
              [(r"/", ProjectIndexHandler),
               (r"/wiki", ProjectWikiHandler),
               (r"/pr", ProjectPrHandler),
               (r"/ar", ProjectArHandler),
               (r"/opensource", ProjectOpensourceHandler),
               ]
            ]

ui_modules = {"side_projects":SideProjectsModule, "hot_projects":HotProjectsModule, "chat_projects":ChatProjectsModule}
