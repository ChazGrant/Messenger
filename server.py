from flask import Flask, request
from datetime import datetime
import hashlib
import time
import re
from crypt import *
from bot import *
import sqlite3 as sq

conn = sq.connect("Messenger.db")
cur = conn.cursor()

app = Flask(__name__)
server_start = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
last_timestamps = dict()


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
        'current_users': len(serv[2].split()),
        'current_messages': messages_count
    }


@app.route("/create_server")
def create_server():
    servName = request.get_json()['serverName']
    servPass = request.get_json()['serverPassword']
    servAdmin = request.get_json()['username']
    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        serverNames = cur.execute("SELECT `server_name` FROM servers").fetchall()
        for serverName in serverNames:
            if servName in serverName:
                return { "nameIsTaken": True }
        cur.execute("INSERT INTO servers(`server_name`, `admin`, `users`, `start_time`, `password`) VALUES(?, ?, ?, ?, ?)", (servName, servAdmin, servAdmin, time.time(), hash(servPass)))
        conn.commit()
        return { "ok": True }
    return { "someProblems": True }
    '''
Название сервера, дата запуска, админ
    '''


@app.route("/connect")
def connect():
    with sq.connect("Messenger.db") as conn:
        try:
            cur = conn.cursor()
            server_id = request.json['server_id']
            username = request.json['username']
            password = request.json['password']
            rightPassword = cur.execute(f"SELECT password FROM `servers` WHERE server_id={server_id}").fetchone()[0]
            if rightPassword == hashlib.md5(password.encode()).hexdigest():
                cur.execute(
                    f"UPDATE `users` SET isOnline=1 WHERE username='{ username }'")
                servs_id = cur.execute(
                    f"SELECT servers_id FROM `users` WHERE username='{ username }'").fetchone()[0]
                if str(server_id) not in servs_id:
                    cur.execute(
                        f"UPDATE `users` SET servers_id=servers_id || ' ' || { server_id } WHERE username='{username}';")
                    conn.commit()
                serv_users = cur.execute(
                    f"SELECT `users` FROM servers WHERE `server_id` = { server_id };").fetchone()
                if username not in serv_users:
                    cur.execute(
                        f"UPDATE `servers` SET users = users || ' ' || '{ username }' WHERE `server_id` = {server_id};")
                    conn.commit()
            else:
                return { "badPassword": True }
        except:
            return { "someProblems": True }
    return {"ok": True}


@app.route("/login")
def login():
    username = request.json['username']
    password = request.json['password']
    if username == "" or password == "":
        return { 'isNotFilled': True }
    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        if cur.execute(f"SELECT user_id from users WHERE `username`='{username}' AND `password`='{hash(password)}';").fetchone():
            cur.execute(
                f"UPDATE `users` SET isOnline=1 WHERE `username`='{username}'")
            conn.commit()
            return { 'ok': True }
        return { 'invalidData': True }


@app.route("/reg")
def reg():
    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        username = request.json['username']
        password = request.json['password']

        # Минимум 1 символ, буквы или цифры. Длина пароля от 8 до 16
        pattern = r"^(?=.*[\W].*)(?=.*[0-9].*)(?=.*[a-zA-Z].*)[0-9a-zA-Z\W_]{8,16}?$"
        password = re.sub(r"[\s]+", "_", password)

        if username == "" or password == "":
            return { 'isNotFilled': True }
        if cur.execute(f"SELECT `username` FROM `users` WHERE `username`='{ username }';").fetchone():
            return { 'nameIsTaken': True }
        if re.match(pattern, password):
            cur.execute("INSERT INTO users(`username`, `password`) VALUES(?, ?)", (username, hash(password)))
            conn.commit()
            return { 'ok': True }
    return { "badPassword": True }
    

@app.route("/send_message")
def send_message():
    username = request.json['username']
    text = decrypt(request.json['text'], 314)
    server_id = request.json['server_id']

    if text == "":
        return { "blankMessage": True }

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


@app.route("/get_server_name")
def get_server_name():
    server_id = request.json['server_id']
    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        server_name = cur.execute(f"SELECT server_name FROM `servers` WHERE `server_id`={server_id}").fetchone()[0]
    return { 'server_name': server_name }


@app.route("/get_servers")
def get_servers():
    with sq.connect("Messenger.db") as conn:
        try:
            cur = conn.cursor()
            servers = cur.execute("SELECT * FROM `servers`").fetchall()
            return {
                "servers": servers
                }
        except:
            return {"someProblems": True}


@app.route("/get_messages")
def get_messages():
    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        after = float(request.args['after'])
        server_id = int(request.args['server_id'])
        try:
            if last_timestamps[server_id] >= after:
                res = cur.execute(
                    f"SELECT `username`, `text`, `timestamp` FROM `messages` WHERE `timestamp` > {after} AND `server_id` = {server_id};").fetchall()
                return {
                    'messages': res
                    }
            else:
                return {
                    'messages': []
                    }
        except:
            last_timestamps[server_id] = after
            res = cur.execute(
                f"SELECT `username`, `text`, `timestamp` FROM `messages` WHERE `timestamp` > {after} AND `server_id` = {server_id};").fetchall()
            return {
                'messages': res
                }


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
            f"UPDATE `users` SET `isOnline`=0 WHERE `username`='{ username }';")
        conn.commit()
    return 'ok'


if __name__ == '__main__':
    app.run(debug=True)
