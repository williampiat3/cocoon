import os
import MySQLdb
import base64
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import os

from apiclient import errors


def get_connection():
    CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')
    CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
    CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD')
    if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
        cloudsql_unix_socket = os.path.join('/cloudsql', CLOUDSQL_CONNECTION_NAME)
        db = MySQLdb.connect(unix_socket=cloudsql_unix_socket,user=CLOUDSQL_USER,passwd=CLOUDSQL_PASSWORD)
    else:
        db = MySQLdb.connect(
            host='35.189.18.225', user=CLOUDSQL_USER, passwd=CLOUDSQL_PASSWORD,db="ops",port=3306)

    return db

def select_db(query,conn):
    results=[]
    cursor=conn.cursor()
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
    
def select_specific(table,ids,conn):
    cursor=conn.cursor()
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


def update_db(query,conn):
    cursor=conn.cursor()
    cursor.execute(query)
    conn.commit()
    cursor.close()
    return True

def update_targeted(data,table,ids,conn):
    cursor=conn.cursor()
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
    conn.commit()
    cursor.close()
    return True

def insert_batch(data,table,conn,batch=100):
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

    

