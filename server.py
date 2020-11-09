from flask import Flask, request
from datetime import datetime
import hashlib
import time
# Удалить после релиза (и список messages сделать пустым)
from crypt import *
from bot import *
import sqlite3 as sq

conn = sq.connect("Messenger.db")
cur = conn.cursor()

app = Flask(__name__)
server_start = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
messages = [
    {'username': 'Jack', 'text': encrypt(
        'Hello', 314), 'timestamp': time.time()},
    {'username': 'Jack2', 'text': encrypt(
        'Hello, Jack', 314), 'timestamp': time.time()},
]

users = {
    'Jack': {
        'password': hashlib.md5('1234'.encode()).hexdigest(),
        'online': False
    },
    'Jack2': {
        'password': hashlib.md5('5678'.encode()).hexdigest(),
        'online': False
    },
    'Jack3': {
        'password': hashlib.md5('1234'.encode()).hexdigest(),
        'online': False
    },
    'Jack4': {
        'password': hashlib.md5('5678'.encode()).hexdigest(),
        'online': False
    }
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

@app.route("/connect")
def conn():
    server_id = request.json['server_id']
    username = request.json['username']
    users[username]['online'] = True

@app.route("/login")
def login():
    username = request.json['username']
    password = request.json['password']
    if username == "" or password == "":
        return {'isNotFilled': True}
    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        if cur.execute(f"SELECT user_id from users WHERE username='{username}' AND password='{password}';").fetchone():
            return {'ok': True}
        return {'invalidData': True}


@app.route("/reg")
def reg():
    username = request.json['username']
    password = request.json['password']
    if username == "" or password == "":
        return {'isNotFilled': True}
    if username in users:
        return {'nameIsTaken': True}
    users[username] = {}
    users[username]['password'] = password
    users[username]['online'] = True
    print(users[username]['online'])
    messages.append(
        {
            "username": "BOT",
            "text": encrypt(f"{username}, добро пожаловать в чат", 314),
            "timestamp": time.time()
        })
    return 'ok'


@app.route("/send_message")
def send_message():
    username = request.json['username']
    text = decrypt(request.json['text'], 314)
    if text == "":
        return {"blankMessage": True}

    inp = [ch for ch in text.split(' ') if ch]

    name, arg = None, None
    try:
        name, arg = inp[0].lower(), inp[1].lower()
    except:
        name = inp[0].lower()
    if len(inp) <= 2:
        arg = None if arg == "" else arg
        if name in commands:
            if arg is not None:
                messages.append(
                    {
                        'username': 'BOT',
                        'text': encrypt(commands[name]['action'](arg), 314),
                        'timestamp': time.time()
                    })
            else:
                messages.append(
                    {
                        'username': 'BOT',
                        'text': encrypt(commands[name]['action'](), 314),
                        'timestamp': time.time()
                    })
    else:
        messages.append(
            {
                'username': username,
                'text': encrypt(text, 314),
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
    # Возвращаем словарь
    # users нужен, чтобы обращаться к нему как к json, list нужен, чтобы перебирать никнеймы

    return {
        'users': list(users.keys()),
        'isOnline': list(users[x]['online'] for x in users.keys())
    }


@app.route("/disconnect")
def disconnect():
    name = request.json['username']
    users[name]['online'] = False
    print(users[name]['online'])
    return 'ok'


if __name__ == '__main__':
    app.run()
