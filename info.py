import logging
import base
import re
import urllib
import tornado.httpclient
import bundles
import markdown

class InfoHandler(base.BaseHandler):
    @tornado.web.asynchronous
    def get(self,path):
        logging.info('ASync-Getting ' + path)
        logging.info(self.request.headers)
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
    
