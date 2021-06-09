import requests
import os
import json
import sqlite3 as sq
from crypt import encrypt, decrypt
import random
import hashlib
import re


def parse_keys(keys):
    keys = str(keys)
    return int(keys[keys.index("[") + 1:keys.index("]")])

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

for us in isLoggedIn[1]:
    print(us.keys())
    print(us[parse_keys(us.keys())])

# def beautifyText(text, searchText):
#     if searchText == "":
#         raise ValueError("Пустая строка для поиска")
#     currentIndex = 0
#     newStr = ""
#     while True:
#         try:
#             text[currentIndex:].index(searchText)
#         except:
#             break
#         findIndex = text[currentIndex:].index(searchText)
#         sumIndex = currentIndex + findIndex
#         newStr += text[currentIndex:sumIndex] + "<span style='color: red;'>" + text[sumIndex:sumIndex + len(searchText)] + "</span>"

#         currentIndex += findIndex + 1
#     try:
#         newStr += text[sumIndex + len(searchText):]
#     except:
#         newStr += text[len(searchText):]
#     return newStr

# print(beautifyText("Ауф".lower(), "а"))

# exit()

# def cleanhtml(raw_html):
#     cleanr = re.compile('<.*?>')
#     cleantext = re.sub(cleanr, '', raw_html)
#     return cleantext

# isLoggedIn = {
#     1: [
#         {
#             23: 1
#         },
#         {
#             2: 1
#         }
#     ]
# }

# while True:
#     print(cleanhtml(input()))
# exit()
# user_id = 14
# server_id = 1

# isFound = False

# def parse_keys(keys):
#     keys = str(keys)
#     return int(keys[keys.index("[") + 1:keys.index("]")])

# for us in isLoggedIn[int(server_id)]:
#     us[parse_keys(us.keys())] = 123

# print(isLoggedIn)
# exit()
# user_id = '23'
# server_id = 1

# for us in isLoggedIn[int(server_id)]:
#     if int(user_id) == parse_keys(us.keys()):
#         isLogged = us[parse_keys(us.keys())]
#         break

# print(isLogged)
# exit()
# for us in isLoggedIn[server_id]:
#     if str(user_id) == parse_keys(us.keys()):
#         isLogged = isLoggedIn[server_id][parse_keys(us.keys())]


# server_id = 1
# user_id= 23
# for us in isLoggedIn[server_id]:
#     us[parse_keys(us.keys())] = 0
        

# print(isLoggedIn)
# exit()
# with sq.connect("Messenger.db") as conn:
#         users = "CREATORJack"
#         usersReversed = "JackCREATOR"
#         cur = conn.cursor()
#         res = cur.execute(f"SELECT `chat_id` FROM chats WHERE chatName LIKE '%{users}%' OR chatName LIKE '%{usersReversed}%'").fetchone()
#         if res:
#             print(res)
#         else:
#             cur.execute("INSERT INTO chats(`chatName`) VALUES(?)", (users, ))
#             conn.commit()
#             print("commited")
# exit()


# with sq.connect("Messenger.db") as conn:
#         cur = conn.cursor()
#         isUsernameIsInUse = cur.execute(f"SELECT `session_id` FROM sessions WHERE `username` LIKE '%ff%'").fetchone()
#         if isUsernameIsInUse:
#             print("?f")
