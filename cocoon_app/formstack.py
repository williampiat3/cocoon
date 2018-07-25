import requests
import datetime
import toolbox
import re
import json
import requests_toolbelt.adapters.appengine

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()

class Formstack():
	def __init__(self,conn):
		self.conn=conn
		self.creds=toolbox.select_db("SELECT * FROM ops.api_tokens WHERE service='formstack'",conn)[0]


	def get_request_headed(self,endpoint):
		get_headers={
		"Authorization":"Bearer "+self.creds["access_token"],
		"Content-Type": "application/json"
		}
		return requests.get(endpoint,headers=get_headers).json()
	def post_request_headed(self,endpoint,data):
		post_headers={
		"Content-Type":"application/json",
		"Authorization": "Bearer "+self.creds["access_token"]
		}

		return requests.post(endpoint,headers=post_headers,data=json.dumps(data)).json()

	def get_submission(self,id):
		endpoint="https://www.formstack.com/api/v2/submission/{0}.json".format(str(id))
		return self.get_request_headed(endpoint)
