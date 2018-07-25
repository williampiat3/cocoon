import MySQLdb
import json
import datetime


class mysql_conn():
	def __init__(self,config_file):
		with open(config_file,"r") as json_file:
			configuration=json.load(json_file)
		try:
			conn_mysql= MySQLdb.connect(host=configuration["mysql"]["host"], user=configuration["mysql"]["user"], passwd=configuration["mysql"]["password"], db=configuration["mysql"]["db"] ,port=configuration["mysql"]["port"])

		except:
			print("Connections to Mysql failed")
	
		self.conn=conn_mysql

	def select_db(self,query):
		results=[]
		cursor=self.conn.cursor()
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

	def select_specific(self,table,ids):
		cursor=self.conn.cursor()
		where=[]
		results=[]
		for key in ids:
			info=ids[key]
			if type(info)==type('test') or type(info)==type(u'test'):
				where.append(key+"='"+info+"'")
			else:
				where.append(key+"="+str(info))
		query="SELECT * FROM "+ table+" WHERE "+' AND '.join(where)
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
		return results[0]

	def update_db(self,query):
		cursor=self.conn.cursor()
		cursor.execute(query)
		self.conn.commit()
		cursor.close()

	def update_targeted(self,data,table,ids):
		cursor=self.conn.cursor()
		setting=[]
		where=[]
		for key in data:
			info=data[key]
			if type(info)==type('test') or type(info)==type(u'test'):
				setting.append(key+"='"+info+"'")
			else:
				setting.append(key+"="+str(info))
		for key in ids:
			info=ids[key]
			if type(info)==type('test') or type(info)==type(u'test'):
				where.append(key+"='"+info+"'")
			else:
				where.append(key+"="+str(info))
		query="UPDATE "+ table+" SET "+",".join(setting)+ " WHERE "+' AND '.join(where)
		cursor.execute(query)
		self.conn.commit()
		cursor.close()

	
	def insert_batch(self,data,table,batch=100):
		try:
			cursor=conn.cursor()
			headers=data[0].keys()
			nb_batch=len(data)/batch
			for i in range(nb_batch+1):
				intel=data[batch*i:min(batch*(i+1),len(data))]
				values=[]
				for value in intel:
					sentence=[]
					for head in headers:
						val=value[head]
						if (type(val)==type('test') or type(val)==type(u'test')):
							sentence.append("'"+value[head]+"'")
						else:
							sentence.append(str(value[head]))
					values.append("("+",".join(sentence)+")")
				query="INSERT INTO "+table+" ( "+",".join(headers)+") VALUES "+ ','.join(values)
				cursor.execute(query)
			conn.commit()
			cursor.close()
			return True
		except IndexError:
			return False

	

if __name__=="__main__":
	tb=mysql_conn('config.json')
	print(tb.select_db("SELECT * FROM ops.houses"))

