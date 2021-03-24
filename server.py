from flask import Flask, request, send_from_directory
from datetime import datetime
import hashlib
import time
import re
from crypt import *
from bot import *
import sqlite3 as sq
import os
import zipfile
import random



ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

app = Flask(__name__)
server_start = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
last_timestamps = dict()

isLoggedIn = {
    1: [
        {
            23: 1
        },
        {
            2: 1
        }
    ]
}

privateChats = dict()
invitesToChat = []

userIsLoggedIn = dict()

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def parse_keys(keys):
    keys = str(keys)
    return int(keys[keys.index("[") + 1:keys.index("]")])

def hash_(text):
    return hashlib.md5(text.encode()).hexdigest()

def get_server_name_(server_id):
    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        server_name = cur.execute(
            f"SELECT server_name FROM `servers` WHERE `server_id`={server_id}").fetchone()[0]
        return server_name

def get_chat_name_(chat_id):
    with sq.connect("Messenger.db") as conn:
            cur = conn.cursor()
            chatName = cur.execute(f"SELECT `chatName` FROM chats WHERE `chat_id` = {request.json['chat_id']}").fetchone()[0]
            return chatName


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
    servName = request.json['serverName']
    servPass = request.json['serverPassword']
    servAdmin = request.json['username']
    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        serverNames = cur.execute(
            "SELECT `server_name` FROM servers").fetchall()
        for serverName in serverNames:
            if servName in serverName:
                return {"nameIsTaken": True}
        cur.execute("INSERT INTO servers(`server_name`, `admins`, `users`, `start_time`, `password`) VALUES(?, ?, ?, ?, ?)",
                    (servName, servAdmin, servAdmin, time.time(), hash_(servPass)))
        conn.commit()

        server_id = cur.execute(f"SELECT server_id FROM `servers` WHERE `server_name` LIKE '%{servName}%'").fetchone()

        os.mkdir("static/" + str(servName))

        return {"server_id": server_id}
    return {"someProblems": True}
    '''
Название сервера, дата запуска, админ
    '''

# Проверить обновляются ли юзеры на разных серверах
@app.route("/connect")
def connect():
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
                return {"badPassword": True}
        except:
            return {"someProblems": True}

    for us in isLoggedIn[int(server_id)]:
        us[parse_keys(us.keys())] = 1

    return {
        "ok": True
    }


@app.route("/login")
def login():
    username = request.json['username']
    password = request.json['password']
    if username == "" or password == "":
        return {'isNotFilled': True}
    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        if cur.execute(f"SELECT user_id from users WHERE `username`='{username}' AND `password`='{hash_(password)}';").fetchone():
            return {'ok': True}
        return {'invalidData': True}

@app.route("/create_user")
def create_user():
    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        username = request.json['username']
        password = request.json['password']
        server_id = request.json['server_id']

        pattern = r"^(?=.*[\W].*)(?=.*[0-9].*)(?=.*[a-zA-Z].*)[0-9a-zA-Z\W_]{8,16}?$"
        password = re.sub(r"[\s]+", "_", password)

        if username == "" or password == "":
            return {'isNotFilled': True}
        if cur.execute(f"SELECT `username` FROM `users` WHERE `username`='{ username }';").fetchone():
            return {'nameIsTaken': True}
        if re.match(pattern, password):
            cur.execute(
                "INSERT INTO users(`username`, `password`, `isOnline`, `servers_id`, `lastSeen`, `entryTime`, `timeSpent`, `isBanned`) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",\
                    (username, hash_(password), '0', server_id, str(time.time()), str(time.time()), '0.0', '0'))
            conn.commit()
            
            return {'ok': True}
    return {"badPassword": True}

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
            return {'isNotFilled': True}
        if cur.execute(f"SELECT `username` FROM `users` WHERE `username`='{ username }';").fetchone():
            return {'nameIsTaken': True}
        if re.match(pattern, password):
            cur.execute(
                "INSERT INTO users(`username`, `password`) VALUES(?, ?)", (username, hash_(password)))
            conn.commit()
            return {'ok': True}
    return {"badPassword": True}


@app.route("/send_message")
def send_message():
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

    return {
        'ok': True
    }


@app.route("/get_server_name")
def get_server_name():
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
        'rightsGranted': str(username) in admins or str(username) == "CREATOR"
        }

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


@app.route("/upload")
def upload():
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
            chatName = cur.execute(f"SELECT `chatName` FROM chats WHERE `chat_id` = {chat_id}").fetchone()[0]
            files = [f for _, _, f in os.walk("static/" + str(chatName))]

            if files:
                files = files[0]
            else:
                pass

            for file in files:
                if file == filename:
                    return {
                        "nameIsTaken": True
                    }
            with open("static/privateChats/" + chatName + "/" + filename, "wb+") as file:
                file.write(data)


    if not server_id:
        files = [f for _, _, f in os.walk("static")][0]
    else:
        files = [f for _, _, f in os.walk("static/" + str(server_name))][0]

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

    return {"ok": True}

# Можно вернуть либо один файл, либо архивом несколько
@app.route("/download")
def download():
    neededFile = request.json["neededFile"]

    if "chat_id" in request.json: 
        chatName = get_chat_name_(request.json["chat_id"])

        filesList = [f for _, _, f in os.walk("static/privateChats/" + chatName)]

    else:
        if "server_id" in request.json:
            server_name = get_server_name_(request.json['server_id'])
        else:
            server_id = 0

        if not server_id:
            filesList = [f for _, _, f in os.walk("static/")]
        else:
            filesList = [f for _, _, f in os.walk("static/" + str(server_name))]


    for file in filesList:
        if neededFile == file:
            if server_id:
                return send_from_directory(directory="static/" + str(server_name), filename=file, as_attachment=True)
            else:
                return send_from_directory(directory="static/", filename=file, as_attachment=True)

@app.route("/get_files")
def get_files():
    if "server_id" in request.json:
        server_id = request.json['server_id']
    else:
        server_id = 0
    
    if "chat_id" in request.json:
        chatName = get_chat_name_(request.json["chat_id"])
        files = [f for _, _, f in os.walk("static/privateChats/" + chatName)]

        if files:
            files = files[0]
        else:
            pass

        return {
            "allFiles": files
        }

    if not server_id:
        files = [f for _, _, f in os.walk("static")][0]

    else:
        server_name = get_server_name_(server_id)
        files = [f for _, _, f in os.walk("static/" + str(server_name))][0]

    if files:
        files = files[0]
    else:
        pass

    return {
        "allFiles": files
    }

@app.route("/get_chat_id")
def get_chat_id():
    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        users = request.json["users"]
        usersReversed = request.json["usersReversed"]

        res = cur.execute(f"SELECT `chat_id` FROM chats WHERE `chatName` LIKE '%{users}%' OR `chatName` LIKE '%{usersReversed}%'").fetchone()
        if res:
            return {
                "chat_id": res[0]
            }
        else:
            os.mkdir("static/privateChats/" + users)
            cur.execute("INSERT INTO chats(`chatName`) VALUES(?)", (users, ))
            conn.commit()
            res = cur.execute(f"SELECT `chat_id` FROM chats WHERE chatName LIKE '%{users}%' OR chatName LIKE '%{usersReversed}%'").fetchone()
            return {
                "chat_id": res[0]
            }

@app.route("/send_private_message")
def send_private_message():
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
    except Exception as e:
        return {
            "someProblems": str(e)
        }

@app.route("/get_private_messages")
def get_private_messages():
    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        after = float(request.args['after'])
        chat_id = str(request.args['chat_id'])
        try:
            if last_timestamps[chat_id] >= after:
                res = cur.execute(
                    f"SELECT `username`, `text`, `timestamp` FROM `chatMessages` WHERE `timestamp` > {after} AND `chat_id` = {int(chat_id)};").fetchall()
                return {
                    'messages': res
                }
            else:
                return {
                    'messages': []
                }
        except:
            last_timestamps[chat_id] = after
            res = cur.execute(
                f"SELECT `username`, `text`, `timestamp` FROM `chatMessages` WHERE `timestamp` > {after} AND `chat_id` = {int(chat_id)};").fetchall()

            return {
                'messages': res
            }

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
                    'messages': res,
                }
            else:
                return {
                    'messages': [],
                }
        except:
            last_timestamps[server_id] = after
            res = cur.execute(
                f"SELECT `username`, `text`, `timestamp` FROM `messages` WHERE `timestamp` > {after} AND `server_id` = {server_id};").fetchall()
            return {
                'messages': res,
            }

############# SESSION #################
@app.route("/create_session")
def create_session():
    try:
        username = request.json["username"]
        usernameForHash = username

        with sq.connect("Messenger.db") as conn:
            cur = conn.cursor()
            isUsernameInUse = cur.execute(f"SELECT `session_id` FROM sessions WHERE `username` LIKE '%{username}%'").fetchone()

            for i in range(16):
                usernameForHash += random.choice(ALPHABET)
            saltedHash = hashlib.md5(usernameForHash.encode()).hexdigest()

            if isUsernameInUse:
                cur.execute(f"UPDATE sessions SET `hash` = '{saltedHash}' WHERE `username` LIKE '%{username}%'").fetchone()
                conn.commit()
            else:
                cur.execute("INSERT INTO sessions(`username`, `hash`) VALUES(?, ?)", (username, saltedHash))
                conn.commit()
            
            return {
                "hash": encrypt(saltedHash, 314)
            }

    except Exception as e:
        return {
            "someProblems": str(e)
        }

@app.route("/check_for_session")
def check_for_session():
    username = decrypt(request.json["username"], 314)
    saltedHash = decrypt(request.json["hash"], 314)

    with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        isValid = cur.execute(f"SELECT `session_id` FROM sessions WHERE `username` LIKE '%{username}%' AND `hash` LIKE '%{saltedHash}%'").fetchone()

        return {"username": username} if isValid else {"badHash": True}

############# SESSION #################

@app.route("/get_users")
def get_users():
    with sq.connect("Messenger.db") as conn:
        server_id = str(request.json["server_id"])
        cur = conn.cursor()

        isLogged = 0
        isCurrentUserBanned = 0

        try:
            
            username = str(request.json["username"])
            
            user_id = cur.execute(
                f"SELECT `user_id` FROM users WHERE `username` LIKE '%{username}%';"
            ).fetchone()[0]
            
            isFound = False
            
            for i in isLoggedIn[int(server_id)]:
                if user_id == parse_keys(i.keys()):
                    isFound = True

            if not isFound:
                isLoggedIn[int(server_id)].append({
                    int(user_id): 1})

            for us in isLoggedIn[int(server_id)]:
                if int(user_id) == parse_keys(us.keys()):
                    isLogged = us[parse_keys(us.keys())]
                    us[parse_keys(us.keys())] = 0
                    break
            
            server_id_ = cur.execute(
                f"SELECT servers_id FROM `users` WHERE `username` LIKE '%{username}%' ").fetchone()[0].split().index(server_id)
            userIsBanned = cur.execute(
                f"SELECT `isBanned` FROM users WHERE `username` LIKE '%{username}%'").fetchone()[0].split()
            isCurrentUserBanned = int(userIsBanned[server_id_])
        except:
            pass


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
        'res': res,
        'userIsLoggedIn': isLogged,
        "isBanned": isCurrentUserBanned
    }
    
@app.route("/ban_user")
def ban():
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
            isBanned = cur.execute(
                    f"SELECT `isBanned` FROM `users` WHERE `username` LIKE '%{uname}%' ").fetchone()[0].split()
            isBanned[server_id_] = (str( int( not( int(isBanned[server_id_]) ) ) ))

            isBannedToStr = " ".join(isBanned)

            cur.execute(
                f"UPDATE users SET isBanned='{isBannedToStr}' WHERE `username` LIKE '%{uname}%'")
            conn.commit()
    except Exception as e:
        return {"someProblems": str(e)}
    return {"ok": True}

@app.route("/disconnect")
def disconnect():
    uname = request.json['username']
    server_id = str(request.json['server_id'])

    with sq.connect("Messenger.db") as conn:
        try:
            cur = conn.cursor()
            # Достаём необходимые данные из БД
            server_id_ = cur.execute(
                    f"SELECT servers_id FROM `users` WHERE `username` LIKE '%{uname}%' ").fetchone()[0].split().index(server_id)
            isOnline = cur.execute(
                    f"SELECT isOnline FROM `users` WHERE `username` LIKE '%{uname}%' ").fetchone()[0].split()
            lastSeen = cur.execute(
                    f"SELECT `lastSeen` FROM `users` WHERE `username` LIKE '%{uname}%' ").fetchone()[0].split()
            timeSpent = cur.execute(
                    f"SELECT `timeSpent` FROM `users` WHERE `username` LIKE '%{uname}%' ").fetchone()[0].split()
            entryTime =cur.execute(
                    f"SELECT `entryTime` FROM `users` WHERE `username` LIKE '%{uname}%' ").fetchone()[0].split()
            isOnline[server_id_] = '0'
            timeSpent[server_id_] = str(float(timeSpent[server_id_]) + time.time() - float(entryTime[server_id_]))
            lastSeen[server_id_] = str(time.time())

            isOnlineToStr = " ".join(isOnline)
            lastSeenToStr = " ".join(lastSeen)
            timeSpentToStr = " ".join(timeSpent)

            cur.execute(
                f"UPDATE `users` SET `timeSpent`='{timeSpentToStr}', `isOnline`='{isOnlineToStr}', `lastSeen`='{lastSeenToStr}' WHERE `username` LIKE '%{uname}%';")
            conn.commit()
        except Exception as e:
            return {
                "someProblems": str(e)
            }

    for us in isLoggedIn[int(server_id)]:
        us[parse_keys(us.keys())] = 1

    return {
        "ok": True
    }


if __name__ == '__main__':
    app.run(debug=True)
