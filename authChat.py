from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMessageBox, QVBoxLayout, QListView, QTextBrowser, QPushButton, QInputDialog, QLineEdit, QDialog, QLabel, QFrame, QAbstractItemView
from PyQt5.QtCore import QPoint, QThread, pyqtSignal

import AuthUI
import MainUI
import LobbyUI
import downloadUI
import AdminUI
import searchFormUI
import userCreatorUI
import privateChatUI
import resources

import json
import requests
import hashlib
import datetime
import time
import os
import re
from crypt import encrypt, decrypt

URL = "http://127.0.0.1:5000"
USERNAME = "CREATOR"
KEY = 314

sizes = \
{
    "Chat":
        {
            "WIDTH": 1299,
            "HEIGHT": 700 
        },
    "Lobby":
        {
            "WIDTH": 550,
            "HEIGHT": 391 
        },
    "Auth":
        {
            "WIDTH": 471,
            "HEIGHT": 531 
        },
    "adminPanel":
        {
            "WIDTH": 773,
            "HEIGHT": 464 
        },
    "downloadHub":
        {
            "WIDTH": 372,
            "HEIGHT": 317 
        },
    "searchForm":
        {
            "WIDTH": 467,
            "HEIGHT": 288 
        },
    "userCreatorForm":
        {
            "WIDTH": 441,
            "HEIGHT": 351 
        }
}

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def loadData(url):
    try:
        with open("userdata/data.json", "r") as file:
            savedData = json.load(file)
        if "hash" not in savedData:
            return 0

        response = requests.get(url + "/check_for_session", json={
            "username": savedData["username"],
            "hash": savedData["hash"]
        })
        return response.json()["username"] if "username" in response.json() else 0
    except:
        return 0

def showError(text):
    '''
    Создаёт окно с ошибкой и выводит текст
    '''
    msg = QMessageBox()
    msg.setWindowTitle("Ошибка")
    msg.setIcon(QMessageBox.Critical)
    msg.setText(text)
    msg.setWindowTitle("Error")
    msg.exec_()

def showMessage(text):
    '''
    Создаёт окно с ошибкой и выводим текст
    '''
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(text)
    msg.setWindowTitle("Info")
    msg.exec_()

def beautifyText(text, searchText):
    if searchText == "":
        raise ValueError("Пустая строка для поиска")
    currentIndex = 0
    newStr = ""
    while True:
        try:
            text[currentIndex:].lower().index(searchText.lower())
        except:
            break
        findIndex = text[currentIndex:].lower().index(searchText.lower())
        sumIndex = currentIndex + findIndex
        newStr += text[currentIndex:sumIndex] + "<span style='color: red;'>" + text[sumIndex:sumIndex + len(searchText)] + "</span>"

        currentIndex += findIndex + 1

    newStr += text[sumIndex + len(searchText):]
    return newStr

def removeSpaces(string):
    '''
    Удаляет все пустые символы в строке
    '''
    for _ in string:
        string = string.lstrip(' ')
        string = string.rstrip(' ')
        string = string.lstrip('\n')
        string = string.rstrip('\n')
        string = string.rstrip('\t')
        string = string.rstrip('\t')
    return string


class LoadMessagesThread(QThread):
    load_finished = pyqtSignal(object)

    def __init__(self, url, ts, serv_id, PM=False):
        super().__init__()

        self.url = url
        self.timestamp = ts
        self.server_id = serv_id
        self.PM = PM

    def run(self):
        try:
            if self.PM:
                rs = requests.get(self.url,
                          params={
                              'after': self.timestamp,
                              'chat_id': self.server_id
                          })
            else:
                rs = requests.get(self.url,
                            params={
                                'after': self.timestamp,
                                'server_id': self.server_id
                            })
        except:
            rs = False
        finally:
            self.load_finished.emit(rs)


class LoadUsersThread(QThread):
    load_finished = pyqtSignal(object)

    def __init__(self, url, serv_id, username):
        super().__init__()

        self.__url = url
        self.server_id = serv_id
        self.username = username

    def run(self):
        try:
            rs = requests.get(self.__url,
                          json={
                              "server_id": self.server_id,
                              "username": self.username
                          })
        except:
            rs = False
        finally:
            self.load_finished.emit(rs)


class Auth(QtWidgets.QMainWindow, AuthUI.Ui_MainWindow):
    def __init__(self, url=URL, key=KEY):
        super().__init__()
        self.setupUi(self)

        self.oldPos = self.pos()
        self.__key = key
        self.__url = url

        self.loginButton.pressed.connect(self.login)
        self.registrateButton.pressed.connect(self.registration)
        self.exitButton.pressed.connect(self.close)

        self.exitButton.setIcon(QtGui.QIcon(":/resources/Images/cross.png"))

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def saveData(self, username):
        response = requests.get(self.__url + "/create_session", json={
                "username": username
            })
        if "someProblems" in response.json():
            print(response.json()["someProblems"])
            return 0
        with open("userdata/data.json", "w+") as file:  
            json.dump({
                "username": encrypt(username, self.__key),
                "hash": response.json()["hash"]
            }, file) 
            return 1

    def clearSpaces(self, string):
        string = string.replace(' ', '')
        string = string.replace('\n', '')
        string = string.replace('\t', '')
        return string

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def login(self):
        ### Извлекаем имя пользователя и пароль из текстовых полей ###
        self.username = self.clearSpaces(self.usernameText.text())
        self.__password = removeSpaces(self.passwordText.text())

        # Передаём логин и пароль на сервер
        response = requests.get(self.__url + '/login',
                                json={
                                    'username': self.username,
                                    'password': self.__password
                                })

        if response.status_code == 200:
            ### Обработка ошибки пустых полей ###
            if "isNotFilled" in response.json():
                return showError("Не все поля заполнены")

            ### Обработка ошибки неверного пароля ###
            if "invalidData" in response.json():
                return showError("Неверное имя пользователя и/или пароль")

            self.close()
            if self.rememberMe.isChecked():
                response = self.saveData(self.username)
                if not response:
                    showError("Ваши данные не были сохранены")

            self.main = Lobby(self.username, self.__url)
            return self.main.show()
        else:
            showError("Ошибка в подключении к серверу")
            return self.close()

    def registration(self):
        self.username = " ".join(self.usernameText.text().split())
        self.__password = self.passwordText.text()
        response = requests.get(self.__url + '/reg',
                                json={
                                    'username': self.username,
                                    'password': self.__password
                                })

        if response.status_code == 200:
            if "isNotFilled" in response.json():
                return showError("Не все поля заполнены")

            if "badPassword" in response.json():
                return showError("Пароль должен иметь специальные символы, буквы и цифры. Длина пароля от 8 до 16")

            if "nameIsTaken" in response.json():
                return showError("Данное имя пользователя уже занято")

            self.close()
            
            if self.rememberMe.isChecked():
                response = self.saveData(self.username)
                if not response:
                    showError("Ваши данные не были сохранены")

            self.main = Lobby(self.username, self.__url)
            return self.main.show()
        else:
            showError(
                "При попытке подключиться к серверу возникла ошибка")
            return self.close()


class Chat(QtWidgets.QMainWindow, MainUI.Ui_MainWindow):
    def __init__(self, username=USERNAME, url=URL, server_id=1):
        super().__init__()
        self.setupUi(self)

        self.sendButton.setToolTip("Отправить")

        self.sendButton.pressed.connect(self.send_message)
        self.exitButton.pressed.connect(self.close)
        self.disconnectButton.pressed.connect(self.disconnect)
        self.exitAccountButton.pressed.connect(self.logOff)
        self.searchButton.pressed.connect(self.search)
        self.abortSearchButton.pressed.connect(self.abortSearch)
        self.downloadButton.pressed.connect(self.download)
        self.uploadButton.pressed.connect(self.upload)
        self.showUsersButton.pressed.connect(self.showUsers)
        self.backButton.pressed.connect(self.backward)
        self.forwardButton.pressed.connect(self.forward)

        self.exitButton.setIcon(QtGui.QIcon(":/resources/Images/cross.png"))
        self.showUsersButton.setIcon(QtGui.QIcon(":/resources/Images/settings.png"))
        self.backButton.setIcon(QtGui.QIcon(":/resources/Images/left.png"))
        self.forwardButton.setIcon(QtGui.QIcon(":/resources/Images/right.png"))
        self.sendButton.setIcon(QtGui.QIcon(":/resources/Images/send.png"))
        self.exitAccountButton.setIcon(QtGui.QIcon(":/resources/Images/exit_from_acc.png"))
        self.disconnectButton.setIcon(QtGui.QIcon(":/resources/Images/disconnect.png"))

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.scrollArea.setAlignment(QtCore.Qt.AlignTop)
        self.scrollArea.setWidgetResizable(False)

        self.oldPos = self.pos()
        self.timestamp = 0.0
        self.username = username
        self.previousMessages = []
        self.previousMessageDate = 0
        self.chat_id = 0
        self.__key = KEY
        self.__url = url
        self.server_id = server_id
        self.isSearchEnabled = False
        self.currentUsers = []
        self.isNotInUsers = False

        self.forwardButton.hide()
        self.backButton.hide()
        self.messagesAmount.hide()

        self.connect()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)
        # self.update()

    def checkForBoundaries(self):
        # Check for highest boundary
        if self.currentLine + 1 == self.matches:
            self.forwardButton.hide()
            if self.currentLine - 1 >= 0:
                self.backButton.show()
            return 1
        elif self.forwardButton.isHidden():
            self.forwardButton.show()

        # Check for lowest boundary
        if self.currentLine - 1 < 0:
            self.backButton.hide()
            if self.currentLine + 1 != self.matches:
                self.forwardButton.show()
            return -1
        elif self.backButton.isHidden():
            self.backButton.show()

        return 0

    def refillSearchBrowser(self):
        self.textBrowser.clear()

        self.shifts = list()

        isNewDate = 0
        currentShift = 2
        self.previousMessageDate = 0
        for searchedMessage in self.result:

            if "isNotForSearch" in searchedMessage:
                currentShift += int(self.time_management(searchedMessage["timestamp"]))
            else:
                isNewDate = self.time_management(searchedMessage["timestamp"])

            if (searchedMessage['username'] == self.username):
                self.textBrowser.setAlignment(QtCore.Qt.AlignRight)

            else:
                self.textBrowser.setAlignment(QtCore.Qt.AlignLeft)

            if "isNotForSearch" not in searchedMessage:
                if isNewDate:
                    currentShift += 2 
                    self.shifts.append(currentShift)
                else:
                    self.shifts.append(currentShift)

            self.textBrowser.append(searchedMessage["message"])
            self.textBrowser.append("")

    def backward(self):
        self.currentLine -= 1
        self.messagesAmount.setText(str(self.currentLine + 1) + "/" + str(self.matches))

        previousText = self.textBrowser.document().findBlockByLineNumber(self.msgLines[self.currentLine + 1] * 2 + self.shifts[self.currentLine + 1]).text()
        currentText = self.textBrowser.document().findBlockByLineNumber(self.msgLines[self.currentLine] * 2 + self.shifts[self.currentLine]).text()

        self.underlineText(currentText)
        self.removeUnderlineFromText(previousText)

        self.refillSearchBrowser()

        currentText = self.textBrowser.document().findBlockByLineNumber(self.msgLines[self.currentLine] * 2 + self.shifts[self.currentLine])
        cursor = QtGui.QTextCursor(currentText)
        self.textBrowser.setTextCursor(cursor)

        self.checkForBoundaries()

    def forward(self):
        self.currentLine += 1
        self.messagesAmount.setText(str(self.currentLine + 1) + "/" + str(self.matches))


        # TODO

        # НЕ РАБОТАЕТ СУКА ПОСЛЕ ВТОРОГО РАЗА
        # ВОЗМОЖНО refillSearchBrowser меняет позиции строк

        # FIXED

        # Надо было просто заново заполнять msgLines и shifts (ху ноус почему так)

        previousText = self.textBrowser.document().findBlockByLineNumber(self.msgLines[self.currentLine - 1] * 2 + self.shifts[self.currentLine - 1]).text()
        currentText = self.textBrowser.document().findBlockByLineNumber(self.msgLines[self.currentLine] * 2 + self.shifts[self.currentLine]).text()

        self.underlineText(currentText)
        self.removeUnderlineFromText(previousText)

        self.refillSearchBrowser()

        currentText = self.textBrowser.document().findBlockByLineNumber(self.msgLines[self.currentLine] * 2 + self.shifts[self.currentLine])
        cursor = QtGui.QTextCursor(currentText)
        self.textBrowser.setTextCursor(cursor)

        self.checkForBoundaries()

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    # Переопределяем метод выхода из приложения
    def closeEvent(self, event):
        self.exit()
        event.accept()

    def showUsers(self):
        self.main = adminPanel(server_id=self.server_id, url=self.__url, isCreator=self.username=="CREATOR")
        self.main.show()

    def download(self):
        if self.chat_id:
            resp = requests.get(self.__url + "/get_files", json={
                "chat_id": self.chat_id
            })  

            if resp.status_code == 200:
                allFiles = resp.json()['allFiles']
                self.main = downloadHub(allFiles)
                self.main.show()
        else:
            resp = requests.get(self.__url + "/get_files", json={
                "server_id": self.server_id
            })

            if resp.status_code == 200:
                allFiles = resp.json()['allFiles']
                self.main = downloadHub(allFiles)
                self.main.show()

    def upload(self):
        frame = QtWidgets.QFileDialog()
        frame.setFileMode(QtWidgets.QFileDialog.AnyFile)
        if frame.exec_():
            fileNames = frame.selectedFiles()
            fileName, okPressed = QInputDialog.getText(
                self, "Название файла", "Введите новое название файла: ", QLineEdit.Normal, "")
            if okPressed:
                if fileName == "":
                    fileName = fileNames[0].split("/")[-1]
                else:
                    fileName = fileName + "." + fileNames[0].split("/")[-1].split('.')[1]
                with open(fileNames[0], "rb") as file:
                    if self.chat_id:
                        upl = requests.get(self.__url + "/upload", data=file.read(), params={
                            "filename": fileName,
                            "chat_id": self.chat_id
                        })
                    else:
                        upl = requests.get(self.__url + "/upload", data=file.read(), params={
                            "filename": fileName,
                            "server_id": self.server_id
                        })
                if "nameIstaken" in upl.json():
                    return showError("Данное имя файла заянято")

    def connect(self):
        try:
            response = requests.get(self.__url + "/get_server_name",
                                    json={
                                        "username": self.username,
                                        "server_id": self.server_id
                                    })
            self.serverNameLabel.setText(response.json()['server_name'])
            if not response.json()["rightsGranted"]:
                self.showUsersButton.hide()
        except:
            showError("При попытке подключиться к серверу возникли ошибки")
            return self.close()

    def update(self):
        if not self.isSearchEnabled:
            try:
                self.usersThread = LoadUsersThread(
                    self.__url + "/get_users", self.server_id, self.username)
                self.usersThread.load_finished.connect(self.update_users)
                self.usersThread.finished.connect(self.usersThread.deleteLater)
                self.usersThread.start()

                if self.chat_id:
                    self.msgThread = LoadMessagesThread(
                        self.__url + "/get_private_messages", self.timestamp, self.chat_id, PM=True)
                    self.msgThread.load_finished.connect(self.update_private_messages)
                    self.msgThread.finished.connect(self.msgThread.deleteLater)
                    self.msgThread.start()
                else:
                    self.msgThread = LoadMessagesThread(
                        self.__url + "/get_messages", self.timestamp, self.server_id)
                    self.msgThread.load_finished.connect(self.update_messages)
                    self.msgThread.finished.connect(self.msgThread.deleteLater)
                    self.msgThread.start()
            except:
                showError("Вознилки неполадки")
                return self.close()

    def update_users(self, rs):
        try:
            rs.status_code
        except AttributeError:
            return self.close()

        if rs.status_code == 200:
            res = rs.json()['res']
            isLogged = rs.json()['userIsLoggedIn']

            print(isLogged)

            if int(rs.json()["isBanned"]):
                self.timer.stop()
                showError("Вы были забанены")
                self.exit()
                return self.close()

            # sample:
            # ['Илья 0 1611867749.54902', 'Тест 0 1611865145.06428', 'qwerty 0 1612211290.75964', '123 0 1611867690.18362']

            for user_info in res:
                user = user_info.split()
                if user[0] not in self.currentUsers:
                    self.currentUsers.append(user[0])
                    self.isNotInUsers = True
            if self.isNotInUsers or isLogged:
                onlineUsers = list()
                offlineUsers = list()
                for user_info in res:
                    user = user_info.split()
                    if user[0] == self.username:
                        continue
                    
                    user[1] = int(user[1])
                    lastTimeSeen = datetime.datetime.fromtimestamp(float(user[2]))
                    currentTime = datetime.datetime.fromtimestamp(time.time())
                    if (currentTime.year > lastTimeSeen.year):
                        if (currentTime.day > lastTimeSeen.day) and (currentTime.month == lastTimeSeen.month):
                            status = "Online" if user[1] else f"Offline {lastTimeSeen.strftime('%H:%M %d/%m/%y')}"
                        elif (currentTime.month > lastTimeSeen.month):
                            status = "Online" if user[1] else f"Offline {lastTimeSeen.strftime('%H:%M %d/%m/%y')}"
                        else:
                            status = "Online" if user[1] else f"Offline {lastTimeSeen.strftime('%H:%M %d/%m/%y')}"
                    else:
                        if (currentTime.day > lastTimeSeen.day) and (currentTime.month == lastTimeSeen.month):
                            status = "Online" if user[1] else f"Offline {lastTimeSeen.strftime('%H:%M %d/%m')}"
                        elif (currentTime.month > lastTimeSeen.month):
                            status = "Online" if user[1] else f"Offline {lastTimeSeen.strftime('%H:%M %d/%m')}"
                        else:
                            status = "Online" if user[1] else f"Offline {lastTimeSeen.strftime('%H:%M')}"
                    if user[1]:
                        onlineUsers.append(user[0] + f' {status}')
                    else:
                        offlineUsers.append(user[0] + f' {status}')
                
                self.layout = QVBoxLayout()

                self.usersButtons = list()

                if self.isOnline.isChecked():
                    for onu in onlineUsers:
                        if onu.split()[0] == self.username:
                            continue

                        button = QPushButton(onu.split()[0], objectName="whisperButton")
                        button.setFixedSize(220, 30)
                        button.pressed.connect(lambda key=onu.split()[0]: self.whisper(key))
                        button.installEventFilter(self)
                        button.setStyleSheet('''
                            color: white;
                            background: rgb(0, 170, 127);
                        ''')
                        button.setToolTip(onu.split()[1])
                        self.usersButtons.append(button)

                        self.layout.addWidget(button) 
                    for ofu in offlineUsers:
                        if ofu.split()[0] == self.username:
                            continue

                        button = QPushButton(ofu.split()[0], objectName="whisperButton")
                        button.setFixedSize(220, 30)
                        button.pressed.connect(lambda key=ofu.split()[0]: self.whisper(key))
                        button.installEventFilter(self)
                        button.setStyleSheet('''
                            color: white;
                            background: rgb(0, 170, 127);
                        ''')
                        self.usersButtons.append(button)

                        try:
                            button.setToolTip(ofu.split()[1] + "\n" + ofu.split()[2] + " " + ofu.split()[3])
                        except:
                            button.setToolTip(ofu.split()[1] + "\n" + ofu.split()[2])

                        self.layout.addWidget(button)

                    widget = QWidget()
                    widget.setLayout(self.layout)
                    self.scrollArea.setWidget(widget)
                else:
                    for ofu in offlineUsers:
                        if ofu.split()[0] == self.username:
                            continue

                        button = QPushButton(ofu.split()[0], objectName="whisperButton")
                        button.setStyleSheet('''
                            color: white;
                            background: rgb(0, 170, 127);
                        ''')
                        button.setFixedSize(30, 30)
                        button.pressed.connect(lambda key=ofu.split()[0]: self.whisper(key))
                        self.usersButtons.append(button)

                        try:
                            button.setToolTip(ofu.split()[1] + "\n" + ofu.split()[2] + " " + ofu.split()[3])
                        except:
                            button.setToolTip(ofu.split()[1] + "\n" + ofu.split()[2])

                        self.layout.addWidget(button)
                    for onu in onlineUsers:
                        if onu.split()[0] == self.username:
                            continue

                        button = QPushButton(onu.split()[0], objectName="whisperButton")
                        button.setFixedSize(220, 30)
                        button.pressed.connect(lambda key=onu.split()[0]: self.whisper(key))
                        button.installEventFilter(self)
                        button.setStyleSheet('''
                            color: white;
                            background: rgb(0, 170, 127);
                        ''')
                        button.setToolTip(onu.split()[1])
                        self.usersButtons.append(button)

                        self.layout.addWidget(button) 

                    widget = QWidget()
                    widget.setLayout(self.layout)
                    

                # Тест не проводился
                self.isNotInUsers = False
                self.scrollArea.setWidget(widget)
        else:
            return self.close()

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.Enter and source.objectName() == "whisperButton":
            source.setStyleSheet('''
                color: black;
            ''')

        elif event.type() == QtCore.QEvent.Leave:
            source.setStyleSheet('''
                color: white;
                background: rgb(0, 170, 127);
            ''')

        return super().eventFilter(source, event)

    def whisper(self, username):
        response = requests.get(self.__url + "/get_chat_id", json={
            "users": self.username + username,
            "usersReversed": username + self.username
        })

        chat_id = response.json()["chat_id"]

        self.abortSearch()

        if chat_id == self.chat_id:
            self.chat_id = 0
            self.serverNameLabel.setText(self.serverName)
        else:
            if self.chat_id == 0:
                self.serverName = self.serverNameLabel.text()
            self.serverNameLabel.setText(username)
            self.chat_id = chat_id

        self.textBrowser.clear()
        self.timestamp = 0.0

    def update_private_messages(self, rs):
        self.previousMessageDate = 0
        try:
            rs.status_code
        except AttributeError:
            return self.close()
    
        if rs.status_code == 200:
            messages = rs.json()['messages'] 
            if messages:
                for message in messages:
                    ###
                    # 0 - имя пользователя
                    # 1 - сообщение
                    # 2 - время
                    ###

                    dt = datetime.datetime.fromtimestamp(
                        message[2]).strftime('%H:%M')

                    messageDate = datetime.datetime.fromtimestamp(
                        message[2])
                    
                    self.time_management(messageDate)

                    if message[0] == self.username:
                        self.textBrowser.setAlignment(QtCore.Qt.AlignRight)
                    else:
                        self.textBrowser.setAlignment(QtCore.Qt.AlignLeft)

                    self.textBrowser.append("<b>" + dt + " " +
                                                message[0] + "</b>:<br>" + decrypt(message[1], self.__key))

                    self.textBrowser.append("")
                    self.timestamp = message[2]
        else:
            self.timer.stop()
            showError(
                "При попытке подключиться к серверу возникли ошибки")
            return self.close()

    def time_management(self, messageDate):
        if not self.previousMessageDate:
            self.previousMessageDate = messageDate
            self.textBrowser.setAlignment(QtCore.Qt.AlignCenter)
            self.textBrowser.append("<b>Начало переписки</b>")
            self.textBrowser.append("<b>" + messageDate.strftime("%d/%m/%Y") + "</b>")
            self.textBrowser.append("")
            return 1
                    
        if self.previousMessageDate.year < messageDate.year:
            self.previousMessageDate = messageDate
            self.textBrowser.setAlignment(QtCore.Qt.AlignCenter)
            self.textBrowser.append("<b>" + messageDate.strftime("%d/%m/%Y") + "</b>")
            self.textBrowser.append("")
            return 2

        elif self.previousMessageDate.month < messageDate.month:
            self.previousMessageDate = messageDate
            self.textBrowser.setAlignment(QtCore.Qt.AlignCenter)
            self.textBrowser.append("<b>" + messageDate.strftime("%d/%m/%Y") + "</b>")
            self.textBrowser.append("")
            return 2
        
        elif self.previousMessageDate.month == messageDate.month and self.previousMessageDate.day < messageDate.day:
            self.previousMessageDate = messageDate
            self.textBrowser.setAlignment(QtCore.Qt.AlignCenter)
            self.textBrowser.append("<b>" + messageDate.strftime("%d/%m/%Y") + "</b>")
            self.textBrowser.append("")
            return 2

        return 0

    def update_messages(self, rs):
        try:
            rs.status_code
        except AttributeError:
            return self.close()
    
        if rs.status_code == 200:
            invitations = rs.json()["invitations"]
            try:
                for count in range(len(invitations)):
                    if self.username.lower() in invitations[count].keys():
                            if invitations[count][self.username.lower()]: 
                                self.timer.stop()
                                showMessage("Вас пригласили в чат")
                                response = requests.get(self.__url + "/accept_invitation", json={
                                    "username": self.username.lower()
                                })
                                print(response.json())
                                self.main = privateChat(self.username, invitations[count]["serverName"], self.__url)
                                self.close()
                                self.main.show()
            except:
                pass

            messages = rs.json()['messages'] 
            if messages:
                for message in messages:
                    ###
                    # 0 - имя пользователя
                    # 1 - сообщение
                    # 2 - время
                    ###

                    dt = datetime.datetime.fromtimestamp(
                        message[2]).strftime('%H:%M')

                    messageDate = datetime.datetime.fromtimestamp(
                        message[2])
                    

                    self.time_management(messageDate)

                    if message[0] == self.username:
                        self.textBrowser.setAlignment(QtCore.Qt.AlignRight)
                    else:
                        self.textBrowser.setAlignment(QtCore.Qt.AlignLeft)

                    self.textBrowser.append("<b>" + dt + " " +
                                                message[0] + "</b>:<br>" + decrypt(message[1], self.__key))

                    self.textBrowser.append("")
                    self.timestamp = message[2]
        else:
            showError(
                "При попытке подключиться к серверу возникли ошибки")
            return self.close()

    def send_message(self):
        text = removeSpaces(self.textEdit.toPlainText())
        if len(text) > 100:
            return showError("Длина сообщения должна быть не более 100")
        if self.chat_id:
            response = requests.get(
                self.__url + '/send_private_message',
                json={
                    'username': self.username,
                    'text': encrypt(text, self.__key),
                    'chat_id': self.chat_id,
                }
            )
            if response.status_code == 200:
                if "blankMessage" in response.json():
                    showError("Сообщение не может быть пустым")
                return self.textEdit.setText("")
            else:
                self.timer.stop()
                showError("Ошибка в подключении к серверу")
                return self.close()
        else:
            response = requests.get(
                self.__url + '/send_message',
                json={
                    'username': self.username,
                    'text': encrypt(text, self.__key),
                    'server_id': self.server_id,
                }
            )
            if response.status_code == 200:
                if "blankMessage" in response.json():
                    showError("Сообщение не может быть пустым")
                if "invalidUsername" in response.json():
                    showError("Данного пользователя не существует")
                if "serverCreated" in response.json():
                    self.timer.stop()
                    self.main = privateChat(self.username, response.json()["serverName"], self.__url)
                    self.close()
                    self.main.show()
                return self.textEdit.setText("")
            else:
                self.timer.stop()
                showError("Ошибка в подключении к серверу")
                return self.close()

    def search(self):
        self.sForm = searchForm()
        self.sForm.show()
        
        self.sForm.closeDialog.connect(lambda: self.find(self.sForm.text, self.sForm.checkBox.isChecked(), self.sForm.checkBox_2.isChecked()))

    def removeUnderlineFromText(self, textToDeunderline):
        byte = b'\xe2\x80\xa8'
        for msg in self.result:
            for ch in textToDeunderline:
                    if ch.encode() == byte:
                        textToDeunderline = textToDeunderline.replace(ch, "")
            if cleanhtml(msg["message"]) == textToDeunderline:
                    msg["message"] = msg["message"].replace("<strong>", "")
                    msg["message"] = msg["message"].replace("</strong>", "")
                    return True

    def underlineText(self, textToUnderline):
        byte = b'\xe2\x80\xa8'
        for msg in self.result:
            for ch in textToUnderline: 
                if ch.encode() == byte:
                    textToUnderline = textToUnderline.replace(ch, "")
            if cleanhtml(msg["message"]) == textToUnderline:
                msg["message"] = msg["message"][:msg["message"].index("<br>") + 4] + "<strong>" + msg["message"][msg["message"].index("<br>") + 4:] + "</strong>"
                return True
                
    def find(self, text, nameIsChecked, msgIsChecked):
        self.word = removeSpaces(text)
        self.result = []

        if self.word:
            if self.chat_id:
                response = requests.get(
                self.__url + '/get_private_messages',
                params={
                    'after': 0.0,
                    'chat_id': self.chat_id
                })
            else:
                response = requests.get(
                    self.__url + '/get_messages',
                    params={
                        'after': 0.0,
                        'server_id': self.server_id
                    })

            if response.status_code == 200:
                self.matches = 0
                self.msgLines = list()
                self.totalLines = 0

                if not nameIsChecked and not msgIsChecked:
                    return showError("Выберите критерии поиска")

                messages = response.json()['messages']
                self.messages = messages
                
                for message in messages:

                    dt = datetime.datetime.fromtimestamp(
                            message[2]).strftime('%H:%M')

                    if self.word.lower() in message[0].lower() and nameIsChecked:
                        self.dict = {"username": message[0], 
                                    "message": ("<b>" + dt + " " + beautifyText(message[0], self.word) + "</b>:<br>" + decrypt(message[1], self.__key) + ""),
                                    "timestamp": datetime.datetime.fromtimestamp(message[2])}
                        self.result.append(self.dict)
                        self.msgLines.append(self.totalLines)

                        self.matches += 1

                    elif self.word.lower() in decrypt(message[1], self.__key).lower() and msgIsChecked:
                        self.dict = {"username": message[0], 
                                    "message": ("<b>" + dt + " " +
                                                message[0] + "</b>:<br>" + beautifyText(decrypt(message[1], self.__key), self.word) + ""),
                                    "timestamp": datetime.datetime.fromtimestamp(message[2])}

                        self.result.append(self.dict)
                        self.msgLines.append(self.totalLines)

                        self.matches += 1

                    else:
                        self.dict = {"username": message[0], 
                                    "message": ("<b>" + dt + " " +
                                                message[0] + "</b>:<br>" + decrypt(message[1], self.__key) + ""),
                                    "timestamp": datetime.datetime.fromtimestamp(message[2]),
                                    "isNotForSearch": True
                                    }
                        self.result.append(self.dict)

                    self.totalLines += 1

                    if not self.isSearchEnabled:
                        self.dict = {"username": message[0], 
                                    "message": ("<b>" + dt + " " +
                                                message[0] + "</b>:<br>" + decrypt(message[1], self.__key) + ""),
                                    "timestamp": datetime.datetime.fromtimestamp(message[2])}
                        self.previousMessages.append(self.dict)

                if (self.matches):
                    self.sForm.close()
                    self.textBrowser.clear()
                    self.shifts = list()

                    currentShift = 2

                    self.isSearchEnabled = True
                    self.previousMessageDate = 0
                    for searchedMessage in self.result:
                        if "isNotForSearch" in searchedMessage:
                            currentShift += int(self.time_management(searchedMessage["timestamp"]))
                        else:
                            isNewDate = self.time_management(searchedMessage["timestamp"])

                        if (searchedMessage['username'] == self.username):
                            self.textBrowser.setAlignment(QtCore.Qt.AlignRight)
                        else:
                            self.textBrowser.setAlignment(QtCore.Qt.AlignLeft)
                        self.textBrowser.append(searchedMessage["message"])
                        self.textBrowser.append("")
                        if "isNotForSearch" not in searchedMessage:
                            if isNewDate:
                                currentShift += 2 
                                self.shifts.append(currentShift)
                            else:
                                self.shifts.append(currentShift)

                    
                    self.underlineText(self.textBrowser.document().findBlockByLineNumber(self.msgLines[0] * 2 + self.shifts[0]).text())
                    self.refillSearchBrowser()
                    # for i in range(len(self.msgLines)):
                    #     print(i)
                    #     print(self.textBrowser.document().findBlockByLineNumber(self.msgLines[i] * 2 + self.shifts[i]).text())


                    currentText = self.textBrowser.document().findBlockByLineNumber(self.msgLines[0] * 2 - 1 + self.shifts[0])
                    cursor = QtGui.QTextCursor(currentText)
                    self.textBrowser.setTextCursor(cursor)

                    self.forwardButton.show()
                    self.messagesAmount.show()
                    self.searchButton.hide()

                    self.messagesAmount.setText("1/" + str(self.matches))

                    # Создаём список из номеров линий для каждого сообщения
                    # self.msgLines = [i*2 for i in range(len(self.result))]
                    self.currentLine = 0

                    self.checkForBoundaries()

                else:
                    self.result = []
                    return showMessage("Ваш запрос не выдал результатов(")
        else:
            return showError("Поле поиска не может быть пустым")

    def abortSearch(self):
        self.previousMessageDate = 0

        if self.isSearchEnabled:
            self.textBrowser.clear()
            for msg in self.previousMessages:
                self.time_management(msg["timestamp"])
                if (msg['username'] == self.username):
                    self.textBrowser.setAlignment(QtCore.Qt.AlignRight)
                else:
                    self.textBrowser.setAlignment(QtCore.Qt.AlignLeft)
                self.textBrowser.append(msg["message"])
                self.textBrowser.append("")
            
            self.backButton.hide()
            self.forwardButton.hide()
            self.messagesAmount.hide()
            self.searchButton.show()

            self.isSearchEnabled = False

    def exit(self):
        resp = requests.get(
            self.__url + "/disconnect",
            json={
                "username": self.username,
                "server_id": self.server_id
            }
        )
        if "someProblems" in resp.json():
            return showError(resp.json()["someProblems"])

    # Выйти с акка
    def logOff(self):
        requests.get(
            self.__url + "/disconnect",
            json={
                "username": self.username,
                "server_id": self.server_id
            }
        )

        try:
            with open("userdata/data.json", "w") as js:
                js.write("")
        except:
            pass

        self.close()
        self.timer.stop()
        self.main = Auth()
        return self.main.show()

    # Отключиться от сервера
    def disconnect(self):
        requests.get(
            self.__url + "/disconnect",
            json={
                "username": self.username,
                "server_id": self.server_id
            }
        )
        self.close()
        self.timer.stop()
        self.main = Lobby(self.username, self.__url)
        return self.main.show()


'''
Должна быть кнопка создать сервер
'''

class Lobby(QtWidgets.QMainWindow, LobbyUI.Ui_MainWindow):
    def __init__(self, username=USERNAME, url=URL):
        super().__init__()
        self.setupUi(self)

        self.__url = url
        self.username = username
        self.oldPos = self.pos()

        self.exitButton.setIcon(QtGui.QIcon(":/resources/Images/cross.png"))
        self.showUsersButton.setIcon(QtGui.QIcon(":/resources/Images/settings.png"))
        self.createServerButton.setIcon(QtGui.QIcon(":/resources/Images/plus.png"))
        
        if self.username != "CREATOR":
            self.createServerButton.hide()
            self.showUsersButton.hide()

        self.updateButton.pressed.connect(self.update)
        self.logOffButton.pressed.connect(self.logOff)
        self.exitButton.pressed.connect(self.close)
        self.createServerButton.pressed.connect(self.createServer)
        self.downloadButton.pressed.connect(self.download)
        self.uploadButton.pressed.connect(self.upload)
        self.showUsersButton.pressed.connect(self.showUsers)

        self.scrollArea.setAlignment(QtCore.Qt.AlignTop)
        self.scrollArea.setWidgetResizable(False)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.update()

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def update(self):
        request = requests.get(self.__url + "/get_servers")
        if "someProblems" in request.json():
            showError("Проблемы с сервером")
            return self.close()
        res = request.json()['servers']

        self.layout = QVBoxLayout()
        time = 100

        self.updateButton.hide()
        for i in res:
            button = QPushButton(i[1], self)
            button.setFixedSize(186, 30)
            button.pressed.connect(lambda key=i[0]: self.connect(key))

            loop = QtCore.QEventLoop()
            QtCore.QTimer.singleShot(time, loop.quit)
            loop.exec_()

            self.layout.addWidget(button)
            widget = QWidget()
            widget.setLayout(self.layout)
            self.scrollArea.setWidget(widget)

        self.updateButton.show()

    def logOff(self):
        self.close()
        
        try:
            with open("userdata/data.json", "w") as js:
                js.write("")
        except:
            pass

        self.main = Auth()
        return self.main.show()

    def download(self):
        resp = requests.get(URL + "/get_files")
        if resp.status_code == 200:
            allFiles = resp.json()['allFiles']
            self.main = downloadHub(allFiles)
            self.main.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            self.main.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            self.main.show()

    def upload(self):
        frame = QtWidgets.QFileDialog()
        frame.setFileMode(QtWidgets.QFileDialog.AnyFile)
        if frame.exec_():
            fileNames = frame.selectedFiles()
            fileName, okPressed = QInputDialog.getText(
                self, "Название файла", "Введите новое название файла: ", QLineEdit.Normal, "")
            if okPressed:
                if fileName == "":
                    fileName = fileNames[0].split("/")[-1]
                else:
                    fileName = fileName + "." + fileNames[0].split("/")[-1].split('.')[1]
                with open(fileNames[0], "rb") as file:
                    upl = requests.get(self.__url + "/upload", data=file.read(), params={
                        "filename": fileName,
                    })
                if "nameIstaken" in upl.json():
                    return showError("Данное имя файла заянято")

    def showUsers(self):
        self.main = adminPanel(0, True, self.__url)
        self.main.show()

    def createServer(self):
        while True:
            serverName, okPressed = QInputDialog.getText(
                self, "Название сервера", "Введите название сервера:", QLineEdit.Normal, "")
            if (okPressed):
                if(serverName != ""):
                    serverPassword, okPressed = QInputDialog.getText(
                        self, "Пароль сервера", "Введите пароль для сервера(если не требуется - оставьте поле пустым):", QLineEdit.Password, "")
                    res = requests.get(self.__url + "/create_server", json={
                        "serverName": serverName,
                        "serverPassword": serverPassword,
                        "username": self.username
                    })
                    if ("someProblems" in res.json()):
                        return showError("Беды")
                    if ("nameIsTaken" in res.json()):
                        return showError("Данное имя сервера занято")
                    self.main = Chat(self.username, self.__url,
                                     res.json()['server_id'])
                    break
                else:
                    showError("Название сервера не может быть пустым")
            else:
                break


    def connect(self, id):
        self.__serverPassword, okPressed = QInputDialog.getText(
            self, "Требуется пароль", "Введите пароль: ", QLineEdit.Password, "")
        if okPressed:
            response = requests.get(self.__url + "/connect",
                                    json={
                                        'server_id': id,
                                        'username': self.username,
                                        'password': hashlib.md5(self.__serverPassword.encode()).hexdigest()
                                    })
            if response.status_code == 200:
                if "badPassword" in response.json():
                    return showError("Неверный пароль")

                if "isBanned" in response.json():
                    return showError("Вы были забанены на этом сервере")

                if "someProblems" in response.json():
                    return showError(str(response.json()))

                self.close()
                self.main = Chat(self.username, self.__url, id)
                return self.main.show()
            else:
                showError("Беды с сервером")


class adminPanel(QtWidgets.QMainWindow, AdminUI.Ui_MainWindow):
    def __init__(self, server_id, isCreator, url=URL):
        super().__init__()
        self.setupUi(self)

        self.banButton.pressed.connect(self.banUser)
        self.createUserButton.pressed.connect(self.createUser)
        self.exitButton.pressed.connect(self.close)

        self.__url = url
        self.server_id = server_id
        self.isCreator = isCreator

        self.exitButton.setIcon(QtGui.QIcon(":/resources/Images/cross.png"))

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.tree.setHeaderLabels(['Пользователи в данном чате'])
        self.insertUsers()

    def insertUsers(self):
        res = requests.get(self.__url + "/get_users", json={
                            "server_id": self.server_id
                        })
        print(res.json())
        '''
            0 - username
            1 - isOnline
            2 - lastSeen
            3 - entryTime
            4 - timeSpent
            5 - isBanned
        '''
        if self.server_id == 0:
            users = res.json()['res']
            for server_id in users.keys():
                self.current_server_id = QtWidgets.QTreeWidgetItem(self.tree, [server_id])

                for user in users[server_id]:
                    u = user.split()
                    status = "Online" if int(u[1]) else "Offline"
                    status = "Banned" if int(u[5]) else status
                    us = QtWidgets.QTreeWidgetItem(self.current_server_id, [u[0]])
                    
                    QtWidgets.QTreeWidgetItem(us, [f"Статус: {status}"])
                    QtWidgets.QTreeWidgetItem(us, [f"Последнее время входа: {datetime.datetime.fromtimestamp(float(u[2])).strftime('%H:%M:%S %d/%m/%y')}"])
                    if int(u[1]):
                        totalTime = (
                                float(u[4]) + time.time() - float(u[3]))
                        QtWidgets.QTreeWidgetItem(us, [f"Общее время онлайн: {self.calculateTime(totalTime)}"])
                    else:
                        QtWidgets.QTreeWidgetItem(us, [f"Общее время онлайн: {self.calculateTime(float(u[4]))}"])
            return

        users = res.json()['res']
        for user in users:
            u = user.split()
            status = "Online" if int(u[1]) else "Offline"
            status = "Banned" if int(u[5]) else status
            us = QtWidgets.QTreeWidgetItem(self.tree, [u[0]])
            
            QtWidgets.QTreeWidgetItem(us, [f"Статус: {status}"])
            QtWidgets.QTreeWidgetItem(us, [f"Последнее время входа: {datetime.datetime.fromtimestamp(float(u[2])).strftime('%H:%M:%S %d/%m/%y')}"])
            if int(u[1]):
                totalTime = (
                        float(u[4]) + time.time() - float(u[3]))
                QtWidgets.QTreeWidgetItem(us, [f"Общее время онлайн: {self.calculateTime(totalTime)}"])
            else:
                QtWidgets.QTreeWidgetItem(us, [f"Общее время онлайн: {self.calculateTime(float(u[4]))}"])

    def calculateTime(self, time):
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

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QtCore.QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def banUser(self):
        if not (self.tree.selectedItems()):
            return
        if self.server_id == 0:
            if (self.tree.selectedItems()[0].parent()) and (not(self.tree.selectedItems()[0].parent().parent())):
                response = requests.get(self.__url + "/ban_user", json={
                    "username": self.tree.selectedItems()[0].text(0),
                    "server_id": self.tree.selectedItems()[0].parent().text(0)
                })
                if "someProblems" in response.json():
                    return showError("Возникли неполадки с севрером")

                banned = "разбанен" if self.tree.selectedItems()[0].child(0).text(0).split("Статус: ")[1] \
                    == "Banned" else "забанен"
                showMessage(self.tree.selectedItems()[0].text(0) + " был " + banned)
                self.tree.clear()
                self.insertUsers()

        else:
            if not (self.tree.selectedItems()[0].parent()):
                response = requests.get(self.__url + "/ban_user", json={
                    "username": self.tree.selectedItems()[0].text(0),
                    "server_id": self.server_id
                })
                if "someProblems" in response.json():
                    return showError("Возникли неполадки с севрером")

                banned = "разбанен" if self.tree.selectedItems()[0].child(0).text(0).split("Статус: ")[1] \
                    == "Banned" else "забанен"

                showMessage(self.tree.selectedItems()[0].text(0) + " был " + banned)
                self.tree.clear()
                self.insertUsers()
    
    def createUser(self):
        self.main = userCreatorForm(self.server_id, self.isCreator, self.__url)
        # self.main.setFixedSize()
        self.main.show()
        self.tree.clear()
        self.insertUsers()

class userCreatorForm(QtWidgets.QMainWindow, userCreatorUI.Ui_MainWindow):
    def __init__(self, server_id, isCreator, url=URL):
        super().__init__()
        self.setupUi(self)

        self.server_id = server_id
        self.__url = url

        if  not isCreator:
            self.label_2.hide()
            self.availableServers.hide()
        else:
            response = requests.get(self.__url + "/get_servers")
            servers = response.json()["servers"]

            if response.status_code == 200:
                if "someProblems" in response.json():
                    return showError("Беды")
                for serverInfo in servers:
                    self.availableServers.addItem(str(serverInfo[0]))

        self.createButton.pressed.connect(self.createUser)
        self.exitButton.pressed.connect(self.close)

        self.exitButton.setIcon(QtGui.QIcon(":/resources/Images/cross.png"))

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QtCore.QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def createUser(self):
        if self.availableServers.isVisible():
            self.server_id = int(self.availableServers.currentText())
        response = requests.get(self.__url + "/create_user", json={
            "username": self.usernameText.text(),
            "password": self.passwordText.text(),
            "server_id": self.server_id,
        })

        if "isNotFilled" in response.json():
            return showError("Не все поля заполнены")
        if "nameIsTaken" in response.json():
            return showError("Данное имя пользователя занято")
        if "badPassword" in response.json():
            return showError("Пароль должен иметь специальные символы, буквы и цифры. Длина пароля от 8 до 16")

        showMessage("Пользователь был создан")
        self.close()

class searchForm(searchFormUI.Ui_MainWindow, QtWidgets.QMainWindow):
    closeDialog = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.oldPos = self.pos()
        self.checkBox.setChecked(True)

        self.text = ""

        self.searchButton.pressed.connect(self.setText)
        self.cancelButton.pressed.connect(self.close)
        self.exitButton.pressed.connect(self.close)

        self.exitButton.setIcon(QtGui.QIcon(":/resources/Images/cross.png"))

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def setText(self):
        self.text = self.textEdit.toPlainText()
        self.closeDialog.emit()

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()


class downloadHub(QtWidgets.QMainWindow, downloadUI.Ui_Form):
    def __init__(self, items):
        super().__init__()
        self.setupUi(self)
        self.items = items
        self.isCancelled = False

        self.browser = QtWidgets.QTextBrowser()
        self.listWidget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.exitButton.pressed.connect(self.close)

        self.oldPos = 0.0

        self.selectButton.pressed.connect(self.download)

        self.exitButton.setIcon(QtGui.QIcon(":/resources/Images/cross.png"))

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        for i in items:
            self.listWidget.addItem(i)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def download(self):
        neededFiles = list()
        self.downloadedFiles = dict()

        for item in self.listWidget.selectedItems():
            neededFiles.append(item.text())

        for neededFile in neededFiles:
            resp = requests.get(URL + "/download", json={
                "neededFile": neededFile
            })

            filesList = [f for _, _, f in os.walk(os.getcwd() + "/Загрузки")][0]

            isFound = False

            for file in filesList:
                if neededFile == file:
                    isFound = True

                    self.dial = QDialog(self)
                    label = QLabel(
                        text=f"{file}<br>уже скачан")
                    
                        
                    accept = QPushButton(text="Скачать заново")
                    decline = QPushButton(text="Отменить")

                    accept.pressed.connect(lambda: self.accept(file, resp.content))
                    decline.pressed.connect(lambda: self.dial.close())

                    self.dial.setLayout(QVBoxLayout())
                    self.dial.layout().addWidget(label)
                    self.dial.layout().addWidget(accept)
                    self.dial.layout().addWidget(decline)
                    self.dial.setFixedSize(310, 150)
                    self.dial.exec_()

            if not isFound:
                self.downloadedFiles[neededFile] = resp.content
            
        if self.downloadedFiles:
            info = ""
            
            for fileName in self.downloadedFiles.keys():
                with open("Загрузки/" + str(fileName), "wb") as file:
                    file.write(self.downloadedFiles[fileName])
                    info = info + str(fileName) + ", "

            showMessage(f"Файлы {info[:-2]} были успешно скачаны")

    def accept(self, fileName, fileContent):
        self.dial.close()
        self.downloadedFiles[fileName] = fileContent


class privateChat(privateChatUI.Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(self, username, serverName, url=URL):
        super().__init__()
        self.setupUi(self)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.__url = url
        self.username = username
        self.serverName = serverName
        self.disconnect = True
        self.timestamp = 0.0

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
            "serverName": self.serverName,
            "timestamp": self.timestamp
        })

        if response.status_code == 200:
            if response.json()["isLeft"]:
                self.timer.stop()
                response = requests.get(self.__url + "/delete_private_server", json={
                    "serverName": self.serverName
                })
                if "username" in response.json():
                    username = response.json()["username"]

                showMessage(username + " покинул сервер")
                self.disconnect = False
                return self.close()
            messages = response.json()["messages"]
            if len(messages):
                for message in messages:
                    if message["username"] == self.username:
                        self.textBrowser.setAlignment(QtCore.Qt.AlignRight)
                    else:
                        self.textBrowser.setAlignment(QtCore.Qt.AlignLeft)
                    self.textBrowser.append(message["username"] + ": " + message["message"])
                    self.textBrowser.append("")
                    self.timestamp = message["timestamp"]


    def closeEvent(self, event, disconnect=True):
        if self.disconnect:
            requests.get(self.__url + "/disconnect_from_private_server", json={
                "serverName": self.serverName,
                "username": self.username
            })
        event.accept()


if __name__ == "__main__":
    try:
        with open("url.txt", "r") as file:
            URL = file.read()
    except:
        pass
    app = QtWidgets.QApplication([])
    
    window = Lobby()
    window.setFixedSize(sizes["Chat"]["WIDTH"], sizes["Chat"]["HEIGHT"])
    window.show()
    app.exec_()
    exit()

    data = loadData(URL)
    if data != 0:
        window = Lobby(data, URL)
        window.setFixedSize(sizes["Chat"]["WIDTH"], sizes["Chat"]["HEIGHT"])
        window.show()
        app.exec_()
    else:
        window = Auth()
        window.setFixedSize(sizes["Chat"]["WIDTH"], sizes["Chat"]["HEIGHT"])
        window.show()
        app.exec_()
