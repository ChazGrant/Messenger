# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'searchForm.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(467, 288)
        MainWindow.setStyleSheet("*{\n"
"    font-family: century gothic;\n"
"    font-size: 20px;\n"
"}\n"
"QMainWindow{\n"
"    background-color: transparent;\n"
"}\n"
"QPushButton{\n"
"    border-radius: 15px;\n"
"    color: white;\n"
"}\n"
"#searchButton:hover{\n"
"    background: #333;\n"
"    color: rgb(0, 170, 127);\n"
"}\n"
"#cancelButton:hover{\n"
"    background: #333;\n"
"    color: rgb(255, 98, 51);\n"
"}\n"
"QToolButton{\n"
"    border-radius: 60px;\n"
"}\n"
"QFrame{\n"
"    background: #333;\n"
"    border-radius: 15px;\n"
"}\n"
"\n"
"#exitButton{\n"
"    /*background-color: red;*/\n"
"    border-radius: 15px;\n"
"    background-size: 5px;\n"
"}\n"
"#searchButton{\n"
"    background: rgb(0, 170, 127);\n"
"}\n"
"#cancelButton{\n"
"    background: rgb(255, 98, 51);    \n"
"}\n"
"QCheckBox{\n"
"    color: lightgrey;\n"
"}")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(10, 10, 451, 221))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.cancelButton = QtWidgets.QPushButton(self.frame)
        self.cancelButton.setGeometry(QtCore.QRect(280, 160, 101, 41))
        self.cancelButton.setObjectName("cancelButton")
        self.checkBox = QtWidgets.QCheckBox(self.frame)
        self.checkBox.setGeometry(QtCore.QRect(50, 90, 331, 20))
        self.checkBox.setObjectName("checkBox")
        self.searchButton = QtWidgets.QPushButton(self.frame)
        self.searchButton.setGeometry(QtCore.QRect(50, 160, 111, 41))
        self.searchButton.setStyleSheet("")
        self.searchButton.setObjectName("searchButton")
        self.checkBox_2 = QtWidgets.QCheckBox(self.frame)
        self.checkBox_2.setGeometry(QtCore.QRect(50, 120, 321, 20))
        self.checkBox_2.setObjectName("checkBox_2")
        self.textEdit = QtWidgets.QTextEdit(self.frame)
        self.textEdit.setGeometry(QtCore.QRect(40, 30, 341, 41))
        self.textEdit.setStyleSheet("background-color: lightgrey;\n"
"")
        self.textEdit.setObjectName("textEdit")
        self.exitButton = QtWidgets.QToolButton(self.frame)
        self.exitButton.setGeometry(QtCore.QRect(390, 20, 41, 31))
        self.exitButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("cross.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.exitButton.setIcon(icon)
        self.exitButton.setShortcut("")
        self.exitButton.setAutoRepeatDelay(300)
        self.exitButton.setObjectName("exitButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 467, 29))
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
        self.cancelButton.setText(_translate("MainWindow", "Отмена"))
        self.checkBox.setText(_translate("MainWindow", "Поиск по имени пользователя"))
        self.searchButton.setText(_translate("MainWindow", "Поиск"))
        self.checkBox_2.setText(_translate("MainWindow", "Поиск по сообщениям"))
        self.textEdit.setPlaceholderText(_translate("MainWindow", "Введите текст для поиска"))
