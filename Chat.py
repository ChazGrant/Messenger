from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox, QListView
from crypt import *
import MainUI
import requests
import datetime

knownUsers = []

class Chat(QtWidgets.QMainWindow, MainUI.Ui_MainWindow):
    def __init__(self, username='Jack', password=1234, url='http://127.0.0.1:5000'):
        super().__init__()
        self.setupUi(self)
        self.pushButton.pressed.connect(self.send_message)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)
        self.last_timestamp = 0.0
        self.key = 314
        self.username = username
        self.password = password
        self.url = url
        

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

    def update(self):
        responseUsers = requests.get(
                self.url +'/get_users',
                )
        responseUsers.json()['users']
        users = responseUsers.json()['users']
        isOnline = responseUsers.json()['isOnline']
        usersCount = len(users)
        self.listWidget.clear()
        for user, x in zip(users,isOnline):
            online = "Online" if isOnline[x] else "Offline"
            self.listWidget.addItem(user + f' ({online})')
        '''
        for user, x in zip(users,isOnline):
            if user not in knownUsers:
                online = "Online" if isOnline[x] else "Offline"
                self.listWidget.addItem(user + f' ({online})')
                knownUsers.append(user)
            #self.listWidget.
        for known in knownUsers:
            try:
                online = "Online" if users[known]['isOnline'] else "Offline"
            except:
                pass
            '''
        response = requests.get(
                self.url +'/get_messages',
                params={
                    'after': self.last_timestamp, })
                    
        if response.status_code == 200:
            messages = response.json()['messages']
            for message in messages:
                dt = datetime.datetime.fromtimestamp(
                    message['timestamp']).strftime('%H:%M:%S')
                
                self.textBrowser.append(dt + " " +
                                        message['username'] + ": " + decrypt(message['text'], self.key))
                self.textBrowser.append("")
                self.last_timestamp = message['timestamp']
        else:
            self.showError(
                "При попытке подключиться к серверу возникли ошибки")
            return self.close()

    def send_message(self):
        text = self.removeSpaces(self.textEdit.toPlainText())
        if len(text) > 100:
            return self.showError("Длина сообщения должна быть не более 100")
        response = requests.get(
            self.url + '/send_message',
            json={
                'username': self.username,
                'text': encrypt(text, self.key), 
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


    def disconnect(self):
        response = requests.get(
            self.url + "/disconnect",
            json={
                "username": self.username
            }
        )

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = Chat()
    window.show()
    app.exec_()
