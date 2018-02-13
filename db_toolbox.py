import pymysql
pymysql.install_as_MySQLdb()

def get_connection():
	try:
		conn_mysql= MySQLdb.connect(host="146.148.11.22", user="root", passwd="judo1994", db="project" ,port=3306)

	except:
		print "Connections to Mysql failed"
	query="SELECT hst,usr,pwd,db,port FROM cocoon_db WHERE name='cocoon_db'"
	cursor_mysql=conn_mysql.cursor()
	cursor_mysql.execute(query)
	data=cursor_mysql.fetchall()[0]
	try:
		conn_mysql_cocoon=MySQLdb.connect(host=data[0], user=data[1], passwd=data[2], db=data[3] ,port=data[4])
	except:
		print "connection to cocoon failed"
	return conn_mysql_cocoon

def select_db(query,conn_mysql):
	results=[]
	cursor=conn_mysql.cursor()
	cursor.execute(query)
	data=cursor.fetchall()
	num_fields = len(cursor.description)
	field_names = [i[0] for i in cursor.description]
	for instance in data:
		result={}
		for i in range(len(field_names)):
			result[field_names[i]]=instance[i]
		results.append(result)
	cursor.close()
	return results


def update_db(query,conn):
	cursor=conn_mysql.cursor()
	cursor.execute(query)
	conn.commit()
	cursor.close()

def update_targeted(data,table,ids,conn):
	cursor=conn_mysql.cursor()
	setting=[]
	where=[]
	for key in data:
		info=data[key]
		if type(info)==type('test'):
			setting.append(key+"='"+info+"'")
		else:
			setting.append(key+"="+str(info))
	for key in ids:
		info=ids[key]
		if type(info)==type('test'):
			where.append(key+"='"+info+"'")
		else:
			where.append(key+"="+str(info))
	query="UPDATE "+ table+" SET "+",".join(setting)+ " WHERE "+' AND '.join(where)
	cursor.execute(query)
	conn.commit()
	cursor.close()

def insert_batch(data,table,conn,batch=100):
	cursor=conn_mysql.cursor()
	headers=data[0].keys()
	nb_batch=len(data)/batch
	for i in range(nb_batch+1):
		intel=data[batch*i:min(batch*(i+1),len(data))]
		values=[]
		for value in intel:
			sentence=[]
			for head in headers:
				val=value[head]
				if type(val)==type('test'):
					sentence.append("'"+value[head]+"'")
				else:
					sentence.append(value[head])
			values.append("("+",".join(sentence)+")")
		query="INSERT INTO "+table+" ( '"+"','".join(headers)+"') VALUES "+ ','.join(values)
		cursor.execute(query)
	conn.commit()
	cursor.close()

conn=get_connection()
results=select_db("SELECT address,id,lng FROM houses",conn)
print(results)








