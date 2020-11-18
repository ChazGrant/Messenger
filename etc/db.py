import sqlite3 as sq
import time
import hashlib

conn = sq.connect("Messenger.db")
cur = conn.cursor()
s = cur.execute(f"SELECT servers_id FROM `users` WHERE username='qwerty'").fetchone()[0].split()
if '1' in s:
    print(True)