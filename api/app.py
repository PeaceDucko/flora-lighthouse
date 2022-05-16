from flask import Flask
from flask_restx import Api, Resource, fields
import json

app = Flask(__name__)
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'

api = Api(app, 
    version='0.1', 
    title='FLORA Lighthouse API',
    description='',
    doc='/docs/'
)

@api.route('/')
class Home(Resource):
    def get(self):
        return 'This is my first API call!'

@api.route('/cluster', doc={"description": "Get cluster points"})
class Cluster(Resource):
    @api.doc(responses={
        200: 'Success'
    })
    def get(self):
        # Opening JSON file
        f = open('result.json')

        # returns JSON object as
        # a dictionary
        data = json.load(f)

        return data



if __name__ == "__main__":
    app.run(debug=True)