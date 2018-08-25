import requests
import toolbox
import datetime
import json

def get_coming_time_interval():
	now=datetime.datetime.now()
	date_str=now.strftime('%d-%m-%Y')
	date_end= (now+ datetime.timedelta(days=730)).strftime('%d-%m-%Y')
	return date_str+' - '+date_end


class Arthur():

	def __init__(self,conn):
		self.creds=toolbox.select_db("SELECT * FROM api_tokens WHERE service='arthur'",conn)[0]
		self.conn=conn
		try:
			self.get_current_properties()
		except KeyError:
			self.refresh_tokens()
			self.creds=toolbox.select_db("SELECT * FROM api_tokens WHERE service='arthur'",conn)[0]
		self.persons=self.get_persons()

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
		print(response)
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
		response=requests.post(endpoint,headers=headers,data=json.dumps(data))
		print(response.text)
		return response.json()

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

	def get_unit(self,unit_id):
		endpoint="https://api.arthuronline.co.uk/units/view/{unit_id}.json".format(unit_id=str(unit_id))
		return self.get_request_headed(endpoint)

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
		print(endpoint)
		return self.post_request_headed(endpoint,data)
	def attribute_tenant_to_tenancy(self,id_tenancy,data):
		endpoint="https://api.arthuronline.co.uk/renters/add/tenancy_id:{}.json".format(str(id_tenancy))
		return self.post_request_headed(endpoint,data)
	
	def get_tenancy(self,id_tenancy):
		endpoint="https://api.arthuronline.co.uk/tenancies/view/{}.json".format(id_tenancy)
		return self.get_request_headed(endpoint)

	def get_tenant(self,id_tenant):
		endpoint="https://api.arthuronline.co.uk/renters/view/{}.json".format(id_tenant)
		print(endpoint)
		return self.get_request_headed(endpoint)


	def update_tenancy(self,id_tenancy,data):
		endpoint="https://api.arthuronline.co.uk/tenancies/edit/{}.json".format(str(id_tenancy))
		
		return self.put_request_headed(endpoint,data=data)

	def get_tasks(self,filtered={}):
		endpoint="https://api.arthuronline.co.uk/tasks/index.json"
		return self.get_all_pages_data(endpoint,filtered=filtered)

	def create_task(self,name,description, **kwargs):
		endpoint="https://api.arthuronline.co.uk/tasks/add.json"
		data={"description":description,
		"assign_to_person_id":int(self.persons[name]),
		'Task.tag_cache':'undefined'
		}
		for key in kwargs:
			data[key]=kwargs[key]
		return self.post_request_headed(endpoint,data)

	def update_tenancies_status(self):
		current_units=toolbox.select_db("SELECT * FROM ops.tenants_history WHERE arthur_id IS NOT NULL AND state='OK' AND NOW()<outgoing_date",self.conn)
		for unit in current_units:
			tenancy=self.get_tenancy(unit["arthur_id"])
			room=tenancy["data"]["unit_address_name"].split(" ")[1]
			unit_id=tenancy["data"]["Unit"]["id"]
			unit_arthur=self.get_unit(unit_id)
			current_id_house=toolbox.select_specific("ops.houses",{"arthur_id":str(unit_arthur["data"]["property"]["id"])},self.conn)["id"]
			new_status=tenancy["data"]["status"]
			rent_tenant=int(tenancy["data"]["rent_amount"].split(".")[0])
			if  new_status.lower() == "rejected" :
				print("tenant rejected")
				toolbox.update_targeted({'state':new_status.lower()},"ops.tenants_history",{"arthur_id":unit["arthur_id"]},self.conn)
		 		continue
		 	if new_status.lower() == "approved" and unit["incoming_date"]< datetime.datetime.now().date() and unit["outgoing_date"]>datetime.datetime.now().date():
		 		self.update_tenancy(unit["arthur_id"],{"status":"current"})
		 	if new_status.lower() in ["approved","current","periodic","ending"]:
		 		print("update intel")
		 		try:
		 			data_update = {'tenant_nr':"Tenant "+str(room),
		 			'incoming_date':tenancy["data"]["move_in_date"],
		 			#'outgoing_date':tenancy["data"]["move_out_date"]
		 			'rent':rent_tenant,
		 			"house_id":str(current_id_house)
		 			}
		 			if tenancy["data"]["move_out_date"] != None:
		 				data_update["outgoing_date"]=tenancy["data"]["move_out_date"]
		 			toolbox.update_targeted(data_update,"ops.tenants_history",{"arthur_id":unit["arthur_id"]},self.conn)
		 		except:
		 			pass
		 		continue
		pending_units=toolbox.select_db("SELECT * FROM ops.tenants_history WHERE arthur_id IS NOT NULL AND state='pending'",self.conn)
		for unit in pending_units:
			tenancy=self.get_tenancy(unit["arthur_id"])
			new_status=tenancy["data"]["status"]
			print(new_status)
			if  new_status.lower() == "rejected" :
				print("tenant rejected")
				toolbox.update_targeted({'state':new_status.lower()},"ops.tenants_history",{"arthur_id":unit["arthur_id"]},self.conn)
		 		continue
			if new_status.lower() == "approved":
				toolbox.update_targeted({'state':'OK'},"ops.tenants_history",{"arthur_id":unit["arthur_id"]},self.conn)
				print((unit["incoming_date"]-datetime.datetime.now().date()).days)
				if (unit["incoming_date"]-datetime.datetime.now().date()).days< 7.:
					#create task for checking contracts now
					print(self.create_task('Cocoon',"URGENT TODAY: check signature and prepare incoming report with the tenant ",date_due=datetime.datetime.now().strftime('%Y-%m-%d'),tenancy_id=unit["arthur_id"]))
				else:
					#create task for checking the contracts
					moving_in_date=datetime.datetime.strptime(tenancy["data"]["move_in_date"], "%Y-%m-%d" )
					event_date=(moving_in_date- datetime.timedelta(days=7)).strftime('%d-%m-%Y')
					print(self.create_task('Cocoon',"Please check signature and organise  incoming procedure for "+event_date,date_due=event_date,tenancy_id=unit["arthur_id"]))
		return True

	def update_tenant_information(self):
		renters=self.get_renters()
		match=dict(map(lambda x: (x["tenancy_id"],{"first_name":x["first_name"],"last_name":x["last_name"],"email":x["email"],"phone":x["mobile"]}),renters))
		for renter in match:
			tenancies=toolbox.select_db("SELECT * FROM ops.tenants_history WHERE arthur_id='{}'".format(renter),self.conn)
			id_tenant=None
			for tenancy in tenancies:
				id_tenant=tenancy["tenant_id"]
				break
			if id_tenant!=None:
				toolbox.update_targeted(match[renter],"ops.tenants",{"id":id_tenant},self.conn)

	def get_renters(self,filtered={}):
		endpoint="https://api.arthuronline.co.uk/renters/index.json"
		return self.get_all_pages_data(endpoint,filtered=filtered)


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
	def get_persons(self):
		return dict(map(lambda x: (x["Profile"]["first_name"],x["Person"]["id"]),self.get_all_pages_data("https://api.arthuronline.co.uk/people/index.json")))





if __name__=='__main__':
	conn=toolbox.get_connection()
	arthur=Arthur(conn)
	# #data_ao={"status": "prospective", "move_out_date": "2018-01-17", "rent_amount_weekly": "undefined", "duration": "undefined", "break_clause": "2018-01-17", "tenancy_start": "2018-07-17", "registered_deposit_date": "2018-07-17", "rent_frequency": "weekly", "registered_deposit": "700", "tenancy_end": "2018-01-17", "rent_amount": "350", "Tenancy.tag_cache": "undefined", "status_alias": "undefined", "move_in_date": "2018-07-17", "rent_frequency_id": "undefined"}
	# InformationTenancies=list(map(lambda x: (x["id"],x["Unit"]["Profile"]["address"],x["renters"]),arthur.get_current_tenancies()))
	# for IdTenancy,Address,Name in InformationTenancies:
	# 	try:
	# 		FirstName,LastName=Name.split()
	# 		id_tenant=toolbox.select_db("SELECT id FROM tenants WHERE first_name='{0}' AND last_name='{1}'".format(FirstName,LastName),conn)[0]["id"]
	# 		query="UPDATE tenants_history SET arthur_id='{0}' WHERE tenant_id={1}".format(str(IdTenancy),id_tenant)
	# 		print(query)
	# 		toolbox.update_db(query,conn)
	# 	except:
	# 		continue
	# 	"""UPDATE tenants_history SET"
	# 	toolbox.update_db(query,conn)"""
	arthur.update_tenancies_status()
	arthur.update_tenant_information()
	