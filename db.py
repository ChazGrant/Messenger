import sqlite3 as sq
import time
import hashlib

conn = sq.connect("Messenger.db")
cur = conn.cursor()
serv = cur.execute(f"SELECT `server_name`, `start_time`, `users` FROM servers WHERE `server_id`=1;").fetchall()
print(serv)