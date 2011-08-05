import logging
import base
import re
import urllib
import tornado.httpclient
import bundles
import markdown

class TextHandler(base.BaseHandler):
    @tornado.web.asynchronous
    def get(self,path,filename):
        logging.info('Filename: %s' % filename)
        tpath = '/'.join([urllib.quote(p) for p in path.rstrip('/').split('/')])
        self.path = path
        self.filename = filename
        if re.match(r'u\d{5,6}/', path) != None:
            uid = tpath[1:tpath.find('/')]
            tpath = tpath[tpath.find('/')+1:]
            self.public = True
        else:
            uid = self.current_user
            self.public = False
        if u'Accept' not in self.request.headers or '/json' not in self.request.headers[u'Accept']:
            flist = {'folders':[],'files':[],'images':[],'has_info':False,'has_pass':False}
            title, paths = self.processPath('%s/%s.txt' % (tpath, filename), uid)
            self.render("template/index.html", title=title, paths=paths, flist=flist, uid=uid, public=self.public)
            self.finish()
        logging.info('ASync-Getting ' + path + ' ' + filename)
        #logging.info(tpath)
        url = "http://dl.dropbox.com/u/%(uid)s/%(path)s/%(filename)s.txt" % {'uid':uid,'path':tpath,'filename':filename}
        #logging.info(url)
        http = tornado.httpclient.AsyncHTTPClient()
        http.fetch(url, callback=self.on_response)
    
    def on_response(self, response):
        #logging.info(self.request.headers)
        if response.error:
            logging.error(response)
            self.write(' ')
        else:
            content = bundles.linkify(response.body)
            #content = response.body
            if self.public:
                content = markdown.markdown(content)
            self.write({'content':content})
        logging.info("Finishing...")
        self.finish()
    
