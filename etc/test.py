import requests
import sqlite3 as sq
import re
import datetime
import time
import hashlib

passw = "Nik@0595"

print(hashlib.md5("Test Server".encode()).hexdigest())

# pattern = r"^(?=.*[\W].*)(?=.*[0-9].*)(?=.*[a-zA-Z].*)[0-9a-zA-Z\W]{8,16}?$"
# if re.sub(" ", "", passw) == passw:
#     if re.match(pattern, passw):
#         print("OK")

# with sq.connect("../Messenger.db") as conn:
#         cur = conn.cursor()
#         serv = cur.execute(
#             f"SELECT `users` FROM servers WHERE `server_id`=1;").fetchone()
#         for i in serv[0].split(): 
#             print(i)

