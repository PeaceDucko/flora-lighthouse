from flask import Flask
from flask_restx import Api, Resource, fields
from flask_cors import CORS, cross_origin
import json

app = Flask(__name__)
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'

CORS(app, support_credentials=True)

api = Api(app, 
    version='0.1', 
    title='FLORA Lighthouse API',
    description='',
    doc='/docs/'
)

headers = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Credentials': True,
      'Content-Type':'application/json'
    }

@api.route('/home', doc={"description": "API homepage"})
class Home(Resource):
    @api.doc(responses={
        200: 'Success'
    })
    def get(self):
        return 'This is my first API call!'

@api.route('/cluster', doc={"description": "Get cluster points"})
class Cluster(Resource):
    @cross_origin(supports_credentials=True)
    @api.doc(responses={
        200: 'Success'
    })
    def get(self):
        # Opening JSON file
        f = open('result.json')

        # returns JSON object as
        # a dictionary
        data = json.load(f)

        result = {
            'data':data
        }
            
        return {
            'statusCode': 200,
            'headers': headers,
            'body': result
        }



if __name__ == "__main__":
    app.run(debug=True)