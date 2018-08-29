from flask import Flask
from flask import request
import toolbox
import sys
app = Flask(__name__)
def check_authorization(headers,conn):
	bearer=headers['Authorization']
	allowed_tokens=toolbox.select_db("SELECT access_token FROM webhooks_tokens WHERE access_token='"+bearer.split(" ")[1]+"'",conn)
	print(bearer)
	if (len(allowed_tokens)==0):
		return False
	else:
		return True

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/viewings', methods=['POST'])
def login():
	if request.method == 'POST':
		headers=request.headers
		conn=toolbox.get_connection()
		if(check_authorization(headers,conn)):
			return "Hello there authenticated user"
		else:
			return "who r you"