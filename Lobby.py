'''
Тут должны в цикле показываться все сервера
Должна быть кнопка создать сервер
На каждом сервере показывается сколько участников
'''
import LobbyUI
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox, QListView
import requests


class Lobby(QtWidgets.QMainWindow, LobbyUI.Ui_MainWindow):
    def __init__(self, username='Jack', password=1234, url='http://127.0.0.1:5000'):
        super().__init__()
        self.setupUi(self)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)

    def update(self):
    	request = requests.get(url + "/get_servers")


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = Lobby()
    window.show()
    app.exec_()
