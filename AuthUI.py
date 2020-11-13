# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'beautyAuth.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(524, 515)
        MainWindow.setStyleSheet("*{\n"
"    font-family: century gothic;\n"
"    font-size: 20px;\n"
"}\n"
"#exitButton{\n"
"    /*background-color: red;*/\n"
"    border-radius: 15px;\n"
"    background-size: 5px;\n"
"}\n"
"QMainWindow{\n"
"    background-color: transparent;\n"
"}\n"
"#passwordText{\n"
"    type: password;\n"
"}\n"
"QFrame{\n"
"    background: #333;\n"
"    border-radius: 15px;\n"
"}\n"
"QPushButton{\n"
"    border-radius: 15px;\n"
"    background: red;\n"
"    color: white;\n"
"}\n"
"QPushButton:hover{\n"
"    background: #333;\n"
"    color: red;\n"
"}\n"
"#toolButton{\n"
"    border-radius: 60px;\n"
"    background: red;\n"
"}\n"
"QLabel{\n"
"    color: white;\n"
"}\n"
"QLineEdit{\n"
"    padding-bottom: 5px;\n"
"    background: transparent;\n"
"    border: none;\n"
"    color: #717072;\n"
"    border-bottom: 1px solid #717072;\n"
"}")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(40, 100, 441, 341))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(150, 50, 151, 51))
        self.label.setObjectName("label")
        self.loginButton = QtWidgets.QPushButton(self.frame)
        self.loginButton.setGeometry(QtCore.QRect(20, 220, 401, 41))
        self.loginButton.setObjectName("loginButton")
        self.registrateButton = QtWidgets.QPushButton(self.frame)
        self.registrateButton.setGeometry(QtCore.QRect(20, 280, 401, 41))
        self.registrateButton.setObjectName("registrateButton")
        self.usernameText = QtWidgets.QLineEdit(self.frame)
        self.usernameText.setGeometry(QtCore.QRect(40, 131, 371, 31))
        self.usernameText.setText("")
        self.usernameText.setObjectName("usernameText")
        self.passwordText = QtWidgets.QLineEdit(self.frame)
        self.passwordText.setGeometry(QtCore.QRect(40, 171, 371, 31))
        self.passwordText.setInputMask("")
        self.passwordText.setText("")
        self.passwordText.setEchoMode(QtWidgets.QLineEdit.Password)
        self.passwordText.setObjectName("passwordText")
        self.exitButton = QtWidgets.QToolButton(self.frame)
        self.exitButton.setGeometry(QtCore.QRect(390, 20, 41, 31))
        self.exitButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("cross.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.exitButton.setIcon(icon)
        self.exitButton.setShortcut("")
        self.exitButton.setAutoRepeatDelay(300)
        self.exitButton.setObjectName("exitButton")
        self.toolButton = QtWidgets.QToolButton(self.centralwidget)
        self.toolButton.setGeometry(QtCore.QRect(200, 20, 121, 121))
        self.toolButton.setText("")
        self.toolButton.setObjectName("toolButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 524, 29))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Вход в аккаунт"))
        self.loginButton.setText(_translate("MainWindow", "Войти"))
        self.registrateButton.setText(_translate("MainWindow", "Регистрация"))
        self.usernameText.setPlaceholderText(_translate("MainWindow", "Имя пользователя"))
        self.passwordText.setPlaceholderText(_translate("MainWindow", "Пароль"))
