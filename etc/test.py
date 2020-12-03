import requests

req = requests.get("http://mezano.pythonanywhere.com/get_servers")

print(req.json())

