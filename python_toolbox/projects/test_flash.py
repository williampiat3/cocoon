import requests
import json

endpoint='https://heroic-light-175013.appspot.com/formstack_deposit'
headers={"Authorization": "Bearer gvr69niPEZfe_qzepoxnz","Content-Type":"application/json"}
print(requests.post(endpoint,headers=headers,data=json.dumps({"troll":"test","UniqueID":"868790","Email":"william.piat3@gmail.com"})).text)
