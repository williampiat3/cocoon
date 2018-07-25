import requests
client_id='894d936d45bc48dc2333ed853cb83dd9cf8454f1cf664564e62e509cdd15d9c2'
client_secret='a9369d98cf46cc9f5c936a574be52c4bf4d18835e44eeed3b225278bd2c66efb'
temp="7b1f47e089578b9818bd39d723aa46382ca07efe"
state="qSM1RVoi-Q-a7CaODJJUDvqxEruFDR5MfjX0"
endpoint='https://auth.arthuronline.co.uk/oauth/token'
data={
'grant_type':'authorization_code',
'code':temp,
'client_id':client_id,
'client_secret':client_secret,
'redirect_uri':'http://0.0.0.0:8000',
'state':state
}
print(requests.post(endpoint,data=data).json())