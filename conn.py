import requests

us = input("Username: ")
id = input("Id: ")

req = requests.get("http://127.0.0.1:5000/connect", 
json=
{
    "username": us,
    "server_id": id
})