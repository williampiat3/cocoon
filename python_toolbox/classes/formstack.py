import requests
import datetime
import toolbox
import re
import json

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
	def get_fields_form(self,id):
		endpoint="https://www.formstack.com/api/v2/form/{0}.json".format(str(id))
		response=self.get_request_headed(endpoint)
		return dict(map(lambda x: (x["id"],x["label"]),response["fields"]))

if __name__=='__main__':
	conn=toolbox.get_connection()
	form=Formstack(conn)
	tenant_data=form.get_submission(435897919)
	dict_tenant=dict(map(lambda x: (x['field'],x['value']),tenant_data['data']))
	print(dict_tenant["64706779"])
	print(",".join(list(map(lambda x: x.split(" = ")[1],dict_tenant["64706779"].split("\n")))))

