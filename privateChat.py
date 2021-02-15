import privateChatUI
from PyQt5 import QtWidgets, QtCore
import requests

URL = "http://127.0.0.1:5000"

class privateChat(privateChatUI.Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(self, username, receiver="Jack", url=URL):
        super().__init__()
        self.setupUi(self)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.__url = url
        self.username = username
        self.receiver = receiver

        response = requests.get(self.__url + "/create_private_server", json={
            "creator": self.username,
            "user": self.receiver
        })

        self.serverName = response.json()["privateServerName"]

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)

        self.exitButton.pressed.connect(self.close)
        self.sendButton.pressed.connect(self.sendMessage)

        self.oldPos = self.pos()

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QtCore.QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def sendMessage(self):
        response = requests.get(self.__url + "/send_private_message", json={
            "serverName": self.serverName,
            "username": self.username,
            "message": self.textEdit.toPlainText()
        })

        if response.status_code == 200:
            if "ok" not in response.json():
                print("Беды")
            self.textEdit.clear()


    def update(self):
        response = requests.get(self.__url + "/get_private_messages", json={
            "serverName": self.serverName
        })

        if response.status_code == 200:
            if response.json()["isLeft"]:
                return self.close()
            messages = response.json()["messages"]
            if len(messages):
                self.textBrowser.clear()
                for message in messages:
                    if message["username"] == self.username:
                        self.textBrowser.setAlignment(QtCore.Qt.AlignRight)
                    else:
                        self.textBrowser.setAlignment(QtCore.Qt.AlignRight)
                    self.textBrowser.append("<b>" + message["username"] + "</b>: " + message["message"])
                    self.textBrowser.append("")

    def closeEvent(self, event):
        # Disconnection handle
        event.accept()


app = QtWidgets.QApplication([])
window = privateChat("Jack", "Jack1")
window.show()
app.exec_()