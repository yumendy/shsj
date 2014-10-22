import os
import sys
import sae

from sae.ext.shell import ShellMiddleware

root = os.path.dirname(__file__)

sys.path.insert(0, os.path.join(root,'site-packages'))

def app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return ["Hello, world!"]

#application = sae.create_wsgi_app(ShellMiddleware(app))

from shsj import wsgi

application = sae.create_wsgi_app(wsgi.application)