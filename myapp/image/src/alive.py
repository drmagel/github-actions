from flask_restful import Resource

class Check(Resource):
    def get(self):
        return {'Status': 'OK'}, 200