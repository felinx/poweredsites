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

from tornado.web import asynchronous, HTTPError
from tornado import escape
from tornado.web import UIModule

from poweredsites.libs.handler import BaseHandler
from poweredsites.libs.alexarank import AlexaRankMixin
from poweredsites.libs.pagerank import PageRankMinxin
from poweredsites.libs.pagination import PaginationMixin
from poweredsites.libs.decorators import cache, authenticated
from poweredsites.forms.submit import SiteForm, SitePreForm, SitePoweredForm
from poweredsites.handlers.project import SubmitProjectHandler


class SubmitSitePreHandler(BaseHandler):
    @authenticated
    def get(self):
        self._context.title = "Submit site"
        self.render("site/submit_pre.html")

    @authenticated
    def post(self):
        fm = SitePreForm(self)

        if fm.validate():
            self.redirect("/submit/site?url=%s" % escape.url_escape(fm._values["website"]))
        else:
            fm.render("site/submit_pre.html")


class SubmitSiteHandler(SubmitProjectHandler, AlexaRankMixin, \
                        PageRankMinxin):
    _submit_template = "site/submit.html"

    def _authorize(self, author_id):
        if not (self.is_staff or self.current_user.id == author_id):
            raise HTTPError(403)

    @authenticated
    @asynchronous
    def get(self):
        self._context.css.append("markedit.css")
        self._context.title = "Submit site"
        uuid_ = self.get_argument("site", None)
        if uuid_:
            website = self.db.get("select * from site where uuid_ = %s", uuid_)
            if website:
                self._authorize(website.user_id)
                for k in website:
                    if website[k] is None:
                        website[k] = ""
                self._context.metainfos = website

                self.render(self._submit_template)
                return

        super(SubmitSiteHandler, self).get()

    @authenticated
    @asynchronous
    def post(self):
        self._context.css.append("markedit.css")
        self._context.metainfos = {}
        uuid_ = self.get_argument("site", None)
        if uuid_:
            website = self.db.get("select * from site where uuid_ = %s", uuid_)
            if website:
                self._authorize(website.user_id)
                self._context.metainfos = website

        fm = SiteForm(self)
        if fm.validate():
            self._site_record = self.db.get("select * from site where website = %s", \
                                            fm._values["website"])
            ### a chain of asynchronous operations            
            self.get_alexa_rank(fm._values["website"], self._ar_callback)
            self.get_pagerank(self._site_record.website, self._pr_callback)

            self.redirect("/submit/sitepowered?site=" + self._site_record.uuid_)
        else:
            fm.render("site/submit.html")

    def _ar_callback(self, ar):
        self.db.execute("UPDATE site SET ar = %s where id = %s", ar, self._site_record.id)

    def _pr_callback(self, pr):
        self.db.execute("UPDATE site SET pr = %s where id = %s", pr, self._site_record.id)


class SubmitSitePoweredHandler(BaseHandler):
    def prepare(self):
        super(SubmitSitePoweredHandler, self).prepare()

        self.projects = self.db.query("select * from project order by subdomain ASC")

    def _authorize(self, author_id):
        if not (self.is_staff or self.current_user.id == author_id):
            raise HTTPError(403)

    def get_powered_project(self, site_id):
        projects = self.db.query("select project_id from project_sites where site_id = %s", site_id)
        if projects:
            return [str(p.project_id) for p in projects]
        else:
            return []

    @authenticated
    def get(self):
        self._context.title = "Powered by"
        uuid_ = self.get_argument("site", None)
        if uuid_:
            website = self.db.get("select * from site where uuid_ = %s", uuid_)
            if not website:
                self.redirect("/")
            else:
                self._authorize(website.user_id)
                self._context.website = website
                self._context.powered_projects = self.get_powered_project(website.id)
                self.render("site/submit_powered.html")
        else:
            self.redirect("/")

    @authenticated
    def post(self):
        fm = SitePoweredForm(self)
        website = self.db.get("select * from site where id = %s", fm._parmas["site_id"])
        if website is None:
            self.redirect("/")

        self._authorize(website.user_id)

        if fm.validate():
            self.redirect("http://sites.poweredsites.org/%s" % website.uuid_)
        else:
            self._context.website = website
            self._context.powered_projects = self.get_powered_project(website.id)
            fm.render("site/submit_powered.html")


class _WebsiteHandler(BaseHandler):
    """Back compatible for old site page (uuid_ as path info)"""
    def get(self, uuid_):
        site = self.db.get("select site.*, user.username, user.openid_name from "\
                 "site, user where site.user_id = user.id and site.uuid_ = %s", uuid_)
        if not site:
            site = self.db.get("select site.*, user.username, user.openid_name from "\
                 "site, user where site.user_id = user.id and site.slug = %s", uuid_)
            if not site:
                raise HTTPError(404)

        self.redirect("/" + site.slug, permanent=True)


class WebsiteHandler(BaseHandler):
    def cache_pre(self, slug):
        site = self.db.get("select site.*, user.username, user.openid_name from "\
                 "site, user where site.user_id = user.id and site.slug = %s", slug)
        if not site:
            raise HTTPError(404)
        else:
            self.db.execute("UPDATE site SET click = %s where id = %s", site.click + 1, site.id)

        self._website = site

    @property
    def cache_condition(self):
        return "select updated from site where id = %s" % self._website.id

    @cache.page()
    def get(self, slug):
        site = self._website

        site_next = self.db.get("SELECT sitename,slug FROM site WHERE id = %s", site.id + 1)
        if site.id > 1:
            site_before = self.db.get("SELECT sitename,slug FROM site WHERE id = %s", site.id - 1)
        else:
            site_before = None

        powereds = self.db.query("select project.* from project_sites, project "\
                                 "where project_sites.site_id = %s and project_sites.project_id = project.id", site.id)

        powereds_desc = ",".join([p.project for p in powereds])
        self._context.title = site.sitename
        self._context.keywords = ",".join(site.sitename,
                                        powereds_desc,
                                        self._context.keywords
                                    )
        self._context.description = ",".join(site.sitename,
                                        "powered sites",
                                        powereds_desc,
                                        site.description,
                                    )
        self.render("site/site.html", site=site, site_before=site_before, site_next=site_next, powereds=powereds)


class _WebsiteIndexHandler(BaseHandler):
    def get(self):
        # redirect old sites page to home page
        self.redirect(self._context.options.home_url)


class _WebsitesFeedsHandler(BaseHandler):
    def get(self):
        # redirect feeds page to root domain for google webmasters tools
        self.redirect(self._context.options.home_url + "feeds")


class WebsitePoweredsModule(UIModule):
    def render(self, site_id):
        powereds = self.handler.db.query("select project.* from project_sites, project "\
                                 "where project_sites.site_id = %s and project_sites.project_id = project.id", site_id)

        return self.render_string("modules/website_powereds.html", powereds=powereds)


handlers = [
            (r"/submit/sitepre", SubmitSitePreHandler),
            (r"/submit/sitepre/([a-z\-_0-9]{3,20})", SubmitSitePreHandler),
            (r"/submit/site", SubmitSiteHandler),
            (r"/submit/site/([a-z\-_0-9]{3,20})", SubmitSiteHandler),
            (r"/submit/sitepowered", SubmitSitePoweredHandler),
            (r"/submit/sitepowered/([a-z\-_0-9]{3,20})", SubmitSitePoweredHandler),
            ]

sub_handlers = ["^sites.poweredsites.org$",
                [
                 (r"/", _WebsiteIndexHandler),
                 (r"/feeds", _WebsitesFeedsHandler),
                 (r"/([a-z0-9]{32})", _WebsiteHandler),
                 (r"/([^/]+)", WebsiteHandler),
                 ]
                ]

ui_modules = {"website_powereds":WebsitePoweredsModule, }

