'''servers = {
    "testServer":{
        "messages": {
            'username': "ff",
            'text': "hello",
            'timestamp': '22.12.2020'
        },
        "users": {
            "Leha":
            {
                "password": "555",
                "online": True
            }
        },
        "admin": "Leha"
    }
}

print(servers["testServer"]["messages"]["text"])
for i in servers["testServer"]["admins"]:
    print(i)
'''
import time

print(time.time())