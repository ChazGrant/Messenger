# Messenger
# Copyright (C) 2021  ChazGrant (https://github.com/ChazGrant)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from flask import Flask, request, send_from_directory
from datetime import datetime
import hashlib
import time
import re
from crypt import *
from bot import *
import sqlite3 as sq
import os
import random


ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

app = Flask(__name__)
server_start = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
last_timestamps = dict()

servers_hash = list()

hash_ = lambda text: hashlib.md5(text.encode()).hexdigest()

def get_key(keys) -> int:
    keys = str(keys)
    return int(keys[keys.index("[") + 1:keys.index("]")])

def generate_hash(word:str) -> str:
    odd_salt = str(hashlib.md5(word[::2].encode()).hexdigest())
    even_salt = str(hashlib.md5(word[::-2][::-1].encode()).hexdigest())
    return hashlib.md5(word.encode()).hexdigest() + odd_salt + even_salt

def generate_random_hash() -> str:
	out = ""

	for _ in range(16):
		out += random.choice(ALPHABET)

	return hashlib.md5(out.encode()).hexdigest()

def cleanhtml(raw_html: str) -> str:
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def get_server_name_(server_id: int) -> str:
    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        server_name = cur.execute(
            f"SELECT server_name FROM `servers` WHERE `server_id`={int(server_id)}").fetchone()[0]
        return server_name

def get_chat_name_(chat_id: int) -> str:
    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        chatName = cur.execute(f"SELECT `chatName` FROM chats WHERE `chat_id` = {int(request.json['chat_id'])}").fetchone()[0]
        return chatName


@app.route("/")
def main() -> str:
    return "Hello, User! Это наш мессенджер. А вот его статус:<a href='/status'>Status</a>"

@app.route("/open")
def return_file():
    _hash, path = request.args.get("link").split(":")


    if path == "public":
        files = [f for _, _, f in os.walk("static/public")]

        if files:
            files = files[0]

        for file in files:
            if generate_hash(file) == _hash:
                return send_from_directory(directory="static/public", filename=file)
    elif path.isdigit():
        try:
            with sq.connect("Messenger.db") as conn:
                cur = conn.cursor()
                server_name = cur.execute(
                    f"SELECT server_name FROM `servers` WHERE `server_id`={int(path)}").fetchone()[0]
            files = [f for _, _, f in os.walk("static/" + server_name)]

            if files:
                files = files[0]

            for file in files:
                if generate_hash(file) == _hash:
                    return send_from_directory(directory="static/" + server_name, filename=file)
        except:
            return ""
    else:
        files = [f for _, _, f in os.walk("static/privateChats/" + path)]

        if files:
            files = files[0]

        for file in files:
            if generate_hash(file) == _hash:
                return send_from_directory(directory="static/privateChats/" + path, filename=file)


    return ""

@app.route("/status")
def status():
    if request.get_json():
        serv_id = request.json["server_id"]
        with sq.connect("Messenger.db") as conn:
            cur = conn.cursor()
            serv = cur.execute(
                f"SELECT `server_name`, `start_time`, `users` FROM servers WHERE `server_id`={serv_id};").fetchone()
            messages_count = len(cur.execute(
                f"SELECT `server_id` FROM `messages` WHERE `server_id`={serv_id};").fetchall())
        return{
            'status': 'OK',
            'name': serv[0],
            'server_start_time': datetime.fromtimestamp(serv[1]).strftime('%H:%M:%S %d/%m/%Y'),
            'current_users': len(serv[2].split()),
            'current_messages': messages_count
        }
    else:
        with sq.connect("Messenger.db") as conn:
            cur = conn.cursor()
            servers = cur.execute(
                    f"SELECT `server_name`, `start_time`, `users` FROM servers;").fetchall()
            servers_id = cur.execute(
                    f"SELECT `server_id` FROM `servers`;").fetchall()

            servers_id.sort()
            messages = []
            for server_id in servers_id:
                messages.append(
                    len(cur.execute(
                        f"SELECT `server_id` FROM `messages` WHERE `server_id`= {server_id[0]};")
                        .fetchall()))
        info = ""
        for counter in range(len(servers_id)):
            users = "".join(map(lambda x: "<li>" + str(x) + "</li>", servers[counter][2].split()))
            info += f'''
            <ul>
                <li>Название сервера: {servers[counter][0]}</li>
                <li>Время, прошедшее с момента запуска: {servers[counter][1]}</li>
                <li>Пользователи: <ul>{users}</ul></li>
                <li>Кол-во сообщений: {messages[counter]}</li>
            </ul>'''
        return info


@app.route("/create_server")
def create_server() -> dict:
    serv_name = request.json['serverName']
    serv_pass = request.json['serverPassword']
    serv_admin = request.json['username']

    try:
        with sq.connect("Messenger.db") as conn:
            cur = conn.cursor()
            server_names = cur.execute(
                "SELECT `server_name` FROM servers").fetchall()

            for server_name in server_names:
                if serv_name in server_name:
                    return {"nameIsTaken": True}
            cur.execute("INSERT INTO servers(`server_name`, `admins`, `users`, `start_time`, `password`) VALUES(?, ?, ?, ?, ?)",
                        (serv_name, serv_admin, serv_admin, time.time(), hash_(serv_pass)))
            conn.commit()

            server_id = cur.execute(f"SELECT server_id FROM `servers` WHERE `server_name` LIKE '%{serv_name}%'").fetchone()

            os.mkdir("static/" + str(serv_name))

            return {
                "server_id": server_id
                }
    except:
        return {
            "someProblems": True
            }


# Проверить обновляются ли юзеры на разных серверах
@app.route("/connect")
def connect() -> dict:
    with sq.connect("Messenger.db") as conn:
        try:
            cur = conn.cursor()
            # Достаём данные из жсона
            server_id = str(request.json['server_id'])
            username = request.json['username']
            password = request.json['password']

            rightPassword = cur.execute(
                f"SELECT password FROM `servers` WHERE server_id={server_id}").fetchone()[0]

            if rightPassword == password:
                server_id_ = cur.execute(
                    f"SELECT servers_id FROM `users` WHERE `username` LIKE '%{username}%' ").fetchone()[0].split().index(server_id)
                isBanned = cur.execute(
                    f"SELECT `isBanned` FROM users WHERE `username` LIKE'%{username}%';").fetchone()[0].split()[server_id_]
                    
                if int(isBanned):
                    return {
                        "isBanned": True
                    }

                serv_users = cur.execute(
                    f"SELECT `users` FROM servers WHERE `server_id` = { server_id };").fetchone()[0]

                # Обновляем перечень пользователей для сервера
                if username not in serv_users:
                    cur.execute(
                        f"UPDATE `servers` SET users = users || ' ' || '{ username }' WHERE `server_id` = {server_id};")
                    conn.commit()

                # Проверяем на наличие данного сервера у пользователя
                servs_id = cur.execute(
                    f"SELECT servers_id FROM `users` WHERE username='{ username }'").fetchone()[0]
                
                if str(server_id) not in servs_id:
                    cur.execute(
                        f"UPDATE users SET `servers_id` = `servers_id` || ' ' || { server_id }, `isOnline` = `isOnline` || ' ' || '1', `lastSeen` = `lastSeen` || ' ' || {str(time.time())}, `entryTime` = `entryTime` || ' ' || {str(time.time())}, `timeSpent` = `timeSpent` || ' ' || '0.0' WHERE username='{username}';")
                    conn.commit()
                # Обновление онлайна и времени входа
                else:
                    # Получаем индекс сервера и изменяем значения по индексу
                    isOnline = cur.execute(
                            f"SELECT isOnline FROM `users` WHERE `username` LIKE '%{username}%' ").fetchone()[0].split()
                    entryTime = cur.execute(
                            f"SELECT `entryTime` FROM `users` WHERE `username` LIKE '%{username}%' ").fetchone()[0].split()
                    isOnline[server_id_] = '1'
                    entryTime[server_id_] = str(time.time())

                    # Создаём необходимые строки для внесения в бд
                    isOnlineToStr = " ".join(isOnline)
                    entryTimeToStr = " ".join(entryTime)

                    # Обновляем инфу о юзерах с имеющимися данными

                    cur.execute(
                        f"UPDATE `users` SET `isOnline`='{isOnlineToStr}', `entryTime`='{entryTimeToStr}' WHERE username='{ username }'")
                    conn.commit()
            else:
                return {
                    "badPassword": True
                    }
        except:
            return {
                "someProblems": True
                }

    servers_id = [get_key(servers_hash[i].keys()) for i in range(len(servers_hash))]
    server_id = int(server_id)

    if server_id in servers_id:
        servers_hash[servers_id.index(server_id)][server_id] = generate_random_hash()
    else:
        servers_hash.append(
			{
				server_id: generate_random_hash()
			})

    return {
        "ok": True
    }


@app.route("/login")
def login() -> dict:
    username = request.json['username']
    password = request.json['password']

    if username == "" or password == "":
        return {
            "isNotFilled": True
            }
    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        if cur.execute(f"SELECT user_id from users WHERE `username`='{username}' AND `password`='{hash_(password)}';").fetchone():
            return {
                "ok": True
                }
        return {
            "invalidData": True
            }

@app.route("/create_user")
def create_user() -> dict:
    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        username = request.json['username']
        password = request.json['password']
        server_id = request.json['server_id']

        pattern = r"^(?=.*[\W].*)(?=.*[0-9].*)(?=.*[a-zA-Z].*)[0-9a-zA-Z\W_]{8,16}?$"
        password = re.sub(r"[\s]+", "_", password)

        if username == "" or password == "":
            return {
                    "isNotFilled": True
                }
        if cur.execute(f"SELECT `username` FROM `users` WHERE `username`='{ username }';").fetchone():
            return {
                    "nameIsTaken": True
                }
        if re.match(pattern, password):
            cur.execute(
                "INSERT INTO users(`username`, `password`, `isOnline`, `servers_id`, `lastSeen`, `entryTime`, `timeSpent`, `isBanned`) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",\
                    (username, hash_(password), '0', server_id, str(time.time()), str(time.time()), '0.0', '0'))
            conn.commit()
            
            return {
                    "ok": True
                }
    return {
            "badPassword": True
        }

@app.route("/reg")
def reg() -> dict:
    username = request.json['username']
    password = request.json['password']
    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()

        # Минимум 1 символ, буквы или цифры. Длина пароля от 8 до 16
        pattern = r"^(?=.*[\W].*)(?=.*[0-9].*)(?=.*[a-zA-Z].*)[0-9a-zA-Z\W_]{8,16}?$"
        password = re.sub(r"[\s]+", "_", password)

        if username == "" or password == "":
            return {
                    "isNotFilled": True
                }
        if cur.execute(f"SELECT `username` FROM `users` WHERE `username`='{ username }';").fetchone():
            return {
                    "nameIsTaken": True
                }
        if re.match(pattern, password):
            cur.execute(
                "INSERT INTO users(`username`, `password`) VALUES(?, ?)", (username, hash_(password)))
            conn.commit()
            return {
                    "ok": True
                }
    return {
            "badPassword": True
        }


@app.route("/send_message")
def send_message() -> dict:
    username = request.json['username']
    text = cleanhtml(decrypt(request.json['text'], 314))
    server_id = request.json['server_id']

    if text == "":
        return {
            "blankMessage": True
        }

    last_timestamps[server_id] = time.time()

    inp = [ch for ch in text.split(' ') if ch]


    name, arg = None, None
    if len(inp) >= 2:
        name, arg = inp[0].lower(), inp[1].lower()
    else:
        name = inp[0].lower()

    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()

        if len(inp) >= 2:
            arg = None if arg == "" else arg

            if name in commands:
                server_id = request.json["server_id"]
                cur.execute("INSERT INTO messages(`username`, `text`, `timestamp`, `server_id`) VALUES(?, ?, ?, ?)", (
                    "BOT", encrypt(commands[name]['action'](arg), 314), time.time(), server_id))

            else:
                cur.execute("INSERT INTO messages(`username`, `text`, `timestamp`, `server_id`) VALUES(?, ?, ?, ?)", (
                    username, encrypt(text, 314), time.time(), server_id))

        else:
            cur.execute("INSERT INTO messages(`username`, `text`, `timestamp`, `server_id`) VALUES(?, ?, ?, ?)", (
                        username, encrypt(text, 314), time.time(), server_id)) 

    return {
        'ok': True
    }


@app.route("/get_server_name")
def get_server_name() -> dict:
    if "username" not in request.json:
        server_id = request.json['server_id']

        with sq.connect("Messenger.db") as conn:
            cur = conn.cursor()
            server_name = cur.execute(
                f"SELECT server_name FROM `servers` WHERE `server_id`={server_id}").fetchone()[0]
        return {
            'server_name': server_name
            }

    username = request.json['username']
    server_id = request.json['server_id']
    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        admins = cur.execute(
            f"SELECT admins FROM `servers` WHERE `server_id`={server_id}").fetchone()[0]
        server_name = cur.execute(
            f"SELECT server_name FROM `servers` WHERE `server_id`={server_id}").fetchone()[0]
    return {
            'server_name': server_name,
            'rightsGranted': username in admins or username == "CREATOR"
        }


@app.route("/get_servers")
def get_servers() -> dict:
    with sq.connect("Messenger.db") as conn:
        try:
            cur = conn.cursor()
            servers = cur.execute("SELECT * FROM `servers`").fetchall()
            return {
                "servers": servers
            }
        except:
            return {
                "someProblems": True
                }

@app.route("/get_users_amount")
def get_users_amount() -> dict:
    with sq.connect("Messenger.db") as conn:
        id = request.json["id"]
        users_amount = 0

        cur = conn.cursor()
        all_ids = cur.execute("SELECT `servers_id` FROM `users`").fetchall()

        for cur_id in all_ids:
            if str(id) in cur_id[0].split():
                users_amount += 1
        return {
            "users_amount": users_amount
        }

@app.route("/upload")
def upload() -> dict:
    if "server_id" in request.args:
        server_id = request.args['server_id']
        server_name = get_server_name_(server_id)
    else:
        server_id = 0

    data = request.data
    filename = request.args['filename']

    if "chat_id" in request.args:
        chat_id = request.args["chat_id"]
        with sq.connect("Messenger.db") as conn:
            cur = conn.cursor()
            chat_name = cur.execute(f"SELECT `chatName` FROM chats WHERE `chat_id` = {chat_id}").fetchone()[0]
            files = [f for _, _, f in os.walk("static/" + chat_name)]

            if files:
                files = files[0]
            else:
                pass

            for file in files:
                if file == filename:
                    return {
                        "nameIsTaken": True
                    }
            with open("static/privateChats/" + chat_name + "/" + filename, "wb+") as file:
                file.write(data)


    if not server_id:
        files = [f for _, _, f in os.walk("static")][0]
    else:
        files = [f for _, _, f in os.walk("static/" + server_name)][0]

    for file in files:
        if file == filename:
            return {
                "nameIsTaken": True
            }

    if not server_id:
        with open("static/" + filename, "wb+") as file:
            file.write(data)
    else:
        with open("static/" + server_name + "/" + filename, "wb+") as file:
            file.write(data)

    return {
        "ok": True
        }


# Можно вернуть либо один файл, либо архивом несколько
@app.route("/download")
def download() -> str:
    needed_file = request.json["neededFile"]

    if "chat_id" in request.json: 
        chat_name = get_chat_name_(request.json["chat_id"])

        files_list = [f for _, _, f in os.walk("static/privateChats/" + chat_name)]

    else:
        if "server_id" in request.json:
            server_name = get_server_name_(request.json['server_id'])
        else:
            server_id = 0

        if not server_id:
            files_list = [f for _, _, f in os.walk("static/")]
        else:
            files_list = [f for _, _, f in os.walk("static/" + str(server_name))]


    for file in files_list:
        if needed_file == file:
            if server_id:
                return send_from_directory(directory="static/" + str(server_name), filename=file, as_attachment=True)
            else:
                return send_from_directory(directory="static/", filename=file, as_attachment=True)
                

@app.route("/get_files")
def get_files() -> dict:
    if "server_id" in request.json:
        server_id = request.json['server_id']
    else:
        server_id = 0
    
    if "chat_id" in request.json:
        chat_name = get_chat_name_(request.json["chat_id"])
        try:
            files = [f for _, _, f in os.walk("static/privateChats/" + chat_name)]
        except:
            return {
                "someProblems": True
            }

        if files:
            # files это 2-мерный список, 0 список содержит всю инфу
            files = files[0]
        else:
            return {
                "someProblems": True
            }

        return {
            "allFiles": files
        }

    if not server_id:
        files = [f for _, _, f in os.walk("static")]

    else:
        server_name = get_server_name_(server_id)
        files = [f for _, _, f in os.walk("static/" + server_name)]

    if files:
        files = files[0]
    else:
        return {
            "someProblems": True
        }

    return {
        "allFiles": files
    }

@app.route("/get_server_password_existence")
def get_server_password_existence() -> dict:
    server_id = request.json["server_id"]

    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        server_password = cur.execute(f"SELECT `password` FROM `servers` WHERE `server_id` = '{server_id}'").fetchone()[0]

    return {
        "server_password": server_password
        }

@app.route("/get_chat_id")
def get_chat_id() -> dict:
    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        users = request.json["users"]
        users_reversed = request.json["usersReversed"]

        res = cur.execute(f"SELECT `chat_id` FROM chats WHERE `chatName` LIKE '%{users}%' OR `chatName` LIKE '%{users_reversed}%'").fetchone()
        if res:
            return {
                "chat_id": res[0]
            }
        else:
            os.mkdir("static/privateChats/" + users)
            cur.execute("INSERT INTO chats(`chatName`) VALUES(?)", (users, ))
            conn.commit()
            res = cur.execute(f"SELECT `chat_id` FROM chats WHERE chatName LIKE '%{users}%' OR chatName LIKE '%{users_reversed}%'").fetchone()
            return {
                "chat_id": res[0]
            }

@app.route("/send_private_message")
def send_private_message() -> dict:
    chat_id = request.json["chat_id"]
    username = request.json["username"]
    message = cleanhtml(request.json["text"])

    if message == "":
        return {
            "blankMessage": True
        }
    try:
        with sq.connect("Messenger.db") as conn:
            cur = conn.cursor()

            last_timestamps[str(chat_id)] = time.time()

            cur.execute("INSERT INTO chatMessages(`text`, `username`, `timestamp`, `chat_id`) VALUES(?, ?, ?, ?)", (message, username, time.time(), chat_id))

            return {
                "ok": True
            }
    except:
        return {
            "someProblems": True
        }

@app.route("/get_private_messages")
def get_private_messages() -> dict:
    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        companion = str(request.args['companion'])
        after = float(request.args['after'])
        chat_id = str(request.args['chat_id'])

        is_online = cur.execute(f"SELECT `isOnline` FROM users WHERE `username`='{companion}'").fetchone()[0].split()

        is_online = '1' in is_online

        try:
            if last_timestamps[chat_id] > after:
                res = cur.execute(
                    f"SELECT `username`, `text`, `timestamp` FROM `chatMessages` WHERE `timestamp` > {after} AND `chat_id` = {int(chat_id)};").fetchall()
                return {
                    'messages': res,
                    "isOnline": is_online
                }
            else:
                return {
                    'messages': [],
                    "isOnline": is_online
                }
        except:
            last_timestamps[chat_id] = after
            res = cur.execute(
                f"SELECT `username`, `text`, `timestamp` FROM `chatMessages` WHERE `timestamp` > {after} AND `chat_id` = {int(chat_id)};").fetchall()

            return {
                'messages': res,
                "isOnline": is_online
            }

@app.route("/get_messages")
def get_messages() -> dict:
    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        after = float(request.args['after'])
        server_id = int(request.args['server_id'])
        try:
            if last_timestamps[server_id] >= after:
                res = cur.execute(
                    f"SELECT `username`, `text`, `timestamp` FROM `messages` WHERE `timestamp` >= {after} AND `server_id` = {server_id};").fetchall()
                return {
                    'messages': res,
                }
            else:
                return {
                    'messages': [],
                }
        except:
            last_timestamps[server_id] = after
            res = cur.execute(
                f"SELECT `username`, `text`, `timestamp` FROM `messages` WHERE `timestamp` >= {after} AND `server_id` = {server_id};").fetchall()
            return {
                'messages': res,
            }

############# SESSION #################
@app.route("/create_session")
def create_session() -> dict:
    try:
        username = request.json["username"]
        username_for_hash = username

        with sq.connect("Messenger.db") as conn:
            cur = conn.cursor()
            username_in_use = cur.execute(f"SELECT `session_id` FROM sessions WHERE `username` LIKE '%{username}%'").fetchone()

            for _ in range(16):
                username_for_hash += random.choice(ALPHABET)
            salted_hash = hashlib.md5(username_for_hash.encode()).hexdigest()

            if username_in_use:
                cur.execute(f"UPDATE sessions SET `hash` = '{salted_hash}' WHERE `username` LIKE '%{username}%'").fetchone()
                conn.commit()
            else:
                cur.execute("INSERT INTO sessions(`username`, `hash`) VALUES(?, ?)", (username, salted_hash))
                conn.commit()
            
            return {
                "hash": encrypt(salted_hash, 314)
            }

    except:
        return {
            "someProblems": True
        }

@app.route("/check_for_session")
def check_for_session() -> dict:
    username = decrypt(request.json["username"], 314)
    salted_hash = decrypt(request.json["hash"], 314)

    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        is_valid = cur.execute(f"SELECT `session_id` FROM sessions WHERE `username` LIKE '%{username}%' AND `hash` LIKE '%{salted_hash}%'").fetchone()

        return {"username": username} if is_valid else {"badHash": True}

############# SESSION #################

@app.route("/get_users")
def get_users() -> dict:
    server_id = str(request.json["server_id"])
    try:
        for_admin = int(request.json["for_admin"])
    except:
        for_admin = 0

    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()

        if server_id == '0':
            allServersId = cur.execute(
                f"SELECT server_id FROM `servers`").fetchall()
            allServersId = " ".join(str(i[0]) for i in allServersId).split()

            res = {}

            for server_id in allServersId:
                user_info = cur.execute(
                    f"SELECT `username`, `servers_id`, `isOnline`, `lastSeen`, `entryTime`, `timeSpent`, `isBanned` FROM users WHERE `servers_id` LIKE '%{server_id}%';"
                ).fetchall()

                returnList = list()
                for user in user_info:
                    if server_id in user[1].split():
                        server_id_ = user[1].split().index(server_id)
                        isOnline = user[2].split()[server_id_]
                        lastSeen = user[3].split()[server_id_]
                        entryTime = user[4].split()[server_id_]
                        timeSpent = user[5].split()[server_id_]
                        isBanned = user[6].split()[server_id_]
                        returnList.append(user[0] + " " + isOnline + " " + lastSeen + " " + entryTime + " " + timeSpent + " " + isBanned)
                
                res[server_id] = returnList


            return {
                'res': res,
            }

        if for_admin and server_id:
            user_info = cur.execute(
            f"SELECT `username`, `servers_id`, `isOnline`, `lastSeen`, `entryTime`, `timeSpent`, `isBanned` FROM users WHERE `servers_id` LIKE '%{server_id}%';"
        ).fetchall()
            returnList = list()
            for user in user_info:
                server_id_ = user[1].split().index(server_id)
                isOnline = user[2].split()[server_id_]
                lastSeen = user[3].split()[server_id_]
                entryTime = user[4].split()[server_id_]
                timeSpent = user[5].split()[server_id_]
                isBanned = user[6].split()[server_id_]
                returnList.append(user[0] + " " + isOnline + " " + lastSeen + " " + entryTime + " " + timeSpent + " " + isBanned)


            res = sorted(returnList, key=lambda tup: tup[1], reverse=True)

            return {
                'res': res
            }


        is_current_user_banned = 0

        try:
            
            username = request.json["username"]
            
            
            server_id_ = cur.execute(
                f"SELECT servers_id FROM `users` WHERE `username` LIKE '%{username}%' ").fetchone()[0].split().index(server_id)
            user_is_banned = cur.execute(
                f"SELECT `isBanned` FROM users WHERE `username` LIKE '%{username}%'").fetchone()[0].split()
            is_current_user_banned = int(user_is_banned[server_id_])
        except Exception as e:
            return {
                "someProblems": str(e)
            }


    user_info = cur.execute(
            f"SELECT `username`, `servers_id`, `isOnline`, `lastSeen`, `entryTime`, `timeSpent`, `isBanned` FROM users WHERE `servers_id` LIKE '%{server_id}%';"
        ).fetchall()
    returnList = list()
    for user in user_info:
        server_id_ = user[1].split().index(server_id)
        isOnline = user[2].split()[server_id_]
        lastSeen = user[3].split()[server_id_]
        entryTime = user[4].split()[server_id_]
        timeSpent = user[5].split()[server_id_]
        isBanned = user[6].split()[server_id_]
        returnList.append(user[0] + " " + isOnline + " " + lastSeen + " " + entryTime + " " + timeSpent + " " + isBanned)


    res = sorted(returnList, key=lambda tup: tup[1], reverse=True)

    servers_id = [get_key(servers_hash[i].keys()) for i in range(len(servers_hash))]
    server_id = int(server_id)

    return {
        'res': res,
        "isBanned": is_current_user_banned,
        "serverHash": servers_hash[servers_id.index(server_id)][server_id]
    }
    
@app.route("/ban_user")
def ban() -> dict:
    try:
        uname = request.json['username']

        if "server_id" in request.json:
            server_id = str(request.json['server_id'])

        with sq.connect("Messenger.db") as conn:
            cur = conn.cursor()
            if "server_name" in request.json:
                server_name = request.json["server_name"]
                server_id = str(cur.execute(f"SELECT server_id FROM servers WHERE server_name = '{server_name}'").fetchone()[0])
            server_id_ = cur.execute(
                    f"SELECT servers_id FROM `users` WHERE `username` LIKE '%{uname}%' ").fetchone()[0].split().index(server_id)
            is_banned = cur.execute(
                    f"SELECT `isBanned` FROM `users` WHERE `username` LIKE '%{uname}%' ").fetchone()[0].split()
            # convert to int
            # !
            # convert from true/false to 0/1
            # convert to string
            is_banned[server_id_] = (str( int( not( int(is_banned[server_id_]) ) ) ))

            is_banned_to_str = " ".join(is_banned)

            cur.execute(
                f"UPDATE users SET isBanned='{is_banned_to_str}' WHERE `username` LIKE '%{uname}%'")
            conn.commit()
    except:
        return {
            "someProblems": True
            }
    return {
        "ok": True
        }

@app.route("/disconnect")
def disconnect() -> dict:
    uname = request.json['username']
    server_id = str(request.json['server_id'])

    with sq.connect("Messenger.db") as conn:
        try:
            cur = conn.cursor()

            server_id_ = cur.execute(
                    f"SELECT servers_id FROM `users` WHERE `username` LIKE '%{uname}%' ").fetchone()[0].split().index(server_id)
            is_online = cur.execute(
                    f"SELECT isOnline FROM `users` WHERE `username` LIKE '%{uname}%' ").fetchone()[0].split()
            last_seen = cur.execute(
                    f"SELECT `lastSeen` FROM `users` WHERE `username` LIKE '%{uname}%' ").fetchone()[0].split()
            time_spent = cur.execute(
                    f"SELECT `timeSpent` FROM `users` WHERE `username` LIKE '%{uname}%' ").fetchone()[0].split()
            entry_time =cur.execute(
                    f"SELECT `entryTime` FROM `users` WHERE `username` LIKE '%{uname}%' ").fetchone()[0].split()
            is_online[server_id_] = '0'
            time_spent[server_id_] = str(float(time_spent[server_id_]) + time.time() - float(entry_time[server_id_]))
            last_seen[server_id_] = str(time.time())

            is_online_to_str = " ".join(is_online)
            last_seen_to_str = " ".join(last_seen)
            time_spent_to_str = " ".join(time_spent)

            cur.execute(
                f"UPDATE `users` SET `timeSpent`='{time_spent_to_str}', `isOnline`='{is_online_to_str}', `lastSeen`='{last_seen_to_str}' WHERE `username` LIKE '%{uname}%';")
            conn.commit()
        except Exception as e:
            return {
                "someProblems": True
            }

    servers_id = [get_key(servers_hash[i].keys()) for i in range(len(servers_hash))]
    server_id = int(server_id)

    if server_id in servers_id:
        servers_hash[servers_id.index(server_id)][server_id] = generate_random_hash()
    else:
        servers_hash.append(
            {
                server_id: generate_random_hash()
            })

    return {
        "ok": True
    }


if __name__ == '__main__':
    app.run(debug=True)