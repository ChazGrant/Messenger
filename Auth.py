from PyQt5 import QtWidgets
import AuthUI
import requests
from PyQt5.QtWidgets import QMessageBox
from Chat import Chat
import hashlib


class Auth(QtWidgets.QMainWindow, AuthUI.Ui_MainWindow):
    def __init__(self, url='http://127.0.0.1:5000'):
        super().__init__()
        self.setupUi(self) # Инициализация UI
        self.__url = url # Создаём переменную, которая ссылается на адрес сервера
        self.pushButton.pressed.connect(self.login) # Связываем событие нажатия на первую кнопку с функцией входа
        self.pushButton_2.pressed.connect(self.registration) # Связываем событие нажатия на первую кнопку с функцией регистрации

    def removeSpaces(self, string):
        '''
        Удаляет все пустые символы в строке
        '''
        for n in string:
            string = string.lstrip(' ')
            string = string.rstrip(' ')
            string = string.lstrip('\n')
            string = string.rstrip('\n')
            string = string.rstrip('\t')
            string = string.rstrip('\t')
        return string

    def clearSpaces(self, string):
        string = string.replace(' ', '')
        string = string.replace('\n', '')
        string = string.replace('\t', '')
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
        self._username = self.clearSpaces(self.lineEdit.text())
        self.__password = self.removeSpaces(self.lineEdit_2.text())
        response = requests.get(self.__url + '/login', # Передаём логин и пароль на сервер
                                json={
                                    'username': self._username,
                                    'password': hashlib.md5(self.__password.encode()).hexdigest()
                                })

        if response.status_code == 200:
            ### Обработка ошибки пустых полей ###
            if "isNotFilled" in response.json():
                return self.showError("Не все поля заполнены")

            ### Обработка ошибки неверного пароля ###
            if "invalidData" in response.json():
                    return self.showError("Неверное имя пользователя и/или пароль")

            self.close()
            self.main = Chat(self._username, self.__password, self.__url)
            return self.main.show()

        else:
            self.showError("Ошибка в подключении к серверу")
            return self.close()

    def registration(self):
        self._username = " ".join(self.lineEdit.text().split())
        self.__password = self.lineEdit_2.text()
        response = requests.get(self.__url + '/reg',
                                    json={
                                        'username': self._username,
                                        'password': hashlib.md5(self.__password.encode()).hexdigest() })
        if response.status_code == 200:
           
            if "isNotFilled" in response.json():
                    return self.showError("Не все поля заполнены")

            if "nameIsTaken" in response.json():
                    return self.showError("Данное имя пользователя уже занято")
        
            self.close() # Закрываем текущее окно
            self.main = Chat(self._username, self.__password, self.__url) # Инициализируем новое окно, передавая логин и пароль
            return self.main.show() # Открываем инициализированное окно
            
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
    window = Auth()
    window.show()
    app.exec_()