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

class ClearCacheHandler(AdminBaseHandler):
    def get(self):
        clearup()
        self.write("Clearup cache OK")


sub_handlers = ["^admin.poweredsites.org$",
              [(r"/clearcache", ClearCacheHandler),
               ]
            ]
