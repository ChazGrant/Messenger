# Messenger
# Copyright (C) 2021  ChazGrant (https://github.com/ChazGrant)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMessageBox, QVBoxLayout, QListView, QTextBrowser, QPushButton, QInputDialog, QLineEdit, QDialog, QLabel, QFrame, QAbstractItemView
from PyQt5.QtCore import QPoint, QThread, pyqtSignal
from PyQt5 import Qt

import AuthUI
import MainUI
import LobbyUI
import serverLoginUI
import serverLoginWithoutPasswordUI
import createServerFormUI
import downloadUI
import AdminUI
import searchFormUI
import userCreatorUI
import SecondaryUI
import resources

import pickle
import requests
import hashlib
import datetime
import time
import os
import re
import webbrowser
from crypt import encrypt, decrypt

URL = "http://127.0.0.1:5000"
USERNAME = "CREATOR"
KEY = 314
MAX_MESSAGE_LEN = 100

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
    "AdminPanel":
        {
            "WIDTH": 773,
            "HEIGHT": 464 
        },
    "DownloadHub":
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


def cleanhtml(raw_html: str) -> str:
    '''
        Убирает все теги html
    '''
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def load_data(url: str):
    '''
        Загружает данные из файла и возвращает их
        Иначе возвращает 0
    '''
    try:
        with open("userdata/data.pickle", "rb") as file:
            saved_data = pickle.load(file)
        if "hash" not in saved_data:
            return 0

        response = requests.get(url + "/check_for_session", json={
            "username": saved_data["username"],
            "hash": saved_data["hash"]
        })
        return response.json()["username"] if "username" in response.json() else 0
    except:
        return 0

def show_error(text: str) -> None:
    '''
        Создаёт окно с ошибкой и выводит текст
    '''
    msg = QMessageBox()
    msg.setWindowTitle("Ошибка")
    msg.setIcon(QMessageBox.Critical)
    msg.setText(text)
    msg.setWindowTitle("Error")
    msg.exec_()

def show_message(text: str) -> None:
    '''
    Создаёт окно с ошибкой и выводим текст
    '''
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(text)
    msg.setWindowTitle("Info")
    msg.exec_()

def beautify_text(text: str, search_text: str) -> str:
    if search_text == "":
        raise ValueError("Пустая строка для поиска")

    current_index = 0
    new_str = ""
    while True:
        try:
            # Находим слово, необходимое для поиска, начиная с current_index
            text[current_index:].lower().index(search_text.lower())
        except:
            # Выход из цикла если слова больше нет
            break
        # Находим индекс конца необходимого слова и добавляем к нему текущий индекс
        find_index = text[current_index:].lower().index(search_text.lower())
        sum_index = current_index + find_index
        # Изменяем цвет найденного слова на красный
        new_str += text[current_index:sum_index] + "<span style='color: red;'>" + text[sum_index:sum_index + len(search_text)] + "</span>"

        # Нужен для поиска не с 0 элемента
        current_index += find_index + 1

    # Добавляем последние символы в строку
    new_str += text[sum_index + len(search_text):]
    return new_str

def remove_spaces(string: str) -> str:
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

    def __init__(self, url: str, ts: float, serv_id: int, PM:bool=False, companion:str="") -> None:
        super().__init__()

        self.url = url
        self.timestamp = ts
        self.server_id = serv_id
        self.PM = PM
        self.companion = companion

    def run(self):
        # Запрашиваем сообщения в зависимости от того сервер это или чат
        try:
            if self.PM:
                rs = requests.get(self.url,
                          params={
                              'after': self.timestamp,
                              'chat_id': self.server_id,
                              'companion': self.companion
                          })
            else:
                rs = requests.get(self.url,
                            params={
                                'after': self.timestamp,
                                'server_id': self.server_id
                            })
        except:
            # Нужен для ошибки
            rs = False
        finally:
            # После завершения потока - передаём управление функции
            self.load_finished.emit(rs)


class LoadUsersThread(QThread):
    load_finished = pyqtSignal(object)

    def __init__(self, url: str, serv_id: int, username: str) -> None:
        super().__init__()

        self.__url = url
        self.server_id = serv_id
        self.username = username

    def run(self):
        try:
            # Запрос пользователей с сервера
            rs = requests.get(self.__url,
                          json={
                              "server_id": self.server_id,
                              "username": self.username
                          })
        except:
            rs = False
        finally:
            self.load_finished.emit(rs)


class PushButton(QPushButton):
    right_click = pyqtSignal()
    left_click = pyqtSignal()
    def __init__(self, username, parent=None):
        super(PushButton, self).__init__(parent)
        self.setText(username)
        self.mouse_event:int = 0
        

    def mousePressEvent(self, event):
        if event.button() == 2:
            self.mouse_event = 2
            self.right_click.emit()
        elif event.button() == 1:
            self.mouse_event = 1
            self.left_click.emit()
        event.accept()


class Auth(QtWidgets.QMainWindow, AuthUI.Ui_MainWindow):
    def __init__(self, url:str=URL, key:str=KEY) -> None:
        super().__init__()
        self.setupUi(self)

        self.oldPos = self.pos()
        self.__key = key
        self.__url = url
        self.is_login_showed = True
        self.users.setAlignment(QtCore.Qt.AlignTop)
        self.users.setWidgetResizable(False)

        self.showSavedUsersButton.setToolTip("Показать/Скрыть ваши аккаунты")

        # Прикрепление событий к каждой кнопке
        self.loginButton.pressed.connect(self.login)
        self.exitButton.pressed.connect(self.close)
        self.registrateButton.pressed.connect(self.registration)
        self.showSavedUsersButton.pressed.connect(self.show_hide_login)

        # Установка картинки для кнопки выхода
        self.exitButton.setIcon(QtGui.QIcon(":/resources/Images/cross.png"))
        self.showSavedUsersButton.setIcon(QtGui.QIcon(":/resources/Images/threebars.png"))
        

        # Прозрачное окно без рамок
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def create_saved_users(self) -> None:
        users = [f for _, _, f in os.walk("userdata")]

        used_usernames = []

        if users:
            self.layout = QVBoxLayout()
            users = users[0]
            self.saved_data = list()


            for user in users:
                with open(f"userdata/{user}", "rb") as file:
                    try:
                        tmp = pickle.load(file)
                    except:
                        continue
                    self.saved_data.append({
                        "username": tmp["username"],
                        "hash": tmp["hash"]
                    })

            successful_buttons = 0

            for el in self.saved_data:

                response = requests.get(self.__url + "/check_for_session", json={
                    "username": el["username"], 
                    "hash": el["hash"]
                })

                if "badHash" in response.json():
                    continue

                username = response.json()["username"]
                
                if username in used_usernames:
                    continue
                else:
                    used_usernames.append(username)

                button = PushButton(username, self)
                button.setToolTip("ПКМ для удаления пользователя")
                
                button.setFixedSize(250, 30)

                button.right_click.connect(lambda key=username: self.remove_user(key))
                button.left_click.connect(lambda key=username: self.login(key))

                successful_buttons += 1

                try:
                    self.layout.addWidget(button)
                    widget = QWidget()
                    widget.setLayout(self.layout)
                    self.users.setWidget(widget)
                except:
                    pass
                
            if successful_buttons:
                self.is_login_showed = False
            else:
                self.is_login_showed = False
                self.show_hide_login()
        else:
            self.is_login_showed = False
            self.show_hide_login()
        
    def remove_user(self, username):
        accepted = False
        self.dial = QDialog(self)
        label = QLabel(
            text=f"Вы уверены, что хотите выйти?")
        
            
        accept = QPushButton(text="Да")
        decline = QPushButton(text="Нет")

        accept.pressed.connect(lambda: self.accept_remove_user(username))
        decline.pressed.connect(lambda: self.dial.close())

        self.dial.setLayout(QVBoxLayout())
        self.dial.layout().addWidget(label)
        self.dial.layout().addWidget(accept)
        self.dial.layout().addWidget(decline)
        self.dial.setFixedSize(310, 150)
        self.dial.exec_()

    def accept_remove_user(self, username):
        self.dial.close()
        tmp_users = [f for _, _, f in os.walk("userdata")]
        if tmp_users:
            tmp_users = tmp_users[0]
        else:
            return
        for f in tmp_users:
            with open("userdata/" + f, "rb") as file:
                try:
                    tmp = pickle.load(file)
                except:
                    continue

                if tmp["username"] == encrypt(username, self.__key):
                    open("userdata/" + f, "wb")
                    break
            
        self.create_saved_users()

    def show_hide_login(self) -> None:
        if self.is_login_showed:
            self.users.show()

            self.label.setText("Ваши аккаунты")

            self.usernameText.hide()
            self.passwordText.hide()
            self.loginButton.hide()
            self.registrateButton.hide()
            self.label_2.hide()
            self.rememberMe.hide()

            self.is_login_showed = False

            self.create_saved_users()

        else:
            self.users.hide()

            self.label.setText("Вход в аккаунт")

            self.usernameText.show()
            self.passwordText.show()
            self.loginButton.show()
            self.label_2.show()
            self.rememberMe.show()
            self.registrateButton.show()

            self.is_login_showed = True

    def save_data(self, username: str) -> int:
        if (os.path.exists("userdata/" + username + ".pickle")):
            return 1

        response = requests.get(self.__url + "/create_session", json={
                "username": username
            })
        if "someProblems" in response.json():
            show_error("Возникли неполадки во время сохранения данных")
            return 0
       
        
        with open(f"userdata/{username}.pickle", "wb") as file:
            # Запись json-данных в файл 
            pickle.dump({
                "username": encrypt(username, self.__key),
                "hash": response.json()["hash"]
            }, file) 
            return 1

    def clear_spaces(self, string: str) -> str:
        string = string.replace(' ', '')
        string = string.replace('\n', '')
        string = string.replace('\t', '')
        return string

    def mousePressEvent(self, event):
        # Меняет позицию в зависимости куда нажали мышкой
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        # Перемещает окно в необходимое направление
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def login(self, username:str="") -> None:
        if username:
            self.users.setEnabled(False)
            main = Lobby(username=username, url=self.__url)
            self.close()
            return main.show()
        ### Извлекаем имя пользователя и пароль из текстовых полей ###
        self.username = self.clear_spaces(self.usernameText.text())
        self.__password = remove_spaces(self.passwordText.text())

        # Передаём логин и пароль на сервер
        response = requests.get(self.__url + '/login',
                                json={
                                    'username': self.username,
                                    'password': self.__password
                                })

        if response.status_code == 200:
            ### Обработка ошибки пустых полей ###
            if "isNotFilled" in response.json():
                return show_error("Не все поля заполнены")

            ### Обработка ошибки неверного пароля ###
            if "invalidData" in response.json():
                return show_error("Неверное имя пользователя и/или пароль")

            self.close()
            # Попытка сохранить данные если checkbox активирован
            if self.rememberMe.isChecked():
                response = self.save_data(self.username)
                if not response:
                    show_error("Ваши данные не были сохранены")

            # Открытие окна "Lobby"
            self.main = Lobby(self.username, self.__url)
            return self.main.show()
        else:
            show_error("Ошибка в подключении к серверу")
            return self.close()

    def registration(self) -> None:
        # Игнорирование пустых символов
        self.username = " ".join(self.usernameText.text().split())
        self.__password = self.passwordText.text()
        response = requests.get(self.__url + '/reg',
                                json={
                                    'username': self.username,
                                    'password': self.__password
                                })

        if response.status_code == 200:
            if "isNotFilled" in response.json():
                return show_error("Не все поля заполнены")

            if "badPassword" in response.json():
                return show_error("Пароль должен иметь специальные символы, буквы и цифры. Длина пароля от 8 до 16")

            if "nameIsTaken" in response.json():
                return show_error("Данное имя пользователя уже занято")

            self.close()
            
            # Попытка сохранить данные если checkbox активирован
            if self.rememberMe.isChecked():
                response = self.save_data(self.username)
                if not response:
                    show_error("Ваши данные не были сохранены")

            # Открытие окна "Lobby"
            self.main = Lobby(self.username, self.__url)
            return self.main.show()
        else:
            show_error(
                "При попытке подключиться к серверу возникла ошибка")
            return self.close()


class Chat(QtWidgets.QMainWindow, MainUI.Ui_MainWindow):
    def __init__(self, username:str=USERNAME, url:str=URL, server_id:int=1) -> None:
        super().__init__()
        self.setupUi(self)

        self.sendButton.setToolTip("Отправить")

        # Прикрепление событий к каждой кнопке
        self.sendButton.pressed.connect(self.send_message)
        self.exitButton.pressed.connect(self.close)
        self.disconnectButton.pressed.connect(self.disconnect)
        self.exitAccountButton.pressed.connect(self.log_off)
        self.searchButton.pressed.connect(self.search)
        self.abortSearchButton.pressed.connect(self.abort_search)
        self.downloadButton.pressed.connect(self.download)
        self.uploadButton.pressed.connect(self.upload)
        self.showUsersButton.pressed.connect(self.show_users)
        self.backButton.pressed.connect(self.backward)
        self.forwardButton.pressed.connect(self.forward)
        self.sortingTypeButton.pressed.connect(self.change_sorting_type)

        # Установка иконок для каждой кнопки
        self.exitButton.setIcon(QtGui.QIcon(":/resources/Images/cross.png"))
        self.showUsersButton.setIcon(QtGui.QIcon(":/resources/Images/settings.png"))
        self.backButton.setIcon(QtGui.QIcon(":/resources/Images/left.png"))
        self.forwardButton.setIcon(QtGui.QIcon(":/resources/Images/right.png"))
        self.sendButton.setIcon(QtGui.QIcon(":/resources/Images/send.png"))
        self.exitAccountButton.setIcon(QtGui.QIcon(":/resources/Images/exit_from_acc.png"))
        self.disconnectButton.setIcon(QtGui.QIcon(":/resources/Images/disconnect.png"))

        # Прозрачное окно без рамок
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Прикрепление области прокрутки к верху приложения
        self.scrollArea.setAlignment(QtCore.Qt.AlignTop)
        # Запрет на изменение размера
        self.scrollArea.setWidgetResizable(False)

        self.oldPos = self.pos()
        self.timestamp = 0.0
        self.username = username

        # Переменные для поиска по сообщениям
        self.previous_messages = []
        self.previous_message_date = 0
        self.is_search_enabled = False

        self.__key = KEY
        self.__url = url
        self.server_id = server_id
        self.sorting_type = "Online"
        self.sorting_type_is_changed = False
        self.hash = ""

        # Скрытие кнопок, которые потом появляются при поиске сообщений
        self.forwardButton.hide()
        self.backButton.hide()
        self.messagesAmount.hide()
        self.abortSearchButton.hide()

        self.connect()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)

    def change_sorting_type(self) -> None:
        self.sorting_type = "Online" if self.sorting_type == "Offline" else "Offline"

        if self.sorting_type == "Online":
            self.sortingTypeButton.setStyleSheet("background-color: green;")
            self.sortingTypeButton.setText("Онлайн")
        else:
            self.sortingTypeButton.setStyleSheet("background-color: red;")
            self.sortingTypeButton.setText("Офлайн")
        
        self.sorting_type_is_changed = True

    def check_for_boundaries(self) -> None:
        # Крайняя правая граница
        if self.current_line + 1 == self.matches:
            self.forwardButton.hide()
            if self.current_line - 1 >= 0:
                self.backButton.show()
            return 1
        elif self.forwardButton.isHidden():
            self.forwardButton.show()

        # Крайняя левая граница
        if self.current_line - 1 < 0:
            self.backButton.hide()
            if self.current_line + 1 < self.matches:
                self.forwardButton.show()
            return -1
        elif self.backButton.isHidden():
            self.backButton.show()

        return 0

    def refill_search_browser(self) -> None:
        self.textBrowser.clear()

        self.shifts = list()

        is_new_date = 0
        current_shift = 3
        self.previous_message_date = 0
        for searched_message in self.result:

            if "isNotForSearch" in searched_message:
                current_shift += int(self.time_management(searched_message["timestamp"]))
            else:
                is_new_date = self.time_management(searched_message["timestamp"])

            if (searched_message['username'] == self.username):
                self.textBrowser.setAlignment(QtCore.Qt.AlignRight)
            else:
                self.textBrowser.setAlignment(QtCore.Qt.AlignLeft)

            if "isNotForSearch" not in searched_message:
                if is_new_date:
                    current_shift += 2 
                    self.shifts.append(current_shift)
                else:
                    self.shifts.append(current_shift)

            self.textBrowser.append(searched_message["message"])
            self.textBrowser.append("")

    def backward(self) -> None:
        self.current_line -= 1
        self.messagesAmount.setText(str(self.current_line + 1) + "/" + str(self.matches))

        previous_text = self.textBrowser.document().findBlockByLineNumber(self.msg_lines[self.current_line + 1] * 2 + self.shifts[self.current_line + 1]).text()
        current_text = self.textBrowser.document().findBlockByLineNumber(self.msg_lines[self.current_line] * 2 + self.shifts[self.current_line]).text()

        self.underline_text(current_text)
        self.remove_underline_from_text(previous_text)

        self.refill_search_browser()

        current_text = self.textBrowser.document().findBlockByLineNumber(self.msg_lines[self.current_line] * 2 + self.shifts[self.current_line])
        cursor = QtGui.QTextCursor(current_text)
        self.textBrowser.setTextCursor(cursor)

        self.check_for_boundaries()

    def forward(self) -> None:
        self.current_line += 1
        self.messagesAmount.setText(str(self.current_line + 1) + "/" + str(self.matches))

        previous_text = self.textBrowser.document().findBlockByLineNumber(self.msg_lines[self.current_line - 1] * 2 + self.shifts[self.current_line - 1]).text()
        current_text = self.textBrowser.document().findBlockByLineNumber(self.msg_lines[self.current_line] * 2 + self.shifts[self.current_line]).text()

        self.underline_text(current_text)
        self.remove_underline_from_text(previous_text)

        self.refill_search_browser()

        current_text = self.textBrowser.document().findBlockByLineNumber(self.msg_lines[self.current_line] * 2 + self.shifts[self.current_line])
        cursor = QtGui.QTextCursor(current_text)
        self.textBrowser.setTextCursor(cursor)

        self.check_for_boundaries()

    def mousePressEvent(self, event) -> None:
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event) -> None:
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    # Переопределяем метод выхода из приложения
    def closeEvent(self, event) -> None:
        self.exit()
        event.accept()

    def show_users(self) -> None:
        self.main = AdminPanel(server_id=self.server_id, url=self.__url, is_creator=self.username=="CREATOR")
        self.main.show()

    def download(self) -> None:
        resp = requests.get(self.__url + "/get_files", json={
            "server_id": self.server_id
        })


        if resp.status_code == 200:
            if "someProblems" in resp.json():
                return show_error("Возникли неполадки с сервером")

            all_files = resp.json()['allFiles']
            self.main = DownloadHub(self.server_id, all_files)
            return self.main.show()

    def upload(self) -> None:
        # Переменные для выбора файлов
        frame = QtWidgets.QFileDialog()
        frame.setFileMode(QtWidgets.QFileDialog.AnyFile)

        if frame.exec_():
            file_names = frame.selectedFiles()
            file_name, ok_is_pressed = QInputDialog.getText(
                self, "Название файла", "Введите новое название файла: ", QLineEdit.Normal, "")
            if ok_is_pressed:
                if file_name == "":
                    file_name = file_names[0].split("/")[-1]
                else:
                    file_name = file_name + "." + file_names[0].split("/")[-1].split('.')[1]
                with open(file_names[0], "rb") as file:
                    upl = requests.get(self.__url + "/upload", data=file.read(), params={
                        "filename": file_name,
                        "server_id": self.server_id
                    })
                if "nameIstaken" in upl.json():
                    return show_error("Данное имя файла заянято")

    def connect(self) -> None:
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
            show_error("При попытке подключиться к серверу возникли ошибки")
            return self.close()

    def update(self) -> None:
        if not self.is_search_enabled:
            try:
                # Запускаем поток, который обновляет пользователей при принятии ответа от сервера
                self.users_thread = LoadUsersThread(
                    self.__url + "/get_users", self.server_id, self.username)
                self.users_thread.load_finished.connect(self.update_users)
                self.users_thread.finished.connect(self.users_thread.deleteLater)
                self.users_thread.start()

                # Запускаем поток, который обновляет сообщения при принятии ответа от сервера
                self.msg_thread = LoadMessagesThread(
                    self.__url + "/get_messages", self.timestamp, self.server_id)
                self.msg_thread.load_finished.connect(self.update_messages)
                self.msg_thread.finished.connect(self.msg_thread.deleteLater)
                self.msg_thread.start()
            except:
                self.timer.stop()
                show_error("Вознилки неполадки")
                return self.close()

    def update_users(self, rs) -> None:
        try:
            # Если нет status_code значит эта переменная типа Boolean
            rs.status_code
        except AttributeError:
            return self.close()

        if rs.status_code == 200:
            if "someProblems" in rs.json():
                return show_error("Возникли неполадки")
            res = rs.json()['res']

            if int(rs.json()["isBanned"]):
                self.timer.stop()
                show_error("Вы были забанены")
                self.exit()
                return self.close()

            # Пример входных значений:
            # ['Илья 0 1611867749.54902', 'Тест 0 1611865145.06428', 'qwerty 0 1612211290.75964', '123 0 1611867690.18362']

            for user_info in res:
                user = user_info.split()

            server_hash = rs.json()["serverHash"]

            if self.hash == "":
                self.hash = server_hash

            elif server_hash == self.hash and not self.sorting_type_is_changed:
                return

            online_users = list()
            offline_users = list()

            self.hash = server_hash

            for user_info in res:
                user = user_info.split()

                if user[0] == self.username:
                    continue
                
                user[1] = int(user[1])
                last_time_seen = datetime.datetime.fromtimestamp(float(user[2]))
                current_time = datetime.datetime.fromtimestamp(time.time())

                if (current_time.year > last_time_seen.year):
                    if (current_time.day > last_time_seen.day) and (current_time.month == last_time_seen.month):
                        status = "Online" if user[1] else f"Offline {last_time_seen.strftime('%H:%M %d/%m/%y')}"

                    elif (current_time.month > last_time_seen.month):
                        status = "Online" if user[1] else f"Offline {last_time_seen.strftime('%H:%M %d/%m/%y')}"

                    else:
                        status = "Online" if user[1] else f"Offline {last_time_seen.strftime('%H:%M %d/%m/%y')}"

                else:
                    if (current_time.day > last_time_seen.day) and (current_time.month == last_time_seen.month):
                        status = "Online" if user[1] else f"Offline {last_time_seen.strftime('%H:%M %d/%m')}"

                    elif (current_time.month > last_time_seen.month):
                        status = "Online" if user[1] else f"Offline {last_time_seen.strftime('%H:%M %d/%m')}"

                    else:
                        status = "Online" if user[1] else f"Offline {last_time_seen.strftime('%H:%M')}"

                if user[1]:
                    online_users.append(user[0] + f' {status}')
                    
                else:
                    offline_users.append(user[0] + f' {status}')
            
            self.layout = QVBoxLayout()

            self.users_buttons = list()

            # Последовательность при которой выводятся кнопки пользователей
            if self.sorting_type == "Online":
                for onu in online_users:
                    if onu.split()[0] == self.username:
                        continue
                    
                    # Создаём кнопки для каждого пользователя с его именем и добавляем их в layout
                    button = QPushButton(onu.split()[0], objectName="whisperButton")
                    button.setFixedSize(220, 30)
                    button.pressed.connect(lambda key=onu.split()[0]: self.whisper(key))
                    button.setIcon(Qt.QIcon(":/resources/Images/online.png"))
                    button.installEventFilter(self)
                    button.setStyleSheet('''
                        color: black;
                        background: transparent;
                        text-align: left;
                    ''')

                    button.setToolTip(onu.split()[1])
                    

                    self.users_buttons.append(button)

                    self.layout.addWidget(button) 
                for ofu in offline_users:
                    if ofu.split()[0] == self.username:
                        continue

                    # Создаём кнопки для каждого пользователя с его именем и добавляем их в layout
                    button = QPushButton(ofu.split()[0], objectName="whisperButton")
                    button.setFixedSize(220, 30)
                    button.pressed.connect(lambda key=ofu.split()[0]: self.whisper(key))
                    button.setIcon(Qt.QIcon(":/resources/Images/offline.png"))
                    button.installEventFilter(self)
                    button.setStyleSheet('''
                        color: black;
                        background: transparent;
                        text-align: left;
                    ''')
                    self.users_buttons.append(button)

                    # Установка текста при наведении на кнопку
                    try:
                        button.setToolTip(ofu.split()[1] + "\n" + ofu.split()[2] + " " + ofu.split()[3])
                    except:
                        button.setToolTip(ofu.split()[1] + "\n" + ofu.split()[2])
                    

                    self.layout.addWidget(button)

                widget = QWidget()
                widget.setLayout(self.layout)
                self.scrollArea.setWidget(widget)

            else:
                for ofu in offline_users:
                    if ofu.split()[0] == self.username:
                        continue

                    # Создаём кнопки для каждого пользователя с его именем и добавляем их в layout
                    button = QPushButton(ofu.split()[0], objectName="whisperButton")
                    button.setFixedSize(220, 30)
                    button.pressed.connect(lambda key=ofu.split()[0]: self.whisper(key))
                    button.setIcon(Qt.QIcon(":/resources/Images/offline.png"))
                    button.installEventFilter(self)
                    button.setStyleSheet('''
                        color: black;
                        background: transparent;
                        text-align: left;
                    ''')
                    self.users_buttons.append(button)

                    # Установка текста при наведении на кнопку
                    try:
                        button.setToolTip(ofu.split()[1] + "\n" + ofu.split()[2] + " " + ofu.split()[3])
                    except:
                        button.setToolTip(ofu.split()[1] + "\n" + ofu.split()[2])
                    

                    self.layout.addWidget(button)
                for onu in online_users:
                    if onu.split()[0] == self.username:
                        continue
                    
                    # Создаём кнопки для каждого пользователя с его именем и добавляем их в layout
                    button = QPushButton(onu.split()[0], objectName="whisperButton")
                    button.setFixedSize(220, 30)
                    button.pressed.connect(lambda key=onu.split()[0]: self.whisper(key))
                    button.setIcon(Qt.QIcon(":/resources/Images/online.png"))
                    button.installEventFilter(self)
                    button.setStyleSheet('''
                        color: black;
                        background: transparent;
                        text-align: left;
                    ''')

                    button.setToolTip(onu.split()[1])
                    

                    self.users_buttons.append(button)

                    self.layout.addWidget(button) 

                widget = QWidget()
                widget.setLayout(self.layout)
                    
                self.scrollArea.setWidget(widget)
        else:
            return self.close()

    def eventFilter(self, source, event) -> None:
        if event.type() == QtCore.QEvent.Enter and source.objectName() == "whisperButton":
            source.setStyleSheet('''
                color: orange;
            ''')

        elif event.type() == QtCore.QEvent.Leave:
            source.setStyleSheet('''
                        color: black;
                        background: transparent;
                        text-align: left;
                    ''')
            

        return super().eventFilter(source, event)

    def whisper(self, username: str) -> None:
        response = requests.get(self.__url + "/get_chat_id", json={
            "users": self.username + username,
            "usersReversed": username + self.username
        })

        chat_id = response.json()["chat_id"]

        self.main = privateChat(self.username, username, chat_id, self.__url)
        return self.main.show()

    def time_management(self, message_date: datetime) -> int:
        if not self.previous_message_date:
            self.previous_message_date = message_date
            self.textBrowser.setAlignment(QtCore.Qt.AlignCenter)
            self.textBrowser.append("<b>Начало переписки</b>")
            self.textBrowser.append("<b>" + message_date.strftime("%d/%m/%Y") + "</b>")
            self.textBrowser.append("")
            return 0
                    
        elif self.previous_message_date.year < message_date.year:
            self.previous_message_date = message_date
            self.textBrowser.setAlignment(QtCore.Qt.AlignCenter)
            self.textBrowser.append("<b>" + message_date.strftime("%d/%m/%Y") + "</b>")
            self.textBrowser.append("")
            return 2

        elif self.previous_message_date.month < message_date.month:
            self.previous_message_date = message_date
            self.textBrowser.setAlignment(QtCore.Qt.AlignCenter)
            self.textBrowser.append("<b>" + message_date.strftime("%d/%m/%Y") + "</b>")
            self.textBrowser.append("")
            return 2
        
        elif self.previous_message_date.month == message_date.month and self.previous_message_date.day < message_date.day:
            self.previous_message_date = message_date
            self.textBrowser.setAlignment(QtCore.Qt.AlignCenter)
            self.textBrowser.append("<b>" + message_date.strftime("%d/%m/%Y") + "</b>")
            self.textBrowser.append("")
            return 2

        return 0

    def update_messages(self, rs) -> None:
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

                    message_date = datetime.datetime.fromtimestamp(
                        message[2])      

                    self.time_management(message_date)

                    if message[0] == self.username:
                        self.textBrowser.setAlignment(QtCore.Qt.AlignRight)
                    else:
                        self.textBrowser.setAlignment(QtCore.Qt.AlignLeft)

                    self.textBrowser.append("<b>" + dt + " " +
                                                message[0] + "</b>:<br>" + decrypt(message[1], self.__key))

                    self.textBrowser.append("")
                    self.timestamp = message[2]
        else:
            show_error(
                "При попытке подключиться к серверу возникли ошибки")
            return self.close()

    def send_message(self) -> None:
        text = remove_spaces(self.textEdit.toPlainText())
        if len(text) > MAX_MESSAGE_LEN:
            return show_error("Длина сообщения должна быть не более 100")
        
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
                    show_error("Сообщение не может быть пустым")

                if "invalidUsername" in response.json():
                    show_error("Данного пользователя не существует")

                return self.textEdit.setText("")
            else:
                self.timer.stop()
                show_error("Ошибка в подключении к серверу")
                return self.close()

    def search(self) -> None:
        self.sForm = searchForm()
        self.sForm.show()
        
        # Текст поиска, чекбокс для поиска по тексту, чекбокс для поиска по имени пользователя
        self.sForm.closeDialog.connect(lambda: self.find(self.sForm.text, self.sForm.checkBox.isChecked(), self.sForm.checkBox_2.isChecked()))

    ### FORMATTING TEXT FOR SEARCH ###

    def remove_empty_characters_from_text(self, text_to_manage: str) -> str:
        for _ in text_to_manage:
            text_to_manage = text_to_manage.replace("\n", "").replace(" ", "")
        
        return " ".join(text_to_manage.split())

    def remove_underline_from_text(self, text_to_deunderline: str) -> bool:
        # В консоле есть символ, который отображается как ?
        # Поэтому я знаю только его битовое представление
        byte = b'\xe2\x80\xa8'
        for msg in self.result:
            for ch in text_to_deunderline:
                    if ch.encode() == byte:
                        text_to_deunderline = text_to_deunderline.replace(ch, "")

            # Создаём временную переменную чтобы сравнить её с тем, что было передано в качестве аргумента
            tmp = self.remove_empty_characters_from_text(cleanhtml(msg["message"]))
            text_to_deunderline = self.remove_empty_characters_from_text(text_to_deunderline)

            # Убираем жирный текст у выделенного текста
            if tmp == text_to_deunderline:
                    msg["message"] = msg["message"].replace("<strong>", "").replace("</strong>", "")
                    return True

    def underline_text(self, text_to_underline: str) -> bool:
        # Известное толькое битовое представление символа
        byte = b'\xe2\x80\xa8'
        for msg in self.result:
            for ch in text_to_underline: 
                if ch.encode() == byte:
                    text_to_underline = text_to_underline.replace(ch, "")

            tmp = self.remove_empty_characters_from_text(cleanhtml(msg["message"]))
            text_to_underline = self.remove_empty_characters_from_text(text_to_underline)

            if tmp == text_to_underline:
                msg["message"] = msg["message"][:msg["message"].index("<br>") + 4] + "<strong>" + msg["message"][msg["message"].index("<br>") + 4:] + "</strong>"
                return True

    ###################################

    def find(self, text: str, name_is_checked: bool, msg_is_checked: bool) -> None:
        self.word = remove_spaces(text)
        self.result = []

        if self.word:
            response = requests.get(
                self.__url + '/get_messages',
                params={
                    'after': 0.0,
                    'server_id': self.server_id
                })

            if response.status_code == 200:
                self.matches = 0
                self.msg_lines = list()
                self.total_lines = 0

                if not name_is_checked and not msg_is_checked:
                    return show_error("Выберите критерии поиска")

                messages = response.json()['messages']
                self.messages = messages
                
                for message in messages:

                    dt = datetime.datetime.fromtimestamp(
                            message[2]).strftime('%H:%M')

                    if self.word.lower() in message[0].lower() and name_is_checked:
                        self.dict = {"username": message[0], 
                                    "message": ("<b>" + dt + " " + beautify_text(message[0], self.word) + "</b>:<br>" + decrypt(message[1], self.__key) + ""),
                                    "timestamp": datetime.datetime.fromtimestamp(message[2])}
                        self.result.append(self.dict)
                        self.msg_lines.append(self.total_lines)

                        self.matches += 1

                    elif self.word.lower() in decrypt(message[1], self.__key).lower() and msg_is_checked:
                        self.dict = {"username": message[0], 
                                    "message": ("<b>" + dt + " " +
                                                message[0] + "</b>:<br>" + beautify_text(decrypt(message[1], self.__key), self.word) + ""),
                                    "timestamp": datetime.datetime.fromtimestamp(message[2])}

                        self.result.append(self.dict)
                        self.msg_lines.append(self.total_lines)

                        self.matches += 1

                    else:
                        self.dict = {"username": message[0], 
                                    "message": ("<b>" + dt + " " +
                                                message[0] + "</b>:<br>" + decrypt(message[1], self.__key) + ""),
                                    "timestamp": datetime.datetime.fromtimestamp(message[2]),
                                    "isNotForSearch": True
                                    }
                        self.result.append(self.dict)

                    self.total_lines += 1

                    if not self.is_search_enabled:
                        self.dict = {"username": message[0], 
                                    "message": ("<b>" + dt + " " +
                                                message[0] + "</b>:<br>" + decrypt(message[1], self.__key) + ""),
                                    "timestamp": datetime.datetime.fromtimestamp(message[2])}
                        self.previous_messages.append(self.dict)

                if (self.matches):
                    self.sForm.close()
                    self.textBrowser.clear()
                    self.shifts = list()

                    current_shift = 3

                    self.is_search_enabled = True
                    self.previous_message_date = 0
                    for searched_message in self.result:
                        if "isNotForSearch" in searched_message:
                            current_shift += int(self.time_management(searched_message["timestamp"]))
                        else:
                            is_new_date = self.time_management(searched_message["timestamp"])

                        if (searched_message['username'] == self.username):
                            self.textBrowser.setAlignment(QtCore.Qt.AlignRight)
                        else:
                            self.textBrowser.setAlignment(QtCore.Qt.AlignLeft)
                        self.textBrowser.append(searched_message["message"])
                        self.textBrowser.append("")
                        if "isNotForSearch" not in searched_message:
                            if is_new_date:
                                current_shift += 2 
                                self.shifts.append(current_shift)
                            else:
                                self.shifts.append(current_shift)

                    
                    self.underline_text(self.textBrowser.document().findBlockByLineNumber(self.msg_lines[0] * 2 + self.shifts[0]).text())
                    self.refill_search_browser()

                    current_text = self.textBrowser.document().findBlockByLineNumber(self.msg_lines[0] * 2 - 1 + self.shifts[0])
                    cursor = QtGui.QTextCursor(current_text)
                    self.textBrowser.setTextCursor(cursor)

                    self.forwardButton.show()
                    self.messagesAmount.show()
                    self.searchButton.hide()
                    self.abortSearchButton.show()

                    self.messagesAmount.setText("1/" + str(self.matches))

                    self.current_line = 0

                    self.check_for_boundaries()

                else:
                    self.result = []
                    return show_message("Ваш запрос не выдал результатов(")
        else:
            return show_error("Поле поиска не может быть пустым")

    def abort_search(self) -> None:
        self.previous_message_date = 0

        if self.is_search_enabled:
            self.textBrowser.clear()
            for msg in self.previous_messages:
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
            self.abortSearchButton.hide()

            self.is_search_enabled = False

    def exit(self) -> None:
        resp = requests.get(
            self.__url + "/disconnect",
            json={
                "username": self.username,
                "server_id": self.server_id
            }
        )
        if "someProblems" in resp.json():
            return show_error(resp.json()["someProblems"])

    # Выйти с акка
    def log_off(self) -> None:
        requests.get(
            self.__url + "/disconnect",
            json={
                "username": self.username,
                "server_id": self.server_id
            }
        )

        self.close()
        self.timer.stop()
        self.main = Auth()
        return self.main.show()

    # Отключиться от сервера
    def disconnect(self) -> None:
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


class Lobby(QtWidgets.QMainWindow, LobbyUI.Ui_MainWindow):
    def __init__(self, username:str=USERNAME, url:str=URL) -> None:
        super().__init__()
        self.setupUi(self)

        self.__url = url
        self.username = username
        self.oldPos = self.pos()

        # Иконки для кнопок
        self.exitButton.setIcon(QtGui.QIcon(":/resources/Images/cross.png"))
        self.showUsersButton.setIcon(QtGui.QIcon(":/resources/Images/settings.png"))
        self.createServerButton.setIcon(QtGui.QIcon(":/resources/Images/plus.png"))

        self.createServerButton.setToolTip("Создать сервер")
        self.showUsersButton.setToolTip("Админ меню")

        # Проверка на админа всех админов   
        if self.username != "CREATOR":
            self.createServerButton.hide()
            self.showUsersButton.hide()

        # События кнопок
        self.updateButton.pressed.connect(self.update)
        self.logOffButton.pressed.connect(self.log_off)
        self.exitButton.pressed.connect(self.close)
        self.createServerButton.pressed.connect(self.create_server)
        self.downloadButton.pressed.connect(self.download)
        self.uploadButton.pressed.connect(self.upload)
        self.showUsersButton.pressed.connect(self.show_users)

        # Область прокрутки привязываем к верху
        self.scrollArea.setAlignment(QtCore.Qt.AlignTop)
        self.scrollArea.setWidgetResizable(False)

        # Прозрачное окно без рамок
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Обновляем все сервера
        self.update()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def update(self) -> None:
        try:
            request = requests.get(self.__url + "/get_servers")

            if request.status_code == 200:

                if "someProblems" in request.json():
                    return show_error("Проблемы с сервером")

                res = request.json()['servers']
            else:
                return show_error("Сервер не отвечает")
        except:
            return show_error("Возникли неполадки")

        self.layout = QVBoxLayout()
        time = 100

        self.updateButton.hide()
        for i in res:
            # i[0] - id
            # i[1] - server_name
            button = QPushButton(i[1], self)
            button.setFixedSize(186, 30)
            button.pressed.connect(lambda key=[i[0], i[1]]: self.show_server_login(key[1], key[0]))

            # Задержка перед созданием следующей кнопки
            loop = QtCore.QEventLoop()
            QtCore.QTimer.singleShot(time, loop.quit)
            loop.exec_()

            self.layout.addWidget(button)
            widget = QWidget()
            widget.setLayout(self.layout)
            self.scrollArea.setWidget(widget)

        self.updateButton.show()

    def log_off(self) -> None:
        self.close()

        self.main = Auth()
        return self.main.show()

    def download(self) -> None:
        resp = requests.get(URL + "/get_files", json={})

        if resp.status_code == 200:
            if "someProblems" in resp.json():
                return show_error("Возникли неполадки с сервером")

            all_files = resp.json()['allFiles']

            self.main = DownloadHub("public", all_files)
            self.main.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            self.main.setAttribute(QtCore.Qt.WA_TranslucentBackground)

            return self.main.show()

    def upload(self) -> None:
        frame = QtWidgets.QFileDialog()
        frame.setFileMode(QtWidgets.QFileDialog.AnyFile)

        if frame.exec_():
            file_names = frame.selectedFiles()
            file_name, ok_is_pressed = QInputDialog.getText(
                self, "Название файла", "Введите новое название файла: ", QLineEdit.Normal, "")

            if ok_is_pressed:
                if file_name == "":
                    file_name = file_names[0].split("/")[-1]

                else:
                    file_name = file_name + "." + file_names[0].split("/")[-1].split('.')[1]

                with open(file_names[0], "rb") as file:
                    upl = requests.get(self.__url + "/upload", data=file.read(), params={
                        "filename": file_name,
                    })
                if "nameIstaken" in upl.json():
                    return show_error("Данное имя файла заянято")

    def show_users(self) -> None:
        self.main = AdminPanel(server_id=0, is_creator=True, url=self.__url)
        return self.main.show()

    def create_server(self) -> None:
        self.main = createServerForm(username=self.username)
        self.main.show()

    def show_server_login(self, server_name: str, id: int) -> None:

        res = requests.get(self.__url + "/get_users_amount", json={
            "id": id
        })

        if res.status_code == 200:
            server_name = server_name
            users_amount = res.json()["users_amount"]

        server_password = requests.get(self.__url + "/get_server_password_existence", json={
            "server_id": id
        })


        if server_password.json()["server_password"] == "d41d8cd98f00b204e9800998ecf8427e":
            self.main = serverLoginWithoutPassword(
                url=self.__url,
                username=self.username,
                server_id=id,
                name=server_name,
                users_amount=users_amount)
        else:
            self.main = serverLogin(
                url=self.__url,
                username=self.username,
                server_id=id,
                name=server_name,
                users_amount=users_amount
                )
        self.main.show()

        self.main.login_succeeded.connect(lambda key=id: self.connect(id))

    def connect(self, id: int) -> None:
        self.main = Chat(self.username, self.__url, id)
        self.main.show()
        return self.close()


class AdminPanel(QtWidgets.QMainWindow, AdminUI.Ui_MainWindow):
    def __init__(self, server_id: int, is_creator:bool, url:str=URL) -> None:
        super().__init__()
        self.setupUi(self)

        # Привязка событий к кнопкам
        self.banButton.pressed.connect(self.ban_user)
        self.createUserButton.pressed.connect(self.create_user)
        self.exitButton.pressed.connect(self.close)

        # Переменные
        self.__url = url
        self.server_id = server_id
        self.is_creator = is_creator

        # Иконки
        self.exitButton.setIcon(QtGui.QIcon(":/resources/Images/cross.png"))

        # Прозрачное окно без рамок
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        if server_id:
            self.tree.setHeaderLabels(['Пользователи в данном чате'])
        else:
            self.tree.setHeaderLabels(['Пользователи чатах'])
        self.insert_users()

    def insert_users(self) -> None:
        res = requests.get(self.__url + "/get_users", json={
                            "server_id": self.server_id,
                            "for_admin": True
                        })
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
                response = requests.get(self.__url + "/get_server_name", json={
                    "server_id": server_id
                })
                server_name = response.json()["server_name"]
                self.current_server_id = QtWidgets.QTreeWidgetItem(self.tree, [server_name])

                for user in users[server_id]:
                    u = user.split()
                    status = "Online" if int(u[1]) else "Offline"
                    status = "Banned" if int(u[5]) else status
                    us = QtWidgets.QTreeWidgetItem(self.current_server_id, [u[0]])
                    
                    QtWidgets.QTreeWidgetItem(us, [f"Статус: {status}"])
                    QtWidgets.QTreeWidgetItem(us, [f"Последнее время входа: {datetime.datetime.fromtimestamp(float(u[2])).strftime('%H:%M:%S %d/%m/%y')}"])
                    if int(u[1]):
                        total_time = (
                                float(u[4]) + time.time() - float(u[3]))
                        QtWidgets.QTreeWidgetItem(us, [f"Общее время онлайн: {self.calculate_time(total_time)}"])
                    else:
                        QtWidgets.QTreeWidgetItem(us, [f"Общее время онлайн: {self.calculate_time(float(u[4]))}"])
            return

        if "someProblems" in res.json():
            return show_error(res.json()["someProblems"])
        users = res.json()['res']
        for user in users:
            u = user.split()
            status = "Online" if int(u[1]) else "Offline"
            status = "Banned" if int(u[5]) else status
            us = QtWidgets.QTreeWidgetItem(self.tree, [u[0]])
            
            QtWidgets.QTreeWidgetItem(us, [f"Статус: {status}"])
            QtWidgets.QTreeWidgetItem(us, [f"Последнее время входа: {datetime.datetime.fromtimestamp(float(u[2])).strftime('%H:%M:%S %d/%m/%y')}"])
            if int(u[1]):
                total_time = (
                        float(u[4]) + time.time() - float(u[3]))
                QtWidgets.QTreeWidgetItem(us, [f"Общее время онлайн: {self.calculate_time(total_time)}"])
            else:
                QtWidgets.QTreeWidgetItem(us, [f"Общее время онлайн: {self.calculate_time(float(u[4]))}"])

    def calculate_time(self, time: float) -> str:
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

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        delta = QtCore.QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def ban_user(self) -> None:
        if not (self.tree.selectedItems()):
            return

        if self.server_id == 0:
            # Если у выбранного элемента есть только один родитель (выбран пользователь)
            if (self.tree.selectedItems()[0].parent()) and (not(self.tree.selectedItems()[0].parent().parent())):
                response = requests.get(self.__url + "/ban_user", json={
                    "username": self.tree.selectedItems()[0].text(0),
                    "server_name": self.tree.selectedItems()[0].parent().text(0)
                })


                if "someProblems" in response.json():
                    return show_error("Возникли неполадки с сервером")

                banned = "разбанен" if self.tree.selectedItems()[0].child(0).text(0).split("Статус: ")[1] \
                    == "Banned" else "забанен"
                show_message(self.tree.selectedItems()[0].text(0) + " был " + banned)
                self.tree.clear()
                return self.insert_users()

        else:
            if not (self.tree.selectedItems()[0].parent()):
                response = requests.get(self.__url + "/ban_user", json={
                    "username": self.tree.selectedItems()[0].text(0),
                    "server_id": self.server_id
                })
                if "someProblems" in response.json():
                    return show_error("Возникли неполадки с севрером")

                banned = "разбанен" if self.tree.selectedItems()[0].child(0).text(0).split("Статус: ")[1] \
                    == "Banned" else "забанен"

                show_message(self.tree.selectedItems()[0].text(0) + " был " + banned)
                self.tree.clear()
                self.insertUsers()
    
    def create_user(self) -> None:
        self.main = userCreatorForm(
            server_id=self.server_id, 
            is_creator=self.is_creator, 
            url=self.__url)
        self.main.show()
        self.tree.clear()
        return self.insert_users()


class userCreatorForm(QtWidgets.QMainWindow, userCreatorUI.Ui_MainWindow):
    def __init__(self, server_id: int, is_creator: bool, url:str=URL) -> None:
        super().__init__()
        self.setupUi(self)

        self.server_id = server_id
        self.__url = url

        # Если пользователь не создатель или находится на каком-то сервере => скрываем перечень серверов
        if (not is_creator) or (is_creator and self.server_id):
            self.label_2.hide()
            self.availableServers.hide()

        else:
            response = requests.get(self.__url + "/get_servers")
            servers = response.json()["servers"]

            if response.status_code == 200:
                if "someProblems" in response.json():
                    return show_error("Беды")
                for server_info in servers:
                    self.availableServers.addItem(str(server_info[0]))
            else:
                return show_error("Возникли неполадки при подключении к серверу")

        # События для кнопок
        self.createButton.pressed.connect(self.create_user)
        self.exitButton.pressed.connect(self.close)

        # Иконки
        self.exitButton.setIcon(QtGui.QIcon(":/resources/Images/cross.png"))

        # Прозрачное окно без рамок
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        delta = QtCore.QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def create_user(self) -> None:
        if self.availableServers.isVisible():
            self.server_id = int(self.availableServers.current_text())

        response = requests.get(self.__url + "/create_user", json={
            "username": self.usernameText.text(),
            "password": self.passwordText.text(),
            "server_id": self.server_id,
        })

        if "isNotFilled" in response.json():
            return show_error("Не все поля заполнены")

        if "nameIsTaken" in response.json():
            return show_error("Данное имя пользователя занято")

        if "badPassword" in response.json():
            return show_error("Пароль должен иметь специальные символы, буквы и цифры. Длина пароля от 8 до 16")

        show_message("Пользователь был создан")
        return self.close()


class searchForm(QtWidgets.QMainWindow, searchFormUI.Ui_MainWindow):
    closeDialog = pyqtSignal()
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        
        self.oldPos = self.pos()
        self.checkBox.setChecked(True)

        self.text = ""

        self.searchButton.pressed.connect(self.set_text)
        self.cancelButton.pressed.connect(self.close)
        self.exitButton.pressed.connect(self.close)

        self.exitButton.setIcon(QtGui.QIcon(":/resources/Images/cross.png"))

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def set_text(self) -> None:
        self.text = self.textEdit.toPlainText()
        self.closeDialog.emit()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()


class DownloadHub(QtWidgets.QMainWindow, downloadUI.Ui_Form):
    def __init__(self, path:str, items: list) -> None:
        super().__init__()
        self.setupUi(self)
        self.items = items
        self.is_cancelled = False
        self.path = path

        self.browser = QtWidgets.QTextBrowser()
        self.listWidget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.exitButton.pressed.connect(self.close)

        self.oldPos = 0.0

        self.selectButton.pressed.connect(self.view)

        self.exitButton.setIcon(QtGui.QIcon(":/resources/Images/cross.png"))

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        for i in items:
            self.listWidget.addItem(i)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def generate_hash(self, word:str) -> str:
        odd_salt = str(hashlib.md5(word[::2].encode()).hexdigest())
        even_salt = str(hashlib.md5(word[::-2][::-1].encode()).hexdigest())
        return hashlib.md5(word.encode()).hexdigest() + odd_salt + even_salt

    def view(self) -> None:
        needed_files = list()
        self.downloaded_files = dict()

        for item in self.listWidget.selectedItems():
            needed_files.append(item.text())

        for needed_file in needed_files:
            if needed_file.split(".")[-1] in ["docx", "doc", "pptx", "xlsx", "xls"]:
                self.dial = QDialog(self)
                label = QLabel(
                    text=f"{needed_file}")
                
                    
                dload = QPushButton(text="Скачать")
                view = QPushButton(text="Просмотреть")

                dload.pressed.connect(lambda: self.download(file, resp.content))
                url = f"https://docs.google.com/gview?url=http://mezano.pythonanywhere.com/open?link={self.generate_hash(needed_file)}:{self.path}"
                view.pressed.connect(lambda: webbrowser.open(url))

                self.dial.setLayout(QVBoxLayout())
                self.dial.layout().addWidget(label)
                self.dial.layout().addWidget(dload)
                self.dial.layout().addWidget(view)
                self.dial.setFixedSize(310, 150)
                self.dial.exec_()
            else:
                resp = requests.get(URL + "/download", json={
                    "neededFile": needed_file
                })

                files_list = [f for _, _, f in os.walk(os.getcwd() + "/Загрузки")][0]

                is_found = False

                for file in files_list:
                    if needed_file == file:
                        is_found = True

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

                if not is_found:
                    self.downloaded_files[needed_file] = resp.content
            
        if self.downloaded_files:
            info = ""
            
            for file_name in self.downloaded_files.keys():
                with open("Загрузки/" + str(file_name), "wb") as file:
                    file.write(self.downloaded_files[file_name])
                    info = info + str(file_name) + ", "

            # [:-2] - без расширения
            show_message(f"Файлы {info[:-2]} были успешно скачаны")

    def accept(self, file_name: str, file_content: bytes) -> None:
        self.dial.close()
        self.downloaded_files[file_name] = file_content


class privateChat(QtWidgets.QMainWindow, SecondaryUI.Ui_MainWindow):
    def __init__(self, username: str, server_name: str, chat_id: int, url:str=URL) -> None:
        super().__init__()
        self.setupUi(self)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.__url = url
        self.chat_id = chat_id
        self.username = username
        self.server_name = server_name

        self.timestamp = 0.0
        self.is_search_enabled = False
        self.previous_messages = list()
        self.__key = KEY

        self.exitButton.setIcon(QtGui.QIcon(":/resources/Images/cross.png"))
        self.backButton.setIcon(QtGui.QIcon(":/resources/Images/left.png"))
        self.forwardButton.setIcon(QtGui.QIcon(":/resources/Images/right.png"))
        self.sendButton.setIcon(QtGui.QIcon(":/resources/Images/send.png"))

        self.searchButton.pressed.connect(self.search)
        self.backButton.pressed.connect(self.backward)
        self.forwardButton.pressed.connect(self.forward)
        self.exitButton.pressed.connect(self.close)
        self.sendButton.pressed.connect(self.send_private_message)
        self.downloadButton.pressed.connect(self.download)
        self.uploadButton.pressed.connect(self.upload)
        self.abortSearchButton.pressed.connect(self.abort_search)

        self.serverNameLabel.setText(self.server_name)

        self.backButton.hide()
        self.forwardButton.hide()
        self.messagesAmount.hide()
        self.abortSearchButton.hide()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)

        self.oldPos = self.pos()

    def check_for_boundaries(self) -> None:
        # Левая граница
        if self.current_line + 1 == self.matches:
            self.forwardButton.hide()
            if self.current_line - 1 >= 0:
                self.backButton.show()
            return 1
        elif self.forwardButton.isHidden():
            self.forwardButton.show()

        # Правая граница
        if self.current_line - 1 < 0:
            self.backButton.hide()
            if self.current_line + 1 != self.matches:
                self.forwardButton.show()
            return -1
        elif self.backButton.isHidden():
            self.backButton.show()

        return 0

    def refill_search_browser(self):
        self.textBrowser.clear()

        self.shifts = list()

        is_new_date = 0
        current_shift = 3
        self.previous_message_date = 0
        for searched_message in self.result:

            if "isNotForSearch" in searched_message:
                current_shift += int(self.time_management(searched_message["timestamp"]))
            else:
                is_new_date = self.time_management(searched_message["timestamp"])

            if (searched_message['username'] == self.username):
                self.textBrowser.setAlignment(QtCore.Qt.AlignRight)

            else:
                self.textBrowser.setAlignment(QtCore.Qt.AlignLeft)

            if "isNotForSearch" not in searched_message:
                if is_new_date:
                    current_shift += 2 
                    self.shifts.append(current_shift)
                else:
                    self.shifts.append(current_shift)

            self.textBrowser.append(searched_message["message"])
            self.textBrowser.append("")

    ### FORMATTING TEXT FOR SEARCH ###
    
    def remove_empty_characters_from_text(self, text_to_manage: str) -> str:
        for _ in text_to_manage:
            text_to_manage = text_to_manage.replace("\n", "").replace(" ", "")
        
        return " ".join(text_to_manage.split())

    def remove_underline_from_text(self, text_to_deunderline: str) -> bool:
        # В консоле есть символ, который отображается как ?
        # Поэтому я знаю только его битовое представление
        byte = b'\xe2\x80\xa8'
        for msg in self.result:
            for ch in text_to_deunderline:
                    if ch.encode() == byte:
                        text_to_deunderline = text_to_deunderline.replace(ch, "")

            # Создаём временную переменную чтобы сравнить её с тем, что было передано в качестве аргумента
            tmp = self.remove_empty_characters_from_text(cleanhtml(msg["message"]))
            text_to_deunderline = self.remove_empty_characters_from_text(text_to_deunderline)

            # Убираем жирный текст у выделенного текста
            if tmp == text_to_deunderline:
                    msg["message"] = msg["message"].replace("<strong>", "").replace("</strong>", "")
                    return True

    def underline_text(self, text_to_underline: str) -> bool:
        # Известное толькое битовое представление символа
        byte = b'\xe2\x80\xa8'
        for msg in self.result:
            for ch in text_to_underline: 
                if ch.encode() == byte:
                    text_to_underline = text_to_underline.replace(ch, "")

            tmp = self.remove_empty_characters_from_text(cleanhtml(msg["message"]))
            text_to_underline = self.remove_empty_characters_from_text(text_to_underline)

            if tmp == text_to_underline:
                msg["message"] = msg["message"][:msg["message"].index("<br>") + 4] + "<strong>" + msg["message"][msg["message"].index("<br>") + 4:] + "</strong>"
                return True

    ###################################

    def backward(self) -> None:
        self.current_line -= 1
        self.messagesAmount.setText(str(self.current_line + 1) + "/" + str(self.matches))

        previous_text = self.textBrowser.document().findBlockByLineNumber(self.msg_lines[self.current_line + 1] * 2 + self.shifts[self.current_line + 1]).text()
        current_text = self.textBrowser.document().findBlockByLineNumber(self.msg_lines[self.current_line] * 2 + self.shifts[self.current_line]).text()

        self.underline_text(current_text)
        self.remove_underline_from_text(previous_text)

        self.refill_search_browser()

        current_text = self.textBrowser.document().findBlockByLineNumber(self.msg_lines[self.current_line] * 2 + self.shifts[self.current_line])
        cursor = QtGui.QTextCursor(current_text)
        self.textBrowser.setTextCursor(cursor)

        self.check_for_boundaries()

    def forward(self) -> None:
        self.current_line += 1
        self.messagesAmount.setText(str(self.current_line + 1) + "/" + str(self.matches))

        previous_text = self.textBrowser.document().findBlockByLineNumber(self.msg_lines[self.current_line - 1] * 2 + self.shifts[self.current_line - 1]).text()
        current_text = self.textBrowser.document().findBlockByLineNumber(self.msg_lines[self.current_line] * 2 + self.shifts[self.current_line]).text()

        self.underline_text(current_text)
        self.remove_underline_from_text(previous_text)

        self.refill_search_browser()

        current_text = self.textBrowser.document().findBlockByLineNumber(self.msg_lines[self.current_line] * 2 + self.shifts[self.current_line])
        cursor = QtGui.QTextCursor(current_text)
        self.textBrowser.setTextCursor(cursor)

        self.check_for_boundaries()

    def send_private_message(self) -> None:
        text = remove_spaces(self.textEdit.toPlainText())
        if len(text) > MAX_MESSAGE_LEN:
            return show_error("Длина сообщения должна быть не более 100")
        
        else:
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
                    return show_error("Сообщение не может быть пустым")
                
                if "someProblems" in response.json():
                    return show_error("Возникли неполадки с сервером")
                
                return self.textEdit.setText("")
            else:
                self.timer.stop()
                show_error("Ошибка в подключении к серверу")
                return self.close()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        delta = QtCore.QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()
 
    def time_management(self, message_date: datetime) -> int:
        if not self.previous_message_date:
            self.previous_message_date = message_date
            self.textBrowser.setAlignment(QtCore.Qt.AlignCenter)
            self.textBrowser.append("<b>Начало переписки</b>")
            self.textBrowser.append("<b>" + message_date.strftime("%d/%m/%Y") + "</b>")
            self.textBrowser.append("")
            return 0
                    
        elif self.previous_message_date.year < message_date.year:
            self.previous_message_date = message_date
            self.textBrowser.setAlignment(QtCore.Qt.AlignCenter)
            self.textBrowser.append("<b>" + message_date.strftime("%d/%m/%Y") + "</b>")
            self.textBrowser.append("")
            return 2

        elif self.previous_message_date.month < message_date.month:
            self.previous_message_date = message_date
            self.textBrowser.setAlignment(QtCore.Qt.AlignCenter)
            self.textBrowser.append("<b>" + message_date.strftime("%d/%m/%Y") + "</b>")
            self.textBrowser.append("")
            return 2
        
        elif self.previous_message_date.month == message_date.month and self.previous_message_date.day < message_date.day:
            self.previous_message_date = message_date
            self.textBrowser.setAlignment(QtCore.Qt.AlignCenter)
            self.textBrowser.append("<b>" + message_date.strftime("%d/%m/%Y") + "</b>")
            self.textBrowser.append("")
            return 2

        return 0


    def update_private_messages(self, rs) -> None:
        self.previous_message_date = 0
        try:
            rs.status_code
        except AttributeError:
            return self.close()
    
        if rs.status_code == 200:
            is_online = rs.json()["isOnline"]
            self.serverNameLabel.setText(self.server_name + ("(online)" if is_online else "(offline)"))
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

                    message_date = datetime.datetime.fromtimestamp(
                        message[2])
                    
                    self.time_management(message_date)

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
            show_error(
                "При попытке подключиться к серверу возникли ошибки")
            return self.close()

    def search(self) -> None:
        self.sForm = searchForm()
        self.sForm.show()
        
        self.sForm.closeDialog.connect(lambda: self.find(self.sForm.text, self.sForm.checkBox.isChecked(), self.sForm.checkBox_2.isChecked()))

    def find(self, text: str, name_is_checked: bool, msg_is_checked: bool) -> None:
        self.word = remove_spaces(text)
        self.result = []

        if self.word:
            response = requests.get(
                self.__url + '/get_private_messages',
                params={
                    'after': 0.0,
                    'chat_id': self.chat_id
                })

            if response.status_code == 200:
                self.matches = 0
                self.msg_lines = list()
                self.total_lines = 0

                if not name_is_checked and not msg_is_checked:
                    return show_error("Выберите критерии поиска")

                messages = response.json()['messages']
                self.messages = messages
                
                for message in messages:

                    dt = datetime.datetime.fromtimestamp(
                            message[2]).strftime('%H:%M')

                    if self.word.lower() in message[0].lower() and name_is_checked:
                        self.dict = {"username": message[0], 
                                    "message": ("<b>" + dt + " " + beautify_text(message[0], self.word) + "</b>:<br>" + decrypt(message[1], self.__key) + ""),
                                    "timestamp": datetime.datetime.fromtimestamp(message[2])}
                        self.result.append(self.dict)
                        self.msg_lines.append(self.total_lines)

                        self.matches += 1

                    elif self.word.lower() in decrypt(message[1], self.__key).lower() and msg_is_checked:
                        self.dict = {"username": message[0], 
                                    "message": ("<b>" + dt + " " +
                                                message[0] + "</b>:<br>" + beautify_text(decrypt(message[1], self.__key), self.word) + ""),
                                    "timestamp": datetime.datetime.fromtimestamp(message[2])}

                        self.result.append(self.dict)
                        self.msg_lines.append(self.total_lines)

                        self.matches += 1

                    else:
                        self.dict = {"username": message[0], 
                                    "message": ("<b>" + dt + " " +
                                                message[0] + "</b>:<br>" + decrypt(message[1], self.__key) + ""),
                                    "timestamp": datetime.datetime.fromtimestamp(message[2]),
                                    "isNotForSearch": True
                                    }
                        self.result.append(self.dict)

                    self.total_lines += 1

                    if not self.is_search_enabled:
                        self.dict = {"username": message[0], 
                                    "message": ("<b>" + dt + " " +
                                                message[0] + "</b>:<br>" + decrypt(message[1], self.__key) + ""),
                                    "timestamp": datetime.datetime.fromtimestamp(message[2])}
                        self.previousMessages.append(self.dict)

                if (self.matches):
                    self.sForm.close()
                    self.textBrowser.clear()
                    self.shifts = list()

                    current_shift = 3

                    self.is_search_enabled = True
                    self.abortSearchButton.show()
                    self.previous_message_date = 0
                    for searched_message in self.result:
                        if "isNotForSearch" in searched_message:
                            current_shift += int(self.time_management(searched_message["timestamp"]))
                        else:
                            is_new_date = self.time_management(searched_message["timestamp"])

                        if (searched_message['username'] == self.username):
                            self.textBrowser.setAlignment(QtCore.Qt.AlignRight)
                        else:
                            self.textBrowser.setAlignment(QtCore.Qt.AlignLeft)

                        self.textBrowser.append(searched_message["message"])
                        self.textBrowser.append("")

                        if "isNotForSearch" not in searched_message:
                            if is_new_date:
                                current_shift += 2 
                                self.shifts.append(current_shift)
                            else:
                                self.shifts.append(current_shift)

                    
                    self.underline_text(self.textBrowser.document().findBlockByLineNumber(self.msg_lines[0] * 2 + self.shifts[0]).text())
                    self.refill_search_browser()

                    current_text = self.textBrowser.document().findBlockByLineNumber(self.msg_lines[0] * 2 - 1 + self.shifts[0])
                    cursor = QtGui.QTextCursor(current_text)
                    self.textBrowser.setTextCursor(cursor)

                    self.forwardButton.show()
                    self.messagesAmount.show()
                    self.searchButton.hide()

                    self.messagesAmount.setText("1/" + str(self.matches))

                    self.current_line = 0

                    self.check_for_boundaries()

                else:
                    self.result = []
                    return show_message("Ваш запрос не выдал результатов(")
        else:
            return show_error("Поле поиска не может быть пустым")

    def abort_search(self) -> None:
        self.previous_message_date = 0

        if self.is_search_enabled:
            self.textBrowser.clear()
            for msg in self.previous_messages:
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

            self.is_search_enabled = False

    def download(self) -> None:
        resp = requests.get(self.__url + "/get_files", json={
            "chat_id": self.chat_id
        })  

        if resp.status_code == 200:
            if "someProblems" in resp.json():
                return show_error("Возникли неполадки с сервером")

            all_files = resp.json()['allFiles']
            self.main = DownloadHub(self.server_name, all_files)
            return self.main.show()
        else:
            return show_error("Возникли неполадки при подключении")

    def upload(self) -> None:
        frame = QtWidgets.QFileDialog()
        frame.setFileMode(QtWidgets.QFileDialog.AnyFile)
        if frame.exec_():
            file_names = frame.selectedFiles()
            file_name, ok_is_pressed = QInputDialog.getText(
                self, "Название файла", "Введите новое название файла: ", QLineEdit.Normal, "")
            if ok_is_pressed:
                if file_name == "":
                    file_name = file_names[0].split("/")[-1]

                else:
                    file_name = file_name + "." + file_names[0].split("/")[-1].split('.')[1]

                with open(file_names[0], "rb") as file:
                    upl = requests.get(self.__url + "/upload", data=file.read(), params={
                        "filename": file_name,
                        "chat_id": self.chat_id
                    })

                if "nameIstaken" in upl.json():
                    return show_error("Данное имя файла заянято")

    def update(self) -> None:
        self.msg_thread = LoadMessagesThread(
            url=self.__url + "/get_private_messages", 
            ts=self.timestamp, 
            serv_id=self.chat_id, 
            PM=True,
            companion=self.server_name)
        self.msg_thread.load_finished.connect(self.update_private_messages)
        self.msg_thread.finished.connect(self.msg_thread.deleteLater)
        self.msg_thread.start()


class serverLogin(QtWidgets.QMainWindow, serverLoginUI.Ui_MainWindow):
    login_succeeded = pyqtSignal()
    def __init__(self, username:str, server_id:int, name:str, users_amount:int, url:str=URL) -> None:
        super().__init__()
        self.setupUi(self)

        self.username = username
        self.server_id = server_id
        self.__url = url

        self.serverName.setText(name)
        self.usersAmount.setText(self.usersAmount.text() + str(users_amount))

        self.loginButton.pressed.connect(self.login)
        self.exitButton.pressed.connect(self.close)

        self.exitButton.setIcon(QtGui.QIcon(":/resources/Images/cross.png"))

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.oldPos = self.pos()

    
    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def login(self) -> None:
        response = requests.get(self.__url + "/connect",
                                    json={
                                        'server_id': self.server_id,
                                        'username': self.username,
                                        'password': hashlib.md5(self.passwordInput.text().encode()).hexdigest()
                                    })

        if response.status_code == 200:
            if "badPassword" in response.json():
                return show_error("Неверный пароль")

            if "isBanned" in response.json():
                return show_error("Вы были забанены на этом сервере")

            if "someProblems" in response.json():
                return show_error("Возникли неполадки с сервером")

            self.login_succeeded.emit()
            return self.close()


class serverLoginWithoutPassword(QtWidgets.QMainWindow, serverLoginWithoutPasswordUI.Ui_MainWindow):
    login_succeeded = pyqtSignal()
    def __init__(self, username:str, server_id:int, name:str, users_amount:int, url:str=URL) -> None:
        super().__init__()
        self.setupUi(self)

        self.username = username
        self.server_id = server_id
        self.__url = url

        self.serverName.setText(name)
        self.usersAmount.setText(self.usersAmount.text() + str(users_amount))

        self.loginButton.pressed.connect(self.login)
        self.exitButton.pressed.connect(self.close)

        self.exitButton.setIcon(QtGui.QIcon(":/resources/Images/cross.png"))

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.oldPos = self.pos()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def login(self) -> None:
        response = requests.get(self.__url + "/connect",
                                    json={
                                        'server_id': self.server_id,
                                        'username': self.username,
                                        'password': hashlib.md5("".encode()).hexdigest()
                                    })

        if response.status_code == 200:
            if "badPassword" in response.json():
                return show_error("Неверный пароль")

            if "isBanned" in response.json():
                return show_error("Вы были забанены на этом сервере")

            if "someProblems" in response.json():
                return show_error("Возникли неполадки с сервером")

            self.login_succeeded.emit()
            return self.close()


class createServerForm(QtWidgets.QMainWindow, createServerFormUI.Ui_MainWindow):
    def __init__(self, username:str) -> None:
        super().__init__()

        self.setupUi(self)

        self.username = username
        self.oldPos = 0

        self.exitButton.setIcon(QtGui.QIcon(":resources/Images/cross.png"))

        self.exitButton.pressed.connect(self.close)
        self.createServerButton.pressed.connect(self.create)
        self.hasPasswordCheckBox.pressed.connect(self.show_hide_passwordInput)

        self.passwordInput.hide()

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.oldPos = self.pos()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def show_hide_passwordInput(self):
        if not self.hasPasswordCheckBox.isChecked():
            self.passwordInput.show()
        else:
            self.passwordInput.hide()

    def create(self):
        server_name = self.serverNameInput.text()
        server_password = self.passwordInput.text()

        if server_name != "":

            res = requests.get(self.__url + "/create_server", json={
                "serverName": server_name,
                "serverPassword": server_password,
                "username": self.username
            })

            if "someProblems" in res.json():
                return show_error("Беды")

            if "nameIsTaken" in res.json():
                return show_error("Данное имя сервера занято")

            self.main = Chat(username=self.username, url=self.__url,
                            server_id=res.json()['server_id'])
        else:
            show_error("Название сервера не может быть пустым")
        

if __name__ == "__main__":
    try:
        with open("url.txt", "r") as file:
            URL = file.read()
    except:
        pass
    app = QtWidgets.QApplication([])


    window = Auth(URL)
    window.setFixedSize(sizes["Chat"]["WIDTH"], sizes["Chat"]["HEIGHT"])
    window.show()
    app.exec_()
