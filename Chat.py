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
        self._timestamp = 0.0
        self._username = username
        self._password = password
        self.__key = 314
        self.__url = url
        

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
        event.accept()

    def update(self):
        responseUsers = requests.get(
                self.__url +'/get_users',
                )
        responseUsers.json()['users']
        users = responseUsers.json()['users']
        isOnline = responseUsers.json()['isOnline']
        self.listWidget.clear()
        for user, x in zip(users,isOnline):
            online = "Online" if x else "Offline"
            self.listWidget.addItem(user + f' ({online})')
        response = requests.get(
                self.__url +'/get_messages',
                params={
                    'after': self._timestamp, })
                    
        if response.status_code == 200:
            messages = response.json()['messages']
            for message in messages:
                dt = datetime.datetime.fromtimestamp(
                    message['timestamp']).strftime('%H:%M:%S')
                
                self.textBrowser.append(dt + " " +
                                        message['username'] + ": " + decrypt(message['text'], self.__key))
                self.textBrowser.append("")
                self._timestamp = message['timestamp']
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
            print("Чзх")
            self.showError("Ошибка в подключении к серверу")
            return self.close()


    def disconnect(self):
        response = requests.get(
            self.__url + "/disconnect",
            json={
                "username": self._username
            }
        )

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = Chat()
    window.show()
    app.exec_()
