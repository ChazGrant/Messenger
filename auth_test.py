from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMessageBox, QVBoxLayout, QListView, QTextBrowser, QPushButton, QInputDialog, QLineEdit, QDialog, QLabel, QFrame, QAbstractItemView
from PyQt5.QtCore import QPoint, QThread, pyqtSignal

import AuthUI

import json
import requests
import hashlib
import datetime
import time
import os
import re
from crypt import encrypt, decrypt

URL = "http://127.0.0.1:5000"
USERNAME = "CREATOR"
KEY = 314

def show_message(text: str) -> None:
    '''
    Создаёт окно с ошибкой и выводим текст
    '''
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(text)
    msg.setWindowTitle("Info")
    msg.exec_()








app = QtWidgets.QApplication([])
window = Auth()
window.show()
app.exec_()