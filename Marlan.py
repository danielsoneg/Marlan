#!/usr/bin/env python
# Tornado
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.escape
from tornado.options import define, options
# Base System
import os
import logging
try: import simplejson as json
except ImportError: import json
import cStringIO
# Dropbox
from dropbox import auth, client
# Ours
from db import SQLite as db
import bundles

define("port", default=8000, help="run on the given port", type=int)

Users = db.userDB() 
#auth.HTTP_DEBUG_LEVEL=10

config = auth.Authenticator.load_config("config/config.ini")
config.update(auth.Authenticator.load_config("config/apikeys.ini"))
tokens = {}
user_tokens = {}

class dbAuth(object):
    """docstring for dbAuth"""
    def __init__(self):
        super(dbAuth, self).__init__()
        self.dba = auth.Authenticator(config)
        self.baseToken = self.dba.obtain_request_token()

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

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
        self.set_secure_cookie('destpath',sentpath) 
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
        self.set_secure_cookie("user", uid)
        dest = self.get_secure_cookie('destpath')
        self.set_secure_cookie('destpath','')
        self.redirect(dest)

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def prepare(self):
        #logging.info(self.get_login_url())
        if str(self.current_user) not in user_tokens.keys():
            self.set_secure_cookie("user", '')
            self.redirect("%s?next=%s"% (self.get_login_url(),self.request.full_url()))
            return
        userToken = user_tokens[str(self.current_user)]
        self.Auth = dbAuth()
        oauth_token = self.Auth.baseToken.from_string(userToken)
        self.dbc = client.DropboxClient(self.Auth.dba.config['server'], self.Auth.dba.config['content_server'], self.Auth.dba.config['port'], self.Auth.dba, oauth_token)
        self.clear_cookie('destpath')
        self.Bundles = bundles.Bundles(self.dbc)
    
    def get(self,path):
        (t, ret) = self.Bundles.getPath(path)
        getattr(self, 'get_%s' % t)(ret,path)
        
    def get_index(self, flist, path):
        if path == '' or path == '/': 
            title, npath = 'Index', ''
        else:
            split = path.rsplit('/',1)
            (npath, title) = (split[0], split[1]) if len(split) > 1 else ('',split[0])
        self.prepare()
        infopath = '%s/info.txt' % path
        infopath = infopath.replace('//', '/')
        (t, info) = self.Bundles.getPath(infopath)
        #(t,info) = ('error','')
        info = info.read() if t == "text" else ""
        other = flist['other']
        images = flist['images']
        #self.render("templates/index.html", title=title, path=path, dirs=flist['dirs'], files=flist['files'])
        self.set_header("Content-Type", 'text/plain')
        self.write(self.ret(title, npath, info, other, images))
        
    def ret(self, title, path, info, other, images):
        """docstring for ret"""
        ret = """Title: %(title)s
Path: %(path)s
Info: 
%(info)s
Files - 
Images: 
%(images)s
Other: 
%(other)s
"""
        val = {'title':title,'path':path,'info':info}
        val['other'] = '\n- '.join(other)
        val['images'] = '\n- '.join(images)
        logging.info(ret%val)
        return ret % val
    
    def get_image(self,image,path):
        self.clear()
        self.set_header("Content-Type", image.data['mime_type'])
        img = cStringIO.StringIO() 
        img.write(image.read())
        img.seek(0)
        logging.info(img)
        self.write(image.read())
    
    def post(self, path):
        if not path.endswith('.txt'):
            raise tornado.web.HTTPError(400)
        try: 
            action = self.get_argument('action')
        except:
            raise tornado.web.HTTPError(400)
        if hasattr(self, 'post_%s' % action):
            status = getattr(self, 'post_%s' %action)(path)
            self.write(status)
        else:
            logging.error('Asked for invalid action: %s' % action)
            raise tornado.web.HTTPError(400)
    
    def post_write(self,path):
        content = tornado.escape.xhtml_unescape(self.get_argument('text'))
        (t, f) = self.Bundles.getPath(path)
        if t == 'text' or t == 'new':
            status = f.write(content)
        else:
            status = self.__error(t)
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
            (r"/(.*?)", MainHandler),
    ],**settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()