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

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation
from sqlalchemy import orm

DeclarativeBase = declarative_base()
metadata = DeclarativeBase.metadata

user = Table('user', metadata,
    Column(u'id', Integer(), primary_key=True, nullable=False),
            Column(u'username', String(length=40), nullable=False),
            Column(u'openid_api', Integer(), nullable=False),
            Column(u'openid_id', String(length=1024), nullable=False),
            Column(u'openid_name', String(length=1024), nullable=False),
            Column(u'email', String(length=120)),
            Column(u'signup_ip', String(length=39), nullable=False),
            Column(u'login_ip', String(length=39), nullable=False),
            Column(u'signup_date', DateTime(timezone=False), nullable=False),
            Column(u'login_date', DateTime(timezone=False), nullable=False),
            Column(u'login_c', Integer(), nullable=False),
            Column(u'click_c', Integer(), nullable=False),
            Column(u'role', Integer(), nullable=False),
            Column(u'blog_name', String(length=120)),
            Column(u'blog_url', String(length=600)),
            Column(u'uuid', String(length=32), nullable=False),
            Column(u'status', Integer(), nullable=False),
    )
Index(u'username', user.c.username, unique=True)
Index(u'email', user.c.email, unique=True)
Index(u'uuid', user.c.uuid, unique=True)

class User(object):
    pass

orm.mapper(User, user)


class Project(DeclarativeBase):
    __tablename__ = 'project'

    #column definitions
    created = Column(u'created', DateTime(timezone=False), nullable=False)
    desc = Column(u'desc', String(length=200, convert_unicode=False, assert_unicode=None), nullable=False)
    id = Column(u'id', Integer(), primary_key=True, nullable=False)
    keywords = Column(u'keywords', String(length=100, convert_unicode=False, assert_unicode=None), nullable=False)
    logo = Column(u'logo', String(length=600, convert_unicode=False, assert_unicode=None))
    name = Column(u'name', String(length=40, convert_unicode=False, assert_unicode=None), nullable=False)
    status = Column(u'status', Integer(), nullable=False)
    updated = Column(u'updated', TIMESTAMP(timezone=False), nullable=False)
    url = Column(u'url', String(length=600, convert_unicode=False, assert_unicode=None))
    urlfix = Column(u'urlfix', String(length=20, convert_unicode=False, assert_unicode=None), nullable=False)
    user_id = Column(u'user_id', Integer(), ForeignKey('user.id'), nullable=False)
    uuid = Column(u'uuid', String(length=32, convert_unicode=False, assert_unicode=None), nullable=False)


#class User(DeclarativeBase):
#    __tablename__ = 'user'
#    id = Column(u'id', Integer(), primary_key=True, nullable=False)
#    username = Column(u'username', String(length=40), nullable=False)
#    username = Column(u'openid_api', String(length=40), nullable=False)
#
#    #column definitions
#    blog_name = Column(u'blog_name', String(length=60, convert_unicode=False, assert_unicode=None))
#    blog_url = Column(u'blog_url', String(length=600, convert_unicode=False, assert_unicode=None))
#    click_c = Column(u'click_c', Integer(), nullable=False)
#    email = Column(u'email', String(length=120, convert_unicode=False, assert_unicode=None), nullable=False)
#    first_name = Column(u'first_name', String(length=45, convert_unicode=False, assert_unicode=None))
#
#    last_name = Column(u'last_name', String(length=45, convert_unicode=False, assert_unicode=None))
#    locale = Column(u'locale', String(length=45, convert_unicode=False, assert_unicode=None))
#    login_c = Column(u'login_c', Integer(), nullable=False)
#    login_date = Column(u'login_date', DateTime(timezone=False), nullable=False)
#    login_ip = Column(u'login_ip', String(length=39, convert_unicode=False, assert_unicode=None), nullable=False)
#    pic_url = Column(u'pic_url', String(length=600, convert_unicode=False, assert_unicode=None))
#    role = Column(u'role', Integer(), nullable=False)
#    signup_date = Column(u'signup_date', DateTime(timezone=False), nullable=False)
#    signup_ip = Column(u'signup_ip', String(length=39, convert_unicode=False, assert_unicode=None), nullable=False)
#    status = Column(u'status', Integer(), nullable=False)
#
#    uuid = Column(u'uuid', String(length=32, convert_unicode=False, assert_unicode=None), nullable=False)
#
#    #relation definitions
##    blogs = relation('Blog', secondary=blog_comments)
##    sites = relation('Site', secondary=wiki)
##    wikis = relation('Wiki', secondary=wiki_comments)


#blog_comments = Table(u'blog_comments', metadata,
#    Column(u'id', Integer(), primary_key=True, nullable=False),
#    Column(u'content', String(length=2000, convert_unicode=False, assert_unicode=None), nullable=False),
#    Column(u'markdown', Text(length=None, convert_unicode=False, assert_unicode=None), nullable=False),
#    Column(u'created', DateTime(timezone=False), nullable=False),
#    Column(u'updated', TIMESTAMP(timezone=False), nullable=False),
#    Column(u'blog_id', Integer(), ForeignKey('blog.id'), nullable=False),
#    Column(u'user_id', Integer(), ForeignKey('user.id'), nullable=False),
#    Column(u'comm_id', Integer(), ForeignKey('blog_comments.id'), nullable=False),
#)
#
#site_comments = Table(u'site_comments', metadata,
#    Column(u'id', Integer(), primary_key=True, nullable=False),
#    Column(u'site_id', Integer(), ForeignKey('site.id'), nullable=False),
#    Column(u'user_id', Integer(), ForeignKey('user.id'), nullable=False),
#    Column(u'comm_id', Integer(), ForeignKey('site_comments.id')),
#    Column(u'content', String(length=2000, convert_unicode=False, assert_unicode=None), nullable=False),
#    Column(u'markdown', Text(length=None, convert_unicode=False, assert_unicode=None), nullable=False),
#    Column(u'created', DateTime(timezone=False), nullable=False),
#    Column(u'updated', TIMESTAMP(timezone=False), nullable=False),
#)
#
#site_keywords = Table(u'site_keywords', metadata,
#    Column(u'site_id', Integer(), ForeignKey('site.id'), primary_key=True, nullable=False),
#    Column(u'keyword_id', Integer(), ForeignKey('keywords.id'), primary_key=True, nullable=False),
#)
#
#site_owner = Table(u'site_owner', metadata,
#    Column(u'site_id', Integer(), ForeignKey('site.id'), primary_key=True, nullable=False),
#    Column(u'user_id', Integer(), ForeignKey('user.id'), primary_key=True, nullable=False),
#    Column(u'role', Integer(), nullable=False),
#)
#
#site_vote = Table(u'site_vote', metadata,
#    Column(u'site_id', Integer(), ForeignKey('site.id'), primary_key=True, nullable=False),
#    Column(u'user_id', Integer(), ForeignKey('user.id'), primary_key=True, nullable=False),
#)
#
#wiki = Table(u'wiki', metadata,
#    Column(u'id', Integer(), primary_key=True, nullable=False),
#    Column(u'user_id', Integer(), ForeignKey('user.id'), nullable=False),
#    Column(u'title', String(length=100, convert_unicode=False, assert_unicode=None), nullable=False),
#    Column(u'slug', String(length=200, convert_unicode=False, assert_unicode=None), nullable=False),
#    Column(u'content', Text(length=None, convert_unicode=False, assert_unicode=None), nullable=False),
#    Column(u'markdown', Text(length=None, convert_unicode=False, assert_unicode=None), nullable=False),
#    Column(u'video_url', String(length=500, convert_unicode=False, assert_unicode=None)),
#    Column(u'video_md', String(length=2000, convert_unicode=False, assert_unicode=None)),
#    Column(u'comment_c', Integer(), nullable=False),
#    Column(u'click_c', Integer(), nullable=False),
#    Column(u'created', DateTime(timezone=False), nullable=False),
#    Column(u'updated', TIMESTAMP(timezone=False), nullable=False),
#    Column(u'site_id', Integer(), ForeignKey('site.id'), nullable=False),
#)
#
#wiki_comments = Table(u'wiki_comments', metadata,
#    Column(u'id', Integer(), primary_key=True, nullable=False),
#    Column(u'wiki_id', Integer(), ForeignKey('wiki.id'), nullable=False),
#    Column(u'user_id', Integer(), ForeignKey('user.id'), nullable=False),
#    Column(u'content', String(length=2000, convert_unicode=False, assert_unicode=None), nullable=False),
#    Column(u'markdown', Text(length=None, convert_unicode=False, assert_unicode=None), nullable=False),
#    Column(u'created', DateTime(timezone=False), nullable=False),
#    Column(u'updated', TIMESTAMP(timezone=False), nullable=False),
#    Column(u'comm_id', Integer(), ForeignKey('wiki_comments.id')),
#)
#
#wiki_keywords = Table(u'wiki_keywords', metadata,
#    Column(u'wiki_id', Integer(), ForeignKey('wiki.id'), primary_key=True, nullable=False),
#    Column(u'keyword_id', Integer(), ForeignKey('keywords.id'), primary_key=True, nullable=False),
#)
#
#class Blog(DeclarativeBase):
#    __tablename__ = 'blog'
#
#    #column definitions
#    content = Column(u'content', Text(length=None, convert_unicode=False, assert_unicode=None), nullable=False)
#    created = Column(u'created', DateTime(timezone=False), nullable=False)
#    id = Column(u'id', Integer(), primary_key=True, nullable=False)
#    markdown = Column(u'markdown', Text(length=None, convert_unicode=False, assert_unicode=None), nullable=False)
#    slug = Column(u'slug', String(length=200, convert_unicode=False, assert_unicode=None), nullable=False)
#    title = Column(u'title', String(length=100, convert_unicode=False, assert_unicode=None), nullable=False)
#    updated = Column(u'updated', TIMESTAMP(timezone=False), nullable=False)
#    user_id = Column(u'user_id', Integer(), ForeignKey('user.id'), nullable=False)
#    video_md = Column(u'video_md', String(length=2000, convert_unicode=False, assert_unicode=None))
#    video_url = Column(u'video_url', String(length=500, convert_unicode=False, assert_unicode=None))
#
#    #relation definitions
#    user = relation('User')
#    users = relation('User', secondary=blog_comments)
#
#
#class BlogComment(DeclarativeBase):
#    __table__ = blog_comments
#
#
#    #relation definitions
#    blog = relation('Blog')
#    blog_comments = relation('BlogComment')
#    user = relation('User')
#    blogs = relation('Blog', secondary=blog_comments)
#
#
#class Help(DeclarativeBase):
#    __tablename__ = 'help'
#
#    #column definitions
#    content = Column(u'content', Text(length=None, convert_unicode=False, assert_unicode=None), nullable=False)
#    created = Column(u'created', DateTime(timezone=False), nullable=False)
#    desc = Column(u'desc', String(length=200, convert_unicode=False, assert_unicode=None), nullable=False)
#    id = Column(u'id', Integer(), primary_key=True, nullable=False)
#    keywords = Column(u'keywords', String(length=100, convert_unicode=False, assert_unicode=None), nullable=False)
#    markdown = Column(u'markdown', Text(length=None, convert_unicode=False, assert_unicode=None), nullable=False)
#    name = Column(u'name', String(length=40, convert_unicode=False, assert_unicode=None), nullable=False)
#    updated = Column(u'updated', TIMESTAMP(timezone=False), nullable=False)
#    urlfix = Column(u'urlfix', String(length=20, convert_unicode=False, assert_unicode=None), nullable=False)
#    user_id = Column(u'user_id', Integer(), ForeignKey('user.id'), nullable=False)
#    vedio_md = Column(u'vedio_md', String(length=2000, convert_unicode=False, assert_unicode=None))
#    vedio_url = Column(u'vedio_url', String(length=600, convert_unicode=False, assert_unicode=None))
#
#    #relation definitions
#    user = relation('User')
#
#
#class Keyword(DeclarativeBase):
#    __tablename__ = 'keywords'
#
#    #column definitions
#    id = Column(u'id', Integer(), primary_key=True, nullable=False)
#    keyword = Column(u'keyword', String(length=40, convert_unicode=False, assert_unicode=None), nullable=False)
#
#    #relation definitions
#    sites = relation('Site', secondary=site_keywords)
#    wikis = relation('Wiki', secondary=wiki_keywords)
#
#
#class Project(DeclarativeBase):
#    __tablename__ = 'project'
#
#    #column definitions
#    created = Column(u'created', DateTime(timezone=False), nullable=False)
#    desc = Column(u'desc', String(length=200, convert_unicode=False, assert_unicode=None), nullable=False)
#    id = Column(u'id', Integer(), primary_key=True, nullable=False)
#    keywords = Column(u'keywords', String(length=100, convert_unicode=False, assert_unicode=None), nullable=False)
#    logo = Column(u'logo', String(length=600, convert_unicode=False, assert_unicode=None))
#    name = Column(u'name', String(length=40, convert_unicode=False, assert_unicode=None), nullable=False)
#    status = Column(u'status', Integer(), nullable=False)
#    updated = Column(u'updated', TIMESTAMP(timezone=False), nullable=False)
#    url = Column(u'url', String(length=600, convert_unicode=False, assert_unicode=None))
#    urlfix = Column(u'urlfix', String(length=20, convert_unicode=False, assert_unicode=None), nullable=False)
#    user_id = Column(u'user_id', Integer(), ForeignKey('user.id'), nullable=False)
#    uuid = Column(u'uuid', String(length=32, convert_unicode=False, assert_unicode=None), nullable=False)
#
#    #relation definitions
#    user = relation('User')
#
#
#class Site(DeclarativeBase):
#    __tablename__ = 'site'
#
#    #column definitions
#    ar = Column(u'ar', Integer(), nullable=False)
#    click_c = Column(u'click_c', Integer(), nullable=False)
#    comment_c = Column(u'comment_c', Integer(), nullable=False)
#    created = Column(u'created', DateTime(timezone=False), nullable=False)
#    desc = Column(u'desc', String(length=200, convert_unicode=False, assert_unicode=None), nullable=False)
#    id = Column(u'id', Integer(), primary_key=True, nullable=False)
#    logo = Column(u'logo', String(length=600, convert_unicode=False, assert_unicode=None))
#    name = Column(u'name', String(length=40, convert_unicode=False, assert_unicode=None), nullable=False)
#    pr = Column(u'pr', Integer(), nullable=False)
#    snapshot = Column(u'snapshot', String(length=32, convert_unicode=False, assert_unicode=None))
#    source_code = Column(u'source_code', String(length=600, convert_unicode=False, assert_unicode=None))
#    updated = Column(u'updated', DateTime(timezone=False), nullable=False)
#    url = Column(u'url', String(length=600, convert_unicode=False, assert_unicode=None), nullable=False)
#    urlfix = Column(u'urlfix', String(length=20, convert_unicode=False, assert_unicode=None), nullable=False)
#    usecase = Column(u'usecase', Text(length=None, convert_unicode=False, assert_unicode=None), nullable=False)
#    usecase_md = Column(u'usecase_md', Text(length=None, convert_unicode=False, assert_unicode=None), nullable=False)
#    user_id = Column(u'user_id', Integer(), ForeignKey('user.id'), nullable=False)
#    uuid = Column(u'uuid', String(length=32, convert_unicode=False, assert_unicode=None), nullable=False)
#    vote_c = Column(u'vote_c', Integer(), nullable=False)
#
#    #relation definitions
#    user = relation('User')
#    users = relation('User', secondary=wiki)
#    keywords = relation('Keyword', secondary=site_keywords)
#
#
#class SiteComment(DeclarativeBase):
#    __table__ = site_comments
#
#
#    #relation definitions
#    site = relation('Site')
#    site_comments = relation('SiteComment')
#    user = relation('User')
#    sites = relation('Site', secondary=site_comments)
#
#
#class SiteOwner(DeclarativeBase):
#    __table__ = site_owner
#
#
#    #relation definitions
#    site = relation('Site')
#    user = relation('User')
#
#
#
#
#class Wiki(DeclarativeBase):
#    __table__ = wiki
#
#
#    #relation definitions
#    site = relation('Site')
#    user = relation('User')
#    users = relation('User', secondary=wiki_comments)
#    keywords = relation('Keyword', secondary=wiki_keywords)
#
#
#class WikiComment(DeclarativeBase):
#    __table__ = wiki_comments
#
#
#    #relation definitions
#    user = relation('User')
#    wiki = relation('Wiki')
#    wiki_comments = relation('WikiComment')
#    wikis = relation('Wiki', secondary=wiki_comments)
