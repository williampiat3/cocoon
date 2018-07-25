import requests
endpoint = "https://api.minut.com/v1/oauth/token"
data = {
 "redirect_uri": "http://localhost:8000/point",
 "client_id": "92b3eb7ed5b9893a",
 "client_secret": "ce108818eabafb9a5abb5054d3892e19",
 "code": "QPgeCTLmDzlwfYqC",
 "grant_type": "authorization_code"
}
headers_post = {"Cache-Control": "no-cache"}

##inb_x80

print requests.post(endpoint,data=data,headers=headers_post).json()
"""results=requests.get(endpoint,headers=headers_get).json()["_results"]
for i in results:
	print(i["name"])
	print(i["id"])
	print('-----------------')"""

"""results=requests.get("https://api2.frontapp.com/conversations/cnv_dixtzl/messages?limit=100",headers=headers_get).json()["_results"]
for i in results:
	print(results.index(i))
	print(i["recipients"])
	print(i["id"])
	print(i["type"])
	print(i["text"])
	print('-----------------')"""

# results=requests.get("https://api2.frontapp.com/conversations/cnv_dixtzl",headers=headers_get).json()
# print(results["recipient"])