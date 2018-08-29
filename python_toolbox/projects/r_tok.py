import requests
import json
"""
curl -X POST \
          https://auth.arthuronline.co.uk/oauth/token \
          -H 'Cache-Control: no-cache' \
          -H 'Content-Type: application/x-www-form-urlencoded' \
          -d 'grant_type=authorization_code&code=YOUR_AUTHORIZATION_CODE&client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET&redirect_uri=YOUR_REDIRECT_URI&state=YOUR_STATE_STRING'

code=058a5a9a96f84d7fe6c91a4ebbece2e01a24e546&state=wDSzYf8w-TkWrrOgNAJ0ImY6xnURuo9rp8-I
"""
endpoint="https://auth.arthuronline.co.uk/oauth/token"

headers={'Cache-Control': 'no-cache','Content-Type': 'application/x-www-form-urlencoded'}
data={
	'grant_type':'authorization_code',
	'code':"4c778ce3b2313d46c088645f574dc23e7c3028e0",
	'client_id':'894d936d45bc48dc2333ed853cb83dd9cf8454f1cf664564e62e509cdd15d9c2',
	'client_secret':'a9369d98cf46cc9f5c936a574be52c4bf4d18835e44eeed3b225278bd2c66efb',
	'redirect_uri':"http://0.0.0.0:8000",
	'state':"O9M52abI-ACl2g7CcqjdrkMC3DcIslQnqxe8"
}
response=requests.post(endpoint,headers=headers,data=data).json()
print(json.dumps(response))

{u'info': {u'user_id': 14438, u'email': u'marcus@cocoon.ly'},
 u'access_token': u'27e73410611bca1b443b2add104511a6d30db8b5d35ffee70fd5071adcb9d25a',
 u'expires_in': 1209599,
 u'token_type': u'Bearer',
 u'scope': u'read',
 u'refresh_token': u'5c269ad0b3efdeb79ec1dcbf8937671a2a43d1d382d0cf335d29237a0b763b07'}
