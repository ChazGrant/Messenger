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
last_timestamps = dict()

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

def hash(text):
    return hashlib.md5(text.encode()).hexdigest()

@app.route("/")
def hello():
    return "Hello, User! Это наш мессенджер. А вот его статус:<a href='/status'>Status</a>"


@app.route("/status")
def status():
    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        serv = cur.execute(
            f"SELECT `server_name`, `start_time`, `users` FROM servers WHERE `server_id`=1;").fetchone()
        messages_count = len(cur.execute(
            f"SELECT `server_id` FROM `messages` WHERE `server_id`=1;").fetchall())
    return{
        'status': 'OK',
        'name': serv[0],
        'server_start_time': datetime.fromtimestamp(serv[1]).strftime('%H:%M:%S %d/%m/%Y'),
        'current_time': datetime.now().strftime('%H:%M:%S %d/%m/%Y'),
        'current_users': len(serv[2].split()),
        'current_messages': messages_count
    }


@app.route("/create_server")
def create_server():
    pass
    '''
Название сервера, дата запуска, админ
    '''


@app.route("/connect")
def connect():
    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        server_id = request.json['server_id']
        username = request.json['username']
        users = cur.execute(
            f"SELECT users FROM `servers` WHERE `server_id`='{server_id}'").fetchall()[0][0].split()
        for user in users:
            print(user)
        return {'ok': True}
        try:
            cur.execute(
                f"UPDATE servers  SET `server_name` = `server_name` || '{username}' WHERE `server_id`='{server_id}';")
            conn.commit()
            print(cur.execute("SELECT * FROM servers;").fetchall())
        except Exception as e:
            return {"DB_Error": True}
    return {'ok': True}


@app.route("/login")
def login():
    username = request.json['username']
    password = request.json['password']
    if username == "" or password == "":
        return {'isNotFilled': True}
    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        if cur.execute(f"SELECT user_id from users WHERE `username`='{username}' AND `password`='{hash(password)}';").fetchone():
            cur.execute(
                f"UPDATE `users` SET isOnline=1 WHERE `username`='{username}'")
            conn.commit()
            return {'ok': True}
        return {'invalidData': True}


@app.route("/reg")
def reg():
    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        username = request.json['username']
        password = request.json['password']
        if username == "" or password == "":
            return {'isNotFilled': True}
        if cur.execute(f"SELECT `username` FROM `users` WHERE `username`='{username}';").fetchone():
            return {'nameIsTaken': True}
        else:
            cur.execute("INSERT INTO users(username, password, servers_id, isOnline) VALUES(?, ?, ?, ?);",
                        (username, hash(password), '1', 1))
            conn.commit()
    return {'ok': True}


@app.route("/send_message")
def send_message():
    username = request.json['username']
    text = decrypt(request.json['text'], 314)
    server_id = request.json['server_id']

    if text == "":
        return {"blankMessage": True}

    last_timestamps[server_id] = time.time()

    inp = [ch for ch in text.split(' ') if ch]

    name, arg = None, None
    try:
        name, arg = inp[0].lower(), inp[1].lower()
    except:
        name = inp[0].lower()
    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        if len(inp) <= 2:
            arg = None if arg == "" else arg
            if name in commands:
                if arg is not None:
                    server_id = request.json["server_id"]

                    cur.execute("INSERT INTO messages(`username`, `text`, `timestamp`, `server_id`) VALUES(?, ?, ?, ?)", (
                        "BOT", encrypt(commands[name]['action'](arg), 314), time.time(), server_id))
                else:
                    cur.execute("INSERT INTO messages(`username`, `text`, `timestamp`, `server_id`) VALUES(?, ?, ?, ?)", (
                        "BOT", encrypt(commands[name]['action'](), 314), time.time(), server_id))
            else:
                cur.execute("INSERT INTO messages(`username`, `text`, `timestamp`, `server_id`) VALUES(?, ?, ?, ?)", (
                    username, encrypt(text, 314), time.time(), server_id))
        else:
            cur.execute("INSERT INTO messages(`username`, `text`, `timestamp`, `server_id`) VALUES(?, ?, ?, ?)", (
                        username, encrypt(text, 314), time.time(), server_id))

    return {'ok': True}


@app.route("/get_messages")
def get_message():
    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        after = float(request.args['after'])
        server_id = int(request.args['server_id'])
        try:
            if last_timestamps[server_id] >= after:
                res = cur.execute(
                    f"SELECT `username`, `text`, `timestamp` FROM `messages` WHERE `timestamp` > {after} AND `server_id` = {server_id};").fetchall()
                return {'messages': res}
            else:
                return {'messages': []}
        except:
            last_timestamps[server_id] = after
            res = cur.execute(
                f"SELECT `username`, `text`, `timestamp` FROM `messages` WHERE `timestamp` > {after} AND `server_id` = {server_id};").fetchall()
            return {'messages': res}


@app.route("/get_users")
def get_users():
    # Возвращаем словарь
    # users нужен, чтобы обращаться к нему как к json, list нужен, чтобы перебирать никнеймы
    with sq.connect("Messenger.db") as conn:
        server_id = request.json["server_id"]
        cur = conn.cursor()
        res = cur.execute(
            f"SELECT username, isOnline FROM users WHERE `servers_id` LIKE '%{server_id}%';").fetchall()
    return {
        'res': res
    }


@app.route("/disconnect")
def disconnect():
    with sq.connect("Messenger.db") as conn:
        username = request.json['username']
        cur = conn.cursor()
        cur.execute(
            f"UPDATE `users` SET `isOnline`=0 WHERE `username`='{username}';")
        conn.commit()
    return 'ok'


if __name__ == '__main__':
    app.run(debug=True)
