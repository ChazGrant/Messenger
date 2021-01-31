from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMessageBox, QVBoxLayout, QListView, QTextBrowser, QPushButton, QInputDialog, QLineEdit, QDialog, QLabel, QFrame, QAbstractItemView
from PyQt5.QtCore import QPoint, QThread, pyqtSignal
import AuthUI
import MainUI
import LobbyUI
import downloadUI
import searchFormUI
import requests
import hashlib
import datetime
import time
import os
from crypt import *

URL = "http://127.0.0.1:5000"
USERNAME = "qwerty"
KEY = 314
WORD_FOR_SEARCH = ""


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

    def __init__(self, url, ts, serv_id):
        super().__init__()

        self.url = url
        self.timestamp = ts
        self.server_id = serv_id

    def run(self):
        try:
            rs = requests.get(self.url,
                          params={
                              'after': self.timestamp,
                              'server_id': self.server_id
                          })
        except:
            print("Беды")
            rs = False
        finally:
            self.load_finished.emit(rs)


class LoadUsersThread(QThread):
    load_finished = pyqtSignal(object)

    def __init__(self, url, serv_id):
        super().__init__()

        self.url = url
        self.server_id = serv_id

    def run(self):
        try:
            rs = requests.get(self.url,
                          json={
                              "server_id": self.server_id
                          })
        except:
            print("Беды")
            rs = False
        finally:
            self.load_finished.emit(rs)


class Auth(QtWidgets.QMainWindow, AuthUI.Ui_MainWindow):
    def __init__(self, url=URL):
        super().__init__()
        self.setupUi(self)

        self.oldPos = self.pos()
        self.__url = url

        self.loginButton.pressed.connect(self.login)
        self.registrateButton.pressed.connect(self.registration)
        self.exitButton.pressed.connect(self.close)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

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

            # Закрываем текущее окно
            self.close()
            # Инициализируем новое окно, передавая логин и пароль и открываем его
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

        self.sendButton.pressed.connect(self.send_message)
        self.clearMessageButton.pressed.connect(
            lambda: self.textEdit.setText(""))
        self.exitButton.pressed.connect(self.close)
        self.disconnectButton.pressed.connect(self.disconnect)
        self.exitAccountButton.pressed.connect(self.logOff)
        self.searchButton.pressed.connect(self.search)
        self.abortSearchButton.pressed.connect(self.abortSearch)
        self.downloadButton.pressed.connect(self.download)
        self.uploadButton.pressed.connect(self.upload)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.scrollArea.setAlignment(QtCore.Qt.AlignTop)
        self.scrollArea.setWidgetResizable(False)

        self.oldPos = self.pos()
        self.timestamp = 0.0
        self.username = username
        self.previousMessages = []
        self.__key = KEY
        self.__url = url
        self.server_id = server_id
        self.isSearchEnabled = False
        self.currentUsers = []
        self.isNotInUsers = False

        self.connect()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)
        self.update()

    def showMessage(self, text):
        '''
        Создаёт окно с ошибкой и выводим текст
        '''
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle("Info")
        msg.exec_()

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

    def download(self):
        resp = requests.get(self.__url + "/get_files", json={
            "server_id": self.server_id
        })

        hub = downloadHub(resp.json()["allFiles"])
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
                with open(fileNames[0], "rb") as file:
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
                                        "server_id": self.server_id,
                                    })
            self.serverNameLabel.setText(response.json()['server_name'])
        except:
            showError("При попытке подключиться к серверу возникли ошибки")
            return self.close()

    def update_users(self, rs):
        try:
            rs.status_code
        except AttributeError:
            return self.close()

        if rs.status_code == 200:
            res = rs.json()['res']
            isLogged = rs.json()['userIsLoggedIn']
            self.users = QTextBrowser()

            # Протестить
            for i in res:
                if i[0] not in self.currentUsers:
                    self.currentUsers.append(i[0])
                    self.isNotInUsers = True
            if self.isNotInUsers or isLogged:
                onlineUsers = list()
                offlineUsers = list()
                for i in res:
                    lastTimeSeen = datetime.datetime.fromtimestamp(i[2])
                    currentTime = datetime.datetime.fromtimestamp(time.time())
                    if (currentTime.year > lastTimeSeen.year):
                        if (currentTime.day > lastTimeSeen.day) and (currentTime.month == lastTimeSeen.month):
                            status = "Online" if i[1] else f"Offline {lastTimeSeen.strftime('%H:%M %d/%m/%y')}"
                        elif (currentTime.month > lastTimeSeen.month):
                            status = "Online" if i[1] else f"Offline {lastTimeSeen.strftime('%H:%M %d/%m/%y')}"
                        else:
                            status = "Online" if i[1] else f"Offline {lastTimeSeen.strftime('%H:%M %d/%m/%y')}"
                    else:
                        if (currentTime.day > lastTimeSeen.day) and (currentTime.month == lastTimeSeen.month):
                            status = "Online" if i[1] else f"Offline {lastTimeSeen.strftime('%H:%M %d/%m')}"
                        elif (currentTime.month > lastTimeSeen.month):
                            status = "Online" if i[1] else f"Offline {lastTimeSeen.strftime('%H:%M %d/%m')}"
                        else:
                            status = "Online" if i[1] else f"Offline {lastTimeSeen.strftime('%H:%M')}"
                    if i[1]:
                        onlineUsers.append(i[0] + f' ({status})')
                    else:
                        offlineUsers.append(i[0] + f' ({status})')
                
                if self.isOnline.isChecked():
                    for onu in onlineUsers:
                        self.users.append(onu)
                    for ofu in offlineUsers:
                        self.users.append(ofu)
                else:
                    for ofu in offlineUsers:
                        self.users.append(ofu)
                    for onu in onlineUsers:
                        self.users.append(onu)

                # Тест не проводился
                self.isNotInUsers = False
                self.scrollArea.setWidget(self.users)
        else:
            showError("Возникли неполадки с сервером")
            return self.close()

    def update_messages(self, rs):
        try:
            rs.status_code
        except AttributeError:
            return self.close()
    
        if rs.status_code == 200:
            messages = rs.json()['messages']
            previousMessageDate = 0
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
                    

                    if not previousMessageDate:
                        previousMessageDate = messageDate
                        self.textBrowser.setAlignment(QtCore.Qt.AlignCenter)
                        self.textBrowser.append("<b>Начало переписки</b>")
                        self.textBrowser.append("<b>" + messageDate.strftime("%d/%m/%Y") + "</b>")
                        self.textBrowser.append("")
                    
                    if previousMessageDate.year < messageDate.year:
                        previousMessageDate = messageDate
                        self.textBrowser.setAlignment(QtCore.Qt.AlignCenter)
                        self.textBrowser.append("<b>" + messageDate.strftime("%d/%m/%Y") + "</b>")
                        self.textBrowser.append("")

                    elif previousMessageDate.month < messageDate.month:
                        previousMessageDate = messageDate
                        self.textBrowser.setAlignment(QtCore.Qt.AlignCenter)
                        self.textBrowser.append("<b>" + messageDate.strftime("%d/%m/%Y") + "</b>")
                        self.textBrowser.append("")
                    
                    elif previousMessageDate.month == messageDate.month and previousMessageDate.day < messageDate.day:
                        previousMessageDate = messageDate
                        self.textBrowser.setAlignment(QtCore.Qt.AlignCenter)
                        self.textBrowser.append("<b>" + messageDate.strftime("%d/%m/%Y") + "</b>")
                        self.textBrowser.append("")

                    if message[0] == self.username:
                        self.textBrowser.setAlignment(QtCore.Qt.AlignRight)
                    else:
                        self.textBrowser.setAlignment(QtCore.Qt.AlignLeft)

                    # if len(message[1]) > 50:
                    #     self.textBrowser.append("<b>" + dt + " " +
                    #                             message[0] + "</b><br> " + decrypt(message[1][:50], self.__key) + "<br>" + decrypt(message[1][50:], self.__key))
                    # else:
                    self.textBrowser.append("<b>" + dt + " " +
                                                message[0] + "</b>:<br>" + decrypt(message[1], self.__key))

                    self.textBrowser.append("")
                    self.timestamp = message[2]
        else:
            showError(
                "При попытке подключиться к серверу возникли ошибки")
            return self.close()

    def update(self):
        if not self.isSearchEnabled:
            try:
                self.usersThread = LoadUsersThread(
                    self.__url + "/get_users", self.server_id)
                self.usersThread.load_finished.connect(self.update_users)
                self.usersThread.finished.connect(self.usersThread.deleteLater)
                self.usersThread.start()

                self.msgThread = LoadMessagesThread(
                    self.__url + "/get_messages", self.timestamp, self.server_id)
                self.msgThread.load_finished.connect(self.update_messages)
                self.msgThread.finished.connect(self.msgThread.deleteLater)
                self.msgThread.start()
            except:
                showError("Вознилки неполадки")
                return self.close()

    def send_message(self):
        text = removeSpaces(self.textEdit.toPlainText())
        if len(text) > 100:
            return showError("Длина сообщения должна быть не более 100")
        response = requests.get(
            self.__url + '/send_message',
            json={
                'username': self.username,
                'text': encrypt(text, self.__key),
                'server_id': self.server_id,
            }
        )
        if response.status_code == 200:
            try:
                if response.json()['blankMessage']:
                    showError("Сообщение не может быть пустым")
            except:
                pass
            return self.textEdit.setText("")
        else:
            showError("Ошибка в подключении к серверу")
            return self.close()

    def search(self):
        self.sForm = searchForm()
        self.sForm.show()
        
        self.sForm.closeDialog.connect(lambda: self.find(self.sForm.text, self.sForm.checkBox.isChecked(), self.sForm.checkBox_2.isChecked()))
        
    def find(self, text, nameIsChecked, msgIsChecked):
        self.word = text
        self.result = []


        if self.word:
            response = requests.get(
                self.__url + '/get_messages',
                params={
                    'after': 0.0,
                    'server_id': self.server_id
                })

            if response.status_code == 200:
                messages = response.json()['messages']
                for message in messages:
                    dt = datetime.datetime.fromtimestamp(
                            message[2]).strftime('%H:%M')
                    if self.word in message[0] and nameIsChecked:
                        self.dict = {"username": message[0], 
                                    "message": ("<b>" + dt + " " +
                                                message[0] + "</b>:<br>" + decrypt(message[1], self.__key) + "")}
                        self.result.append(self.dict)
                    elif self.word in decrypt(message[1], self.__key) and msgIsChecked:
                        self.dict = {"username": message[0], 
                                    "message": ("<b>" + dt + " " +
                                                message[0] + "</b>:<br>" + decrypt(message[1], self.__key) + "")}
                        self.result.append(self.dict)

                    if not self.isSearchEnabled:
                        self.dict = {"username": message[0], 
                                    "message": ("<b>" + dt + " " +
                                                message[0] + "</b>:<br>" + decrypt(message[1], self.__key) + "")}
                        self.previousMessages.append(self.dict)


                if (self.result):
                    self.textBrowser.clear()
                    self.isSearchEnabled = True
                    for searchedMessage in self.result:
                        if (searchedMessage['username'] == self.username):
                            self.textBrowser.setAlignment(QtCore.Qt.AlignRight)
                        else:
                            self.textBrowser.setAlignment(QtCore.Qt.AlignLeft)
                        self.textBrowser.append(searchedMessage["message"])
                        self.textBrowser.append("")
                else:
                    return self.showMessage("Ваш запрос не выдал результатов(")

    def abortSearch(self):
        if self.isSearchEnabled:
            self.textBrowser.clear()
            for msg in self.previousMessages:
                if (msg['username'] == self.username):
                    self.textBrowser.setAlignment(QtCore.Qt.AlignRight)
                else:
                    self.textBrowser.setAlignment(QtCore.Qt.AlignLeft)
                self.textBrowser.append(msg["message"])
                self.textBrowser.append("")
            self.isSearchEnabled = False

    def exit(self):
        return requests.get(
            self.__url + "/disconnect",
            json={
                "username": self.username
            }
        )

    # Выйти с акка
    def logOff(self):
        requests.get(
            self.__url + "/disconnect",
            json={
                "username": self.username
            }
        )
        self.close()
        self.timer.stop()
        self.main = Auth()
        return self.main.show()

    # Отключиться от сервера
    def disconnect(self):
        requests.get(
            self.__url + "/disconnect",
            json={
                "username": self.username
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

        self.updateButton.pressed.connect(self.update)
        self.logOffButton.pressed.connect(self.logOff)
        self.exitButton.pressed.connect(self.close)
        self.createServerButton.pressed.connect(self.createServer)
        self.downloadButton.pressed.connect(self.download)
        self.uploadButton.pressed.connect(self.upload)

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

    def logOff(self):
        self.close()
        self.main = Auth()
        return self.main.show()

    def download(self):
        resp = requests.get(URL + "/get_files")
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
                with open(fileNames[0], "rb") as file:
                    upl = requests.get(self.__url + "/upload", data=file.read(), params={
                        "filename": fileName,
                    })
                if "nameIstaken" in upl.json():
                    return showError("Данное имя файла заянято")

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

    def update(self):
        request = requests.get(self.__url + "/get_servers")
        if "someProblems" in request.json():
            showError("Проблемы с сервером")
            return self.close()
        res = request.json()['servers']

        self.layout = QVBoxLayout()
        buttons = list()

        for i in res:
            button = QPushButton(i[1], self)
            button.setFixedSize(186, 30)
            button.pressed.connect(lambda key=i[0]: self.connect(key))
            buttons.append(button)
            self.layout.addWidget(button)
        widget = QWidget()
        widget.setLayout(self.layout)
        self.scrollArea.setWidget(widget)

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

                if "someProblems" in response.json():
                    return showError(str(response.json()))

                self.close()
                self.main = Chat(self.username, self.__url, id)
                return self.main.show()
            else:
                showError("Беды с сервером")


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

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def setText(self):
        self.text = self.textEdit.toPlainText()
        self.closeDialog.emit()
        self.close()

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

        self.selectButton.pressed.connect(
            self.download)

        for i in items:
            self.listWidget.addItem(i)

    def showMessage(self, text):
        '''
        Создаёт окно с ошибкой и выводим текст
        '''
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle("Info")
        msg.exec_()

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
                        text=f"{file} уже скачан\nВы уверены, что хотите перезаписать данные?")
                    accept = QPushButton(text="Да")
                    decline = QPushButton(text="Нет")

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
            self.showMessage(f"Файлы {info[:-2]} были успешно скачаны")
            

    def accept(self, fileName, fileContent):
        self.dial.close()
        self.downloadedFiles[fileName] = fileContent


if __name__ == "__main__":
    try:
        with open("url.txt", "r") as file:
            URL = file.read()
    except:
        pass
    app = QtWidgets.QApplication([])
    window = Chat()
    # window.setFixedSize(490, 540)
    window.show()
    app.exec_()
