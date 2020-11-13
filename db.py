import sqlite3 as sq
import time
import hashlib

conn = sq.connect("Messenger.db")
cur = conn.cursor()