#!/usr/bin/env python
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

import os
from tornado.options import options

from poweredsites.libs.utils import AsyncProcessMixin

class SnapShotMinxin(AsyncProcessMixin):
    def grab_shapshot(self, url, uuid_, callback, width=960, height=720, scale_width=600, scale_height=450):
        # please make sure the permission right        
        fd = os.path.join(options.snapshot_dir, uuid_[0:2])
        if not os.path.isdir(fd):
            os.mkdir(fd)
        f = os.path.join(fd, "%s.png" % uuid_)

        cmd = "%s -o %s -g %d %d --scale %d %d %s" % (options.webkit2png, f, width, height, scale_width, scale_height, url)
        self.call_subprocess(str(cmd))
