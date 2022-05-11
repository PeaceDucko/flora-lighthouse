from flask import Flask
import json
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'This is my first API call!'

@app.route('/cluster', methods=["GET"])
def cluster():
    # Opening JSON file
    f = open('result.json')

    # returns JSON object as
    # a dictionary
    data = json.load(f)

    return data



if __name__ == "__main__":
    app.run(debug=True)