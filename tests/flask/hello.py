from flask import Flask
from flask import request
import toolbox
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/viewings', methods=['POST'])
def login():
    if request.method == 'POST':
        head=request.headers['access_token']
        

@app.route('/houses', methods=['POST'])
def login():
    if request.method == 'POST':
        head=request.headers['access_token']
        