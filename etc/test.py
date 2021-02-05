import requests
import sqlite3 as sq
import re
import datetime
import time
import hashlib
import os
import math

def index(text, searchText):
    try:
        text.index(searchText)
        return True
    except ValueError:
        return False

def beautifyText(text, searchText):
    if searchText == "":
        raise ValueError("Пустая строка для поиска")
    currentIndex = 0
    newStr = ""
    while True:
        try:
            text[currentIndex:].index(searchText)
        except:
            break
        findIndex = text[currentIndex:].index(searchText)
        sumIndex = currentIndex + findIndex
        newStr += text[currentIndex:currentIndex + findIndex] + text[sumIndex:sumIndex + len(searchText)].upper()

        currentIndex += findIndex + 1
        
    newStr += text[currentIndex:]
    return newStr
    

string = "Выводит информацию о нужной команде"
word = "а"
print(word in string)
exit()
print(beautifyText(string, word))
exit()
newstring = string[0:string.find(word)] + string[string.find(word):string.find(word) + len(word)].upper() + string[string.find(word) + len(word):]
# print(string[0:string.find(word)])
# print(string[string.find(word):string.find(word) + len(word)].upper())
# print(string[string.find(word) + len(word):])
print(newstring)
exit()

keyboard.add_hotkey("enter", lambda: print("ffffffffffffffffffffffffffffffffffffffffffffff\nffffffffffffffffffffffffffffffff"))
while True:
    print("f")
exit()
print(time.time())

'''
time_spent
disconnected -> time_spent = current_time - entry_time
connected -> entry_time = current_time
admin -> time_spent_for_user -> current_time - entry_time + time_spent
'''
# 3600sec -> 1 hour
# 360sec -> 1 min
tm = float('3668.72721290')

hours = int(tm / (3600))
strhours = str(hours)
if len(strhours) == 1:
    strhours = "0" + strhours
mins = int( (tm - (hours * 3600) ) / 60)
strmins = str(mins)
if len(strmins) == 1:
    strmins = "0" + strmins

secs = int(tm - hours * 3600 - mins * 60)
strsecs = str(secs)
if len(strsecs) == 1:
    strsecs = "0" + strsecs

print(strhours, strmins, strsecs)
exit()
print(datetime.datetime.fromtimestamp(tm).strftime("%m"))
exit()
with sq.connect("../Messenger.db") as conn:
    cur = conn.cursor()
    print(cur.execute("SELECT * FROM users WHERE username = 'qwerty'").fetchall())
    exit()
with sq.connect("../Messenger.db") as conn:
    cur = conn.cursor()
    server_id = "1"
    uname = "qwerty"
    server_id_ = cur.execute(
            f"SELECT servers_id FROM `users` WHERE `username` LIKE '%{uname}%' ").fetchone()[0].split().index(server_id)
    isOnline = cur.execute(
            f"SELECT isOnline FROM `users` WHERE `username` LIKE '%{uname}%' ").fetchone()[0].split()
    entryTime = cur.execute(
            f"SELECT `lastSeen` FROM `users` WHERE `username` LIKE '%{uname}%' ").fetchone()[0].split()
    isOnline[server_id_] = '1'
    entryTime[server_id_] = str(time.time())

isOnlineToStr = ""
lastSeenToStr = ""
for s in isOnline:
    isOnlineToStr += s + " "
for s in entryTime:
    lastSeenToStr += s + " "
print(isOnlineToStr)
print(lastSeenToStr)

exit()


exit()

# pattern = r"^(?=.*[\W].*)(?=.*[0-9].*)(?=.*[a-zA-Z].*)[0-9a-zA-Z\W]{8,16}?$"
# if re.sub(" ", "", passw) == passw:
#     if re.match(pattern, passw):
#         print("OK")
exit()
print(time.time())

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