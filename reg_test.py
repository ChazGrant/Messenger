from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMessageBox, QVBoxLayout, QListView, QTextBrowser, QPushButton, QInputDialog, QLineEdit, QDialog, QLabel, QFrame, QAbstractItemView
from PyQt5.QtCore import QPoint, QThread, pyqtSignal

import AuthUI
import MainUI
import LobbyUI
import downloadUI
import AdminUI
import searchFormUI
import userCreatorUI
import SecondaryUI
import resources

import json
import requests
import hashlib
import datetime
import time
import os
import re
from crypt import encrypt, decrypt

class Auth(QtWidgets.QMainWindow, AuthUI.Ui_MainWindow):
    def __init__(self, url:str=URL, key:str=KEY) -> None:
        super().__init__()
        self.setupUi(self)

        self.oldPos = self.pos()
        self.__key = key
        self.__url = url

        # Прикрепление событий к каждой кнопке
        self.loginButton.pressed.connect(self.login)
        self.registrateButton.pressed.connect(self.registration)
        self.exitButton.pressed.connect(self.close)

        # Установка картинки для кнопки выхода
        self.exitButton.setIcon(QtGui.QIcon(":/resources/Images/cross.png"))

        # Прозрачное окно без рамок
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def save_data(self, username: str) -> int:
        response = requests.get(self.__url + "/create_session", json={
                "username": username
            })
        if "someProblems" in response.json():
            show_error("Возникли неполадки во время сохранения данных")
            return 0
        with open("userdata/data.json", "w+") as file:
            # Запись json-данных в файл 
            json.dump({
                "username": encrypt(username, self.__key),
                "hash": response.json()["hash"]
            }, file) 
            return 1

    def clear_spaces(self, string: str) -> str:
        string = string.replace(' ', '')
        string = string.replace('\n', '')
        string = string.replace('\t', '')
        return string

    def mousePressEvent(self, event):
        # Меняет позицию в зависимости куда нажали мышкой
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        # Перемещает окно в необходимое направление
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def login(self) -> None:
        ### Извлекаем имя пользователя и пароль из текстовых полей ###
        self.username = self.clear_spaces(self.usernameText.text())
        self.__password = remove_spaces(self.passwordText.text())

        # Передаём логин и пароль на сервер
        response = requests.get(self.__url + '/login',
                                json={
                                    'username': self.username,
                                    'password': self.__password
                                })

        if response.status_code == 200:
            ### Обработка ошибки пустых полей ###
            if "isNotFilled" in response.json():
                return show_error("Не все поля заполнены")

            ### Обработка ошибки неверного пароля ###
            if "invalidData" in response.json():
                return show_error("Неверное имя пользователя и/или пароль")

            self.close()
            # Попытка сохранить данные если checkbox активирован
            if self.rememberMe.isChecked():
                response = self.save_data(self.username)
                if not response:
                    show_error("Ваши данные не были сохранены")

            # Открытие окна "Lobby"
            self.main = Lobby(self.username, self.__url)
            return self.main.show()
        else:
            show_error("Ошибка в подключении к серверу")
            return self.close()

    def registration(self) -> None: