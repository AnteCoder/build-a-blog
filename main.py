#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2

from google.appengine.ext import db


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

def get_posts(limit, offset):
    posts = db.GqlQuery("SELECT * FROM BlogPosts ORDER BY created DESC LIMIT " + str(limit) + " OFFSET " + str(offset))

    return posts

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class BlogPosts(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class BlogForm(Handler):
    def render_form(self, title="", body="", error=""):

    	self.render("front.html", title=title, body=body, error=error)

    def get(self):
        self.render_form()

    def post(self):

        title = self.request.get("title")
        body =  self.request.get("body")

        if title and body:

            b = BlogPosts(title = title, body = body)
            b.put()

            self.redirect("/blog/" + str(b.key().id()))

        else:
            error = "Please enter both a post title and body."
            self.render_form(title, body, error)

class Index(Handler):
    def render_index(self):

        #I am automatically redirecting from the Index to the blog page, since the index page has no content
    	self.redirect("/blog")

    def get(self):
        self.render_index()

class Bposts(Handler):
    def render_blog(self, title="", body=""):

        # This is a call to the get_posts function above that sets the LIMIT and OFFSET on the GQL query that determines which and how many posts appear on the page
        bposts = get_posts(5, 0)

        #bposts = db.GqlQuery("SELECT * FROM BlogPosts ORDER BY created DESC LIMIT 5")

    	self.render("blog.html", title=title, body=body,  bposts=bposts)

    def get(self):
        self.render_blog()

class PostHandler(Handler):
    def get(self, post_id, error=""):

        post = BlogPosts.get_by_id(int(post_id))

        if not post:

            error="This post does not exist. Try again."
            t = jinja_env.get_template('blog_post.html')
            content = t.render(post=post, error=error)


        else:
            t = jinja_env.get_template('blog_post.html')
            content = t.render(post=post)

        self.response.write(content)


app = webapp2.WSGIApplication([
    ('/', Index),
    ('/newpost', BlogForm),
    ("/blog", Bposts),
    webapp2.Route('/blog/<post_id:\d+>', PostHandler),
], debug=True)
