from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QPoint
from Chat import Chat
import AuthUI
import requests
import hashlib


class Auth(QtWidgets.QMainWindow, AuthUI.Ui_MainWindow):
    def __init__(self, url='http://127.0.0.1:5000'):
        super().__init__()
        self.setupUi(self)
        self.oldPos = self.pos()
        self.__url = url
        self.loginButton.pressed.connect(self.login)
        self.registrateButton.pressed.connect(self.registration)
        self.exitButton.pressed.connect(self.close)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def removeSpaces(self, string):
        '''
        Удаляет все пустые символы в строке
        '''
        for n in string:
            string = string.lstrip(' ')
            string = string.rstrip(' ')
            string = string.lstrip('\n')
            string = string.rstrip('\n')
            string = string.rstrip('\t')
            string = string.rstrip('\t')
        return string

    def clearSpaces(self, string):
        string = string.replace(' ', '')
        string = string.replace('\n', '')
        string = string.replace('\t', '')
        return string

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint (event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()
    
    def showError(self, text):
        '''
        Создаёт окно с ошибкой и выводим текст
        '''
        msg = QMessageBox()
        msg.setWindowTitle("Ошибка")
        msg.setIcon(QMessageBox.Critical)
        msg.setText(text)
        msg.setWindowTitle("Error")
        msg.exec_()

    def login(self):
        ### Извлекаем имя пользователя и пароль из текстовых полей ###
        self._username = self.clearSpaces(self.usernameText.text())
        self.__password = self.removeSpaces(self.passwordText.text())
        response = requests.get(self.__url + '/login', # Передаём логин и пароль на сервер
                                json={
                                    'username': self._username,
                                    'password': (self.__password)
                                })

        if response.status_code == 200:
            ### Обработка ошибки пустых полей ###
            if "isNotFilled" in response.json():
                return self.showError("Не все поля заполнены")

            ### Обработка ошибки неверного пароля ###
            if "invalidData" in response.json():
                    return self.showError("Неверное имя пользователя и/или пароль")

            self.close()
            self.main = Chat(self._username, self.__password, self.__url)
            return self.main.show()

        else:
            self.showError("Ошибка в подключении к серверу")
            return self.close()

    def registration(self):
        self._username = " ".join(self.usernameText.text().split())
        self.__password = self.passwordText.text()
        response = requests.get(self.__url + '/reg',
                                    json={
                                        'username': self._username,
                                        'password': self.__password
                                    })
        if response.status_code == 200:
            if "isNotFilled" in response.json():
                    return self.showError("Не все поля заполнены")

            if "nameIsTaken" in response.json():
                    return self.showError("Данное имя пользователя уже занято")
            
            self.close() # Закрываем текущее окно
            self.main = Chat(self._username, self.__password, self.__url) # Инициализируем новое окно, передавая логин и пароль
            return self.main.show() # Открываем инициализированное окно
            
        else:
            self.showError("При попытке подключиться к серверу возникла ошибка")
            return self.close()


app = QtWidgets.QApplication([])
window = Auth()
window.show()
app.exec_()