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

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name="PoweredSites",
    version="0.1",
    install_requires=["pycurl==7.18.2",
                      "tornado>=0.2",
                      "pymongo>=1.7",
                      "markdown>=2.0.3",
                      "chardet==1.0.1",
                      "beautifulsoup==3.1.0.1",
                      "webhelpers>=1.0",
                      "formencode==1.2.2",
                      ],
    packages=find_packages(),
    author="Felinx",
    author_email="felinx.lee@gmail.com",
    url="http://poweredsites.org/",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    description="PoweredSites is the open source code of poweredsites.org which \
        is a site to show a project powered sites(eg. tornado powered sites).",
)
