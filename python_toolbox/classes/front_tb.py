import requests
import datetime
import toolbox
import re
import json

class Front():
	def __init__(self,conn):
		self.creds=toolbox.select_db("SELECT * FROM api_tokens WHERE service='front'",conn)[0]

	def send_email(self,to,subject,msg,cc=[],bcc=[]):
		endpoint="https://api2.frontapp.com/channels/{}/messages".format("cha_d5t")
		data={
		"sender_name":"Cocoon",
		"subject":subject,
		"body":msg,
		"to":to,
		"cc":cc,
		"bcc":bcc,
		"option":{
			"tags":[],
			"archive":True
		}
		}
		return self.post_request_headed(endpoint,data=data)
	def send_sms(self,to,subject,msg,cc=[],bcc=[]):
		endpoint="https://api2.frontapp.com/channels/{}/messages".format("cha_d5u")
		data={
		"sender_name":"Cocoon",
		"subject":subject,
		"body":msg,
		"to":to,
		"cc":cc,
		"bcc":bcc,
		"option":{
			"tags":[],
			"archive":True
		}
		}
		return self.post_request_headed(endpoint,data=data)


	def get_request_headed(self,endpoint):
		get_headers={
		"Authorization":"Bearer "+self.creds["access_token"],
		"Host":"api2.frontapp.com"
		}
		return requests.get(endpoint,headers=get_headers).json()
	def post_request_headed(self,endpoint,data):
		post_headers={
		"Content-Type":"application/json",
		"Authorization": "Bearer "+self.creds["access_token"],
		"Accept":"application/json"
		}

		return requests.post(endpoint,headers=post_headers,data=json.dumps(data)).json()

if __name__=='__main__':
	conn=toolbox.get_connection()
	front=Front(conn)
	#print(front.get_request_headed("https://api2.frontapp.com/channels"))
	print(front.send_email(["william.piat3@gmail.com"],"test subject","<body>Try</body>"))
	
	#print(front.send_sms(["+61467666788"],'test_api','hello there just testing front api please tell me if you received this message, thanks! William'))