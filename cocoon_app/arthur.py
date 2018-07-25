import requests
import toolbox
import datetime
import json
import requests_toolbelt.adapters.appengine

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()


def get_coming_time_interval():
	now=datetime.datetime.now()
	date_str=now.strftime('%d-%m-%Y')
	date_end= (now+ datetime.timedelta(days=730)).strftime('%d-%m-%Y')
	return date_str+' - '+date_end


class Arthur():

	def __init__(self,conn):
		self.creds=toolbox.select_db("SELECT * FROM ops.api_tokens WHERE service='arthur'",conn)[0]
		self.conn=conn
		try:
			self.get_current_properties()
		except KeyError:
			self.refresh_tokens()
			self.creds=toolbox.select_db("SELECT * FROM ops.api_tokens WHERE service='arthur'",conn)[0]

	def refresh_tokens(self):
		endpoint='https://auth.arthuronline.co.uk/oauth/token'

		headers={
		'Cache-Control': 'no-cache',
		'content-type': 'application/x-www-form-urlencoded'}

		data={
		'refresh_token':self.creds['refresh_token'],
		'client_id':self.creds['client_id'],
		'client_secret':self.creds['client_secret'],
		'grant_type':'refresh_token'
		}

		response=requests.post(endpoint,data=data,headers=headers).json()
		toolbox.update_targeted({'access_token':response['access_token'],'refresh_token':response['refresh_token']},'api_tokens',{'service':'arthur'},self.conn)
		return {'access_token':response['access_token'],'refresh_token':response['refresh_token']}

		
	def get_request_headed(self,endpoint,payload={},filtered={}):
		headers={"X-ENTITYID": self.creds['entity_id'],
				"Authorization": "Bearer "+self.creds['access_token'],
				"Content-Type": "application/json",
				"Cache-Control": "no-cache"}
		if (filtered!={}):
			extension="/filter:"
			array=[]
			for key in filtered:
				array.append(key+":"+filtered[key])
			extension+='/filter:'.join(array)
		else:
			extension=""
		response=requests.get(endpoint[:-5]+extension+".json",headers=headers,params=payload).json()
		return response

	def get_all_pages_data(self,endpoint,payload={},filtered={}):
		endpoint_cut=endpoint[:-5]
		formatable_string="/page:{0}"
		i=1
		output=[]
		last_page=True
		while last_page:
			intel=self.get_request_headed(endpoint_cut+formatable_string.format(str(i))+".json",payload=payload,filtered=filtered)
			output+=intel["data"]
			last_page=intel["pagination"]["nextPage"]
			i+=1
		return output

	def post_request_headed(self,endpoint,data):
		headers={"X-ENTITYID": self.creds['entity_id'],
				"Authorization": "Bearer "+self.creds['access_token'],
				"Content-Type": "application/json",
				"Cache-Control": "no-cache"}
		return requests.post(endpoint,headers=headers,data=json.dumps(data)).json()

	def put_request_headed(self,endpoint,data):
		headers={"X-ENTITYID": self.creds['entity_id'],
				"Authorization": "Bearer "+self.creds['access_token'],
				"Content-Type": "application/json",
				"Cache-Control": "no-cache"}
		return requests.put(endpoint,headers=headers,data=json.dumps(data)).json()

	def get_current_tenancies(self):
		endpoint="https://api.arthuronline.co.uk/tenancies/index.json"
		filtered={"_tenancy_end":get_coming_time_interval()}
		return self.get_all_pages_data(endpoint,filtered=filtered)

	def get_current_units(self,filtered={}):
		endpoint="https://api.arthuronline.co.uk/units/index.json"
		return self.get_all_pages_data(endpoint,filtered=filtered)

	def get_current_properties(self):
		endpoint="https://api.arthuronline.co.uk/properties/index.json"
		return self.get_all_pages_data(endpoint)

	def get_coming_viewings(self):
		endpoint="https://api.arthuronline.co.uk/viewings/index.json"
		filtered={"_tenancy_end":get_coming_time_interval()}
		return self.get_all_pages_data(endpoint,filtered=filtered)

	def add_tenancy(self,data,house_ao_id,tenant_nr):
		intel_units=self.get_current_units(filtered={"property_id":house_ao_id})
		for unit in intel_units:
			if unit["name"].split(",")[0] == "Bed "+tenant_nr.split(" ")[1]:
				out_unit=unit
				break
		endpoint="https://api.arthuronline.co.uk/tenancies/add/unit_id:{}.json".format(out_unit["id"])
		return self.post_request_headed(endpoint,data)

	def attribute_tenant_to_tenancy(self,id_tenancy,data):
		endpoint="https://api.arthuronline.co.uk/renters/add/tenancy_id:{}.json".format(str(id_tenancy))
		return self.post_request_headed(endpoint,data)
	
	def get_tenancy(self,id_tenancy):
		endpoint="https://api.arthuronline.co.uk/tenancies/view/{}.json".format(id_tenancy)
		return self.get_request_headed(endpoint)

	def update_tenancy(self,id_tenancy,data):
		endpoint="https://api.arthuronline.co.uk/tenancies/edit/{}.json".format(str(id_tenancy))
		
		return self.put_request_headed(endpoint,data=data)

	def update_tenancies_status(self):
		pending_units=toolbox.select_db("SELECT * FROM ops.tenants_history WHERE arthur_id IS NOT NULL AND state='OK' AND NOW()<outgoing_date",self.conn)
		print(pending_units)
		for unit in pending_units:
			tenancy=self.get_tenancy(unit["arthur_id"])
			new_status=tenancy["data"]["status"]
			if  new_status.lower() == "rejected" :
				print("tenant rejected")
				toolbox.update_targeted({'state':new_status.lower()},"ops.tenants_history",{"arthur_id":unit["arthur_id"]},self.conn)
		 		continue
		 	if unit["signature"]!=None and new_status.lower() == "prospective":
		 		#update status on arthur
		 		self.update_tenancy(unit["arthur_id"],{"status":"approved","renters":"test"})
		 		print("status update on arthur")
		 		continue
		 	if unit["signature"]!=None and new_status.lower() != "prospective":
		 		print("update intel")
		 		toolbox.update_targeted({'incoming_date':tenancy["data"]["move_in_date"],'outgoing_date':tenancy["data"]["move_out_date"]},"ops.tenants_history",{"arthur_id":unit["arthur_id"]},self.conn)
		 		continue
		return True



	def get_availabilities(self,limit_date=""):
		data_tenancies=self.get_current_tenancies()
		data_units=self.get_current_units()
		availabilities={}
		now=datetime.datetime.now()
		for unit in data_units:
			availabilities[unit["address"]]={
				"rent":float(unit["rent_amount"]),
				"postcode":unit["postcode"]
				}
			if (unit["current_tenant"]==None):
			 	availabilities[unit["address"]]["available"]=now

			else:
				try:
					dates_array=[]
					for tenancy in data_tenancies:
						if (tenancy["unit"]["id"]==unit['id']):
							dates_array.append(datetime.datetime.strptime( tenancy["tenancy_end"], "%Y-%m-%d" ))
					availabilities[unit["address"]]["available"]=max(dates_array)
				except ValueError:
					availabilities[unit["address"]]["available"]=now


		return availabilities