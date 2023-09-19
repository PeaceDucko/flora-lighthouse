#%%
from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_cors import CORS, cross_origin
import json
import pandas as pd
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import os
from functions import *
from lians import *
import re

#%%

app = Flask(__name__)
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'
app.debug = True

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

@api.route('/feature', doc={"description": "Features"})
class Feature(Resource):
    @cross_origin(supports_credentials=True)
    @api.doc(responses={
        200: 'Success'
    })
    def get(self):
        # Get label names csv
        path = Path("../data/label_names.csv")

        df = pd.read_csv(path)

        # Change column names for API readability
        df.columns = ["id", "shortname", "description"]

        data = df.to_dict(orient="records")

        result = {
            'data':data
        }
            
        return {
            'statusCode': 200,
            'headers': headers,
            'body': result
        }

    def post(self):
        content_type = request.headers.get('Content-Type')
        data = request.data
        data = data.decode("utf-8")

        users = []

        BasePath_3 = r"../data/flora Data/Study 3/"
        files_3 = os.listdir(BasePath_3)

        # getting the combined files
        combined_files = []
        for x in files_3:
            if "combined.csv" in x:
                combined_files.append(x)

        BasePath_f = r"../data/Future/Process label/"
        files_f = os.listdir(BasePath_f)
        for f in files_f:
            users.append(load_process_features_study_f(BasePath_f, f))

        for c_file in combined_files:
            users.append(load_process_features_study_3(BasePath_3, c_file))

        user_df = pd.concat(users)

        # print(list(user_df.columns))

        user_df['Username'] = user_df['Username'].str.replace('.combined.csv','')

        # here i set all features to be chosen for clustering in future this should be chosen by user
        features_chosen = pd.read_csv(r"../data/label_names.csv")
        features_chosen = json.loads(data)

        reduced_df = reduce_df(user_df, features_chosen)

        labels = cluster(reduced_df)
        X = create_X(reduced_df, labels)

        # # here i make a list where the index is the class and the contents is a list of what each class is distinctive at
        # important_features_lst = important_features(reduced_df, labels)

        # # making a dictionary that explains each pattern label
        # features_explained = explain(important_features_lst)

        reduced_df = reduced_df.reset_index(drop=True) # Reset index to work with concat

        result_df = pd.concat([X, reduced_df['Username']], axis=1)
        result_df.rename(columns={"Username": "username"}, inplace=True)

        result = dict()
        for label in sorted(result_df['label'].unique()):
            label = int(label)

            result[label] = {
                'users':result_df[result_df['label'] == label].drop(columns=['label']).to_dict(orient="records")
            }

        result = {
            'content_type':content_type,
            'data':result
        }

        return {
            'statusCode': 200,
            'headers': headers,
            'body':result
        }

@api.route('/result', doc={"description": "Results"})
class Result(Resource):
    @cross_origin(supports_credentials=True)
    @api.doc(responses={
        200: 'Success'
    })
    def get(self):
        content_type = request.headers.get('Content-Type')
        data = request.data
        data = data.decode("utf-8")
        
        print(request.url)
        
        print("Parsed data")
        o = urlparse(request.url)
        query = parse_qs(o.query)
        
        print(query['studentNumber'])
        studentNumber = query['studentNumber']

        # loading the maps for colour and labels of each pattern id
        sub_dict, main_dict, color_dict = load_label_meanings()


        # =============================================================================== username is set here
        user_name = studentNumber[0].replace('_', '')
        print(user_name)
        # user_name = "fsh" + str(numbers)

        # making the pattern dataframe
        try:
            df, time_scaler = load_process_features_study_f(BasePath_f + "processLabel/", sub_dict, main_dict, color_dict, user_name + "_pattern.csv")
        except Exception as e:
            print(e)
            return {
                'statusCode': 400,
                'headers': headers            
            }
            pass

        # making the data series and percentages for meta and cog
        m_series, m_perc, m_personal = create_series(df, "Metacognition", time_scaler)
        c_series, c_perc, c_personal = create_series(df, "Cognition", time_scaler)
        series, perc, personal = create_series(df, "Combined", time_scaler)

        # loading in the pre, post and learning gain results
        tests = results(BasePath_f + "test/", user_name)

        # creating the dictionary for personal feedback
        personal = m_personal
        personal.update(c_personal)

        # getting the essay score:
        spiderdata = susanneScript(user_name)

        # # ====================================================================================================
        # # this is how the json should look really
        # print("meta:")
        # print(m_series)
        # print(", m_perc:")
        # print(m_perc)
        # print(", cog:")
        # print(c_series)
        # print(", c_perc:")
        # print(c_perc)
        # print(", pplg:")
        # print(tests)
        # print(", personal:")
        # print(personal)
        # print(", spiderData:") # has order of es_source_overlap, mean_cohesion, word_countrel
        # print(spiderdata)

        result = {
            'meta':m_series,
            'm_perc':m_perc,
            'cog':c_series,
            'c_perc':c_perc,
            'pplg':tests,
            'personal':personal,
            'spiderData':spiderdata,
            'combined_perc': perc,
            'combined_series': series,
        }

        return {
            'statusCode': 200,
            'headers': headers,
            'body': result
        }

if __name__ == "__main__":
    app.run(port=5001)

#%%


#%%
