# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'download.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(372, 317)
        Form.setStyleSheet("*{\n"
"    font-family: century gothic;\n"
"    font-size: 20px;\n"
"}\n"
"QMainWindow{\n"
"    background-color: transparent;\n"
"}\n"
"QPushButton{\n"
"    border-radius: 15px;\n"
"    background: rgb(0, 170, 127);\n"
"    color: white;\n"
"}\n"
"QPushButton:hover{\n"
"    background: #333;\n"
"    color: rgb(0, 170, 127);\n"
"}\n"
"#exitAccountButton, #disconnectButton{\n"
"    background: rgb(255, 98, 51);\n"
"}\n"
"#exitAccountButton:hover, #disconnectButton:hover{\n"
"    background: #333;\n"
"    color: rgb(255, 98, 51);\n"
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
"#showUsersButton{\n"
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
        self.frame = QtWidgets.QFrame(Form)
        self.frame.setGeometry(QtCore.QRect(10, 10, 341, 291))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.listWidget = QtWidgets.QListWidget(self.frame)
        self.listWidget.setGeometry(QtCore.QRect(10, 30, 321, 192))
        self.listWidget.setStyleSheet("color: white;")
        self.listWidget.setObjectName("listWidget")
        self.selectButton = QtWidgets.QPushButton(self.frame)
        self.selectButton.setGeometry(QtCore.QRect(10, 240, 321, 41))
        self.selectButton.setObjectName("selectButton")
        self.exitButton = QtWidgets.QToolButton(self.frame)
        self.exitButton.setGeometry(QtCore.QRect(300, 0, 41, 31))
        self.exitButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("cross.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.exitButton.setIcon(icon)
        self.exitButton.setShortcut("")
        self.exitButton.setAutoRepeatDelay(300)
        self.exitButton.setObjectName("exitButton")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.selectButton.setText(_translate("Form", "Скачать"))