import requests
import time
import hashlib

responseUsers = requests.get('http://127.0.0.1:5000/get_users',
                json=
                {
                    "server_id": 1
                })

resp = responseUsers.json()['res']
for i in resp:
    print(i[0], "(Online)" if i[1] else "(Offline)")
