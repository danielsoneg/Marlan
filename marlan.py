#!/usr/bin/env python
# Tornado
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.escape
import tornado.httpclient
from tornado.options import define, options
# Base System
import os
import logging
try: import simplejson as json
except ImportError: import json
import cStringIO
import subprocess
import urllib
import time
import re
import markdown
# Dropbox
from dropbox import auth, client
# Ours
from db import SQLite as db
import bundles
import cipher

define("port", default=8000, help="run on the given port", type=int)

Users = db.userDB() 
#auth.HTTP_DEBUG_LEVEL=10

config = auth.Authenticator.load_config("config/config.ini")
config.update(auth.Authenticator.load_config("config/apikeys.ini"))
tokens = {}
user_tokens = {}

c = cipher.Cipher()

class dbAuth(object):
    """docstring for dbAuth"""
    def __init__(self):
        super(dbAuth, self).__init__()
        self.dba = auth.Authenticator(config)
        self.baseToken = self.dba.obtain_request_token()

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_cookie("user")

    def encookieatePath(self, p):
        p = p.replace('/','-').replace(' ','_')
        return p

class LoginHandler(BaseHandler):
    """docstring for LoginHandler"""
    def prepare(self):
        self.Auth = dbAuth()
    
    def get(self):
        if self.get_argument('oauth_token',False):
            self.setAccess()
        else:
            self.getAccess()
    
    def getAccess(self):
        userToken = self.Auth.dba.obtain_request_token()
        tokens[userToken.key] = userToken.to_string()
        sentpath = self.get_argument('next','/')
        self.set_cookie('destpath',tornado.escape.url_escape(sentpath)) 
        userAuthURL= self.Auth.dba.build_authorize_url(userToken,'http://%s%s' %(self.request.headers['Host'],self.get_login_url()))
        self.redirect(userAuthURL)
        pass
    
    def setAccess(self):
        uid = self.get_argument('uid')
        token = self.Auth.baseToken.from_string(tokens[self.get_argument('oauth_token')])
        oauth_token = self.Auth.dba.obtain_access_token(token,'')
        user_tokens[uid] = oauth_token.to_string()
        dbc = client.DropboxClient(self.Auth.dba.config['server'], self.Auth.dba.config['content_server'], self.Auth.dba.config['port'], self.Auth.dba, oauth_token)
        email = dbc.account_info().data['email']
        Users.addUser(uid,oauth_token,email)
        self.set_cookie("user", uid)
        dest = tornado.escape.url_unescape(self.get_cookie('destpath'))
        self.set_cookie('destpath','')
        self.redirect(dest)
    


class InfoHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self,path):
        logging.info('ASync-Getting ' + path)
        tpath = '/'.join([urllib.quote(p) for p in path.rstrip('/').split('/')])
        if re.match(r'u\d{5,6}/', path) != None:
            uid = tpath[1:tpath.find('/')]
            tpath = tpath[tpath.find('/')+1:]
            self.public = True
        else:
            uid = self.current_user
            self.public = False
        #logging.info(tpath)
        url = "http://dl.dropbox.com/u/%(uid)s/%(path)s/info.txt" % {'uid':uid,'path':tpath}
        #logging.info(url)
        http = tornado.httpclient.AsyncHTTPClient()
        http.fetch(url, callback=self.on_response)
    
    def on_response(self, response):
        if response.error:
            logging.error(response)
            self.write(' ')
        else:
            content = bundles.linkify(response.body)
            #content = response.body
            if self.public:
                content = markdown.markdown(content)
            self.write(content)
        logging.info("Finishing...")
        self.finish()
    

class PublicHandler(BaseHandler):
    def get(self,uid,path):
        #self.clear_all_cookies()
        title, paths = self.__processPath(path,uid)
        flist = {'folders':[],'files':[],'images':[],'has_info':False}
        self.render("template/index.html", title=title, paths=paths, flist=flist, uid=uid, public=True)
    
    def __processPath(self, path,uid):
        longp = "/u%s" % uid
        path = path.rstrip('/')
        if path == '': return 'Index',[]
        pathlist = path.split('/')
        paths = []
        title = pathlist.pop()
        for p in pathlist:
            longp = longp + '/%s' % p
            paths.append(longp)
        return title, paths
    
    @tornado.web.asynchronous
    def post(self,uid,path):
        logging.info('ASync-Posting ' + path)
        pw = self.get_argument('pw', default=False)
        logging.info('pw: %s' % pw)
        logging.info('uid: %s' % uid)
        self.op = '/%s/%s' % (uid, path)
        if pw == 'cookie':
            pw=self.get_secure_cookie('pw-%s' % self.encookieatePath(self.op))
            logging.info(pw)
            self.p=pw
        else:
            self.p = c.hsh("%s-%s" % (uid, pw))
        if not pw or pw is None:
            raise tornado.web.HTTPError(403)
            self.finish()
        #logging.info('self.p: %s' % self.p)
        path = '/'.join([urllib.quote(p) for p in path.rstrip('/').split('/')])
        self.url = "http://dl.dropbox.com/u/%(uid)s/%(path)s/" % {'uid':uid,'path':path}
        url = self.url + '.metadata'
        #logging.info(url)
        http = tornado.httpclient.AsyncHTTPClient()
        http.fetch(url, callback=self.on_response)
    
    def on_response(self, response):
        logging.info('gotResponse')
        #logging.info(response.body)
        logging.info('Key: %s' % self.p)
        md = c.decryptInfo(self.p,response.body)
        if md == False:
            logging.info('No MD')
            raise tornado.web.HTTPError(403)
        else:
            #logging.info("Path for Cookie: %s" % self.op)
            self.set_secure_cookie('pw-%s' % self.encookieatePath(self.op),self.p,expires_days=60)
            self.write(md)
            self.finish()
        return
    

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def prepare(self):
        #logging.info(self.get_login_url())
        if str(self.current_user) not in user_tokens.keys():
            self.set_cookie("user", '')
            self.redirect("%s?next=%s"% (self.get_login_url(),tornado.escape.url_escape(self.request.full_url())))
            return
        userToken = user_tokens[str(self.current_user)]
        self.Auth = dbAuth()
        oauth_token = self.Auth.baseToken.from_string(userToken)
        self.dbc = client.DropboxClient(self.Auth.dba.config['server'], self.Auth.dba.config['content_server'], self.Auth.dba.config['port'], self.Auth.dba, oauth_token)
        if self.get_cookie('destpath',default=False): self.clear_cookie('destpath')
        self.Bundles = bundles.Bundles(self.dbc, c)
    
    def get(self,path):
        (t, ret) = self.Bundles.getPath(path)
        getattr(self, 'get_%s' % t)(ret,path)
    
    def get_index(self, flist, path):
        title, paths = self.__processPath(path)
        self.render("template/index.html", title=title, paths=paths, flist=flist, uid=self.current_user, public=False)
    
    def __processPath(self, path):
        longp = ""
        path = path.rstrip('/')
        if path == '': return 'Index',[]
        pathlist = path.split('/')
        paths = []
        title = pathlist.pop()
        for p in pathlist:
            longp = longp + '/%s' % p
            paths.append(longp)
        return title, paths
    
    def post(self, path):
        logging.info("Posting!")
        try: 
            action = self.get_argument('action')
        except:
            raise tornado.web.HTTPError(400)
        if hasattr(self, 'post_%s' % action):
            status = getattr(self, 'post_%s' %action)(path)
            if status:
                self.write(status)
            else:
                self.finish()
        else:
            logging.error('Asked for invalid action: %s' % action)
            raise tornado.web.HTTPError(400)
    
    def post_share(self, path):
        pw = self.get_argument('pw', default=False)
        uid = self.current_user
        p = False
        if pw != False:
            p = c.hsh("%s-%s" % (uid, pw))
            logging.info("%s - %s" % (p, path))
            self.set_secure_cookie('share-%s' % self.encookieatePath(path),p,expires_days=60)
            logging.info("Writing metadata")
            self.Bundles.writeMetadata(path,p)
        return json.dumps({'Code':1})
    
    def post_metadata(self,path):
        logging.info('meta-data-ing')
        p = self.get_secure_cookie('share-%s' % self.encookieatePath(path),False)
        if p:
            self.Bundles.writeMetadata(path,p)
            return "1"
        else:
            return "0"
    
    def post_write(self,path):
        content = tornado.escape.xhtml_unescape(self.get_argument('text'))
        pw = self.get_secure_cookie('share-%s' % self.encookieatePath(path))
        status = self.Bundles.writeContent(path,content,pw)
        return status
    
    def post_rename(self,path):
        newPath = self.get_argument('name')
        (t, f) = self.Bundles.getPath(path)
        if t == 'text':
            status = f.rename(newPath)
        else:
            status = self.__error(t)
        return status
    
    def __error(t):
        #logging.info(t)
        status = json.dumps({'Code':0,'Message':t})
        return status
    

def main():
    tornado.options.parse_command_line()
    settings = {
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "cookie_secret": "TmV2ZXJHZXRNZUx1dsakflhsdjY2t5Q2hhcm1z",
        "login_url": "/login",
        "debug": "true",
    }
    application = tornado.web.Application([
        (r"/login", LoginHandler),
        (r"/(.*?)/info.txt", InfoHandler),
        (r'/u([\d]{5,6})/(.*?)', PublicHandler),
            (r"/(.*?)", MainHandler),
    ],**settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
