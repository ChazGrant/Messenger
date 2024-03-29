from PyQt5 import QtWidgets
from PyQt5 import QtCore
import AdminUI
import userCreatorUI
import requests
import time
import datetime

def calculateTime(time):
    tm = float(time)

    hours = int(tm / (3600))
    strhours = str(hours)
    if len(strhours) == 1:
        strhours = "0" + strhours

    mins = int( (tm - (hours * 3600) ) / 60)
    strmins = str(mins)
    if len(strmins) == 1:
        strmins = "0" + strmins

    secs = int(tm - hours * 3600 - mins * 60)
    strsecs = str(secs)
    if len(strsecs) == 1:
        strsecs = "0" + strsecs

    return strhours + ":" + strmins + ":" + strsecs

class adminPanel(QtWidgets.QMainWindow, AdminUI.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.banButton.pressed.connect(self.banUser)
        self.createUserButton.pressed.connect(self.createUser)
        self.exitButton.pressed.connect(self.close)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.tree.setHeaderLabels(['Пользователи в данном чате'])
        res = requests.get("http://127.0.0.1:5000/get_users", json={
                              "server_id": '1'
                          })
        # self.tree.addTopLevelItem(QtWidgets.QTreeWidgetItem(["fae", "qwe"]))
        '''
            0 - username
            1 - isOnline
            2 - lastSeen
            3 - entryTime
            4 - timeSpent
        '''
        users = res.json()['res']
        for user in users:
            u = user.split()
            status = "Online" if int(u[1]) else "Offline"
            us = QtWidgets.QTreeWidgetItem(self.tree, [u[0]])
            
            QtWidgets.QTreeWidgetItem(us, [f"Статус: {status}"])
            QtWidgets.QTreeWidgetItem(us, [f"Последнее время входа: {datetime.datetime.fromtimestamp(float(u[2])).strftime('%H:%M:%S %d/%m/%y')}"])
            if int(u[1]):
                totalTime = (
                        float(u[4]) + time.time() - float(u[3]))
                QtWidgets.QTreeWidgetItem(us, [f"Общее время онлайн: {calculateTime(totalTime)}"])
            else:
                QtWidgets.QTreeWidgetItem(us, [f"Общее время онлайн: {calculateTime(float(u[4]))}"])


    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QtCore.QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def banUser(self):
        if not (self.tree.selectedItems()):
            return
        if not (self.tree.selectedItems()[0].parent()):
            print(self.tree.selectedItems()[0].text(0) + " был забанен")
            self.tree.invisibleRootItem().removeChild(self.tree.selectedItems()[0])
    
    def createUser(self):
        self.main = userCreatorForm()
        # self.main.setFixedSize()
        self.main.show()
        
class userCreatorForm(QtWidgets.QMainWindow, userCreatorUI.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.createButton.pressed.connect(self.createUser)
        self.exitButton.pressed.connect(self.close)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QtCore.QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def createUser(self):
        if self.usernameText.text() == "" or self.passwordText.text() == "":
            print("Не все поля заполнены")
        else:
            # Проверка на занятое имя
            if self.issueAdminRights.isChecked():
                print("Создан админ")
            else:
                print("Создан обычный пользователь")

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = adminPanel()
    window.show()
    app.exec_()