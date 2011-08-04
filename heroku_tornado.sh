virtualenv --no-site-packages .
source bin/activate
bin/pip install tornado
bin/pip freeze > requirements.txt
mkdir app
git init
cat >.gitignore <<EOF
bin/
include/
lib/
EOF
echo
cat >> app/app.py <<EOF

import os
import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()

EOF

cat > Procfile <<EOF
web:      bin/python app/app.py 0.0.0.0:\$PORT
EOF

git add .
git commit -m 'startproject'
heroku create --stack cedar
git push heroku master