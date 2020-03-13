#import depedency for flask
from flask import Flask

#create flask application instance
app = Flask(__name__)

#create a route for handling request
@app.route('/')
def hello_world():
    return 'Hello World'