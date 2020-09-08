from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox
from crypt import encrypt, decrypt
import MainUI
import requests
import datetime


class Chat(QtWidgets.QMainWindow, MainUI.Ui_MainWindow):
    def __init__(self, username='Jack', password=1234):
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
        response = requests.get(
                'http://127.0.0.1:5000/get_messages',
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
        print(text, "f")
        response = requests.get(
            'http://127.0.0.1:5000/send_message',
            json={
                'username': self.username,
                'text': encrypt(text, self.key), }
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


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = Chat()
    window.show()
    app.exec_()
