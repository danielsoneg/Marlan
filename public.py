import base
import logging
import tornado.httpclient
import urllib


class PublicHandler(base.BaseHandler):
    def get(self,uid,path):
        #self.clear_all_cookies()
        title, paths = self.processPath(path,uid)
        flist = {'folders':[],'files':[],'images':[],'has_info':False}
        self.render("template/index.html", title=title, paths=paths, flist=flist, uid=uid, public=True)
    
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
            self.p = base.cipher.hsh("%s-%s" % (uid, pw))
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
        md = base.cipher.decryptInfo(self.p,response.body)
        if md == False:
            logging.info('No MD')
            raise tornado.web.HTTPError(403)
        else:
            #logging.info("Path for Cookie: %s" % self.op)
            self.set_secure_cookie('pw-%s' % self.encookieatePath(self.op),self.p,expires_days=60)
            self.write(md)
            self.finish()
        return
    

