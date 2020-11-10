import requests
import hashlib
'''
responseUsers = requests.get('http://127.0.0.1:5000/get_users',
                json=
                {
                    "server_id": 1
                })

resp = responseUsers.json()['res']
print(resp[0])
'''

f = ""
print(hashlib.md5(f.encode()).hexdigest())