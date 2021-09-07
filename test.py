import requests
import os
import json
import sqlite3 as sq
from crypt import encrypt, decrypt
import random
import hashlib
import re

companion = "Илья"

with sq.connect("Messenger.db") as conn:
        cur = conn.cursor()
        is_online = cur.execute(f"SELECT `isOnline` FROM users WHERE `username`='{companion}'").fetchone()[0].split()

is_online = '1' in is_online

print(is_online)
