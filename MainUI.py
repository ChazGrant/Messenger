# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Main.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1299, 700)
        MainWindow.setStyleSheet("*{\n"
"    font-family: century gothic;\n"
"    font-size: 20px;\n"
"}\n"
"QMainWindow{\n"
"    background-color: transparent;\n"
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
"#textBrowser{\n"
"    font-size: 16px;\n"
"}\n"
"#toolButton{\n"
"    border-radius: 60px;\n"
"    background: red;\n"
"}\n"
"QLabel{\n"
"    color: white;\n"
"}\n"
"QFrame{\n"
"    background: #333;\n"
"    border-radius: 15px;\n"
"}\n"
"QLineEdit{\n"
"    padding-bottom: 5px;\n"
"    background: transparent;\n"
"    border: none;\n"
"    color: #717072;\n"
"    border-bottom: 1px solid #717072;\n"
"}\n"
"#exitButton{\n"
"    /*background-color: red;*/\n"
"    border-radius: 15px;\n"
"    background-size: 5px;\n"
"}\n"
"#searchButton{\n"
"    border-radius: 15px;\n"
"    background-size: 5px;\n"
"}\n"
"#searchButton_2{\n"
"    border-radius: 15px;\n"
"    background-size: 5px;\n"
"}")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(80, 30, 1171, 591))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setGeometry(QtCore.QRect(900, 0, 231, 71))
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.textBrowser = QtWidgets.QTextBrowser(self.frame)
        self.textBrowser.setGeometry(QtCore.QRect(20, 70, 851, 371))
        self.textBrowser.setStyleSheet("background-color: lightgrey;")
        self.textBrowser.setObjectName("textBrowser")
        self.sendButton = QtWidgets.QPushButton(self.frame)
        self.sendButton.setGeometry(QtCore.QRect(580, 460, 121, 51))
        self.sendButton.setObjectName("sendButton")
        self.textEdit = QtWidgets.QTextEdit(self.frame)
        self.textEdit.setGeometry(QtCore.QRect(20, 460, 551, 111))
        self.textEdit.setStyleSheet("background-color: lightgrey;")
        self.textEdit.setObjectName("textEdit")
        self.serverNameLabel = QtWidgets.QLabel(self.frame)
        self.serverNameLabel.setGeometry(QtCore.QRect(30, 10, 401, 51))
        self.serverNameLabel.setText("")
        self.serverNameLabel.setWordWrap(True)
        self.serverNameLabel.setObjectName("serverNameLabel")
        self.exitAccountButton = QtWidgets.QPushButton(self.frame)
        self.exitAccountButton.setGeometry(QtCore.QRect(960, 460, 191, 51))
        self.exitAccountButton.setObjectName("exitAccountButton")
        self.disconnectButton = QtWidgets.QPushButton(self.frame)
        self.disconnectButton.setGeometry(QtCore.QRect(960, 520, 191, 51))
        self.disconnectButton.setObjectName("disconnectButton")
        self.clearMessageButton = QtWidgets.QPushButton(self.frame)
        self.clearMessageButton.setGeometry(QtCore.QRect(580, 520, 121, 51))
        self.clearMessageButton.setObjectName("clearMessageButton")
        self.scrollArea = QtWidgets.QScrollArea(self.frame)
        self.scrollArea.setGeometry(QtCore.QRect(900, 70, 251, 301))
        self.scrollArea.setAutoFillBackground(False)
        self.scrollArea.setStyleSheet("background-color: lightgrey;")
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 251, 301))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.exitButton = QtWidgets.QToolButton(self.frame)
        self.exitButton.setGeometry(QtCore.QRect(1120, 10, 41, 31))
        self.exitButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("cross.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.exitButton.setIcon(icon)
        self.exitButton.setShortcut("")
        self.exitButton.setAutoRepeatDelay(300)
        self.exitButton.setObjectName("exitButton")
        self.searchButton = QtWidgets.QPushButton(self.frame)
        self.searchButton.setGeometry(QtCore.QRect(660, 10, 201, 51))
        self.searchButton.setObjectName("searchButton")
        self.abortSearchButton = QtWidgets.QPushButton(self.frame)
        self.abortSearchButton.setGeometry(QtCore.QRect(450, 10, 201, 51))
        self.abortSearchButton.setObjectName("abortSearchButton")
        self.isOnline = QtWidgets.QRadioButton(self.frame)
        self.isOnline.setGeometry(QtCore.QRect(900, 390, 111, 31))
        self.isOnline.setChecked(True)
        self.isOnline.setObjectName("isOnline")
        self.isOffline = QtWidgets.QRadioButton(self.frame)
        self.isOffline.setGeometry(QtCore.QRect(1010, 390, 151, 31))
        self.isOffline.setObjectName("isOffline")
        self.uploadButton = QtWidgets.QPushButton(self.frame)
        self.uploadButton.setGeometry(QtCore.QRect(710, 520, 191, 51))
        self.uploadButton.setObjectName("uploadButton")
        self.downloadButton = QtWidgets.QPushButton(self.frame)
        self.downloadButton.setGeometry(QtCore.QRect(710, 460, 191, 51))
        self.downloadButton.setObjectName("downloadButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1299, 29))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MyMessanger"))
        self.label_2.setText(_translate("MainWindow", "Пользователи в данном чате"))
        self.sendButton.setText(_translate("MainWindow", "Отправить"))
        self.exitAccountButton.setText(_translate("MainWindow", "Выйти с аккаунта"))
        self.disconnectButton.setText(_translate("MainWindow", "Выйти с сервера"))
        self.clearMessageButton.setText(_translate("MainWindow", "Очистить"))
        self.searchButton.setText(_translate("MainWindow", "Поиск"))
        self.abortSearchButton.setText(_translate("MainWindow", "Сбросить поиск"))
        self.isOnline.setText(_translate("MainWindow", "Онлайн"))
        self.isOffline.setText(_translate("MainWindow", "Оффлайн"))
        self.uploadButton.setText(_translate("MainWindow", "Загрузить файлы"))
        self.downloadButton.setText(_translate("MainWindow", "Скачать файлы"))
