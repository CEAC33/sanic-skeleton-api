import argparse
from sanic import Sanic

from core.extentions.exceptions import blueprint as ext_exceptions
from core.extentions.middlewares import blueprint as ext_middlewares

from apps.es_report import blueprint as app_name
from settings import Settings
from sanic_openapi import swagger_blueprint

from sanic_jwt import Initialize
from apps.jwt.main import authenticate

# Command line parser options & setup default values
parser = argparse.ArgumentParser()
parser.add_argument('--host', help='Setup host ip to listen up, default to 0.0.0.0', default='0.0.0.0')
parser.add_argument('--port', help='Setup port to attach, default to 8080', default='8080')
parser.add_argument('--workers', help='Setup workers to run, default to 1', type=int, default=1)
parser.add_argument('--debug', help='Enable or disable debugging', action='store_true')
parser.add_argument('--accesslog', help='Enable or disable access log', action='store_true')
args = parser.parse_args()

# Configure Sanic apps
app = Sanic(__name__)
app.config.from_object(Settings())

# Install extentions
app.blueprint(ext_exceptions)
app.blueprint(ext_middlewares)

# Versions
version = 'v1/'

# Name of the API
name = 'my_api'

# Install apps
app.blueprint(app_name, url_prefix=version+name)
app.blueprint(swagger_blueprint) # swagger

# JWT
Initialize(app, authenticate=authenticate)

# Running sanic, we need to make sure directly run by interpreter
# ref: http://sanic.readthedocs.io/en/latest/sanic/deploying.html#running-via-command
if __name__ == '__main__':
    app.run(
        host=args.host, 
        port=args.port, 
        workers=args.workers, 
        debug=args.debug, 
        access_log=args.accesslog
    )
