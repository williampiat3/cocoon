import MySQLdb
import psycopg2
import psycopg2.extensions
import json
import sys
import os
import time
import datetime

import global_configuration

def NA(value, cur):
	'''turn all None is into SQL nulls'''
	if value is None:
		return 'NA'
	return value

def register():
	None2NA = psycopg2.extensions.new_type((600,), 'None2NA', NA)
	psycopg2.extensions.register_type(None2NA)


def get_and_load(cursor_mysql):
	query = """SELECT CONCAT( h.address,' ',th.tenant_nr) AS room, CONCAT (t.first_name,' ',t.last_name)as name,th.incoming_date,th.outgoing_date FROM tenants_history AS th
   INNER JOIN tenants AS t
 ON t.id=th.tenant_id
 INNER JOIN houses AS h
 ON h.id=th.house_id
  WHERE th.state='OK' AND CURDATE()< th.outgoing_date
 ORDER BY h.address,th.tenant_nr"""


	cursor_mysql.execute(query)
	data = cursor_mysql.fetchall()
	print(data)


def numCheck(value):
	if value == None :
		return str(0)
	else:
		return str(value)

def timestampCheck(value):
	if value == None :
		return str('0000-00-00 00:00:00')
	else:
		return str(value)

def strCheck(str):
	if str is None:
		return ''
	else :
		return MySQLdb.escape_string(str)


def load_data(cursor_mysql,data):
	query = 'INSERT IGNORE INTO sw_au_bi.middledb (order_nr, fk_customer, gmv_bef_coupons_aft_cancel, manual_cogs_capture, shipping_paid, device, shipping_theory, GST, delivery_time_start, name_en, name_company, provider_reference, shopper_pay, shopper_spent, total_cogs, shopper_id, delivery_zip_code, city_region, partner_cogs, partner_gmv, partner_net_gmv, partner_unique_items, canceled_items, substituted_items, valid_items, total_gmv_canceled_items, unique_items_ordered, total_gmv_refunded_items, coupon_money_value, shopper_score, date_first_at_customer, sales_order_created_at, comments, customer_email,sales_order_grand_total ) values '
	for i in range(0,len(data)):
		query_bit = "("+str(data[i][0])+","+numCheck(data[i][1])+","+numCheck(data[i][2])+","+numCheck(data[i][3])+","+numCheck(data[i][4])+",'"+strCheck(data[i][5])+"',"+numCheck(data[i][6])+","+numCheck(data[i][7])+",'"+timestampCheck(data[i][8])+"','"+strCheck(data[i][9])+"','"+strCheck(data[i][10])+"','"+strCheck(data[i][11])+"',"+numCheck(data[i][12])+","+numCheck(data[i][13])+","+numCheck(data[i][14])+",'"+strCheck(data[i][15])+"','"+strCheck(data[i][16])+"','"+strCheck(data[i][17])+"',"+numCheck(data[i][18])+","+numCheck(data[i][19])+","+numCheck(data[i][20])+","+numCheck(data[i][21])+","+numCheck(data[i][22])+","+numCheck(data[i][23])+","+numCheck(data[i][24])+","+numCheck(data[i][25])+","+numCheck(data[i][26])+","+numCheck(data[i][27])+","+numCheck(data[i][28])+","+numCheck(data[i][29])+",'"+timestampCheck(data[i][30])+"','"+timestampCheck(data[i][31])+"','"+strCheck(data[i][32])+"','"+strCheck(data[i][33])+"','"+numCheck(data[i][35])+"')"
		if i > 0:
			query = query + ',' + query_bit
		else :
			query = query + query_bit
	cursor_mysql.execute(query)


def main():
	None2NA = psycopg2.extensions.new_type((600,), 'None2NA', NA)
	psycopg2.extensions.register_type(None2NA)

	try:

		conn_mysql= MySQLdb.connect(host=global_configuration.mysql_au.host, user=global_configuration.mysql_au.username, passwd=global_configuration.mysql_au.password, db=global_configuration.mysql_au.db, port=global_configuration.mysql_au.port)

	except:
		print "Connections to Mysql failed"

	cursor_mysql = conn_mysql.cursor()
	

	try:
	    get_and_load(cursor_pg,cursor_mysql)
	    status="Success"

	except:
		status="Fail"


	conn_mysql.commit()
	cursor_mysql.close()
	conn_mysql.close()

if __name__=='__main__':main()
