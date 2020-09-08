from PyQt5 import QtWidgets
import AuthUI
import requests
from PyQt5.QtWidgets import QMessageBox
from Chat import Chat
import hashlib


class Auth(QtWidgets.QMainWindow, AuthUI.Ui_MainWindow):
    def __init__(self, url):
        super().__init__()
        self.setupUi(self) # Инициализация UI
        self.url = url # Создаём переменную, которая ссылается на адрес сервера
        self.pushButton.pressed.connect(self.login) # Связываем событие нажатия на первую кнопку с функцией входа
        self.pushButton_2.pressed.connect(self.registration) # Связываем событие нажатия на первую кнопку с функцией регистрации

    def removeSpaces(self, string):
        '''
        Удаляет все пустые символы в строке
        '''
        for n in string:
            string = string.lstrip('')
            string = string.rstrip('')
            string = string.lstrip('\n')
            string = string.rstrip('\n')
        return string

    def showError(self, text):
        '''
        Создаёт окно с ошибкой и выводим текст
        '''
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(text)
        msg.setWindowTitle("Error")
        msg.exec_()

    def login(self):
        ### Извлекаем имя пользователя и пароль из текстовых полей ###
        self.username = self.removeSpaces(self.lineEdit.text())
        self.password = self.removeSpaces(self.lineEdit_2.text())
        response = requests.get(self.url + '/login', # Передаём логин и пароль на сервер
                                json={
                                    'username': self.username,
                                    'password': hashlib.md5(self.password.encode()).hexdigest(), })

        if response.status_code == 200:
            ###Обработка ошибки пустых полей###
            try:
                if response.json()['isNotFilled']:
                    return self.showError("Не все поля заполнены")
            except:
                pass

            ###Обработка ошибки неверного пароля###
            try:
                if response.json()['invalidPassword']:
                    return self.showError("Неверный пароль")
            except:
                pass

            ###Обработка ошибки неверного юзернейма###
            try:
                if response.json()['invalidUsername']:
                    return self.showError("Неверное имя пользователя")
            except:
                pass

            self.close()
            self.main = Chat(self.username, self.password)
            return self.main.show()

        else:
            self.showError("Ошибка в подключении к серверу")
            return self.close()

    def registration(self):
        self.username = self.lineEdit.text()
        self.password = self.lineEdit_2.text()

        response = requests.get(self.url + '/reg',
                                    json={
                                        'username': self.username,
                                        'password': hashlib.md5(self.password.encode()).hexdigest() })
        if response.status_code == 200:
            ###Обработка ошибки пустых полей###
            try:
                if response.json()['isNotFilled']:
                    return self.showError("Не все поля заполнены")
            except:
                pass

            ###Обработка ошибки занятого юзернейма###
            try:
                if response.json()['nameIsTaken']:
                    return self.showError("Данное имя пользователя уже занято")
            except:
                pass
            
            self.close() # Закрываем текущее окно
            self.main = Chat(self.username, self.password) # Инициализируем новое окно, передавая логин и пароль
            self.main.show() # Открываем инициализированное окно
            
        else:
            self.showError("При попытке подключиться к серверу возникла ошибка")
            return self.close()

### Ищем файл с урлом нашего сайта, если такого нет, то обращаемся к локалхосту ###
try:
    file = open('url.txt')
    url = file.readline()
    app = QtWidgets.QApplication([])
    window = Auth(url)
    window.show()
    app.exec_()
except FileNotFoundError:
    app = QtWidgets.QApplication([])
    window = Auth('http://127.0.0.1:5000')
    window.show()
    app.exec_()
