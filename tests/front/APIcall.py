import requests
import datetime
import toolbox

if __name__="__main__":

	headers_post = {"Authorization":"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzY29wZXMiOlsiKiJdLCJpc3MiOiJmcm9udCIsInN1YiI6ImNvY29vbl9sZWFzaW5nX3B0eV9sdGQifQ.2EcizeQt3PNCEnp3LbV65VABayYUyagULDGFG_z1Fyk",
				"Host":"api2.frontapp.com",
				"Accept": "application/json",
				"Content-Type": "application/json"}
	headers_get = {"Authorization":"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzY29wZXMiOlsiKiJdLCJpc3MiOiJmcm9udCIsInN1YiI6ImNvY29vbl9sZWFzaW5nX3B0eV9sdGQifQ.2EcizeQt3PNCEnp3LbV65VABayYUyagULDGFG_z1Fyk",
				"Host":"api2.frontapp.com"}
	array_inboxes=['FACEBOOK','Easyroommate_AU','Flatmates Notifications']
	conn=toolbox.get_connection()
	msg_already_stored=toolbox.db_select("SELECT msg_id FROM front_emails",conn)
	exclusion_list=list(map(lambda x: x["msg_id"],msg_already_stored))
	endpoint = "https://api2.frontapp.com/inboxes"
	results=requests.get(endpoint,headers=headers_get).json()["_results"]

	ids={}
	output=[]
	
	for result in results:
		if result["name"] in array_inboxes:
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
					data["msg_blurb"]=msg["blurb"]
					data["created_at"]=datetime.datetime.fromtimestamp(int(msg["created_at"])).strftime('%Y-%m-%d %H:%M:%S')
					print(str(data))
					output.append(data)
					exclusion_list.append(msg["id"])
	toolbox.insert_batch(output,'front_msgs',conn)