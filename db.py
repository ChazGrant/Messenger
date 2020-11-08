import sqlite3 as sq
import time

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
#cur.execute("DROP TABLE servers;")
#conn.commit()
#cur.executemany("INSERT INTO messages(username, text, timestamp, server_id) VALUES(?, ?, ?, ?);", [('Jack', 'HelloWorld', time.time(), 1)])
#conn.commit()
#print(cur.execute("SELECT * FROM servers;").fetchall())

#inf = [('JustTalking', 'Jack')]
#cur.executemany("INSERT INTO servers(server_name, admin) VALUES(?, ?);", inf)
#conn.commit()
#print(cur.execute("SELECT * FROM servers;").fetchall())