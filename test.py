import requests
import os
import json
import sqlite3 as sq
from crypt import encrypt, decrypt
import random
import hashlib
import re
import pickle
import webbrowser


with open("D:/GitHub/Messenger/static/send.docx", "rb") as f:
        data = f.read()

url = 'file:///'
webbrowser.open(data, new=2)  # open in new tab