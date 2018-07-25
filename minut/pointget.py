import requests
import MySQLdb
endpoint = "https://api.minut.com/v1/devices/5a17b959605d0800010918c0/sound_level?start_at=2017-12-15T22:29:00"
headers_post = {"Authorization":"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOiI1YTE3NmY0M2JmYjVkMTAwMDE0ZmIwYTgiLCJyb2xlcyI6WyJtaW51dCJdLCJvcmdJZCI6Im1pbnV0Iiwic2NvcGUiOiIiLCJpYXQiOjE1MTI0NzczNzUsImV4cCI6MTUxMjQ4MDk3NSwiaXNzIjoiTWludXQsIEluYy4ifQ.K8x3k7PAGvioTdQT8t-_8vE10cO09__berj5_qk6cng",
			"Content-Type": "application/json"}
headers_get = {"Authorization":"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOiI1YTE3NmY0M2JmYjVkMTAwMDE0ZmIwYTgiLCJyb2xlcyI6WyJtaW51dCJdLCJvcmdJZCI6Im1pbnV0Iiwic2NvcGUiOiIiLCJpYXQiOjE1MTYyOTk1NzgsImV4cCI6MTUxNjMwMzE3OCwiaXNzIjoiTWludXQsIEluYy4ifQ.blN7mGTMe1-Fgv6GvYDxLUwU2mAb4dNe_Jk3InX5g24"}
data=requests.get(endpoint,headers=headers_get).json()["values"]

try:

		conn_mysql= MySQLdb.connect(host="35.189.18.225", user="root", passwd="C0coonlyfe", db="ops" ,port=3306)

except:
		print "Connections to Mysql failed"

cursor_mysql = conn_mysql.cursor()





j=0
i=0
for mesure in data:
	datetime_mesure=mesure['datetime'].split("T")[0]+" "+ mesure['datetime'].split("T")[1][:6]+"00"
	query="UPDATE minut_data SET avg_sound_db="+str(mesure["value"])+" WHERE house_id='4' AND mesure_datetime='"+datetime_mesure+"'"
	cursor_mysql.execute(query)
	i=i+1
	if i==100:
		conn_mysql.commit()
		i=0
		j=j+1
		print(100*j)




conn_mysql.commit()
cursor_mysql.close()
conn_mysql.close()
