import requests
import os
import json
import sqlite3 as sq
from crypt import encrypt, decrypt
import random
import hashlib

with open("userdata/data.json", "w") as js:
        js.write("")

with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO sessions(`username`, `hash`) VALUES(?, ?)",
                    ("ff", "ff"))
        conn.commit()


# with sq.connect("Messenger.db") as conn:
#         cur = conn.cursor()
#         isUsernameIsInUse = cur.execute(f"SELECT `session_id` FROM sessions WHERE `username` LIKE '%ff%'").fetchone()
#         if isUsernameIsInUse:
#             print("?f")
