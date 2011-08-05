import tornado.web
# Base System
import logging
try: import simplejson as json
except ImportError: import json
# Dropbox
from dropbox import client
# Ours
import bundles
import base
import auth

class MainHandler(base.BaseHandler):
    @tornado.web.authenticated
    def prepare(self):
        #logging.info(self.get_login_url())
        if str(self.current_user) not in auth.user_tokens.keys():
            self.set_cookie("user", '')
            self.redirect("%s?next=%s"% (self.get_login_url(),tornado.escape.url_escape(self.request.full_url())))
            return
        userToken = auth.user_tokens[str(self.current_user)]
        self.Auth = auth.dbAuth()
        oauth_token = self.Auth.baseToken.from_string(userToken)
        self.dbc = client.DropboxClient(self.Auth.dba.config['server'], self.Auth.dba.config['content_server'], self.Auth.dba.config['port'], self.Auth.dba, oauth_token)
        if self.get_cookie('destpath',default=False): self.clear_cookie('destpath')
        self.Bundles = bundles.Bundles(self.dbc, base.cipher)
    
    def get(self,path):
        if path.endswith('/'): self.redirect(path[-1] + path[:-1])
        (t, ret) = self.Bundles.getPath(path)
        getattr(self, 'get_%s' % t)(ret,path)
    
    def get_index(self, flist, path):
        title, paths = self.processPath(path)
        self.render("template/index.html", title=title, paths=paths, flist=flist, uid=self.current_user, public=False)
    
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
            p = base.cipher.hsh("%s-%s" % (uid, pw))
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
    
