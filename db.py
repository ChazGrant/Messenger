import sqlite3 as sq
import time
import hashlib

conn = sq.connect("Messenger.db")
cur = conn.cursor()
cur.execute("UPDATE servers SET `server_name`='JUST TALKING' WHERE `server_id` = '1';")
conn.commit()
print(cur.execute("SELECT * FROM servers;").fetchall())