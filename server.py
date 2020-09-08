from flask import Flask, request
from datetime import datetime
import hashlib
import time
# Удалить после релиза (и список messages сделать пустым)
from crypt import encrypt

app = Flask(__name__)
server_start = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
messages = [
    {'username': 'Jack', 'text': encrypt(
        'Hello', 314), 'timestamp': time.time()},
    {'username': 'Jack2', 'text': encrypt(
        'Hello, Jack', 314), 'timestamp': time.time()},
]

users = {
    'Jack': hashlib.md5('1234'.encode()).hexdigest(),
    'Jack2': hashlib.md5('5678'.encode()).hexdigest(),
}


@app.route("/")
def hello():
    return "Hello, User! Это наш мессенджер. А вот его статус:<a href='/status'>Status</a>"


@app.route("/status")
def status():
    return{
        'status': 'OK',
        'name': 'Mezzano Corp',
        'server_start_time': server_start,
        'server_current_time': datetime.now().strftime('%H:%M:%S %d/%m/%Y'),
        'current_time_seconds': time.time(),
        'current_users': len(users),
        'current_messages': len(messages)
    }


@app.route("/login")
def login():
    username = request.json['username']
    password = request.json['password']
    if username == "" or password == "":
        return {'isNotFilled': True}
    if username in users:
        if users[username] != password:
            return {'invalidPassword': True}
    else:
        return {'invalidUsername': True}
    return 'ok'


@app.route("/reg")
def reg():
    username = request.json['username']
    password = request.json['password']
    if username == "" or password == "":
        return {'isNotFilled': True}
    if username not in users:
        users[username] = password
        return{'nameIsTaken': False}
    else:
        return{'nameIsTaken': True}
    return 'ok'


@app.route("/send_message")
def send_message():
    username = request.json['username']
    text = request.json['text']

    if text == "":
        return {"blankMessage": True}

    messages.append(
        {
            'username': username,
            'text': text,
            'timestamp': time.time()
        })

    return 'ok'


@app.route("/get_messages")
def get_message():
    after = float(request.args['after'])

    result = []

    for message in messages:
        if message['timestamp'] > after:
            result.append(message)

    return{
        'messages': result
    }


@app.route("/get_users")
def get_users():
    return "<meta charset='utf-8'>" + str(users)


@app.route("/get_msgs")
def get_messages():
    return "<meta charset='utf-8'>" + str(messages)


if __name__ == '__main__':
    app.run()
