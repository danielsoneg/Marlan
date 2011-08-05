# Tornado
import tornado.web
import cipher

cipher = cipher.Cipher()

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_cookie("user")
    
    def encookieatePath(self, p):
        #TODO: Do real fixing of path for cookies
        p = p.replace('/','-').replace(' ','_')
        return p
    
    def processPath(self, path, uid=False):
        longp = "/u%s" % uid if uid else ''
        path = path.rstrip('/')
        if path == '': return 'Index',[]
        pathlist = path.split('/')
        paths = []
        title = pathlist.pop()
        for p in pathlist:
            longp = longp + '/%s' % p
            paths.append(longp)
        return title, paths
    
    
