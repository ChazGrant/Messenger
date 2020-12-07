import requests
import sqlite3 as sq
import re

passw = "Nik@0595"

pattern = r"^(?=.*[\W].*)(?=.*[0-9].*)(?=.*[a-zA-Z].*)[0-9a-zA-Z\W]{8,16}?$"
if re.sub(" ", "", passw) == passw:
    if re.match(pattern, passw):
        print("OK")



