from bs4 import BeautifulSoup
import requests
import toolbox
import datetime
import json
import time
import random
import unidecode

def login_in_flatmates(s):
	
	soup=BeautifulSoup(s.get("https://flatmates.com.au").text, "html5lib")
	print(soup)
	object_intel=eval(soup.find('div',attrs={'data-react-props':True})['data-react-props'].replace('null','None').replace('false','False').replace('true','True'))
	token=eval(object_intel['session'])['csrf']['token']
	post_endpoint='https://flatmates.com.au/login'
	headers={'Accept': 'application/json',
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
		'Connection': 'keep-alive',
		'Content-Length': '60',
		'Content-Type': 'application/x-www-form-urlencoded',
		'Host': 'flatmates.com.au',
		'Origin': 'https://flatmates.com.au',
		'Referer': 'https://flatmates.com.au/',
		'X-CSRF-Token': token}
	data={'email':'help@cocoon.ly',
		  'password':'SkWGBuFi9HYi'
		}
	response=s.post(post_endpoint,headers=headers,data=data)
	return s

def get_last_profiles(session,path):
	response=session.get(path)
	print(response.status_code)
	soup2=BeautifulSoup(response.text,"html5lib")
	person=soup2.find('div',{'data-react-class':"Tiles/ListingResults"})
	listing=json.loads(json.loads(person['data-react-props'])['listings'])['listings']
	return listing

def get_token(session,path):
	soup2=BeautifulSoup(session.get(path).text,"html5lib")
	
	object_intel=eval(soup2.find('div',attrs={'data-react-props':True})['data-react-props'].replace('null','None').replace('false','False').replace('true','True'))
	token=eval(object_intel['session'])['csrf']['token']
	return token
def build_message(profile,path):
	data={
	"age":str(profile["listing"]["applicant_age"][0]),
	"name":unidecode.unidecode(profile["head"]),
	}
	date_sydney=(datetime.datetime.now() +datetime.timedelta(hours=10))
	if date_sydney.hour > 15:
		data["day"]="tomorrow"
	else:
		data["day"]="today"
	date=profile['listing']['move_date']
	applicant_age=profile['listing']['applicant_age']
	number_applicant=len(applicant_age)
	applicant_name=profile['listing']['applicant_names']
	postcodes=profile['listing']['postcode']

	with open(path,'r') as file:
		msg=file.read()
	return msg.format(**data)

def send_message(session,profile,path):
	token=get_token(session,path)
	wait_random_time(15,22)
	post_endpoint="https://flatmates.com.au/conversations/create"
	headers={
	"Accept": "application/json",
	"Accept-Encoding": "gzip, deflate, br",
	"Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
	"Connection": "keep-alive",
	"Content-Length": "79",
	"Content-Type": "application/x-www-form-urlencoded",
	"Host": "flatmates.com.au",
	"Origin": "https://flatmates.com.au",
	"Referer": "https://flatmates.com.au/"+profile["link"],
	"X-CSRF-Token": token}
	data={
	"listing": "PERSON",
	"listing_id": str(profile["listing"]["id"]),
	"member_id": str(profile["memberId"]),
	"message": profile["message"]
	}
	answer=session.post(post_endpoint,headers=headers,data=data)
	print(answer.status_code)



def check_interest_profile(session,profiles,couple=False):
	#change this to match the requirements on the google doc
	# add the 21 limit on contacting tenants
	# add the one month limit after 1 month we will send a new message if need be
	#add update date

	new_profiles=[]
	for profile in profiles:

		postcodes=profile["listing"]["postcode"]
		max_rent=profile["listing"]["max_rent"]
		move_date=datetime.datetime.strptime( profile["listing"]["move_date"], "%Y-%m-%d" )
		updated_at=datetime.datetime.strptime( profile["listing"]["updated_at"].split('T')[0], "%Y-%m-%d" )
		launch_date=datetime.datetime.strptime( "2018-05-11", "%Y-%m-%d" )
		if updated_at>=launch_date:
			if not couple:
				if max_rent<551 and max_rent>=150 and move_date<(datetime.datetime.now()+ datetime.timedelta(days=21)):
					if max_rent>=150 and max_rent<=279:
						msg=build_message(profile,"/home/will/to/cheap.txt")
						#cheap message

					if max_rent>=280 and max_rent<551:
						msg=build_message(profile,"/home/will/to/middle.txt")
					new_profiles.append(profiles[profiles.index(profile)])
			 		new_profiles[-1]["message"]=msg

			else:
				if max_rent>350 and max_rent<550 and move_date<(datetime.datetime.now()+ datetime.timedelta(days=21)):
					#message_couple
					msg=build_message(profile,"/home/will/to/couple.txt")
					new_profiles.append(profiles[profiles.index(profile)])
			 		new_profiles[-1]["message"]=msg




		# profile_interest={}
		# for key in availabilities:
		# 	if availabilities[key]["postcode"] in postcodes and max_rent*1.2>availabilities[key]["rent"]:
		# 		profile_interest[key]=availabilities[key]
		# if profile_interest=={}:
		# 	continue
		# else:
		# 	msg=build_message(profile,profile_interest)
		# 	new_profiles.append(profiles[profiles.index(profile)])
		# 	new_profiles[-1]["message"]=msg

	return new_profiles

def get_exclusion_list(conn):
	former=toolbox.select_db("SELECT * FROM prospections WHERE message_sent=1",conn)
	exclusion_list=list(map(lambda x: x["link"],former))
	former=toolbox.select_db("SELECT * FROM prospections WHERE message_sent=0",conn)
	not_interesting=list(map(lambda x: x["link"],former))
	return exclusion_list,not_interesting

def upload_to_db(conn,profiles,send):
	right_format=[]
	for profile in profiles:
		agent={"name":profile["listing"]["name"],
				"link":profile["link"],
				"age":profile["listing"]["applicant_age"][0],
				"postcodes":",".join(profile["listing"]["postcode"]),
				"professions":",".join(profile["listing"]["professions"]),
				"move_date":profile["listing"]["move_date"],
				"length_stay":profile["listing"]["length_of_stay"],
				"rent":profile["listing"]["max_rent"],
				"message_sent":send}
		right_format.append(agent)
	toolbox.insert_batch(right_format,"prospections",conn,batch=100)

		
def wait_random_time(number_min,number_max):

	time.sleep(random.randint(number_min,number_max))
	return True



if __name__=='__main__':
	#wait_random_time(30*60,44*60)
	
	#some hard coded shit I don't like this but it is sure necessary
	# not check the newest member but the incoming date required 
	links=["https://flatmates.com.au/people/{0}/couple+max-31yrs+min-180+min-8-weeks+shared-room",
		"https://flatmates.com.au/people/{0}/max-31yrs+min-180+min-8-weeks+newest+shared-room",
	"https://flatmates.com.au/people/{0}/max-31yrs+min-180+min-8-weeks+share-house",
	"https://flatmates.com.au/people/{0}/max-31yrs+min-180+min-8-weeks+student-accommodation",
	"https://flatmates.com.au/people/{0}/max-31yrs+min-180+min-8-weeks+shared-room",
	"https://flatmates.com.au/people/{0}/max-31yrs+min-180+min-8-weeks+newest+share-house",
	"https://flatmates.com.au/people/{0}/max-31yrs+min-180+min-8-weeks+newest+student-accommodation",

	]
	locations=["alexandria-2015",
	"darling-harbour-2007",
	"forest-lodge-2037",
	"glebe-2037",
	"sydney-2000",
	"barangaroo-2000",
	"camperdown-2050",
	"centennial-park-2021",
	"chippendale-2008",
	"darlinghurst-2010",
	"darlington-2008",
	"erskineville-2043",
	"eveleigh-2015",
	"haymarket-2000",
	"kingsford-2032",
	"millers-point-2000",
	"moore-park-2021",
	"paddington-2021",
	"potts-point-2011",
	"pyrmont-2009",
	"randwick-2031",
	"redfern-2016",
	"rozelle-2039",
	"rushcutters-bay-2011",
	"surry-hills-2010",
	"the-rocks-2000",
	"ultimo-2007",
	"waterloo-2017",
	"woolloomooloo-2011",
	"zetland-2017"
	]
	paths=list(map(lambda x: x.format('+'.join(locations)),links))
	conn=toolbox.get_connection()
	with requests.Session() as s:
		#proxies={"http":"http://119.40.106.250:8080","https":"https://139.99.172.152:3128"}
		#s.proxies.update(proxies)
		login_in_flatmates(s)
		i=0
		for path in paths:
			print("new batch")
			if i==0:
				couple=True
			else:
				couple=False
			profiles=get_last_profiles(s,path)
			candidates=check_interest_profile(s,profiles,couple=couple)
			exclusion_list,not_interesting=get_exclusion_list(conn)
			to_exclude=[]
			for candidate in candidates:
				to_exclude.append(candidate["link"])
				if candidate["link"] in exclusion_list:
					continue
				if candidate["link"] in not_interesting:
					send_message(s,candidate,path)
					toolbox.update_targeted({"message_sent":1},"prospections",{"link":candidate["link"]},conn)
					wait_random_time(12,20)
					continue
				to_upload_to_db=[candidate]
				send_message(s,candidate,path)
				wait_random_time(15,22)
				upload_to_db(conn,to_upload_to_db,1)
			to_upload_to_db=[]
			for profile in profiles:
				if profile['link'] not in to_exclude and profile['link'] not in exclusion_list and profile['link'] not in not_interesting:
					to_upload_to_db.append(profile)
			upload_to_db(conn,to_upload_to_db,0)
			i+=1
