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

from poweredsites.libs.handler import ErrorHandler

handlers = []
sub_handlers = []
ui_modules = {}

if options.chat_app:
    from poweredsites.handlers import chat, project, site, blog
    sub_handlers.append(chat.sub_handlers)
else:
    from poweredsites.handlers import admin, user, front, \
                project, site, help, wiki, blog

    handlers.extend(front.handlers)
    handlers.extend(user.handlers)
    handlers.extend(site.handlers)
    handlers.extend(project.handlers)
    handlers.extend(help.handlers)

    # Append default 404 handler, and make sure it is the last one.
    handlers.append((r".*", ErrorHandler))


    sub_handlers.append(site.sub_handlers)
    sub_handlers.append(wiki.sub_handlers)
    sub_handlers.append(blog.sub_handlers)
    sub_handlers.append(admin.sub_handlers)
    # wildcat subdomain handler for project should be the last one.
    sub_handlers.append(project.sub_handlers)


ui_modules.update(site.ui_modules)
ui_modules.update(project.ui_modules)
ui_modules.update(blog.ui_modules)

for sh in sub_handlers:
    sh.append((r".*", ErrorHandler))
