from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QListView
from PyQt5.QtCore import QPoint
from Chat import Chat
import AuthUI
import MainUI
import requests
import hashlib
import datetime
from crypt import *


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
        delta = QPoint(event.globalPos() - self.oldPos)
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
        response = requests.get(self.__url + '/login',  # Передаём логин и пароль на сервер
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

            self.close()  # Закрываем текущее окно
            # Инициализируем новое окно, передавая логин и пароль
            self.main = Chat(self._username, self.__password, self.__url)
            return self.main.show()  # Открываем инициализированное окно

        else:
            self.showError(
                "При попытке подключиться к серверу возникла ошибка")
            return self.close()


class Chat(QtWidgets.QMainWindow, MainUI.Ui_MainWindow):
    def __init__(self, username='Jack', password=1234, url='http://127.0.0.1:5000', server_id=1):
        super().__init__()
        self.setupUi(self)
        self.pushButton.pressed.connect(self.send_message)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)
        self._timestamp = 0.0
        self._username = username
        self._password = password
        self.__key = 314
        self.__url = url
        self.__server_id = server_id

    def removeSpaces(self, string):
        '''
        Удаляет все пустые символы в строке
        '''
        for n in string:
            string = string.lstrip(' ')
            string = string.rstrip(' ')
            string = string.lstrip('\t')
            string = string.rstrip('\t')
            string = string.lstrip('\n')
            string = string.rstrip('\n')
        return string

    def showError(self, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(text)
        msg.setWindowTitle("Error")
        msg.exec_()

    # Переопределяем метод выхода из приложения
    def closeEvent(self, event):
        self.disconnect()
        self.close()
        self.main = Auth()
        self.main.show()
        return event.accept()

    def update(self):
        responseUsers = requests.get(
            self.__url + '/get_users',
            json={
                "server_id": self.__server_id
            })
        res = responseUsers.json()['res']
        self.listWidget.clear()
        for i in res:
            status = "Online" if i[1] else "Offline"
            self.listWidget.addItem(i[0] + f' ({status})')
        response = requests.get(
            self.__url + '/get_messages',
            params={
                'after': self._timestamp,
                'server_id': self.__server_id
            })

        if response.status_code == 200:
            messages = response.json()['messages']
            for message in messages:
                ###
                # 0 - имя пользователя
                # 1 - сообщение
                # 2 - время
                ###
                dt = datetime.datetime.fromtimestamp(
                    message[2]).strftime('%H:%M')

                self.textBrowser.append(dt + " " +
                                        message[0] + ": " + decrypt(message[1], self.__key))
                self.textBrowser.append("")
                self._timestamp = message[2]
        else:
            self.showError(
                "При попытке подключиться к серверу возникли ошибки")
            return self.close()

    def send_message(self):
        text = self.removeSpaces(self.textEdit.toPlainText())
        if len(text) > 100:
            return self.showError("Длина сообщения должна быть не более 100")
        response = requests.get(
            self.__url + '/send_message',
            json={
                'username': self._username,
                'text': encrypt(text, self.__key),
                'server_id': self.__server_id,
            }
        )
        print(response)
        if response.status_code == 200:
            try:
                if response.json()['blankMessage']:
                    self.showError("Сообщение не может быть пустым")
            except:
                pass
            return self.textEdit.setText("")
        else:
            self.showError("Ошибка в подключении к серверу")
            return self.close()

    def disconnect(self):
        return requests.get(
            self.__url + "/disconnect",
            json={
                "username": self._username
            }
        )


app = QtWidgets.QApplication([])
window = Auth()
window.show()
app.exec_()