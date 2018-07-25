import arthur
import requests
import toolbox
import datetime
import json

if __name__=='__main__':
	conn=toolbox.get_connection()
	arthur_tb=arthur.Arthur(conn)
	print(arthur_tb.get_all_pages_data("https://api.arthuronline.co.uk/viewings/index.json"))