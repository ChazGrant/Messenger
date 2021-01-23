import downloadUI
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox, QAbstractItemView, QDialog, QLabel, QVBoxLayout, QPushButton
import requests
import os

URL = "http://127.0.0.1:5000"


def showError(text):
    '''
    Создаёт окно с ошибкой и выводит текст
    '''
    msg = QtWidgets.QMessageBox()
    msg.setWindowTitle("Ошибка")
    msg.setIcon(QMessageBox.Critical)
    msg.setText(text)
    msg.setWindowTitle("Error")
    msg.exec_()


class download(QtWidgets.QMainWindow, downloadUI.Ui_Form):
    def __init__(self, items):
        super().__init__()
        self.setupUi(self)
        self.items = items
        self.isCancelled = False

        self.browser = QtWidgets.QTextBrowser()
        # self.listWidget.setSelectionMode(QAbstractItemView.MultiSelection)

        self.selectButton.pressed.connect(
            self.download)

        for i in items:
            self.listWidget.addItem(i)

    def download(self):
        neededFiles = list()

        for item in self.listWidget.selectedItems():
            neededFiles.append(item.text())

        resp = requests.get(URL + "/download", json={
            "neededFile": neededFiles[0]
        })

        filesList = [f for _, _, f in os.walk(os.getcwd() + "/Загрузки")][0]

        for file in filesList:
            if neededFiles[0] == file:
                self.dial = QDialog(self)
                label = QLabel(
                    text="Данный файл уже скачан\nВы уверены, что хотите перезаписать данные?")
                accept = QPushButton(text="Да")
                decline = QPushButton(text="Нет")

                accept.pressed.connect(lambda: self.dial.close())
                decline.pressed.connect(lambda: self.decline())

                self.dial.setLayout(QVBoxLayout())
                self.dial.layout().addWidget(label)
                self.dial.layout().addWidget(accept)
                self.dial.layout().addWidget(decline)
                self.dial.setFixedSize(310, 150)
                self.dial.exec_()

        if not self.isCancelled:
            with open("Загрузки/" + str(neededFiles[0]), "wb") as file:
                file.write(resp.content)
            showError("Ваш файл был успешно скачан")
        self.isCancelled = False

    def decline(self):
        self.dial.close()
        self.isCancelled = True


app = QtWidgets.QApplication([])
allFiles = requests.get(URL + "/get_files").json()['allFiles']
main = download(allFiles)
main.show()
app.exec_()
