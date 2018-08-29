import requests
import datetime
import toolbox
import re

def match_blurb(subject,array_match):
	for match in array_match:
		if re.search(match, subject):
			return True
	return False

if __name__=="__main__":

	
	array_inboxes={'FACEBOOK':["sent a message to the conversation"],
	'Easyroommate_AU':["ve just received a message from"],
	'Flatmates Notifications':["You have received a new message from"]
	}
	conn=toolbox.get_connection()
	msg_already_stored=toolbox.select_db("SELECT msg_id FROM front_emails",conn)
	exclusion_list=list(map(lambda x: x["msg_id"],msg_already_stored))
	endpoint = "https://api2.frontapp.com/inboxes"
	token=toolbox.select_db("SELECT access_token FROM api_tokens WHERE service='front'",conn)[0]["access_token"]
	headers_get = {"Authorization":"Bearer "+token,
				"Host":"api2.frontapp.com"}
	results=requests.get(endpoint,headers=headers_get).json()["_results"]
	
	ids={}
	output=[]
	
	for result in results:
		if result["name"] in array_inboxes.keys():
			ids[result["id"]]=result["name"]
	for id_inbox in ids:
		endpoint_conv="https://api2.frontapp.com/inboxes/"+id_inbox+"/conversations"
		convs=requests.get(endpoint_conv,headers=headers_get).json()["_results"]
		for conv in convs:
			conv_id=conv["id"]
			endpoint_msg="https://api2.frontapp.com/conversations/"+conv_id+"/messages"
			msgs=requests.get(endpoint_msg,headers=headers_get).json()["_results"]
			for msg in msgs:
				if msg["id"] not in exclusion_list:
					data={}
					data["inbox"]=ids[id_inbox]
					data["conv_id"]=conv_id
					data["msg_id"]=msg["id"]
					data["msg_blurb"]=msg["blurb"].replace(u"\u2018", "'").replace(u'\u202c', "'").replace(u"\u202d", " ").replace(u"\u2019", "'").replace(u'\U0001f60a'," ").replace(u'\U0001f642'," ").replace("'"," ").replace(u'\u2014',' ')
					data["created_at"]=datetime.datetime.fromtimestamp(int(msg["created_at"])).strftime('%Y-%m-%d %H:%M:%S')
					
					if(match_blurb(msg["blurb"],array_inboxes[ids[id_inbox]])):
						print(str(data))
						output.append(data)
					exclusion_list.append(msg["id"])
	toolbox.insert_batch(output,'front_emails',conn)
