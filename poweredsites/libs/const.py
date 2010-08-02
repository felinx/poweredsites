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


class Status(object):
    LOCK = -2
    SPAM = -1
    INIT = 0
    PENDING = 1
    UNVERIFIED = 2
    ACTIVE = 9

class Role(object):
    NORMAL = 0
    STAFF = 5
    ADMIN = 9

class OpenID(object):
    GOOGLE = 1
    FACEBOOK = 2
    TWITTER = 3
    FRIENDFEED = 4

    NAME = {GOOGLE:"Google", FACEBOOK:"Facebook",
            TWITTER:"Twitter", FRIENDFEED:"Friendfeed"}

class Category(object):
    TOOLKIT = 1
    HOSTING = 2
    SERVER = 3
    DATABASE = 4
    FRAMEWORK = 5
    FRONTEND = 6
    LANGUAGE = 7
