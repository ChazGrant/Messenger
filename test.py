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


print(hashlib.md5("".encode()).hexdigest())