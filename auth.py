import tornado.escape
import base
from dropbox import auth, client
#from db import SQLite as db
import os
pwd = os.path.dirname(os.path.abspath(__file__))

#auth.HTTP_DEBUG_LEVEL=10

config = auth.Authenticator.load_config(os.path.join(pwd,"config/config.ini"))
config.update(auth.Authenticator.load_config(os.path.join(pwd,"config/apikeys.ini")))
tokens = {}
user_tokens = {}

class dbAuth(object):
    """docstring for dbAuth"""
    def __init__(self):
        super(dbAuth, self).__init__()
        self.dba = auth.Authenticator(config)
        self.baseToken = self.dba.obtain_request_token()

class LoginHandler(base.BaseHandler):
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
        self.set_cookie("user", uid)
        dest = tornado.escape.url_unescape(self.get_cookie('destpath'))
        self.set_cookie('destpath','')
        self.redirect(dest)
    


