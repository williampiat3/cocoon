import front_tb
import requests
import arthur
import formstack
import datetime
import toolbox
import json

conn=toolbox.get_connection()
front=front_tb.Front(conn)
data_email_roommates={
		"first_name":"bit",
		"address":"Auldnoir",
		"nationality":"Skycitizen",
		"age":"19",
		"sex":"M",
		"occupation":"God",
		"phone":"+61613",
		"email":"william.piat3@gmail.com",
		"description":"no point",
		}
for i,value in enumerate("0,1,2,3,4,5,6,7,8,9,10".split(',')):
	data_email_roommates["p"+str(i)] = value

with open("/home/will/Documents/GitHub/cocoon/cocoon_app/templates/tenants_information.html","r") as file:
	template_t=file.read()
	template_t=template_t.format(**data_email_roommates)
front.send_email(["william.piat3@gmail.com"],"Introducing a future possible housemate",template_t)
front.send_email(["william.piat3@gmail.com"],"Submission notice","Thank you for filling the information form. Now your tenancy is pending, you will receive an email in case your subscription is accepted. Please be reminded to send you bond to the account provided in the last email. Cocoon")
	