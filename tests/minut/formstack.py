import requests
import MySQLdb
endpoint = "https://www.formstack.com/api/v2/form/3073329/field.json"
headers_post = {"Authorization":"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOiI1YTE3NmY0M2JmYjVkMTAwMDE0ZmIwYTgiLCJyb2xlcyI6WyJtaW51dCJdLCJvcmdJZCI6Im1pbnV0Iiwic2NvcGUiOiIiLCJpYXQiOjE1MTI0NzczNzUsImV4cCI6MTUxMjQ4MDk3NSwiaXNzIjoiTWludXQsIEluYy4ifQ.K8x3k7PAGvioTdQT8t-_8vE10cO09__berj5_qk6cng",
			"Content-Type": "application/json"}
headers_get = {"Authorization":"Bearer 8bd9f7454d0c3e9bd1199ac31874e00c"}
data=requests.get(endpoint,headers=headers_get).json()
results={}
for field in data:
	print((field['id']+ ":"+field['label']).encode('utf-8'))
"""
61514726:Address
59498821:Tenants
59498681:Area type
59498691:Area Location/ Details
61514680:Items (Entrance/Hall)
59498643:Items (Living room)
59498684:Items (Kitchen)
61514808:Items (Bathroom)
61514810:Items (Bathroom-toilet only)
61514837:Items (Bedroom)
61516392:Items ( Bedroom+bathroom)
61514839:Items (Laundry area)
61514811:Items (Storage)
61515028:Items (Stairwell)
63222397:Items (Outdoor area)
61515029:Items (Hallways)
61515031:Items (Garage)
59498877:Picture
61514699:Condition
59498864:Condition Details
"""