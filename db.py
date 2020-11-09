import sqlite3 as sq
import time
import hashlib

conn = sq.connect("Messenger.db")
cur = conn.cursor()
cur.execute(
'''
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        username TEXT, 
        password TEXT,
        isOnline INTEGER DEFAULT 0);
'''
)
username = input("Введите имя пользователя: ")
password = hashlib.md5(input("Введите пароль: ").encode()).hexdigest()
if cur.execute(f"SELECT user_id FROM users WHERE username='{username}' AND password='{password}';").fetchone():
    input("Выберите сервер: ")
    res = cur.execute(f"UPDATE users SET isOnline=1 WHERE username='{username}';")
    conn.commit()
else:
    print("Беды")

#cur.execute("INSERT INTO users(username, password) VALUES(?, ?);", (username, password))
#cur.execute("DROP TABLE servers;")
#conn.commit()
#cur.executemany("INSERT INTO messages(username, text, timestamp, server_id) VALUES(?, ?, ?, ?);", [('Jack', 'HelloWorld', time.time(), 1)])
#conn.commit()
#print(cur.execute("SELECT * FROM servers;").fetchall())

#inf = [('JustTalking', 'Jack')]
#cur.executemany("INSERT INTO servers(server_name, admin) VALUES(?, ?);", inf)
#conn.commit()
#print(cur.execute("SELECT * FROM servers;").fetchall())