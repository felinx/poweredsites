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
from tornado.options import options
from tornado.web import UIModule

from poweredsites.libs.handler import BaseHandler, StaffBaseHandler
from poweredsites.libs.alexarank import AlexaRankMixin
from poweredsites.libs.pagerank import PageRankMinxin
from poweredsites.libs.snapshot import SnapShotMinxin
from poweredsites.libs.pagination import PaginationMixin
from poweredsites.libs.decorators import cache, authenticated
from poweredsites.forms.submit import SiteForm, SitePreForm, SitePoweredForm
from poweredsites.handlers.project import SubmitProjectHandler


class SubmitSitePreHandler(BaseHandler):
    @authenticated
    def get(self):
        self._context.title = "Submit a site"
        self.render("site/submit_pre.html")

    @authenticated
    def post(self):
        fm = SitePreForm(self)

        if fm.validate():
            self.redirect("/submit/site?url=%s" % escape.url_escape(fm._values["website"]))
        else:
            fm.render("site/submit_pre.html")


class SubmitSiteHandler(SubmitProjectHandler, AlexaRankMixin, \
                        PageRankMinxin, SnapShotMinxin):
    _submit_template = "site/submit.html"

    def _authorize(self, author_id):
        if not (self.is_staff or self.current_user.id == author_id):
            raise HTTPError(403)

    @authenticated
    @asynchronous
    def get(self):
        self._context.css.append("markedit.css")
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
            # a chain of asynchronous operations            
            self.get_alexa_rank(fm._values["website"], self._ar_callback)
            self.grab_shapshot(self._site_record.website, self._site_record.uuid_, \
                               self._snapshot_callback)
            self.get_pagerank(self._site_record.website, self._pr_callback)

            #self.redirect("http://sites.poweredsites.org/" + self._site_record.sitename.lower())
            self.redirect("/submit/sitepowered?site=" + self._site_record.uuid_)
        else:
            fm.render("site/submit.html")

    def _ar_callback(self, ar):
        self.db.execute("UPDATE site SET ar = %s where id = %s", ar, self._site_record.id)

    def _snapshot_callback(self):
        self.db.execute("UPDATE site SET updated_ss = UTC_TIMESTAMP() where id = %s", \
                        self._site_record.id)

    def _pr_callback(self, pr):
        self.db.execute("UPDATE site SET pr = %s where id = %s", pr, self._site_record.id)


class SubmitSitePoweredHandler(BaseHandler):
    def prepare(self):
        super(SubmitSitePoweredHandler, self).prepare()

        self.projects = self.db.query("select p.*, b.c from ( "
                "(select * from project) as p left join "
                "(select count(*) as c, project_id from project_sites group by project_id) as b "
                "on p.id = b.project_id) order by b.c DESC")
        self.current_project = None

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


class WebsiteIndexHandler(BaseHandler):
    _order_by = "id DESC"
    _condition = ""
    _handler_template = "site/index.html"
    _ws_count_query = "select count(*) as c from site"
    _context_title = "Latest sites"

    @cache.page(3600, condition="select id from site order by id DESC")
    def get(self):
        self._context.ws_count_query = self._ws_count_query
        self._context.ws_query = "select site.*, user.username, user.openid_name "\
                "from site, user where site.user_id = user.id %s order by %s" % \
                (self._condition, self._order_by)
        self._context.ws_query = str(self._context.ws_query)
        self._context.page = self.get_argument("page", 1)

        self._context.title = self._context_title

        self.render(self._handler_template)


class WebsitePrHandler(WebsiteIndexHandler):
    _order_by = "pr DESC, ar ASC"
    _handler_template = "site/pr.html"
    _context_title = "TOP page rank sites"


class WebsiteArHandler(WebsiteIndexHandler):
    _order_by = "ar ASC"
    _handler_template = "site/ar.html"
    _context_title = "TOP alexa rank sites"


class WebsiteOpensourceHandler(WebsiteIndexHandler):
    _order_by = "ar ASC"
    _condition = "and site.source_url is not NULL"
    _ws_count_query = "select count(*) as c from site where source_url is not NULL"
    _handler_template = "site/opensource.html"
    _context_title = "Open source sites"


class WebsiteHandler(BaseHandler):
    def get(self, uuid_):
        site = self.db.get("select site.*, user.username, user.openid_name from "\
                 "site, user where site.user_id = user.id and site.uuid_ = %s", uuid_)
        if not site:
            raise HTTPError(404)

        powereds = self.db.query("select project.* from project_sites, project "\
                                 "where project_sites.site_id = %s and project_sites.project_id = project.id", site.id)

        powereds_desc = ",".join([p.project for p in powereds])
        self._context.title = site.sitename
        self._context.keywords = self._context.keywords + "," + powereds_desc
        self._context.description = powereds_desc + ",PoweredSites" + "," + site.description[0:100]
        self.render("site/site.html", site=site, powereds=powereds)


class WebsitesModule(UIModule, PaginationMixin):
    def render(self, count_query, query, page):
        pagination = self.get_pagination(count_query, query, page)

        return self.render_string("modules/websites.html", pagination=pagination)

class WebsitePoweredsModule(UIModule):
    @cache.cache()
    def render(self, site_id):
        powereds = self.handler.db.query("select project.* from project_sites, project "\
                                 "where project_sites.site_id = %s and project_sites.project_id = project.id", site_id)

        return self.render_string("modules/website_powereds.html", powereds=powereds)


class WebsitesIndexModule(UIModule):
    _module_template = "modules/websites_index.html"
    @cache.cache(condition="select id from site order by id DESC")
    def render(self, count_query, query, page):
        return self.render_string(self._module_template,
                            count_query=count_query, query=query, page=page)


class WebsitesPrModule(WebsitesIndexModule):
    _module_template = "modules/websites_pr.html"


class WebsitesArModule(WebsitesIndexModule):
    _module_template = "modules/websites_ar.html"


class WebsitesOpensourceModule(WebsitesIndexModule):
    _module_template = "modules/websites_opensource.html"


handlers = [
            (r"/submit/sitepre", SubmitSitePreHandler),
            (r"/submit/sitepre/([a-z\-_0-9]{3,20})", SubmitSitePreHandler),
            (r"/submit/site", SubmitSiteHandler),
            (r"/submit/site/([a-z\-_0-9]{3,20})", SubmitSiteHandler),
            (r"/submit/sitepowered", SubmitSitePoweredHandler),
            (r"/submit/sitepowered/([a-z\-_0-9]{3,20})", SubmitSitePoweredHandler),
            ]

sub_handlers = ["^sites.poweredsites.org$",
              [(r"/", WebsiteIndexHandler),
               (r"/pr", WebsitePrHandler),
               (r"/ar", WebsiteArHandler),
               (r"/opensource", WebsiteOpensourceHandler),
               (r"/([a-z0-9]{32})", WebsiteHandler),
               ]
            ]

ui_modules = {"websites":WebsitesModule,
              "websites_index":WebsitesIndexModule,
              "websites_ar":WebsitesArModule,
              "websites_pr":WebsitesPrModule,
              "websites_opensource":WebsitesOpensourceModule,
              "website_powereds":WebsitePoweredsModule,
              }
