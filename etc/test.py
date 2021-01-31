import requests
import sqlite3 as sq
import re
import datetime
import time
import hashlib
import os



# pattern = r"^(?=.*[\W].*)(?=.*[0-9].*)(?=.*[a-zA-Z].*)[0-9a-zA-Z\W]{8,16}?$"
# if re.sub(" ", "", passw) == passw:
#     if re.match(pattern, passw):
#         print("OK")

print(os.getcwd())

filesList = [f for _, _, f in os.walk(os.getcwd() + "/static" + "/JUST TALKING")][0]


print(filesList)
with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        print(cur.execute(
            f"SELECT `server_name` FROM servers WHERE `server_id` = 1").fetchone()[0])
exit()
f = [1,5,6,2]

j = [5,4]

print(f+j)

# print(hashlib.md5("".encode()).hexdigest())
# currentDate = datetime.datetime.fromtimestamp(time.time())
# print(time.time())
# print(currentDate.year)

# firstDate = datetime.datetime.fromtimestamp(time.time())
# secondDate = datetime.datetime.fromtimestamp(time.time() + 15)
# print(firstDate.month)