'''
Тут должны в цикле показываться все сервера
Должна быть кнопка создать сервер
На каждом сервере показывается сколько участников
'''
import LobbyUI
from PyQt5 import QtWidgets, QtCore, Qt
from PyQt5.QtWidgets import QMessageBox, QVBoxLayout, QPushButton, QInputDialog, QLineEdit
import requests
from Chat import Chat
import sqlite3 as sq
import hashlib

class Lobby(QtWidgets.QMainWindow, LobbyUI.Ui_MainWindow):
    def __init__(self, username='qwerty', password=1234, url='http://127.0.0.1:5000'):
        super().__init__()
        self.url = url
        self.setupUi(self)
        self.username = username
        self.updateButton.pressed.connect(self.update)
        self.scrollArea.setAlignment(QtCore.Qt.AlignTop)
        self.scrollArea.setWidgetResizable(False)
        self.update()

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

    def update(self):
        request = requests.get(self.url + "/get_servers")
        if "someProblems" in request.json():
            return self.showError("Проблемы с сервером")
        res = request.json()['servers']
        self.layout = QVBoxLayout()
        print(res)
        for i in range(10):
            button = QPushButton(res[0][1], self)
            button.setFixedSize(186, 30)
            button.pressed.connect(lambda: self.connect(res[0][0]))
            self.layout.addWidget(button)
        w = Qt.QWidget()
        w.setLayout(self.layout)
        self.scrollArea.setWidget(w)
            
    def connect(self, id):
        serverPassword, okPressed = QInputDialog.getText(self, "Get text","Введите пароль:", QLineEdit.Normal, "")
        if okPressed:
            response = requests.get(self.url + "/connect", 
                json=
                {
                    'username': self.username,
                    'server_id': id,
                    'password': serverPassword
                })
            if response.status_code == 200:
                if "badPassword" in response.json():
                    return self.showError("Неверный пароль")

                if "someProblems" in response.json():
                    return self.showError("Беды с базой")
                
                self.close()
                self.main = Chat(self.username, self.url, id)
                return self.main.show()
            else:
                self.showError("Беды с сервером")
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = Lobby()
    window.show()
    app.exec_()
