# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'privateChat.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(464, 428)
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
"    background: rgb(0, 170, 127);\n"
"    color: white;\n"
"}\n"
"QPushButton:hover{\n"
"    background: #333;\n"
"    color:  rgb(0, 170, 127);\n"
"}\n"
"#toolButton{\n"
"    border-radius: 60px;\n"
"    background:  rgb(0, 170, 127);\n"
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
        self.frame.setGeometry(QtCore.QRect(10, 10, 441, 351))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.exitButton = QtWidgets.QToolButton(self.frame)
        self.exitButton.setGeometry(QtCore.QRect(390, 20, 41, 31))
        self.exitButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("cross.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.exitButton.setIcon(icon)
        self.exitButton.setShortcut("")
        self.exitButton.setAutoRepeatDelay(300)
        self.exitButton.setObjectName("exitButton")
        self.sendButton = QtWidgets.QPushButton(self.frame)
        self.sendButton.setGeometry(QtCore.QRect(300, 250, 111, 41))
        self.sendButton.setObjectName("sendButton")
        self.clearButton = QtWidgets.QPushButton(self.frame)
        self.clearButton.setGeometry(QtCore.QRect(300, 297, 111, 41))
        self.clearButton.setObjectName("clearButton")
        self.textBrowser = QtWidgets.QTextBrowser(self.frame)
        self.textBrowser.setGeometry(QtCore.QRect(20, 20, 371, 221))
        self.textBrowser.setStyleSheet("background: lightgrey")
        self.textBrowser.setObjectName("textBrowser")
        self.textEdit = QtWidgets.QTextEdit(self.frame)
        self.textEdit.setGeometry(QtCore.QRect(20, 266, 261, 61))
        self.textEdit.setStyleSheet("background: lightgrey")
        self.textEdit.setObjectName("textEdit")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 464, 29))
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
        self.sendButton.setText(_translate("MainWindow", "Отправить"))
        self.clearButton.setText(_translate("MainWindow", "Очистить"))