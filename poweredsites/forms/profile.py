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
from formencode import validators
from tornado.options import options

from poweredsites.forms.base import BaseForm, URL
from poweredsites.libs import const

class ProfileForm(BaseForm):
    email = validators.Email(not_empty=True, resolve_domain=False, max=120)
    username = validators.PlainText(not_empty=True, strip=True)

    blog_name = validators.String(not_empty=False, max=40, strip=True)
    blog_url = URL(not_empty=False, max=600, add_http=True)

    def __after__(self):
        try:
            v = self._values
            length = len(v["username"])

            if length < 3 or length > 40:
                self.add_error("username", "Username should be more than three and less than forty charaters.")

            self._handler.db.execute(
                            "UPDATE user SET username = %s, email = %s, status_ = %s, \
                            blog_name = %s, blog_url = %s WHERE id = %s",
                            v['username'].lower(), v['email'], const.Status.ACTIVE, \
                            v['blog_name'], v['blog_url'], self._handler.current_user.id
                            )

            self._handler.set_secure_cookie("user", v['username'], domain=options.cookie_domain)
        except Exception, e:
            logging.error(str(e))
            self.add_error("username", "Save profile error, please try it later.")
