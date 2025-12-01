from datetime import datetime
from flask_restful import Resource
from config import Config

class Status(Resource):
    def get(self):
        resp = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "timeout": Config.alive_timeout,
            "version": Config.version
        }
        return resp, 200

class Version(Resource):
    def get(self):
        return {"version": Config.version}, 200