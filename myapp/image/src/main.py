#!/usr/bin/env python3

from flask import Flask
from gevent.pywsgi import WSGIServer
from flask_cors import CORS
from flask_restful import Api
from time import sleep

from logger import appLogger
from config import Config
from alive import Check
from apis import Version, Status

app = Flask(__name__)
app.logger = appLogger
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
api = Api(app)

api.add_resource(Check, '/alive')
api.add_resource(Version, '/api/version')
api.add_resource(Status, '/api/status')

if __name__ == '__main__':
    port = Config.port
    debug = Config.debug
    timeout = Config.alive_timeout
    appLogger.info(f'Waiting for {timeout} sec')
    sleep(timeout)
    appLogger.info(f'Running...')

    if debug:
        app.run(host='0.0.0.0', port=port, debug=debug)
    else:
        http_server = WSGIServer(('', port), app, log=app.logger)
        appLogger.info(f"Server running on port: {port}")        
        http_server.serve_forever()
