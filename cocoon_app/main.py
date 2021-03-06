from flask import Flask, render_template, request,abort
import toolbox
import MySQLdb
import json
from flask import jsonify
from flask_api import status
import front_tb
import requests
import arthur
import formstack
import datetime
import logging

def check_authentication(Authorization):
	conn=toolbox.get_connection()
	data=toolbox.select_db("SELECT access_token FROM ops.webhooks_tokens;",conn)
	conn.close()
	list_bearer=list(map(lambda x: "Bearer "+x["access_token"],data))
	print(list_bearer)
	if Authorization in list_bearer:
		return True
	else:
		raise InvalidUsage('Authentication failed', status_code=410)

def get_success(answer={}):
	message={"status":"success"}
	if answer != {}:
		message["data"]=answer
	return json.dumps(message)

class InvalidUsage(Exception):
		status_code = 400

		def __init__(self, message, status_code=None, payload=None):
				Exception.__init__(self)
				self.message = message
				if status_code is not None:
						self.status_code = status_code
				self.payload = payload

		def to_dict(self):
				rv = dict(self.payload or ())
				rv['message'] = self.message
				return rv


app = Flask(__name__)

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
		response = jsonify(error.to_dict())
		response.status_code = error.status_code
		return response

# @app.route('/form')
# def form():
# 	return render_template('form.html')

# @app.route('/submitted', methods=['POST'])
# def submitted_form():
# 	name = request.form['name']
# 	email = request.form['email']
# 	site = request.form['site_url']
# 	comments = request.form['comments']
# 	return render_template('submitted_form.html',name=name,email=email,site=site,comments=comments)



@app.route('/formstack_deposit',methods=['POST'])
def db_display():
	#head=request.headers['Authorization']
	#if check_authentication(head):
	conn=toolbox.get_connection()
	front=front_tb.Front(conn)
	intel=request.get_json()
	id_sub=intel["UniqueID"]
	email=intel["Email"]
	#hard coded shit I know
	form=formstack.Formstack(conn)
	initial_data=form.get_submission(id_sub)
	dict_initial=dict(map(lambda x: (x['field'],x['value']),initial_data['data']))
	link="https://cocoon.formstack.com/forms/tenant_information?id_sub={0}".format(str(id_sub))
	data_email_propective_tenant={
	"link":link,
	"last_name":dict_initial["64515438"],
	"first_name":dict_initial["64515437"],
	"address":dict_initial["64515442"],
	"bond":str(2*int(dict_initial["64515461"])),
	"rent":str(int(dict_initial["64515461"])),
	"incoming_date":dict_initial["64515462"],
	}
	try:
		query=[]
		house_info=toolbox.select_db("SELECT * FROM ops.houses WHERE address='"+dict_initial["64515442"]+"'",conn)[0]
		query.append("SELECT t.first_name, t.nationality,  TIMESTAMPDIFF(year,t.birthdate, now() ) AS age,t.sex,t.occupation,t.phone,t.email")
		query.append("FROM ops.tenants AS t INNER JOIN ops.tenants_history AS th ON t.id=th.tenant_id")
		query.append("WHERE th.house_id='"+house_info["id"]+"' AND '"+ dict_initial["64515462"]+"' BETWEEN incoming_date AND outgoing_date ")
		roommates= toolbox.select_db(' '.join(query),conn)
		emails=[]
		extension=[]
		for roommate in roommates:
			emails.append(roommate["email"])
			string="<td>"+roommate["first_name"]+"</td>"
			string+="<td>"+roommate["nationality"]+"</td>"
			string+="<td>"+str(roommate["age"])+"</td>"
			string+="<td>"+roommate["sex"]+"</td>"
			string+="<td>"+roommate["occupation"]+"</td>"
			string+="<td>"+str(roommate["phone"])+"</td>"
			string+="<td>"+roommate["email"]+"</td>"
			extension.append("<tr>"+string+"</tr>")
		with open("templates/deposit_email.html","r") as file:
			template=file.read()

		template=template.format(**data_email_propective_tenant)
		template=template.replace("<h3></h3>",' '.join(extension))
	except Exception, e:
		front.send_email(["marcus@cocoon.ly"],"issue",str(e))

	#front.send_email([dict_initial["64515456"]],"Finishing your application for "+dict_initial["64515442"],"Please follow this link to finish your application: \n"+link)
	front.send_email([dict_initial["64515456"]],"ACTION NEEDED Complete this form NOW so we can approve your tenancy + info within",template)
	return get_success()

@app.route('/formstack_tenant_information',methods=['POST'])
def big_daddy():
	logging.debug('start')
	conn=toolbox.get_connection()
	front=front_tb.Front(conn)
	try:
		arthur_tb=arthur.Arthur(conn)
		form=formstack.Formstack(conn)
		logging.debug('passed1')
	except Exception, e:
		front.send_email(["marcus@cocoon.ly"],"issue2",str(e))
		logging.debug("a"+str(e))
	try:
		intel=request.get_json()
		logging.debug(intel["id_sub"])
		initial_data=form.get_submission(intel["id_sub"])
		dict_initial=dict(map(lambda x: (x['field'],x['value']),initial_data['data']))
		tenant_data=form.get_submission(intel["UniqueID"])
		dict_tenant=dict(map(lambda x: (x['field'],x['value']),tenant_data['data']))
		data_tenant={ #old fields
					"first_name":MySQLdb.escape_string(dict_initial["64515437"].encode('ascii', 'ignore')),
					"last_name":MySQLdb.escape_string(dict_initial["64515438"].encode('ascii', 'ignore')),
					"nationality":MySQLdb.escape_string(dict_tenant["64706970"].encode('ascii', 'ignore')),
					"occupation":MySQLdb.escape_string(dict_tenant["64811196"].encode('ascii', 'ignore')),
					"email":dict_initial["64515456"].encode('ascii', 'ignore'),
					"birthdate":dict_tenant["64707048"],
					"phone":dict_initial["64515457"].encode('ascii', 'ignore'),
					"sex":dict_initial["64515441"],
					"private":MySQLdb.escape_string(dict_initial["64515459"].encode('ascii', 'ignore')),
					"share_with_other_gender":dict_initial["64515460"],
					"assignment_type": "app engine",
					#new fields
					"visa_type":dict_tenant["64706778"],
					"employment_status":dict_tenant["64706801"],
					"employment_area":dict_tenant["64706803"].encode('ascii', 'ignore'),
					#"company_name":dict_tenant["64706826"],
					"coordinates":",".join(list(map(lambda x: x.split(" = ")[1],dict_tenant["64706779"].split("\n")))),
					#"description":dict_tenant["64707081"],
					#"emergency_name":dict_tenant["64707109"].split("\n")[0].split(" = ")[1]+" "+dict_tenant["64707109"].split("\n")[1].split(" = ")[1],
					#"emergency_email":dict_tenant["64707111"],
					#"emergency_phone":dict_tenant["64707114"],
					#"emergency_relation":dict_tenant["64707116"]
		}
		logging.debug('passed2')
		try:
			data_tenant["emergency_name"]=MySQLdb.escape_string(dict_tenant["64707109"].split("\n")[0].split(" = ")[1]+" "+dict_tenant["64707109"].split("\n")[1].split(" = ")[1].encode('ascii', 'ignore'))
		except KeyError:
			pass
		try:
			data_tenant["emergency_email"]=dict_tenant["64707111"].encode('ascii', 'ignore')
		except KeyError:
			pass
		try:
			data_tenant["emergency_phone"]=dict_tenant["64707114"].encode('ascii', 'ignore')
		except KeyError:
			pass
		try:
			data_tenant["company_name"]=MySQLdb.escape_string(dict_tenant["64706826"].encode('ascii', 'ignore'))
		except KeyError:
			pass
		try:
			data_tenant["emergency_relation"]=MySQLdb.escape_string(dict_tenant["64707116"].encode('ascii', 'ignore'))
		except KeyError:
			pass
		try:
			data_tenant["description"]=MySQLdb.escape_string(''.join([i if ord(i) < 128 else ' ' for i in dict_tenant["64707081"].replace("'"," ").replace(u'\xc1',"a").replace(u'\xe3',"a").replace(u'\U0001f601',"").replace(u'\u202d'," ")]).encode('ascii', 'ignore'))
		except KeyError:
			pass

		logging.debug(data_tenant)
		house_info=toolbox.select_db("SELECT * FROM ops.houses WHERE address='"+dict_initial["64515442"]+"'",conn)[0]
		
		data_ao={'status':'prospective',
				'status_alias':'undefined',
				'tenancy_start':dict_initial["64515462"],
				'tenancy_end':dict_initial["64515463"],
				'duration':'undefined',
				'break_clause':dict_initial["64515463"],
				'move_in_date':dict_initial["64515462"],
				'move_out_date':dict_initial["64515463"],
				'registered_deposit':str(int(dict_initial["64515461"])*2),
				'registered_deposit_date':dict_initial["64515462"],
				'rent_amount':str(dict_initial["64515461"]),
				'rent_frequency_id':'5',
				'rent_frequency':'weekly',
				'rent_amount_weekly':'undefined',
				'Tenancy.tag_cache':'undefined'}
		logging.debug('passed3')
	except Exception, e:
		front.send_email(["marcus@cocoon.ly"],"issue1",str(e))
		logging.debug("b"+str(e))
	try:
		logging.debug(dict_initial["64515437"])
		logging.debug(dict_initial["64515438"])
		logging.debug(dict_initial["64515456"])
		intel_possible_tenant=toolbox.select_specific("ops.tenants",{"first_name":dict_initial["64515437"],"last_name":dict_initial["64515438"],"email":dict_initial["64515456"]},conn)
		logging.debug('ok1b')
		if {}!=intel_possible_tenant:
			# GA 20181107 added "rent": int(dict_initial["64515461"]) as search parameter to cover the case where a tenant stays in the same room but agrees to pay a new price
			# and therefore needs a new contract
			logging.debug('ok2')
			logging.debug(intel_possible_tenant["id"])
			possible_tenancy=toolbox.select_specific("ops.tenants_history",{"tenant_id":intel_possible_tenant["id"],"rent": int(dict_initial["64515461"])},conn)
			logging.debug('ok3')
			if {}!=possible_tenancy:
				if possible_tenancy["house_id"] != house_info["id"] or possible_tenancy["tenant_nr"] != dict_initial["64515458"]:
					pass
					#need to create tenancy but not the tenant then
				else:
					#ignoring duplicate
					return get_success()
			else:
				pass
				#need to create tenancy but not the tenant then
		else:
			#creating brand new tenant
			logging.debug('bef_ok4')
			toolbox.insert_batch([data_tenant],"ops.tenants",conn)
			logging.debug('ok4')
		intel_ao=arthur_tb.add_tenancy(data_ao,house_info["arthur_id"],dict_initial["64515458"])
		logging.debug('passed4')
	except Exception, e:
		front.send_email(["marcus@cocoon.ly"],"issue2",str(e))
		logging.debug("c"+str(e))
	try:
		data_history={#old fields
					"tenant_id":toolbox.select_specific("ops.tenants",{"first_name":dict_initial["64515437"],"last_name":dict_initial["64515438"],"email":dict_initial["64515456"]},conn)["id"],
					"tenant_nr":dict_initial["64515458"],
					"house_id":house_info["id"],
					"incoming_date":dict_initial["64515462"],
					"outgoing_date":dict_initial["64515463"],
					"rent":int(dict_initial["64515461"]),
					"commitment_fees":0,
					"state":"pending",
					"multiple_booking":dict_initial["64515459"],
					"agent":dict_initial["64515465"],
					"agent_signature":dict_initial["64515466"],
					"arthur_id":str(intel_ao["data"]["id"])
					}
		data_ao_tenant={"first_name":dict_initial["64515437"],
					"last_name": dict_initial["64515438"],
					"email": dict_initial["64515456"],
					"mobile": dict_initial["64515457"]}
		logging.debug('passed5')
	except Exception, e:
		front.send_email(["marcus@cocoon.ly"],"issue3",str(e))
		logging.debug("c"+str(e))
	try:
		returns=arthur_tb.attribute_tenant_to_tenancy(intel_ao["data"]["id"],data_ao_tenant)
		toolbox.insert_batch([data_history],"ops.tenants_history",conn)
		logging.debug('passed6')
	except Exception, e:
		front.send_email(["marcus@cocoon.ly"],"issue3",str(e))
		logging.debug("d"+str(e))
	try:
		query=[]
		query.append("SELECT t.first_name, t.nationality,  TIMESTAMPDIFF(year,t.birthdate, now() ) AS age,t.sex,t.occupation,t.phone,t.email")
		query.append("FROM ops.tenants AS t INNER JOIN ops.tenants_history AS th ON t.id=th.tenant_id")
		query.append("WHERE th.house_id='"+house_info["id"]+"' AND '"+ dict_initial["64515462"]+"' BETWEEN incoming_date AND outgoing_date ")
		roommates= toolbox.select_db(' '.join(query),conn)
		emails=list(map(lambda x: x['email'],roommates))
		data_email_roommates={
		"first_name":data_tenant["first_name"],
		"address":dict_initial["64515442"],
		"nationality":data_tenant["nationality"],
		"age":str((datetime.datetime.today()-datetime.datetime.strptime(data_tenant["birthdate"], "%Y-%m-%d" )).days//365),
		"sex":data_tenant["sex"],
		"occupation":data_tenant["occupation"],
		"phone":data_tenant["phone"],
		"email":data_tenant["email"],
		"description":data_tenant["description"],
		}
		logging.debug('passed7')
	except Exception, e:
		front.send_email(["marcus@cocoon.ly"],"issue4",str(e))
		logging.debug("e"+str(e))
	try:
		for i,value in enumerate(data_tenant["coordinates"].split(',')):
			data_email_roommates["p"+str(i)] = value
		logging.debug('passed8')
	except Exception, e:
		front.send_email(["marcus@cocoon.ly"],"issue5",str(e))
		logging.debug("f"+str(e))
	try:
		with open("templates/tenants_information.html","r") as file:
			template_t=file.read()
			template_t=template_t.format(**data_email_roommates)
		front.send_email(emails,"Introducing a future possible housemate",template_t)
		front.send_email([dict_initial["64515456"]],"Submission notice","Thank you for filling the information form. Now your tenancy is pending, you will receive an email in case your subscription is accepted. Please be reminded to send you bond to the account provided in the last email. Cocoon")
		logging.debug('passed9')
		return get_success()
	except Exception, e:
		front.send_email(["marcus@cocoon.ly"],"issue",str(e))
		logging.debug("g"+str(e))

