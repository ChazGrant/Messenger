from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox, QTextBrowser
from PyQt5.QtCore import QPoint
from crypt import *
import MainUI
import requests
import datetime


class Chat(QtWidgets.QMainWindow, MainUI.Ui_MainWindow):
    def __init__(self, username='Jack', url='http://127.0.0.1:5000', server_id=1):
        super().__init__()
        self.setupUi(self)

        self.sendButton.pressed.connect(self.send_message)
        self.clearMessageButton.pressed.connect(lambda: self.textEdit.setText(""))
        self.disconnectButton.pressed.connect(self.disconnect)
        self.exitAccountButton.pressed.connect(self.logOff)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.scrollArea.setAlignment(QtCore.Qt.AlignTop)
        self.scrollArea.setWidgetResizable(False)
        
        self.oldPos = self.pos()
        self._timestamp = 0.0
        self._username = username
        self.__key = 314
        self.__url = url
        self.server_id = server_id
        
        self.connect()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)
        

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

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint (event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    # Переопределяем метод выхода из приложения
    def closeEvent(self, event):
        self.exit()
        event.accept()

    def connect(self):
        try:
            response = requests.get(self.__url + "/get_server_name",
            json = {
                "server_id": self.server_id,
            })
            self.serverNameLabel.setText(response.json()['server_name'])
        except:
            self.showError("При попытке подключиться к серверу возникли ошибки")
            return self.close()

    def update(self):
        responseUsers = requests.get(
                self.__url +'/get_users',
                json=
                {
                    "server_id": self.server_id
                })
        res = responseUsers.json()['res']
        self.users = QTextBrowser()
        for i in res:
            status = "Online" if i[1] else "Offline"
            self.users.append(i[0] + f' ({status})')
        self.scrollArea.setWidget(self.users)
        response = requests.get(
                self.__url +'/get_messages',
                params={
                    'after': self._timestamp,
                    'server_id': self.server_id
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
                'server_id': self.server_id,
                }
        )
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

    def exit(self):
        return requests.get(
            self.__url + "/disconnect",
            json={
                "username": self._username
            }
        )

    # Выйти с акка
    def logOff(self):
        requests.get(
            self.__url + "/disconnect",
            json={
                "username": self._username
            }
        )
        return self.showError("Вы вышли с аккаунта и попали на форму Auth")

    # Отключиться от сервера
    def disconnect(self):
        requests.get(
            self.__url + "/disconnect",
            json={
                "username": self._username
            }
        )
        return self.showError("Вы вышли с сервера и попали на форму Lobby")

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = Chat()
    window.setFixedSize(720, 498)
    window.show()
    app.exec_()
